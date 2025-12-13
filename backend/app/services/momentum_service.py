"""
Paper Momentum Service - Research Intelligence for Rising Papers

Identifies papers gaining traction through:
- Citation velocity (citations per day)
- Age-adjusted performance (vs peers of same age)
- Breakout detection (5x+ expected performance)
- Hidden gem detection (high quality, low visibility)
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.db.database import database


@dataclass
class MomentumMetrics:
    """Momentum metrics for a paper."""
    paper_id: str
    title: str
    published_date: datetime
    citation_count: int
    days_since_publication: int
    citations_per_day: float
    velocity_percentile: float  # 99 = top 1%
    expected_citations: float  # Based on age
    performance_ratio: float  # Actual / Expected
    momentum_score: float  # Composite score
    is_breakout: bool  # 3x+ expected
    context: str  # Human-readable explanation


class MomentumService:
    """Service for paper momentum and rising star detection."""

    # Expected citations by age bucket (based on typical ML/AI papers)
    # These are calibrated from the actual data
    AGE_EXPECTED_CITATIONS = {
        7: 0.1,      # 1 week old
        14: 0.3,     # 2 weeks
        30: 0.8,     # 1 month
        60: 2.0,     # 2 months
        90: 4.0,     # 3 months
        180: 8.0,    # 6 months
        365: 15.0,   # 1 year
    }

    async def _get_expected_citations(self, days_old: int) -> float:
        """Get expected citations for a paper of given age."""
        # Linear interpolation between age buckets
        prev_days, prev_expected = 0, 0.0
        for days, expected in sorted(self.AGE_EXPECTED_CITATIONS.items()):
            if days_old <= days:
                if days == prev_days:
                    return expected
                # Interpolate
                ratio = (days_old - prev_days) / (days - prev_days)
                return prev_expected + ratio * (expected - prev_expected)
            prev_days, prev_expected = days, expected
        # Beyond 1 year, extrapolate
        return prev_expected + (days_old - prev_days) * 0.05

    async def get_rising_stars(
        self,
        days: int = 90,
        min_citations: int = 1,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find papers with highest citation velocity.

        These are papers accumulating citations faster than their peers.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = """
            WITH paper_velocity AS (
                SELECT
                    p.id,
                    p.title,
                    p.abstract,
                    p.published_date,
                    p.citation_count,
                    EXTRACT(days FROM NOW() - p.published_date)::int as days_old,
                    p.citation_count::float / GREATEST(EXTRACT(days FROM NOW() - p.published_date), 1) as velocity
                FROM papers p
                WHERE p.published_date > :cutoff_date
                AND p.citation_count >= :min_citations
                AND p.published_date IS NOT NULL
            ),
            velocity_stats AS (
                SELECT
                    AVG(velocity) as avg_velocity,
                    STDDEV(velocity) as stddev_velocity,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY velocity) as median_velocity,
                    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY velocity) as p90_velocity,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY velocity) as p95_velocity,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY velocity) as p99_velocity
                FROM paper_velocity
            )
            SELECT
                pv.*,
                vs.avg_velocity,
                vs.median_velocity,
                vs.p90_velocity,
                vs.p95_velocity,
                PERCENT_RANK() OVER (ORDER BY pv.velocity) * 100 as velocity_percentile
            FROM paper_velocity pv
            CROSS JOIN velocity_stats vs
            ORDER BY pv.velocity DESC
            LIMIT :limit
        """

        rows = await database.fetch_all(query, {
            "cutoff_date": cutoff_date,
            "min_citations": min_citations,
            "limit": limit
        })

        results = []
        for row in rows:
            days_old = row["days_old"] or 1
            expected = await self._get_expected_citations(days_old)
            actual = row["citation_count"] or 0
            performance_ratio = actual / expected if expected > 0 else 0

            # Calculate momentum score (velocity * recency bonus)
            recency_bonus = max(1.0, 2.0 - (days_old / 90))  # Newer papers get up to 2x bonus
            momentum_score = row["velocity"] * recency_bonus * 100

            is_breakout = performance_ratio >= 3.0

            results.append({
                "paper_id": row["id"],
                "title": row["title"],
                "abstract": (row["abstract"] or "")[:300] + "..." if row["abstract"] and len(row["abstract"]) > 300 else row["abstract"],
                "published_date": row["published_date"].isoformat() if row["published_date"] else None,
                "citation_count": row["citation_count"],
                "days_since_publication": days_old,
                "citations_per_day": round(row["velocity"], 4),
                "velocity_percentile": round(row["velocity_percentile"], 1),
                "expected_citations": round(expected, 1),
                "performance_ratio": round(performance_ratio, 2),
                "momentum_score": round(momentum_score, 1),
                "is_breakout": is_breakout,
                "context": self._generate_momentum_context(
                    row["velocity"],
                    row["velocity_percentile"],
                    performance_ratio,
                    is_breakout,
                    days_old
                )
            })

        return results

    async def get_breakout_papers(
        self,
        days: int = 30,
        min_ratio: float = 3.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find recent papers significantly outperforming expectations.

        Breakout papers are getting 3x+ the citations expected for their age.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = """
            SELECT
                p.id,
                p.title,
                p.abstract,
                p.published_date,
                p.citation_count,
                EXTRACT(days FROM NOW() - p.published_date)::int as days_old,
                p.citation_count::float / GREATEST(EXTRACT(days FROM NOW() - p.published_date), 1) as velocity
            FROM papers p
            WHERE p.published_date > :cutoff_date
            AND p.citation_count >= 2
            AND p.published_date IS NOT NULL
            ORDER BY velocity DESC
            LIMIT 200
        """

        rows = await database.fetch_all(query, {
            "cutoff_date": cutoff_date
        })

        # Filter by performance ratio
        breakouts = []
        for row in rows:
            days_old = row["days_old"] or 1
            expected = await self._get_expected_citations(days_old)
            actual = row["citation_count"] or 0
            performance_ratio = actual / expected if expected > 0 else 0

            if performance_ratio >= min_ratio:
                recency_bonus = max(1.0, 2.0 - (days_old / 90))
                momentum_score = row["velocity"] * recency_bonus * 100

                breakouts.append({
                    "paper_id": row["id"],
                    "title": row["title"],
                    "abstract": (row["abstract"] or "")[:300] + "..." if row["abstract"] and len(row["abstract"]) > 300 else row["abstract"],
                    "published_date": row["published_date"].isoformat() if row["published_date"] else None,
                    "citation_count": row["citation_count"],
                    "days_since_publication": days_old,
                    "citations_per_day": round(row["velocity"], 4),
                    "expected_citations": round(expected, 1),
                    "performance_ratio": round(performance_ratio, 2),
                    "momentum_score": round(momentum_score, 1),
                    "context": f"🚀 {performance_ratio:.1f}x expected citations for {days_old}-day-old paper"
                })

        # Sort by performance ratio and return top N
        breakouts.sort(key=lambda x: x["performance_ratio"], reverse=True)
        return breakouts[:limit]

    async def get_hidden_gems(
        self,
        min_age_days: int = 60,
        max_age_days: int = 365,
        min_citations: int = 5,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find underappreciated quality papers.

        Hidden gems have solid citations but aren't trending -
        papers that deserve more attention.
        """
        # Calculate cutoff dates (max_age creates earlier date, min_age creates later date)
        min_cutoff_date = datetime.utcnow() - timedelta(days=min_age_days)
        max_cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

        query = """
            WITH paper_data AS (
                SELECT
                    p.id,
                    p.title,
                    p.abstract,
                    p.published_date,
                    p.citation_count,
                    EXTRACT(days FROM NOW() - p.published_date)::int as days_old
                FROM papers p
                WHERE p.published_date BETWEEN :max_cutoff_date AND :min_cutoff_date
                AND p.citation_count >= :min_citations
                AND p.published_date IS NOT NULL
            ),
            peer_stats AS (
                SELECT
                    AVG(citation_count) as avg_citations,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY citation_count) as p75_citations
                FROM paper_data
            )
            SELECT
                pd.*,
                ps.avg_citations,
                ps.p75_citations,
                PERCENT_RANK() OVER (ORDER BY pd.citation_count) * 100 as citation_percentile
            FROM paper_data pd
            CROSS JOIN peer_stats ps
            WHERE pd.citation_count BETWEEN ps.avg_citations * 0.5 AND ps.p75_citations * 1.2
            ORDER BY pd.citation_count DESC
            LIMIT :limit
        """

        rows = await database.fetch_all(query, {
            "min_cutoff_date": min_cutoff_date,
            "max_cutoff_date": max_cutoff_date,
            "min_citations": min_citations,
            "limit": limit
        })

        results = []
        for row in rows:
            days_old = row["days_old"] or 1
            velocity = (row["citation_count"] or 0) / days_old

            results.append({
                "paper_id": row["id"],
                "title": row["title"],
                "abstract": (row["abstract"] or "")[:300] + "..." if row["abstract"] and len(row["abstract"]) > 300 else row["abstract"],
                "published_date": row["published_date"].isoformat() if row["published_date"] else None,
                "citation_count": row["citation_count"],
                "days_since_publication": days_old,
                "citations_per_day": round(velocity, 4),
                "citation_percentile": round(row["citation_percentile"], 1),
                "context": f"💎 Solid {row['citation_count']} citations but not yet trending - quality paper worth attention"
            })

        return results

    async def get_paper_momentum(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get momentum metrics for a specific paper."""
        query = """
            SELECT
                p.id,
                p.title,
                p.published_date,
                p.citation_count,
                EXTRACT(days FROM NOW() - p.published_date)::int as days_old
            FROM papers p
            WHERE p.id = :paper_id
        """

        row = await database.fetch_one(query, {"paper_id": paper_id})
        if not row:
            return None

        days_old = row["days_old"] or 1
        actual = row["citation_count"] or 0
        velocity = actual / days_old
        expected = await self._get_expected_citations(days_old)
        performance_ratio = actual / expected if expected > 0 else 0

        # Get velocity percentile by comparing to peers
        percentile_query = """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN citation_count::float / GREATEST(EXTRACT(days FROM NOW() - published_date), 1) < :velocity THEN 1 ELSE 0 END) as below
            FROM papers
            WHERE published_date > NOW() - INTERVAL '180 days'
            AND citation_count > 0
        """
        pct_row = await database.fetch_one(percentile_query, {"velocity": velocity})
        velocity_percentile = (pct_row["below"] / pct_row["total"] * 100) if pct_row and pct_row["total"] > 0 else 50

        recency_bonus = max(1.0, 2.0 - (days_old / 90))
        momentum_score = velocity * recency_bonus * 100
        is_breakout = performance_ratio >= 3.0

        return {
            "paper_id": row["id"],
            "title": row["title"],
            "published_date": row["published_date"].isoformat() if row["published_date"] else None,
            "citation_count": row["citation_count"],
            "days_since_publication": days_old,
            "citations_per_day": round(velocity, 4),
            "velocity_percentile": round(velocity_percentile, 1),
            "expected_citations": round(expected, 1),
            "performance_ratio": round(performance_ratio, 2),
            "momentum_score": round(momentum_score, 1),
            "is_breakout": is_breakout,
            "context": self._generate_momentum_context(
                velocity,
                velocity_percentile,
                performance_ratio,
                is_breakout,
                days_old
            )
        }

    async def get_weekly_digest(self, limit: int = 10) -> Dict[str, Any]:
        """
        Generate a weekly digest of paper momentum.

        Combines rising stars, breakouts, and hidden gems.
        """
        rising = await self.get_rising_stars(days=7, min_citations=1, limit=5)
        breakouts = await self.get_breakout_papers(days=14, min_ratio=2.0, limit=5)
        gems = await self.get_hidden_gems(min_age_days=30, max_age_days=180, limit=5)

        return {
            "week_of": datetime.utcnow().strftime("%Y-%m-%d"),
            "rising_stars": rising,
            "breakout_papers": breakouts,
            "hidden_gems": gems,
            "summary": {
                "total_rising": len(rising),
                "total_breakouts": len(breakouts),
                "total_gems": len(gems)
            }
        }

    def _generate_momentum_context(
        self,
        velocity: float,
        percentile: float,
        performance_ratio: float,
        is_breakout: bool,
        days_old: int
    ) -> str:
        """Generate human-readable momentum context."""
        if is_breakout:
            return f"🚀 Breakout paper! {performance_ratio:.1f}x expected performance. Top {100 - percentile:.1f}% velocity."

        if percentile >= 95:
            return f"🔥 Top 5% citation velocity ({velocity:.3f}/day). Gaining traction fast."

        if percentile >= 90:
            return f"📈 Top 10% velocity. Strong momentum for a {days_old}-day-old paper."

        if percentile >= 75:
            return f"↗️ Above average momentum. Outperforming {percentile:.0f}% of peers."

        if percentile >= 50:
            return f"➡️ Average momentum. On par with similar-age papers."

        return f"📊 Below average momentum. May be a niche topic or early stage."


# Singleton instance
_momentum_service: Optional[MomentumService] = None


def get_momentum_service() -> MomentumService:
    """Get or create the momentum service singleton."""
    global _momentum_service
    if _momentum_service is None:
        _momentum_service = MomentumService()
    return _momentum_service
