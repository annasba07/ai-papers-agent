"""
Benchmark Leaderboards API - Intelligence-Driven Performance Rankings

Provides contextual benchmark leaderboards with:
- Dataset/metric rankings with SOTA detection
- Paper benchmark context (rank, percentile, delta from SOTA)
- Model performance tracking across benchmarks
- Recent SOTA discoveries

This is NOT just data tables - it's research intelligence.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from app.services.leaderboard_service import get_leaderboard_service


router = APIRouter(prefix="/leaderboards")


# ============== Response Models ==============

class ValueRange(BaseModel):
    """Statistics for benchmark values."""
    min: float
    max: float
    avg: Optional[float] = None


class PopularLeaderboard(BaseModel):
    """A popular benchmark leaderboard."""
    dataset: str
    metric: str
    entry_count: int
    paper_count: int
    model_count: int
    value_range: ValueRange
    higher_is_better: bool


class LeaderboardEntry(BaseModel):
    """Single entry in a leaderboard."""
    rank: int
    paper_id: str
    paper_title: str
    model_name: Optional[str]
    value: float
    metric: str
    published_date: Optional[str]
    is_sota: bool
    percentile: float
    delta_from_sota: Optional[float]
    context: str  # Human-readable context


class SOTAInfo(BaseModel):
    """State-of-the-art information."""
    value: float
    paper_id: str
    paper_title: str
    model_name: Optional[str]
    published_date: Optional[str]


class LeaderboardStats(BaseModel):
    """Statistics for a leaderboard."""
    min: float
    max: float
    avg: float
    spread: float


class LeaderboardResponse(BaseModel):
    """Full leaderboard response."""
    dataset: str
    metric: str
    higher_is_better: bool
    available_metrics: List[str]
    total_entries: int
    sota: SOTAInfo
    stats: LeaderboardStats
    entries: List[LeaderboardEntry]


class PaperBenchmark(BaseModel):
    """Benchmark result for a paper with context."""
    dataset: str
    metric: str
    value: float
    model_name: Optional[str]
    rank: int
    total_entries: int
    percentile: float
    is_sota: bool
    context: str


class PaperBenchmarksResponse(BaseModel):
    """All benchmarks for a paper."""
    paper_id: str
    paper_title: str
    published_date: Optional[str]
    benchmark_count: int
    sota_count: int
    top5_count: int
    summary: str
    benchmarks: List[PaperBenchmark]


class RecentSOTA(BaseModel):
    """Recent SOTA achievement."""
    paper_id: str
    paper_title: str
    dataset: str
    metric: str
    value: float
    model_name: Optional[str]
    published_date: Optional[str]


# ============== Endpoints ==============

@router.get("/popular", response_model=List[PopularLeaderboard])
async def get_popular_leaderboards(
    limit: int = Query(default=20, ge=1, le=100, description="Number of leaderboards to return"),
    min_entries: int = Query(default=5, ge=1, description="Minimum entries for a leaderboard")
):
    """
    Get most popular benchmark leaderboards.

    Returns dataset+metric combinations sorted by number of papers,
    with statistics about value ranges and entry counts.

    Use this to discover which benchmarks have the most activity.
    """
    service = get_leaderboard_service()
    return await service.get_popular_leaderboards(limit=limit, min_entries=min_entries)


@router.get("/dataset/{dataset}", response_model=dict)
async def get_dataset_leaderboard(
    dataset: str,
    metric: Optional[str] = Query(default=None, description="Specific metric (defaults to most common)"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum entries to return")
):
    """
    Get leaderboard for a specific dataset.

    Returns ranked entries with:
    - Rank position
    - SOTA indicator
    - Percentile ("Top 5%")
    - Delta from SOTA
    - Human-readable context

    Examples:
    - /leaderboards/dataset/ImageNet-1K
    - /leaderboards/dataset/GSM8K?metric=accuracy
    - /leaderboards/dataset/HumanEval?metric=pass@1
    """
    service = get_leaderboard_service()
    result = await service.get_leaderboard(dataset=dataset, metric=metric, limit=limit)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/paper/{paper_id}", response_model=dict)
async def get_paper_benchmarks(paper_id: str):
    """
    Get all benchmark results for a paper with leaderboard context.

    For each benchmark the paper reports, shows:
    - The value and metric
    - Rank in the overall leaderboard
    - Percentile position
    - Whether it's SOTA

    Also provides a summary like:
    "Achieves SOTA on 2 benchmarks. Top 5% on 3 additional benchmarks."
    """
    service = get_leaderboard_service()
    result = await service.get_paper_benchmarks(paper_id=paper_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/model/{model_name}", response_model=dict)
async def get_model_performance(
    model_name: str,
    limit: int = Query(default=50, ge=1, le=200, description="Maximum benchmarks to return")
):
    """
    Get performance of a model across all benchmarks.

    Searches for benchmarks mentioning the model name and shows
    its ranking on each dataset+metric combination.

    Examples:
    - /leaderboards/model/GPT-4
    - /leaderboards/model/LLaMA
    - /leaderboards/model/BERT
    """
    service = get_leaderboard_service()
    result = await service.get_model_performance(model_name=model_name, limit=limit)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/recent-sota", response_model=List[RecentSOTA])
async def get_recent_sota(
    days: int = Query(default=30, ge=1, le=365, description="Look back N days"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum results")
):
    """
    Find papers that achieved SOTA recently.

    Returns papers from the last N days that hold the top position
    on at least one dataset+metric combination.

    Great for staying current on breakthrough results.
    """
    service = get_leaderboard_service()
    return await service.get_recent_sota(days=days, limit=limit)


@router.get("/search")
async def search_leaderboards(
    q: str = Query(..., min_length=2, description="Search term for dataset or metric"),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Search for leaderboards by dataset or metric name.

    Examples:
    - /leaderboards/search?q=imagenet
    - /leaderboards/search?q=accuracy
    - /leaderboards/search?q=code
    """
    from app.db.database import database

    query = """
        SELECT DISTINCT
            dataset,
            metric,
            COUNT(*) as entry_count
        FROM benchmarks
        WHERE
            LOWER(dataset) LIKE LOWER(:pattern)
            OR LOWER(metric) LIKE LOWER(:pattern)
        GROUP BY dataset, metric
        ORDER BY entry_count DESC
        LIMIT :limit
    """

    rows = await database.fetch_all(query, {
        "pattern": f"%{q}%",
        "limit": limit
    })

    return {
        "query": q,
        "results": [
            {
                "dataset": r["dataset"],
                "metric": r["metric"],
                "entry_count": r["entry_count"]
            }
            for r in rows
        ]
    }
