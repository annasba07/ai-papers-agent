"""
FastAPI application entry point with clean service architecture
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.services.local_atlas_service import local_atlas_service


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Accept"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
    
    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app


# Create application instance
app = create_application()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.PROJECT_VERSION}


# Frontend compatibility endpoints (without /api/v1 prefix)
@app.get("/papers")
async def get_papers_compat(
    days: str = "7",
    category: str = "all",
    query: str = ""
):
    """Frontend-compatible papers endpoint."""
    from app.services.arxiv_service import arxiv_service

    try:
        limit = min(20, settings.MAX_PAPERS_PER_BATCH)

        def _parse_days(value: str) -> Optional[int]:
            try:
                parsed = int(value)
                return parsed if parsed > 0 else None
            except (TypeError, ValueError):
                return None

        days_int = _parse_days(days)
        category_filter = None if category in (None, "", "all") else category

        # Prefer local atlas results when available
        if local_atlas_service.enabled:
            if query.strip():
                papers = local_atlas_service.search(
                    query,
                    top_k=limit,
                    category=category_filter,
                    max_age_days=days_int,
                )
            else:
                papers = local_atlas_service.recent_papers(
                    limit=limit,
                    category=category_filter,
                    days=days_int,
                )

            if papers:
                sanitized = [
                    {
                        "id": paper.get("id"),
                        "title": paper.get("title"),
                        "abstract": paper.get("abstract"),
                        "authors": paper.get("authors"),
                        "published": paper.get("published"),
                        "category": paper.get("category"),
                        "link": paper.get("link"),
                        "window_start": paper.get("window_start"),
                        "window_end": paper.get("window_end"),
                    }
                    for paper in papers[:limit]
                ]
                return {"papers": sanitized}

        # Fallback to live arXiv search when there are no atlas results
        if query.strip():
            papers = await arxiv_service.search_papers(query, max_results=limit)
        elif category_filter:
            papers = await arxiv_service.get_recent_papers(category_filter, max_results=limit)
        else:
            papers = await arxiv_service.get_recent_papers("cs.AI", max_results=limit)

        return {"papers": papers or []}

    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=f"Failed to fetch papers: {str(exc)}")


@app.post("/papers/contextual-search")
async def contextual_search_compat(request: dict):
    """Frontend-compatible contextual search endpoint"""
    from fastapi import HTTPException
    from app.api.v1.endpoints.papers import contextual_search
    from app.schemas.paper import ContextualSearchRequest

    try:
        # Convert dict to ContextualSearchRequest
        search_request = ContextualSearchRequest(description=request.get("description", ""))
        result = await contextual_search(search_request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contextual search failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
