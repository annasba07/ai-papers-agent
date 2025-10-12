"""
Similarity and knowledge graph query service

Implements all 5 query patterns:
1. Semantic similarity (vector search)
2. Concept similarity (shared concepts)
3. Citation lineage (graph traversal)
4. Latest in domain (temporal + topic)
5. Performance benchmarks (leaderboards)
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy import text

from app.db.database import database


class SimilarityService:
    """Service for finding related papers and knowledge graph queries"""

    def __init__(self):
        self.default_limit = 10
        self.max_limit = 100

    # ============================================================================
    # 1. SEMANTIC SIMILARITY (Vector Search)
    # ============================================================================

    async def find_similar_papers(
        self,
        paper_id: str,
        limit: int = 10,
        min_similarity: float = 0.7,
        exclude_cited: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find semantically similar papers using vector cosine distance

        Args:
            paper_id: Source paper arXiv ID
            limit: Maximum results (default 10, max 100)
            min_similarity: Minimum cosine similarity (0.0-1.0)
            exclude_cited: Exclude papers already cited

        Returns:
            List of similar papers with similarity scores
        """
        limit = min(limit, self.max_limit)

        # Build query with optional citation filter
        exclude_clause = ""
        if exclude_cited:
            exclude_clause = """
                AND p2.id NOT IN (
                    SELECT cited_paper_id FROM citations WHERE citing_paper_id = :paper_id
                )
            """

        query = f"""
            SELECT
                p2.id,
                p2.title,
                p2.abstract,
                p2.authors,
                p2.published_date,
                p2.category,
                p2.citation_count,
                p2.quality_score,
                1 - (p1.embedding <=> p2.embedding) as similarity
            FROM papers p1
            CROSS JOIN papers p2
            WHERE p1.id = :paper_id
                AND p2.id != :paper_id
                AND p1.embedding IS NOT NULL
                AND p2.embedding IS NOT NULL
                AND (1 - (p1.embedding <=> p2.embedding)) >= :min_similarity
                {exclude_clause}
            ORDER BY p1.embedding <=> p2.embedding
            LIMIT :limit
        """

        results = await database.fetch_all(
            text(query),
            {
                "paper_id": paper_id,
                "min_similarity": min_similarity,
                "limit": limit
            }
        )

        return [dict(r) for r in results]

    async def find_similar_by_text(
        self,
        text_embedding: List[float],
        limit: int = 10,
        category: Optional[str] = None,
        min_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Find papers similar to arbitrary text (search query)

        Args:
            text_embedding: Pre-computed embedding vector
            limit: Maximum results
            category: Optional category filter (e.g., 'cs.AI')
            min_date: Optional minimum publication date

        Returns:
            List of similar papers
        """
        limit = min(limit, self.max_limit)

        # Build optional filters
        filters = []
        params = {
            "embedding": str(text_embedding),
            "limit": limit
        }

        if category:
            filters.append("category = :category")
            params["category"] = category

        if min_date:
            filters.append("published_date >= :min_date")
            params["min_date"] = min_date

        where_clause = "WHERE " + " AND ".join(filters) if filters else ""

        query = f"""
            SELECT
                id,
                title,
                abstract,
                authors,
                published_date,
                category,
                citation_count,
                quality_score,
                1 - (embedding <=> :embedding::vector) as similarity
            FROM papers
            {where_clause}
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """

        results = await database.fetch_all(text(query), params)
        return [dict(r) for r in results]

    # ============================================================================
    # 2. CONCEPT SIMILARITY (Shared Concepts)
    # ============================================================================

    async def find_papers_by_concept(
        self,
        concept_name: str,
        limit: int = 20,
        min_relevance: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find papers related to a specific concept

        Args:
            concept_name: Concept name (fuzzy match)
            limit: Maximum results
            min_relevance: Minimum relevance score

        Returns:
            List of papers with relevance scores
        """
        limit = min(limit, self.max_limit)

        query = """
            SELECT
                p.id,
                p.title,
                p.abstract,
                p.published_date,
                p.category,
                p.citation_count,
                pc.relevance,
                c.name as concept_name
            FROM papers p
            JOIN paper_concepts pc ON p.id = pc.paper_id
            JOIN concepts c ON pc.concept_id = c.id
            WHERE c.normalized_name ILIKE :concept_pattern
                AND pc.relevance >= :min_relevance
            ORDER BY pc.relevance DESC, p.citation_count DESC
            LIMIT :limit
        """

        results = await database.fetch_all(
            text(query),
            {
                "concept_pattern": f"%{concept_name.lower()}%",
                "min_relevance": min_relevance,
                "limit": limit
            }
        )

        return [dict(r) for r in results]

    async def find_similar_by_concepts(
        self,
        paper_id: str,
        limit: int = 10,
        min_shared_concepts: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Find papers that share concepts with given paper

        Args:
            paper_id: Source paper ID
            limit: Maximum results
            min_shared_concepts: Minimum number of shared concepts

        Returns:
            List of papers with shared concept count and scores
        """
        limit = min(limit, self.max_limit)

        query = """
            WITH source_concepts AS (
                SELECT concept_id, relevance
                FROM paper_concepts
                WHERE paper_id = :paper_id
            )
            SELECT
                p.id,
                p.title,
                p.abstract,
                p.published_date,
                p.category,
                p.citation_count,
                COUNT(DISTINCT pc.concept_id) as shared_concepts,
                AVG(pc.relevance * sc.relevance) as concept_similarity
            FROM papers p
            JOIN paper_concepts pc ON p.id = pc.paper_id
            JOIN source_concepts sc ON pc.concept_id = sc.concept_id
            WHERE p.id != :paper_id
            GROUP BY p.id
            HAVING COUNT(DISTINCT pc.concept_id) >= :min_shared_concepts
            ORDER BY concept_similarity DESC, shared_concepts DESC
            LIMIT :limit
        """

        results = await database.fetch_all(
            text(query),
            {
                "paper_id": paper_id,
                "min_shared_concepts": min_shared_concepts,
                "limit": limit
            }
        )

        return [dict(r) for r in results]

    async def get_trending_concepts(
        self,
        days: int = 30,
        limit: int = 20,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get trending concepts based on recent papers

        Args:
            days: Look back period
            limit: Maximum results
            category: Optional category filter

        Returns:
            List of concepts with paper counts and growth
        """
        limit = min(limit, self.max_limit)

        category_filter = ""
        params = {
            "days": days,
            "limit": limit
        }

        if category:
            category_filter = "AND p.category = :category"
            params["category"] = category

        query = f"""
            SELECT
                c.id,
                c.name,
                c.category,
                c.paper_count as total_papers,
                COUNT(DISTINCT pc.paper_id) as recent_papers,
                AVG(pc.relevance) as avg_relevance,
                ROUND(100.0 * COUNT(DISTINCT pc.paper_id) / NULLIF(c.paper_count, 0), 2) as growth_percentage
            FROM concepts c
            JOIN paper_concepts pc ON c.id = pc.concept_id
            JOIN papers p ON pc.paper_id = p.id
            WHERE p.published_date > CURRENT_DATE - INTERVAL ':days days'
                {category_filter}
            GROUP BY c.id
            HAVING COUNT(DISTINCT pc.paper_id) >= 3
            ORDER BY recent_papers DESC, growth_percentage DESC
            LIMIT :limit
        """

        results = await database.fetch_all(text(query), params)
        return [dict(r) for r in results]

    # ============================================================================
    # 3. CITATION LINEAGE (Graph Traversal)
    # ============================================================================

    async def get_citation_ancestry(
        self,
        paper_id: str,
        max_depth: int = 3,
        limit_per_level: int = 10
    ) -> Dict[str, Any]:
        """
        Get papers that this paper cites (ancestry)

        Args:
            paper_id: Source paper ID
            max_depth: Maximum recursion depth
            limit_per_level: Max papers per depth level

        Returns:
            Tree structure of cited papers
        """
        query = """
            WITH RECURSIVE citation_tree AS (
                -- Base case: direct citations
                SELECT
                    c.cited_paper_id as paper_id,
                    p.title,
                    p.published_date,
                    p.citation_count,
                    c.is_influential,
                    1 as depth,
                    ARRAY[c.cited_paper_id] as path
                FROM citations c
                JOIN papers p ON c.cited_paper_id = p.id
                WHERE c.citing_paper_id = :paper_id

                UNION ALL

                -- Recursive case: citations of citations
                SELECT
                    c.cited_paper_id,
                    p.title,
                    p.published_date,
                    p.citation_count,
                    c.is_influential,
                    ct.depth + 1,
                    ct.path || c.cited_paper_id
                FROM citation_tree ct
                JOIN citations c ON ct.paper_id = c.citing_paper_id
                JOIN papers p ON c.cited_paper_id = p.id
                WHERE ct.depth < :max_depth
                    AND NOT (c.cited_paper_id = ANY(ct.path))  -- Prevent cycles
            )
            SELECT DISTINCT ON (paper_id)
                paper_id,
                title,
                published_date,
                citation_count,
                is_influential,
                depth
            FROM citation_tree
            ORDER BY paper_id, depth
        """

        results = await database.fetch_all(
            text(query),
            {
                "paper_id": paper_id,
                "max_depth": max_depth
            }
        )

        # Organize by depth
        tree = {"paper_id": paper_id, "cited_papers": {}}
        for r in results:
            depth = r["depth"]
            if depth not in tree["cited_papers"]:
                tree["cited_papers"][depth] = []

            tree["cited_papers"][depth].append(dict(r))

            # Limit per level
            if len(tree["cited_papers"][depth]) >= limit_per_level:
                continue

        return tree

    async def get_citation_descendants(
        self,
        paper_id: str,
        max_depth: int = 3,
        limit_per_level: int = 10
    ) -> Dict[str, Any]:
        """
        Get papers that cite this paper (descendants)

        Args:
            paper_id: Source paper ID
            max_depth: Maximum recursion depth
            limit_per_level: Max papers per depth level

        Returns:
            Tree structure of citing papers
        """
        query = """
            WITH RECURSIVE citation_tree AS (
                -- Base case: direct citations
                SELECT
                    c.citing_paper_id as paper_id,
                    p.title,
                    p.published_date,
                    p.citation_count,
                    c.is_influential,
                    1 as depth,
                    ARRAY[c.citing_paper_id] as path
                FROM citations c
                JOIN papers p ON c.citing_paper_id = p.id
                WHERE c.cited_paper_id = :paper_id

                UNION ALL

                -- Recursive case: papers that cite citations
                SELECT
                    c.citing_paper_id,
                    p.title,
                    p.published_date,
                    p.citation_count,
                    c.is_influential,
                    ct.depth + 1,
                    ct.path || c.citing_paper_id
                FROM citation_tree ct
                JOIN citations c ON ct.paper_id = c.cited_paper_id
                JOIN papers p ON c.citing_paper_id = p.id
                WHERE ct.depth < :max_depth
                    AND NOT (c.citing_paper_id = ANY(ct.path))  -- Prevent cycles
            )
            SELECT DISTINCT ON (paper_id)
                paper_id,
                title,
                published_date,
                citation_count,
                is_influential,
                depth
            FROM citation_tree
            ORDER BY paper_id, depth
        """

        results = await database.fetch_all(
            text(query),
            {
                "paper_id": paper_id,
                "max_depth": max_depth
            }
        )

        # Organize by depth
        tree = {"paper_id": paper_id, "citing_papers": {}}
        for r in results:
            depth = r["depth"]
            if depth not in tree["citing_papers"]:
                tree["citing_papers"][depth] = []

            tree["citing_papers"][depth].append(dict(r))

            # Limit per level
            if len(tree["citing_papers"][depth]) >= limit_per_level:
                continue

        return tree

    async def get_citation_network(
        self,
        paper_id: str,
        radius: int = 2
    ) -> Dict[str, Any]:
        """
        Get local citation network (both ancestors and descendants)

        Args:
            paper_id: Center paper ID
            radius: How many hops in each direction

        Returns:
            Graph structure with nodes and edges
        """
        # Get both directions
        ancestry = await self.get_citation_ancestry(paper_id, max_depth=radius)
        descendants = await self.get_citation_descendants(paper_id, max_depth=radius)

        # Collect all paper IDs
        all_paper_ids: Set[str] = {paper_id}
        for depth_papers in ancestry.get("cited_papers", {}).values():
            all_paper_ids.update(p["paper_id"] for p in depth_papers)
        for depth_papers in descendants.get("citing_papers", {}).values():
            all_paper_ids.update(p["paper_id"] for p in depth_papers)

        # Get all edges
        if len(all_paper_ids) > 1:
            placeholders = ",".join([f":id_{i}" for i in range(len(all_paper_ids))])
            params = {f"id_{i}": pid for i, pid in enumerate(all_paper_ids)}

            edges_query = f"""
                SELECT citing_paper_id, cited_paper_id, is_influential
                FROM citations
                WHERE citing_paper_id IN ({placeholders})
                    OR cited_paper_id IN ({placeholders})
            """

            edges = await database.fetch_all(text(edges_query), params)
        else:
            edges = []

        return {
            "center": paper_id,
            "nodes": list(all_paper_ids),
            "edges": [dict(e) for e in edges],
            "ancestry": ancestry,
            "descendants": descendants
        }

    # ============================================================================
    # 4. LATEST IN DOMAIN (Temporal + Topic)
    # ============================================================================

    async def get_latest_papers(
        self,
        category: Optional[str] = None,
        concepts: Optional[List[str]] = None,
        days: int = 30,
        limit: int = 20,
        min_quality: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Get latest papers in a domain/topic

        Args:
            category: arXiv category (e.g., 'cs.AI')
            concepts: List of concept names
            days: Look back period
            limit: Maximum results
            min_quality: Minimum quality score

        Returns:
            List of recent papers sorted by date
        """
        limit = min(limit, self.max_limit)

        filters = ["published_date > CURRENT_DATE - INTERVAL ':days days'"]
        params = {"days": days, "limit": limit, "min_quality": min_quality}

        if category:
            filters.append("category = :category")
            params["category"] = category

        if min_quality > 0:
            filters.append("quality_score >= :min_quality")

        # Build concept filter if provided
        concept_join = ""
        if concepts:
            concept_join = """
                JOIN paper_concepts pc ON p.id = pc.paper_id
                JOIN concepts c ON pc.concept_id = c.id
            """
            concept_conditions = " OR ".join([
                f"c.normalized_name ILIKE :concept_{i}"
                for i in range(len(concepts))
            ])
            filters.append(f"({concept_conditions})")
            for i, concept in enumerate(concepts):
                params[f"concept_{i}"] = f"%{concept.lower()}%"

        where_clause = " AND ".join(filters)

        query = f"""
            SELECT DISTINCT
                p.id,
                p.title,
                p.abstract,
                p.authors,
                p.published_date,
                p.category,
                p.citation_count,
                p.quality_score
            FROM papers p
            {concept_join}
            WHERE {where_clause}
            ORDER BY p.published_date DESC, p.quality_score DESC
            LIMIT :limit
        """

        results = await database.fetch_all(text(query), params)
        return [dict(r) for r in results]

    # ============================================================================
    # 5. PERFORMANCE BENCHMARKS (Leaderboards)
    # ============================================================================

    async def get_benchmark_leaderboard(
        self,
        task: str,
        dataset: str,
        metric: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get benchmark leaderboard for a task/dataset

        Args:
            task: Task name (e.g., 'image classification')
            dataset: Dataset name (e.g., 'ImageNet')
            metric: Optional metric filter (e.g., 'accuracy')
            limit: Maximum results

        Returns:
            Ranked list of papers with performance scores
        """
        limit = min(limit, self.max_limit)

        filters = ["b.task ILIKE :task", "b.dataset ILIKE :dataset"]
        params = {
            "task": f"%{task}%",
            "dataset": f"%{dataset}%",
            "limit": limit
        }

        if metric:
            filters.append("b.metric ILIKE :metric")
            params["metric"] = f"%{metric}%"

        where_clause = " AND ".join(filters)

        query = f"""
            SELECT
                p.id,
                p.title,
                p.published_date,
                p.citation_count,
                b.task,
                b.dataset,
                b.metric,
                b.value as score,
                b.model_name,
                b.model_size,
                b.compute_cost,
                RANK() OVER (PARTITION BY b.task, b.dataset, b.metric ORDER BY b.value DESC) as rank
            FROM benchmarks b
            JOIN papers p ON b.paper_id = p.id
            WHERE {where_clause}
            ORDER BY b.value DESC, p.published_date DESC
            LIMIT :limit
        """

        results = await database.fetch_all(text(query), params)
        return [dict(r) for r in results]

    async def get_trending_techniques(
        self,
        task: str,
        days: int = 180,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get techniques with improving performance over time

        Args:
            task: Task name
            days: Look back period
            limit: Maximum results

        Returns:
            List of improving techniques with trend data
        """
        query = """
            WITH recent_benchmarks AS (
                SELECT
                    b.model_name,
                    b.task,
                    b.dataset,
                    b.metric,
                    MAX(b.value) as best_score,
                    COUNT(*) as paper_count,
                    MAX(b.reported_date) as latest_date
                FROM benchmarks b
                WHERE b.task ILIKE :task
                    AND b.reported_date > CURRENT_DATE - INTERVAL ':days days'
                GROUP BY b.model_name, b.task, b.dataset, b.metric
            )
            SELECT *
            FROM recent_benchmarks
            WHERE paper_count >= 2
            ORDER BY best_score DESC, latest_date DESC
            LIMIT :limit
        """

        results = await database.fetch_all(
            text(query),
            {
                "task": f"%{task}%",
                "days": days,
                "limit": limit
            }
        )

        return [dict(r) for r in results]


# Global instance
_similarity_service: Optional[SimilarityService] = None


def get_similarity_service() -> SimilarityService:
    """Get or create global similarity service instance"""
    global _similarity_service
    if _similarity_service is None:
        _similarity_service = SimilarityService()
    return _similarity_service
