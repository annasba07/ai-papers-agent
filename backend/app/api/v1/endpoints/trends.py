"""
Trend Detection API Endpoints

Provides access to research trend analysis:
- Hot topics (accelerating techniques)
- Rising methods (consistent growth)
- Active authors
- Emerging research areas
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.trend_service import (
    get_trend_service,
    TrendingTopic,
    AuthorTrend,
    TrendSummary
)


router = APIRouter(prefix="/trends", tags=["Trends"])


# ============================================================================
# Response Models
# ============================================================================

class HotTopicResponse(BaseModel):
    """Hot topic with acceleration data"""
    name: str
    normalized_name: str
    category: str
    current_count: int
    previous_count: int
    acceleration: float = Field(description="Percentage change")
    representative_papers: List[dict] = []
    related_topics: List[str] = []


class RisingTechniqueResponse(BaseModel):
    """Rising technique with growth data"""
    name: str
    normalized_name: str
    category: str
    current_count: int
    previous_count: int
    acceleration: float


class ActiveAuthorResponse(BaseModel):
    """Active author with recent activity"""
    name: str
    paper_count: int
    recent_papers: int
    top_topics: List[str] = []


class TrendSummaryResponse(BaseModel):
    """Complete trend summary"""
    hot_topics: List[HotTopicResponse]
    rising_techniques: List[RisingTechniqueResponse]
    active_authors: List[ActiveAuthorResponse]
    emerging_areas: List[str]
    generated_at: str


# ============================================================================
# HOT TOPICS ENDPOINTS
# ============================================================================

@router.get("/hot-topics", response_model=List[HotTopicResponse])
async def get_hot_topics(
    window_days: int = Query(30, ge=7, le=90, description="Current time window in days"),
    comparison_days: int = Query(30, ge=7, le=90, description="Previous window for comparison"),
    top_k: int = Query(10, ge=1, le=50, description="Number of topics to return")
):
    """
    Get hot research topics based on paper velocity

    Identifies topics with accelerating paper counts by comparing
    current window to previous window.

    - **window_days**: Current time window (7-90 days)
    - **comparison_days**: Previous window for comparison
    - **top_k**: Number of topics to return

    Returns topics sorted by acceleration (percentage growth).
    """
    service = get_trend_service()

    try:
        topics = service.get_hot_topics(
            window_days=window_days,
            comparison_window_days=comparison_days,
            top_k=top_k
        )

        return [
            HotTopicResponse(
                name=t.name,
                normalized_name=t.normalized_name,
                category=t.category,
                current_count=t.current_count,
                previous_count=t.previous_count,
                acceleration=t.acceleration,
                representative_papers=t.representative_papers,
                related_topics=t.related_topics
            )
            for t in topics
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RISING TECHNIQUES ENDPOINTS
# ============================================================================

@router.get("/rising-techniques", response_model=List[RisingTechniqueResponse])
async def get_rising_techniques(
    lookback_days: int = Query(90, ge=30, le=180, description="How far back to analyze"),
    top_k: int = Query(10, ge=1, le=50, description="Number of techniques to return")
):
    """
    Get techniques with consistent growth patterns

    Identifies techniques that show steady increase over three periods.

    - **lookback_days**: Analysis window (30-180 days)
    - **top_k**: Number of techniques to return

    Returns techniques sorted by growth rate.
    """
    service = get_trend_service()

    try:
        techniques = service.get_rising_techniques(
            lookback_days=lookback_days,
            top_k=top_k
        )

        return [
            RisingTechniqueResponse(
                name=t.name,
                normalized_name=t.normalized_name,
                category=t.category,
                current_count=t.current_count,
                previous_count=t.previous_count,
                acceleration=t.acceleration
            )
            for t in techniques
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AUTHOR ACTIVITY ENDPOINTS
# ============================================================================

@router.get("/active-authors", response_model=List[ActiveAuthorResponse])
async def get_active_authors(
    window_days: int = Query(30, ge=7, le=90, description="Time window in days"),
    top_k: int = Query(15, ge=1, le=50, description="Number of authors to return")
):
    """
    Get most active authors in recent period

    - **window_days**: Time window to consider (7-90 days)
    - **top_k**: Number of authors to return

    Returns authors sorted by recent paper count.
    """
    service = get_trend_service()

    try:
        authors = service.get_active_authors(
            window_days=window_days,
            top_k=top_k
        )

        return [
            ActiveAuthorResponse(
                name=a.name,
                paper_count=a.paper_count,
                recent_papers=a.recent_papers,
                top_topics=a.top_topics
            )
            for a in authors
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EMERGING AREAS ENDPOINTS
# ============================================================================

@router.get("/emerging-areas", response_model=List[str])
async def get_emerging_areas(
    top_k: int = Query(5, ge=1, le=20, description="Number of areas to return")
):
    """
    Get emerging research areas

    Identifies task domains with accelerating paper counts.

    - **top_k**: Number of areas to return

    Returns area names sorted by growth.
    """
    service = get_trend_service()

    try:
        areas = service.get_emerging_areas(top_k=top_k)
        return areas

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUMMARY ENDPOINTS
# ============================================================================

@router.get("/summary", response_model=TrendSummaryResponse)
async def get_trend_summary():
    """
    Get comprehensive trend summary

    Combines hot topics, rising techniques, active authors,
    and emerging areas into a single response.

    Useful for dashboard displays and trend overviews.
    """
    service = get_trend_service()

    try:
        summary = service.get_trend_summary()

        return TrendSummaryResponse(
            hot_topics=[
                HotTopicResponse(
                    name=t.name,
                    normalized_name=t.normalized_name,
                    category=t.category,
                    current_count=t.current_count,
                    previous_count=t.previous_count,
                    acceleration=t.acceleration,
                    representative_papers=t.representative_papers,
                    related_topics=t.related_topics
                )
                for t in summary.hot_topics
            ],
            rising_techniques=[
                RisingTechniqueResponse(
                    name=t.name,
                    normalized_name=t.normalized_name,
                    category=t.category,
                    current_count=t.current_count,
                    previous_count=t.previous_count,
                    acceleration=t.acceleration
                )
                for t in summary.rising_techniques
            ],
            active_authors=[
                ActiveAuthorResponse(
                    name=a.name,
                    paper_count=a.paper_count,
                    recent_papers=a.recent_papers,
                    top_topics=a.top_topics
                )
                for a in summary.active_authors
            ],
            emerging_areas=summary.emerging_areas,
            generated_at=summary.generated_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TECHNIQUE COMPARISON ENDPOINTS
# ============================================================================

@router.get("/compare-techniques")
async def compare_techniques(
    technique_a: str = Query(..., description="First technique name"),
    technique_b: str = Query(..., description="Second technique name"),
    window_days: int = Query(90, ge=30, le=180)
):
    """
    Compare two techniques across multiple dimensions

    - **technique_a**: First technique to compare
    - **technique_b**: Second technique to compare
    - **window_days**: Analysis window

    Returns comparison data including:
    - Paper counts over time
    - Growth rates
    - Common task domains
    - Representative papers
    """
    from app.services.local_atlas_service import local_atlas_service
    from app.services.technique_extraction_service import TECHNIQUE_PATTERNS, TASK_DOMAINS
    from datetime import datetime, timedelta
    from collections import defaultdict

    if not local_atlas_service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Atlas service not available"
        )

    try:
        now = datetime.utcnow()
        cutoff = now - timedelta(days=window_days)

        # Normalize technique names
        norm_a = technique_a.lower().replace(" ", "_").replace("-", "_")
        norm_b = technique_b.lower().replace(" ", "_").replace("-", "_")

        # Get patterns for each technique
        patterns_a = TECHNIQUE_PATTERNS.get(norm_a, [norm_a])
        patterns_b = TECHNIQUE_PATTERNS.get(norm_b, [norm_b])

        # Count papers and collect domains for each technique
        stats_a = {"count": 0, "papers": [], "domains": defaultdict(int)}
        stats_b = {"count": 0, "papers": [], "domains": defaultdict(int)}

        for record in local_atlas_service._records:
            published_dt = record.get("_published_dt")
            if not published_dt or published_dt < cutoff:
                continue

            text = record.get("_search_text", "").lower()

            # Check technique A
            if any(p in text for p in patterns_a):
                stats_a["count"] += 1
                if len(stats_a["papers"]) < 3:
                    stats_a["papers"].append({
                        "id": record.get("id"),
                        "title": record.get("title")
                    })

                for domain, keywords in TASK_DOMAINS.items():
                    if any(kw in text for kw in keywords):
                        stats_a["domains"][domain] += 1

            # Check technique B
            if any(p in text for p in patterns_b):
                stats_b["count"] += 1
                if len(stats_b["papers"]) < 3:
                    stats_b["papers"].append({
                        "id": record.get("id"),
                        "title": record.get("title")
                    })

                for domain, keywords in TASK_DOMAINS.items():
                    if any(kw in text for kw in keywords):
                        stats_b["domains"][domain] += 1

        # Format comparison result
        return {
            "technique_a": {
                "name": technique_a,
                "normalized_name": norm_a,
                "paper_count": stats_a["count"],
                "representative_papers": stats_a["papers"],
                "top_domains": sorted(
                    stats_a["domains"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            },
            "technique_b": {
                "name": technique_b,
                "normalized_name": norm_b,
                "paper_count": stats_b["count"],
                "representative_papers": stats_b["papers"],
                "top_domains": sorted(
                    stats_b["domains"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            },
            "comparison": {
                "window_days": window_days,
                "count_ratio": (
                    stats_a["count"] / max(stats_b["count"], 1)
                    if stats_a["count"] > 0 else 0
                ),
                "common_domains": list(
                    set(stats_a["domains"].keys()) &
                    set(stats_b["domains"].keys())
                )
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
