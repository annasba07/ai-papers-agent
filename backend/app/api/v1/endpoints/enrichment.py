"""
Paper Enrichment API Endpoints

Provides access to:
- Citation data (OpenAlex)
- Code repositories (Papers With Code)
- Benchmark results
- Technique extraction
- Citation graphs
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from app.services.enrichment_service import get_enrichment_service, EnrichedPaper
from app.services.providers.openalex_provider import get_openalex_provider, CitationInfo
from app.services.providers.pwc_provider import get_pwc_provider, PWCRepository, PWCResult
from app.services.technique_extraction_service import (
    get_technique_extraction_service,
    TechniqueExtractionResult
)


router = APIRouter(prefix="/enrichment", tags=["Enrichment"])


# ============================================================================
# Response Models
# ============================================================================

class CitationResponse(BaseModel):
    """Citation data response"""
    paper_id: str
    cited_by_count: int
    references_count: int
    openalex_id: Optional[str] = None
    concepts: List[Dict[str, Any]] = []


class RepositoryResponse(BaseModel):
    """Code repository response"""
    url: str
    owner: str
    name: str
    stars: int
    framework: Optional[str] = None
    is_official: bool = False


class BenchmarkResponse(BaseModel):
    """Benchmark result response"""
    task: str
    dataset: str
    metric: str
    value: float
    model_name: Optional[str] = None


class TechniqueResponse(BaseModel):
    """Extracted technique"""
    name: str
    normalized_name: str
    category: Optional[str] = None
    technique_type: Optional[str] = None
    is_primary: bool = False
    confidence: float


class CitationGraphResponse(BaseModel):
    """Citation graph structure"""
    center: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    node_count: int
    edge_count: int


class BatchEnrichmentRequest(BaseModel):
    """Request for batch enrichment"""
    papers: List[Dict[str, Any]] = Field(..., description="Papers with id, title, abstract")
    include_citations: bool = True
    include_code: bool = True
    include_benchmarks: bool = True
    include_techniques: bool = True


# ============================================================================
# CITATION ENDPOINTS
# ============================================================================

@router.get("/papers/{paper_id}/citations", response_model=CitationResponse)
async def get_paper_citations(paper_id: str):
    """
    Get citation data for a paper from OpenAlex

    - **paper_id**: arXiv paper ID (e.g., "2106.09685")

    Returns citation count, reference count, and OpenAlex concepts.
    """
    provider = get_openalex_provider()

    try:
        info = await provider.get_citation_info(paper_id)

        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"No citation data found for paper {paper_id}"
            )

        return CitationResponse(
            paper_id=info.paper_id,
            cited_by_count=info.cited_by_count,
            references_count=info.references_count,
            openalex_id=info.openalex_id,
            concepts=info.concepts
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers/{paper_id}/citing")
async def get_citing_papers(
    paper_id: str,
    limit: int = Query(25, ge=1, le=100)
):
    """
    Get papers that cite this paper

    - **paper_id**: arXiv paper ID
    - **limit**: Maximum results (1-100)
    """
    provider = get_openalex_provider()

    try:
        papers = await provider.get_citing_papers(paper_id, limit=limit)

        return {
            "paper_id": paper_id,
            "citing_papers": [
                {
                    "arxiv_id": p.arxiv_id,
                    "title": p.title,
                    "cited_by_count": p.cited_by_count,
                    "publication_date": p.publication_date
                }
                for p in papers
            ],
            "count": len(papers)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers/{paper_id}/references")
async def get_paper_references(
    paper_id: str,
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get papers that this paper references

    - **paper_id**: arXiv paper ID
    - **limit**: Maximum results (1-100)
    """
    provider = get_openalex_provider()

    try:
        papers = await provider.get_references(paper_id, limit=limit)

        return {
            "paper_id": paper_id,
            "references": [
                {
                    "arxiv_id": p.arxiv_id,
                    "title": p.title,
                    "cited_by_count": p.cited_by_count,
                    "publication_date": p.publication_date
                }
                for p in papers
            ],
            "count": len(papers)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers/{paper_id}/citation-graph", response_model=CitationGraphResponse)
async def get_citation_graph(
    paper_id: str,
    depth: int = Query(1, ge=1, le=3),
    max_papers: int = Query(20, ge=5, le=50)
):
    """
    Build a citation graph around a paper

    - **paper_id**: Center paper arXiv ID
    - **depth**: How many hops to traverse (1-3)
    - **max_papers**: Maximum papers to include (5-50)

    Returns graph data with nodes and edges suitable for visualization.
    """
    service = get_enrichment_service()

    try:
        graph = await service.get_citation_graph(
            paper_id=paper_id,
            depth=depth,
            max_papers=max_papers
        )

        return CitationGraphResponse(**graph)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CODE REPOSITORY ENDPOINTS
# ============================================================================

@router.get("/papers/{paper_id}/repositories", response_model=List[RepositoryResponse])
async def get_paper_repositories(paper_id: str):
    """
    Get code repositories for a paper from Papers With Code

    - **paper_id**: arXiv paper ID
    """
    provider = get_pwc_provider()

    try:
        repos = await provider.get_repositories(paper_id)

        return [
            RepositoryResponse(
                url=r.url,
                owner=r.owner,
                name=r.name,
                stars=r.stars,
                framework=r.framework,
                is_official=r.is_official
            )
            for r in repos
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BENCHMARK ENDPOINTS
# ============================================================================

@router.get("/papers/{paper_id}/benchmarks", response_model=List[BenchmarkResponse])
async def get_paper_benchmarks(paper_id: str):
    """
    Get benchmark results for a paper from Papers With Code

    - **paper_id**: arXiv paper ID
    """
    provider = get_pwc_provider()

    try:
        results = await provider.get_paper_results(paper_id)

        return [
            BenchmarkResponse(
                task=r.task,
                dataset=r.dataset,
                metric=r.metric,
                value=r.value,
                model_name=r.model_name
            )
            for r in results
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sota/{task}")
async def get_state_of_the_art(
    task: str,
    dataset: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get state-of-the-art results for a task

    - **task**: Task name (e.g., "Image Classification")
    - **dataset**: Optional dataset filter (e.g., "ImageNet")
    - **limit**: Maximum results
    """
    provider = get_pwc_provider()

    try:
        results = await provider.get_sota_for_task(
            task=task,
            dataset=dataset,
            limit=limit
        )

        return {
            "task": task,
            "dataset": dataset,
            "results": [
                {
                    "metric": r.metric,
                    "value": r.value,
                    "model_name": r.model_name,
                    "paper_title": r.paper_title,
                    "paper_arxiv_id": r.paper_arxiv_id
                }
                for r in results
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TECHNIQUE EXTRACTION ENDPOINTS
# ============================================================================

@router.get("/papers/{paper_id}/techniques")
async def get_paper_techniques(
    paper_id: str,
    title: str = Query(..., description="Paper title"),
    abstract: str = Query(..., description="Paper abstract")
):
    """
    Extract techniques from a paper

    - **paper_id**: arXiv paper ID
    - **title**: Paper title
    - **abstract**: Paper abstract

    Uses LLM extraction when available, with heuristic fallback.
    """
    service = get_technique_extraction_service()

    try:
        result = await service.extract_techniques(
            paper_id=paper_id,
            title=title,
            abstract=abstract
        )

        return {
            "paper_id": result.paper_id,
            "techniques": [
                {
                    "name": t.name,
                    "normalized_name": t.normalized_name,
                    "category": t.category,
                    "technique_type": t.technique_type,
                    "is_primary": t.is_primary,
                    "confidence": t.confidence
                }
                for t in result.techniques
            ],
            "architecture_type": result.architecture_type,
            "task_domains": result.task_domains,
            "novelty_type": result.novelty_type,
            "key_components": result.key_components,
            "extraction_method": result.extraction_method
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/papers/{paper_id}/techniques")
async def extract_techniques_from_body(
    paper_id: str,
    paper_data: Dict[str, Any] = Body(...)
):
    """
    Extract techniques from a paper (POST version for long abstracts)

    Body should contain:
    - **title**: Paper title
    - **abstract**: Paper abstract
    """
    service = get_technique_extraction_service()

    title = paper_data.get("title", "")
    abstract = paper_data.get("abstract", paper_data.get("summary", ""))

    if not title or not abstract:
        raise HTTPException(
            status_code=400,
            detail="Both title and abstract are required"
        )

    try:
        result = await service.extract_techniques(
            paper_id=paper_id,
            title=title,
            abstract=abstract
        )

        return {
            "paper_id": result.paper_id,
            "techniques": [t.model_dump() for t in result.techniques],
            "architecture_type": result.architecture_type,
            "task_domains": result.task_domains,
            "novelty_type": result.novelty_type,
            "key_components": result.key_components,
            "extraction_method": result.extraction_method
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FULL ENRICHMENT ENDPOINTS
# ============================================================================

@router.get("/papers/{paper_id}/enrich")
async def enrich_paper(
    paper_id: str,
    title: str = Query(...),
    abstract: str = Query(...),
    include_citations: bool = Query(True),
    include_code: bool = Query(True),
    include_benchmarks: bool = Query(True),
    include_techniques: bool = Query(True)
):
    """
    Fully enrich a paper with all available data

    Combines:
    - Citation data from OpenAlex
    - Code repositories from Papers With Code
    - Benchmark results from Papers With Code
    - Extracted techniques

    - **paper_id**: arXiv paper ID
    - **title**: Paper title
    - **abstract**: Paper abstract
    """
    service = get_enrichment_service()

    try:
        enriched = await service.enrich_paper(
            paper_id=paper_id,
            title=title,
            abstract=abstract,
            include_citations=include_citations,
            include_code=include_code,
            include_benchmarks=include_benchmarks,
            include_techniques=include_techniques
        )

        return enriched.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/papers/batch-enrich")
async def batch_enrich_papers(request: BatchEnrichmentRequest = Body(...)):
    """
    Enrich multiple papers at once

    More efficient than individual requests due to concurrent processing.

    Body:
    - **papers**: List of papers with id, title, abstract
    - **include_***: Which enrichment types to include
    """
    service = get_enrichment_service()

    if len(request.papers) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 papers per batch"
        )

    try:
        results = await service.batch_enrich_papers(
            papers=request.papers,
            include_citations=request.include_citations,
            include_code=request.include_code,
            include_benchmarks=request.include_benchmarks,
            include_techniques=request.include_techniques
        )

        return {
            "enriched": {
                paper_id: enriched.model_dump()
                for paper_id, enriched in results.items()
            },
            "count": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
