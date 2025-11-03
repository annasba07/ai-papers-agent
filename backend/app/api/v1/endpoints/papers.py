"""
API endpoints for paper operations
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any
import json
from app.services.arxiv_service import arxiv_service
from app.services.ai_analysis_service import ai_analysis_service
from app.schemas.paper import (
    PaperResponse,
    PaperSearchParams,
    BatchAnalysisRequest,
    AIAnalysisSchema,
    ContextualSearchRequest,
    ContextualSearchResponse
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


@router.post("/contextual-search", response_model=ContextualSearchResponse)
async def contextual_search(request: ContextualSearchRequest = Body(...)):
    """
    Contextual search: Analyze user's project description and find relevant papers with recommendations
    """
    try:
        user_description = request.description.strip()
        fallback_mode = getattr(ai_analysis_service, "fallback_mode", False)

        # Step 1: Deconstruct user query to generate search keywords
        if fallback_mode:
            keywords = [
                word.strip(".,;:").lower()
                for word in user_description.split()
                if len(word.strip(".,;:")) > 3
            ]
            search_query = " ".join(keywords[:6]) or user_description[:100]
        else:
            deconstruct_prompt = f"""Analyze the following user project description and extract the key information needed to find relevant academic papers.
            Identify the main problem, the domain, and any specific technologies or methodologies mentioned.

            User Description: "{user_description}"

            Return a JSON object with the following keys: "problem", "domain", "technologies", "search_query".
            The 'search_query' should be a concise string of 3-5 keywords suitable for a semantic search on arXiv."""

            try:
                deconstruct_response = await ai_analysis_service.model.generate_content_async(deconstruct_prompt)
                deconstructed_info = json.loads(
                    deconstruct_response.text.replace("```json", "").replace("```", "").strip()
                )
                search_query = deconstructed_info.get("search_query", "")
            except Exception:
                search_query = user_description[:100]

        if not search_query:
            raise HTTPException(
                status_code=400,
                detail="Could not generate a search query from the description"
            )

        # Step 2: Search arXiv with the generated query
        papers = await arxiv_service.search_papers(search_query, max_results=10)

        if not papers:
            return ContextualSearchResponse(
                analysis="No relevant papers found for your project description.",
                papers=[]
            )

        # Step 3: Format papers for analysis
        papers_for_response = []
        papers_formatted = []

        for paper in papers:
            papers_for_response.append({
                "id": paper.get('link', ''),
                "title": paper.get('title', ''),
                "summary": paper.get('summary', '')
            })
            papers_formatted.append(
                f"- Title: {paper.get('title', '')}\n  Summary: {paper.get('summary', '')}"
            )

        papers_text = "\n".join(papers_formatted)

        # Step 4: Generate synthesis and recommendations
        synthesis_prompt = f"""You are an expert AI research assistant. A user has described a project they are working on.
        Based on their goal and a list of relevant research papers, your task is to synthesize the information and provide actionable advice.

        User's Project Goal: "{user_description}"

        Relevant Research Papers:
        {papers_text}

        Please provide a concise analysis that includes:

        1. **State-of-the-Art Techniques:** Briefly describe 2-3 of the most cutting-edge techniques from these papers that are directly applicable to the user's project.

        2. **How to Apply Them:** For each technique, explain how the user could specifically implement or adapt it for their application.

        3. **Potential Challenges:** Mention any potential challenges or limitations the user should be aware of when using these advanced methods.

        **Analysis Report:**"""

        if fallback_mode:
            bullet_points = "\n".join(
                [
                    f"- {paper.get('title', 'Untitled')} — apply ideas from the abstract for rapid experimentation."
                    for paper in papers_for_response[:3]
                ]
            )
            analysis_text = (
                "Offline contextual summary:\n"
                "The selected papers mirror your goals. Focus on their implementation sections and reported benchmarks.\n"
                f"{bullet_points}\n"
                "Connect a Gemini API key to unlock tailored strategy notes."
            )
        else:
            try:
                synthesis_response = await ai_analysis_service.model.generate_content_async(synthesis_prompt)
                analysis_text = synthesis_response.text
            except Exception:
                fallback_mode = True
                bullet_points = "\n".join(
                    [
                        f"- {paper.get('title', 'Untitled')} — inspect its methodology for actionable leads."
                        for paper in papers_for_response[:3]
                    ]
                )
                analysis_text = (
                    "Contextual synthesis temporarily unavailable. "
                    "Here is a quick brief of promising papers:\n"
                    f"{bullet_points}"
                )

        return ContextualSearchResponse(
            analysis=analysis_text,
            papers=papers_for_response
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Contextual search failed: {str(e)}"
        )


@router.post("/{paper_id}/generate-code")
async def generate_code_for_paper(paper_id: str):
    """
    Generate working code for a paper using multi-agent system

    This endpoint implements the full AgentCoder pipeline:
    1. Deep paper analysis
    2. AI-designed tests
    3. Test-driven code generation
    4. Execution & debugging
    5. Reflection & learning

    Based on research: AgentCoder (2024), Reflexion (2023), SAGE (2024)
    """
    try:
        from app.agents import get_orchestrator

        # Get paper details
        paper = await arxiv_service.get_paper_by_id(paper_id)

        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        # Get AI analysis if not already present
        if 'aiSummary' not in paper:
            ai_summary = await ai_analysis_service.generate_comprehensive_analysis(
                paper.get('summary', ''),
                paper.get('title', ''),
                paper.get('authors', []),
                paper_id
            )
            paper['aiSummary'] = ai_summary

        # Get orchestrator (global instance for memory persistence)
        orchestrator = get_orchestrator()

        # Generate code using multi-agent system
        result = await orchestrator.generate_quick_start(
            paper_title=paper['title'],
            paper_abstract=paper['summary'],
            paper_summary=paper['aiSummary'],
            paper_id=paper_id,
            paper_category=paper.get('category', 'cs.AI')
        )

        # Return formatted response
        return {
            "success": result.success,
            "generation_time": result.generation_time_seconds,
            "paper": {
                "id": result.paper_id,
                "title": result.paper_title,
                "analysis_summary": result.analysis_summary
            },
            "code": {
                "main": result.code.main_code if result.code else None,
                "config": result.code.config_code if result.code else None,
                "utils": result.code.utils_code if result.code else None,
                "example": result.code.example_code if result.code else None,
                "dependencies": result.code.dependencies if result.code else [],
                "framework": result.code.framework if result.code else "pytorch"
            },
            "tests": {
                "total": result.tests.total_tests if result.tests else 0,
                "passed": result.test_results.tests_passed if result.test_results else 0,
                "failed": result.test_results.tests_failed if result.test_results else 0,
                "execution_time": result.test_results.execution_time if result.test_results else 0
            },
            "debug": {
                "iterations": result.debug_iterations,
                "total_attempts": result.total_attempts
            },
            "readme": result.readme,
            "reflection": result.system_reflection
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code generation failed: {str(e)}"
        )


@router.post("/{paper_id}/generate-code-simple")
async def generate_code_simple(paper_id: str):
    """
    Generate working code for a paper using elegant single-conversation approach

    This endpoint uses a simplified architecture where Claude self-orchestrates
    the entire pipeline through extended context and tool use.

    Advantages over multi-agent approach:
    - 300 lines instead of 4,000
    - Single conversation with self-correction
    - Simpler to debug and maintain
    - Claude naturally adapts the pipeline

    Based on: Claude Sonnet 4 extended context + tool use
    """
    try:
        from app.agents.simple_generator import get_simple_generator

        # Get paper details
        paper = await arxiv_service.get_paper_by_id(paper_id)

        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        # Get AI analysis if not already present
        if 'aiSummary' not in paper:
            ai_summary = await ai_analysis_service.generate_comprehensive_analysis(
                paper.get('summary', ''),
                paper.get('title', ''),
                paper.get('authors', []),
                paper_id
            )
            paper['aiSummary'] = ai_summary

        # Get simple generator (global instance)
        generator = get_simple_generator()

        # Generate code using elegant approach
        result = await generator.generate(
            paper_title=paper['title'],
            paper_abstract=paper['summary'],
            paper_id=paper_id,
            paper_category=paper.get('category', 'cs.AI')
        )

        # Return formatted response
        return {
            "success": result.success,
            "generation_time": result.generation_time_seconds,
            "approach": "simple",  # Mark which approach was used
            "paper": {
                "id": result.paper_id,
                "title": result.paper_title
            },
            "code": {
                "model": result.code,
                "config": result.config,
                "utils": None,  # Simple approach may not generate utils
                "example": result.example
            },
            "tests": {
                "code": result.tests,
                "total": result.tests_total,
                "passed": result.tests_passed,
                "failed": result.tests_failed
            },
            "metadata": {
                "complexity": result.complexity,
                "debug_iterations": result.debug_iterations
            },
            "readme": result.readme,
            "reflection": result.reflection
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simple code generation failed: {str(e)}"
        )
