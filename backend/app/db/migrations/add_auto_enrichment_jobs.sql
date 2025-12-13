-- Auto-Create Enrichment Jobs Migration
-- When a paper is inserted, automatically create enrichment jobs for all stages
-- This enables fully automated pipeline: ingest → auto-jobs → workers process

-- =============================================================================
-- 1. FUNCTION: Auto-create enrichment jobs when paper_processing_state is created
-- =============================================================================

CREATE OR REPLACE FUNCTION create_enrichment_jobs_for_paper()
RETURNS TRIGGER AS $$
DECLARE
    v_batch_id UUID := gen_random_uuid();
    v_stages TEXT[] := ARRAY[
        'embedding', 'ai_analysis', 'citations', 'concepts',
        'techniques', 'benchmarks', 'github', 'deep_analysis', 'relationships'
    ];
    v_stage TEXT;
BEGIN
    -- Create jobs for all enrichment stages at HIGH priority (75)
    -- New papers get processed quickly
    FOREACH v_stage IN ARRAY v_stages
    LOOP
        INSERT INTO processing_jobs (
            job_type,
            paper_id,
            batch_id,
            priority,
            idempotency_key,
            metadata
        ) VALUES (
            v_stage::job_type,
            NEW.paper_id,
            v_batch_id,
            75,  -- HIGH priority for new papers
            v_stage || ':' || NEW.paper_id || ':auto',
            jsonb_build_object('source', 'auto_trigger', 'batch_id', v_batch_id)
        )
        ON CONFLICT (idempotency_key) DO NOTHING;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 2. TRIGGER: Fire on paper_processing_state INSERT
-- =============================================================================

-- Drop existing trigger if it exists (for idempotent migrations)
DROP TRIGGER IF EXISTS trigger_auto_create_enrichment_jobs ON paper_processing_state;

-- Create the trigger
CREATE TRIGGER trigger_auto_create_enrichment_jobs
    AFTER INSERT ON paper_processing_state
    FOR EACH ROW
    EXECUTE FUNCTION create_enrichment_jobs_for_paper();

-- =============================================================================
-- 3. COMMENTS
-- =============================================================================

COMMENT ON FUNCTION create_enrichment_jobs_for_paper() IS
'Automatically creates enrichment jobs for all 9 stages when a new paper is inserted.
Jobs are created at HIGH priority (75) so new papers are processed quickly.
Uses idempotency_key to prevent duplicate job creation.';

COMMENT ON TRIGGER trigger_auto_create_enrichment_jobs ON paper_processing_state IS
'Fires after INSERT on paper_processing_state to auto-create enrichment jobs.
Combined with trigger_paper_processing_state on papers table, this creates a
fully automated pipeline: papers INSERT → processing_state INSERT → jobs INSERT';
