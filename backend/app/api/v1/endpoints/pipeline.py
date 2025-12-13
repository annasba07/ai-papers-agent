"""
Pipeline API Endpoints - Control the enrichment pipeline

Provides endpoints for:
- Starting/stopping worker pools
- Creating backfill and enrichment jobs
- Monitoring pipeline health and job status
- Managing individual jobs
"""

from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional, List
from pydantic import BaseModel, Field

from datetime import datetime

from app.services.pipeline.pipeline_service import (
    get_pipeline_service,
    JobPriority,
    JobType,
    EnrichmentStages,
)
from app.services.pipeline.rate_limiter import get_rate_limiter
from app.workers.worker_pool import get_worker_pool
from app.services.daily_ingestion_service import get_daily_ingestion_service
from app.core.config import settings

router = APIRouter(prefix="/pipeline")


# ============== Request/Response Models ==============

class BackfillRequest(BaseModel):
    """Request to start a backfill operation."""
    stages: Optional[List[str]] = Field(
        None,
        description="Stages to backfill (None = auto-detect per paper)"
    )
    max_papers: Optional[int] = Field(
        1000,
        description="Maximum papers to process"
    )
    priority: int = Field(
        JobPriority.NORMAL,
        description="Job priority (25=LOW, 50=NORMAL, 75=HIGH, 100=CRITICAL)"
    )
    min_completeness: int = Field(
        0,
        description="Minimum completeness score"
    )
    max_completeness: int = Field(
        99,
        description="Maximum completeness score (papers to include)"
    )
    published_after: Optional[str] = Field(
        None,
        description="Only process papers published after this date (YYYY-MM-DD), e.g. '2024-01-01'"
    )
    published_before: Optional[str] = Field(
        None,
        description="Only process papers published before this date (YYYY-MM-DD), e.g. '2024-12-31'"
    )


class EnrichRequest(BaseModel):
    """Request to enrich specific papers."""
    paper_ids: List[str] = Field(..., description="Paper IDs to enrich")
    stages: Optional[List[str]] = Field(
        None,
        description="Stages to run (None = all stages)"
    )
    priority: int = Field(
        JobPriority.HIGH,
        description="Job priority"
    )


class WorkerConfig(BaseModel):
    """Configuration for a worker pool."""
    count: int = Field(..., description="Number of workers")


class StartWorkersRequest(BaseModel):
    """Request to start worker pools."""
    llm: Optional[WorkerConfig] = Field(
        None,
        description="LLM worker configuration (default: 15 workers)"
    )
    citations: Optional[WorkerConfig] = Field(
        None,
        description="Citation worker configuration (default: 2 workers)"
    )
    github: Optional[WorkerConfig] = Field(
        None,
        description="GitHub worker configuration (default: 3 workers)"
    )
    local: Optional[WorkerConfig] = Field(
        None,
        description="Local worker configuration (default: 4 workers)"
    )


class ScalePoolRequest(BaseModel):
    """Request to scale a worker pool."""
    count: int = Field(..., description="New worker count")


class ArxivIngestRequest(BaseModel):
    """Request to ingest papers from arXiv with auto-enrichment."""
    categories: Optional[List[str]] = Field(
        None,
        description="arXiv categories to fetch (default: all AI categories)"
    )
    max_per_category: int = Field(
        50000,
        ge=10,
        le=100000,
        description="Safety limit for papers per category"
    )
    days_back: int = Field(
        2,
        ge=1,
        le=365,
        description="Fallback: how many days back (if since_date not provided)"
    )
    since_date: Optional[str] = Field(
        None,
        description="Fetch ALL papers since this date (YYYY-MM-DD), e.g. '2024-01-01'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["cs.AI", "cs.LG"],
                "since_date": "2024-12-01",
                "max_per_category": 50000
            }
        }


# ============== Ingestion + Enrichment Endpoint ==============

@router.post("/arxiv-ingest")
async def arxiv_ingest(request: ArxivIngestRequest, background_tasks: BackgroundTasks):
    """
    Unified endpoint: Ingest papers from arXiv with automatic enrichment job creation.

    This endpoint:
    1. Fetches papers from arXiv for specified categories since the given date
    2. Inserts new papers directly to PostgreSQL (deduplicates automatically)
    3. Database triggers auto-create enrichment jobs for all 9 stages
    4. Workers (if running) will process jobs automatically

    The ingestion runs in the background. Check /pipeline/status for progress.

    Example:
    ```
    POST /pipeline/arxiv-ingest
    {
        "categories": ["cs.AI", "cs.LG", "cs.CV"],
        "since_date": "2024-01-01"
    }
    ```

    Returns info about the ingestion job. New papers will have enrichment jobs
    created at HIGH priority (75) via database triggers.
    """
    service = get_daily_ingestion_service()

    if service.is_running:
        return {
            "status": "already_running",
            "message": "Ingestion is already in progress. Check /pipeline/status for updates."
        }

    # Parse since_date if provided
    since_date = None
    if request.since_date:
        try:
            since_date = datetime.strptime(request.since_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid since_date format: {request.since_date}. Use YYYY-MM-DD."
            )

    # Use default categories if not specified
    categories = request.categories or settings.DEFAULT_AI_CATEGORIES

    # Run ingestion in background
    async def run_background_ingestion():
        await service.run_ingestion(
            categories=categories,
            max_per_category=request.max_per_category,
            days_back=request.days_back,
            since_date=since_date,
            generate_embeddings=False,
            write_ndjson_backup=False  # PostgreSQL is primary, no backup needed
        )

    background_tasks.add_task(run_background_ingestion)

    return {
        "status": "started",
        "message": f"Ingestion started for {len(categories)} categories",
        "categories": categories,
        "since_date": request.since_date or f"last {request.days_back} days",
        "max_per_category": request.max_per_category,
        "auto_enrichment": "Enrichment jobs will be created automatically via database triggers",
        "note": "Start workers with POST /pipeline/workers/start if not already running"
    }


# ============== Worker Management Endpoints ==============

@router.post("/workers/start")
async def start_workers(request: Optional[StartWorkersRequest] = None):
    """
    Start the worker pool.

    Workers will begin processing jobs from the queue immediately.
    By default, starts:
    - 15 LLM workers (Gemini tasks)
    - 2 citation workers (Semantic Scholar)
    - 3 GitHub workers
    - 4 local workers (embeddings, relationships)
    """
    pool = get_worker_pool()

    config = None
    if request:
        config = {}
        if request.llm:
            config["llm"] = {"count": request.llm.count}
        if request.citations:
            config["citations"] = {"count": request.citations.count}
        if request.github:
            config["github"] = {"count": request.github.count}
        if request.local:
            config["local"] = {"count": request.local.count}

    result = await pool.start(config)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/workers/stop")
async def stop_workers():
    """
    Gracefully stop all workers.

    Workers will finish their current job before stopping.
    """
    pool = get_worker_pool()
    result = await pool.stop()

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/workers/status")
async def get_worker_status():
    """Get current status of all worker pools."""
    pool = get_worker_pool()
    return pool.get_status()


@router.post("/workers/scale/{pool_name}")
async def scale_worker_pool(pool_name: str, request: ScalePoolRequest):
    """
    Scale a specific worker pool.

    Example: POST /pipeline/workers/scale/llm {"count": 20}
    """
    pool = get_worker_pool()
    result = await pool.scale_pool(pool_name, request.count)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# ============== Job Management Endpoints ==============

@router.post("/backfill")
async def start_backfill(request: BackfillRequest):
    """
    Start a backfill operation for papers needing processing.

    Creates jobs in the processing_jobs table for papers that:
    - Have completeness score in the specified range
    - Have fewer than 5 errors
    - Need the specified stages (or auto-detect)
    - Fall within the optional date range

    Workers will pick up these jobs automatically if running.

    Example:
    ```
    POST /pipeline/backfill
    {
        "max_papers": 1000,
        "priority": 50,
        "stages": ["ai_analysis", "techniques", "benchmarks"],
        "published_after": "2024-01-01",
        "published_before": "2024-12-31"
    }
    ```
    """
    service = get_pipeline_service()

    result = await service.create_backfill_jobs(
        stages=request.stages,
        max_papers=request.max_papers,
        priority=request.priority,
        min_completeness=request.min_completeness,
        max_completeness=request.max_completeness,
        published_after=request.published_after,
        published_before=request.published_before
    )

    return result


@router.post("/enrich/{paper_id}")
async def enrich_paper(paper_id: str, priority: int = Query(default=JobPriority.CRITICAL)):
    """
    Create enrichment jobs for a single paper.

    Jobs are created at CRITICAL priority by default for fast processing.
    """
    service = get_pipeline_service()

    result = await service.create_enrichment_jobs(
        paper_ids=[paper_id],
        stages=None,  # All stages
        priority=priority
    )

    return result


@router.post("/enrich")
async def enrich_papers(request: EnrichRequest):
    """
    Create enrichment jobs for multiple papers.

    Example:
    ```
    POST /pipeline/enrich
    {
        "paper_ids": ["2401.12345", "2401.12346"],
        "stages": ["ai_analysis", "techniques"],
        "priority": 75
    }
    ```
    """
    service = get_pipeline_service()

    result = await service.create_enrichment_jobs(
        paper_ids=request.paper_ids,
        stages=request.stages,
        priority=request.priority
    )

    return result


@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    paper_id: Optional[str] = Query(None, description="Filter by paper ID"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    List jobs with optional filters.

    Status values: pending, processing, completed, failed, cancelled
    Job types: embedding, ai_analysis, citations, concepts, techniques,
               benchmarks, github, deep_analysis, relationships
    """
    service = get_pipeline_service()

    return await service.get_jobs(
        status=status,
        job_type=job_type,
        paper_id=paper_id,
        batch_id=batch_id,
        limit=limit,
        offset=offset
    )


@router.post("/jobs/{job_id}/retry")
async def retry_job(job_id: int):
    """Retry a failed job."""
    service = get_pipeline_service()

    success = await service.retry_job(job_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found or not in failed state"
        )

    return {"success": True, "job_id": job_id}


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: int):
    """Cancel a pending job."""
    service = get_pipeline_service()

    success = await service.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found or not in pending state"
        )

    return {"success": True, "job_id": job_id}


@router.post("/batch/{batch_id}/cancel")
async def cancel_batch(batch_id: str):
    """Cancel all pending jobs in a batch."""
    service = get_pipeline_service()

    cancelled = await service.cancel_batch(batch_id)

    return {"success": True, "batch_id": batch_id, "jobs_cancelled": cancelled}


# ============== Status/Health Endpoints ==============

@router.get("/status")
async def get_pipeline_status():
    """
    Get pipeline health status.

    Includes:
    - Overall metrics (total papers, fully processed, etc.)
    - Job queue status by type and status
    - Worker pool status
    """
    service = get_pipeline_service()
    pool = get_worker_pool()

    health = await service.get_pipeline_health()
    workers = pool.get_status()

    return {
        **health,
        "workers": workers
    }


@router.get("/stats")
async def get_processing_stats():
    """
    Get detailed processing statistics.

    Includes:
    - Completeness distribution
    - Stage completion counts
    - 24-hour throughput by job type
    """
    service = get_pipeline_service()
    return await service.get_processing_stats()


@router.get("/rate-limits")
async def get_rate_limits():
    """Get current rate limit status for all providers."""
    limiter = get_rate_limiter()
    return await limiter.get_all_stats()


@router.get("/rate-limits/{provider}")
async def get_rate_limit(provider: str):
    """Get rate limit status for a specific provider."""
    limiter = get_rate_limiter()
    return await limiter.get_stats(provider)


# ============== Utility Endpoints ==============

@router.get("/stages")
async def list_stages():
    """List all available enrichment stages."""
    return {
        "execution_order": EnrichmentStages.EXECUTION_ORDER,
        "llm_stages": list(EnrichmentStages.LLM_STAGES),
        "external_api_stages": list(EnrichmentStages.EXTERNAL_API_STAGES),
        "local_stages": list(EnrichmentStages.LOCAL_STAGES),
    }


@router.get("/priorities")
async def list_priorities():
    """List available priority levels."""
    return {
        "LOW": JobPriority.LOW,
        "NORMAL": JobPriority.NORMAL,
        "HIGH": JobPriority.HIGH,
        "CRITICAL": JobPriority.CRITICAL,
    }
