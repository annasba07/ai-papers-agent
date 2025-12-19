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
            p.deep_analysis->'novelty_assessment'->>'novelty_type' as novelty_type,
            p.external_signals->'github' as github_data,
            p.citation_count,
            p.influential_citation_count
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
        github_data = row["github_data"] if isinstance(row["github_data"], dict) else json.loads(row["github_data"]) if row["github_data"] else None

        paper_dict = {
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
            "citation_count": row["citation_count"] or 0,
            "influential_citation_count": row["influential_citation_count"] or 0,
        }

        # Add GitHub stats if available
        if github_data and github_data.get("repos"):
            repos = github_data["repos"]
            top_repo = repos[0] if repos else None
            paper_dict["github_stats"] = {
                "total_stars": github_data.get("total_stars", 0),
                "repo_count": len(repos),
                "top_repo": {
                    "url": top_repo.get("url"),
                    "stars": top_repo.get("stars", 0),
                    "forks": top_repo.get("forks", 0),
                    "language": top_repo.get("language"),
                    "pushed_at": top_repo.get("pushed_at"),
                } if top_repo else None
            }

        papers.append(paper_dict)

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
            p.deep_analysis->'methodology' as methodology,
            p.external_signals->'github' as github_data
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
        github_data = row["github_data"] if isinstance(row["github_data"], dict) else json.loads(row["github_data"]) if row["github_data"] else None

        paper_dict = {
            "id": row["id"],
            "title": row["title"],
            "novelty_type": novelty.get("novelty_type"),
            "novelty_description": novelty.get("novelty_description"),
            "methodology_approach": methodology.get("approach"),
            "key_components": methodology.get("key_components", []),
            "architecture": methodology.get("architecture"),
        }

        # Add GitHub stats if available
        if github_data and github_data.get("repos"):
            repos = github_data["repos"]
            top_repo = repos[0] if repos else None
            paper_dict["github_stats"] = {
                "total_stars": github_data.get("total_stars", 0),
                "repo_count": len(repos),
                "top_repo": {
                    "url": top_repo.get("url"),
                    "stars": top_repo.get("stars", 0),
                    "forks": top_repo.get("forks", 0),
                    "language": top_repo.get("language"),
                    "pushed_at": top_repo.get("pushed_at"),
                } if top_repo else None
            }

        papers.append(paper_dict)

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
    days: Optional[int] = Query(default=90, description="Papers from last N days (default 90 for deep analysis availability)"),
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
            p.ai_analysis->>'keyContribution' as key_contribution,
            p.external_signals->'github' as github_data
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

        github_data = row["github_data"] if isinstance(row["github_data"], dict) else json.loads(row["github_data"]) if row["github_data"] else None

        paper_dict = {
            "id": row["id"],
            "title": row["title"],
            "published": row["published_date"].isoformat() if row["published_date"] else None,
            "category": row["category"],
            "executive_summary": row["executive_summary"],
            "problem_statement": row["problem_statement"],
            "proposed_solution": row["proposed_solution"],
            "key_contribution": row["key_contribution"],
            "reading_time_minutes": reading_time,
        }

        # Add GitHub stats if available
        if github_data and github_data.get("repos"):
            repos = github_data["repos"]
            top_repo = repos[0] if repos else None
            paper_dict["github_stats"] = {
                "total_stars": github_data.get("total_stars", 0),
                "repo_count": len(repos),
                "top_repo": {
                    "url": top_repo.get("url"),
                    "stars": top_repo.get("stars", 0),
                    "forks": top_repo.get("forks", 0),
                    "language": top_repo.get("language"),
                    "pushed_at": top_repo.get("pushed_at"),
                } if top_repo else None
            }

        papers.append(paper_dict)

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
            p.ai_analysis->>'hasCode' as has_code_flag,
            p.external_signals->'github' as github_data
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
        github_data = row["github_data"] if isinstance(row["github_data"], dict) else json.loads(row["github_data"]) if row["github_data"] else None

        repro_score = tech_depth.get("reproducibility_score")
        if isinstance(repro_score, str):
            try:
                repro_score = int(repro_score)
            except ValueError:
                repro_score = None

        paper_dict = {
            "id": row["id"],
            "title": row["title"],
            "reproducibility_score": repro_score,
            "code_availability": tech_depth.get("code_availability"),
            "implementation_detail": tech_depth.get("implementation_detail"),
            "github_urls": artifacts.get("github_urls", []),
            "datasets_mentioned": artifacts.get("datasets_mentioned", []),
            "has_code": row["has_code_flag"] == "true",
        }

        # Add GitHub stats if available (richer data from external_signals)
        if github_data and github_data.get("repos"):
            repos = github_data["repos"]
            top_repo = repos[0] if repos else None
            paper_dict["github_stats"] = {
                "total_stars": github_data.get("total_stars", 0),
                "repo_count": len(repos),
                "top_repo": {
                    "url": top_repo.get("url"),
                    "stars": top_repo.get("stars", 0),
                    "forks": top_repo.get("forks", 0),
                    "language": top_repo.get("language"),
                    "pushed_at": top_repo.get("pushed_at"),
                } if top_repo else None
            }

        papers.append(paper_dict)

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


# ============== Rising Papers (Citation Velocity) ==============

class RisingPaper(BaseModel):
    """Paper with citation velocity metrics"""
    id: str
    title: str
    published: str
    category: str
    citation_count: int
    influential_citation_count: int
    months_since_publication: float
    citation_velocity: float  # citations per month
    link: str


@router.get("/rising", response_model=dict)
async def get_rising_papers(
    category: Optional[str] = Query(default=None),
    min_citations: int = Query(default=5, ge=1, description="Minimum citation count to consider"),
    min_months: float = Query(default=1.0, ge=0.5, description="Minimum months since publication"),
    max_months: Optional[float] = Query(default=24, description="Maximum months since publication (default 24 for recency)"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Discover rising papers with high citation velocity.

    Citation velocity = citations / months_since_publication

    This identifies papers gaining traction faster than average:
    - A paper with 50 citations in 2 months (velocity=25) is more notable
      than a paper with 100 citations in 12 months (velocity=8.3)

    Filters:
    - min_citations: Exclude papers with few citations (noise filter)
    - min_months: Exclude very new papers (need time to accumulate citations)
    - max_months: Focus on recent papers (default 24 months)

    Returns papers sorted by citation velocity (highest first).
    """
    conditions = [
        "p.citation_count >= :min_citations",
        "p.published_date IS NOT NULL",
        # Calculate months since publication
        "EXTRACT(EPOCH FROM (NOW() - p.published_date)) / 2592000.0 >= :min_months"  # 2592000 = 30 days in seconds
    ]
    params = {
        "limit": limit,
        "offset": offset,
        "min_citations": min_citations,
        "min_months": min_months
    }

    if max_months:
        conditions.append("EXTRACT(EPOCH FROM (NOW() - p.published_date)) / 2592000.0 <= :max_months")
        params["max_months"] = max_months

    if category:
        conditions.append("p.category = :category")
        params["category"] = category

    where_clause = " AND ".join(conditions)

    # Count total
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}
    count_query = f"SELECT COUNT(*) as total FROM papers p WHERE {where_clause}"
    count_result = await database.fetch_one(count_query, count_params)
    total = count_result["total"] if count_result else 0

    # Fetch papers with velocity calculation
    query = f"""
        SELECT
            p.id,
            p.title,
            p.published_date,
            p.category,
            p.citation_count,
            p.influential_citation_count,
            EXTRACT(EPOCH FROM (NOW() - p.published_date)) / 2592000.0 as months_since_pub,
            p.citation_count / GREATEST(EXTRACT(EPOCH FROM (NOW() - p.published_date)) / 2592000.0, 0.1) as velocity
        FROM papers p
        WHERE {where_clause}
        ORDER BY velocity DESC, p.citation_count DESC
        LIMIT :limit OFFSET :offset
    """

    rows = await database.fetch_all(query, params)

    papers = []
    for row in rows:
        months = float(row["months_since_pub"]) if row["months_since_pub"] else 1.0
        velocity = float(row["velocity"]) if row["velocity"] else 0.0

        papers.append({
            "id": row["id"],
            "title": row["title"],
            "published": row["published_date"].isoformat() if row["published_date"] else None,
            "category": row["category"],
            "citation_count": row["citation_count"] or 0,
            "influential_citation_count": row["influential_citation_count"] or 0,
            "months_since_publication": round(months, 1),
            "citation_velocity": round(velocity, 2),
            "link": f"https://arxiv.org/abs/{row['id']}"
        })

    # Get velocity distribution stats
    dist_query = f"""
        SELECT velocity_tier, count FROM (
            SELECT
                CASE
                    WHEN velocity >= 20 THEN 'viral (20+/mo)'
                    WHEN velocity >= 10 THEN 'hot (10-20/mo)'
                    WHEN velocity >= 5 THEN 'rising (5-10/mo)'
                    WHEN velocity >= 2 THEN 'growing (2-5/mo)'
                    ELSE 'steady (<2/mo)'
                END as velocity_tier,
                COUNT(*) as count
            FROM (
                SELECT
                    p.citation_count / GREATEST(EXTRACT(EPOCH FROM (NOW() - p.published_date)) / 2592000.0, 0.1) as velocity
                FROM papers p
                WHERE p.citation_count >= :min_citations
                  AND p.published_date IS NOT NULL
                  AND EXTRACT(EPOCH FROM (NOW() - p.published_date)) / 2592000.0 >= :min_months
                  {"AND EXTRACT(EPOCH FROM (NOW() - p.published_date)) / 2592000.0 <= :max_months" if max_months else ""}
            ) sub
            GROUP BY 1
        ) dist
        ORDER BY
            CASE velocity_tier
                WHEN 'viral (20+/mo)' THEN 1
                WHEN 'hot (10-20/mo)' THEN 2
                WHEN 'rising (5-10/mo)' THEN 3
                WHEN 'growing (2-5/mo)' THEN 4
                ELSE 5
            END
    """
    dist_params = {"min_citations": min_citations, "min_months": min_months}
    if max_months:
        dist_params["max_months"] = max_months

    dist_rows = await database.fetch_all(dist_query, dist_params)
    distribution = {row["velocity_tier"]: row["count"] for row in dist_rows}

    return {
        "papers": papers,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(papers) < total,
        "velocity_distribution": distribution,
        "filters": {
            "min_citations": min_citations,
            "min_months": min_months,
            "max_months": max_months,
            "category": category
        },
        "velocity_tiers": {
            "viral": "20+ citations/month",
            "hot": "10-20 citations/month",
            "rising": "5-10 citations/month",
            "growing": "2-5 citations/month",
            "steady": "<2 citations/month"
        }
    }


# ============== Hot Topics Dashboard ==============

class HotTopic(BaseModel):
    """A trending research topic with aggregated metrics"""
    name: str
    paper_count: int
    total_citations: int
    avg_citation_velocity: float
    max_velocity: float
    velocity_tier: str
    trend_direction: str  # up, down, stable
    trend_pct: Optional[float] = None
    categories: List[str] = []
    top_papers: List[dict] = []


@router.get("/hot-topics", response_model=dict)
async def get_hot_topics(
    days: int = Query(default=180, ge=7, le=365, description="Timeframe for trend calculation (default 6 months for citation accumulation)"),
    min_papers: int = Query(default=3, ge=1, le=50, description="Minimum papers per topic"),
    category: Optional[str] = Query(default=None, description="Filter to arXiv category"),
    min_citations: int = Query(default=1, ge=1, description="Minimum citations per paper"),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Get trending research topics based on aggregated citation velocity.

    This endpoint identifies "hot" research topics by:
    1. Finding papers with citation momentum (citation_velocity > 0)
    2. Grouping by concept (topic) from the concepts table
    3. Calculating aggregate metrics: total citations, avg velocity, paper count
    4. Comparing to previous period for trend direction

    Velocity tiers for topics (based on max paper velocity):
    - viral: Has papers with 20+ citations/month
    - hot: Has papers with 10-20 citations/month
    - rising: Has papers with 5-10 citations/month
    - growing: Has papers with 2-5 citations/month
    - emerging: Max velocity < 2/month

    Returns topics sorted by a composite score of velocity + paper count.
    """
    params = {
        "min_papers": min_papers,
        "min_citations": min_citations,
        "limit": limit,
    }

    # Build category filter
    category_filter = ""
    if category:
        category_filter = "AND p.category = :category"
        params["category"] = category

    # Calculate date cutoffs
    cutoff_date = datetime.now() - timedelta(days=days)
    prev_cutoff_date = datetime.now() - timedelta(days=days * 2)

    params["cutoff_date"] = cutoff_date
    params["prev_cutoff_date"] = prev_cutoff_date

    # Main query: Get hot topics with aggregated metrics
    # Join papers -> paper_concepts -> concepts
    # Calculate velocity for each paper, then aggregate by concept
    query = f"""
        WITH paper_velocities AS (
            -- Calculate velocity for each paper in the time window
            SELECT
                p.id as paper_id,
                p.title,
                p.category,
                p.citation_count,
                p.influential_citation_count,
                p.published_date,
                EXTRACT(EPOCH FROM (NOW() - p.published_date)) / 2592000.0 as months_since_pub,
                p.citation_count / GREATEST(EXTRACT(EPOCH FROM (NOW() - p.published_date)) / 2592000.0, 0.1) as velocity
            FROM papers p
            WHERE p.citation_count >= :min_citations
              AND p.published_date >= :cutoff_date
              AND p.published_date IS NOT NULL
              {category_filter}
        ),
        topic_aggregates AS (
            -- Aggregate by concept
            SELECT
                c.name as topic_name,
                c.id as concept_id,
                COUNT(DISTINCT pv.paper_id) as paper_count,
                SUM(pv.citation_count) as total_citations,
                AVG(pv.velocity) as avg_velocity,
                MAX(pv.velocity) as max_velocity,
                array_agg(DISTINCT pv.category) as categories,
                json_agg(
                    json_build_object(
                        'id', pv.paper_id,
                        'title', pv.title,
                        'velocity', ROUND(pv.velocity::numeric, 2),
                        'citations', pv.citation_count
                    ) ORDER BY pv.velocity DESC
                ) FILTER (WHERE pv.velocity IS NOT NULL) as papers_json
            FROM paper_velocities pv
            JOIN paper_concepts pc ON pv.paper_id = pc.paper_id
            JOIN concepts c ON pc.concept_id = c.id
            GROUP BY c.id, c.name
            HAVING COUNT(DISTINCT pv.paper_id) >= :min_papers
        ),
        prev_period AS (
            -- Calculate previous period counts for trend
            SELECT
                c.name as topic_name,
                COUNT(DISTINCT p.id) as prev_paper_count
            FROM papers p
            JOIN paper_concepts pc ON p.id = pc.paper_id
            JOIN concepts c ON pc.concept_id = c.id
            WHERE p.citation_count >= :min_citations
              AND p.published_date >= :prev_cutoff_date
              AND p.published_date < :cutoff_date
              AND p.published_date IS NOT NULL
              {category_filter}
            GROUP BY c.name
        )
        SELECT
            ta.topic_name,
            ta.paper_count,
            ta.total_citations,
            ta.avg_velocity,
            ta.max_velocity,
            ta.categories,
            ta.papers_json,
            pp.prev_paper_count,
            CASE
                WHEN ta.max_velocity >= 20 THEN 'viral'
                WHEN ta.max_velocity >= 10 THEN 'hot'
                WHEN ta.max_velocity >= 5 THEN 'rising'
                WHEN ta.max_velocity >= 2 THEN 'growing'
                ELSE 'emerging'
            END as velocity_tier
        FROM topic_aggregates ta
        LEFT JOIN prev_period pp ON ta.topic_name = pp.topic_name
        ORDER BY
            -- Composite score: velocity matters most, then paper count
            (ta.avg_velocity * 0.6 + ta.paper_count * 0.4) DESC,
            ta.total_citations DESC
        LIMIT :limit
    """

    rows = await database.fetch_all(query, params)

    topics = []
    velocity_tier_counts = {"viral": 0, "hot": 0, "rising": 0, "growing": 0, "emerging": 0}

    for row in rows:
        # Parse papers JSON
        papers_data = row["papers_json"]
        if isinstance(papers_data, str):
            papers_data = json.loads(papers_data)

        # Get top 5 papers for this topic
        top_papers = papers_data[:5] if papers_data else []

        # Calculate trend
        current_count = row["paper_count"]
        prev_count = row["prev_paper_count"] or 0

        if prev_count == 0:
            trend_direction = "up" if current_count > 0 else "stable"
            trend_pct = None
        else:
            change_pct = ((current_count - prev_count) / prev_count) * 100
            if change_pct > 10:
                trend_direction = "up"
            elif change_pct < -10:
                trend_direction = "down"
            else:
                trend_direction = "stable"
            trend_pct = round(change_pct, 1)

        # Parse categories
        categories = row["categories"]
        if isinstance(categories, str):
            categories = categories.strip("{}").split(",") if categories else []

        velocity_tier = row["velocity_tier"]
        velocity_tier_counts[velocity_tier] = velocity_tier_counts.get(velocity_tier, 0) + 1

        topics.append({
            "name": row["topic_name"],
            "paper_count": row["paper_count"],
            "total_citations": row["total_citations"] or 0,
            "avg_citation_velocity": round(float(row["avg_velocity"] or 0), 2),
            "max_velocity": round(float(row["max_velocity"] or 0), 2),
            "velocity_tier": velocity_tier,
            "trend_direction": trend_direction,
            "trend_pct": trend_pct,
            "categories": list(set(categories)) if categories else [],
            "top_papers": top_papers,
        })

    # Get total topic count
    count_query = f"""
        SELECT COUNT(DISTINCT c.name) as total
        FROM papers p
        JOIN paper_concepts pc ON p.id = pc.paper_id
        JOIN concepts c ON pc.concept_id = c.id
        WHERE p.citation_count >= :min_citations
          AND p.published_date >= :cutoff_date
          AND p.published_date IS NOT NULL
          {category_filter}
        GROUP BY c.name
        HAVING COUNT(DISTINCT p.id) >= :min_papers
    """
    count_result = await database.fetch_all(count_query, {
        "min_citations": min_citations,
        "cutoff_date": cutoff_date,
        "min_papers": min_papers,
        **({"category": category} if category else {})
    })
    total_topics = len(count_result) if count_result else 0

    return {
        "topics": topics,
        "total": total_topics,
        "limit": limit,
        "timeframe_days": days,
        "filters": {
            "min_papers": min_papers,
            "min_citations": min_citations,
            "category": category,
        },
        "velocity_tier_distribution": velocity_tier_counts,
        "velocity_tiers": {
            "viral": "Has papers with 20+ citations/month",
            "hot": "Has papers with 10-20 citations/month",
            "rising": "Has papers with 5-10 citations/month",
            "growing": "Has papers with 2-5 citations/month",
            "emerging": "Max velocity < 2/month"
        }
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

    # Category distribution (top 10 categories)
    category_dist_query = """
        SELECT
            category,
            COUNT(*) as count
        FROM papers
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
        ORDER BY count DESC
        LIMIT 10
    """
    category_dist = await database.fetch_all(category_dist_query)

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
            "categories": {row["category"]: row["count"] for row in category_dist},
        }
    }


# ============== Advanced Momentum Intelligence ==============

from app.services.momentum_service import get_momentum_service


@router.get("/rising-stars", response_model=dict)
async def get_rising_stars(
    days: int = Query(default=90, ge=7, le=365, description="Look back N days"),
    min_citations: int = Query(default=1, ge=1, description="Minimum citations to include"),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Find papers with highest citation velocity (citations per day).

    Unlike /rising which uses months, this uses days for more precision
    and includes age-adjusted performance metrics:
    - citations_per_day: Raw velocity
    - velocity_percentile: How this compares to peers
    - expected_citations: What we'd expect for this age
    - performance_ratio: Actual vs expected (>3 = breakout)
    - momentum_score: Composite score factoring velocity + recency

    Great for discovering papers gaining traction RIGHT NOW.
    """
    service = get_momentum_service()
    results = await service.get_rising_stars(
        days=days,
        min_citations=min_citations,
        limit=limit
    )

    return {
        "papers": results,
        "total": len(results),
        "filters": {
            "days": days,
            "min_citations": min_citations
        },
        "metrics_explained": {
            "citations_per_day": "Raw citation velocity",
            "velocity_percentile": "Position vs all papers (99 = top 1%)",
            "expected_citations": "Typical citations for this paper age",
            "performance_ratio": "Actual / Expected (>3 = breakout)",
            "momentum_score": "Composite score (velocity * recency)"
        }
    }


@router.get("/breakout-papers", response_model=dict)
async def get_breakout_papers(
    days: int = Query(default=30, ge=7, le=180, description="Look at papers from last N days"),
    min_ratio: float = Query(default=3.0, ge=1.5, le=10.0, description="Minimum performance ratio"),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Find recent papers dramatically outperforming expectations.

    Breakout papers are getting 3x+ the citations expected for their age.
    This identifies potential landmark papers early - before they become famous.

    A paper from 2 weeks ago with 10 citations when we'd expect 0.5
    is a 20x breakout - that's extremely noteworthy!

    Returns papers sorted by performance_ratio (highest overperformance first).
    """
    service = get_momentum_service()
    results = await service.get_breakout_papers(
        days=days,
        min_ratio=min_ratio,
        limit=limit
    )

    return {
        "papers": results,
        "total": len(results),
        "filters": {
            "days": days,
            "min_ratio": min_ratio
        },
        "explanation": f"Papers from the last {days} days with {min_ratio}x+ expected citations"
    }


@router.get("/hidden-gems", response_model=dict)
async def get_hidden_gems(
    min_age_days: int = Query(default=60, ge=30, description="Minimum paper age in days"),
    max_age_days: int = Query(default=365, ge=60, le=730, description="Maximum paper age in days"),
    min_citations: int = Query(default=5, ge=1, description="Minimum citations"),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Find underappreciated quality papers that deserve more attention.

    Hidden gems are papers with:
    - Solid citation counts (above average but not viral)
    - Good quality indicators (impact score if available)
    - Not currently trending (moderate velocity)

    These are papers that did well but didn't go viral - often because
    they're in niche areas or ahead of their time.

    Perfect for finding important work that the crowd missed.
    """
    service = get_momentum_service()
    results = await service.get_hidden_gems(
        min_age_days=min_age_days,
        max_age_days=max_age_days,
        min_citations=min_citations,
        limit=limit
    )

    return {
        "papers": results,
        "total": len(results),
        "filters": {
            "min_age_days": min_age_days,
            "max_age_days": max_age_days,
            "min_citations": min_citations
        },
        "explanation": f"Quality papers from {min_age_days}-{max_age_days} days ago that aren't trending"
    }


@router.get("/paper/{paper_id}/momentum", response_model=dict)
async def get_paper_momentum(paper_id: str):
    """
    Get momentum metrics for a specific paper.

    Returns detailed velocity and performance analysis:
    - How fast is this paper gaining citations?
    - How does it compare to papers of similar age?
    - Is it a breakout paper?
    - What's the momentum trend?

    Use this to understand if a specific paper is gaining traction.
    """
    service = get_momentum_service()
    result = await service.get_paper_momentum(paper_id)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Paper not found: {paper_id}")

    return result


@router.get("/weekly-digest", response_model=dict)
async def get_weekly_digest():
    """
    Get a curated weekly digest of paper momentum.

    Combines:
    - Rising stars: Top 5 papers by velocity this week
    - Breakout papers: Papers exceeding expectations
    - Hidden gems: Quality papers worth discovering

    Perfect for weekly research updates.
    """
    service = get_momentum_service()
    return await service.get_weekly_digest(limit=10)
