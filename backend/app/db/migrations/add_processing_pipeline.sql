-- Processing Pipeline Tables
-- Tracks paper processing state and enables scalable enrichment

-- =============================================================================
-- 1. PAPER PROCESSING STATE - Tracks what's been done to each paper
-- =============================================================================
CREATE TABLE IF NOT EXISTS paper_processing_state (
    paper_id VARCHAR(50) PRIMARY KEY REFERENCES papers(id) ON DELETE CASCADE,

    -- Processing stages (timestamps when completed, NULL if not done)
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    embedding_at TIMESTAMP WITH TIME ZONE,
    ai_analysis_at TIMESTAMP WITH TIME ZONE,
    citations_at TIMESTAMP WITH TIME ZONE,
    concepts_at TIMESTAMP WITH TIME ZONE,
    techniques_at TIMESTAMP WITH TIME ZONE,
    benchmarks_at TIMESTAMP WITH TIME ZONE,
    github_at TIMESTAMP WITH TIME ZONE,
    deep_analysis_at TIMESTAMP WITH TIME ZONE,
    relationships_at TIMESTAMP WITH TIME ZONE,

    -- Computed completeness score (0-100)
    completeness_score INTEGER GENERATED ALWAYS AS (
        (CASE WHEN embedding_at IS NOT NULL THEN 10 ELSE 0 END) +
        (CASE WHEN ai_analysis_at IS NOT NULL THEN 20 ELSE 0 END) +
        (CASE WHEN citations_at IS NOT NULL THEN 15 ELSE 0 END) +
        (CASE WHEN concepts_at IS NOT NULL THEN 10 ELSE 0 END) +
        (CASE WHEN techniques_at IS NOT NULL THEN 15 ELSE 0 END) +
        (CASE WHEN benchmarks_at IS NOT NULL THEN 10 ELSE 0 END) +
        (CASE WHEN github_at IS NOT NULL THEN 5 ELSE 0 END) +
        (CASE WHEN deep_analysis_at IS NOT NULL THEN 10 ELSE 0 END) +
        (CASE WHEN relationships_at IS NOT NULL THEN 5 ELSE 0 END)
    ) STORED,

    -- Priority for processing (higher = more important)
    priority INTEGER DEFAULT 50,

    -- Last error if any
    last_error TEXT,
    last_error_at TIMESTAMP WITH TIME ZONE,
    error_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for finding papers needing processing
CREATE INDEX IF NOT EXISTS idx_processing_state_completeness ON paper_processing_state(completeness_score);
CREATE INDEX IF NOT EXISTS idx_processing_state_priority ON paper_processing_state(priority DESC);
CREATE INDEX IF NOT EXISTS idx_processing_state_errors ON paper_processing_state(error_count) WHERE error_count > 0;

-- =============================================================================
-- 2. PROCESSING JOBS - Individual enrichment job tracking
-- =============================================================================
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE job_type AS ENUM (
    'ingest', 'embedding', 'ai_analysis', 'citations', 'concepts',
    'techniques', 'benchmarks', 'github', 'deep_analysis', 'relationships',
    'full_enrichment', 'batch_ingest'
);

CREATE TABLE IF NOT EXISTS processing_jobs (
    id SERIAL PRIMARY KEY,
    job_type job_type NOT NULL,
    status job_status DEFAULT 'pending',

    -- Job scope (single paper or batch)
    paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,
    batch_id UUID,  -- Groups related jobs together

    -- Priority (higher = more urgent)
    priority INTEGER DEFAULT 50,

    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Results
    result JSONB,  -- Success data
    error_message TEXT,
    error_details JSONB,

    -- Retry tracking
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,

    -- Idempotency
    idempotency_key VARCHAR(255) UNIQUE,

    -- Worker assignment (for distributed processing)
    worker_id VARCHAR(100),
    heartbeat_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for job processing
CREATE INDEX IF NOT EXISTS idx_jobs_pending ON processing_jobs(status, priority DESC, created_at)
    WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_jobs_paper ON processing_jobs(paper_id);
CREATE INDEX IF NOT EXISTS idx_jobs_batch ON processing_jobs(batch_id) WHERE batch_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_retry ON processing_jobs(next_retry_at)
    WHERE status = 'failed' AND retry_count < max_retries;
CREATE INDEX IF NOT EXISTS idx_jobs_stale ON processing_jobs(heartbeat_at)
    WHERE status = 'processing';

-- =============================================================================
-- 3. PIPELINE RUNS - High-level pipeline execution tracking
-- =============================================================================
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    run_type VARCHAR(50) NOT NULL,  -- 'daily_ingest', 'backfill', 'enrichment_sweep', etc.
    status job_status DEFAULT 'pending',

    -- Configuration
    config JSONB DEFAULT '{}',

    -- Progress
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    skipped_items INTEGER DEFAULT 0,

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Results
    summary JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_type ON pipeline_runs(run_type, created_at DESC);

-- =============================================================================
-- 4. RATE LIMIT TRACKING - Track API usage to avoid hitting limits
-- =============================================================================
CREATE TABLE IF NOT EXISTS rate_limit_tracking (
    provider VARCHAR(50) PRIMARY KEY,  -- 'openalex', 'semantic_scholar', 'github', 'gemini'
    requests_count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    window_seconds INTEGER DEFAULT 60,
    max_requests INTEGER DEFAULT 100,
    last_request_at TIMESTAMP WITH TIME ZONE,
    backoff_until TIMESTAMP WITH TIME ZONE
);

-- =============================================================================
-- 5. HELPER FUNCTIONS
-- =============================================================================

-- Function to get next job for processing (with locking)
CREATE OR REPLACE FUNCTION get_next_job(p_worker_id VARCHAR, p_job_types job_type[] DEFAULT NULL)
RETURNS processing_jobs AS $$
DECLARE
    v_job processing_jobs;
BEGIN
    -- Get and lock next available job
    SELECT * INTO v_job
    FROM processing_jobs
    WHERE status = 'pending'
    AND (p_job_types IS NULL OR job_type = ANY(p_job_types))
    ORDER BY priority DESC, created_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED;

    IF v_job.id IS NOT NULL THEN
        -- Mark as processing
        UPDATE processing_jobs
        SET status = 'processing',
            started_at = NOW(),
            worker_id = p_worker_id,
            heartbeat_at = NOW()
        WHERE id = v_job.id;

        -- Return updated job
        SELECT * INTO v_job FROM processing_jobs WHERE id = v_job.id;
    END IF;

    RETURN v_job;
END;
$$ LANGUAGE plpgsql;

-- Function to complete a job
CREATE OR REPLACE FUNCTION complete_job(p_job_id INTEGER, p_result JSONB DEFAULT NULL)
RETURNS VOID AS $$
BEGIN
    UPDATE processing_jobs
    SET status = 'completed',
        completed_at = NOW(),
        result = p_result
    WHERE id = p_job_id;

    -- Update paper processing state if this was a paper job
    UPDATE paper_processing_state pps
    SET updated_at = NOW()
    FROM processing_jobs pj
    WHERE pj.id = p_job_id
    AND pps.paper_id = pj.paper_id;
END;
$$ LANGUAGE plpgsql;

-- Function to fail a job (with retry logic)
CREATE OR REPLACE FUNCTION fail_job(p_job_id INTEGER, p_error TEXT, p_error_details JSONB DEFAULT NULL)
RETURNS VOID AS $$
DECLARE
    v_retry_count INTEGER;
    v_max_retries INTEGER;
BEGIN
    SELECT retry_count, max_retries INTO v_retry_count, v_max_retries
    FROM processing_jobs WHERE id = p_job_id;

    IF v_retry_count < v_max_retries THEN
        -- Schedule retry with exponential backoff
        UPDATE processing_jobs
        SET status = 'pending',
            retry_count = retry_count + 1,
            error_message = p_error,
            error_details = p_error_details,
            next_retry_at = NOW() + (INTERVAL '1 minute' * POWER(2, retry_count)),
            completed_at = NULL,
            started_at = NULL,
            worker_id = NULL
        WHERE id = p_job_id;
    ELSE
        -- Max retries exceeded
        UPDATE processing_jobs
        SET status = 'failed',
            completed_at = NOW(),
            error_message = p_error,
            error_details = p_error_details
        WHERE id = p_job_id;

        -- Update paper error state
        UPDATE paper_processing_state
        SET last_error = p_error,
            last_error_at = NOW(),
            error_count = error_count + 1,
            updated_at = NOW()
        FROM processing_jobs pj
        WHERE pj.id = p_job_id
        AND paper_processing_state.paper_id = pj.paper_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up stale jobs (workers that died)
CREATE OR REPLACE FUNCTION cleanup_stale_jobs(p_stale_minutes INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    WITH stale AS (
        UPDATE processing_jobs
        SET status = 'pending',
            worker_id = NULL,
            started_at = NULL,
            heartbeat_at = NULL
        WHERE status = 'processing'
        AND heartbeat_at < NOW() - (p_stale_minutes || ' minutes')::INTERVAL
        RETURNING id
    )
    SELECT COUNT(*) INTO v_count FROM stale;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 6. TRIGGERS FOR AUTO-UPDATING
-- =============================================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_processing_state_updated
    BEFORE UPDATE ON paper_processing_state
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Auto-create processing state when paper is inserted
CREATE OR REPLACE FUNCTION create_processing_state()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO paper_processing_state (paper_id, ingested_at)
    VALUES (NEW.id, NOW())
    ON CONFLICT (paper_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_paper_processing_state
    AFTER INSERT ON papers
    FOR EACH ROW EXECUTE FUNCTION create_processing_state();

-- =============================================================================
-- 7. VIEWS FOR MONITORING
-- =============================================================================

-- Papers needing processing (prioritized)
CREATE OR REPLACE VIEW v_papers_need_processing AS
SELECT
    pps.paper_id,
    p.title,
    p.published_date,
    pps.completeness_score,
    pps.priority,
    pps.error_count,
    CASE
        WHEN pps.embedding_at IS NULL THEN 'embedding'
        WHEN pps.ai_analysis_at IS NULL THEN 'ai_analysis'
        WHEN pps.citations_at IS NULL THEN 'citations'
        WHEN pps.concepts_at IS NULL THEN 'concepts'
        WHEN pps.techniques_at IS NULL THEN 'techniques'
        WHEN pps.benchmarks_at IS NULL THEN 'benchmarks'
        WHEN pps.github_at IS NULL THEN 'github'
        WHEN pps.deep_analysis_at IS NULL THEN 'deep_analysis'
        WHEN pps.relationships_at IS NULL THEN 'relationships'
        ELSE 'complete'
    END as next_step
FROM paper_processing_state pps
JOIN papers p ON pps.paper_id = p.id
WHERE pps.completeness_score < 100
AND pps.error_count < 5
ORDER BY pps.priority DESC, pps.completeness_score ASC, p.published_date DESC;

-- Pipeline health summary
CREATE OR REPLACE VIEW v_pipeline_health AS
SELECT
    'total_papers' as metric, COUNT(*)::TEXT as value FROM papers
UNION ALL
SELECT 'papers_with_state', COUNT(*)::TEXT FROM paper_processing_state
UNION ALL
SELECT 'fully_processed', COUNT(*)::TEXT FROM paper_processing_state WHERE completeness_score = 100
UNION ALL
SELECT 'pending_jobs', COUNT(*)::TEXT FROM processing_jobs WHERE status = 'pending'
UNION ALL
SELECT 'processing_jobs', COUNT(*)::TEXT FROM processing_jobs WHERE status = 'processing'
UNION ALL
SELECT 'failed_jobs_24h', COUNT(*)::TEXT FROM processing_jobs WHERE status = 'failed' AND completed_at > NOW() - INTERVAL '24 hours'
UNION ALL
SELECT 'avg_completeness', ROUND(AVG(completeness_score), 1)::TEXT FROM paper_processing_state;

-- Job queue status
CREATE OR REPLACE VIEW v_job_queue_status AS
SELECT
    job_type,
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at)))::INTEGER as avg_duration_sec
FROM processing_jobs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY job_type, status
ORDER BY job_type, status;
