"""
Temporal Tracking Service

Captures metric snapshots over time to enable trend analysis:
- Citation velocity (citations per month)
- GitHub activity trends
- Buzz score tracking
- Rising/falling papers identification

This creates the longitudinal data moat that enables:
- "Show papers with rising citations"
- "What papers are losing momentum?"
- "Predict emerging papers"
"""
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta, timezone
from pydantic import BaseModel

from app.utils.logger import LoggerMixin


class MetricSnapshot(BaseModel):
    """A single point-in-time snapshot of paper metrics"""
    paper_id: str
    snapshot_date: date
    citation_count: Optional[int] = None
    influential_citation_count: Optional[int] = None
    citation_velocity: Optional[float] = None  # Citations per month
    github_stars: Optional[int] = None
    github_forks: Optional[int] = None
    github_open_issues: Optional[int] = None
    huggingface_downloads: Optional[int] = None
    twitter_mentions: Optional[int] = None
    reddit_mentions: Optional[int] = None
    buzz_score: Optional[float] = None
    quality_score: Optional[float] = None


class TrendData(BaseModel):
    """Trend analysis for a paper"""
    paper_id: str
    citation_trend: str  # "rising", "stable", "falling"
    citation_velocity_current: Optional[float] = None
    citation_velocity_30d_ago: Optional[float] = None
    citation_velocity_change: Optional[float] = None
    github_trend: Optional[str] = None
    buzz_trend: Optional[str] = None


class TemporalTracker(LoggerMixin):
    """
    Tracks paper metrics over time and provides trend analysis.
    """

    def calculate_citation_velocity(
        self,
        current_citations: int,
        previous_citations: int,
        days_between: int
    ) -> float:
        """
        Calculate citation velocity (citations per month).

        Args:
            current_citations: Current citation count
            previous_citations: Citation count from previous snapshot
            days_between: Days between snapshots

        Returns:
            Citations per month (30 days)
        """
        if days_between <= 0:
            return 0.0

        delta = current_citations - previous_citations
        velocity = (delta / days_between) * 30  # Normalize to per-month

        return max(0.0, velocity)  # Don't allow negative velocity

    def calculate_buzz_score(
        self,
        citation_velocity: float,
        github_stars: int = 0,
        twitter_mentions: int = 0,
        recency_days: int = 365
    ) -> float:
        """
        Calculate composite buzz score (0-10 scale).

        Factors:
        - Citation velocity (weight: 0.4)
        - GitHub activity (weight: 0.3)
        - Social mentions (weight: 0.2)
        - Recency (weight: 0.1)
        """
        # Normalize citation velocity (0-10 scale, capped at 100 cites/month)
        cv_score = min(10.0, (citation_velocity / 10.0))

        # Normalize GitHub stars (0-10 scale, capped at 10k stars)
        gh_score = min(10.0, (github_stars / 1000.0))

        # Normalize twitter mentions (0-10 scale, capped at 500/month)
        tw_score = min(10.0, (twitter_mentions / 50.0))

        # Recency factor (papers < 1 year old get boost)
        recency_factor = max(0.0, min(1.0, 1 - (recency_days / 730)))
        rec_score = recency_factor * 10.0

        # Weighted average
        buzz = (
            cv_score * 0.4 +
            gh_score * 0.3 +
            tw_score * 0.2 +
            rec_score * 0.1
        )

        return round(buzz, 2)

    async def capture_snapshot(
        self,
        paper: Dict[str, Any],
        db,
        snapshot_date: Optional[date] = None
    ) -> Optional[MetricSnapshot]:
        """
        Capture current metrics for a paper.

        Args:
            paper: Paper dict with current metrics
            db: Database connection
            snapshot_date: Date for snapshot (defaults to today)

        Returns:
            The created snapshot
        """
        snapshot_date = snapshot_date or date.today()
        paper_id = paper.get("id")

        if not paper_id:
            return None

        # Get current metrics
        citation_count = paper.get("citation_count", 0)
        influential_citations = paper.get("influential_citation_count", 0)
        quality_score = paper.get("quality_score", 0.0)

        # Get GitHub stats from external_signals
        signals = paper.get("external_signals") or {}
        if isinstance(signals, str):
            try:
                signals = json.loads(signals)
            except json.JSONDecodeError:
                signals = {}
        github_data = signals.get("github") or {}
        github_stars = github_data.get("total_stars", 0)

        repos = github_data.get("repos") or []
        github_forks = sum(r.get("forks", 0) for r in repos)
        github_issues = sum(r.get("open_issues", 0) for r in repos)

        # Get HuggingFace stats
        hf_data = signals.get("huggingface") or {}
        hf_downloads = hf_data.get("total_downloads", 0)

        # Get social stats
        social_data = signals.get("social") or {}
        twitter_mentions = social_data.get("twitter_mentions_30d", 0)
        reddit_mentions = social_data.get("reddit_threads", 0)

        # Calculate citation velocity from previous snapshot
        prev_query = """
            SELECT citation_count, snapshot_date
            FROM metric_snapshots
            WHERE paper_id = :paper_id
            AND snapshot_date < :current_date
            ORDER BY snapshot_date DESC
            LIMIT 1
        """

        prev = await db.fetch_one(prev_query, {
            "paper_id": paper_id,
            "current_date": snapshot_date
        })

        citation_velocity = 0.0
        if prev and prev["citation_count"] is not None:
            days_between = (snapshot_date - prev["snapshot_date"]).days
            if days_between > 0:
                citation_velocity = self.calculate_citation_velocity(
                    citation_count,
                    prev["citation_count"],
                    days_between
                )

        # Calculate recency
        published_date = paper.get("published_date")
        if isinstance(published_date, str):
            published_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
        # Handle timezone-aware datetimes
        if published_date:
            now = datetime.now(timezone.utc)
            # Make published_date timezone-aware if it isn't
            if published_date.tzinfo is None:
                published_date = published_date.replace(tzinfo=timezone.utc)
            recency_days = (now - published_date).days
        else:
            recency_days = 365

        # Calculate buzz score
        buzz_score = self.calculate_buzz_score(
            citation_velocity,
            github_stars,
            twitter_mentions,
            recency_days
        )

        # Create snapshot
        snapshot = MetricSnapshot(
            paper_id=paper_id,
            snapshot_date=snapshot_date,
            citation_count=citation_count,
            influential_citation_count=influential_citations,
            citation_velocity=citation_velocity,
            github_stars=github_stars,
            github_forks=github_forks,
            github_open_issues=github_issues,
            huggingface_downloads=hf_downloads,
            twitter_mentions=twitter_mentions,
            reddit_mentions=reddit_mentions,
            buzz_score=buzz_score,
            quality_score=quality_score
        )

        # Save to database
        insert_query = """
            INSERT INTO metric_snapshots
            (paper_id, snapshot_date, citation_count, influential_citation_count,
             citation_velocity, github_stars, github_forks, github_open_issues,
             huggingface_downloads, twitter_mentions, reddit_mentions,
             buzz_score, quality_score)
            VALUES
            (:paper_id, :snapshot_date, :citation_count, :influential_citations,
             :citation_velocity, :github_stars, :github_forks, :github_issues,
             :hf_downloads, :twitter_mentions, :reddit_mentions,
             :buzz_score, :quality_score)
            ON CONFLICT (paper_id, snapshot_date) DO UPDATE SET
                citation_count = EXCLUDED.citation_count,
                influential_citation_count = EXCLUDED.influential_citation_count,
                citation_velocity = EXCLUDED.citation_velocity,
                github_stars = EXCLUDED.github_stars,
                github_forks = EXCLUDED.github_forks,
                github_open_issues = EXCLUDED.github_open_issues,
                huggingface_downloads = EXCLUDED.huggingface_downloads,
                twitter_mentions = EXCLUDED.twitter_mentions,
                reddit_mentions = EXCLUDED.reddit_mentions,
                buzz_score = EXCLUDED.buzz_score,
                quality_score = EXCLUDED.quality_score
        """

        await db.execute(insert_query, {
            "paper_id": paper_id,
            "snapshot_date": snapshot_date,
            "citation_count": citation_count,
            "influential_citations": influential_citations,
            "citation_velocity": citation_velocity,
            "github_stars": github_stars,
            "github_forks": github_forks,
            "github_issues": github_issues,
            "hf_downloads": hf_downloads,
            "twitter_mentions": twitter_mentions,
            "reddit_mentions": reddit_mentions,
            "buzz_score": buzz_score,
            "quality_score": quality_score
        })

        return snapshot

    async def get_paper_history(
        self,
        paper_id: str,
        db,
        days: int = 90
    ) -> List[MetricSnapshot]:
        """
        Get metric history for a paper.
        """
        query = """
            SELECT *
            FROM metric_snapshots
            WHERE paper_id = :paper_id
            AND snapshot_date >= :start_date
            ORDER BY snapshot_date DESC
        """

        start_date = date.today() - timedelta(days=days)
        results = await db.fetch_all(query, {
            "paper_id": paper_id,
            "start_date": start_date
        })

        return [
            MetricSnapshot(
                paper_id=r["paper_id"],
                snapshot_date=r["snapshot_date"],
                citation_count=r["citation_count"],
                influential_citation_count=r["influential_citation_count"],
                citation_velocity=r["citation_velocity"],
                github_stars=r["github_stars"],
                github_forks=r["github_forks"],
                github_open_issues=r["github_open_issues"],
                huggingface_downloads=r["huggingface_downloads"],
                twitter_mentions=r["twitter_mentions"],
                reddit_mentions=r["reddit_mentions"],
                buzz_score=r["buzz_score"],
                quality_score=r["quality_score"]
            )
            for r in results
        ]

    async def get_trending_papers(
        self,
        db,
        metric: str = "citation_velocity",
        limit: int = 50,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get papers with highest metric values in recent period.

        Args:
            metric: "citation_velocity", "buzz_score", "github_stars"
            limit: Number of papers to return
            days: Look back period
        """
        # Validate metric
        valid_metrics = ["citation_velocity", "buzz_score", "github_stars", "huggingface_downloads"]
        if metric not in valid_metrics:
            metric = "citation_velocity"

        query = f"""
            WITH latest_snapshots AS (
                SELECT DISTINCT ON (paper_id)
                    paper_id,
                    snapshot_date,
                    {metric},
                    citation_count,
                    buzz_score
                FROM metric_snapshots
                WHERE snapshot_date >= :start_date
                AND {metric} IS NOT NULL
                AND {metric} > 0
                ORDER BY paper_id, snapshot_date DESC
            )
            SELECT
                ls.*,
                p.title,
                p.category,
                p.published_date
            FROM latest_snapshots ls
            JOIN papers p ON ls.paper_id = p.id
            ORDER BY ls.{metric} DESC
            LIMIT :limit
        """

        start_date = date.today() - timedelta(days=days)
        results = await db.fetch_all(query, {
            "start_date": start_date,
            "limit": limit
        })

        return [
            {
                "paper_id": r["paper_id"],
                "title": r["title"],
                "category": r["category"],
                "published_date": r["published_date"].isoformat() if r["published_date"] else None,
                "snapshot_date": r["snapshot_date"].isoformat(),
                metric: r[metric],
                "citation_count": r["citation_count"],
                "buzz_score": r["buzz_score"]
            }
            for r in results
        ]

    async def get_paper_trend(
        self,
        paper_id: str,
        db
    ) -> Optional[TrendData]:
        """
        Analyze trend for a specific paper.
        """
        # Get current and 30-day-ago snapshots
        query = """
            WITH snapshots AS (
                SELECT
                    snapshot_date,
                    citation_velocity,
                    github_stars,
                    buzz_score
                FROM metric_snapshots
                WHERE paper_id = :paper_id
                ORDER BY snapshot_date DESC
            )
            SELECT
                (SELECT citation_velocity FROM snapshots LIMIT 1) as current_velocity,
                (SELECT citation_velocity FROM snapshots WHERE snapshot_date <= CURRENT_DATE - 30 LIMIT 1) as old_velocity,
                (SELECT github_stars FROM snapshots LIMIT 1) as current_stars,
                (SELECT github_stars FROM snapshots WHERE snapshot_date <= CURRENT_DATE - 30 LIMIT 1) as old_stars,
                (SELECT buzz_score FROM snapshots LIMIT 1) as current_buzz,
                (SELECT buzz_score FROM snapshots WHERE snapshot_date <= CURRENT_DATE - 30 LIMIT 1) as old_buzz
        """

        result = await db.fetch_one(query, {"paper_id": paper_id})

        if not result or result["current_velocity"] is None:
            return None

        # Determine trends
        def get_trend(current: float, old: float, threshold: float = 0.2) -> str:
            if old is None or old == 0:
                return "stable"
            change = (current - old) / old
            if change > threshold:
                return "rising"
            elif change < -threshold:
                return "falling"
            return "stable"

        velocity_change = None
        if result["old_velocity"] and result["old_velocity"] > 0:
            velocity_change = (
                (result["current_velocity"] - result["old_velocity"]) / result["old_velocity"] * 100
            )

        return TrendData(
            paper_id=paper_id,
            citation_trend=get_trend(
                result["current_velocity"] or 0,
                result["old_velocity"] or 0
            ),
            citation_velocity_current=result["current_velocity"],
            citation_velocity_30d_ago=result["old_velocity"],
            citation_velocity_change=velocity_change,
            github_trend=get_trend(
                result["current_stars"] or 0,
                result["old_stars"] or 0
            ) if result["current_stars"] else None,
            buzz_trend=get_trend(
                result["current_buzz"] or 0,
                result["old_buzz"] or 0
            ) if result["current_buzz"] else None
        )


class TemporalService(LoggerMixin):
    """
    High-level service for temporal tracking operations.
    """

    def __init__(self):
        self.tracker = TemporalTracker()

    async def capture_daily_snapshots(
        self,
        db,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Capture daily snapshots for all papers (or limited set).

        Should be run as a daily job.
        """
        # Get papers that need snapshots
        query = """
            SELECT
                p.id,
                p.title,
                p.citation_count,
                p.influential_citation_count,
                p.quality_score,
                p.published_date,
                p.external_signals
            FROM papers p
            LEFT JOIN metric_snapshots ms ON p.id = ms.paper_id
                AND ms.snapshot_date = CURRENT_DATE
            WHERE ms.paper_id IS NULL
            ORDER BY p.citation_count DESC NULLS LAST
            LIMIT :limit
        """

        papers = await db.fetch_all(query, {"limit": limit or 10000})

        captured = 0
        errors = 0

        for p in papers:
            try:
                paper_dict = {
                    "id": p["id"],
                    "citation_count": p["citation_count"],
                    "influential_citation_count": p["influential_citation_count"],
                    "quality_score": p["quality_score"],
                    "published_date": p["published_date"],
                    "external_signals": p["external_signals"]
                }

                await self.tracker.capture_snapshot(paper_dict, db)
                captured += 1

            except Exception as e:
                self.log_error(f"Error capturing snapshot for {p['id']}", error=e)
                errors += 1

        return {
            "papers_processed": len(papers),
            "snapshots_captured": captured,
            "errors": errors,
            "date": date.today().isoformat()
        }

    async def get_rising_papers(
        self,
        db,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get papers with rising citation velocity"""
        return await self.tracker.get_trending_papers(
            db, "citation_velocity", limit
        )

    async def get_hot_papers(
        self,
        db,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get papers with highest buzz scores"""
        return await self.tracker.get_trending_papers(
            db, "buzz_score", limit
        )


# Singleton instance
_temporal_service = None

def get_temporal_service() -> TemporalService:
    """Get singleton temporal service instance"""
    global _temporal_service
    if _temporal_service is None:
        _temporal_service = TemporalService()
    return _temporal_service
