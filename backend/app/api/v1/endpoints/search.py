"""
Unified search API endpoint.

Returns a consistent search payload for keyword and semantic results,
optionally including an analysis summary for advisor flows.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal, Tuple
from time import perf_counter
import asyncio
import logging

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.api.v1.endpoints import atlas_db
from app.api.v1.endpoints.papers import contextual_search
from app.schemas.paper import ContextualSearchRequest
from app.services.local_atlas_service import local_atlas_service

router = APIRouter(prefix="/search")
logger = logging.getLogger(__name__)

KEYWORD_TIMEOUT_S = 3.0
SEMANTIC_TIMEOUT_S = 3.0
ANALYSIS_TIMEOUT_S = 12.0


class SearchRequest(BaseModel):
    query: str = ""
    limit: int = 20
    offset: int = 0
    order_by: Optional[str] = None
    order_dir: str = "desc"
    category: Optional[str] = None
    days: Optional[int] = None
    has_deep_analysis: Optional[bool] = None
    min_impact_score: Optional[int] = None
    min_reproducibility: Optional[int] = None
    difficulty_level: Optional[str] = None
    has_code: Optional[bool] = None
    seminal_only: Optional[bool] = None
    mode: Literal["hybrid", "keyword_only", "semantic_only"] = "hybrid"
    include_analysis: bool = False
    analysis_mode: Literal["fast", "deep"] = "fast"


def _extract_paper_id(id_or_url: str) -> str:
    """Extract arXiv ID from URLs or versioned IDs."""
    if not id_or_url:
        return ""
    paper_id = id_or_url
    if "arxiv.org" in id_or_url:
        import re
        match = re.search(r"(?:abs|pdf)/(\d+\.\d+)", id_or_url)
        if match:
            paper_id = match.group(1)
    if "v" in paper_id:
        paper_id = paper_id.split("v")[0]
    return paper_id


def _map_semantic_from_atlas(record: Dict[str, Any]) -> Dict[str, Any]:
    paper_id = record.get("id", "")
    return {
        "id": paper_id,
        "title": record.get("title", ""),
        "abstract": record.get("abstract", ""),
        "authors": record.get("authors", []) or [],
        "published": record.get("published") or "",
        "category": record.get("category") or "",
        "link": record.get("link") or (f"https://arxiv.org/abs/{_extract_paper_id(paper_id)}" if paper_id else ""),
        "citation_count": record.get("citation_count") or 0,
        "concepts": record.get("concepts") or [],
        "_source": "semantic",
        "_relevanceScore": record.get("score", 1.0),
    }


def _map_semantic_from_contextual(paper: Dict[str, Any]) -> Dict[str, Any]:
    raw_id = str(paper.get("id", ""))
    paper_id = _extract_paper_id(raw_id)
    link = raw_id if raw_id.startswith("http") else (f"https://arxiv.org/abs/{paper_id}" if paper_id else "")
    return {
        "id": paper_id or raw_id,
        "title": paper.get("title", ""),
        "abstract": paper.get("summary", "") or "",
        "authors": [],
        "published": "",
        "category": "",
        "link": link,
        "citation_count": 0,
        "concepts": [],
        "_source": "semantic",
        "_relevanceScore": paper.get("relevance_score", 1.0),
    }


async def _keyword_search(payload: SearchRequest) -> Dict[str, Any]:
    return await atlas_db.get_papers(
        limit=payload.limit,
        offset=payload.offset,
        category=payload.category,
        query=payload.query or None,
        days=payload.days,
        order_by=payload.order_by,
        order_dir=payload.order_dir,
        min_impact_score=payload.min_impact_score,
        min_reproducibility=payload.min_reproducibility,
        difficulty_level=payload.difficulty_level,
        has_deep_analysis=payload.has_deep_analysis,
        has_code=payload.has_code,
        seminal_only=payload.seminal_only,
    )


async def _safe_keyword_search(payload: SearchRequest) -> Dict[str, Any]:
    try:
        return await asyncio.wait_for(_keyword_search(payload), timeout=KEYWORD_TIMEOUT_S)
    except asyncio.TimeoutError:
        logger.warning("Keyword search timed out", extra={"query": payload.query})
    except Exception as exc:
        logger.warning("Keyword search failed", exc_info=exc)
    return {"papers": [], "total": 0, "has_more": False}


async def _safe_semantic_search(payload: SearchRequest, query: str) -> List[Dict[str, Any]]:
    if not local_atlas_service.enabled:
        return []

    def _search() -> List[Dict[str, Any]]:
        return local_atlas_service.search(
            query,
            top_k=payload.limit,
            category=payload.category,
            max_age_days=payload.days,
        )

    try:
        return await asyncio.wait_for(asyncio.to_thread(_search), timeout=SEMANTIC_TIMEOUT_S)
    except asyncio.TimeoutError:
        logger.warning("Semantic search timed out", extra={"query": query})
    except Exception as exc:
        logger.warning("Semantic search failed", exc_info=exc)
    return []


def _simplify_query(query: str) -> Optional[str]:
    words = [w for w in query.split() if len(w) >= 3]
    if len(words) >= 3:
        return " ".join(words[:2])
    return None


async def _handle_search(payload: SearchRequest) -> Dict[str, Any]:
    start_time = perf_counter()
    timing = {"semantic_ms": 0.0, "keyword_ms": 0.0, "total_ms": 0.0}

    semantic_results: List[Dict[str, Any]] = []
    keyword_results: List[Dict[str, Any]] = []
    total_keyword = 0
    has_more = False
    database_total: Optional[int] = None
    analysis_text: Optional[str] = None

    mode = payload.mode
    query = payload.query.strip()

    if payload.include_analysis and query:
        analysis_request = ContextualSearchRequest(
            description=query,
            fast_mode=payload.analysis_mode == "fast",
            skip_reranking=False,
            skip_synthesis=payload.analysis_mode != "deep",
        )
        try:
            analysis_response = await asyncio.wait_for(
                contextual_search(analysis_request),
                timeout=ANALYSIS_TIMEOUT_S,
            )
        except Exception as exc:
            logger.warning("Contextual search failed", exc_info=exc)
        else:
            analysis_text = analysis_response.analysis
            semantic_results = [_map_semantic_from_contextual(p) for p in analysis_response.papers]
            mode = "semantic_only"

    if mode != "keyword_only":
        if query and not semantic_results:
            semantic_start = perf_counter()
            papers = await _safe_semantic_search(payload, query)
            semantic_results = [_map_semantic_from_atlas(p) for p in papers]
            timing["semantic_ms"] = (perf_counter() - semantic_start) * 1000

    if mode != "semantic_only":
        keyword_start = perf_counter()
        keyword_payload = await _safe_keyword_search(payload)
        timing["keyword_ms"] = (perf_counter() - keyword_start) * 1000
        keyword_results = keyword_payload.get("papers", []) or []
        total_keyword = keyword_payload.get("total", len(keyword_results))
        has_more = keyword_payload.get("has_more", False)
        database_total = keyword_payload.get("total")

    if query and not semantic_results and not keyword_results and mode != "semantic_only":
        simplified = _simplify_query(query)
        if simplified:
            retry_payload = payload.copy(update={"query": simplified, "limit": payload.limit * 2})
            retry_keyword = await _safe_keyword_search(retry_payload)
            keyword_results = retry_keyword.get("papers", []) or []
            total_keyword = retry_keyword.get("total", len(keyword_results))
            has_more = retry_keyword.get("has_more", False)
            database_total = retry_keyword.get("total")

    if semantic_results and keyword_results:
        keyword_by_id = {paper.get("id"): paper for paper in keyword_results if paper.get("id")}
        enriched_semantic = []
        for paper in semantic_results:
            full = keyword_by_id.get(paper.get("id"))
            if full:
                enriched = {**full, "_source": "semantic", "_relevanceScore": paper.get("_relevanceScore", 1.0)}
                enriched_semantic.append(enriched)
            else:
                enriched_semantic.append(paper)
        semantic_results = enriched_semantic
        seen_ids = {paper.get("id") for paper in semantic_results if paper.get("id")}
        keyword_results = [paper for paper in keyword_results if paper.get("id") not in seen_ids]

    timing["total_ms"] = (perf_counter() - start_time) * 1000

    return {
        "analysis": analysis_text,
        "semanticResults": semantic_results,
        "keywordResults": keyword_results,
        "totalSemantic": len(semantic_results),
        "totalKeyword": total_keyword,
        "has_more": has_more,
        "databaseTotal": database_total,
        "timing": timing,
        "searchMode": "hybrid" if query and mode == "hybrid" else mode,
    }


@router.get("")
async def search_get(
    query: str = Query("", alias="query"),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    order_by: Optional[str] = Query(None),
    order_dir: str = Query("desc"),
    category: Optional[str] = Query(None),
    days: Optional[int] = Query(None, ge=1),
    has_deep_analysis: Optional[bool] = Query(None),
    min_impact_score: Optional[int] = Query(None, ge=1, le=10),
    min_reproducibility: Optional[int] = Query(None, ge=1, le=10),
    difficulty_level: Optional[str] = Query(None),
    has_code: Optional[bool] = Query(None),
    seminal_only: Optional[bool] = Query(None),
    mode: Literal["hybrid", "keyword_only", "semantic_only"] = Query("hybrid"),
):
    payload = SearchRequest(
        query=query,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_dir=order_dir,
        category=category,
        days=days,
        has_deep_analysis=has_deep_analysis,
        min_impact_score=min_impact_score,
        min_reproducibility=min_reproducibility,
        difficulty_level=difficulty_level,
        has_code=has_code,
        seminal_only=seminal_only,
        mode=mode,
    )
    return await _handle_search(payload)


@router.post("")
async def search_post(payload: SearchRequest) -> Dict[str, Any]:
    return await _handle_search(payload)
