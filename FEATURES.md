# AI Papers Research Agent - Complete Feature Documentation

A comprehensive AI-powered research paper discovery, analysis, and knowledge management platform.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Backend API Reference](#backend-api-reference)
- [Frontend Pages](#frontend-pages)
- [Database Schema](#database-schema)
- [AI Enrichment Pipeline](#ai-enrichment-pipeline)
- [Backend Services](#backend-services)
- [External Integrations](#external-integrations)
- [Configuration](#configuration)

---

## Overview

This application provides intelligent discovery and analysis of academic research papers, with a focus on AI/ML research. Key capabilities include:

- **Semantic Search**: Find papers by meaning, not just keywords
- **AI-Powered Analysis**: Two-tier enrichment using Google Gemini
- **Discovery Dashboards**: Multiple views for finding relevant research
- **Knowledge Graph**: Paper relationships, concepts, citations
- **Trend Analysis**: Hot topics, rising techniques, emerging areas
- **Reproducibility Tracking**: Code availability and implementation details

---

## Architecture

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI (Python 3.11) |
| **Frontend** | Next.js 14 (TypeScript) |
| **Database** | Supabase PostgreSQL + pgvector |
| **AI Models** | Google Gemini 1.5/2.5, OpenAI Embeddings |
| **Search** | Vector similarity (1536-dim) + Full-text (tsvector) |
| **Scheduling** | APScheduler |
| **Caching** | Redis (optional) / In-memory LRU |

### System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js UI    │────▶│  FastAPI Backend │────▶│    Supabase     │
│   (Port 3000)   │     │   (Port 8000)    │     │   PostgreSQL    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  External Services  │
                    │  - Google Gemini    │
                    │  - OpenAI           │
                    │  - arXiv API        │
                    │  - Semantic Scholar │
                    │  - OpenAlex         │
                    └─────────────────────┘
```

---

## Backend API Reference

Base URL: `/api/v1`

### Papers Endpoints (`/papers`)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/papers/embedding-caches` | GET | List available embedding caches | - |
| `/papers/atlas/papers` | GET | Fetch papers with filtering | `limit`, `category`, `days`, `query` |
| `/papers/atlas/summary` | GET | Atlas dataset statistics | - |
| `/papers/atlas/cache-stats` | GET | Embedding cache performance | - |
| `/papers/similar/{paper_id}` | GET | Find semantically similar papers | `top_k` |
| `/papers/search` | POST | Full-text search | `query`, `limit`, `category` |
| `/papers/contextual-search` | POST | AI-powered contextual discovery | `description`, `top_k`, `days` |

#### Example: Contextual Search
```bash
curl -X POST "http://localhost:8000/api/v1/papers/contextual-search" \
  -H "Content-Type: application/json" \
  -d '{"description": "transformer models for mobile deployment"}'
```

### Code Generation Endpoint

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/papers/{paper_id}/generate-code` | POST | Generate working implementation from paper |

**Multi-Agent Code Generation Pipeline**

This endpoint uses a 5-agent system to generate production-quality code from research papers:

1. **Paper Analyzer** - Extracts core algorithm, key innovations, hyperparameters
2. **Test Designer** - Creates comprehensive test suites (functionality, correctness, edge cases)
3. **Code Generator** - Writes clean, documented implementation
4. **Test Executor** - Runs tests in isolated environment
5. **Debugger** - Iteratively fixes issues based on test failures

**Response includes:**
- `code.main_code` - Complete implementation (PyTorch/TensorFlow)
- `code.config_code` - Hyperparameters from paper
- `code.dependencies` - Required packages with versions
- `tests` - Generated test suite
- `readme` - Documentation with quick start guide

#### Example: Generate Code
```bash
curl -X POST "http://localhost:8000/api/v1/papers/2510.14486v1/generate-code" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": false,
  "generation_time_seconds": 70.3,
  "paper": {
    "id": "2510.14486v1",
    "title": "Semantic representations emerge in biologically inspired ensembles..."
  },
  "code": {
    "main_code": "import torch\nimport torch.nn as nn...",
    "framework": "pytorch",
    "dependencies": ["torch==2.1.0", "numpy==1.24.3"]
  },
  "readme": "# Quick Start Implementation\n..."
}
```

**Note:** Generation takes 60-90 seconds. The `success` field reflects test pass rate.

---

### Discovery Endpoints (`/discovery`)

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/discovery/stats` | GET | Discovery statistics overview | - |
| `/discovery/impact` | GET | High-impact papers (calibrated 1-10) | `min_score`, `max_score`, `category`, `days` |
| `/discovery/tldr` | GET | Executive summary feed | `days`, `limit`, `category` |
| `/discovery/learning-path` | GET | Difficulty-based progressions | `topic`, `category`, `difficulty_level` |
| `/discovery/techniques` | GET | Browse by methodology | `novelty_type`, `category`, `limit` |
| `/discovery/rising` | GET | Papers with accelerating citations | `min_citations`, `min_velocity`, `days` |
| `/discovery/reproducible` | GET | Papers with code & reproducibility | `min_reproducibility`, `code_availability` |
| `/discovery/practical` | GET | Practical use cases | `industry_relevance`, `min_impact` |
| `/discovery/hot-topics` | GET | Trending techniques | `days`, `min_papers`, `min_citations` |

#### Impact Score Distribution
- **9-10**: Groundbreaking (establishes new paradigms)
- **7-8**: Significant (important contributions)
- **5-6**: Solid (useful incremental work)
- **3-4**: Minor (limited novelty)
- **1-2**: Minimal (derivative work)

#### Example: High-Impact Papers
```bash
curl "http://localhost:8000/api/v1/discovery/impact?min_score=8&limit=10"
```

---

### Trends Endpoints (`/trends`)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/trends/hot-topics` | GET | Techniques with accelerating paper counts | `window_days`, `comparison_days`, `top_k` |
| `/trends/rising-techniques` | GET | Consistently growing techniques | `days`, `min_growth_rate` |
| `/trends/active-authors` | GET | Most productive researchers | `days`, `limit` |
| `/trends/emerging-areas` | GET | New research areas gaining traction | `days`, `min_papers` |

---

### Knowledge Graph Endpoints (`/knowledge-graph`)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/knowledge-graph/similar` | GET | Semantic similarity discovery | `paper_id`, `top_k` |
| `/knowledge-graph/concepts` | GET | Concept exploration | `query`, `trending` |
| `/knowledge-graph/citations` | GET | Citation network graphs | `paper_id`, `depth` |
| `/knowledge-graph/latest-research` | GET | Recent papers in category | `category`, `days` |
| `/knowledge-graph/benchmarks` | GET | Benchmark leaderboards | `task`, `dataset` |

---

### Atlas Database Endpoints (`/atlas-db`)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/atlas-db/papers` | GET | Advanced paper filtering | `limit`, `offset`, `category`, `concept`, `query`, `days`, `order_by`, `has_deep_analysis`, `min_impact_score` |
| `/atlas-db/concepts` | GET | Concept lookup | `query`, `limit` |
| `/atlas-db/summary` | GET | Atlas statistics | - |
| `/atlas-db/categories` | GET | Available arXiv categories | - |
| `/atlas-db/techniques` | GET | Technique exploration | `query`, `limit` |
| `/atlas-db/timeline` | GET | Papers over time | `days`, `granularity` |

---

### Enrichment Endpoints (`/enrichment`)

#### Tier 1: Abstract-Based Enrichment

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/enrichment/trigger` | POST | Start background enrichment |
| `/enrichment/trigger-sync` | POST | Synchronous enrichment |
| `/enrichment/status` | GET | Job status |
| `/enrichment/count` | GET | Enrichment statistics |

#### Tier 2: Deep PDF Enrichment

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/enrichment/deep/trigger` | POST | Start PDF-based enrichment |
| `/enrichment/deep/status` | GET | Progress tracking |
| `/enrichment/deep/count` | GET | Deep enrichment stats |
| `/enrichment/deep/paper/{id}` | POST | Enrich single paper |

#### Citation Enrichment

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/enrichment/citations/trigger` | POST | Start citation enrichment |
| `/enrichment/citations/status` | GET | Citation job status |
| `/enrichment/citations/count` | GET | Citation statistics |
| `/enrichment/citations/paper/{id}` | POST | Enrich single paper |

#### Example: Trigger Deep Enrichment
```bash
curl -X POST "http://localhost:8000/api/v1/enrichment/deep/trigger" \
  -H "Content-Type: application/json" \
  -d '{"max_papers": 100, "skip_enriched": true}'
```

---

### Ingestion Endpoints (`/ingestion`)

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/ingestion/trigger` | POST | Background paper ingestion | `categories`, `days`, `max_papers` |
| `/ingestion/trigger-sync` | POST | Synchronous ingestion | Same as above |
| `/ingestion/status` | GET | Service status | - |
| `/ingestion/categories` | GET | Available arXiv categories | - |
| `/ingestion/scheduler` | GET | Scheduled job status | - |

---

### Agent Memory Endpoints (`/agent-memory`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent-memory/stats` | GET | Agent performance statistics |
| `/agent-memory/reflections` | GET | Learning patterns and reflections |
| `/agent-memory/patterns` | GET | Successful processing patterns |
| `/agent-memory/summary` | GET | Memory system overview |

---

## Frontend Pages

### Core Pages

| Route | Description | Key Features |
|-------|-------------|--------------|
| `/` | Home page | Paper feed, contextual search, atlas overview |
| `/atlas-explore` | Atlas exploration | Embedding selector, citation graphs, timeline visualization |
| `/trends` | Trends dashboard | Hot topics, rising techniques, active authors |
| `/generate` | Code generation | Generate code/reports from papers |
| `/paper/[id]` | Paper detail | Full paper view with analysis |

### Discovery Pages

| Route | Description | Filters Available |
|-------|-------------|-------------------|
| `/discovery` | Discovery hub | Overview of all discovery features |
| `/discovery/impact` | High-impact papers | Score range, category, time period |
| `/discovery/tldr` | Executive summaries | Days, category, reading time |
| `/discovery/learning-path` | Learning progressions | Topic, difficulty, category |
| `/discovery/techniques` | Technique explorer | Novelty type, methodology |
| `/discovery/rising` | Rising papers | Citation velocity, min citations |
| `/discovery/reproducible` | Reproducibility index | Score, code availability |
| `/discovery/practical` | Practical applications | Industry relevance, impact |
| `/discovery/hot-topics` | Hot topics | Time window, min papers |

---

## Database Schema

### Core Tables

#### `papers`
```sql
CREATE TABLE papers (
  id VARCHAR(50) PRIMARY KEY,           -- arXiv ID (e.g., "2401.12345")
  title TEXT NOT NULL,
  abstract TEXT,
  authors JSONB,                         -- Array of author objects
  published_date TIMESTAMPTZ,
  category VARCHAR(20),                  -- Primary arXiv category

  -- Vector Search
  embedding vector(1536),                -- OpenAI text-embedding-3-small

  -- Citation Data
  citation_count INTEGER DEFAULT 0,
  influential_citation_count INTEGER DEFAULT 0,
  citation_velocity FLOAT,               -- Citations per month

  -- Quality Metrics
  quality_score FLOAT,

  -- AI Analysis (JSONB)
  ai_analysis JSONB,                     -- Tier 1: Abstract-based
  deep_analysis JSONB,                   -- Tier 2: PDF-based

  -- Code & Reproducibility
  code_repos JSONB,                      -- GitHub URLs, etc.

  -- Knowledge Graph
  concepts_array TEXT[],                 -- Extracted concepts

  -- Full-Text Search
  search_vector TSVECTOR,

  -- Timestamps
  ingested_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_papers_embedding ON papers USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_papers_search ON papers USING gin(search_vector);
CREATE INDEX idx_papers_category ON papers(category);
CREATE INDEX idx_papers_published ON papers(published_date DESC);
CREATE INDEX idx_papers_citations ON papers(citation_count DESC);
```

### AI Analysis Fields

#### `ai_analysis` (Tier 1 - Abstract-Based)
```json
{
  "summary": "Brief summary of the paper",
  "novelty": "What's new about this work",
  "technicalInnovation": "Technical contributions",
  "keyContribution": "Main contribution",
  "methodologyBreakdown": "Methods used",
  "performanceHighlights": "Key results",
  "implementationInsights": "Implementation details",
  "researchContext": "Related work context",
  "futureImplications": "Future directions",
  "limitations": "Known limitations",
  "impactScore": 7,                      // 1-10 calibrated
  "difficultyLevel": "intermediate",     // beginner/intermediate/advanced
  "readingTime": 25,                     // minutes
  "hasCode": true,
  "implementationComplexity": "medium",
  "practicalApplicability": "high",
  "researchSignificance": "significant",
  "reproductionDifficulty": "moderate"
}
```

#### `deep_analysis` (Tier 2 - PDF-Based)
```json
{
  "executive_summary": "Comprehensive summary",
  "problem_statement": "What problem is solved",
  "proposed_solution": "The solution approach",
  "methodology": {
    "approach": "Overall methodology",
    "architecture": "Model architecture details",
    "key_components": ["Component 1", "Component 2"],
    "training_details": "Training procedure"
  },
  "experimental_results": {
    "benchmarks": ["Benchmark 1", "Benchmark 2"],
    "key_metrics": {"accuracy": 0.95},
    "performance_summary": "Results summary",
    "comparisons": "Comparison with baselines"
  },
  "figures_analysis": "Analysis of key figures",
  "technical_depth": "deep",
  "novelty_assessment": {
    "type": "architectural",            // algorithmic/architectural/theoretical/empirical
    "description": "Novelty details"
  },
  "practical_implications": {
    "use_cases": ["Use case 1", "Use case 2"],
    "industry_relevance": "high",
    "deployment_considerations": "Production considerations",
    "scalability": "Scalability analysis"
  },
  "impact_assessment": {
    "score": 8,                         // 1-10 calibrated
    "justification": "Why this score"
  }
}
```

### Knowledge Graph Tables

```sql
-- Concepts
CREATE TABLE concepts (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE,
  description TEXT,
  embedding vector(1536),
  paper_count INTEGER DEFAULT 0
);

-- Paper-Concept Relationships
CREATE TABLE paper_concepts (
  paper_id VARCHAR(50) REFERENCES papers(id),
  concept_id INTEGER REFERENCES concepts(id),
  relevance_score FLOAT,
  PRIMARY KEY (paper_id, concept_id)
);

-- Citations
CREATE TABLE citations (
  citing_paper_id VARCHAR(50),
  cited_paper_id VARCHAR(50),
  citation_context TEXT,
  is_influential BOOLEAN,
  PRIMARY KEY (citing_paper_id, cited_paper_id)
);

-- Techniques
CREATE TABLE techniques (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE,
  category VARCHAR(100),
  description TEXT,
  paper_count INTEGER DEFAULT 0
);

-- Datasets
CREATE TABLE datasets (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE,
  description TEXT,
  url TEXT,
  paper_count INTEGER DEFAULT 0
);

-- Authors
CREATE TABLE authors (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  affiliations JSONB,
  h_index INTEGER,
  paper_count INTEGER DEFAULT 0
);
```

---

## AI Enrichment Pipeline

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Enrichment Pipeline                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   arXiv     │───▶│   Tier 1    │───▶│   Tier 2    │     │
│  │  Ingestion  │    │  (Abstract) │    │   (PDF)     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Citation   │    │   Concept   │    │  Knowledge  │     │
│  │ Enrichment  │    │ Extraction  │    │   Graph     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tier 1: Abstract-Only Enrichment

| Property | Value |
|----------|-------|
| **Model** | Gemini 1.5 Flash |
| **Input** | Title + Abstract |
| **Output** | 18 structured fields |
| **Speed** | ~2 seconds per paper |
| **Cost** | Low |

**Output Fields:**
- `summary`, `novelty`, `technicalInnovation`, `keyContribution`
- `methodologyBreakdown`, `performanceHighlights`, `implementationInsights`
- `researchContext`, `futureImplications`, `limitations`
- `impactScore` (1-10), `difficultyLevel`, `readingTime`, `hasCode`
- `implementationComplexity`, `practicalApplicability`, `researchSignificance`

### Tier 2: Deep PDF Enrichment

| Property | Value |
|----------|-------|
| **Model** | Gemini 2.5 Flash Lite |
| **Input** | Full PDF (max 15 pages) |
| **Output** | Comprehensive analysis |
| **Concurrency** | 50 workers |
| **Batch Delay** | 2 seconds |

**Processing:**
1. Download PDF from arXiv
2. Extract text (skip appendix, limit 15 pages)
3. Analyze with Gemini 2.5 Flash Lite
4. Parse structured JSON response
5. Store in `deep_analysis` JSONB field

**Output Sections:**
- Executive summary and problem statement
- Methodology (architecture, components, training)
- Experimental results (benchmarks, metrics, comparisons)
- Figure analysis
- Novelty assessment (type + description)
- Practical implications (use cases, scalability, deployment)
- Impact assessment (1-10 with justification)

### Citation Enrichment

| Property | Value |
|----------|-------|
| **Source** | Semantic Scholar API |
| **Rate Limit** | 100 requests/min (with API key) |
| **Data** | citation_count, influential_citations, velocity |

---

## Backend Services

### Data Ingestion & Enrichment

| Service | File | Purpose |
|---------|------|---------|
| `AIAnalysisService` | `ai_analysis_service.py` | Tier 1 abstract enrichment via Gemini |
| `DeepEnrichmentService` | `deep_enrichment_service.py` | Tier 2 PDF enrichment |
| `BatchEnrichmentService` | `batch_enrichment_service.py` | Batch processing with rate limits |
| `IngestionService` | `ingestion_service.py` | arXiv paper fetching |
| `DailyIngestionService` | `daily_ingestion_service.py` | Scheduled daily ingestion |
| `CitationEnrichmentService` | `citation_enrichment_service.py` | Semantic Scholar citations |

### Search & Retrieval

| Service | File | Purpose |
|---------|------|---------|
| `ArxivService` | `arxiv_service.py` | Live arXiv API queries |
| `LocalAtlasService` | `local_atlas_service.py` | In-memory semantic search |
| `EmbeddingService` | `embedding_service.py` | OpenAI embeddings (1536 dims) |
| `ReRankService` | `rerank_service.py` | E5-large-v2, OpenAI, Voyage AI |
| `SimilarityService` | `similarity_service.py` | Cosine similarity computation |

### Knowledge Graph & Analysis

| Service | File | Purpose |
|---------|------|---------|
| `ResearchGraphService` | `research_graph_service.py` | Knowledge graph construction |
| `CitationGraphService` | `citation_graph_service.py` | Citation network visualization |
| `ConceptExtractionService` | `concept_extraction_service.py` | AI-based concept extraction |
| `TechniqueExtractionService` | `technique_extraction_service.py` | Methodology extraction |
| `TrendService` | `trend_service.py` | Hot topics, rising techniques |

### Infrastructure

| Service | File | Purpose |
|---------|------|---------|
| `SchedulerService` | `scheduler_service.py` | APScheduler for daily jobs |
| `CacheService` | `cache_service.py` | Redis/in-memory caching |
| `CodeDetectionService` | `code_detection_service.py` | GitHub URL extraction |
| `AgentMemoryStore` | `agent_memory_store.py` | Learning agent memory |

---

## External Integrations

### APIs Used

| API | Purpose | Rate Limits |
|-----|---------|-------------|
| **arXiv** | Paper metadata & PDFs | 3 requests/second |
| **Google Gemini** | AI analysis | 1500 RPM (Flash) |
| **OpenAI** | Embeddings | 3000 RPM |
| **Semantic Scholar** | Citations | 100 RPM (with key) |
| **OpenAlex** | Metadata enrichment | 10 RPS |
| **Papers with Code** | Code repos | Reasonable use |
| **GitHub** | Repo verification | 5000/hour (with token) |

### Integration Details

#### arXiv API
```python
# Endpoint
http://export.arxiv.org/api/query

# Example query
?search_query=cat:cs.LG&start=0&max_results=100&sortBy=submittedDate
```

#### Semantic Scholar API
```python
# Endpoint (with API key)
https://api.semanticscholar.org/graph/v1/paper/arXiv:{paper_id}

# Fields requested
fields=citationCount,influentialCitationCount,citations.paperId
```

#### Google Gemini
```python
# Models used
gemini-1.5-flash      # Tier 1 enrichment
gemini-2.5-flash-lite # Tier 2 deep enrichment

# Rate limits
1500 requests/minute (Flash)
```

---

## Configuration

### Environment Variables

#### Database
```bash
SUPABASE_DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
```

#### AI Services
```bash
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # Optional
```

#### External APIs
```bash
SEMANTIC_SCHOLAR_API_KEY=...  # Optional, increases rate limit
VOYAGE_API_KEY=...            # Optional, for Voyage reranking
GITHUB_TOKEN=ghp_...          # Optional, for repo verification
```

#### Atlas Configuration
```bash
ATLAS_DERIVED_DIR=/path/to/atlas/derived
ATLAS_EMBED_MODEL=allenai/specter2
ATLAS_EMBED_CACHE_DIR=/path/to/cache
ATLAS_EMBED_CACHE_LABEL=specter2_v1
CONTEXTUAL_SEARCH_TOP_K=20
CONTEXTUAL_SEARCH_MAX_DAYS=365
```

#### Scheduling
```bash
ENABLE_SCHEDULER=true
INGESTION_HOUR=6          # UTC hour for daily ingestion
INGESTION_MINUTE=0
DEFAULT_AI_CATEGORIES=cs.LG,cs.CL,cs.CV,cs.AI,stat.ML
```

#### Rate Limiting
```bash
MAX_PAPERS_PER_BATCH=100
GEMINI_RATE_LIMIT_BATCH_SIZE=5
GEMINI_RATE_LIMIT_DELAY=2
RERANK_E5_BATCH_SIZE=32
```

#### Server
```bash
API_V1_STR=/api/v1
PROJECT_NAME=AI Papers Agent
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL with pgvector
- Supabase account (or local instance)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
npm install
cp .env.example .env.local
# Edit .env.local
npm run dev
```

### Initial Data Load
```bash
# Trigger paper ingestion
curl -X POST "http://localhost:8000/api/v1/ingestion/trigger" \
  -H "Content-Type: application/json" \
  -d '{"categories": ["cs.LG"], "days": 7, "max_papers": 100}'

# Start Tier 1 enrichment
curl -X POST "http://localhost:8000/api/v1/enrichment/trigger" \
  -H "Content-Type: application/json" \
  -d '{"max_papers": 100}'

# Start Tier 2 deep enrichment
curl -X POST "http://localhost:8000/api/v1/enrichment/deep/trigger" \
  -H "Content-Type: application/json" \
  -d '{"max_papers": 50}'
```

---

## Data Statistics

Current database contains:
- **~30,000+ papers** from AI/ML categories
- **~21,000+ papers** with Tier 1 enrichment
- **~21,000+ papers** with Tier 2 deep analysis
- **~20,000+ papers** with citation data
- Daily ingestion adds ~50-200 papers

---

## License

MIT License - See LICENSE file for details.
