"""
Ingestion API Endpoints

Provides API access to paper ingestion:
- Trigger manual ingestion
- Check ingestion status
- View ingestion history
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.daily_ingestion_service import get_daily_ingestion_service
from app.core.config import settings


router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


# ============================================================================
# Request/Response Models
# ============================================================================

class IngestionRequest(BaseModel):
    """Request to trigger paper ingestion"""
    categories: Optional[List[str]] = Field(
        None,
        description="arXiv categories to fetch (default: all AI categories)"
    )
    max_per_category: int = Field(
        100,
        ge=10,
        le=500,
        description="Maximum papers to fetch per category"
    )
    days_back: int = Field(
        2,
        ge=1,
        le=7,
        description="How many days back to look for papers"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["cs.AI", "cs.LG", "cs.CV"],
                "max_per_category": 100,
                "days_back": 2
            }
        }


class IngestionStatus(BaseModel):
    """Current ingestion status"""
    is_running: bool
    last_run: Optional[str]
    last_stats: dict
    catalog_path: str
    catalog_exists: bool


class IngestionResult(BaseModel):
    """Result of an ingestion run"""
    status: str
    message: str
    stats: Optional[dict] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/status", response_model=IngestionStatus)
async def get_ingestion_status():
    """
    Get current ingestion service status.

    Returns information about:
    - Whether ingestion is currently running
    - When the last ingestion was run
    - Statistics from the last run
    """
    service = get_daily_ingestion_service()
    return service.get_status()


@router.post("/trigger", response_model=IngestionResult)
async def trigger_ingestion(
    request: IngestionRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger a paper ingestion run.

    This will fetch recent papers from arXiv for the specified categories,
    deduplicate against existing papers, and append new ones to the atlas.

    The ingestion runs in the background - check /status for progress.
    """
    service = get_daily_ingestion_service()

    if service.is_running:
        return IngestionResult(
            status="already_running",
            message="Ingestion is already in progress. Check /status for updates."
        )

    # Run ingestion in background
    async def run_background_ingestion():
        await service.run_ingestion(
            categories=request.categories,
            max_per_category=request.max_per_category,
            days_back=request.days_back,
            generate_embeddings=False  # Embeddings are expensive, run separately
        )

    background_tasks.add_task(run_background_ingestion)

    return IngestionResult(
        status="started",
        message=f"Ingestion started for {len(request.categories or settings.DEFAULT_AI_CATEGORIES)} categories. "
                "Check /ingestion/status for progress."
    )


@router.post("/trigger-sync", response_model=IngestionResult)
async def trigger_ingestion_sync(request: IngestionRequest):
    """
    Trigger a paper ingestion run synchronously.

    Unlike /trigger, this waits for the ingestion to complete before returning.
    Useful for smaller ingestions or when you need immediate results.

    Note: May timeout for large ingestions. Use /trigger for background processing.
    """
    service = get_daily_ingestion_service()

    if service.is_running:
        return IngestionResult(
            status="already_running",
            message="Ingestion is already in progress. Check /status for updates."
        )

    stats = await service.run_ingestion(
        categories=request.categories,
        max_per_category=request.max_per_category,
        days_back=request.days_back,
        generate_embeddings=False
    )

    return IngestionResult(
        status=stats.get("status", "unknown"),
        message=f"Ingested {stats.get('papers_appended', 0)} new papers",
        stats=stats
    )


@router.get("/categories")
async def get_available_categories():
    """
    Get list of available arXiv categories for ingestion.

    Returns the default AI-related categories configured for this system.
    """
    return {
        "default_categories": settings.DEFAULT_AI_CATEGORIES,
        "description": "These are the default arXiv categories used for paper ingestion. "
                       "You can specify a subset when triggering ingestion."
    }
