"""
Database-backed Atlas API endpoints

These endpoints query the Supabase PostgreSQL database directly,
providing faster and more flexible access than the JSON file-based endpoints.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.database import database

router = APIRouter(prefix="/atlas-db")


def detect_paper_type(title: str) -> str:
    """
    Detect paper type based on title keywords.
    Returns: 'survey', 'tutorial', 'review', 'primer', or 'research'
    """
    title_lower = title.lower()

    # Order matters: check most specific first
    if 'tutorial' in title_lower:
        return 'tutorial'
    elif 'survey' in title_lower:
        return 'survey'
    elif 'review' in title_lower:
        return 'review'
    elif any(keyword in title_lower for keyword in ['primer', 'introduction to', 'guide to']):
        return 'primer'
    else:
        return 'research'


# Domain-specific keyword mappings for cross-domain search
# Helps interdisciplinary researchers find relevant papers
DOMAIN_KEYWORDS = {
    "climate": ["weather", "environmental", "earth", "atmosphere", "ocean", "carbon", "emission"],
    "medical": ["clinical", "health", "patient", "diagnosis", "treatment", "disease", "healthcare"],
    "biology": ["protein", "gene", "cell", "molecular", "organism", "evolution", "biomedical"],
    "finance": ["trading", "stock", "market", "economic", "financial", "investment", "risk"],
    "robotics": ["robot", "manipulation", "control", "autonomous", "navigation", "gripper"],
    "chemistry": ["molecule", "compound", "reaction", "synthesis", "material", "catalyst"],
}


def detect_application_domain(query: str) -> list:
    """
    Detect application domains mentioned in query.
    Returns list of domain-specific keywords to boost.
    """
    query_lower = query.lower()
    related_keywords = []

    for domain, keywords in DOMAIN_KEYWORDS.items():
        if domain in query_lower or any(kw in query_lower for kw in keywords[:2]):
            # Found domain mention - add all related keywords
            related_keywords.extend(keywords)

    return list(set(related_keywords))  # Remove duplicates


class PaperResponse(BaseModel):
    """Paper response model"""
    id: str
    title: str
    abstract: str
    authors: List[str]
    published: str
    category: str
    link: str
    citation_count: int = 0
    concepts: List[str] = []


class ConceptResponse(BaseModel):
    """Concept with paper count"""
    name: str
    category: Optional[str]
    paper_count: int


class AtlasSummaryResponse(BaseModel):
    """Summary statistics for the atlas"""
    total_papers: int
    total_concepts: int
    total_links: int
    categories: List[dict]
    top_concepts: List[dict]
    date_range: dict


@router.get("/papers", response_model=dict)
async def get_papers(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: Optional[str] = Query(default=None),
    concept: Optional[str] = Query(default=None),
    query: Optional[str] = Query(default=None),
    days: Optional[int] = Query(default=None, description="Filter to papers from last N days"),
    order_by: Optional[str] = Query(default=None, enum=["published_date", "citation_count", "title"]),
    order_dir: str = Query(default="desc", enum=["asc", "desc"]),
    # Deep analysis filters
    min_impact_score: Optional[int] = Query(default=None, ge=1, le=10, description="Minimum deep analysis impact score (1-10)"),
    max_impact_score: Optional[int] = Query(default=None, ge=1, le=10, description="Maximum deep analysis impact score (1-10)"),
    difficulty_level: Optional[str] = Query(default=None, enum=["beginner", "intermediate", "advanced", "expert"], description="Filter by difficulty level"),
    has_deep_analysis: Optional[bool] = Query(default=None, description="Filter papers with/without deep analysis"),
    min_reproducibility: Optional[int] = Query(default=None, ge=1, le=10, description="Minimum reproducibility score (1-10)"),
    novelty_type: Optional[str] = Query(default=None, description="Filter by novelty type (architectural, algorithmic, etc.)"),
    has_code: Optional[bool] = Query(default=None, description="Filter papers with/without associated code repositories"),
    seminal_only: Optional[bool] = Query(default=None, description="Filter for highly cited seminal papers (top 1% by citations)"),
):
    """
    Get papers from the database with filtering and pagination.

    Basic filters:
    - **limit**: Maximum number of papers to return (1-100)
    - **offset**: Number of papers to skip
    - **category**: Filter by arXiv category (e.g., cs.AI, cs.LG)
    - **concept**: Filter by concept name
    - **query**: Full-text search in title and abstract
    - **days**: Filter to papers from the last N days
    - **order_by**: Sort field (published_date, citation_count, title)
    - **order_dir**: Sort direction (asc, desc)

    Deep analysis filters (PDF-based enrichment):
    - **min_impact_score**: Minimum calibrated impact score (1-10)
    - **max_impact_score**: Maximum calibrated impact score (1-10)
    - **difficulty_level**: Filter by reading difficulty (beginner/intermediate/advanced/expert)
    - **has_deep_analysis**: Filter papers with/without deep PDF analysis
    - **min_reproducibility**: Minimum reproducibility score (1-10)
    - **novelty_type**: Filter by novelty type (architectural, algorithmic, application, etc.)
    - **has_code**: Filter papers with/without associated code repositories
    """
    # Build query dynamically
    conditions = []
    params = {}

    if category and category != "all":
        conditions.append("p.category = :category")
        params["category"] = category

    if days:
        cutoff = datetime.now() - timedelta(days=days)
        conditions.append("p.published_date >= :cutoff")
        params["cutoff"] = cutoff

    # Track if we're using full-text search for relevance ranking
    using_fts = False

    if query:
        # Tokenize to avoid empty/stop-word-only queries.
        words = [w.strip().lower() for w in query.split() if len(w.strip()) >= 3]

        if len(words) > 0:
            # Detect application domain and expand query with related keywords
            # Helps cross-domain researchers find relevant papers (e.g., climate science + ML)
            domain_keywords = detect_application_domain(query)
            expanded_query = query
            if domain_keywords:
                # Add top 3 most relevant domain keywords to boost recall
                # Use OR logic so papers matching either original query OR domain keywords surface
                top_domain_keywords = domain_keywords[:3]
                expanded_query = query + " " + " ".join(top_domain_keywords)

            # Use FTS with a COALESCE fallback so missing search_vector doesn't drop all results.
            tsvector_expr = (
                "COALESCE(p.search_vector, "
                "to_tsvector('english', COALESCE(p.title, '') || ' ' || COALESCE(p.abstract, '')))"
            )
            conditions.append(f"{tsvector_expr} @@ plainto_tsquery('english', :fts_query)")
            params["fts_query"] = expanded_query
            using_fts = True

    if concept:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM paper_concepts pc
                JOIN concepts c ON pc.concept_id = c.id
                WHERE pc.paper_id = p.id AND c.name ILIKE :concept
            )
        """)
        params["concept"] = f"%{concept}%"

    # Deep analysis filters
    if has_deep_analysis is not None:
        if has_deep_analysis:
            conditions.append("p.deep_analysis IS NOT NULL")
        else:
            conditions.append("p.deep_analysis IS NULL")

    if min_impact_score is not None:
        conditions.append("(p.deep_analysis->'impact_assessment'->>'impact_score')::int >= :min_impact")
        params["min_impact"] = min_impact_score

    if max_impact_score is not None:
        conditions.append("(p.deep_analysis->'impact_assessment'->>'impact_score')::int <= :max_impact")
        params["max_impact"] = max_impact_score

    if difficulty_level:
        conditions.append("p.deep_analysis->'reader_guidance'->>'difficulty_level' = :difficulty")
        params["difficulty"] = difficulty_level

    if min_reproducibility is not None:
        conditions.append("(p.deep_analysis->'technical_depth'->>'reproducibility_score')::int >= :min_repro")
        params["min_repro"] = min_reproducibility

    if novelty_type:
        conditions.append("p.deep_analysis->'novelty_assessment'->>'novelty_type' = :novelty_type")
        params["novelty_type"] = novelty_type

    # Code availability filter - checks code_repos JSONB array
    if has_code is not None:
        if has_code:
            conditions.append("(p.code_repos IS NOT NULL AND jsonb_array_length(p.code_repos) > 0)")
        else:
            conditions.append("(p.code_repos IS NULL OR jsonb_array_length(p.code_repos) = 0)")

    # Seminal papers filter - top 1% by citations
    if seminal_only:
        # Calculate 99th percentile citation threshold
        percentile_query = """
            SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY citation_count)
            FROM papers
            WHERE citation_count > 0
        """
        percentile_result = await database.fetch_one(percentile_query)
        if percentile_result:
            citation_threshold = percentile_result[0] or 100  # Fallback to 100
            conditions.append("p.citation_count >= :citation_threshold")
            params["citation_threshold"] = citation_threshold

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Validate and set order - use relevance ranking for full-text search
    if using_fts and not order_by:
        # When using FTS without explicit ordering, rank by relevance (ts_rank)
        # Secondary sort by recency to break ties
        order_clause = (
            "ts_rank("
            "COALESCE(p.search_vector, "
            "to_tsvector('english', COALESCE(p.title, '') || ' ' || COALESCE(p.abstract, ''))), "
            "plainto_tsquery('english', :fts_query)"
            ") DESC, p.published_date DESC"
        )
    else:
        # Use explicit ordering or default to recency
        valid_order_fields = {"published_date": "p.published_date", "citation_count": "p.citation_count", "title": "p.title"}
        order_field = valid_order_fields.get(order_by or "published_date", "p.published_date")
        order_direction = "DESC" if order_dir == "desc" else "ASC"
        order_clause = f"{order_field} {order_direction}"

    # Count total matching papers
    count_query = f"SELECT COUNT(*) as total FROM papers p WHERE {where_clause}"
    count_result = await database.fetch_one(count_query, params)
    total = count_result["total"] if count_result else 0

    # Fetch papers with concepts
    papers_query = f"""
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.authors,
            p.published_date,
            p.category,
            p.citation_count,
            p.code_repos,
            p.external_signals,
            p.deep_analysis,
            COALESCE(
                (SELECT array_agg(c.name)
                 FROM paper_concepts pc
                 JOIN concepts c ON pc.concept_id = c.id
                 WHERE pc.paper_id = p.id),
                ARRAY[]::text[]
            ) as concepts
        FROM papers p
        WHERE {where_clause}
        ORDER BY {order_clause}
        LIMIT :limit OFFSET :offset
    """

    params["limit"] = limit
    params["offset"] = offset

    rows = await database.fetch_all(papers_query, params)

    papers = []
    for row in rows:
        # Parse authors JSON
        authors = row["authors"]
        if isinstance(authors, str):
            import json
            authors = json.loads(authors)

        # Format link
        plain_id = row["id"].split("v")[0]
        link = f"https://arxiv.org/abs/{plain_id}"

        # Detect paper type from title
        paper_type = detect_paper_type(row["title"])

        papers.append({
            "id": row["id"],
            "title": row["title"],
            "abstract": row["abstract"],
            "authors": authors,
            "published": row["published_date"].isoformat() if row["published_date"] else None,
            "category": row["category"],
            "link": link,
            "citation_count": row["citation_count"] or 0,
            "concepts": row["concepts"] or [],
            "code_repos": row["code_repos"],
            "external_signals": row["external_signals"],
            "deep_analysis": row["deep_analysis"],
            "paper_type": paper_type
        })

    return {
        "papers": papers,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(papers) < total
    }


@router.get("/papers/{paper_id}")
async def get_paper(paper_id: str):
    """Get a single paper by ID with full details"""
    query = """
        SELECT
            p.*,
            COALESCE(
                (SELECT json_agg(json_build_object('name', c.name, 'category', c.category, 'relevance', pc.relevance))
                 FROM paper_concepts pc
                 JOIN concepts c ON pc.concept_id = c.id
                 WHERE pc.paper_id = p.id),
                '[]'::json
            ) as concepts
        FROM papers p
        WHERE p.id = :paper_id
    """

    row = await database.fetch_one(query, {"paper_id": paper_id})

    if not row:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

    # Parse authors JSON
    authors = row["authors"]
    if isinstance(authors, str):
        import json
        authors = json.loads(authors)

    plain_id = row["id"].split("v")[0]

    # Detect paper type from title
    paper_type = detect_paper_type(row["title"])

    return {
        "id": row["id"],
        "title": row["title"],
        "abstract": row["abstract"],
        "authors": authors,
        "published": row["published_date"].isoformat() if row["published_date"] else None,
        "category": row["category"],
        "link": f"https://arxiv.org/abs/{plain_id}",
        "citation_count": row["citation_count"] or 0,
        "quality_score": row["quality_score"] or 0,
        "concepts": row["concepts"] or [],
        "ai_analysis": row["ai_analysis"],
        "deep_analysis": row["deep_analysis"],
        "code_repos": row["code_repos"],
        "paper_type": paper_type
    }


@router.get("/concepts", response_model=List[ConceptResponse])
async def get_concepts(
    limit: int = Query(default=50, ge=1, le=200),
    category: Optional[str] = Query(default=None),
    min_papers: int = Query(default=1, ge=0)
):
    """Get concepts with paper counts"""
    conditions = ["paper_count >= :min_papers"]
    params = {"min_papers": min_papers, "limit": limit}

    if category:
        conditions.append("category = :category")
        params["category"] = category

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT name, category, paper_count
        FROM concepts
        WHERE {where_clause}
        ORDER BY paper_count DESC
        LIMIT :limit
    """

    rows = await database.fetch_all(query, params)

    return [
        {"name": row["name"], "category": row["category"], "paper_count": row["paper_count"]}
        for row in rows
    ]


@router.get("/summary", response_model=AtlasSummaryResponse)
async def get_summary():
    """Get atlas summary statistics"""
    # Get counts
    paper_count = await database.fetch_one("SELECT COUNT(*) as count FROM papers")
    concept_count = await database.fetch_one("SELECT COUNT(*) as count FROM concepts")
    link_count = await database.fetch_one("SELECT COUNT(*) as count FROM paper_concepts")

    # Get top categories
    categories = await database.fetch_all("""
        SELECT category, COUNT(*) as count
        FROM papers
        GROUP BY category
        ORDER BY count DESC
        LIMIT 15
    """)

    # Get top concepts
    top_concepts = await database.fetch_all("""
        SELECT name, category, paper_count
        FROM concepts
        ORDER BY paper_count DESC
        LIMIT 10
    """)

    # Get date range
    date_range = await database.fetch_one("""
        SELECT
            MIN(published_date) as min_date,
            MAX(published_date) as max_date
        FROM papers
    """)

    return {
        "total_papers": paper_count["count"],
        "total_concepts": concept_count["count"],
        "total_links": link_count["count"],
        "categories": [{"category": r["category"], "count": r["count"]} for r in categories],
        "top_concepts": [{"name": r["name"], "category": r["category"], "count": r["paper_count"]} for r in top_concepts],
        "date_range": {
            "min": date_range["min_date"].isoformat() if date_range["min_date"] else None,
            "max": date_range["max_date"].isoformat() if date_range["max_date"] else None
        }
    }


@router.get("/related/{paper_id}")
async def get_related_papers(
    paper_id: str,
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get papers related to a given paper based on shared concepts"""
    # First check if paper exists
    paper = await database.fetch_one("SELECT id, title FROM papers WHERE id = :paper_id", {"paper_id": paper_id})
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

    # Use the get_related_papers function if it exists, otherwise fallback to SQL
    try:
        related = await database.fetch_all("""
            SELECT * FROM get_related_papers(:paper_id, :limit)
        """, {"paper_id": paper_id, "limit": limit})
    except Exception:
        # Fallback: find papers sharing concepts
        related = await database.fetch_all("""
            WITH source_concepts AS (
                SELECT concept_id, relevance
                FROM paper_concepts
                WHERE paper_id = :paper_id
            )
            SELECT
                p.id,
                p.title,
                p.category,
                COUNT(pc.concept_id)::int as shared_concepts,
                SUM(sc.relevance * pc.relevance)::float as relevance_score
            FROM papers p
            JOIN paper_concepts pc ON p.id = pc.paper_id
            JOIN source_concepts sc ON pc.concept_id = sc.concept_id
            WHERE p.id != :paper_id
            GROUP BY p.id, p.title, p.category
            ORDER BY relevance_score DESC
            LIMIT :limit
        """, {"paper_id": paper_id, "limit": limit})

    return {
        "source_paper": {"id": paper["id"], "title": paper["title"]},
        "related_papers": [
            {
                "id": r["id"],
                "title": r["title"],
                "category": r["category"],
                "shared_concepts": r["shared_concepts"],
                "relevance_score": round(r["relevance_score"], 3)
            }
            for r in related
        ]
    }


@router.get("/search")
async def search_papers(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Search papers using full-text search.
    Searches in title and abstract with ranking.
    """
    # Try to use PostgreSQL full-text search if search_vector is populated
    try:
        results = await database.fetch_all("""
            SELECT
                p.id,
                p.title,
                p.abstract,
                p.category,
                p.published_date,
                ts_rank(p.search_vector, plainto_tsquery('english', :query)) as rank
            FROM papers p
            WHERE p.search_vector @@ plainto_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :limit
        """, {"query": q, "limit": limit})
    except Exception:
        # Fallback to ILIKE search
        results = await database.fetch_all("""
            SELECT
                p.id,
                p.title,
                p.abstract,
                p.category,
                p.published_date,
                1.0 as rank
            FROM papers p
            WHERE p.title ILIKE :query OR p.abstract ILIKE :query
            ORDER BY p.published_date DESC
            LIMIT :limit
        """, {"query": f"%{q}%", "limit": limit})

    return {
        "query": q,
        "results": [
            {
                "id": r["id"],
                "title": r["title"],
                "abstract": r["abstract"][:300] + "..." if len(r["abstract"]) > 300 else r["abstract"],
                "category": r["category"],
                "published": r["published_date"].isoformat() if r["published_date"] else None,
                "relevance": round(float(r["rank"]), 3)
            }
            for r in results
        ],
        "total": len(results)
    }


@router.get("/categories")
async def get_categories():
    """
    Get all categories with paper counts.
    """
    results = await database.fetch_all("""
        SELECT
            category,
            COUNT(*) as paper_count
        FROM papers
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY paper_count DESC
    """)

    return [
        {
            "category": r["category"],
            "paper_count": r["paper_count"]
        }
        for r in results
    ]


@router.get("/techniques")
async def get_techniques(
    limit: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = Query(default=None)
):
    """
    Get techniques extracted from deep analysis with paper counts.

    - **limit**: Maximum number of techniques to return
    - **category**: Optional category filter
    """
    category_filter = ""
    params = {"limit": limit}

    if category:
        category_filter = "AND p.category = :category"
        params["category"] = category

    results = await database.fetch_all(f"""
        SELECT
            t.technique_name as name,
            t.technique_type as type,
            COUNT(DISTINCT t.paper_id) as paper_count
        FROM (
            SELECT
                p.id as paper_id,
                jsonb_array_elements_text(
                    COALESCE(p.deep_analysis->'technical_innovations'->'key_techniques', '[]'::jsonb)
                ) as technique_name,
                p.deep_analysis->'technical_innovations'->>'novelty_type' as technique_type
            FROM papers p
            WHERE p.deep_analysis IS NOT NULL
            {category_filter}
        ) t
        GROUP BY t.technique_name, t.technique_type
        ORDER BY paper_count DESC
        LIMIT :limit
    """, params)

    return [
        {
            "name": r["name"],
            "type": r["type"],
            "paper_count": r["paper_count"]
        }
        for r in results
    ]


@router.get("/timeline")
async def get_timeline(
    days: int = Query(default=30, ge=1, le=365),
    granularity: str = Query(default="day", enum=["day", "week", "month"]),
    category: Optional[str] = Query(default=None)
):
    """
    Get paper counts over time for visualization.

    - **days**: Number of days to look back (1-365)
    - **granularity**: Time granularity (day, week, month)
    - **category**: Optional category filter
    """
    category_filter = ""
    params = {}

    if category:
        category_filter = "AND category = :category"
        params["category"] = category

    if granularity == "day":
        date_trunc = "day"
    elif granularity == "week":
        date_trunc = "week"
    else:
        date_trunc = "month"

    results = await database.fetch_all(f"""
        SELECT
            DATE_TRUNC('{date_trunc}', published_date) as period,
            COUNT(*) as paper_count
        FROM papers
        WHERE published_date >= CURRENT_DATE - INTERVAL '{days} days'
        {category_filter}
        GROUP BY DATE_TRUNC('{date_trunc}', published_date)
        ORDER BY period DESC
    """, params)

    return [
        {
            "period": r["period"].isoformat() if r["period"] else None,
            "paper_count": r["paper_count"]
        }
        for r in results
    ]
