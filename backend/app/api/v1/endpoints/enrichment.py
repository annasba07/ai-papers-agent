"""
Enrichment API Endpoints

Provides API access to batch AI enrichment:
- Tier 1: Abstract-only enrichment (fast, cheap)
- Tier 2: Deep PDF-based enrichment (multimodal, comprehensive)
- Trigger enrichment jobs
- Check enrichment status
- Enrich individual papers
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field

from app.services.batch_enrichment_service import get_enrichment_service
from app.services.deep_enrichment_service import get_deep_enrichment_service


router = APIRouter(prefix="/enrichment", tags=["Enrichment"])


# ============================================================================
# Request/Response Models
# ============================================================================

class EnrichmentRequest(BaseModel):
    """Request to trigger batch enrichment."""
    batch_size: int = Field(
        50,
        ge=10,
        le=200,
        description="Papers per batch"
    )
    max_papers: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum papers to process (None = all)"
    )
    skip_existing: bool = Field(
        True,
        description="Skip papers that already have ai_analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "batch_size": 50,
                "max_papers": 1000,
                "skip_existing": True
            }
        }


class EnrichmentStatus(BaseModel):
    """Current enrichment status."""
    enabled: bool
    is_running: bool
    model: str
    stats: Optional[dict] = None


class EnrichmentResult(BaseModel):
    """Result of an enrichment operation."""
    status: str
    message: str
    stats: Optional[dict] = None


class DeepEnrichmentRequest(BaseModel):
    """Request to trigger deep PDF-based enrichment."""
    max_papers: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum papers to process (None = all)"
    )
    priority_filter: Optional[str] = Field(
        None,
        description="SQL filter for priority (e.g., \"(ai_analysis->>'impactScore')::int >= 7\")"
    )
    skip_existing: bool = Field(
        True,
        description="Skip papers that already have deep_analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "max_papers": 100,
                "priority_filter": "(ai_analysis->>'impactScore')::int >= 7",
                "skip_existing": True
            }
        }


class DeepEnrichmentStatus(BaseModel):
    """Current deep enrichment status."""
    enabled: bool
    is_running: bool
    model: str
    pdf_dir: str
    pdf_count: int
    stats: Optional[dict] = None


# ============================================================================
# Endpoints - Tier 1 (Abstract-only)
# ============================================================================

@router.get("/status", response_model=EnrichmentStatus)
async def get_enrichment_status():
    """
    Get current enrichment service status.

    Returns information about:
    - Whether enrichment is enabled (API key configured)
    - Whether an enrichment job is currently running
    - Statistics from the current/last run
    """
    service = get_enrichment_service()
    return service.get_status()


@router.post("/trigger", response_model=EnrichmentResult)
async def trigger_enrichment(
    request: EnrichmentRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger a batch AI enrichment job.

    This will process papers using Gemini 2.5 Flash Lite to generate:
    - Structured AI analysis (summary, novelty, difficulty, etc.)
    - Extracted GitHub/code repository URLs

    The enrichment runs in the background - check /status for progress.
    """
    service = get_enrichment_service()

    if not service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Enrichment service not enabled. Set GOOGLE_API_KEY."
        )

    if service.is_running:
        return EnrichmentResult(
            status="already_running",
            message="Enrichment is already in progress. Check /status for updates.",
            stats=service.get_status().get("stats")
        )

    # Run enrichment in background
    async def run_background_enrichment():
        await service.run_enrichment(
            batch_size=request.batch_size,
            max_papers=request.max_papers,
            skip_existing=request.skip_existing,
        )

    background_tasks.add_task(run_background_enrichment)

    return EnrichmentResult(
        status="started",
        message=f"Enrichment started with batch_size={request.batch_size}. "
                "Check /enrichment/status for progress."
    )


@router.post("/stop", response_model=EnrichmentResult)
async def stop_enrichment():
    """
    Stop the current enrichment job after the current batch completes.
    """
    service = get_enrichment_service()

    if not service.is_running:
        return EnrichmentResult(
            status="not_running",
            message="No enrichment job is currently running."
        )

    service.stop()
    return EnrichmentResult(
        status="stopping",
        message="Stop requested. Will finish current batch and stop."
    )


@router.post("/paper/{paper_id}", response_model=EnrichmentResult)
async def enrich_single_paper(paper_id: str):
    """
    Enrich a single paper by ID.

    Useful for testing or on-demand enrichment.
    """
    service = get_enrichment_service()

    if not service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Enrichment service not enabled. Set GOOGLE_API_KEY."
        )

    analysis = await service.enrich_single_paper(paper_id)

    if analysis:
        return EnrichmentResult(
            status="success",
            message=f"Paper {paper_id} enriched successfully.",
            stats={"analysis_fields": list(analysis.keys())}
        )
    else:
        return EnrichmentResult(
            status="failed",
            message=f"Could not enrich paper {paper_id}. It may not exist or analysis failed."
        )


@router.get("/count")
async def get_enrichment_count():
    """
    Get count of enriched vs unenriched papers in the database.
    """
    from app.db.database import database

    total_query = "SELECT COUNT(*) FROM papers"
    enriched_query = "SELECT COUNT(*) FROM papers WHERE ai_analysis IS NOT NULL"

    total_result = await database.fetch_one(total_query)
    enriched_result = await database.fetch_one(enriched_query)

    total = total_result[0] if total_result else 0
    enriched = enriched_result[0] if enriched_result else 0
    remaining = total - enriched

    return {
        "total_papers": total,
        "enriched": enriched,
        "remaining": remaining,
        "percent_complete": round(100.0 * enriched / total, 1) if total > 0 else 0
    }


@router.get("/test")
async def test_enrichment(
    limit: int = Query(5, ge=1, le=20, description="Number of papers to test with")
):
    """
    Test enrichment on a small sample without saving to database.

    Useful for verifying the service is working before running full batch.
    """
    service = get_enrichment_service()

    if not service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Enrichment service not enabled. Set GOOGLE_API_KEY."
        )

    from app.db.database import database

    # Fetch sample papers
    query = """
        SELECT id, title, abstract
        FROM papers
        WHERE ai_analysis IS NULL
        ORDER BY published_date DESC
        LIMIT :limit
    """
    papers = await database.fetch_all(query, {"limit": limit})

    if not papers:
        return {"status": "no_papers", "message": "No papers without analysis found"}

    results = []
    for paper in papers:
        # Extract code URLs
        code_repos = service.extract_code_urls(paper["abstract"])

        # Test analysis (don't save)
        analysis = await service._analyze_paper(paper["title"], paper["abstract"])

        results.append({
            "id": paper["id"],
            "title": paper["title"][:80] + "..." if len(paper["title"]) > 80 else paper["title"],
            "code_repos": code_repos,
            "analysis_success": analysis is not None,
            "analysis_preview": {
                k: v for k, v in (analysis or {}).items()
                if k in ["impactScore", "difficultyLevel", "hasCode", "researchSignificance"]
            } if analysis else None
        })

    return {
        "status": "ok",
        "tested": len(results),
        "with_code_repos": sum(1 for r in results if r["code_repos"]),
        "analysis_success_rate": sum(1 for r in results if r["analysis_success"]) / len(results) * 100,
        "results": results
    }


# ============================================================================
# Endpoints - Tier 2 (Deep PDF-based enrichment)
# ============================================================================

@router.get("/deep/status", response_model=DeepEnrichmentStatus)
async def get_deep_enrichment_status():
    """
    Get current deep enrichment service status.

    Returns information about:
    - Whether deep enrichment is enabled (API key + PDFs available)
    - Whether a deep enrichment job is currently running
    - PDF directory and count
    - Statistics from the current/last run
    """
    service = get_deep_enrichment_service()
    return service.get_status()


@router.post("/deep/trigger", response_model=EnrichmentResult)
async def trigger_deep_enrichment(
    request: DeepEnrichmentRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger a deep PDF-based enrichment job (Tier 2).

    This uses Gemini 2.0 Flash multimodal to analyze full paper PDFs:
    - Full methodology understanding
    - Figure and table analysis
    - Experimental results extraction
    - Architecture diagram interpretation

    Processing is slower (~1 paper/second) but much richer analysis.
    Runs in the background - check /deep/status for progress.
    """
    service = get_deep_enrichment_service()

    if not service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Deep enrichment service not enabled. Check GOOGLE_API_KEY and PDF directory."
        )

    if service.is_running:
        return EnrichmentResult(
            status="already_running",
            message="Deep enrichment is already in progress. Check /deep/status for updates.",
            stats=service.get_status().get("stats")
        )

    # Run enrichment in background
    async def run_background_deep_enrichment():
        await service.run_deep_enrichment(
            max_papers=request.max_papers,
            priority_filter=request.priority_filter,
            skip_existing=request.skip_existing,
        )

    background_tasks.add_task(run_background_deep_enrichment)

    return EnrichmentResult(
        status="started",
        message="Deep enrichment started. Check /enrichment/deep/status for progress."
    )


@router.post("/deep/stop", response_model=EnrichmentResult)
async def stop_deep_enrichment():
    """
    Stop the current deep enrichment job after the current paper completes.
    """
    service = get_deep_enrichment_service()

    if not service.is_running:
        return EnrichmentResult(
            status="not_running",
            message="No deep enrichment job is currently running."
        )

    service.stop()
    return EnrichmentResult(
        status="stopping",
        message="Stop requested. Will finish current paper and stop."
    )


@router.post("/deep/paper/{paper_id}", response_model=EnrichmentResult)
async def deep_enrich_single_paper(paper_id: str):
    """
    Deep enrich a single paper by ID using PDF analysis.

    Useful for testing or on-demand deep enrichment.
    Requires the PDF to be available in the PDF directory.
    """
    service = get_deep_enrichment_service()

    if not service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Deep enrichment service not enabled. Check GOOGLE_API_KEY and PDF directory."
        )

    analysis = await service.enrich_single_paper(paper_id)

    if analysis:
        return EnrichmentResult(
            status="success",
            message=f"Paper {paper_id} deep enriched successfully.",
            stats={
                "analysis_fields": list(analysis.keys()),
                "has_figures": bool(analysis.get("figures_analysis")),
                "has_methodology": bool(analysis.get("methodology")),
            }
        )
    else:
        return EnrichmentResult(
            status="failed",
            message=f"Could not deep enrich paper {paper_id}. PDF may not exist or analysis failed."
        )


@router.get("/deep/count")
async def get_deep_enrichment_count():
    """
    Get count of deep enriched vs non-enriched papers in the database.
    """
    from app.db.database import database

    total_query = "SELECT COUNT(*) FROM papers"
    deep_enriched_query = "SELECT COUNT(*) FROM papers WHERE deep_analysis IS NOT NULL"
    has_pdf_query = """
        SELECT COUNT(*) FROM papers
        WHERE deep_analysis IS NULL
        AND ai_analysis IS NOT NULL
    """

    total_result = await database.fetch_one(total_query)
    deep_result = await database.fetch_one(deep_enriched_query)
    pending_result = await database.fetch_one(has_pdf_query)

    total = total_result[0] if total_result else 0
    deep_enriched = deep_result[0] if deep_result else 0
    pending = pending_result[0] if pending_result else 0

    return {
        "total_papers": total,
        "deep_enriched": deep_enriched,
        "pending_deep_enrichment": pending,
        "percent_complete": round(100.0 * deep_enriched / total, 1) if total > 0 else 0
    }


# ============================================================================
# Endpoints - Citation Enrichment (OpenAlex)
# ============================================================================

class CitationEnrichmentRequest(BaseModel):
    """Request to trigger citation enrichment."""
    max_papers: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum papers to process (None = all)"
    )
    skip_enriched: bool = Field(
        True,
        description="Skip papers that already have citation_count > 0"
    )
    oldest_first: bool = Field(
        True,
        description="Process oldest papers first (better OpenAlex coverage for papers with time to accumulate citations)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "max_papers": 1000,
                "skip_enriched": True
            }
        }


@router.get("/citations/status")
async def get_citation_enrichment_status():
    """
    Get current citation enrichment service status.

    Returns information about:
    - Whether citation enrichment is running
    - Statistics from the current/last run
    """
    from app.services.citation_enrichment_service import get_citation_enrichment_service
    service = get_citation_enrichment_service()
    return service.get_status()


@router.post("/citations/trigger", response_model=EnrichmentResult)
async def trigger_citation_enrichment(
    request: CitationEnrichmentRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger citation enrichment from OpenAlex.

    This will:
    - Fetch citation counts for each paper from OpenAlex
    - Update papers.citation_count with real citation data
    - Enable citation-based ranking and discovery

    OpenAlex is free and doesn't require an API key.
    Processing is ~100 papers/minute to respect rate limits.
    """
    from app.services.citation_enrichment_service import get_citation_enrichment_service
    service = get_citation_enrichment_service()

    if service.is_running:
        return EnrichmentResult(
            status="already_running",
            message="Citation enrichment is already in progress. Check /citations/status for updates.",
            stats=service.get_status().get("stats")
        )

    async def run_background_citation_enrichment():
        await service.run_citation_enrichment(
            max_papers=request.max_papers,
            skip_enriched=request.skip_enriched,
            oldest_first=request.oldest_first,
        )

    background_tasks.add_task(run_background_citation_enrichment)

    return EnrichmentResult(
        status="started",
        message="Citation enrichment started. Check /enrichment/citations/status for progress."
    )


@router.post("/citations/stop", response_model=EnrichmentResult)
async def stop_citation_enrichment():
    """
    Stop the current citation enrichment job after the current batch completes.
    """
    from app.services.citation_enrichment_service import get_citation_enrichment_service
    service = get_citation_enrichment_service()

    if not service.is_running:
        return EnrichmentResult(
            status="not_running",
            message="No citation enrichment job is currently running."
        )

    service.stop()
    return EnrichmentResult(
        status="stopping",
        message="Stop requested. Will finish current batch and stop."
    )


@router.post("/citations/trigger-prioritized", response_model=EnrichmentResult)
async def trigger_prioritized_citation_enrichment(
    max_papers: Optional[int] = Query(
        None,
        description="Maximum papers to process (None = all)"
    ),
    background_tasks: BackgroundTasks = None
):
    """
    Trigger PRIORITIZED citation enrichment from Semantic Scholar.

    This is ideal for slow API rate limits (public API = 30s/request).
    Papers are processed in priority order:

    1. **deep_analysis papers** - Papers we've already invested in with PDF analysis
    2. **High quality papers** - Papers with quality_score > 50
    3. **Recent papers** - Papers from the last 90 days
    4. **Everything else** - Remaining papers by date

    At 30s per request, we process ~2,880 papers/day.
    This ensures the most valuable papers get citation data first while
    waiting for an API key.

    Use /enrichment/citations/status to monitor progress.
    """
    from app.services.citation_enrichment_service import get_citation_enrichment_service
    service = get_citation_enrichment_service()

    if service.is_running:
        return EnrichmentResult(
            status="already_running",
            message="Citation enrichment is already in progress. Check /citations/status for updates.",
            stats=service.get_status().get("stats")
        )

    async def run_background_prioritized_enrichment():
        await service.run_prioritized_enrichment(max_papers=max_papers)

    background_tasks.add_task(run_background_prioritized_enrichment)

    estimate_hours = (max_papers or 27000) * 30 / 3600
    return EnrichmentResult(
        status="started",
        message=f"Prioritized citation enrichment started. Processing most valuable papers first. "
                f"Estimated time: ~{estimate_hours:.1f} hours for {max_papers or 'all'} papers at public API rate. "
                f"Check /enrichment/citations/status for progress."
    )


@router.post("/citations/paper/{paper_id}", response_model=EnrichmentResult)
async def enrich_single_paper_citations(paper_id: str):
    """
    Fetch citation data for a single paper from OpenAlex.

    Returns the paper's citation info including:
    - Total citation count
    - OpenAlex ID
    - Related concepts
    """
    from app.services.citation_enrichment_service import get_citation_enrichment_service
    service = get_citation_enrichment_service()

    result = await service.enrich_single_paper(paper_id)

    if result:
        return EnrichmentResult(
            status="success",
            message=f"Paper {paper_id} citation data fetched successfully.",
            stats=result
        )
    else:
        return EnrichmentResult(
            status="not_found",
            message=f"Paper {paper_id} not found in OpenAlex. May be too new or not indexed."
        )


@router.get("/citations/count")
async def get_citation_enrichment_count():
    """
    Get count of papers with citation data vs without.
    """
    from app.db.database import database

    total_query = "SELECT COUNT(*) FROM papers"
    has_citations_query = "SELECT COUNT(*) FROM papers WHERE citation_count > 0"
    total_citations_query = "SELECT SUM(citation_count) FROM papers"

    total_result = await database.fetch_one(total_query)
    has_citations_result = await database.fetch_one(has_citations_query)
    total_citations_result = await database.fetch_one(total_citations_query)

    total = total_result[0] if total_result else 0
    has_citations = has_citations_result[0] if has_citations_result else 0
    total_citations = total_citations_result[0] if total_citations_result and total_citations_result[0] else 0

    return {
        "total_papers": total,
        "papers_with_citations": has_citations,
        "papers_without_citations": total - has_citations,
        "total_citations": total_citations,
        "percent_complete": round(100.0 * has_citations / total, 1) if total > 0 else 0
    }


@router.get("/citations/top")
async def get_top_cited_papers(
    limit: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = Query(default=None)
):
    """
    Get top cited papers in the database.

    Useful for finding influential/foundational papers.
    """
    from app.db.database import database

    params = {"limit": limit}
    category_filter = ""
    if category:
        category_filter = "AND category = :category"
        params["category"] = category

    query = f"""
        SELECT
            id,
            title,
            category,
            citation_count,
            published_date
        FROM papers
        WHERE citation_count > 0
        {category_filter}
        ORDER BY citation_count DESC
        LIMIT :limit
    """

    rows = await database.fetch_all(query, params)

    return {
        "papers": [
            {
                "id": row["id"],
                "title": row["title"],
                "category": row["category"],
                "citation_count": row["citation_count"],
                "published": row["published_date"].isoformat() if row["published_date"] else None,
            }
            for row in rows
        ],
        "total": len(rows)
    }
