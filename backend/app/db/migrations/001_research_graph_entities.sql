-- ================================================
-- Migration: Research Atlas Core Entities (v2025.10)
-- ================================================

-- 1. Techniques
CREATE TABLE IF NOT EXISTS techniques (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    normalized_name VARCHAR(200) NOT NULL,
    method_type VARCHAR(100),
    emergence_date TIMESTAMP,
    maturity_score FLOAT DEFAULT 0.0,
    description TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS techniques_normalized_idx ON techniques(normalized_name);
CREATE INDEX IF NOT EXISTS techniques_type_maturity_idx ON techniques(method_type, maturity_score);

-- 2. Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    taxonomy_path VARCHAR(400),
    modality VARCHAR(100),
    application_domain VARCHAR(150),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS tasks_modality_idx ON tasks(modality);
CREATE INDEX IF NOT EXISTS tasks_domain_idx ON tasks(application_domain);

-- 3. Datasets
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    normalized_name VARCHAR(200) NOT NULL,
    modality VARCHAR(100),
    sample_count INTEGER,
    license VARCHAR(100),
    maintainer VARCHAR(200),
    url VARCHAR(300),
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS datasets_normalized_idx ON datasets(normalized_name);
CREATE INDEX IF NOT EXISTS datasets_modality_idx ON datasets(modality);

-- 4. Organisations
CREATE TABLE IF NOT EXISTS organisations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    kind VARCHAR(50),
    region VARCHAR(100),
    homepage VARCHAR(300),
    research_focus JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS organisations_kind_region_idx ON organisations(kind, region);

-- 5. Authors
CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    normalized_name VARCHAR(200) NOT NULL,
    orcid VARCHAR(50) UNIQUE,
    homepage VARCHAR(300),
    primary_affiliation_id INTEGER REFERENCES organisations(id) ON DELETE SET NULL,
    stats JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS authors_normalized_idx ON authors(normalized_name);
CREATE INDEX IF NOT EXISTS authors_affiliation_idx ON authors(primary_affiliation_id);

-- 6. Extend benchmarks with optional FK references
ALTER TABLE benchmarks
    ADD COLUMN IF NOT EXISTS task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS dataset_id INTEGER REFERENCES datasets(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS evidence_source VARCHAR(50);

CREATE INDEX IF NOT EXISTS benchmarks_task_id_dataset_id_idx ON benchmarks(task_id, dataset_id);
CREATE INDEX IF NOT EXISTS benchmarks_metric_idx ON benchmarks(metric);

-- 7. Paper ↔ Technique/Task/Dataset mappings
CREATE TABLE IF NOT EXISTS paper_techniques (
    paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,
    technique_id INTEGER REFERENCES techniques(id) ON DELETE CASCADE,
    role VARCHAR(50),
    confidence FLOAT DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    evidence_source VARCHAR(50),
    notes TEXT,
    PRIMARY KEY (paper_id, technique_id)
);
CREATE INDEX IF NOT EXISTS paper_techniques_technique_role_idx ON paper_techniques(technique_id, role);
CREATE INDEX IF NOT EXISTS paper_techniques_paper_idx ON paper_techniques(paper_id);

CREATE TABLE IF NOT EXISTS paper_tasks (
    paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    evidence_source VARCHAR(50),
    notes TEXT,
    PRIMARY KEY (paper_id, task_id)
);
CREATE INDEX IF NOT EXISTS paper_tasks_task_idx ON paper_tasks(task_id);
CREATE INDEX IF NOT EXISTS paper_tasks_paper_idx ON paper_tasks(paper_id);

CREATE TABLE IF NOT EXISTS paper_datasets (
    paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,
    dataset_id INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    usage_type VARCHAR(50),
    notes TEXT,
    PRIMARY KEY (paper_id, dataset_id)
);
CREATE INDEX IF NOT EXISTS paper_datasets_dataset_idx ON paper_datasets(dataset_id, usage_type);
CREATE INDEX IF NOT EXISTS paper_datasets_paper_idx ON paper_datasets(paper_id);

-- 8. Paper authorship details
CREATE TABLE IF NOT EXISTS paper_authors (
    paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
    author_order INTEGER,
    is_corresponding BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (paper_id, author_id)
);
CREATE INDEX IF NOT EXISTS paper_authors_author_idx ON paper_authors(author_id);
CREATE INDEX IF NOT EXISTS paper_authors_order_idx ON paper_authors(paper_id, author_order);

-- 9. Author affiliation history
CREATE TABLE IF NOT EXISTS author_organisations (
    id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
    organisation_id INTEGER REFERENCES organisations(id) ON DELETE CASCADE,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    role VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(author_id, organisation_id, start_date, end_date)
);
CREATE INDEX IF NOT EXISTS author_organisations_author_idx ON author_organisations(author_id);
CREATE INDEX IF NOT EXISTS author_organisations_org_idx ON author_organisations(organisation_id);

-- 10. Technique relationships
CREATE TABLE IF NOT EXISTS technique_relationships (
    technique_a_id INTEGER REFERENCES techniques(id) ON DELETE CASCADE,
    technique_b_id INTEGER REFERENCES techniques(id) ON DELETE CASCADE,
    relation_type VARCHAR(50) NOT NULL,
    weight FLOAT,
    first_seen_paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (technique_a_id, technique_b_id),
    CHECK (technique_a_id < technique_b_id)
);
CREATE INDEX IF NOT EXISTS technique_relationships_type_idx ON technique_relationships(relation_type);

-- 11. Technique ↔ Benchmark association
CREATE TABLE IF NOT EXISTS technique_benchmarks (
    technique_id INTEGER REFERENCES techniques(id) ON DELETE CASCADE,
    benchmark_id INTEGER REFERENCES benchmarks(id) ON DELETE CASCADE,
    delta_from_sota FLOAT,
    sota_paper_id VARCHAR(50) REFERENCES papers(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (technique_id, benchmark_id)
);
CREATE INDEX IF NOT EXISTS technique_benchmarks_delta_idx ON technique_benchmarks(delta_from_sota);

-- 12. Data hygiene backfills
UPDATE benchmarks
SET evidence_source = COALESCE(evidence_source, 'legacy'),
    task = COALESCE(task, 'unknown'),
    dataset = COALESCE(dataset, 'unknown');
