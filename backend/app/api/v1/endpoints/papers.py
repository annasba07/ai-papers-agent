"""
API endpoints for paper operations
"""
import time
import asyncio
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
import json
from app.services.arxiv_service import arxiv_service
from app.services.ai_analysis_service import ai_analysis_service
from app.services.rerank_service import get_rerank_service
from app.services.local_atlas_service import local_atlas_service
from app.services.citation_graph_service import get_citation_graph_service
from app.db.database import database
from app.schemas.paper import (
    PaperResponse,
    PaperSearchParams,
    BatchAnalysisRequest,
    AIAnalysisSchema,
    ContextualSearchRequest,
    ContextualSearchResponse,
    ContextualSearchTiming,
    EmbeddingCacheInfo,
)
from app.core.config import settings

router = APIRouter()


async def get_paper_from_atlas_db(paper_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a paper from the Supabase atlas database.
    Returns None if not found.
    """
    try:
        query = """
            SELECT
                p.id,
                p.title,
                p.abstract,
                p.authors,
                p.published_date,
                p.category,
                p.citation_count,
                p.ai_analysis,
                p.deep_analysis,
                COALESCE(
                    (SELECT array_agg(c.name)
                     FROM paper_concepts pc
                     JOIN concepts c ON pc.concept_id = c.id
                     WHERE pc.paper_id = p.id),
                    ARRAY[]::text[]
                ) as concepts
            FROM papers p
            WHERE p.id = :paper_id
        """
        row = await database.fetch_one(query, {"paper_id": paper_id})

        if not row:
            return None

        # Parse authors JSON
        authors = row["authors"]
        if isinstance(authors, str):
            authors = json.loads(authors)

        # Parse ai_analysis JSONB (returned as string by databases library)
        ai_analysis = row["ai_analysis"]
        if isinstance(ai_analysis, str):
            ai_analysis = json.loads(ai_analysis)

        # Parse deep_analysis JSONB (returned as string by databases library)
        deep_analysis = row["deep_analysis"]
        if isinstance(deep_analysis, str):
            deep_analysis = json.loads(deep_analysis)

        plain_id = row["id"].split("v")[0]

        return {
            "id": row["id"],
            "title": row["title"],
            "summary": row["abstract"],  # Map abstract to summary for compatibility
            "abstract": row["abstract"],
            "authors": authors,
            "published": row["published_date"].isoformat() if row["published_date"] else None,
            "category": row["category"],
            "link": f"https://arxiv.org/abs/{plain_id}",
            "citation_count": row["citation_count"] or 0,
            "concepts": row["concepts"] or [],
            "aiSummary": ai_analysis,  # Tier 1: Abstract-based analysis
            "deepAnalysis": deep_analysis  # Tier 2: PDF-based analysis
        }
    except Exception as e:
        # Log error but don't fail - caller will fall back to arXiv
        print(f"Atlas DB lookup failed for {paper_id}: {e}")
        return None

@router.get("/embedding-caches", response_model=List[EmbeddingCacheInfo])
async def list_embedding_caches():
    return local_atlas_service.list_embedding_caches()


@router.get("/atlas/papers")
async def atlas_papers(
    limit: int = Query(40, ge=1, le=200),
    category: str = Query("all"),
    days: int = Query(0, ge=0),
    query: str = Query(""),
):
    if not local_atlas_service.enabled:
        raise HTTPException(status_code=503, detail="Atlas dataset is not loaded")
    papers = local_atlas_service.list_papers(
        limit=limit,
        category=category,
        days=days if days > 0 else None,
        query=query,
    )
    return {"papers": papers}


@router.get("/atlas/summary")
async def atlas_summary():
    if not local_atlas_service.enabled:
        raise HTTPException(status_code=503, detail="Atlas dataset is not loaded")
    return local_atlas_service.get_summary()


@router.get("/atlas/cache-stats")
async def atlas_cache_stats():
    """
    Get query embedding cache statistics.

    Returns cache performance metrics including:
    - cache_size: Current number of cached query embeddings
    - max_size: Maximum cache capacity
    - hits: Total cache hits
    - misses: Total cache misses
    - hit_rate: Percentage of requests served from cache

    High hit rates indicate better performance as cached queries
    avoid expensive model inference (200-3000ms → <1ms).
    """
    if not local_atlas_service.enabled:
        raise HTTPException(status_code=503, detail="Atlas dataset is not loaded")
    return local_atlas_service.get_cache_stats()


@router.get("/similar/{paper_id}")
async def get_similar_papers(
    paper_id: str,
    top_k: int = Query(10, ge=1, le=50, description="Number of similar papers to return"),
    category: Optional[str] = Query(None, description="Filter by arXiv category"),
    exclude_same_authors: bool = Query(False, description="Exclude papers by same authors"),
):
    """
    Find papers similar to a given paper using semantic embedding similarity.

    Uses cosine similarity between paper embeddings to find the most related papers.

    - **paper_id**: The arXiv ID of the paper to find similar papers for
    - **top_k**: Maximum number of similar papers to return (1-50)
    - **category**: Optional arXiv category filter (e.g., "cs.AI", "cs.LG")
    - **exclude_same_authors**: If true, excludes papers by the same authors

    Returns papers ranked by similarity score (0-1, higher = more similar).
    """
    if not local_atlas_service.enabled:
        raise HTTPException(status_code=503, detail="Atlas dataset is not loaded")

    if local_atlas_service._embeddings is None:
        raise HTTPException(
            status_code=503,
            detail="Embeddings not available. Similar papers requires embedding support."
        )

    # First check if the paper exists
    source_paper = local_atlas_service.get_paper_by_id(paper_id)
    if not source_paper:
        raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found in atlas")

    # Find similar papers
    similar_papers = local_atlas_service.find_similar(
        paper_id,
        top_k=top_k,
        category=category,
        exclude_same_authors=exclude_same_authors,
    )

    return {
        "source_paper": source_paper,
        "similar_papers": similar_papers,
        "count": len(similar_papers),
        "filters": {
            "category": category,
            "exclude_same_authors": exclude_same_authors,
        }
    }


@router.get("/graph/{paper_id}")
async def get_paper_graph(
    paper_id: str,
    max_depth: int = Query(2, ge=1, le=3, description="Maximum graph depth"),
    neighbors_per_node: int = Query(5, ge=1, le=10, description="Similar papers per node"),
    min_similarity: float = Query(0.5, ge=0.3, le=0.9, description="Minimum similarity threshold"),
    category: Optional[str] = Query(None, description="Filter by arXiv category"),
):
    """
    Get a citation/similarity graph for visualization.

    Returns a graph structure with nodes and edges suitable for visualization libraries
    like D3.js, Cytoscape, or react-force-graph.

    - **paper_id**: The central paper ID
    - **max_depth**: How many hops to explore (1-3)
    - **neighbors_per_node**: Number of similar papers per node (1-10)
    - **min_similarity**: Minimum similarity for edges (0.3-0.9)
    - **category**: Optional arXiv category filter

    Returns nodes with paper metadata and edges with similarity scores.
    """
    service = get_citation_graph_service()

    if not service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Citation graph service not available (no embeddings)"
        )

    graph = service.build_similarity_graph(
        paper_id,
        max_depth=max_depth,
        neighbors_per_node=neighbors_per_node,
        min_similarity=min_similarity,
        category=category,
    )

    if graph is None:
        raise HTTPException(
            status_code=404,
            detail=f"Paper '{paper_id}' not found in atlas"
        )

    return graph.to_dict()


@router.post("/graph/cluster")
async def get_cluster_graph(
    paper_ids: List[str] = Body(..., min_length=2, max_length=20),
    min_similarity: float = Query(0.5, ge=0.3, le=0.9),
):
    """
    Get a graph showing relationships between a set of papers.

    Useful for visualizing connections within a reading list or search results.

    - **paper_ids**: List of paper IDs to include (2-20)
    - **min_similarity**: Minimum similarity for edges

    Returns nodes for all papers and edges for pairs above the similarity threshold.
    """
    service = get_citation_graph_service()

    if not service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Citation graph service not available"
        )

    graph = service.build_cluster_graph(paper_ids, min_similarity=min_similarity)
    return graph.to_dict()


@router.get("/neighborhood/{paper_id}")
async def get_paper_neighborhood(
    paper_id: str,
    top_k: int = Query(15, ge=5, le=50, description="Number of neighbors to return"),
):
    """
    Get immediate neighborhood of a paper with similarity tiers.

    Simpler than the full graph - returns papers grouped by similarity level.

    - **paper_id**: The paper ID
    - **top_k**: Number of neighbors to return

    Returns papers grouped into: highly_similar (>0.85), similar (0.7-0.85), related (0.5-0.7)
    """
    service = get_citation_graph_service()

    if not service.enabled:
        raise HTTPException(
            status_code=503,
            detail="Citation graph service not available"
        )

    result = service.get_paper_neighborhood(paper_id, top_k=top_k)

    if "error" in result:
        raise HTTPException(status_code=503, detail=result["error"])

    return result


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_papers(
    query: str = Query(..., min_length=1, description="Search query for papers"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    enhance_with_ai: bool = Query(False, description="Whether to enhance with AI analysis")
):
    """
    Search for papers using arXiv API
    """
    # Validate query is not just whitespace
    if not query or not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    try:
        # Search for papers
        papers = await arxiv_service.search_papers(query.strip(), max_results)
        
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
    Contextual search: Analyze user's project description and find relevant papers with recommendations.

    Performance modes:
    - Default: Full pipeline with reranking + AI synthesis (~3-10s)
    - fast_mode=True: Skip both reranking and synthesis (~200-500ms)
    - skip_reranking=True: Skip reranking only (~500-2000ms savings)
    - skip_synthesis=True: Skip AI synthesis only (~2-5s savings)
    """
    try:
        user_description = request.description.strip()
        embedding_label = (request.embedding_label or "").strip() or None
        fallback_mode = getattr(ai_analysis_service, "fallback_mode", False)
        top_k = settings.CONTEXTUAL_SEARCH_TOP_K
        max_days = settings.CONTEXTUAL_SEARCH_MAX_DAYS

        # Fast mode implies both skip_reranking and skip_synthesis
        skip_reranking = request.fast_mode or request.skip_reranking
        skip_synthesis = request.fast_mode or request.skip_synthesis

        # Performance timing
        t_start = time.perf_counter()
        timing = {
            "retrieval_ms": 0.0,
            "rerank_ms": 0.0,
            "synthesis_ms": 0.0,
        }

        def _trim(text: str, limit: int = 600) -> str:
            text = (text or "").strip()
            if len(text) > limit:
                return text[:limit].rstrip() + "…"
            return text

        # Step 1: Retrieve candidates from the local atlas (semantic search + recency weighting)
        t_retrieval_start = time.perf_counter()
        try:
            papers = local_atlas_service.search(
                user_description,
                top_k=top_k,
                max_age_days=max_days,
                embedding_label=embedding_label,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        timing["retrieval_ms"] = (time.perf_counter() - t_retrieval_start) * 1000

        used_fallback = False

        if not papers:
            # Lightweight lexical fallback on the atlas
            papers = local_atlas_service.recent_papers(limit=top_k)

        if not papers:
            used_fallback = True
            papers = await arxiv_service.search_papers(user_description[:120], max_results=top_k)

        if not papers:
            total_ms = (time.perf_counter() - t_start) * 1000
            return ContextualSearchResponse(
                analysis="No relevant papers found for your project description.",
                papers=[],
                timing=ContextualSearchTiming(
                    total_ms=total_ms,
                    retrieval_ms=timing["retrieval_ms"],
                    rerank_ms=0,
                    synthesis_ms=0,
                    mode="no_results",
                ),
            )

        # Step 2: Normalize papers for downstream synthesis
        papers_for_response: List[Dict[str, Any]] = []
        for paper in papers:
            title = paper.get("title", "").strip()
            summary = paper.get("abstract") or paper.get("summary") or ""
            link = paper.get("link") or f"http://arxiv.org/abs/{paper.get('id', '')}"

            paper_data: Dict[str, Any] = {
                "id": link or paper.get("id", ""),
                "title": title,
                "summary": summary,
            }
            # Include relevance score for ranking transparency
            if "score" in paper:
                paper_data["relevance_score"] = round(float(paper["score"]), 3)
            papers_for_response.append(paper_data)

        # Optional reranking step (saves 500-2000ms when skipped)
        if not skip_reranking:
            t_rerank_start = time.perf_counter()
            rerank_service = get_rerank_service()
            papers_for_response = rerank_service.rerank(
                user_description,
                papers_for_response,
                top_k=top_k,
            )
            timing["rerank_ms"] = (time.perf_counter() - t_rerank_start) * 1000

        # Optional synthesis step (saves 2-5s when skipped)
        if skip_synthesis:
            # Fast path: return papers without AI synthesis
            total_ms = (time.perf_counter() - t_start) * 1000
            mode = "fast" if request.fast_mode else "skip_synthesis"
            return ContextualSearchResponse(
                analysis="Fast mode: AI synthesis skipped for faster response.",
                papers=papers_for_response,
                timing=ContextualSearchTiming(
                    total_ms=total_ms,
                    retrieval_ms=timing["retrieval_ms"],
                    rerank_ms=timing["rerank_ms"],
                    synthesis_ms=0,
                    mode=mode,
                ),
            )

        papers_formatted: List[str] = [
            f"- Title: {item['title']}\n  Summary: {_trim(item.get('summary', ''))}"
            for item in papers_for_response
        ]
        papers_text = "\n".join(papers_formatted)

        # Step 3: Generate synthesis and recommendations
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

        # Step 3: AI synthesis
        t_synthesis_start = time.perf_counter()
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
                # Add 25-second timeout to prevent hanging (leaves 5s buffer before frontend 30s timeout)
                synthesis_response = await asyncio.wait_for(
                    ai_analysis_service.model.generate_content_async(synthesis_prompt),
                    timeout=25.0
                )
                analysis_text = synthesis_response.text
            except asyncio.TimeoutError:
                fallback_mode = True
                bullet_points = "\n".join(
                    [
                        f"- {paper.get('title', 'Untitled')} — inspect its methodology for actionable leads."
                        for paper in papers_for_response[:3]
                    ]
                )
                analysis_text = (
                    "AI synthesis took too long. "
                    "Here is a quick brief of promising papers:\n"
                    f"{bullet_points}"
                )
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
        timing["synthesis_ms"] = (time.perf_counter() - t_synthesis_start) * 1000

        if used_fallback and not fallback_mode:
            analysis_text = (
                analysis_text
                + "\n\n_Note: pulled from live arXiv due to no local atlas match._"
            )

        # Calculate total time and determine mode
        total_ms = (time.perf_counter() - t_start) * 1000
        mode = "full"
        if skip_reranking:
            mode = "skip_rerank"

        return ContextualSearchResponse(
            analysis=analysis_text,
            papers=papers_for_response,
            timing=ContextualSearchTiming(
                total_ms=total_ms,
                retrieval_ms=timing["retrieval_ms"],
                rerank_ms=timing["rerank_ms"],
                synthesis_ms=timing["synthesis_ms"],
                mode=mode,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Contextual search failed: {str(e)}"
        )


def _build_full_test_code(tests) -> str:
    """Build complete test file from TestSuite for API response."""
    if not tests:
        return ""

    test_file = f"""# Auto-generated test file
import pytest
import torch
import numpy as np
from model import *
from config import *

{tests.fixtures}

# Functionality Tests
"""
    for test in tests.functionality_tests:
        test_file += f"\n{test.test_code}\n"

    test_file += "\n# Correctness Tests\n"
    for test in tests.correctness_tests:
        test_file += f"\n{test.test_code}\n"

    test_file += "\n# Edge Case Tests\n"
    for test in tests.edge_case_tests:
        test_file += f"\n{test.test_code}\n"

    test_file += "\n# Performance Tests\n"
    for test in tests.performance_tests:
        test_file += f"\n{test.test_code}\n"

    return test_file


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

        # Get paper details - try atlas-db first, then fall back to arXiv
        paper = await get_paper_from_atlas_db(paper_id)

        if not paper:
            # Fall back to arXiv API for papers not in our database
            paper = await arxiv_service.get_paper_by_id(paper_id)

        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found in atlas database or arXiv")

        # Get AI analysis if not already present or is None
        if not paper.get('aiSummary'):
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

        # Return formatted response matching frontend GenerationResult interface
        return {
            "success": result.success,
            "generation_time_seconds": result.generation_time_seconds,
            "paper": {
                "id": result.paper_id,
                "title": result.paper_title,
                "analysis_summary": result.analysis_summary
            },
            "code": {
                "main_code": result.code.main_code if result.code else None,
                "test_code": _build_full_test_code(result.tests) if result.tests else None,
                "example_code": result.code.example_code if result.code else None,
                "config_code": result.code.config_code if result.code else None,
                "dependencies": result.code.dependencies if result.code else [],
                "framework": result.code.framework if result.code else "pytorch"
            },
            "tests": {
                "total_tests": result.tests.total_tests if result.tests else 0,
                "functionality_count": len(result.tests.functionality_tests) if result.tests else 0,
                "correctness_count": len(result.tests.correctness_tests) if result.tests else 0,
                "edge_case_count": len(result.tests.edge_case_tests) if result.tests else 0,
                "performance_count": len(result.tests.performance_tests) if result.tests else 0
            },
            "test_results": {
                "tests_passed": result.test_results.tests_passed if result.test_results else 0,
                "tests_total": result.test_results.tests_total if result.test_results else 0,
                "tests_failed": result.test_results.tests_failed if result.test_results else 0,
                "execution_time": result.test_results.execution_time if result.test_results else 0,
                "error_summary": result.test_results.error_summary if result.test_results else None,
                "stdout": result.test_results.stdout[:2000] if result.test_results and result.test_results.stdout else None,
                "stderr": result.test_results.stderr[:2000] if result.test_results and result.test_results.stderr else None
            },
            "debug_iterations": result.debug_iterations,
            "readme": result.readme,
            "system_reflection": result.system_reflection
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

        # Get paper details - try atlas-db first, then fall back to arXiv
        paper = await get_paper_from_atlas_db(paper_id)

        if not paper:
            # Fall back to arXiv API for papers not in our database
            paper = await arxiv_service.get_paper_by_id(paper_id)

        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found in atlas database or arXiv")

        # Get AI analysis if not already present or is None
        if not paper.get('aiSummary'):
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

        # Return formatted response matching frontend GenerationResult interface
        return {
            "success": result.success,
            "generation_time_seconds": result.generation_time_seconds,
            "approach": "simple",  # Mark which approach was used
            "paper": {
                "id": result.paper_id,
                "title": result.paper_title
            },
            "code": {
                "main_code": result.code,
                "test_code": result.tests,
                "config_code": result.config,
                "example_code": result.example,
                "dependencies": []
            },
            "tests": {
                "total_tests": result.tests_total
            },
            "test_results": {
                "tests_passed": result.tests_passed,
                "tests_total": result.tests_total,
                "tests_failed": result.tests_failed
            },
            "debug_iterations": result.debug_iterations,
            "readme": result.readme,
            "system_reflection": result.reflection
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simple code generation failed: {str(e)}"
        )
