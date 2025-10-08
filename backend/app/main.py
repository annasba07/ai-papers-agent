"""
FastAPI application entry point with clean service architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router


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
        allow_origins=settings.ALLOWED_ORIGINS,
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
    """Frontend-compatible papers endpoint"""
    from app.services.arxiv_service import arxiv_service
    from app.services.ai_analysis_service import ai_analysis_service

    try:
        # Determine which type of search to perform
        if query:
            # Search by query
            papers = await arxiv_service.search_papers(query, max_results=20)
        elif category and category != "all":
            # Search by category
            papers = await arxiv_service.get_recent_papers(category, max_results=20)
        else:
            # Get recent AI papers by default
            papers = await arxiv_service.get_recent_papers("cs.AI", max_results=20)

        # Enhance with AI analysis
        if papers:
            batch_size = min(len(papers), settings.MAX_PAPERS_PER_BATCH)
            papers_to_analyze = papers[:batch_size]
            analyzed_papers = await ai_analysis_service.batch_generate_summaries(papers_to_analyze)
            return analyzed_papers

        return []

    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to fetch papers: {str(e)}")


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