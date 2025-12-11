-- Data Moat Tables Migration
-- Phase 2-5: Relationship Graph, External Signals, Temporal Tracking, Benchmarks
-- Run this migration to add new tables for rich data infrastructure

-- ============================================================================
-- PHASE 2: Typed Semantic Relationships Between Papers
-- ============================================================================
-- Unlike paper_relationships (similarity scores), these are MEANINGFUL edges:
-- "Paper B improves Paper A by doing X"
-- "Paper B contradicts Paper A's findings"

CREATE TABLE IF NOT EXISTS paper_semantic_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source paper (the one making the claim/relationship)
    source_paper_id VARCHAR(50) NOT NULL REFERENCES papers(id) ON DELETE CASCADE,

    -- Target paper (the one being referenced)
    target_paper_id VARCHAR(50) NOT NULL REFERENCES papers(id) ON DELETE CASCADE,

    -- Relationship type (the semantic meaning)
    relationship_type VARCHAR(50) NOT NULL,
    -- Types: improves, extends, contradicts, applies, simplifies, explains,
    --        implements, surveys, replicates, criticizes

    -- Human-readable description of the relationship
    description TEXT,
    -- Example: "Improves accuracy by 3% via modified attention mechanism"

    -- Where in the paper this relationship was found
    evidence_section VARCHAR(100),  -- "related_work", "introduction", "experiments"
    evidence_snippet TEXT,          -- The actual text mentioning the relationship

    -- Extraction metadata
    confidence FLOAT DEFAULT 0.8,   -- 0-1, how confident we are in this extraction
    extraction_method VARCHAR(50),  -- "llm", "citation_context", "manual"
    extracted_at TIMESTAMPTZ DEFAULT NOW(),

    -- Prevent duplicates
    CONSTRAINT unique_semantic_edge UNIQUE (source_paper_id, target_paper_id, relationship_type)
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_semantic_edges_source ON paper_semantic_edges(source_paper_id);
CREATE INDEX IF NOT EXISTS idx_semantic_edges_target ON paper_semantic_edges(target_paper_id);
CREATE INDEX IF NOT EXISTS idx_semantic_edges_type ON paper_semantic_edges(relationship_type);
CREATE INDEX IF NOT EXISTS idx_semantic_edges_confidence ON paper_semantic_edges(confidence DESC);

-- ============================================================================
-- PHASE 3: External Signals
-- ============================================================================
-- Add external_signals JSONB column to papers table for GitHub, HuggingFace, social data

ALTER TABLE papers ADD COLUMN IF NOT EXISTS external_signals JSONB DEFAULT '{}';

-- Structure of external_signals:
-- {
--   "github": {
--     "repos": [
--       {
--         "url": "https://github.com/...",
--         "stars": 4200,
--         "forks": 380,
--         "open_issues": 45,
--         "last_commit": "2024-12-08",
--         "contributors": 23,
--         "language": "Python",
--         "license": "MIT"
--       }
--     ],
--     "total_stars": 4200,
--     "updated_at": "2024-12-10T..."
--   },
--   "huggingface": {
--     "models": [
--       {"id": "author/model", "downloads": 125000, "likes": 340}
--     ],
--     "datasets": [...],
--     "total_downloads": 125000,
--     "updated_at": "2024-12-10T..."
--   },
--   "social": {
--     "twitter_mentions_30d": 156,
--     "reddit_threads": 12,
--     "blog_posts": ["https://...", ...],
--     "youtube_videos": 3,
--     "updated_at": "2024-12-10T..."
--   },
--   "industry": {
--     "known_adopters": ["Company A", "Company B"],
--     "job_mentions_30d": 45,
--     "updated_at": "2024-12-10T..."
--   }
-- }

-- Index for querying papers with high GitHub stars, etc.
CREATE INDEX IF NOT EXISTS idx_papers_external_signals ON papers USING GIN (external_signals);

-- ============================================================================
-- PHASE 4: Temporal Tracking (Metric Snapshots)
-- ============================================================================
-- Track ALL metrics over time to enable trend analysis

CREATE TABLE IF NOT EXISTS metric_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    paper_id VARCHAR(50) NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,

    -- Citation metrics
    citation_count INTEGER,
    influential_citation_count INTEGER,
    citation_velocity FLOAT,  -- citations per month (rolling 30 days)

    -- Code metrics (from external_signals)
    github_stars INTEGER,
    github_forks INTEGER,
    github_open_issues INTEGER,
    huggingface_downloads INTEGER,

    -- Social metrics
    twitter_mentions INTEGER,
    reddit_mentions INTEGER,

    -- Computed scores
    buzz_score FLOAT,  -- Composite attention score
    quality_score FLOAT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- One snapshot per paper per day
    CONSTRAINT unique_paper_snapshot UNIQUE (paper_id, snapshot_date)
);

-- Indexes for time-series queries
CREATE INDEX IF NOT EXISTS idx_snapshots_paper_date ON metric_snapshots(paper_id, snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_date ON metric_snapshots(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_buzz ON metric_snapshots(snapshot_date, buzz_score DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_velocity ON metric_snapshots(snapshot_date, citation_velocity DESC);

-- ============================================================================
-- PHASE 5: Benchmark Definitions & SOTA Tracking
-- ============================================================================
-- Clean benchmark definitions (separate from results)

CREATE TABLE IF NOT EXISTS benchmark_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    name VARCHAR(200) UNIQUE NOT NULL,  -- "ImageNet-1K", "MMLU", "HumanEval"
    slug VARCHAR(100) UNIQUE NOT NULL,  -- "imagenet-1k", "mmlu", "humaneval"

    -- Classification
    task_category VARCHAR(100),  -- "image_classification", "question_answering", "code_generation"
    modality VARCHAR(50),        -- "vision", "language", "multimodal", "code"

    -- Metric info
    primary_metric VARCHAR(100) NOT NULL,  -- "top-1 accuracy", "score", "pass@1"
    metric_unit VARCHAR(50),               -- "%", "score", "ms"
    higher_is_better BOOLEAN DEFAULT true,

    -- Description
    description TEXT,
    homepage_url VARCHAR(500),
    paper_url VARCHAR(500),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SOTA History: Track state-of-the-art over time
CREATE TABLE IF NOT EXISTS sota_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    benchmark_id UUID NOT NULL REFERENCES benchmark_definitions(id) ON DELETE CASCADE,
    paper_id VARCHAR(50) NOT NULL REFERENCES papers(id) ON DELETE CASCADE,

    -- The SOTA value
    value FLOAT NOT NULL,

    -- When this became SOTA
    achieved_date DATE NOT NULL,

    -- Model details
    model_name VARCHAR(200),
    model_size VARCHAR(100),  -- "7B", "86M params"

    -- Additional context
    details JSONB,  -- {compute: "8xA100", training_data: "...", etc.}

    -- Was this verified? (manually checked vs auto-extracted)
    is_verified BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Prevent duplicate SOTA entries for same paper/benchmark/date
    CONSTRAINT unique_sota_entry UNIQUE (benchmark_id, paper_id, achieved_date)
);

CREATE INDEX IF NOT EXISTS idx_sota_benchmark_date ON sota_history(benchmark_id, achieved_date DESC);
CREATE INDEX IF NOT EXISTS idx_sota_value ON sota_history(benchmark_id, value DESC);

-- ============================================================================
-- Useful Views
-- ============================================================================

-- View: Current SOTA for each benchmark
CREATE OR REPLACE VIEW current_sota AS
SELECT DISTINCT ON (bd.id)
    bd.id as benchmark_id,
    bd.name as benchmark_name,
    bd.slug as benchmark_slug,
    bd.task_category,
    bd.primary_metric,
    bd.higher_is_better,
    sh.value as sota_value,
    sh.achieved_date,
    sh.paper_id,
    sh.model_name,
    p.title as paper_title
FROM benchmark_definitions bd
JOIN sota_history sh ON bd.id = sh.benchmark_id
JOIN papers p ON sh.paper_id = p.id
ORDER BY bd.id,
    CASE WHEN bd.higher_is_better THEN sh.value ELSE -sh.value END DESC,
    sh.achieved_date DESC;

-- View: Papers with high external signals
CREATE OR REPLACE VIEW papers_with_signals AS
SELECT
    p.id,
    p.title,
    p.category,
    p.published_date,
    p.citation_count,
    (p.external_signals->'github'->>'total_stars')::int as github_stars,
    (p.external_signals->'huggingface'->>'total_downloads')::int as hf_downloads,
    p.external_signals
FROM papers p
WHERE p.external_signals IS NOT NULL
  AND p.external_signals != '{}'::jsonb;

-- View: Paper lineage (what a paper builds on and what builds on it)
CREATE OR REPLACE VIEW paper_lineage AS
SELECT
    p.id as paper_id,
    p.title,
    -- Papers this one improves/extends
    (SELECT json_agg(json_build_object(
        'paper_id', pse.target_paper_id,
        'title', tp.title,
        'relationship', pse.relationship_type,
        'description', pse.description
    ))
    FROM paper_semantic_edges pse
    JOIN papers tp ON pse.target_paper_id = tp.id
    WHERE pse.source_paper_id = p.id
    AND pse.relationship_type IN ('improves', 'extends', 'builds_on')
    ) as builds_on,
    -- Papers that improve/extend this one
    (SELECT json_agg(json_build_object(
        'paper_id', pse.source_paper_id,
        'title', sp.title,
        'relationship', pse.relationship_type,
        'description', pse.description
    ))
    FROM paper_semantic_edges pse
    JOIN papers sp ON pse.source_paper_id = sp.id
    WHERE pse.target_paper_id = p.id
    AND pse.relationship_type IN ('improves', 'extends', 'builds_on')
    ) as improved_by
FROM papers p;

-- ============================================================================
-- Seed some common benchmark definitions
-- ============================================================================

INSERT INTO benchmark_definitions (name, slug, task_category, modality, primary_metric, metric_unit, higher_is_better, description) VALUES
-- Vision
('ImageNet-1K', 'imagenet-1k', 'image_classification', 'vision', 'top-1 accuracy', '%', true, 'Large-scale image classification benchmark with 1000 classes'),
('ImageNet-21K', 'imagenet-21k', 'image_classification', 'vision', 'top-1 accuracy', '%', true, 'ImageNet with 21,841 classes'),
('COCO Detection', 'coco-detection', 'object_detection', 'vision', 'mAP', '%', true, 'Common Objects in Context detection benchmark'),
('COCO Segmentation', 'coco-segmentation', 'instance_segmentation', 'vision', 'mAP', '%', true, 'COCO instance segmentation benchmark'),
('ADE20K', 'ade20k', 'semantic_segmentation', 'vision', 'mIoU', '%', true, 'Scene parsing benchmark'),

-- Language
('MMLU', 'mmlu', 'question_answering', 'language', 'accuracy', '%', true, 'Massive Multitask Language Understanding'),
('HellaSwag', 'hellaswag', 'commonsense_reasoning', 'language', 'accuracy', '%', true, 'Commonsense reasoning benchmark'),
('WinoGrande', 'winogrande', 'commonsense_reasoning', 'language', 'accuracy', '%', true, 'Winograd schema challenge'),
('ARC-Challenge', 'arc-challenge', 'question_answering', 'language', 'accuracy', '%', true, 'AI2 Reasoning Challenge'),
('TruthfulQA', 'truthfulqa', 'question_answering', 'language', 'accuracy', '%', true, 'Measuring truthfulness in QA'),
('GSM8K', 'gsm8k', 'math_reasoning', 'language', 'accuracy', '%', true, 'Grade school math benchmark'),
('MATH', 'math', 'math_reasoning', 'language', 'accuracy', '%', true, 'Competition math problems'),

-- Code
('HumanEval', 'humaneval', 'code_generation', 'code', 'pass@1', '%', true, 'Hand-written Python programming problems'),
('MBPP', 'mbpp', 'code_generation', 'code', 'pass@1', '%', true, 'Mostly Basic Python Problems'),
('SWE-bench', 'swe-bench', 'code_generation', 'code', 'resolved', '%', true, 'Real-world GitHub issues'),

-- Multimodal
('VQAv2', 'vqav2', 'visual_qa', 'multimodal', 'accuracy', '%', true, 'Visual Question Answering v2'),
('GQA', 'gqa', 'visual_qa', 'multimodal', 'accuracy', '%', true, 'Compositional visual reasoning'),
('TextVQA', 'textvqa', 'visual_qa', 'multimodal', 'accuracy', '%', true, 'Text-based visual QA'),

-- Efficiency
('ImageNet Throughput', 'imagenet-throughput', 'inference_speed', 'vision', 'images/sec', 'img/s', true, 'Inference throughput on ImageNet'),
('FLOPS Efficiency', 'flops-efficiency', 'efficiency', 'general', 'accuracy/GFLOP', 'acc/GFLOP', true, 'Accuracy per compute cost')

ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to get paper's full relationship graph
CREATE OR REPLACE FUNCTION get_paper_relationships(target_paper_id VARCHAR(50))
RETURNS TABLE (
    direction VARCHAR(10),
    related_paper_id VARCHAR(50),
    related_paper_title TEXT,
    relationship_type VARCHAR(50),
    description TEXT,
    confidence FLOAT
) AS $$
BEGIN
    RETURN QUERY
    -- Outgoing relationships (this paper -> others)
    SELECT
        'outgoing'::VARCHAR(10) as direction,
        pse.target_paper_id as related_paper_id,
        p.title as related_paper_title,
        pse.relationship_type,
        pse.description,
        pse.confidence
    FROM paper_semantic_edges pse
    JOIN papers p ON pse.target_paper_id = p.id
    WHERE pse.source_paper_id = target_paper_id

    UNION ALL

    -- Incoming relationships (others -> this paper)
    SELECT
        'incoming'::VARCHAR(10) as direction,
        pse.source_paper_id as related_paper_id,
        p.title as related_paper_title,
        pse.relationship_type,
        pse.description,
        pse.confidence
    FROM paper_semantic_edges pse
    JOIN papers p ON pse.source_paper_id = p.id
    WHERE pse.target_paper_id = target_paper_id

    ORDER BY confidence DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate citation velocity
CREATE OR REPLACE FUNCTION calculate_citation_velocity(
    p_paper_id VARCHAR(50),
    p_window_days INTEGER DEFAULT 30
) RETURNS FLOAT AS $$
DECLARE
    recent_citations INTEGER;
    older_citations INTEGER;
    velocity FLOAT;
BEGIN
    -- Get citation count from recent snapshot
    SELECT citation_count INTO recent_citations
    FROM metric_snapshots
    WHERE paper_id = p_paper_id
    ORDER BY snapshot_date DESC
    LIMIT 1;

    -- Get citation count from older snapshot
    SELECT citation_count INTO older_citations
    FROM metric_snapshots
    WHERE paper_id = p_paper_id
    AND snapshot_date <= CURRENT_DATE - p_window_days
    ORDER BY snapshot_date DESC
    LIMIT 1;

    -- Calculate velocity (citations per month)
    IF recent_citations IS NOT NULL AND older_citations IS NOT NULL THEN
        velocity := (recent_citations - older_citations)::FLOAT / (p_window_days / 30.0);
    ELSE
        velocity := 0;
    END IF;

    RETURN velocity;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE paper_semantic_edges IS 'Typed semantic relationships between papers (improves, contradicts, etc.)';
COMMENT ON TABLE metric_snapshots IS 'Historical snapshots of paper metrics for trend analysis';
COMMENT ON TABLE benchmark_definitions IS 'Canonical benchmark definitions (ImageNet, MMLU, etc.)';
COMMENT ON TABLE sota_history IS 'State-of-the-art history tracking per benchmark';
