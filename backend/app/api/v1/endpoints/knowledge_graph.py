"""
Knowledge graph API endpoints

Provides access to all 5 query patterns:
1. Semantic similarity
2. Concept exploration
3. Citation networks
4. Latest research
5. Benchmark leaderboards
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.similarity_service import get_similarity_service
from app.services.embedding_service import get_embedding_service


router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])


# ============================================================================
# Response Models
# ============================================================================

class SimilarPaper(BaseModel):
    """Similar paper with similarity score"""
    id: str
    title: str
    abstract: str
    published_date: datetime
    category: str
    citation_count: int
    similarity: float = Field(ge=0.0, le=1.0)


class ConceptPaper(BaseModel):
    """Paper related to a concept"""
    id: str
    title: str
    abstract: str
    published_date: datetime
    category: str
    citation_count: int
    relevance: float
    concept_name: str


class TrendingConcept(BaseModel):
    """Trending research concept"""
    id: int
    name: str
    category: Optional[str]
    total_papers: int
    recent_papers: int
    avg_relevance: float
    growth_percentage: float


class CitationNode(BaseModel):
    """Paper node in citation graph"""
    paper_id: str
    title: str
    published_date: datetime
    citation_count: int
    is_influential: bool
    depth: int


class CitationNetwork(BaseModel):
    """Citation network graph"""
    center: str
    nodes: List[str]
    edges: List[dict]


class BenchmarkEntry(BaseModel):
    """Benchmark leaderboard entry"""
    id: str
    title: str
    published_date: datetime
    citation_count: int
    task: str
    dataset: str
    metric: str
    score: float
    model_name: Optional[str]
    model_size: Optional[str]
    rank: int


class EmbeddingStats(BaseModel):
    """Embedding coverage statistics"""
    papers: dict
    concepts: dict


# ============================================================================
# 1. SEMANTIC SIMILARITY ENDPOINTS
# ============================================================================

@router.get("/papers/{paper_id}/similar", response_model=List[SimilarPaper])
async def get_similar_papers(
    paper_id: str,
    limit: int = Query(10, ge=1, le=100),
    min_similarity: float = Query(0.7, ge=0.0, le=1.0),
    exclude_cited: bool = Query(False)
):
    """
    Find semantically similar papers using vector embeddings

    - **paper_id**: Source paper arXiv ID
    - **limit**: Maximum results (1-100)
    - **min_similarity**: Minimum cosine similarity (0.0-1.0)
    - **exclude_cited**: Exclude papers already cited by source paper
    """
    service = get_similarity_service()

    try:
        papers = await service.find_similar_papers(
            paper_id=paper_id,
            limit=limit,
            min_similarity=min_similarity,
            exclude_cited=exclude_cited
        )

        if not papers:
            raise HTTPException(
                status_code=404,
                detail=f"No similar papers found for {paper_id}. Paper may not have embedding."
            )

        return papers

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/semantic", response_model=List[SimilarPaper])
async def semantic_search(
    query: str = Query(..., min_length=3),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    days: Optional[int] = Query(None, ge=1)
):
    """
    Search papers by semantic similarity to text query

    - **query**: Search query text
    - **limit**: Maximum results
    - **category**: Optional category filter (e.g., 'cs.AI')
    - **days**: Optional recency filter (papers from last N days)
    """
    embedding_service = get_embedding_service()
    similarity_service = get_similarity_service()

    try:
        # Generate embedding for query
        embedding = await embedding_service.generate_embedding(query)

        # Calculate minimum date if days specified
        min_date = None
        if days:
            min_date = datetime.now() - timedelta(days=days)

        # Search papers
        papers = await similarity_service.find_similar_by_text(
            text_embedding=embedding,
            limit=limit,
            category=category,
            min_date=min_date
        )

        return papers

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 2. CONCEPT EXPLORATION ENDPOINTS
# ============================================================================

@router.get("/concepts/{concept_name}/papers", response_model=List[ConceptPaper])
async def get_papers_by_concept(
    concept_name: str,
    limit: int = Query(20, ge=1, le=100),
    min_relevance: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    Find papers related to a specific concept

    - **concept_name**: Concept name (fuzzy matching)
    - **limit**: Maximum results
    - **min_relevance**: Minimum relevance score
    """
    service = get_similarity_service()

    try:
        papers = await service.find_papers_by_concept(
            concept_name=concept_name,
            limit=limit,
            min_relevance=min_relevance
        )

        if not papers:
            raise HTTPException(
                status_code=404,
                detail=f"No papers found for concept '{concept_name}'"
            )

        return papers

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers/{paper_id}/similar-by-concepts")
async def get_similar_by_concepts(
    paper_id: str,
    limit: int = Query(10, ge=1, le=100),
    min_shared: int = Query(2, ge=1)
):
    """
    Find papers that share concepts with given paper

    - **paper_id**: Source paper ID
    - **limit**: Maximum results
    - **min_shared**: Minimum number of shared concepts
    """
    service = get_similarity_service()

    try:
        papers = await service.find_similar_by_concepts(
            paper_id=paper_id,
            limit=limit,
            min_shared_concepts=min_shared
        )

        return papers

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concepts/trending", response_model=List[TrendingConcept])
async def get_trending_concepts(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None)
):
    """
    Get trending research concepts based on recent papers

    - **days**: Look back period (1-365 days)
    - **limit**: Maximum results
    - **category**: Optional category filter
    """
    service = get_similarity_service()

    try:
        concepts = await service.get_trending_concepts(
            days=days,
            limit=limit,
            category=category
        )

        return concepts

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 3. CITATION NETWORK ENDPOINTS
# ============================================================================

@router.get("/papers/{paper_id}/citations/ancestry")
async def get_citation_ancestry(
    paper_id: str,
    max_depth: int = Query(3, ge=1, le=5),
    limit_per_level: int = Query(10, ge=1, le=50)
):
    """
    Get papers cited by this paper (ancestry tree)

    - **paper_id**: Source paper ID
    - **max_depth**: Maximum recursion depth (1-5)
    - **limit_per_level**: Max papers per depth level
    """
    service = get_similarity_service()

    try:
        tree = await service.get_citation_ancestry(
            paper_id=paper_id,
            max_depth=max_depth,
            limit_per_level=limit_per_level
        )

        return tree

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers/{paper_id}/citations/descendants")
async def get_citation_descendants(
    paper_id: str,
    max_depth: int = Query(3, ge=1, le=5),
    limit_per_level: int = Query(10, ge=1, le=50)
):
    """
    Get papers that cite this paper (descendant tree)

    - **paper_id**: Source paper ID
    - **max_depth**: Maximum recursion depth (1-5)
    - **limit_per_level**: Max papers per depth level
    """
    service = get_similarity_service()

    try:
        tree = await service.get_citation_descendants(
            paper_id=paper_id,
            max_depth=max_depth,
            limit_per_level=limit_per_level
        )

        return tree

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/papers/{paper_id}/citations/network", response_model=CitationNetwork)
async def get_citation_network(
    paper_id: str,
    radius: int = Query(2, ge=1, le=3)
):
    """
    Get local citation network (both ancestors and descendants)

    Perfect for graph visualizations. Returns nodes and edges.

    - **paper_id**: Center paper ID
    - **radius**: How many hops in each direction (1-3)
    """
    service = get_similarity_service()

    try:
        network = await service.get_citation_network(
            paper_id=paper_id,
            radius=radius
        )

        return network

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 4. LATEST RESEARCH ENDPOINTS
# ============================================================================

@router.get("/papers/latest")
async def get_latest_papers(
    category: Optional[str] = Query(None),
    concepts: Optional[List[str]] = Query(None),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    min_quality: float = Query(0.0, ge=0.0, le=1.0)
):
    """
    Get latest papers in a domain/topic

    - **category**: arXiv category (e.g., 'cs.AI', 'cs.CV')
    - **concepts**: List of concept names to filter by
    - **days**: Look back period (1-365 days)
    - **limit**: Maximum results
    - **min_quality**: Minimum quality score (0.0-1.0)
    """
    service = get_similarity_service()

    try:
        papers = await service.get_latest_papers(
            category=category,
            concepts=concepts,
            days=days,
            limit=limit,
            min_quality=min_quality
        )

        return papers

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 5. BENCHMARK LEADERBOARD ENDPOINTS
# ============================================================================

@router.get("/benchmarks/leaderboard", response_model=List[BenchmarkEntry])
async def get_benchmark_leaderboard(
    task: str = Query(..., min_length=2),
    dataset: str = Query(..., min_length=2),
    metric: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get benchmark leaderboard for a task/dataset

    - **task**: Task name (e.g., 'image classification', 'question answering')
    - **dataset**: Dataset name (e.g., 'ImageNet', 'SQuAD')
    - **metric**: Optional metric filter (e.g., 'accuracy', 'F1')
    - **limit**: Maximum results
    """
    service = get_similarity_service()

    try:
        leaderboard = await service.get_benchmark_leaderboard(
            task=task,
            dataset=dataset,
            metric=metric,
            limit=limit
        )

        if not leaderboard:
            raise HTTPException(
                status_code=404,
                detail=f"No benchmarks found for task='{task}', dataset='{dataset}'"
            )

        return leaderboard

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/trending-techniques")
async def get_trending_techniques(
    task: str = Query(..., min_length=2),
    days: int = Query(180, ge=1, le=730),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get techniques with improving performance over time

    - **task**: Task name
    - **days**: Look back period (1-730 days)
    - **limit**: Maximum results
    """
    service = get_similarity_service()

    try:
        techniques = await service.get_trending_techniques(
            task=task,
            days=days,
            limit=limit
        )

        return techniques

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADMIN / UTILITY ENDPOINTS
# ============================================================================

@router.get("/embeddings/stats", response_model=EmbeddingStats)
async def get_embedding_stats():
    """
    Get statistics about embedding coverage

    Returns counts and percentages for papers and concepts with embeddings.
    """
    service = get_embedding_service()

    try:
        stats = await service.get_embedding_stats()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings/backfill")
async def backfill_embeddings(
    batch_size: int = Query(100, ge=1, le=500),
    max_papers: Optional[int] = Query(None, ge=1)
):
    """
    Backfill embeddings for papers that don't have them

    **Admin endpoint** - generates embeddings for papers without them.

    - **batch_size**: Papers to process per batch (1-500)
    - **max_papers**: Max total papers to process (None = all)

    Returns progress statistics.
    """
    service = get_embedding_service()

    try:
        result = await service.backfill_embeddings(
            batch_size=batch_size,
            max_papers=max_papers
        )

        return {
            "status": "completed",
            "total": result["total"],
            "success": result["success"],
            "failed": result["failed"],
            "success_rate": f"{100 * result['success'] / result['total']:.1f}%"
                if result["total"] > 0 else "N/A"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def knowledge_graph_health():
    """
    Health check for knowledge graph services

    Verifies database connection and embedding service availability.
    """
    from app.db.database import database

    try:
        # Test database connection
        await database.fetch_one("SELECT 1")

        # Test embedding service
        embedding_service = get_embedding_service()
        stats = await embedding_service.get_embedding_stats()

        return {
            "status": "healthy",
            "database": "connected",
            "embedding_service": "active",
            "papers_with_embeddings": stats["papers"]["with_embedding"],
            "embedding_coverage": f"{stats['papers']['coverage_percentage']:.1f}%"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
