"""
Discovery API - Rich paper discovery using AI analysis data

This module exposes powerful discovery features leveraging:
- deep_analysis: PDF-based enrichment with impact scores, methodology, etc.
- ai_analysis: Abstract-based enrichment with summaries, difficulty levels

Features:
- Impact Dashboard: High-impact paper discovery
- Learning Paths: Difficulty-based progressions
- Technique Explorer: Browse by novelty type and methodology
- TL;DR Feed: Executive summaries for quick scanning
- Reproducibility Index: Papers with code and high reproducibility
- Artifact Discovery: Datasets, models, and equations mentioned
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from app.db.database import database

router = APIRouter(prefix="/discovery")


# ============== Response Models ==============

class ImpactPaper(BaseModel):
    """Paper with impact assessment data"""
    id: str
    title: str
    published: str
    category: str
    impact_score: int
    citation_potential: Optional[str] = None
    industry_relevance: Optional[str] = None
    research_significance: Optional[str] = None
    executive_summary: Optional[str] = None
    novelty_type: Optional[str] = None


class LearningPaper(BaseModel):
    """Paper formatted for learning paths"""
    id: str
    title: str
    difficulty_level: str
    prerequisites: List[str] = []
    reading_time_minutes: int
    key_sections: List[str] = []
    summary: Optional[str] = None


class TechniquePaper(BaseModel):
    """Paper with methodology and novelty info"""
    id: str
    title: str
    novelty_type: Optional[str] = None
    novelty_description: Optional[str] = None
    methodology_approach: Optional[str] = None
    key_components: List[str] = []
    architecture: Optional[str] = None


class TLDRPaper(BaseModel):
    """Paper with executive summary for quick reading"""
    id: str
    title: str
    published: str
    category: str
    executive_summary: Optional[str] = None
    problem_statement: Optional[str] = None
    proposed_solution: Optional[str] = None
    key_contribution: Optional[str] = None
    reading_time_minutes: Optional[int] = None


class ReproduciblePaper(BaseModel):
    """Paper with reproducibility metrics"""
    id: str
    title: str
    reproducibility_score: Optional[int] = None
    code_availability: Optional[str] = None
    implementation_detail: Optional[str] = None
    github_urls: List[str] = []
    datasets_mentioned: List[str] = []
    has_code: bool = False


# ============== Impact Dashboard ==============

@router.get("/impact", response_model=dict)
async def get_impact_dashboard(
    min_score: int = Query(default=7, ge=1, le=10, description="Minimum impact score (1-10)"),
    max_score: Optional[int] = Query(default=None, ge=1, le=10),
    industry_relevance: Optional[str] = Query(default=None, description="high, medium, low"),
    citation_potential: Optional[str] = Query(default=None, description="high, medium, low"),
    category: Optional[str] = Query(default=None),
    days: Optional[int] = Query(default=None, description="Filter to last N days"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Get high-impact papers based on calibrated impact scoring.

    Impact scores are calibrated to a normal distribution:
    - 9-10: Transformative (top 2% - paradigm shifting)
    - 7-8: High impact (top 15% - significant field advancement)
    - 5-6: Moderate (most papers - solid incremental work)
    - 3-4: Low impact (below average contribution)
    - 1-2: Minimal (very limited novelty)

    This endpoint returns papers with deep analysis, sorted by impact.
    """
    conditions = ["p.deep_analysis IS NOT NULL"]
    params = {"limit": limit, "offset": offset}

    conditions.append("(p.deep_analysis->'impact_assessment'->>'impact_score')::int >= :min_score")
    params["min_score"] = min_score

    if max_score:
        conditions.append("(p.deep_analysis->'impact_assessment'->>'impact_score')::int <= :max_score")
        params["max_score"] = max_score

    if industry_relevance:
        conditions.append("p.deep_analysis->'impact_assessment'->>'industry_relevance' = :industry")
        params["industry"] = industry_relevance

    if citation_potential:
        conditions.append("p.deep_analysis->'impact_assessment'->>'citation_potential' = :cit_potential")
        params["cit_potential"] = citation_potential

    if category:
        conditions.append("p.category = :category")
        params["category"] = category

    if days:
        cutoff = datetime.now() - timedelta(days=days)
        conditions.append("p.published_date >= :cutoff")
        params["cutoff"] = cutoff

    where_clause = " AND ".join(conditions)

    # Count total (exclude limit/offset params)
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}
    count_query = f"SELECT COUNT(*) as total FROM papers p WHERE {where_clause}"
    count_result = await database.fetch_one(count_query, count_params)
    total = count_result["total"] if count_result else 0

    # Add pagination params
    params["limit"] = limit
    params["offset"] = offset

    # Fetch papers
    query = f"""
        SELECT
            p.id,
            p.title,
            p.published_date,
            p.category,
            p.deep_analysis->'impact_assessment' as impact,
            p.deep_analysis->>'executive_summary' as executive_summary,
            p.deep_analysis->'novelty_assessment'->>'novelty_type' as novelty_type
        FROM papers p
        WHERE {where_clause}
        ORDER BY (p.deep_analysis->'impact_assessment'->>'impact_score')::int DESC,
                 p.published_date DESC
        LIMIT :limit OFFSET :offset
    """

    rows = await database.fetch_all(query, params)

    papers = []
    for row in rows:
        impact = row["impact"] if isinstance(row["impact"], dict) else json.loads(row["impact"]) if row["impact"] else {}
        papers.append({
            "id": row["id"],
            "title": row["title"],
            "published": row["published_date"].isoformat() if row["published_date"] else None,
            "category": row["category"],
            "impact_score": impact.get("impact_score", 0),
            "citation_potential": impact.get("citation_potential"),
            "industry_relevance": impact.get("industry_relevance"),
            "research_significance": impact.get("research_significance"),
            "executive_summary": row["executive_summary"],
            "novelty_type": row["novelty_type"],
        })

    # Get distribution stats
    dist_query = """
        SELECT
            (p.deep_analysis->'impact_assessment'->>'impact_score')::int as score,
            COUNT(*) as count
        FROM papers p
        WHERE p.deep_analysis IS NOT NULL
        GROUP BY score
        ORDER BY score DESC
    """
    dist_rows = await database.fetch_all(dist_query)
    distribution = {row["score"]: row["count"] for row in dist_rows if row["score"]}

    return {
        "papers": papers,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(papers) < total,
        "score_distribution": distribution,
        "score_rubric": {
            "9-10": "Transformative (paradigm shifting)",
            "7-8": "High impact (significant field advancement)",
            "5-6": "Moderate (solid incremental work)",
            "3-4": "Low impact (below average contribution)",
            "1-2": "Minimal (very limited novelty)"
        }
    }


# ============== Learning Paths ==============

@router.get("/learning-path", response_model=dict)
async def get_learning_path(
    topic: Optional[str] = Query(default=None, description="Topic to search for in title/abstract"),
    category: Optional[str] = Query(default=None),
    start_level: str = Query(default="beginner", enum=["beginner", "intermediate", "advanced", "expert"]),
    limit_per_level: int = Query(default=5, ge=1, le=20),
):
    """
    Get papers organized as a learning progression.

    Returns papers sorted by difficulty level to create a learning path:
    - beginner: Foundational concepts, accessible introductions
    - intermediate: Building on fundamentals
    - advanced: Requires strong background
    - expert: Cutting-edge, assumes deep expertise

    Each paper includes prerequisites and estimated reading time.
    """
    difficulty_order = ["beginner", "intermediate", "advanced", "expert"]
    start_idx = difficulty_order.index(start_level)
    levels_to_fetch = difficulty_order[start_idx:]

    result = {"topic": topic, "category": category, "path": []}

    for level in levels_to_fetch:
        conditions = [
            "p.deep_analysis IS NOT NULL",
            "p.deep_analysis->'reader_guidance'->>'difficulty_level' = :level"
        ]
        params = {"level": level, "limit": limit_per_level}

        if topic:
            conditions.append("(p.title ILIKE :topic OR p.abstract ILIKE :topic)")
            params["topic"] = f"%{topic}%"

        if category:
            conditions.append("p.category = :category")
            params["category"] = category

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT
                p.id,
                p.title,
                p.deep_analysis->'reader_guidance' as guidance,
                p.ai_analysis->>'summary' as summary
            FROM papers p
            WHERE {where_clause}
            ORDER BY (p.deep_analysis->'impact_assessment'->>'impact_score')::int DESC
            LIMIT :limit
        """

        rows = await database.fetch_all(query, params)

        papers = []
        for row in rows:
            guidance = row["guidance"] if isinstance(row["guidance"], dict) else json.loads(row["guidance"]) if row["guidance"] else {}
            papers.append({
                "id": row["id"],
                "title": row["title"],
                "difficulty_level": level,
                "prerequisites": guidance.get("prerequisites", []),
                "reading_time_minutes": guidance.get("reading_time_minutes", 30),
                "key_sections": guidance.get("key_sections", []),
                "summary": row["summary"],
            })

        if papers:
            result["path"].append({
                "level": level,
                "description": {
                    "beginner": "Start here - foundational concepts",
                    "intermediate": "Build on fundamentals",
                    "advanced": "Requires strong background",
                    "expert": "Cutting-edge research"
                }.get(level, level),
                "papers": papers
            })

    return result


# ============== Technique Explorer ==============

@router.get("/techniques", response_model=dict)
async def get_techniques(
    novelty_type: Optional[str] = Query(default=None, description="Filter by type: architectural, algorithmic, application, theoretical"),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Explore papers by their technical novelty and methodology.

    Novelty types include:
    - architectural: New model architectures
    - algorithmic: Novel algorithms or optimization methods
    - application: New applications of existing methods
    - theoretical: Theoretical contributions and analysis
    - empirical: New benchmarks, datasets, or empirical studies

    Returns methodology details, key components, and architectural insights.
    """
    conditions = ["p.deep_analysis IS NOT NULL"]
    params = {"limit": limit, "offset": offset}

    if novelty_type:
        conditions.append("p.deep_analysis->'novelty_assessment'->>'novelty_type' ILIKE :novelty_type")
        params["novelty_type"] = f"%{novelty_type}%"

    if category:
        conditions.append("p.category = :category")
        params["category"] = category

    where_clause = " AND ".join(conditions)

    # Count total (exclude limit/offset params)
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}
    count_query = f"SELECT COUNT(*) as total FROM papers p WHERE {where_clause}"
    count_result = await database.fetch_one(count_query, count_params)
    total = count_result["total"] if count_result else 0

    query = f"""
        SELECT
            p.id,
            p.title,
            p.deep_analysis->'novelty_assessment' as novelty,
            p.deep_analysis->'methodology' as methodology
        FROM papers p
        WHERE {where_clause}
        ORDER BY (p.deep_analysis->'impact_assessment'->>'impact_score')::int DESC
        LIMIT :limit OFFSET :offset
    """

    rows = await database.fetch_all(query, params)

    papers = []
    for row in rows:
        novelty = row["novelty"] if isinstance(row["novelty"], dict) else json.loads(row["novelty"]) if row["novelty"] else {}
        methodology = row["methodology"] if isinstance(row["methodology"], dict) else json.loads(row["methodology"]) if row["methodology"] else {}

        papers.append({
            "id": row["id"],
            "title": row["title"],
            "novelty_type": novelty.get("novelty_type"),
            "novelty_description": novelty.get("novelty_description"),
            "methodology_approach": methodology.get("approach"),
            "key_components": methodology.get("key_components", []),
            "architecture": methodology.get("architecture"),
        })

    # Get novelty type distribution
    dist_query = """
        SELECT
            p.deep_analysis->'novelty_assessment'->>'novelty_type' as novelty_type,
            COUNT(*) as count
        FROM papers p
        WHERE p.deep_analysis IS NOT NULL
          AND p.deep_analysis->'novelty_assessment'->>'novelty_type' IS NOT NULL
        GROUP BY novelty_type
        ORDER BY count DESC
    """
    dist_rows = await database.fetch_all(dist_query)
    distribution = {row["novelty_type"]: row["count"] for row in dist_rows}

    return {
        "papers": papers,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(papers) < total,
        "novelty_type_distribution": distribution
    }


# ============== TL;DR Feed ==============

@router.get("/tldr", response_model=dict)
async def get_tldr_feed(
    category: Optional[str] = Query(default=None),
    days: Optional[int] = Query(default=7, description="Papers from last N days"),
    min_impact: Optional[int] = Query(default=None, ge=1, le=10),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    """
    Get executive summaries for quick paper scanning.

    Returns condensed information:
    - Executive summary (1-2 sentences)
    - Problem statement
    - Proposed solution
    - Key contribution
    - Estimated reading time

    Perfect for staying up-to-date with recent research.
    """
    conditions = ["p.deep_analysis IS NOT NULL"]
    params = {"limit": limit, "offset": offset}

    if category:
        conditions.append("p.category = :category")
        params["category"] = category

    if days:
        cutoff = datetime.now() - timedelta(days=days)
        conditions.append("p.published_date >= :cutoff")
        params["cutoff"] = cutoff

    if min_impact:
        conditions.append("(p.deep_analysis->'impact_assessment'->>'impact_score')::int >= :min_impact")
        params["min_impact"] = min_impact

    where_clause = " AND ".join(conditions)

    # Count total (exclude limit/offset params)
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}
    count_query = f"SELECT COUNT(*) as total FROM papers p WHERE {where_clause}"
    count_result = await database.fetch_one(count_query, count_params)
    total = count_result["total"] if count_result else 0

    query = f"""
        SELECT
            p.id,
            p.title,
            p.published_date,
            p.category,
            p.deep_analysis->>'executive_summary' as executive_summary,
            p.deep_analysis->>'problem_statement' as problem_statement,
            p.deep_analysis->>'proposed_solution' as proposed_solution,
            p.deep_analysis->'reader_guidance'->>'reading_time_minutes' as reading_time,
            p.ai_analysis->>'keyContribution' as key_contribution
        FROM papers p
        WHERE {where_clause}
        ORDER BY p.published_date DESC
        LIMIT :limit OFFSET :offset
    """

    rows = await database.fetch_all(query, params)

    papers = []
    for row in rows:
        reading_time = None
        if row["reading_time"]:
            try:
                reading_time = int(row["reading_time"])
            except (ValueError, TypeError):
                reading_time = None

        papers.append({
            "id": row["id"],
            "title": row["title"],
            "published": row["published_date"].isoformat() if row["published_date"] else None,
            "category": row["category"],
            "executive_summary": row["executive_summary"],
            "problem_statement": row["problem_statement"],
            "proposed_solution": row["proposed_solution"],
            "key_contribution": row["key_contribution"],
            "reading_time_minutes": reading_time,
        })

    return {
        "papers": papers,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(papers) < total,
        "time_range_days": days
    }


# ============== Reproducibility Index ==============

@router.get("/reproducible", response_model=dict)
async def get_reproducible_papers(
    min_reproducibility: int = Query(default=7, ge=1, le=10, description="Minimum reproducibility score"),
    has_code: Optional[bool] = Query(default=None, description="Filter to papers with code"),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Find papers with high reproducibility scores and available code.

    Reproducibility factors:
    - Reproducibility score (1-10): How easy to reproduce results
    - Code availability: Whether code is mentioned/available
    - Implementation detail: Level of implementation specifics
    - GitHub URLs: Direct links to code repositories
    - Datasets mentioned: Referenced datasets
    """
    conditions = ["p.deep_analysis IS NOT NULL"]
    params = {"limit": limit, "offset": offset}

    conditions.append("(p.deep_analysis->'technical_depth'->>'reproducibility_score')::int >= :min_repro")
    params["min_repro"] = min_reproducibility

    if has_code is True:
        conditions.append("""(
            p.ai_analysis->>'hasCode' = 'true'
            OR p.deep_analysis->'technical_depth'->>'code_availability' NOT IN ('unknown', 'none', 'unavailable')
            OR jsonb_array_length(p.deep_analysis->'extracted_artifacts'->'github_urls') > 0
        )""")
    elif has_code is False:
        conditions.append("p.ai_analysis->>'hasCode' = 'false'")

    if category:
        conditions.append("p.category = :category")
        params["category"] = category

    where_clause = " AND ".join(conditions)

    # Count total (exclude limit/offset params)
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}
    count_query = f"SELECT COUNT(*) as total FROM papers p WHERE {where_clause}"
    count_result = await database.fetch_one(count_query, count_params)
    total = count_result["total"] if count_result else 0

    query = f"""
        SELECT
            p.id,
            p.title,
            p.deep_analysis->'technical_depth' as tech_depth,
            p.deep_analysis->'extracted_artifacts' as artifacts,
            p.ai_analysis->>'hasCode' as has_code_flag
        FROM papers p
        WHERE {where_clause}
        ORDER BY (p.deep_analysis->'technical_depth'->>'reproducibility_score')::int DESC
        LIMIT :limit OFFSET :offset
    """

    rows = await database.fetch_all(query, params)

    papers = []
    for row in rows:
        tech_depth = row["tech_depth"] if isinstance(row["tech_depth"], dict) else json.loads(row["tech_depth"]) if row["tech_depth"] else {}
        artifacts = row["artifacts"] if isinstance(row["artifacts"], dict) else json.loads(row["artifacts"]) if row["artifacts"] else {}

        repro_score = tech_depth.get("reproducibility_score")
        if isinstance(repro_score, str):
            try:
                repro_score = int(repro_score)
            except ValueError:
                repro_score = None

        papers.append({
            "id": row["id"],
            "title": row["title"],
            "reproducibility_score": repro_score,
            "code_availability": tech_depth.get("code_availability"),
            "implementation_detail": tech_depth.get("implementation_detail"),
            "github_urls": artifacts.get("github_urls", []),
            "datasets_mentioned": artifacts.get("datasets_mentioned", []),
            "has_code": row["has_code_flag"] == "true",
        })

    return {
        "papers": papers,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(papers) < total
    }


# ============== Artifact Discovery ==============

@router.get("/artifacts", response_model=dict)
async def get_artifacts(
    artifact_type: str = Query(..., enum=["github", "datasets", "models", "equations"]),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Discover papers by extracted artifacts.

    Artifact types:
    - github: Papers with GitHub repository links
    - datasets: Papers mentioning specific datasets
    - models: Papers mentioning specific model architectures
    - equations: Papers with key equations documented
    """
    artifact_map = {
        "github": "github_urls",
        "datasets": "datasets_mentioned",
        "models": "models_mentioned",
        "equations": "key_equations"
    }

    artifact_field = artifact_map[artifact_type]

    query = f"""
        SELECT
            p.id,
            p.title,
            p.category,
            p.deep_analysis->'extracted_artifacts'->'{artifact_field}' as artifacts,
            (p.deep_analysis->'impact_assessment'->>'impact_score')::int as impact_score
        FROM papers p
        WHERE p.deep_analysis IS NOT NULL
          AND jsonb_array_length(p.deep_analysis->'extracted_artifacts'->'{artifact_field}') > 0
        ORDER BY impact_score DESC NULLS LAST
        LIMIT :limit
    """

    rows = await database.fetch_all(query, {"limit": limit})

    papers = []
    all_artifacts = set()

    for row in rows:
        artifacts_list = row["artifacts"] if isinstance(row["artifacts"], list) else json.loads(row["artifacts"]) if row["artifacts"] else []
        all_artifacts.update(artifacts_list)

        papers.append({
            "id": row["id"],
            "title": row["title"],
            "category": row["category"],
            "impact_score": row["impact_score"],
            "artifacts": artifacts_list
        })

    return {
        "artifact_type": artifact_type,
        "papers": papers,
        "total_papers": len(papers),
        "unique_artifacts": sorted(list(all_artifacts))[:50]  # Top 50 unique artifacts
    }


# ============== Practical Applications ==============

@router.get("/practical", response_model=dict)
async def get_practical_papers(
    industry_relevance: str = Query(default="high", enum=["high", "medium", "low"]),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Find papers with practical industry applications.

    Returns papers with:
    - Use cases for industry deployment
    - Scalability considerations
    - Deployment recommendations
    - Limitations for practical use
    """
    conditions = [
        "p.deep_analysis IS NOT NULL",
        "p.deep_analysis->'impact_assessment'->>'industry_relevance' = :industry"
    ]
    params = {"limit": limit, "offset": offset, "industry": industry_relevance}

    if category:
        conditions.append("p.category = :category")
        params["category"] = category

    where_clause = " AND ".join(conditions)

    # Count total (exclude limit/offset params)
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}
    count_query = f"SELECT COUNT(*) as total FROM papers p WHERE {where_clause}"
    count_result = await database.fetch_one(count_query, count_params)
    total = count_result["total"] if count_result else 0

    query = f"""
        SELECT
            p.id,
            p.title,
            p.category,
            p.deep_analysis->'practical_implications' as practical,
            p.deep_analysis->'impact_assessment' as impact,
            p.ai_analysis->>'practicalApplicability' as ai_practical
        FROM papers p
        WHERE {where_clause}
        ORDER BY (p.deep_analysis->'impact_assessment'->>'impact_score')::int DESC
        LIMIT :limit OFFSET :offset
    """

    rows = await database.fetch_all(query, params)

    papers = []
    for row in rows:
        practical = row["practical"] if isinstance(row["practical"], dict) else json.loads(row["practical"]) if row["practical"] else {}
        impact = row["impact"] if isinstance(row["impact"], dict) else json.loads(row["impact"]) if row["impact"] else {}

        papers.append({
            "id": row["id"],
            "title": row["title"],
            "category": row["category"],
            "industry_relevance": impact.get("industry_relevance"),
            "impact_score": impact.get("impact_score"),
            "use_cases": practical.get("use_cases", []),
            "scalability": practical.get("scalability"),
            "deployment_considerations": practical.get("deployment_considerations"),
            "limitations": practical.get("limitations", []),
            "ai_practical_score": row["ai_practical"]
        })

    return {
        "papers": papers,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(papers) < total,
        "industry_relevance_filter": industry_relevance
    }


# ============== Analysis Statistics ==============

@router.get("/stats", response_model=dict)
async def get_discovery_stats():
    """
    Get statistics about analysis coverage and distributions.
    """
    stats_query = """
        SELECT
            COUNT(*) as total_papers,
            COUNT(ai_analysis) as ai_analyzed,
            COUNT(deep_analysis) as deep_analyzed,
            COUNT(CASE WHEN ai_analysis->>'hasCode' = 'true' THEN 1 END) as with_code
        FROM papers
    """

    counts = await database.fetch_one(stats_query)

    # Impact score distribution
    impact_dist_query = """
        SELECT
            (p.deep_analysis->'impact_assessment'->>'impact_score')::int as score,
            COUNT(*) as count
        FROM papers p
        WHERE p.deep_analysis IS NOT NULL
        GROUP BY score
        ORDER BY score
    """
    impact_dist = await database.fetch_all(impact_dist_query)

    # Difficulty level distribution
    difficulty_dist_query = """
        SELECT
            p.deep_analysis->'reader_guidance'->>'difficulty_level' as level,
            COUNT(*) as count
        FROM papers p
        WHERE p.deep_analysis IS NOT NULL
          AND p.deep_analysis->'reader_guidance'->>'difficulty_level' IS NOT NULL
        GROUP BY level
        ORDER BY count DESC
    """
    difficulty_dist = await database.fetch_all(difficulty_dist_query)

    # Novelty type distribution
    novelty_dist_query = """
        SELECT
            p.deep_analysis->'novelty_assessment'->>'novelty_type' as type,
            COUNT(*) as count
        FROM papers p
        WHERE p.deep_analysis IS NOT NULL
          AND p.deep_analysis->'novelty_assessment'->>'novelty_type' IS NOT NULL
        GROUP BY type
        ORDER BY count DESC
    """
    novelty_dist = await database.fetch_all(novelty_dist_query)

    # Industry relevance distribution
    industry_dist_query = """
        SELECT
            p.deep_analysis->'impact_assessment'->>'industry_relevance' as relevance,
            COUNT(*) as count
        FROM papers p
        WHERE p.deep_analysis IS NOT NULL
          AND p.deep_analysis->'impact_assessment'->>'industry_relevance' IS NOT NULL
        GROUP BY relevance
        ORDER BY count DESC
    """
    industry_dist = await database.fetch_all(industry_dist_query)

    return {
        "coverage": {
            "total_papers": counts["total_papers"],
            "ai_analyzed": counts["ai_analyzed"],
            "ai_coverage_pct": round(100 * counts["ai_analyzed"] / counts["total_papers"], 1) if counts["total_papers"] > 0 else 0,
            "deep_analyzed": counts["deep_analyzed"],
            "deep_coverage_pct": round(100 * counts["deep_analyzed"] / counts["total_papers"], 1) if counts["total_papers"] > 0 else 0,
            "with_code": counts["with_code"],
        },
        "distributions": {
            "impact_scores": {row["score"]: row["count"] for row in impact_dist if row["score"]},
            "difficulty_levels": {row["level"]: row["count"] for row in difficulty_dist},
            "novelty_types": {row["type"]: row["count"] for row in novelty_dist},
            "industry_relevance": {row["relevance"]: row["count"] for row in industry_dist},
        }
    }
