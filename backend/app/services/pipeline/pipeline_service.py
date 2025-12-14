"""
Pipeline Service - Job Creation and Pipeline Orchestration

Manages the creation and tracking of enrichment jobs:
- Create jobs for individual papers or batches
- Priority-based job scheduling
- Pipeline run tracking for batch operations
- Health monitoring via database views
"""

import json
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import IntEnum
from dataclasses import dataclass

from app.db.database import database

logger = logging.getLogger(__name__)


class JobPriority(IntEnum):
    """Priority levels for job processing."""
    LOW = 25
    NORMAL = 50
    HIGH = 75
    CRITICAL = 100


class JobType:
    """Available job types matching the database enum."""
    INGEST = "ingest"
    EMBEDDING = "embedding"
    AI_ANALYSIS = "ai_analysis"
    CITATIONS = "citations"
    CONCEPTS = "concepts"
    TECHNIQUES = "techniques"
    BENCHMARKS = "benchmarks"
    GITHUB = "github"
    DEEP_ANALYSIS = "deep_analysis"
    RELATIONSHIPS = "relationships"
    FULL_ENRICHMENT = "full_enrichment"
    BATCH_INGEST = "batch_ingest"


# Map job types to their rate limit providers
JOB_RATE_LIMIT_PROVIDERS = {
    JobType.EMBEDDING: "local",
    JobType.AI_ANALYSIS: "gemini",
    JobType.CITATIONS: "semantic_scholar",
    JobType.CONCEPTS: "gemini",
    JobType.TECHNIQUES: "gemini",
    JobType.BENCHMARKS: "gemini",
    JobType.GITHUB: "github",
    JobType.DEEP_ANALYSIS: "gemini",
    JobType.RELATIONSHIPS: "local",
}


@dataclass
class EnrichmentStages:
    """Defines enrichment stages and their dependencies."""

    # Order of execution (respects dependencies)
    EXECUTION_ORDER = [
        JobType.EMBEDDING,      # First - needed for relationships
        JobType.AI_ANALYSIS,    # Can run early
        JobType.CITATIONS,      # External API
        JobType.CONCEPTS,       # LLM
        JobType.TECHNIQUES,     # LLM
        JobType.BENCHMARKS,     # LLM
        JobType.GITHUB,         # External API
        JobType.DEEP_ANALYSIS,  # LLM - depends on basic analysis
        JobType.RELATIONSHIPS,  # Last - needs embeddings
    ]

    # Stages that use Gemini LLM
    LLM_STAGES = {JobType.AI_ANALYSIS, JobType.CONCEPTS, JobType.TECHNIQUES,
                  JobType.BENCHMARKS, JobType.DEEP_ANALYSIS}

    # Stages that call external APIs
    EXTERNAL_API_STAGES = {JobType.CITATIONS, JobType.GITHUB}

    # Stages that run locally (no rate limit)
    LOCAL_STAGES = {JobType.EMBEDDING, JobType.RELATIONSHIPS}


class PipelineService:
    """
    Service for job creation and pipeline orchestration.

    Handles:
    - Creating jobs in the processing_jobs table
    - Tracking pipeline runs for batch operations
    - Querying pipeline health and job status
    """

    async def create_job(
        self,
        job_type: str,
        paper_id: Optional[str] = None,
        priority: int = JobPriority.NORMAL,
        batch_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Create a single job in the queue.

        Returns the job ID if created, None if duplicate (idempotency).
        """
        # Generate idempotency key to prevent duplicates
        idempotency_key = f"{job_type}:{paper_id or 'batch'}:{batch_id or 'single'}"

        query = """
            INSERT INTO processing_jobs (
                job_type, paper_id, batch_id, priority,
                idempotency_key, metadata
            ) VALUES (
                :job_type, :paper_id, :batch_id, :priority,
                :idempotency_key, :metadata
            )
            ON CONFLICT (idempotency_key) DO NOTHING
            RETURNING id
        """

        import json
        result = await database.fetch_one(query, {
            "job_type": job_type,
            "paper_id": paper_id,
            "batch_id": batch_id,
            "priority": priority,
            "idempotency_key": idempotency_key,
            "metadata": json.dumps(metadata or {})
        })

        return result["id"] if result else None

    async def create_enrichment_jobs(
        self,
        paper_ids: List[str],
        stages: Optional[List[str]] = None,
        priority: int = JobPriority.NORMAL,
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create enrichment jobs for multiple papers.

        Args:
            paper_ids: List of paper IDs to enrich
            stages: List of stages to run (None = all stages)
            priority: Job priority
            batch_id: Optional batch ID to group jobs

        Returns:
            Summary of created jobs
        """
        if not batch_id:
            batch_id = str(uuid.uuid4())

        stages = stages or EnrichmentStages.EXECUTION_ORDER

        created = 0
        skipped = 0

        for paper_id in paper_ids:
            for stage in stages:
                if stage not in EnrichmentStages.EXECUTION_ORDER:
                    continue

                job_id = await self.create_job(
                    job_type=stage,
                    paper_id=paper_id,
                    priority=priority,
                    batch_id=batch_id
                )

                if job_id:
                    created += 1
                else:
                    skipped += 1

        logger.info(f"Created {created} jobs, skipped {skipped} duplicates (batch: {batch_id})")

        return {
            "batch_id": batch_id,
            "paper_count": len(paper_ids),
            "stages": stages,
            "jobs_created": created,
            "jobs_skipped": skipped,
            "priority": priority
        }

    async def create_backfill_jobs(
        self,
        stages: Optional[List[str]] = None,
        max_papers: Optional[int] = None,
        priority: int = JobPriority.NORMAL,
        min_completeness: int = 0,
        max_completeness: int = 99,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create backfill jobs for papers needing processing.

        Args:
            stages: Stages to backfill (None = auto-detect per paper)
            max_papers: Maximum papers to process
            priority: Job priority
            min_completeness: Minimum completeness score
            max_completeness: Maximum completeness score (papers to include)
            published_after: Only process papers published after this date (YYYY-MM-DD)
            published_before: Only process papers published before this date (YYYY-MM-DD)

        Returns:
            Summary of created jobs
        """
        batch_id = str(uuid.uuid4())

        # Build dynamic WHERE clause for date filtering
        date_conditions = ""
        if published_after:
            date_conditions += " AND p.published_date >= :published_after"
        if published_before:
            date_conditions += " AND p.published_date <= :published_before"

        # Get papers needing processing
        # Only apply LIMIT if max_papers is explicitly set
        limit_clause = "LIMIT :max_papers" if max_papers else ""

        query = f"""
            SELECT
                pps.paper_id,
                pps.completeness_score,
                pps.embedding_at IS NULL as needs_embedding,
                pps.ai_analysis_at IS NULL as needs_ai_analysis,
                pps.citations_at IS NULL as needs_citations,
                pps.concepts_at IS NULL as needs_concepts,
                pps.techniques_at IS NULL as needs_techniques,
                pps.benchmarks_at IS NULL as needs_benchmarks,
                pps.github_at IS NULL as needs_github,
                pps.deep_analysis_at IS NULL as needs_deep_analysis,
                pps.relationships_at IS NULL as needs_relationships,
                p.published_date
            FROM paper_processing_state pps
            JOIN papers p ON pps.paper_id = p.id
            WHERE pps.completeness_score >= :min_completeness
            AND pps.completeness_score <= :max_completeness
            AND pps.error_count < 5
            {date_conditions}
            ORDER BY pps.priority DESC, pps.completeness_score ASC
            {limit_clause}
        """

        params = {
            "min_completeness": min_completeness,
            "max_completeness": max_completeness,
        }
        if max_papers:
            params["max_papers"] = max_papers
        if published_after:
            params["published_after"] = datetime.strptime(published_after, "%Y-%m-%d")
        if published_before:
            params["published_before"] = datetime.strptime(published_before, "%Y-%m-%d")

        rows = await database.fetch_all(query, params)

        created = 0

        for row in rows:
            paper_id = row["paper_id"]

            # Determine which stages this paper needs
            if stages:
                paper_stages = stages
            else:
                paper_stages = []
                if row["needs_embedding"]:
                    paper_stages.append(JobType.EMBEDDING)
                if row["needs_ai_analysis"]:
                    paper_stages.append(JobType.AI_ANALYSIS)
                if row["needs_citations"]:
                    paper_stages.append(JobType.CITATIONS)
                if row["needs_concepts"]:
                    paper_stages.append(JobType.CONCEPTS)
                if row["needs_techniques"]:
                    paper_stages.append(JobType.TECHNIQUES)
                if row["needs_benchmarks"]:
                    paper_stages.append(JobType.BENCHMARKS)
                if row["needs_github"]:
                    paper_stages.append(JobType.GITHUB)
                if row["needs_deep_analysis"]:
                    paper_stages.append(JobType.DEEP_ANALYSIS)
                if row["needs_relationships"]:
                    paper_stages.append(JobType.RELATIONSHIPS)

            # Create jobs for needed stages
            for stage in paper_stages:
                job_id = await self.create_job(
                    job_type=stage,
                    paper_id=paper_id,
                    priority=priority,
                    batch_id=batch_id
                )
                if job_id:
                    created += 1

        # Create pipeline run record
        await self._create_pipeline_run(
            run_type="backfill",
            batch_id=batch_id,
            total_items=len(rows),
            config={
                "stages": stages,
                "priority": priority,
                "min_completeness": min_completeness,
                "max_completeness": max_completeness
            }
        )

        logger.info(f"Backfill created {created} jobs for {len(rows)} papers (batch: {batch_id})")

        return {
            "batch_id": batch_id,
            "papers_found": len(rows),
            "jobs_created": created,
            "priority": priority,
            "completeness_range": f"{min_completeness}-{max_completeness}"
        }

    async def _create_pipeline_run(
        self,
        run_type: str,
        batch_id: str,
        total_items: int,
        config: Dict[str, Any]
    ) -> int:
        """Create a pipeline run record for tracking."""
        query = """
            INSERT INTO pipeline_runs (
                run_type, status, config, total_items, started_at
            ) VALUES (
                :run_type, 'processing', :config, :total_items, NOW()
            )
            RETURNING id
        """
        result = await database.fetch_one(query, {
            "run_type": run_type,
            "config": json.dumps({**config, "batch_id": batch_id}, default=str),
            "total_items": total_items
        })
        return result["id"]

    async def get_pipeline_health(self) -> Dict[str, Any]:
        """Get pipeline health metrics from the v_pipeline_health view."""
        query = "SELECT metric, value FROM v_pipeline_health"
        rows = await database.fetch_all(query)

        metrics = {row["metric"]: row["value"] for row in rows}

        # Get job queue status
        queue_query = """
            SELECT job_type, status, COUNT(*) as count
            FROM processing_jobs
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY job_type, status
        """
        queue_rows = await database.fetch_all(queue_query)

        job_status = {}
        for row in queue_rows:
            job_type = row["job_type"]
            if job_type not in job_status:
                job_status[job_type] = {}
            job_status[job_type][row["status"]] = row["count"]

        return {
            "metrics": metrics,
            "job_queue": job_status,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_jobs(
        self,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
        paper_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get jobs with optional filters."""
        conditions = ["1=1"]
        params = {"limit": limit, "offset": offset}

        if status:
            conditions.append("status = :status")
            params["status"] = status
        if job_type:
            conditions.append("job_type = :job_type")
            params["job_type"] = job_type
        if paper_id:
            conditions.append("paper_id = :paper_id")
            params["paper_id"] = paper_id
        if batch_id:
            conditions.append("batch_id = :batch_id")
            params["batch_id"] = str(batch_id)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT
                id, job_type, status, paper_id, batch_id,
                priority, created_at, started_at, completed_at,
                error_message, retry_count, worker_id
            FROM processing_jobs
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """

        rows = await database.fetch_all(query, params)

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM processing_jobs WHERE {where_clause}"
        count_result = await database.fetch_one(count_query, params)

        return {
            "jobs": [
                {
                    "id": row["id"],
                    "job_type": row["job_type"],
                    "status": row["status"],
                    "paper_id": row["paper_id"],
                    "batch_id": str(row["batch_id"]) if row["batch_id"] else None,
                    "priority": row["priority"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "started_at": row["started_at"].isoformat() if row["started_at"] else None,
                    "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
                    "error_message": row["error_message"],
                    "retry_count": row["retry_count"],
                    "worker_id": row["worker_id"]
                }
                for row in rows
            ],
            "total": count_result["total"],
            "limit": limit,
            "offset": offset
        }

    async def retry_job(self, job_id: int) -> bool:
        """Manually retry a failed job."""
        query = """
            UPDATE processing_jobs
            SET status = 'pending',
                started_at = NULL,
                completed_at = NULL,
                worker_id = NULL,
                error_message = NULL
            WHERE id = :job_id
            AND status = 'failed'
            RETURNING id
        """
        result = await database.fetch_one(query, {"job_id": job_id})
        return result is not None

    async def cancel_job(self, job_id: int) -> bool:
        """Cancel a pending job."""
        query = """
            UPDATE processing_jobs
            SET status = 'cancelled'
            WHERE id = :job_id
            AND status = 'pending'
            RETURNING id
        """
        result = await database.fetch_one(query, {"job_id": job_id})
        return result is not None

    async def cancel_batch(self, batch_id: str) -> int:
        """Cancel all pending jobs in a batch."""
        query = """
            UPDATE processing_jobs
            SET status = 'cancelled'
            WHERE batch_id = :batch_id
            AND status = 'pending'
        """
        result = await database.execute(query, {"batch_id": batch_id})
        return result

    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get detailed processing statistics."""
        # Completeness distribution
        completeness_query = """
            SELECT
                CASE
                    WHEN completeness_score = 0 THEN '0%'
                    WHEN completeness_score < 25 THEN '1-24%'
                    WHEN completeness_score < 50 THEN '25-49%'
                    WHEN completeness_score < 75 THEN '50-74%'
                    WHEN completeness_score < 100 THEN '75-99%'
                    ELSE '100%'
                END as bucket,
                COUNT(*) as count
            FROM paper_processing_state
            GROUP BY bucket
            ORDER BY bucket
        """
        completeness_rows = await database.fetch_all(completeness_query)

        # Stage completion stats
        stage_query = """
            SELECT
                SUM(CASE WHEN embedding_at IS NOT NULL THEN 1 ELSE 0 END) as embedding,
                SUM(CASE WHEN ai_analysis_at IS NOT NULL THEN 1 ELSE 0 END) as ai_analysis,
                SUM(CASE WHEN citations_at IS NOT NULL THEN 1 ELSE 0 END) as citations,
                SUM(CASE WHEN concepts_at IS NOT NULL THEN 1 ELSE 0 END) as concepts,
                SUM(CASE WHEN techniques_at IS NOT NULL THEN 1 ELSE 0 END) as techniques,
                SUM(CASE WHEN benchmarks_at IS NOT NULL THEN 1 ELSE 0 END) as benchmarks,
                SUM(CASE WHEN github_at IS NOT NULL THEN 1 ELSE 0 END) as github,
                SUM(CASE WHEN deep_analysis_at IS NOT NULL THEN 1 ELSE 0 END) as deep_analysis,
                SUM(CASE WHEN relationships_at IS NOT NULL THEN 1 ELSE 0 END) as relationships,
                COUNT(*) as total
            FROM paper_processing_state
        """
        stage_row = await database.fetch_one(stage_query)

        # Recent job throughput
        throughput_query = """
            SELECT
                job_type,
                COUNT(*) as completed_24h,
                AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_sec
            FROM processing_jobs
            WHERE status = 'completed'
            AND completed_at > NOW() - INTERVAL '24 hours'
            GROUP BY job_type
        """
        throughput_rows = await database.fetch_all(throughput_query)

        return {
            "completeness_distribution": {
                row["bucket"]: row["count"] for row in completeness_rows
            },
            "stage_completion": {
                "embedding": stage_row["embedding"],
                "ai_analysis": stage_row["ai_analysis"],
                "citations": stage_row["citations"],
                "concepts": stage_row["concepts"],
                "techniques": stage_row["techniques"],
                "benchmarks": stage_row["benchmarks"],
                "github": stage_row["github"],
                "deep_analysis": stage_row["deep_analysis"],
                "relationships": stage_row["relationships"],
                "total_papers": stage_row["total"]
            },
            "throughput_24h": {
                row["job_type"]: {
                    "completed": row["completed_24h"],
                    "avg_duration_sec": round(row["avg_duration_sec"], 2) if row["avg_duration_sec"] else None
                }
                for row in throughput_rows
            }
        }


# Singleton instance
_pipeline_service: Optional[PipelineService] = None


def get_pipeline_service() -> PipelineService:
    """Get or create the pipeline service singleton."""
    global _pipeline_service
    if _pipeline_service is None:
        _pipeline_service = PipelineService()
    return _pipeline_service
