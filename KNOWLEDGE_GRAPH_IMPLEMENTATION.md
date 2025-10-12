# Research Knowledge Graph - Implementation Guide

**Goal**: Build the fastest paper exploration system supporting 5 critical query patterns across millions of papers.

## 🎯 Query Patterns to Support

1. **Semantic Similarity** - "Find papers like this one" (vector search)
2. **Concept Similarity** - "Similar research ideas" (concept graph)
3. **Citation Lineage** - "What led to this paper" (directed graph traversal)
4. **Latest Techniques** - "Recent advances in transformers" (temporal + topic filter)
5. **Performance Benchmarks** - "Best accuracy on ImageNet" (structured search)

**Performance Target**: <100ms per query on 1M+ papers

---

## 🏗️ Architecture Overview

### Database Stack

```
┌─────────────────────────────────────────────────────┐
│              Application Layer (FastAPI)             │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Similarity  │  │   Citation   │  │ Benchmark │ │
│  │   Service    │  │   Service    │  │  Service  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│         │                  │                 │      │
├─────────┼──────────────────┼─────────────────┼──────┤
│         ▼                  ▼                 ▼      │
│  ┌──────────────────────────────────────────────┐  │
│  │        PostgreSQL 15+ with Extensions        │  │
│  │                                              │  │
│  │  • pgvector (vector similarity)             │  │
│  │  • pg_trgm (text search)                    │  │
│  │  • btree_gin (multi-column indexes)         │  │
│  │                                              │  │
│  │  Tables: papers, concepts, citations,       │  │
│  │          paper_concepts, benchmarks          │  │
│  └──────────────────────────────────────────────┘  │
│                       │                             │
├───────────────────────┼─────────────────────────────┤
│         ┌─────────────▼────────────┐                │
│         │   Redis (Optional)       │                │
│         │   - Query result cache   │                │
│         │   - Hot paper cache      │                │
│         └──────────────────────────┘                │
└─────────────────────────────────────────────────────┘
```

### Why PostgreSQL + pgvector?

**Pros:**
- ✅ Single database for all query types
- ✅ ACID transactions
- ✅ Mature ecosystem
- ✅ pgvector handles vector similarity well
- ✅ Great for <10M papers
- ✅ Easier to operate than multi-DB setup

**Limitations:**
- ⚠️ Vector search slower than dedicated vector DBs (Pinecone, Weaviate)
- ⚠️ Graph traversal slower than Neo4j for complex paths
- ⚠️ But fast enough for our use case!

---

## 📊 Database Schema

### Core Tables

```sql
-- ================================================================
-- PAPERS TABLE - Core paper metadata with vector embeddings
-- ================================================================
CREATE TABLE papers (
    -- Identity
    id VARCHAR(50) PRIMARY KEY,                -- arXiv ID: "2010.11929"

    -- Basic metadata
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    authors JSONB NOT NULL,                    -- ["Author 1", "Author 2", ...]
    published_date TIMESTAMP NOT NULL,
    updated_date TIMESTAMP,
    category VARCHAR(20) NOT NULL,             -- "cs.AI", "cs.CV", etc.

    -- Semantic search
    embedding vector(1536),                    -- OpenAI text-embedding-3-small

    -- Computed metrics (denormalized for speed)
    citation_count INTEGER DEFAULT 0,
    influential_citation_count INTEGER DEFAULT 0,
    quality_score FLOAT DEFAULT 0.0,           -- Computed score 0-10

    -- Rich cached data
    ai_analysis JSONB,                         -- Full AI analysis from Gemini
    code_repos JSONB,                          -- GitHub repos found
    concepts_array TEXT[],                     -- Denormalized for quick access

    -- Full-text search
    search_vector tsvector,                    -- Auto-generated from title + abstract

    -- Housekeeping
    ingested_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- CONCEPTS TABLE - Research topics/techniques/methods
-- ================================================================
CREATE TABLE concepts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,         -- "attention mechanisms", "diffusion models"
    normalized_name VARCHAR(200) NOT NULL,     -- Lowercase, cleaned
    category VARCHAR(50),                      -- "architecture", "technique", "dataset", "task"

    -- Metadata
    paper_count INTEGER DEFAULT 0,             -- Denormalized count
    first_seen_date TIMESTAMP DEFAULT NOW(),
    last_seen_date TIMESTAMP DEFAULT NOW(),

    -- Optional: embeddings for concept similarity
    embedding vector(1536),

    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- PAPER_CONCEPTS - Many-to-many with relevance scores
-- ================================================================
CREATE TABLE paper_concepts (
    paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,
    concept_id INTEGER REFERENCES concepts(id) ON DELETE CASCADE,
    relevance FLOAT NOT NULL CHECK (relevance >= 0 AND relevance <= 1),

    -- Metadata
    extraction_method VARCHAR(50),             -- "llm", "keyword", "citation"
    confidence FLOAT DEFAULT 1.0,

    PRIMARY KEY (paper_id, concept_id)
);

-- ================================================================
-- CITATIONS - Directed graph of paper citations
-- ================================================================
CREATE TABLE citations (
    citing_paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,
    cited_paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,

    -- Citation metadata
    is_influential BOOLEAN DEFAULT FALSE,       -- Semantic Scholar "influential citation"
    context_snippet TEXT,                       -- Optional: where/how cited
    section VARCHAR(50),                        -- "introduction", "related work", etc.

    -- Computed
    citation_year INTEGER,                      -- Year of citing paper (for temporal analysis)

    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (citing_paper_id, cited_paper_id)
);

-- ================================================================
-- BENCHMARKS - Performance metrics on datasets
-- ================================================================
CREATE TABLE benchmarks (
    id SERIAL PRIMARY KEY,
    paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,

    -- What was tested
    task VARCHAR(100) NOT NULL,                -- "image_classification", "object_detection"
    dataset VARCHAR(100) NOT NULL,             -- "ImageNet", "COCO", "SQuAD"
    metric VARCHAR(50) NOT NULL,               -- "accuracy", "f1", "bleu"

    -- Performance
    value FLOAT NOT NULL,

    -- Additional context
    model_name VARCHAR(200),                   -- "ResNet-50", "BERT-base"
    model_size VARCHAR(50),                    -- "355M params"
    compute_cost VARCHAR(100),                 -- "8x V100 GPUs"

    -- Metadata
    reported_date TIMESTAMP,
    metadata JSONB,                            -- Flexible additional data

    created_at TIMESTAMP DEFAULT NOW(),

    -- Prevent duplicates
    UNIQUE(paper_id, task, dataset, metric, model_name)
);

-- ================================================================
-- PAPER_RELATIONSHIPS - Computed similarities (materialized)
-- ================================================================
CREATE TABLE paper_relationships (
    paper_a_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,
    paper_b_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,

    -- Relationship types
    semantic_similarity FLOAT,                  -- From embeddings
    concept_similarity FLOAT,                   -- From shared concepts
    citation_distance INTEGER,                  -- Shortest path in citation graph

    -- Metadata
    computed_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (paper_a_id, paper_b_id),
    CHECK (paper_a_id < paper_b_id)            -- Enforce ordering to prevent duplicates
);
```

### Critical Indexes

```sql
-- ================================================================
-- INDEXES FOR BLAZING FAST QUERIES
-- ================================================================

-- 1. Vector Similarity Search (Query 1)
-- HNSW index for approximate nearest neighbor search (Supabase recommended)
CREATE INDEX papers_embedding_idx ON papers
USING hnsw (embedding vector_cosine_ops);
-- HNSW adapts to data growth automatically, no tuning needed

-- 2. Citation Graph Traversal (Query 3)
-- Bidirectional citation lookup
CREATE INDEX citations_citing_idx ON citations(citing_paper_id);
CREATE INDEX citations_cited_idx ON citations(cited_paper_id);
CREATE INDEX citations_year_idx ON citations(citation_year);

-- 3. Concept-based Search (Query 2)
-- Fast concept → papers lookup
CREATE INDEX paper_concepts_concept_relevance_idx
ON paper_concepts(concept_id, relevance DESC);
-- Fast paper → concepts lookup
CREATE INDEX paper_concepts_paper_idx ON paper_concepts(paper_id);

-- 4. Temporal + Category Filtering (Query 4)
-- Most common query pattern: recent papers in category
CREATE INDEX papers_published_category_idx
ON papers(category, published_date DESC);
-- Hot papers (recent + highly cited)
CREATE INDEX papers_category_citations_idx
ON papers(category, citation_count DESC, published_date DESC);

-- 5. Full-Text Search
CREATE INDEX papers_search_vector_idx ON papers USING gin(search_vector);
CREATE INDEX papers_title_trgm_idx ON papers USING gin(title gin_trgm_ops);

-- 6. Benchmark Queries (Query 5)
-- Fast leaderboard lookup
CREATE INDEX benchmarks_task_dataset_value_idx
ON benchmarks(task, dataset, value DESC);
CREATE INDEX benchmarks_task_dataset_date_idx
ON benchmarks(task, dataset, reported_date DESC);

-- 7. Concept Search
CREATE INDEX concepts_name_trgm_idx ON concepts USING gin(normalized_name gin_trgm_ops);
CREATE INDEX concepts_category_count_idx ON concepts(category, paper_count DESC);

-- 8. Quality filtering
CREATE INDEX papers_quality_published_idx
ON papers(quality_score DESC, published_date DESC);

-- 9. Arrays (for denormalized concepts)
CREATE INDEX papers_concepts_array_idx ON papers USING gin(concepts_array);
```

### Auto-Update Triggers

```sql
-- ================================================================
-- TRIGGERS - Keep denormalized data in sync
-- ================================================================

-- 1. Auto-update search_vector on paper changes
CREATE OR REPLACE FUNCTION papers_search_vector_update()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.abstract, '')), 'B');
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER papers_search_vector_trigger
BEFORE INSERT OR UPDATE OF title, abstract ON papers
FOR EACH ROW EXECUTE FUNCTION papers_search_vector_update();

-- 2. Update paper citation_count when citations added/removed
CREATE OR REPLACE FUNCTION update_citation_count()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE papers
        SET citation_count = citation_count + 1,
            updated_at = NOW()
        WHERE id = NEW.cited_paper_id;

        IF NEW.is_influential THEN
            UPDATE papers
            SET influential_citation_count = influential_citation_count + 1
            WHERE id = NEW.cited_paper_id;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE papers
        SET citation_count = citation_count - 1,
            updated_at = NOW()
        WHERE id = OLD.cited_paper_id;

        IF OLD.is_influential THEN
            UPDATE papers
            SET influential_citation_count = influential_citation_count - 1
            WHERE id = OLD.cited_paper_id;
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER citation_count_trigger
AFTER INSERT OR DELETE ON citations
FOR EACH ROW EXECUTE FUNCTION update_citation_count();

-- 3. Update concept paper_count
CREATE OR REPLACE FUNCTION update_concept_count()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE concepts
        SET paper_count = paper_count + 1,
            last_seen_date = NOW()
        WHERE id = NEW.concept_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE concepts
        SET paper_count = paper_count - 1
        WHERE id = OLD.concept_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER concept_count_trigger
AFTER INSERT OR DELETE ON paper_concepts
FOR EACH ROW EXECUTE FUNCTION update_concept_count();
```

---

## 🚀 Fast Query Implementations

### Query 1: Semantic Similarity

**Use Case**: "Find papers similar to CLIP"

```python
# backend/app/services/similarity_service.py

from typing import List, Optional
from app.db.database import get_db

class SimilarityService:
    """Find semantically similar papers using vector search"""

    async def find_similar_papers(
        self,
        paper_id: str,
        limit: int = 20,
        min_similarity: float = 0.7,
        category_filter: Optional[str] = None,
        min_citations: Optional[int] = None,
        since_date: Optional[str] = None
    ) -> List[dict]:
        """
        Find papers with similar embeddings

        Performance: ~20-50ms for 1M papers
        """

        filters = []
        params = {"paper_id": paper_id, "limit": limit}

        if category_filter:
            filters.append("p.category = :category")
            params["category"] = category_filter

        if min_citations is not None:
            filters.append("p.citation_count >= :min_citations")
            params["min_citations"] = min_citations

        if since_date:
            filters.append("p.published_date >= :since_date")
            params["since_date"] = since_date

        filter_clause = " AND ".join(filters) if filters else "TRUE"

        query = f"""
        WITH target AS (
            SELECT embedding, category, published_date
            FROM papers
            WHERE id = :paper_id
        )
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.category,
            p.published_date,
            p.citation_count,
            p.ai_analysis->>'impactScore' as impact_score,
            p.code_repos->>'officialRepo' as has_code,
            -- Cosine similarity (1 = identical, 0 = orthogonal)
            1 - (p.embedding <=> target.embedding) as similarity_score
        FROM papers p, target
        WHERE
            p.id != :paper_id
            AND {filter_clause}
            -- Early filtering with vector ops
            AND (p.embedding <=> target.embedding) < (1 - {min_similarity})
        ORDER BY p.embedding <=> target.embedding
        LIMIT :limit;
        """

        db = await get_db()
        results = await db.fetch_all(query, params)

        return [dict(row) for row in results]

    async def find_similar_by_text(
        self,
        query_text: str,
        limit: int = 20
    ) -> List[dict]:
        """
        Find papers similar to arbitrary text
        (for when user doesn't have a specific paper)
        """
        from app.services.embedding_service import embedding_service

        # Generate embedding for query text
        query_embedding = await embedding_service.embed_text(query_text)

        query = """
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.category,
            p.citation_count,
            1 - (p.embedding <=> :query_embedding::vector) as similarity_score
        FROM papers p
        WHERE (p.embedding <=> :query_embedding::vector) < 0.3
        ORDER BY p.embedding <=> :query_embedding::vector
        LIMIT :limit;
        """

        db = await get_db()
        results = await db.fetch_all(
            query,
            {"query_embedding": query_embedding, "limit": limit}
        )

        return [dict(row) for row in results]
```

### Query 2: Concept-based Similarity

**Use Case**: "Papers with similar research ideas to Transformers"

```python
# backend/app/services/concept_service.py

class ConceptService:
    """Find papers through shared concepts"""

    async def find_papers_by_similar_concepts(
        self,
        paper_id: str,
        limit: int = 20,
        min_shared_concepts: int = 2
    ) -> List[dict]:
        """
        Find papers that share concepts with target paper

        Performance: ~15-30ms
        """

        query = """
        WITH target_concepts AS (
            -- Get concepts from target paper
            SELECT
                pc.concept_id,
                pc.relevance,
                c.name as concept_name
            FROM paper_concepts pc
            JOIN concepts c ON pc.concept_id = c.id
            WHERE pc.paper_id = :paper_id
        )
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.category,
            p.citation_count,
            -- Weighted concept overlap score
            SUM(pc.relevance * tc.relevance) as concept_similarity,
            -- Number of shared concepts
            COUNT(DISTINCT pc.concept_id) as shared_concept_count,
            -- List of shared concepts (for display)
            ARRAY_AGG(DISTINCT tc.concept_name) as shared_concepts
        FROM papers p
        JOIN paper_concepts pc ON p.id = pc.paper_id
        JOIN target_concepts tc ON pc.concept_id = tc.concept_id
        WHERE
            p.id != :paper_id
            AND pc.relevance > 0.3  -- Only strong relevance
        GROUP BY p.id, p.title, p.abstract, p.category, p.citation_count
        HAVING COUNT(DISTINCT pc.concept_id) >= :min_shared_concepts
        ORDER BY concept_similarity DESC, p.citation_count DESC
        LIMIT :limit;
        """

        db = await get_db()
        results = await db.fetch_all(
            query,
            {
                "paper_id": paper_id,
                "min_shared_concepts": min_shared_concepts,
                "limit": limit
            }
        )

        return [dict(row) for row in results]

    async def get_papers_by_concept(
        self,
        concept_name: str,
        limit: int = 50,
        sort_by: str = "relevance"  # "relevance", "citations", "recent"
    ) -> List[dict]:
        """
        Get all papers tagged with a concept

        Performance: ~10ms
        """

        sort_clause = {
            "relevance": "pc.relevance DESC, p.citation_count DESC",
            "citations": "p.citation_count DESC, pc.relevance DESC",
            "recent": "p.published_date DESC, pc.relevance DESC"
        }.get(sort_by, "pc.relevance DESC")

        query = f"""
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.category,
            p.published_date,
            p.citation_count,
            pc.relevance,
            c.name as concept_name
        FROM papers p
        JOIN paper_concepts pc ON p.id = pc.paper_id
        JOIN concepts c ON pc.concept_id = c.id
        WHERE
            c.normalized_name ILIKE :concept_pattern
            AND pc.relevance > 0.5
        ORDER BY {sort_clause}
        LIMIT :limit;
        """

        db = await get_db()
        results = await db.fetch_all(
            query,
            {
                "concept_pattern": f"%{concept_name.lower()}%",
                "limit": limit
            }
        )

        return [dict(row) for row in results]

    async def extract_and_store_concepts(
        self,
        paper_id: str,
        title: str,
        abstract: str
    ) -> List[str]:
        """
        Extract concepts from paper using LLM
        """
        from app.services.ai_analysis_service import ai_analysis_service
        import json

        prompt = f"""Extract key technical concepts from this research paper.

Title: {title}
Abstract: {abstract}

Extract 5-10 concepts that represent:
- Architectures (e.g., "transformer", "CNN")
- Techniques (e.g., "attention mechanisms", "batch normalization")
- Methods (e.g., "contrastive learning", "fine-tuning")
- Datasets (e.g., "ImageNet", "COCO")
- Tasks (e.g., "image classification", "object detection")

Return as JSON: {{"concepts": [{{"name": "...", "category": "...", "relevance": 0.0-1.0}}]}}
"""

        response = await ai_analysis_service.model.generate_content_async(prompt)

        try:
            data = json.loads(response.text.strip())
            concepts_data = data.get("concepts", [])
        except:
            # Fallback: extract from text
            concepts_data = await self._extract_concepts_fallback(title, abstract)

        # Store concepts and relationships
        db = await get_db()

        for concept_data in concepts_data:
            name = concept_data["name"]
            category = concept_data.get("category", "technique")
            relevance = concept_data.get("relevance", 0.8)

            # Insert or get concept
            concept_id = await db.fetch_val("""
                INSERT INTO concepts (name, normalized_name, category)
                VALUES (:name, :normalized_name, :category)
                ON CONFLICT (name) DO UPDATE SET
                    last_seen_date = NOW()
                RETURNING id;
            """, {
                "name": name,
                "normalized_name": name.lower().strip(),
                "category": category
            })

            # Link to paper
            await db.execute("""
                INSERT INTO paper_concepts (paper_id, concept_id, relevance, extraction_method)
                VALUES (:paper_id, :concept_id, :relevance, 'llm')
                ON CONFLICT (paper_id, concept_id) DO UPDATE SET
                    relevance = GREATEST(paper_concepts.relevance, :relevance);
            """, {
                "paper_id": paper_id,
                "concept_id": concept_id,
                "relevance": relevance
            })

        return [c["name"] for c in concepts_data]
```

### Query 3: Citation Lineage

**Use Case**: "What papers led to GPT-4?"

```python
# backend/app/services/citation_service.py

class CitationService:
    """Citation graph operations"""

    async def get_citation_lineage(
        self,
        paper_id: str,
        max_depth: int = 3,
        limit_per_level: int = 50
    ) -> dict:
        """
        Get papers that influenced this paper (ancestors)

        Performance: ~50-100ms for 3 hops
        """

        query = """
        WITH RECURSIVE lineage AS (
            -- Base case: papers directly cited (depth 1)
            SELECT
                c.cited_paper_id as paper_id,
                c.citing_paper_id as influenced,
                1 as depth,
                ARRAY[c.cited_paper_id] as path,
                c.is_influential
            FROM citations c
            WHERE c.citing_paper_id = :paper_id

            UNION

            -- Recursive case: citations of citations
            SELECT
                c.cited_paper_id,
                c.citing_paper_id,
                l.depth + 1,
                l.path || c.cited_paper_id,
                c.is_influential
            FROM citations c
            JOIN lineage l ON c.citing_paper_id = l.paper_id
            WHERE
                l.depth < :max_depth
                -- Prevent cycles
                AND NOT (c.cited_paper_id = ANY(l.path))
        )
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.published_date,
            p.citation_count,
            l.depth,
            l.influenced as cited_by,
            l.is_influential,
            -- Count how many paths lead to this paper (influence score)
            COUNT(*) OVER (PARTITION BY p.id) as path_count
        FROM lineage l
        JOIN papers p ON l.paper_id = p.id
        ORDER BY
            l.depth ASC,
            l.is_influential DESC,
            p.citation_count DESC
        LIMIT :total_limit;
        """

        db = await get_db()
        results = await db.fetch_all(
            query,
            {
                "paper_id": paper_id,
                "max_depth": max_depth,
                "total_limit": limit_per_level * max_depth
            }
        )

        # Group by depth
        lineage_by_depth = {}
        for row in results:
            depth = row["depth"]
            if depth not in lineage_by_depth:
                lineage_by_depth[depth] = []
            lineage_by_depth[depth].append(dict(row))

        return {
            "paper_id": paper_id,
            "max_depth": max_depth,
            "lineage": lineage_by_depth,
            "total_ancestors": len(results)
        }

    async def get_citation_descendants(
        self,
        paper_id: str,
        max_depth: int = 2,
        limit: int = 100
    ) -> dict:
        """
        Get papers that built upon this paper (descendants)

        Similar recursive query but reversed direction
        """

        query = """
        WITH RECURSIVE descendants AS (
            SELECT
                c.citing_paper_id as paper_id,
                c.cited_paper_id as builds_on,
                1 as depth,
                ARRAY[c.citing_paper_id] as path
            FROM citations c
            WHERE c.cited_paper_id = :paper_id

            UNION

            SELECT
                c.citing_paper_id,
                c.cited_paper_id,
                d.depth + 1,
                d.path || c.citing_paper_id
            FROM citations c
            JOIN descendants d ON c.cited_paper_id = d.paper_id
            WHERE
                d.depth < :max_depth
                AND NOT (c.citing_paper_id = ANY(d.path))
        )
        SELECT
            p.id,
            p.title,
            p.published_date,
            p.citation_count,
            d.depth
        FROM descendants d
        JOIN papers p ON d.paper_id = p.id
        ORDER BY d.depth ASC, p.citation_count DESC
        LIMIT :limit;
        """

        db = await get_db()
        results = await db.fetch_all(
            query,
            {"paper_id": paper_id, "max_depth": max_depth, "limit": limit}
        )

        return {
            "paper_id": paper_id,
            "descendants": [dict(row) for row in results]
        }

    async def get_co_citations(
        self,
        paper_id: str,
        limit: int = 20
    ) -> List[dict]:
        """
        Find papers frequently co-cited with this paper
        (papers cited together suggest similarity)

        Performance: ~30ms
        """

        query = """
        WITH paper_citations AS (
            -- Papers that cite our target paper
            SELECT citing_paper_id
            FROM citations
            WHERE cited_paper_id = :paper_id
        )
        SELECT
            p.id,
            p.title,
            p.citation_count,
            -- How many papers cite both our target and this paper
            COUNT(DISTINCT pc.citing_paper_id) as co_citation_count
        FROM citations c
        JOIN paper_citations pc ON c.citing_paper_id = pc.citing_paper_id
        JOIN papers p ON c.cited_paper_id = p.id
        WHERE
            c.cited_paper_id != :paper_id
        GROUP BY p.id, p.title, p.citation_count
        HAVING COUNT(DISTINCT pc.citing_paper_id) >= 3
        ORDER BY co_citation_count DESC, p.citation_count DESC
        LIMIT :limit;
        """

        db = await get_db()
        results = await db.fetch_all(query, {"paper_id": paper_id, "limit": limit})

        return [dict(row) for row in results]
```

### Query 4: Latest in Domain

**Use Case**: "Recent advances in diffusion models"

```python
# backend/app/services/domain_service.py

class DomainService:
    """Domain/topic exploration"""

    async def get_latest_in_domain(
        self,
        domain: str,  # "transformers", "diffusion models", etc.
        days: int = 180,
        limit: int = 50,
        min_quality: float = 5.0
    ) -> List[dict]:
        """
        Get recent papers in a specific domain/topic

        Performance: ~10-20ms with proper indexes
        """

        query = """
        SELECT DISTINCT
            p.id,
            p.title,
            p.abstract,
            p.published_date,
            p.category,
            p.citation_count,
            p.quality_score,
            p.ai_analysis->>'impactScore' as impact_score,
            -- List concepts matched
            ARRAY_AGG(DISTINCT c.name) as matched_concepts
        FROM papers p
        JOIN paper_concepts pc ON p.id = pc.paper_id
        JOIN concepts c ON pc.concept_id = c.id
        WHERE
            -- Fuzzy match on concept name
            c.normalized_name ILIKE :domain_pattern
            -- Recent papers only
            AND p.published_date > NOW() - INTERVAL '1 day' * :days
            -- Strong relevance to concept
            AND pc.relevance > 0.5
            -- Quality filter
            AND p.quality_score >= :min_quality
        GROUP BY p.id, p.title, p.abstract, p.published_date, p.category,
                 p.citation_count, p.quality_score, p.ai_analysis
        ORDER BY
            p.published_date DESC,
            p.citation_count DESC
        LIMIT :limit;
        """

        db = await get_db()
        results = await db.fetch_all(
            query,
            {
                "domain_pattern": f"%{domain.lower()}%",
                "days": days,
                "min_quality": min_quality,
                "limit": limit
            }
        )

        return [dict(row) for row in results]

    async def get_trending_concepts(
        self,
        category: Optional[str] = None,
        days: int = 90,
        limit: int = 20
    ) -> List[dict]:
        """
        Find trending concepts (lots of recent papers)

        Performance: ~15ms
        """

        category_filter = "AND p.category = :category" if category else ""

        query = f"""
        SELECT
            c.id,
            c.name,
            c.category,
            COUNT(DISTINCT p.id) as recent_paper_count,
            c.paper_count as total_paper_count,
            -- Growth rate
            COUNT(DISTINCT p.id)::FLOAT / NULLIF(c.paper_count, 0) as growth_rate,
            -- Sample recent papers
            ARRAY_AGG(p.title ORDER BY p.published_date DESC)
                FILTER (WHERE p.published_date > NOW() - INTERVAL '30 days')
                [:5] as recent_papers
        FROM concepts c
        JOIN paper_concepts pc ON c.id = pc.concept_id
        JOIN papers p ON pc.paper_id = p.id
        WHERE
            p.published_date > NOW() - INTERVAL '1 day' * :days
            {category_filter}
        GROUP BY c.id, c.name, c.category, c.paper_count
        HAVING COUNT(DISTINCT p.id) >= 5  -- At least 5 recent papers
        ORDER BY growth_rate DESC, recent_paper_count DESC
        LIMIT :limit;
        """

        params = {"days": days, "limit": limit}
        if category:
            params["category"] = category

        db = await get_db()
        results = await db.fetch_all(query, params)

        return [dict(row) for row in results]
```

### Query 5: Performance Benchmarks

**Use Case**: "Best models for ImageNet classification"

```python
# backend/app/services/benchmark_service.py

class BenchmarkService:
    """Performance benchmark queries"""

    async def get_leaderboard(
        self,
        task: str,
        dataset: str,
        metric: str = "accuracy",
        min_date: Optional[str] = None,
        limit: int = 50
    ) -> List[dict]:
        """
        Get leaderboard for a specific task/dataset

        Performance: ~5-10ms with index
        """

        date_filter = "AND p.published_date > :min_date" if min_date else ""

        query = f"""
        SELECT
            p.id,
            p.title,
            p.published_date,
            p.citation_count,
            b.model_name,
            b.model_size,
            b.value as score,
            b.compute_cost,
            b.metadata,
            p.code_repos->>'officialRepo' as code_url,
            -- Rank within this leaderboard
            RANK() OVER (ORDER BY b.value DESC) as rank
        FROM benchmarks b
        JOIN papers p ON b.paper_id = p.id
        WHERE
            b.task = :task
            AND b.dataset = :dataset
            AND b.metric = :metric
            {date_filter}
        ORDER BY b.value DESC
        LIMIT :limit;
        """

        params = {
            "task": task,
            "dataset": dataset,
            "metric": metric,
            "limit": limit
        }
        if min_date:
            params["min_date"] = min_date

        db = await get_db()
        results = await db.fetch_all(query, params)

        return [dict(row) for row in results]

    async def get_paper_benchmarks(
        self,
        paper_id: str
    ) -> List[dict]:
        """
        Get all benchmarks reported in a paper
        """

        query = """
        SELECT
            b.task,
            b.dataset,
            b.metric,
            b.value,
            b.model_name,
            b.model_size,
            b.compute_cost,
            b.metadata,
            -- How this compares to SOTA
            (
                SELECT MAX(value)
                FROM benchmarks
                WHERE task = b.task AND dataset = b.dataset AND metric = b.metric
            ) as sota_value,
            b.value::FLOAT / (
                SELECT MAX(value)
                FROM benchmarks
                WHERE task = b.task AND dataset = b.dataset AND metric = b.metric
            ) as sota_ratio
        FROM benchmarks b
        WHERE b.paper_id = :paper_id
        ORDER BY b.task, b.dataset, b.metric;
        """

        db = await get_db()
        results = await db.fetch_all(query, {"paper_id": paper_id})

        return [dict(row) for row in results]

    async def compare_approaches(
        self,
        task: str,
        dataset: str,
        paper_ids: List[str]
    ) -> dict:
        """
        Compare specific papers on a benchmark
        """

        query = """
        SELECT
            p.id,
            p.title,
            b.metric,
            b.value,
            b.model_name
        FROM benchmarks b
        JOIN papers p ON b.paper_id = p.id
        WHERE
            b.task = :task
            AND b.dataset = :dataset
            AND p.id = ANY(:paper_ids)
        ORDER BY b.metric, b.value DESC;
        """

        db = await get_db()
        results = await db.fetch_all(
            query,
            {"task": task, "dataset": dataset, "paper_ids": paper_ids}
        )

        # Group by metric
        by_metric = {}
        for row in results:
            metric = row["metric"]
            if metric not in by_metric:
                by_metric[metric] = []
            by_metric[metric].append(dict(row))

        return {
            "task": task,
            "dataset": dataset,
            "comparison": by_metric
        }
```

---

## 📡 API Endpoints

```python
# backend/app/api/v1/endpoints/knowledge_graph.py

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.similarity_service import similarity_service
from app.services.concept_service import concept_service
from app.services.citation_service import citation_service
from app.services.domain_service import domain_service
from app.services.benchmark_service import benchmark_service

router = APIRouter(prefix="/knowledge", tags=["knowledge-graph"])

# ================================================================
# SIMILARITY ENDPOINTS
# ================================================================

@router.get("/{paper_id}/similar")
async def get_similar_papers(
    paper_id: str,
    limit: int = Query(20, ge=1, le=100),
    min_similarity: float = Query(0.7, ge=0.0, le=1.0),
    category: Optional[str] = None,
    min_citations: Optional[int] = None
):
    """Find papers semantically similar to this one"""

    results = await similarity_service.find_similar_papers(
        paper_id=paper_id,
        limit=limit,
        min_similarity=min_similarity,
        category_filter=category,
        min_citations=min_citations
    )

    return {
        "paper_id": paper_id,
        "similar_papers": results,
        "count": len(results)
    }

@router.get("/{paper_id}/similar-concepts")
async def get_similar_by_concepts(
    paper_id: str,
    limit: int = Query(20, ge=1, le=100),
    min_shared: int = Query(2, ge=1, le=10)
):
    """Find papers with similar research concepts"""

    results = await concept_service.find_papers_by_similar_concepts(
        paper_id=paper_id,
        limit=limit,
        min_shared_concepts=min_shared
    )

    return {
        "paper_id": paper_id,
        "concept_similar_papers": results,
        "count": len(results)
    }

# ================================================================
# CITATION GRAPH ENDPOINTS
# ================================================================

@router.get("/{paper_id}/lineage")
async def get_lineage(
    paper_id: str,
    max_depth: int = Query(3, ge=1, le=5),
    limit_per_level: int = Query(50, ge=1, le=100)
):
    """Get papers that influenced this paper (ancestors)"""

    lineage = await citation_service.get_citation_lineage(
        paper_id=paper_id,
        max_depth=max_depth,
        limit_per_level=limit_per_level
    )

    return lineage

@router.get("/{paper_id}/descendants")
async def get_descendants(
    paper_id: str,
    max_depth: int = Query(2, ge=1, le=4),
    limit: int = Query(100, ge=1, le=200)
):
    """Get papers that built upon this paper"""

    descendants = await citation_service.get_citation_descendants(
        paper_id=paper_id,
        max_depth=max_depth,
        limit=limit
    )

    return descendants

@router.get("/{paper_id}/co-citations")
async def get_co_citations(
    paper_id: str,
    limit: int = Query(20, ge=1, le=50)
):
    """Find papers frequently co-cited with this paper"""

    results = await citation_service.get_co_citations(
        paper_id=paper_id,
        limit=limit
    )

    return {
        "paper_id": paper_id,
        "co_cited_papers": results
    }

# ================================================================
# CONCEPT/DOMAIN ENDPOINTS
# ================================================================

@router.get("/concepts/{concept_name}/papers")
async def get_papers_by_concept(
    concept_name: str,
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("relevance", regex="^(relevance|citations|recent)$")
):
    """Get papers tagged with this concept"""

    results = await concept_service.get_papers_by_concept(
        concept_name=concept_name,
        limit=limit,
        sort_by=sort_by
    )

    return {
        "concept": concept_name,
        "papers": results,
        "count": len(results)
    }

@router.get("/domain/{domain}/latest")
async def get_latest_in_domain(
    domain: str,
    days: int = Query(180, ge=1, le=730),
    limit: int = Query(50, ge=1, le=200),
    min_quality: float = Query(5.0, ge=0.0, le=10.0)
):
    """Get recent papers in a research domain"""

    results = await domain_service.get_latest_in_domain(
        domain=domain,
        days=days,
        limit=limit,
        min_quality=min_quality
    )

    return {
        "domain": domain,
        "time_range_days": days,
        "papers": results,
        "count": len(results)
    }

@router.get("/concepts/trending")
async def get_trending_concepts(
    category: Optional[str] = None,
    days: int = Query(90, ge=30, le=365),
    limit: int = Query(20, ge=1, le=50)
):
    """Find trending research concepts"""

    results = await domain_service.get_trending_concepts(
        category=category,
        days=days,
        limit=limit
    )

    return {
        "trending_concepts": results,
        "time_range_days": days
    }

# ================================================================
# BENCHMARK ENDPOINTS
# ================================================================

@router.get("/benchmarks/leaderboard")
async def get_benchmark_leaderboard(
    task: str = Query(..., description="e.g., 'image_classification'"),
    dataset: str = Query(..., description="e.g., 'ImageNet'"),
    metric: str = Query("accuracy", description="e.g., 'accuracy', 'f1'"),
    min_date: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Get leaderboard for a benchmark task"""

    results = await benchmark_service.get_leaderboard(
        task=task,
        dataset=dataset,
        metric=metric,
        min_date=min_date,
        limit=limit
    )

    return {
        "task": task,
        "dataset": dataset,
        "metric": metric,
        "leaderboard": results
    }

@router.get("/{paper_id}/benchmarks")
async def get_paper_benchmarks(paper_id: str):
    """Get all benchmarks reported in a paper"""

    results = await benchmark_service.get_paper_benchmarks(paper_id)

    return {
        "paper_id": paper_id,
        "benchmarks": results
    }

@router.post("/benchmarks/compare")
async def compare_papers(
    task: str,
    dataset: str,
    paper_ids: List[str]
):
    """Compare multiple papers on a benchmark"""

    comparison = await benchmark_service.compare_approaches(
        task=task,
        dataset=dataset,
        paper_ids=paper_ids
    )

    return comparison
```

---

## 🎨 Frontend Components

### Similar Papers Component

```tsx
// src/components/SimilarPapers.tsx

import React, { useEffect, useState } from 'react';

interface SimilarPapersProps {
  paperId: string;
}

export default function SimilarPapers({ paperId }: SimilarPapersProps) {
  const [similar, setSimilar] = useState([]);
  const [conceptSimilar, setConceptSimilar] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSimilar() {
      // Load both types in parallel
      const [semanticRes, conceptRes] = await Promise.all([
        fetch(`/api/v1/knowledge/${paperId}/similar?limit=10`),
        fetch(`/api/v1/knowledge/${paperId}/similar-concepts?limit=10`)
      ]);

      const semanticData = await semanticRes.json();
      const conceptData = await conceptRes.json();

      setSimilar(semanticData.similar_papers);
      setConceptSimilar(conceptData.concept_similar_papers);
      setLoading(false);
    }

    loadSimilar();
  }, [paperId]);

  if (loading) return <div>Loading similar papers...</div>;

  return (
    <div className="similar-papers">
      <h3>Papers Like This</h3>

      {/* Semantic similarity */}
      <section>
        <h4>📊 Semantically Similar</h4>
        <p className="text-muted">Based on content and methodology</p>
        {similar.map(paper => (
          <PaperCard
            key={paper.id}
            paper={paper}
            badge={`${(paper.similarity_score * 100).toFixed(0)}% similar`}
          />
        ))}
      </section>

      {/* Concept similarity */}
      <section>
        <h4>🔬 Similar Research Ideas</h4>
        <p className="text-muted">Shared concepts: {conceptSimilar[0]?.shared_concepts.join(', ')}</p>
        {conceptSimilar.map(paper => (
          <PaperCard
            key={paper.id}
            paper={paper}
            badge={`${paper.shared_concept_count} shared concepts`}
          />
        ))}
      </section>
    </div>
  );
}
```

### Citation Graph Component

```tsx
// src/components/CitationGraph.tsx

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface CitationGraphProps {
  paperId: string;
  maxDepth?: number;
}

export default function CitationGraph({ paperId, maxDepth = 3 }: CitationGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    async function loadGraph() {
      const res = await fetch(`/api/v1/knowledge/${paperId}/lineage?max_depth=${maxDepth}`);
      const graphData = await res.json();
      setData(graphData);
    }

    loadGraph();
  }, [paperId, maxDepth]);

  useEffect(() => {
    if (!data || !svgRef.current) return;

    // D3.js force-directed graph
    const svg = d3.select(svgRef.current);
    const width = 800;
    const height = 600;

    // Convert lineage data to nodes and links
    const nodes = [];
    const links = [];

    // Target paper at center
    nodes.push({ id: paperId, depth: 0, type: 'target' });

    // Add ancestor papers
    Object.entries(data.lineage).forEach(([depth, papers]) => {
      papers.forEach(paper => {
        nodes.push({
          id: paper.id,
          title: paper.title,
          depth: parseInt(depth),
          type: 'ancestor',
          citations: paper.citation_count
        });

        links.push({
          source: paper.id,
          target: paper.cited_by || paperId
        });
      });
    });

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Draw links
    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // Draw nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', d => d.type === 'target' ? 10 : 5 + Math.log(d.citations + 1))
      .attr('fill', d => {
        if (d.type === 'target') return '#ff6b6b';
        return d3.interpolateBlues(0.3 + (d.depth / maxDepth) * 0.6);
      })
      .call(drag(simulation));

    // Add labels on hover
    node.append('title')
      .text(d => d.title || d.id);

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    });

    function drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }
  }, [data]);

  return (
    <div className="citation-graph">
      <h3>Citation Lineage</h3>
      <p className="text-muted">Papers that influenced this research</p>
      <svg ref={svgRef} width="800" height="600" />
    </div>
  );
}
```

### Benchmark Leaderboard

```tsx
// src/components/BenchmarkLeaderboard.tsx

import React, { useEffect, useState } from 'react';

interface LeaderboardProps {
  task: string;
  dataset: string;
  metric?: string;
}

export default function BenchmarkLeaderboard({
  task,
  dataset,
  metric = 'accuracy'
}: LeaderboardProps) {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadLeaderboard() {
      const res = await fetch(
        `/api/v1/knowledge/benchmarks/leaderboard?task=${task}&dataset=${dataset}&metric=${metric}`
      );
      const data = await res.json();
      setLeaderboard(data.leaderboard);
      setLoading(false);
    }

    loadLeaderboard();
  }, [task, dataset, metric]);

  if (loading) return <div>Loading leaderboard...</div>;

  return (
    <div className="benchmark-leaderboard">
      <h3>🏆 {task} on {dataset}</h3>
      <p className="text-muted">Ranked by {metric}</p>

      <table className="table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Paper</th>
            <th>Model</th>
            <th>{metric}</th>
            <th>Year</th>
            <th>Code</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((entry, idx) => (
            <tr key={entry.id}>
              <td>
                <span className={`rank-badge rank-${idx + 1}`}>
                  #{entry.rank}
                </span>
              </td>
              <td>
                <a href={`/papers/${entry.id}`}>{entry.title}</a>
              </td>
              <td>
                <code>{entry.model_name}</code>
                {entry.model_size && <small> ({entry.model_size})</small>}
              </td>
              <td>
                <strong>{entry.score.toFixed(2)}%</strong>
              </td>
              <td>{new Date(entry.published_date).getFullYear()}</td>
              <td>
                {entry.code_url ? (
                  <a href={entry.code_url} target="_blank">
                    <i className="bi bi-github" />
                  </a>
                ) : (
                  <span className="text-muted">-</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 🚀 Data Ingestion Pipeline

### Continuous Ingestion Service

```python
# backend/app/services/ingestion_service.py

import asyncio
from datetime import datetime, timedelta
from typing import List
from app.db.database import get_db
from app.services.arxiv_service import arxiv_service
from app.services.ai_analysis_service import ai_analysis_service
from app.services.embedding_service import embedding_service
from app.services.concept_service import concept_service
from app.services.code_detection_service import code_detection_service

class IngestionService:
    """Continuously ingest papers from arXiv into our database"""

    async def ingest_new_papers(
        self,
        categories: List[str] = ['cs.AI', 'cs.LG', 'cs.CV', 'cs.CL', 'cs.NE'],
        days_lookback: int = 7
    ):
        """
        Ingest recent papers from arXiv

        Run this daily as a cron job
        """

        print(f"🔄 Starting ingestion for categories: {categories}")

        since_date = datetime.now() - timedelta(days=days_lookback)

        for category in categories:
            print(f"\n📚 Processing category: {category}")

            # Fetch papers from arXiv
            papers = await arxiv_service.get_recent_papers(
                category=category,
                max_results=100  # Per category
            )

            print(f"   Found {len(papers)} papers")

            for paper in papers:
                try:
                    await self._ingest_single_paper(paper)
                except Exception as e:
                    print(f"   ❌ Failed to ingest {paper.get('id')}: {e}")
                    continue

            # Rate limiting
            await asyncio.sleep(2)

        print(f"\n✅ Ingestion complete")

    async def _ingest_single_paper(self, paper_data: dict):
        """
        Ingest a single paper with all enrichments
        """
        paper_id = paper_data['id']

        db = await get_db()

        # Check if already exists
        existing = await db.fetch_one(
            "SELECT id FROM papers WHERE id = :id",
            {"id": paper_id}
        )

        if existing:
            print(f"   ⏭️  Skipping {paper_id} (already exists)")
            return

        print(f"   📄 Ingesting {paper_id}")

        # Parallel enrichment
        title = paper_data['title']
        abstract = paper_data['summary']
        authors = paper_data.get('authors', [])

        # Run enrichments in parallel
        results = await asyncio.gather(
            # 1. Generate embedding
            embedding_service.embed_text(f"{title}\n\n{abstract}"),

            # 2. AI analysis
            ai_analysis_service.generate_comprehensive_analysis(
                abstract, title, authors, paper_id
            ),

            # 3. Code detection
            code_detection_service.find_code_repos(title, abstract, authors),

            # 4. Extract concepts
            concept_service.extract_and_store_concepts(paper_id, title, abstract),

            return_exceptions=True
        )

        embedding, ai_analysis, code_repos, concepts = results

        # Store paper
        await db.execute("""
            INSERT INTO papers (
                id, title, abstract, authors, published_date, category,
                embedding, ai_analysis, code_repos, concepts_array,
                quality_score, citation_count
            ) VALUES (
                :id, :title, :abstract, :authors, :published_date, :category,
                :embedding, :ai_analysis, :code_repos, :concepts_array,
                :quality_score, 0
            )
        """, {
            "id": paper_id,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "published_date": paper_data['published'],
            "category": paper_data.get('category', 'cs.AI'),
            "embedding": embedding if not isinstance(embedding, Exception) else None,
            "ai_analysis": ai_analysis if not isinstance(ai_analysis, Exception) else {},
            "code_repos": code_repos if not isinstance(code_repos, Exception) else {},
            "concepts_array": concepts if not isinstance(concepts, Exception) else [],
            "quality_score": self._compute_quality_score(ai_analysis)
        })

        print(f"   ✅ Ingested {paper_id}")

    def _compute_quality_score(self, ai_analysis: dict) -> float:
        """
        Compute paper quality score 0-10

        Factors:
        - Impact score from AI
        - Research significance
        - Implementation complexity
        """
        if isinstance(ai_analysis, Exception) or not ai_analysis:
            return 5.0  # Default

        impact = ai_analysis.get('impactScore', 5)
        significance = {
            'breakthrough': 10,
            'significant': 7,
            'incremental': 4
        }.get(ai_analysis.get('researchSignificance'), 5)

        # Weighted average
        score = (impact * 0.6 + significance * 0.4)

        return round(score, 2)

    async def backfill_citations(self, batch_size: int = 1000):
        """
        Backfill citation data from Semantic Scholar

        Run this periodically to update citation counts and graph
        """
        import requests

        print("🔄 Starting citation backfill")

        db = await get_db()

        # Get papers without citation data
        papers = await db.fetch_all("""
            SELECT id FROM papers
            WHERE citation_count = 0
            LIMIT :batch_size
        """, {"batch_size": batch_size})

        for paper in papers:
            arxiv_id = paper['id']

            try:
                # Fetch from Semantic Scholar
                response = requests.get(
                    f"https://api.semanticscholar.org/v1/paper/arXiv:{arxiv_id}",
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()

                    # Update citation count
                    await db.execute("""
                        UPDATE papers
                        SET citation_count = :count,
                            influential_citation_count = :influential_count
                        WHERE id = :id
                    """, {
                        "id": arxiv_id,
                        "count": len(data.get('citations', [])),
                        "influential_count": data.get('influentialCitationCount', 0)
                    })

                    # Store citation edges
                    for citation in data.get('citations', []):
                        cited_arxiv_id = citation.get('arxivId')
                        if cited_arxiv_id:
                            await db.execute("""
                                INSERT INTO citations (citing_paper_id, cited_paper_id, is_influential)
                                VALUES (:citing, :cited, :influential)
                                ON CONFLICT DO NOTHING
                            """, {
                                "citing": arxiv_id,
                                "cited": cited_arxiv_id,
                                "influential": citation.get('isInfluential', False)
                            })

                # Rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                print(f"   Failed to fetch citations for {arxiv_id}: {e}")
                continue

        print("✅ Citation backfill complete")
```

### Cron Job Setup

```python
# backend/cron_jobs.py

import asyncio
from app.services.ingestion_service import ingestion_service

async def daily_ingestion():
    """Run daily to ingest new papers"""
    await ingestion_service.ingest_new_papers(
        categories=['cs.AI', 'cs.LG', 'cs.CV', 'cs.CL', 'cs.NE', 'cs.RO'],
        days_lookback=7
    )

async def weekly_citation_update():
    """Run weekly to update citations"""
    await ingestion_service.backfill_citations(batch_size=5000)

if __name__ == "__main__":
    # Run daily ingestion
    asyncio.run(daily_ingestion())
```

Add to crontab:
```bash
# Daily at 2 AM: Ingest new papers
0 2 * * * cd /path/to/backend && python cron_jobs.py daily

# Weekly on Sunday at 3 AM: Update citations
0 3 * * 0 cd /path/to/backend && python cron_jobs.py weekly
```

---

## 📈 Performance Optimization

### 1. Connection Pooling

```python
# backend/app/db/database.py

from databases import Database
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Connection pool for async queries
database = Database(
    DATABASE_URL,
    min_size=5,
    max_size=20
)

async def get_db():
    return database
```

### 2. Query Result Caching

```python
# backend/app/services/cache_service.py

import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_result(ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and args
            cache_key = f"{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs)}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=1800)  # Cache for 30 minutes
async def get_similar_papers(paper_id: str):
    ...
```

### 3. Database Query Optimization

```sql
-- Regular VACUUM and ANALYZE
VACUUM ANALYZE papers;
VACUUM ANALYZE citations;
VACUUM ANALYZE paper_concepts;

-- Update statistics
ANALYZE papers;
ANALYZE citations;

-- Check index usage
SELECT
    schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Find missing indexes
SELECT
    schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY abs(correlation) DESC;
```

### 4. Materialized Views for Hot Queries

```sql
-- Pre-compute popular paper relationships
CREATE MATERIALIZED VIEW popular_paper_relationships AS
SELECT
    p1.id as paper_a,
    p2.id as paper_b,
    1 - (p1.embedding <=> p2.embedding) as similarity,
    (
        SELECT COUNT(*)
        FROM paper_concepts pc1
        JOIN paper_concepts pc2 ON pc1.concept_id = pc2.concept_id
        WHERE pc1.paper_id = p1.id AND pc2.paper_id = p2.id
    ) as shared_concepts
FROM papers p1
CROSS JOIN papers p2
WHERE
    p1.id < p2.id
    AND p1.citation_count > 100  -- Only popular papers
    AND p2.citation_count > 100
    AND (p1.embedding <=> p2.embedding) < 0.3  -- Only similar
;

CREATE INDEX ON popular_paper_relationships(paper_a);
CREATE INDEX ON popular_paper_relationships(paper_b);

-- Refresh daily
REFRESH MATERIALIZED VIEW CONCURRENTLY popular_paper_relationships;
```

---

## 🚢 Deployment

### Using Supabase (Easiest)

1. **Create Supabase project** (free tier)
2. **Enable pgvector extension**:
   ```sql
   CREATE EXTENSION vector;
   ```

3. **Run schema** from above

4. **Connect from FastAPI**:
   ```python
   DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
   ```

### Self-Hosted PostgreSQL

```bash
# Install PostgreSQL 15+
sudo apt-get install postgresql-15

# Install pgvector
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Enable in database
psql -d your_database -c "CREATE EXTENSION vector;"
```

### Scaling

**For 1M papers:**
- Single Postgres instance (4 CPUs, 16GB RAM)
- pgvector handles well

**For 10M+ papers:**
- Read replicas for query load
- Partition papers table by year
- Separate vector DB (Pinecone/Weaviate)

---

## 📊 Monitoring

```python
# backend/app/api/v1/endpoints/monitoring.py

@router.get("/stats")
async def get_system_stats():
    """System statistics"""
    db = await get_db()

    stats = await db.fetch_one("""
        SELECT
            (SELECT COUNT(*) FROM papers) as total_papers,
            (SELECT COUNT(*) FROM concepts) as total_concepts,
            (SELECT COUNT(*) FROM citations) as total_citations,
            (SELECT COUNT(*) FROM benchmarks) as total_benchmarks,
            (SELECT MAX(published_date) FROM papers) as latest_paper_date,
            (SELECT AVG(citation_count) FROM papers) as avg_citations
    """)

    return dict(stats)
```

---

## ✅ Implementation Checklist

**Phase 1: Database (Week 1)**
- [ ] Set up PostgreSQL with pgvector
- [ ] Create schema (tables + indexes)
- [ ] Create triggers
- [ ] Test query performance

**Phase 2: Services (Week 2)**
- [ ] Embedding service
- [ ] Similarity service
- [ ] Citation service
- [ ] Concept service
- [ ] Domain service
- [ ] Benchmark service

**Phase 3: Ingestion (Week 2)**
- [ ] Ingestion service
- [ ] Citation backfill
- [ ] Cron jobs

**Phase 4: API (Week 3)**
- [ ] Knowledge graph endpoints
- [ ] Test all 5 query types
- [ ] Add caching

**Phase 5: Frontend (Week 3-4)**
- [ ] Similar papers component
- [ ] Citation graph visualization
- [ ] Benchmark leaderboard
- [ ] Concept explorer
- [ ] Integrate into existing UI

**Phase 6: Optimization (Week 4)**
- [ ] Add Redis caching
- [ ] Query optimization
- [ ] Materialized views
- [ ] Monitoring

---

## 🎯 Expected Performance

| Query Type | Target | With Optimization |
|------------|--------|-------------------|
| Semantic similarity | <50ms | <20ms (with cache) |
| Concept similarity | <30ms | <10ms (with cache) |
| Citation lineage | <100ms | <50ms |
| Latest in domain | <20ms | <5ms (with cache) |
| Benchmark ranking | <15ms | <5ms |

**Database size estimates:**
- 1M papers: ~10GB (with embeddings)
- 10M citations: ~1GB
- 50K concepts: ~10MB
- 100K benchmarks: ~50MB

**Total**: ~12GB for 1M papers

---

**This implementation gives you the fastest paper exploration system possible with a single database. Ready to build it?**
