"""
Benchmark Service

Manages benchmark definitions and SOTA tracking:
- Benchmark registry (ImageNet, MMLU, HumanEval, etc.)
- SOTA history per benchmark
- Leaderboard queries
- Performance comparison across papers

This enables queries like:
- "What's SOTA on ImageNet?"
- "Show me the SOTA progression over time"
- "How does this paper compare to SOTA?"
"""
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from pydantic import BaseModel

from app.utils.logger import LoggerMixin


class BenchmarkDefinition(BaseModel):
    """A benchmark definition"""
    id: str
    name: str
    slug: str
    task_category: Optional[str] = None
    modality: Optional[str] = None
    primary_metric: str
    metric_unit: Optional[str] = None
    higher_is_better: bool = True
    description: Optional[str] = None


class SOTAEntry(BaseModel):
    """A state-of-the-art entry"""
    benchmark_id: str
    benchmark_name: str
    paper_id: str
    paper_title: str
    value: float
    achieved_date: date
    model_name: Optional[str] = None
    model_size: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class LeaderboardEntry(BaseModel):
    """An entry in the benchmark leaderboard"""
    rank: int
    paper_id: str
    paper_title: str
    value: float
    model_name: Optional[str] = None
    model_size: Optional[str] = None
    achieved_date: Optional[date] = None
    is_current_sota: bool = False


class BenchmarkService(LoggerMixin):
    """
    Service for managing benchmarks and SOTA tracking.
    """

    async def get_all_benchmarks(
        self,
        db,
        modality: Optional[str] = None,
        task_category: Optional[str] = None
    ) -> List[BenchmarkDefinition]:
        """
        Get all benchmark definitions.

        Args:
            modality: Filter by modality (vision, language, code, etc.)
            task_category: Filter by task category
        """
        conditions = ["1=1"]
        params = {}

        if modality:
            conditions.append("modality = :modality")
            params["modality"] = modality

        if task_category:
            conditions.append("task_category = :task_category")
            params["task_category"] = task_category

        query = f"""
            SELECT
                id::text,
                name,
                slug,
                task_category,
                modality,
                primary_metric,
                metric_unit,
                higher_is_better,
                description
            FROM benchmark_definitions
            WHERE {' AND '.join(conditions)}
            ORDER BY modality, task_category, name
        """

        results = await db.fetch_all(query, params)

        return [
            BenchmarkDefinition(
                id=str(r["id"]),
                name=r["name"],
                slug=r["slug"],
                task_category=r["task_category"],
                modality=r["modality"],
                primary_metric=r["primary_metric"],
                metric_unit=r["metric_unit"],
                higher_is_better=r["higher_is_better"],
                description=r["description"]
            )
            for r in results
        ]

    async def get_benchmark_by_slug(
        self,
        slug: str,
        db
    ) -> Optional[BenchmarkDefinition]:
        """Get a specific benchmark by slug"""
        query = """
            SELECT
                id::text,
                name,
                slug,
                task_category,
                modality,
                primary_metric,
                metric_unit,
                higher_is_better,
                description
            FROM benchmark_definitions
            WHERE slug = :slug
        """

        result = await db.fetch_one(query, {"slug": slug})

        if not result:
            return None

        return BenchmarkDefinition(
            id=str(result["id"]),
            name=result["name"],
            slug=result["slug"],
            task_category=result["task_category"],
            modality=result["modality"],
            primary_metric=result["primary_metric"],
            metric_unit=result["metric_unit"],
            higher_is_better=result["higher_is_better"],
            description=result["description"]
        )

    async def get_current_sota(
        self,
        benchmark_slug: str,
        db
    ) -> Optional[SOTAEntry]:
        """
        Get current state-of-the-art for a benchmark.
        """
        query = """
            SELECT
                bd.id::text as benchmark_id,
                bd.name as benchmark_name,
                bd.higher_is_better,
                sh.paper_id,
                p.title as paper_title,
                sh.value,
                sh.achieved_date,
                sh.model_name,
                sh.model_size,
                sh.details
            FROM benchmark_definitions bd
            JOIN sota_history sh ON bd.id = sh.benchmark_id
            JOIN papers p ON sh.paper_id = p.id
            WHERE bd.slug = :slug
            ORDER BY
                CASE WHEN bd.higher_is_better THEN sh.value ELSE -sh.value END DESC,
                sh.achieved_date DESC
            LIMIT 1
        """

        result = await db.fetch_one(query, {"slug": benchmark_slug})

        if not result:
            return None

        return SOTAEntry(
            benchmark_id=result["benchmark_id"],
            benchmark_name=result["benchmark_name"],
            paper_id=result["paper_id"],
            paper_title=result["paper_title"],
            value=result["value"],
            achieved_date=result["achieved_date"],
            model_name=result["model_name"],
            model_size=result["model_size"],
            details=result["details"]
        )

    async def get_sota_history(
        self,
        benchmark_slug: str,
        db,
        limit: int = 20
    ) -> List[SOTAEntry]:
        """
        Get SOTA progression over time for a benchmark.

        Shows how SOTA has improved over time.
        """
        query = """
            WITH ranked AS (
                SELECT
                    bd.id::text as benchmark_id,
                    bd.name as benchmark_name,
                    bd.higher_is_better,
                    sh.paper_id,
                    p.title as paper_title,
                    sh.value,
                    sh.achieved_date,
                    sh.model_name,
                    sh.model_size,
                    sh.details,
                    ROW_NUMBER() OVER (
                        PARTITION BY sh.achieved_date
                        ORDER BY
                            CASE WHEN bd.higher_is_better THEN sh.value ELSE -sh.value END DESC
                    ) as rn
                FROM benchmark_definitions bd
                JOIN sota_history sh ON bd.id = sh.benchmark_id
                JOIN papers p ON sh.paper_id = p.id
                WHERE bd.slug = :slug
            )
            SELECT *
            FROM ranked
            WHERE rn = 1
            ORDER BY achieved_date DESC
            LIMIT :limit
        """

        results = await db.fetch_all(query, {
            "slug": benchmark_slug,
            "limit": limit
        })

        return [
            SOTAEntry(
                benchmark_id=r["benchmark_id"],
                benchmark_name=r["benchmark_name"],
                paper_id=r["paper_id"],
                paper_title=r["paper_title"],
                value=r["value"],
                achieved_date=r["achieved_date"],
                model_name=r["model_name"],
                model_size=r["model_size"],
                details=r["details"]
            )
            for r in results
        ]

    async def get_leaderboard(
        self,
        benchmark_slug: str,
        db,
        limit: int = 20
    ) -> List[LeaderboardEntry]:
        """
        Get full leaderboard for a benchmark.

        Returns all papers ranked by performance.
        """
        # First get benchmark details
        benchmark = await self.get_benchmark_by_slug(benchmark_slug, db)
        if not benchmark:
            return []

        # Get current SOTA for marking
        current_sota = await self.get_current_sota(benchmark_slug, db)

        query = """
            SELECT
                sh.paper_id,
                p.title as paper_title,
                sh.value,
                sh.model_name,
                sh.model_size,
                sh.achieved_date,
                ROW_NUMBER() OVER (
                    ORDER BY
                        CASE WHEN :higher_is_better THEN sh.value ELSE -sh.value END DESC,
                        sh.achieved_date ASC
                ) as rank
            FROM sota_history sh
            JOIN benchmark_definitions bd ON sh.benchmark_id = bd.id
            JOIN papers p ON sh.paper_id = p.id
            WHERE bd.slug = :slug
            ORDER BY rank
            LIMIT :limit
        """

        results = await db.fetch_all(query, {
            "slug": benchmark_slug,
            "higher_is_better": benchmark.higher_is_better,
            "limit": limit
        })

        return [
            LeaderboardEntry(
                rank=r["rank"],
                paper_id=r["paper_id"],
                paper_title=r["paper_title"],
                value=r["value"],
                model_name=r["model_name"],
                model_size=r["model_size"],
                achieved_date=r["achieved_date"],
                is_current_sota=(
                    current_sota and r["paper_id"] == current_sota.paper_id
                )
            )
            for r in results
        ]

    async def add_sota_entry(
        self,
        benchmark_slug: str,
        paper_id: str,
        value: float,
        db,
        achieved_date: Optional[date] = None,
        model_name: Optional[str] = None,
        model_size: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        is_verified: bool = False
    ) -> bool:
        """
        Add a new SOTA entry.

        Args:
            benchmark_slug: Benchmark to add entry for
            paper_id: Paper achieving this result
            value: Performance value
            achieved_date: When this was achieved (defaults to paper's publish date)
            model_name: Name of the model/method
            model_size: Size of the model
            details: Additional details (compute, training data, etc.)
            is_verified: Whether this has been manually verified

        Returns:
            True if successfully added
        """
        # Get benchmark ID
        benchmark = await self.get_benchmark_by_slug(benchmark_slug, db)
        if not benchmark:
            self.log_error(f"Benchmark not found: {benchmark_slug}")
            return False

        # Get paper's published date if not provided
        if not achieved_date:
            paper_query = """
                SELECT published_date FROM papers WHERE id = :paper_id
            """
            paper = await db.fetch_one(paper_query, {"paper_id": paper_id})
            if paper and paper["published_date"]:
                achieved_date = paper["published_date"].date() if hasattr(paper["published_date"], 'date') else paper["published_date"]
            else:
                achieved_date = date.today()

        # Insert entry - convert benchmark_id to string for proper UUID binding
        benchmark_id_str = str(benchmark.id)
        insert_query = """
            INSERT INTO sota_history
            (benchmark_id, paper_id, value, achieved_date, model_name, model_size, details, is_verified)
            VALUES
            (:benchmark_id, :paper_id, :value, :achieved_date, :model_name, :model_size, :details, :is_verified)
            ON CONFLICT (benchmark_id, paper_id, achieved_date) DO UPDATE SET
                value = EXCLUDED.value,
                model_name = EXCLUDED.model_name,
                model_size = EXCLUDED.model_size,
                details = EXCLUDED.details,
                is_verified = EXCLUDED.is_verified
        """

        try:
            await db.execute(insert_query, {
                "benchmark_id": benchmark_id_str,
                "paper_id": paper_id,
                "value": value,
                "achieved_date": achieved_date,
                "model_name": model_name,
                "model_size": model_size,
                "details": json.dumps(details) if details else None,
                "is_verified": is_verified
            })
            return True

        except Exception as e:
            self.log_error(f"Error adding SOTA entry", error=e)
            return False

    async def extract_benchmarks_from_paper(
        self,
        paper: Dict[str, Any],
        db
    ) -> List[Dict[str, Any]]:
        """
        Extract benchmark results from a paper's deep analysis.

        Looks for reported results in the structured analysis data.
        """
        extracted = []

        deep_analysis = paper.get("deep_analysis") or {}
        if isinstance(deep_analysis, str):
            try:
                deep_analysis = json.loads(deep_analysis)
            except json.JSONDecodeError:
                deep_analysis = {}
        artifacts = deep_analysis.get("extracted_artifacts") or {}

        # Check for benchmark results in technical_depth
        technical = deep_analysis.get("technical_depth") or {}

        # This would be enhanced with LLM extraction in production
        # For now, look for existing benchmark table in paper

        return extracted

    async def compare_paper_to_sota(
        self,
        paper_id: str,
        db
    ) -> Dict[str, Any]:
        """
        Compare a paper's results to current SOTA across all benchmarks.
        """
        # Get paper's benchmark entries
        query = """
            SELECT
                bd.name as benchmark_name,
                bd.slug as benchmark_slug,
                bd.primary_metric,
                bd.higher_is_better,
                sh.value as paper_value,
                sh.model_name,
                (
                    SELECT MAX(CASE WHEN bd.higher_is_better THEN sh2.value ELSE -sh2.value END)
                    FROM sota_history sh2
                    WHERE sh2.benchmark_id = bd.id
                ) as sota_value
            FROM sota_history sh
            JOIN benchmark_definitions bd ON sh.benchmark_id = bd.id
            WHERE sh.paper_id = :paper_id
        """

        results = await db.fetch_all(query, {"paper_id": paper_id})

        comparisons = []
        for r in results:
            if r["higher_is_better"]:
                delta = r["paper_value"] - r["sota_value"]
                delta_pct = (delta / r["sota_value"] * 100) if r["sota_value"] else 0
                is_sota = r["paper_value"] >= r["sota_value"]
            else:
                delta = r["sota_value"] - r["paper_value"]
                delta_pct = (delta / r["sota_value"] * 100) if r["sota_value"] else 0
                is_sota = r["paper_value"] <= r["sota_value"]

            comparisons.append({
                "benchmark": r["benchmark_name"],
                "benchmark_slug": r["benchmark_slug"],
                "metric": r["primary_metric"],
                "paper_value": r["paper_value"],
                "sota_value": abs(r["sota_value"]),
                "delta": delta,
                "delta_percent": round(delta_pct, 2),
                "is_sota": is_sota,
                "model_name": r["model_name"]
            })

        return {
            "paper_id": paper_id,
            "comparisons": comparisons,
            "is_sota_on_any": any(c["is_sota"] for c in comparisons)
        }


# Singleton instance
_benchmark_service = None

def get_benchmark_service() -> BenchmarkService:
    """Get singleton benchmark service instance"""
    global _benchmark_service
    if _benchmark_service is None:
        _benchmark_service = BenchmarkService()
    return _benchmark_service
