"""
API endpoints for paper operations
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any
from app.services.arxiv_service import arxiv_service
from app.services.ai_analysis_service import ai_analysis_service
from app.schemas.paper import (
    PaperResponse, 
    PaperSearchParams, 
    BatchAnalysisRequest,
    AIAnalysisSchema
)
from app.core.config import settings

router = APIRouter()


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_papers(
    query: str = Query(..., description="Search query for papers"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    enhance_with_ai: bool = Query(False, description="Whether to enhance with AI analysis")
):
    """
    Search for papers using arXiv API
    """
    try:
        # Search for papers
        papers = await arxiv_service.search_papers(query, max_results)
        
        if not papers:
            return []
        
        # Enhanced with AI analysis if requested
        if enhance_with_ai:
            # Limit batch size to prevent timeout
            batch_size = min(len(papers), settings.MAX_PAPERS_PER_BATCH)
            papers_to_analyze = papers[:batch_size]
            
            analyzed_papers = await ai_analysis_service.batch_generate_summaries(papers_to_analyze)
            return analyzed_papers
        
        return papers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/recent", response_model=List[Dict[str, Any]])
async def get_recent_papers(
    category: str = Query("cs.AI", description="arXiv category"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    enhance_with_ai: bool = Query(False, description="Whether to enhance with AI analysis")
):
    """
    Get recent papers from a specific category
    """
    try:
        # Get recent papers
        papers = await arxiv_service.get_recent_papers(category, max_results)
        
        if not papers:
            return []
        
        # Enhanced with AI analysis if requested
        if enhance_with_ai:
            # Limit batch size to prevent timeout
            batch_size = min(len(papers), settings.MAX_PAPERS_PER_BATCH)
            papers_to_analyze = papers[:batch_size]
            
            analyzed_papers = await ai_analysis_service.batch_generate_summaries(papers_to_analyze)
            return analyzed_papers
        
        return papers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recent papers fetch failed: {str(e)}")


@router.get("/{paper_id}", response_model=Dict[str, Any])
async def get_paper(
    paper_id: str,
    enhance_with_ai: bool = Query(False, description="Whether to enhance with AI analysis")
):
    """
    Get a specific paper by arXiv ID
    """
    try:
        # Get paper details
        paper = await arxiv_service.get_paper_by_id(paper_id)
        
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Enhanced with AI analysis if requested
        if enhance_with_ai:
            ai_analysis = await ai_analysis_service.generate_comprehensive_analysis(
                paper.get('summary', ''),
                paper.get('title', '')
            )
            paper['aiSummary'] = ai_analysis
        
        return paper
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Paper fetch failed: {str(e)}")


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_paper(paper_data: Dict[str, Any]):
    """
    Analyze a paper using AI
    """
    try:
        title = paper_data.get('title', '')
        abstract = paper_data.get('summary', '')
        
        if not title or not abstract:
            raise HTTPException(status_code=400, detail="Title and summary are required")
        
        analysis = await ai_analysis_service.generate_comprehensive_analysis(abstract, title)
        
        return {
            'title': title,
            'analysis': analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/batch-analyze", response_model=List[Dict[str, Any]])
async def batch_analyze_papers(request: BatchAnalysisRequest = Body(...)):
    """
    Analyze multiple papers using AI
    """
    try:
        papers_data = request.papers
        
        if len(papers_data) > settings.MAX_PAPERS_PER_BATCH:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many papers. Maximum {settings.MAX_PAPERS_PER_BATCH} allowed"
            )
        
        # Validate papers have required fields
        for paper in papers_data:
            if not paper.get('title') or not paper.get('summary'):
                raise HTTPException(status_code=400, detail="Each paper must have title and summary")
        
        analyzed_papers = await ai_analysis_service.batch_generate_summaries(papers_data)
        
        return analyzed_papers
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")