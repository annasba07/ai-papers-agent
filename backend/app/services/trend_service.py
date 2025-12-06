"""
Trend Detection Service

Identifies and tracks research trends including:
- Hot topics (techniques with accelerating paper counts)
- Rising methods (new techniques gaining traction)
- Author activity patterns
- Conference buzz

Uses the local atlas data to compute trends efficiently.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from pydantic import BaseModel

from app.utils.logger import LoggerMixin
from app.services.local_atlas_service import local_atlas_service
from app.services.technique_extraction_service import (
    get_technique_extraction_service,
    TECHNIQUE_PATTERNS,
    TASK_DOMAINS
)


class TrendingTopic(BaseModel):
    """A trending research topic"""
    name: str
    normalized_name: str
    category: str  # "technique", "task", "architecture"
    current_count: int
    previous_count: int
    acceleration: float  # Percentage change
    representative_papers: List[Dict[str, Any]] = []
    related_topics: List[str] = []


class AuthorTrend(BaseModel):
    """Author activity trend"""
    name: str
    paper_count: int
    recent_papers: int  # Papers in last 30 days
    top_topics: List[str] = []
    avg_citations: Optional[float] = None


class TrendSummary(BaseModel):
    """Summary of research trends"""
    hot_topics: List[TrendingTopic]
    rising_techniques: List[TrendingTopic]
    active_authors: List[AuthorTrend]
    emerging_areas: List[str]
    generated_at: str


class TrendService(LoggerMixin):
    """
    Service for detecting and tracking research trends.

    Uses local atlas data for efficient computation.
    """

    def __init__(self):
        self.technique_extractor = get_technique_extraction_service()
        self.log_info("Trend service initialized")

    def get_hot_topics(
        self,
        window_days: int = 30,
        comparison_window_days: int = 30,
        top_k: int = 10
    ) -> List[TrendingTopic]:
        """
        Identify hot topics based on paper velocity.

        Compares paper counts in current window vs previous window
        to find accelerating topics.

        Args:
            window_days: Current time window
            comparison_window_days: Previous window for comparison
            top_k: Number of topics to return

        Returns:
            List of trending topics sorted by acceleration
        """
        if not local_atlas_service.enabled:
            self.log_warning("Atlas service not available for trend detection")
            return []

        now = datetime.utcnow()
        current_cutoff = now - timedelta(days=window_days)
        previous_cutoff = current_cutoff - timedelta(days=comparison_window_days)

        # Count techniques in each window
        current_counts: Dict[str, int] = defaultdict(int)
        previous_counts: Dict[str, int] = defaultdict(int)
        technique_papers: Dict[str, List[Dict]] = defaultdict(list)

        for record in local_atlas_service._records:
            published_dt = record.get("_published_dt")
            if not published_dt:
                continue

            text = record.get("_search_text", "").lower()

            # Find techniques in this paper
            for technique_key, patterns in TECHNIQUE_PATTERNS.items():
                if any(p in text for p in patterns):
                    if published_dt >= current_cutoff:
                        current_counts[technique_key] += 1
                        if len(technique_papers[technique_key]) < 3:
                            technique_papers[technique_key].append({
                                "id": record.get("id"),
                                "title": record.get("title"),
                                "published": record.get("published")
                            })
                    elif published_dt >= previous_cutoff:
                        previous_counts[technique_key] += 1

        # Calculate acceleration
        trends = []
        for technique, current in current_counts.items():
            previous = previous_counts.get(technique, 0)

            if previous > 0:
                acceleration = ((current - previous) / previous) * 100
            elif current > 3:
                acceleration = 100.0  # New technique with activity
            else:
                continue

            trends.append(TrendingTopic(
                name=technique.replace("_", " ").title(),
                normalized_name=technique,
                category="technique",
                current_count=current,
                previous_count=previous,
                acceleration=acceleration,
                representative_papers=technique_papers.get(technique, []),
                related_topics=self._find_related_topics(technique)
            ))

        # Sort by acceleration
        trends.sort(key=lambda t: t.acceleration, reverse=True)

        return trends[:top_k]

    def get_rising_techniques(
        self,
        lookback_days: int = 90,
        top_k: int = 10
    ) -> List[TrendingTopic]:
        """
        Find techniques that are gaining traction.

        Focuses on newer techniques with steady growth.

        Args:
            lookback_days: How far back to look
            top_k: Number of techniques to return

        Returns:
            List of rising techniques
        """
        if not local_atlas_service.enabled:
            return []

        now = datetime.utcnow()

        # Divide lookback into three periods
        period_days = lookback_days // 3
        periods = [
            (now - timedelta(days=period_days), now),
            (now - timedelta(days=2 * period_days), now - timedelta(days=period_days)),
            (now - timedelta(days=3 * period_days), now - timedelta(days=2 * period_days))
        ]

        # Count by period
        period_counts: List[Dict[str, int]] = [{} for _ in periods]

        for record in local_atlas_service._records:
            published_dt = record.get("_published_dt")
            if not published_dt:
                continue

            text = record.get("_search_text", "").lower()

            for technique_key, patterns in TECHNIQUE_PATTERNS.items():
                if any(p in text for p in patterns):
                    for i, (start, end) in enumerate(periods):
                        if start <= published_dt < end:
                            period_counts[i][technique_key] = period_counts[i].get(technique_key, 0) + 1

        # Find techniques with consistent growth
        rising = []
        for technique in set().union(*[set(p.keys()) for p in period_counts]):
            counts = [period_counts[i].get(technique, 0) for i in range(3)]

            # Check for growth pattern: recent > middle > old
            if counts[0] > counts[1] >= counts[2] and counts[0] > 2:
                growth_rate = ((counts[0] - counts[2]) / max(counts[2], 1)) * 100

                rising.append(TrendingTopic(
                    name=technique.replace("_", " ").title(),
                    normalized_name=technique,
                    category="technique",
                    current_count=counts[0],
                    previous_count=counts[2],
                    acceleration=growth_rate,
                    representative_papers=[],
                    related_topics=[]
                ))

        rising.sort(key=lambda t: t.acceleration, reverse=True)
        return rising[:top_k]

    def get_active_authors(
        self,
        window_days: int = 30,
        top_k: int = 15
    ) -> List[AuthorTrend]:
        """
        Find most active authors in recent period.

        Args:
            window_days: Time window to consider
            top_k: Number of authors to return

        Returns:
            List of active authors with their stats
        """
        if not local_atlas_service.enabled:
            return []

        now = datetime.utcnow()
        cutoff = now - timedelta(days=window_days)

        author_stats: Dict[str, Dict] = defaultdict(lambda: {
            "total_count": 0,
            "recent_count": 0,
            "topics": defaultdict(int)
        })

        for record in local_atlas_service._records:
            published_dt = record.get("_published_dt")
            authors = record.get("authors", [])
            text = record.get("_search_text", "").lower()

            for author in authors:
                author_stats[author]["total_count"] += 1

                if published_dt and published_dt >= cutoff:
                    author_stats[author]["recent_count"] += 1

                    # Track topics
                    for technique_key, patterns in TECHNIQUE_PATTERNS.items():
                        if any(p in text for p in patterns):
                            author_stats[author]["topics"][technique_key] += 1

        # Build author trend list
        trends = []
        for name, stats in author_stats.items():
            if stats["recent_count"] < 2:
                continue

            top_topics = sorted(
                stats["topics"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            trends.append(AuthorTrend(
                name=name,
                paper_count=stats["total_count"],
                recent_papers=stats["recent_count"],
                top_topics=[t[0].replace("_", " ").title() for t in top_topics]
            ))

        trends.sort(key=lambda t: t.recent_papers, reverse=True)
        return trends[:top_k]

    def get_emerging_areas(self, top_k: int = 5) -> List[str]:
        """
        Identify emerging research areas based on task domain growth.

        Returns:
            List of emerging area names
        """
        if not local_atlas_service.enabled:
            return []

        now = datetime.utcnow()
        recent_cutoff = now - timedelta(days=60)
        older_cutoff = recent_cutoff - timedelta(days=60)

        recent_counts: Dict[str, int] = defaultdict(int)
        older_counts: Dict[str, int] = defaultdict(int)

        for record in local_atlas_service._records:
            published_dt = record.get("_published_dt")
            if not published_dt:
                continue

            text = record.get("_search_text", "").lower()

            for domain, keywords in TASK_DOMAINS.items():
                if any(kw in text for kw in keywords):
                    if published_dt >= recent_cutoff:
                        recent_counts[domain] += 1
                    elif published_dt >= older_cutoff:
                        older_counts[domain] += 1

        # Find areas with acceleration
        emerging = []
        for domain, recent in recent_counts.items():
            older = older_counts.get(domain, 0)
            if older > 0 and recent > older * 1.2:  # 20% growth
                emerging.append((domain, (recent - older) / older))
            elif older == 0 and recent > 5:
                emerging.append((domain, 1.0))

        emerging.sort(key=lambda x: x[1], reverse=True)
        return [e[0].replace("_", " ").title() for e in emerging[:top_k]]

    def get_trend_summary(self) -> TrendSummary:
        """
        Generate a comprehensive trend summary.

        Returns:
            TrendSummary with all trend data
        """
        self.log_info("Generating trend summary")

        return TrendSummary(
            hot_topics=self.get_hot_topics(),
            rising_techniques=self.get_rising_techniques(),
            active_authors=self.get_active_authors(),
            emerging_areas=self.get_emerging_areas(),
            generated_at=datetime.utcnow().isoformat()
        )

    def _find_related_topics(self, technique: str) -> List[str]:
        """Find topics that often appear with this technique"""
        # Simple co-occurrence based on common categories
        related_map = {
            "transformer": ["attention", "layer_norm", "flash_attention"],
            "diffusion": ["vae", "contrastive", "rmsnorm"],
            "lora": ["qlora", "peft", "adam"],
            "flash_attention": ["transformer", "sparse_attention"],
            "contrastive": ["clip", "transformer", "distillation"],
            "rlhf": ["dpo", "transformer", "peft"],
        }
        return related_map.get(technique, [])[:3]


# Module-level singleton
_trend_service: Optional[TrendService] = None


def get_trend_service() -> TrendService:
    """Get or create trend service singleton"""
    global _trend_service
    if _trend_service is None:
        _trend_service = TrendService()
    return _trend_service
