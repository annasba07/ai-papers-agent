"""
Data Moat API Endpoints

Exposes the rich data infrastructure:
- Paper relationships (knowledge graph)
- External signals (GitHub, HuggingFace)
- Temporal tracking (trends, velocity)
- Benchmarks (SOTA, leaderboards)
"""
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from databases import Database

from app.db.database import get_db
from app.services.relationship_extractor import get_relationship_service
from app.services.github_enricher import get_external_signals_service
from app.services.temporal_tracker import get_temporal_service
from app.services.benchmark_service import get_benchmark_service

router = APIRouter()


# ============================================================================
# Paper Relationships (Knowledge Graph)
# ============================================================================

class RelationshipResponse(BaseModel):
    paper_id: str
    title: Optional[str] = None
    relationship_type: str
    description: Optional[str] = None
    confidence: Optional[float] = None


class PaperRelationshipsResponse(BaseModel):
    paper_id: str
    builds_on: List[RelationshipResponse]
    built_upon_by: List[RelationshipResponse]


class LineageNode(BaseModel):
    paper_id: str
    title: str
    relationship: str
    description: Optional[str] = None
    depth: int
    published_date: Optional[str] = None
    citation_count: Optional[int] = None


class PaperLineageResponse(BaseModel):
    paper_id: str
    ancestors: List[LineageNode]
    descendants: List[LineageNode]


@router.get(
    "/relationships/{paper_id}",
    response_model=PaperRelationshipsResponse,
    summary="Get paper relationships",
    description="Get all typed relationships for a paper (what it builds on, what builds on it)"
)
async def get_paper_relationships(
    paper_id: str,
    db: Database = Depends(get_db)
):
    """Get relationships for a specific paper."""
    service = get_relationship_service()
    result = await service.get_paper_relationships(paper_id, db)

    return PaperRelationshipsResponse(
        paper_id=result["paper_id"],
        builds_on=[
            RelationshipResponse(**r) for r in result.get("builds_on", [])
        ],
        built_upon_by=[
            RelationshipResponse(**r) for r in result.get("built_upon_by", [])
        ]
    )


@router.get(
    "/lineage/{paper_id}",
    response_model=PaperLineageResponse,
    summary="Get paper lineage",
    description="Get the full ancestry and descendant tree for a paper"
)
async def get_paper_lineage(
    paper_id: str,
    max_depth: int = Query(default=3, ge=1, le=5),
    db: Database = Depends(get_db)
):
    """Get full lineage tree for a paper."""
    service = get_relationship_service()
    result = await service.get_paper_lineage(paper_id, db, max_depth)

    return PaperLineageResponse(
        paper_id=result["paper_id"],
        ancestors=[LineageNode(**a) for a in result.get("ancestors", [])],
        descendants=[LineageNode(**d) for d in result.get("descendants", [])]
    )


@router.post(
    "/relationships/extract/{paper_id}",
    summary="Extract relationships for a paper",
    description="Trigger LLM-based relationship extraction for a paper"
)
async def extract_paper_relationships(
    paper_id: str,
    db: Database = Depends(get_db)
):
    """Extract relationships for a paper using LLM analysis."""
    # Get paper
    query = """
        SELECT id, title, abstract FROM papers WHERE id = :paper_id
    """
    paper = await db.fetch_one(query, {"paper_id": paper_id})

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper_dict = {
        "id": paper["id"],
        "title": paper["title"],
        "abstract": paper["abstract"]
    }

    service = get_relationship_service()
    result = await service.extract_and_save(paper_dict, db)

    return result


# ============================================================================
# External Signals (GitHub, HuggingFace)
# ============================================================================

class GitHubRepoResponse(BaseModel):
    url: str
    stars: int
    forks: int
    open_issues: int
    language: Optional[str] = None
    license: Optional[str] = None
    pushed_at: Optional[str] = None


class ExternalSignalsResponse(BaseModel):
    paper_id: str
    github: Optional[dict] = None
    huggingface: Optional[dict] = None
    social: Optional[dict] = None


# NOTE: Static routes must come BEFORE dynamic parameter routes
@router.get(
    "/signals/top-github",
    summary="Papers with most GitHub stars",
    description="Get papers with highest GitHub activity"
)
async def get_top_github_papers(
    min_stars: int = Query(default=100, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Database = Depends(get_db)
):
    """Get papers with most GitHub stars."""
    service = get_external_signals_service()
    papers = await service.get_papers_with_high_github_activity(db, min_stars, limit)

    return {"papers": papers, "count": len(papers)}


@router.get(
    "/signals/{paper_id}",
    response_model=ExternalSignalsResponse,
    summary="Get external signals",
    description="Get GitHub, HuggingFace, and social signals for a paper"
)
async def get_external_signals(
    paper_id: str,
    db: Database = Depends(get_db)
):
    """Get external signals for a paper."""
    service = get_external_signals_service()
    signals = await service.get_paper_signals(paper_id, db)

    return ExternalSignalsResponse(
        paper_id=paper_id,
        github=signals.get("github"),
        huggingface=signals.get("huggingface"),
        social=signals.get("social")
    )


@router.post(
    "/signals/refresh/{paper_id}",
    summary="Refresh external signals",
    description="Refresh GitHub and other external signals for a paper"
)
async def refresh_external_signals(
    paper_id: str,
    db: Database = Depends(get_db)
):
    """Refresh external signals for a paper."""
    # Get paper
    query = """
        SELECT id, title, code_repos, deep_analysis, external_signals
        FROM papers WHERE id = :paper_id
    """
    paper = await db.fetch_one(query, {"paper_id": paper_id})

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper_dict = {
        "id": paper["id"],
        "title": paper["title"],
        "code_repos": paper["code_repos"],
        "deep_analysis": paper["deep_analysis"],
        "external_signals": paper["external_signals"]
    }

    service = get_external_signals_service()
    result = await service.refresh_github_signals(paper_dict, db)

    return {
        "paper_id": paper_id,
        "signals": result
    }


# ============================================================================
# Temporal Tracking (Trends, Velocity)
# ============================================================================

class MetricSnapshotResponse(BaseModel):
    paper_id: str
    snapshot_date: str
    citation_count: Optional[int] = None
    citation_velocity: Optional[float] = None
    github_stars: Optional[int] = None
    buzz_score: Optional[float] = None


class TrendResponse(BaseModel):
    paper_id: str
    citation_trend: str
    citation_velocity_current: Optional[float] = None
    citation_velocity_change: Optional[float] = None
    github_trend: Optional[str] = None
    buzz_trend: Optional[str] = None


@router.get(
    "/metrics/history/{paper_id}",
    summary="Get metric history",
    description="Get historical metric snapshots for a paper"
)
async def get_metric_history(
    paper_id: str,
    days: int = Query(default=90, ge=1, le=365),
    db: Database = Depends(get_db)
):
    """Get metric history for a paper."""
    service = get_temporal_service()
    snapshots = await service.tracker.get_paper_history(paper_id, db, days)

    return {
        "paper_id": paper_id,
        "snapshots": [
            {
                "date": s.snapshot_date.isoformat(),
                "citation_count": s.citation_count,
                "citation_velocity": s.citation_velocity,
                "github_stars": s.github_stars,
                "buzz_score": s.buzz_score
            }
            for s in snapshots
        ]
    }


@router.get(
    "/metrics/trend/{paper_id}",
    response_model=TrendResponse,
    summary="Get paper trend",
    description="Analyze citation and activity trends for a paper"
)
async def get_paper_trend(
    paper_id: str,
    db: Database = Depends(get_db)
):
    """Get trend analysis for a paper."""
    service = get_temporal_service()
    trend = await service.tracker.get_paper_trend(paper_id, db)

    if not trend:
        raise HTTPException(
            status_code=404,
            detail="No trend data available for this paper"
        )

    return TrendResponse(
        paper_id=trend.paper_id,
        citation_trend=trend.citation_trend,
        citation_velocity_current=trend.citation_velocity_current,
        citation_velocity_change=trend.citation_velocity_change,
        github_trend=trend.github_trend,
        buzz_trend=trend.buzz_trend
    )


@router.get(
    "/metrics/rising",
    summary="Rising papers",
    description="Get papers with highest citation velocity"
)
async def get_rising_papers(
    limit: int = Query(default=50, ge=1, le=200),
    db: Database = Depends(get_db)
):
    """Get papers with rising citation velocity."""
    service = get_temporal_service()
    papers = await service.get_rising_papers(db, limit)

    return {"papers": papers, "count": len(papers)}


@router.get(
    "/metrics/hot",
    summary="Hot papers",
    description="Get papers with highest buzz scores"
)
async def get_hot_papers(
    limit: int = Query(default=50, ge=1, le=200),
    db: Database = Depends(get_db)
):
    """Get papers with highest buzz scores."""
    service = get_temporal_service()
    papers = await service.get_hot_papers(db, limit)

    return {"papers": papers, "count": len(papers)}


@router.post(
    "/metrics/capture",
    summary="Capture daily snapshots",
    description="Capture metric snapshots for papers (admin operation)"
)
async def capture_snapshots(
    limit: Optional[int] = Query(default=None),
    db: Database = Depends(get_db)
):
    """Capture daily metric snapshots."""
    service = get_temporal_service()
    result = await service.capture_daily_snapshots(db, limit)

    return result


# ============================================================================
# Benchmarks (SOTA, Leaderboards)
# ============================================================================

class BenchmarkResponse(BaseModel):
    id: str
    name: str
    slug: str
    task_category: Optional[str] = None
    modality: Optional[str] = None
    primary_metric: str
    higher_is_better: bool
    description: Optional[str] = None


class SOTAResponse(BaseModel):
    benchmark_name: str
    paper_id: str
    paper_title: str
    value: float
    achieved_date: str
    model_name: Optional[str] = None
    model_size: Optional[str] = None


class LeaderboardEntryResponse(BaseModel):
    rank: int
    paper_id: str
    paper_title: str
    value: float
    model_name: Optional[str] = None
    is_current_sota: bool


@router.get(
    "/benchmarks",
    summary="List benchmarks",
    description="Get all benchmark definitions"
)
async def list_benchmarks(
    modality: Optional[str] = Query(default=None),
    task_category: Optional[str] = Query(default=None),
    db: Database = Depends(get_db)
):
    """List all benchmarks."""
    service = get_benchmark_service()
    benchmarks = await service.get_all_benchmarks(db, modality, task_category)

    return {
        "benchmarks": [
            BenchmarkResponse(
                id=b.id,
                name=b.name,
                slug=b.slug,
                task_category=b.task_category,
                modality=b.modality,
                primary_metric=b.primary_metric,
                higher_is_better=b.higher_is_better,
                description=b.description
            )
            for b in benchmarks
        ],
        "count": len(benchmarks)
    }


@router.get(
    "/benchmarks/{slug}/sota",
    response_model=SOTAResponse,
    summary="Get current SOTA",
    description="Get current state-of-the-art for a benchmark"
)
async def get_sota(
    slug: str,
    db: Database = Depends(get_db)
):
    """Get current SOTA for a benchmark."""
    service = get_benchmark_service()
    sota = await service.get_current_sota(slug, db)

    if not sota:
        raise HTTPException(status_code=404, detail="No SOTA data for this benchmark")

    return SOTAResponse(
        benchmark_name=sota.benchmark_name,
        paper_id=sota.paper_id,
        paper_title=sota.paper_title,
        value=sota.value,
        achieved_date=sota.achieved_date.isoformat(),
        model_name=sota.model_name,
        model_size=sota.model_size
    )


@router.get(
    "/benchmarks/{slug}/history",
    summary="Get SOTA history",
    description="Get SOTA progression over time for a benchmark"
)
async def get_sota_history(
    slug: str,
    limit: int = Query(default=20, ge=1, le=100),
    db: Database = Depends(get_db)
):
    """Get SOTA history for a benchmark."""
    service = get_benchmark_service()
    history = await service.get_sota_history(slug, db, limit)

    return {
        "benchmark_slug": slug,
        "history": [
            {
                "paper_id": s.paper_id,
                "paper_title": s.paper_title,
                "value": s.value,
                "achieved_date": s.achieved_date.isoformat(),
                "model_name": s.model_name,
                "model_size": s.model_size
            }
            for s in history
        ]
    }


@router.get(
    "/benchmarks/{slug}/leaderboard",
    summary="Get leaderboard",
    description="Get full leaderboard for a benchmark"
)
async def get_leaderboard(
    slug: str,
    limit: int = Query(default=20, ge=1, le=100),
    db: Database = Depends(get_db)
):
    """Get leaderboard for a benchmark."""
    service = get_benchmark_service()
    entries = await service.get_leaderboard(slug, db, limit)

    return {
        "benchmark_slug": slug,
        "leaderboard": [
            LeaderboardEntryResponse(
                rank=e.rank,
                paper_id=e.paper_id,
                paper_title=e.paper_title,
                value=e.value,
                model_name=e.model_name,
                is_current_sota=e.is_current_sota
            )
            for e in entries
        ]
    }


@router.get(
    "/benchmarks/paper/{paper_id}",
    summary="Compare paper to SOTA",
    description="Compare a paper's results to current SOTA across benchmarks"
)
async def compare_paper_to_sota(
    paper_id: str,
    db: Database = Depends(get_db)
):
    """Compare paper results to SOTA."""
    service = get_benchmark_service()
    result = await service.compare_paper_to_sota(paper_id, db)

    return result
