"""
Leaderboard Service - Benchmark Intelligence with Context

Provides:
- Task/Dataset leaderboards with rankings
- SOTA detection and historical tracking
- Percentile calculations ("This is top 5%")
- Model comparison across benchmarks
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.db.database import database


# Metric configurations - higher is better for most, lower for some
HIGHER_IS_BETTER = {
    "accuracy", "f1", "precision", "recall", "auc", "map", "miou", "bleu",
    "rouge", "pass@1", "pass@10", "pass@100", "top-1", "top-5", "em",
    "hit@1", "hit@10", "mrr", "ndcg", "success rate", "win rate"
}

LOWER_IS_BETTER = {
    "perplexity", "wer", "cer", "fid", "mse", "mae", "rmse", "loss",
    "latency", "inference time", "ade", "fde", "error"
}


def is_higher_better(metric: str) -> bool:
    """Determine if higher values are better for a metric."""
    metric_lower = metric.lower()
    for m in LOWER_IS_BETTER:
        if m in metric_lower:
            return False
    return True  # Default to higher is better


@dataclass
class LeaderboardEntry:
    """Single entry in a leaderboard."""
    rank: int
    paper_id: str
    paper_title: str
    model_name: Optional[str]
    value: float
    metric: str
    published_date: Optional[datetime]
    is_sota: bool
    percentile: float  # 99 = top 1%
    delta_from_sota: Optional[float]


class LeaderboardService:
    """Service for benchmark leaderboards with intelligence."""

    async def get_popular_leaderboards(
        self,
        limit: int = 20,
        min_entries: int = 5
    ) -> List[Dict[str, Any]]:
        """Get most popular dataset+metric combinations for leaderboards."""
        query = """
            SELECT
                dataset,
                metric,
                COUNT(*) as entry_count,
                COUNT(DISTINCT paper_id) as paper_count,
                COUNT(DISTINCT model_name) as model_count,
                MAX(value) as max_value,
                MIN(value) as min_value,
                AVG(value) as avg_value
            FROM benchmarks
            WHERE dataset != 'N/A' AND dataset IS NOT NULL
            GROUP BY dataset, metric
            HAVING COUNT(*) >= :min_entries
            ORDER BY paper_count DESC, entry_count DESC
            LIMIT :limit
        """
        rows = await database.fetch_all(query, {
            "limit": limit,
            "min_entries": min_entries
        })

        return [
            {
                "dataset": row["dataset"],
                "metric": row["metric"],
                "entry_count": row["entry_count"],
                "paper_count": row["paper_count"],
                "model_count": row["model_count"],
                "value_range": {
                    "min": row["min_value"],
                    "max": row["max_value"],
                    "avg": round(row["avg_value"], 2) if row["avg_value"] else None
                },
                "higher_is_better": is_higher_better(row["metric"])
            }
            for row in rows
        ]

    async def get_leaderboard(
        self,
        dataset: str,
        metric: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get leaderboard for a specific dataset with full context."""

        # First, find available metrics for this dataset
        metric_query = """
            SELECT DISTINCT metric, COUNT(*) as cnt
            FROM benchmarks
            WHERE LOWER(dataset) = LOWER(:dataset)
            GROUP BY metric
            ORDER BY cnt DESC
        """
        metrics_rows = await database.fetch_all(metric_query, {"dataset": dataset})
        available_metrics = [r["metric"] for r in metrics_rows]

        if not available_metrics:
            return {"error": f"No benchmarks found for dataset: {dataset}"}

        # Use provided metric or default to most common
        selected_metric = metric if metric and metric in available_metrics else available_metrics[0]
        higher_better = is_higher_better(selected_metric)

        # Get all entries for this dataset+metric
        order_dir = "DESC" if higher_better else "ASC"
        entries_query = f"""
            SELECT
                b.paper_id,
                p.title as paper_title,
                b.model_name,
                b.value,
                b.metric,
                p.published_date,
                b.created_at
            FROM benchmarks b
            JOIN papers p ON b.paper_id = p.id
            WHERE LOWER(b.dataset) = LOWER(:dataset)
            AND b.metric = :metric
            ORDER BY b.value {order_dir}
            LIMIT :limit
        """

        rows = await database.fetch_all(entries_query, {
            "dataset": dataset,
            "metric": selected_metric,
            "limit": limit
        })

        if not rows:
            return {
                "dataset": dataset,
                "metric": selected_metric,
                "entries": [],
                "available_metrics": available_metrics
            }

        # Calculate stats for context
        values = [r["value"] for r in rows]
        sota_value = max(values) if higher_better else min(values)

        # Build entries with rankings and percentiles
        entries = []
        total_entries = len(rows)

        for i, row in enumerate(rows):
            rank = i + 1
            percentile = round(100 * (1 - rank / total_entries), 1) if total_entries > 1 else 100

            delta = None
            if row["value"] != sota_value:
                if higher_better:
                    delta = round(sota_value - row["value"], 3)
                else:
                    delta = round(row["value"] - sota_value, 3)

            entries.append({
                "rank": rank,
                "paper_id": row["paper_id"],
                "paper_title": row["paper_title"],
                "model_name": row["model_name"],
                "value": row["value"],
                "metric": row["metric"],
                "published_date": row["published_date"].isoformat() if row["published_date"] else None,
                "is_sota": row["value"] == sota_value,
                "percentile": percentile,
                "delta_from_sota": delta,
                "context": self._generate_context(rank, percentile, delta, higher_better, selected_metric)
            })

        # SOTA holder info
        sota_entry = entries[0]

        return {
            "dataset": dataset,
            "metric": selected_metric,
            "higher_is_better": higher_better,
            "available_metrics": available_metrics,
            "total_entries": total_entries,
            "sota": {
                "value": sota_value,
                "paper_id": sota_entry["paper_id"],
                "paper_title": sota_entry["paper_title"],
                "model_name": sota_entry["model_name"],
                "published_date": sota_entry["published_date"]
            },
            "stats": {
                "min": round(min(values), 3),
                "max": round(max(values), 3),
                "avg": round(sum(values) / len(values), 3),
                "spread": round(max(values) - min(values), 3)
            },
            "entries": entries
        }

    def _generate_context(
        self,
        rank: int,
        percentile: float,
        delta: Optional[float],
        higher_better: bool,
        metric: str
    ) -> str:
        """Generate human-readable context for a benchmark result."""
        if rank == 1:
            return "Current SOTA - best reported result"

        if percentile >= 95:
            tier = "Top 5%"
        elif percentile >= 90:
            tier = "Top 10%"
        elif percentile >= 75:
            tier = "Top 25%"
        elif percentile >= 50:
            tier = "Above median"
        else:
            tier = "Below median"

        if delta:
            direction = "behind" if higher_better else "above"
            return f"Rank #{rank} ({tier}) - {abs(delta):.2f} {direction} SOTA"

        return f"Rank #{rank} ({tier})"

    async def get_paper_benchmarks(
        self,
        paper_id: str
    ) -> Dict[str, Any]:
        """Get all benchmarks for a paper with leaderboard context."""

        # Get paper info
        paper_query = "SELECT id, title, published_date FROM papers WHERE id = :paper_id"
        paper = await database.fetch_one(paper_query, {"paper_id": paper_id})

        if not paper:
            return {"error": f"Paper not found: {paper_id}"}

        # Get all benchmarks for this paper
        benchmarks_query = """
            SELECT dataset, metric, value, model_name
            FROM benchmarks
            WHERE paper_id = :paper_id
            ORDER BY dataset, metric
        """
        benchmarks = await database.fetch_all(benchmarks_query, {"paper_id": paper_id})

        if not benchmarks:
            return {
                "paper_id": paper_id,
                "paper_title": paper["title"],
                "benchmarks": [],
                "summary": "No benchmark results found for this paper"
            }

        # For each benchmark, get its rank in the leaderboard
        results = []
        sota_count = 0
        top5_count = 0

        for b in benchmarks:
            higher_better = is_higher_better(b["metric"])
            order_dir = "DESC" if higher_better else "ASC"

            # Get rank for this result
            rank_query = f"""
                SELECT COUNT(*) + 1 as rank
                FROM benchmarks
                WHERE dataset = :dataset AND metric = :metric
                AND value {'>' if higher_better else '<'} :value
            """
            rank_result = await database.fetch_one(rank_query, {
                "dataset": b["dataset"],
                "metric": b["metric"],
                "value": b["value"]
            })
            rank = rank_result["rank"] if rank_result else 1

            # Get total count for percentile
            total_query = """
                SELECT COUNT(*) as total FROM benchmarks
                WHERE dataset = :dataset AND metric = :metric
            """
            total_result = await database.fetch_one(total_query, {
                "dataset": b["dataset"],
                "metric": b["metric"]
            })
            total = total_result["total"] if total_result else 1

            percentile = round(100 * (1 - rank / total), 1) if total > 1 else 100
            is_sota = rank == 1

            if is_sota:
                sota_count += 1
            if percentile >= 95:
                top5_count += 1

            results.append({
                "dataset": b["dataset"],
                "metric": b["metric"],
                "value": b["value"],
                "model_name": b["model_name"],
                "rank": rank,
                "total_entries": total,
                "percentile": percentile,
                "is_sota": is_sota,
                "context": self._generate_context(rank, percentile, None, higher_better, b["metric"])
            })

        # Generate summary
        summary_parts = []
        if sota_count > 0:
            summary_parts.append(f"Achieves SOTA on {sota_count} benchmark(s)")
        if top5_count > sota_count:
            summary_parts.append(f"Top 5% on {top5_count - sota_count} additional benchmark(s)")
        if not summary_parts:
            summary_parts.append(f"Reports results on {len(results)} benchmark(s)")

        return {
            "paper_id": paper_id,
            "paper_title": paper["title"],
            "published_date": paper["published_date"].isoformat() if paper["published_date"] else None,
            "benchmark_count": len(results),
            "sota_count": sota_count,
            "top5_count": top5_count,
            "summary": ". ".join(summary_parts),
            "benchmarks": results
        }

    async def get_model_performance(
        self,
        model_name: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get performance of a specific model across all benchmarks."""

        query = """
            SELECT
                b.dataset,
                b.metric,
                b.value,
                b.paper_id,
                p.title as paper_title,
                p.published_date
            FROM benchmarks b
            JOIN papers p ON b.paper_id = p.id
            WHERE LOWER(b.model_name) LIKE LOWER(:model_pattern)
            ORDER BY b.dataset, b.metric
            LIMIT :limit
        """

        rows = await database.fetch_all(query, {
            "model_pattern": f"%{model_name}%",
            "limit": limit
        })

        if not rows:
            return {"error": f"No benchmarks found for model: {model_name}"}

        results = []
        for row in rows:
            higher_better = is_higher_better(row["metric"])

            # Get rank
            order_dir = ">" if higher_better else "<"
            rank_query = f"""
                SELECT COUNT(*) + 1 as rank
                FROM benchmarks
                WHERE dataset = :dataset AND metric = :metric
                AND value {order_dir} :value
            """
            rank_result = await database.fetch_one(rank_query, {
                "dataset": row["dataset"],
                "metric": row["metric"],
                "value": row["value"]
            })
            rank = rank_result["rank"] if rank_result else 1

            results.append({
                "dataset": row["dataset"],
                "metric": row["metric"],
                "value": row["value"],
                "rank": rank,
                "paper_id": row["paper_id"],
                "paper_title": row["paper_title"]
            })

        return {
            "model_name": model_name,
            "benchmark_count": len(results),
            "benchmarks": results
        }

    async def get_recent_sota(
        self,
        days: int = 30,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find papers that achieved SOTA recently."""

        cutoff = datetime.utcnow() - timedelta(days=days)

        # This is complex - we need to find benchmarks where the value is the best
        # for that dataset+metric combination AND was published recently
        query = """
            WITH ranked AS (
                SELECT
                    b.paper_id,
                    b.dataset,
                    b.metric,
                    b.value,
                    b.model_name,
                    p.title as paper_title,
                    p.published_date,
                    ROW_NUMBER() OVER (
                        PARTITION BY b.dataset, b.metric
                        ORDER BY b.value DESC
                    ) as rank_desc,
                    ROW_NUMBER() OVER (
                        PARTITION BY b.dataset, b.metric
                        ORDER BY b.value ASC
                    ) as rank_asc
                FROM benchmarks b
                JOIN papers p ON b.paper_id = p.id
                WHERE b.dataset != 'N/A'
            )
            SELECT *
            FROM ranked
            WHERE (rank_desc = 1 OR rank_asc = 1)
            AND published_date >= :cutoff
            ORDER BY published_date DESC
            LIMIT :limit
        """

        rows = await database.fetch_all(query, {
            "cutoff": cutoff,
            "limit": limit
        })

        results = []
        for row in rows:
            higher_better = is_higher_better(row["metric"])
            is_sota = (row["rank_desc"] == 1 and higher_better) or (row["rank_asc"] == 1 and not higher_better)

            if is_sota:
                results.append({
                    "paper_id": row["paper_id"],
                    "paper_title": row["paper_title"],
                    "dataset": row["dataset"],
                    "metric": row["metric"],
                    "value": row["value"],
                    "model_name": row["model_name"],
                    "published_date": row["published_date"].isoformat() if row["published_date"] else None
                })

        return results


# Singleton instance
_leaderboard_service: Optional[LeaderboardService] = None


def get_leaderboard_service() -> LeaderboardService:
    """Get or create the leaderboard service singleton."""
    global _leaderboard_service
    if _leaderboard_service is None:
        _leaderboard_service = LeaderboardService()
    return _leaderboard_service
