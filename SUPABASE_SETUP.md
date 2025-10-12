# Supabase PostgreSQL Setup Guide

Complete guide to setting up the knowledge graph database with Supabase.

## Why Supabase?

- ✅ Managed PostgreSQL with pgvector support
- ✅ Automatic backups and scaling
- ✅ Built-in connection pooling
- ✅ Free tier for development (500MB database)
- ✅ Easy dashboard for monitoring queries
- ✅ Auto-generated REST API (optional)

---

## Step 1: Create Supabase Project

### 1.1 Sign up and create project

1. Go to [supabase.com](https://supabase.com) and sign up
2. Click "New Project"
3. Choose a name (e.g., "ai-papers-knowledge-graph")
4. Set a strong database password (save it!)
5. Choose a region close to your users
6. Wait ~2 minutes for project setup

### 1.2 Get connection string

1. In your Supabase dashboard, go to **Settings** → **Database**
2. Scroll to **Connection string** section
3. **Choose the right connection mode:**
   - **Session Mode (Recommended for this project)** - Use for persistent connections with connection pooling
   - Transaction Mode - For serverless/edge functions only
   - Direct Connection - For persistent servers (IPv6 only)

4. Copy the **Session Mode** connection string (looks like):
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password

**Why Session Mode?** Our FastAPI backend uses connection pooling (databases + asyncpg), which works best with Session Mode. Transaction Mode requires disabling prepared statements and is designed for transient connections.

---

## Step 2: Configure Environment

### 2.1 Update .env file

Add your Supabase connection URL to `backend/.env`:

```bash
# Supabase PostgreSQL
SUPABASE_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres

# OpenAI for embeddings
OPENAI_API_KEY=sk-...

# Optional: Connection pooling (Supabase provides this)
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### 2.2 Install dependencies

```bash
cd backend

# Install database dependencies
pip install databases asyncpg sqlalchemy psycopg2-binary pgvector

# Or use requirements file (includes all)
pip install -r requirements.txt
```

---

## Step 3: Enable pgvector Extension

Supabase includes pgvector, but you need to enable it:

### Option A: Via Supabase Dashboard (Recommended)

1. Go to **SQL Editor** in your Supabase dashboard
2. Run this SQL:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;
   ```
3. Click "Run"

**Note**: Supabase recommends creating extensions in the `extensions` schema for better organization and security.

### Option B: Via Migration Script

The init script will attempt to enable it automatically:
```bash
python -m app.db.init_db
```

---

## Step 4: Initialize Database

### 4.1 Run migration script

```bash
cd backend

# Initialize all tables, indexes, triggers, and views
python -m app.db.init_db
```

Expected output:
```
============================================================
🚀 Initializing Knowledge Graph Database
============================================================
✅ Connected to Supabase PostgreSQL

📦 Creating PostgreSQL extensions...
✅ Extensions created successfully
📊 Creating tables...
✅ Tables created successfully
⚡ Creating triggers...
✅ Triggers created successfully
👁️  Creating materialized views...
✅ Views created successfully

🔍 Verifying database setup...
✅ pgvector extension is active
✅ Table 'papers' exists (rows: 0)
✅ Table 'concepts' exists (rows: 0)
✅ Table 'paper_concepts' exists (rows: 0)
✅ Table 'citations' exists (rows: 0)
✅ Table 'benchmarks' exists (rows: 0)
✅ Created 23 indexes

============================================================
🎉 Database initialization complete!

Next steps:
1. Add SUPABASE_DATABASE_URL to .env
2. Run embedding service to populate vectors
3. Ingest papers from arXiv
4. Start querying the knowledge graph!
============================================================
```

### 4.2 Verify in Supabase Dashboard

1. Go to **Table Editor** in Supabase dashboard
2. You should see these tables:
   - `papers` - Core paper metadata with embeddings
   - `concepts` - Extracted research concepts
   - `paper_concepts` - Many-to-many relationships
   - `citations` - Citation graph
   - `benchmarks` - Performance metrics
   - `paper_relationships` - Precomputed similarities

3. Click on **papers** table to see the schema:
   - `embedding` column should have type `vector(1536)`
   - `search_vector` column should have type `tsvector`

---

## Step 5: Test Database Connection

Create a simple test script:

```python
# test_db_connection.py
import asyncio
from app.db.database import database

async def test_connection():
    await database.connect()

    # Test basic query
    result = await database.fetch_one(
        "SELECT COUNT(*) as count FROM papers"
    )
    print(f"✅ Connected! Papers table has {result['count']} rows")

    # Test pgvector
    result = await database.fetch_one(
        "SELECT extname FROM pg_extension WHERE extname = 'vector'"
    )
    if result:
        print("✅ pgvector extension is active")
    else:
        print("❌ pgvector not enabled")

    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(test_connection())
```

Run it:
```bash
cd backend
python test_db_connection.py
```

---

## Step 6: Database Schema

### Tables Created

1. **papers** (main table)
   - `id` - arXiv ID (primary key)
   - `title`, `abstract`, `authors`
   - `embedding` - 1536-dimensional vector (OpenAI)
   - `citation_count`, `influential_citation_count` (denormalized)
   - `ai_analysis` - JSONB with AI insights
   - `concepts_array` - Array of concept names
   - `search_vector` - Full-text search (auto-updated)

2. **concepts** (research topics)
   - `id`, `name`, `normalized_name`
   - `category` - architecture, technique, dataset, etc.
   - `paper_count` - Denormalized count (auto-updated)
   - `embedding` - Optional vector for concept similarity

3. **paper_concepts** (relationships)
   - `paper_id`, `concept_id` (composite primary key)
   - `relevance` - 0.0 to 1.0 score
   - `confidence`, `extraction_method`

4. **citations** (directed graph)
   - `citing_paper_id`, `cited_paper_id`
   - `is_influential` - Boolean flag
   - `context_snippet`, `section`

5. **benchmarks** (performance metrics)
   - `paper_id`, `task`, `dataset`, `metric`
   - `value` - Performance score
   - `model_name`, `model_size`, `compute_cost`

6. **paper_relationships** (precomputed)
   - `paper_a_id`, `paper_b_id`
   - `semantic_similarity`, `concept_similarity`
   - `citation_distance`

### Indexes Created (23 total)

**Vector search:**
- `papers_embedding_idx` - HNSW index for fast cosine similarity

**Citation queries:**
- `citations_citing_idx`, `citations_cited_idx` - Graph traversal
- `citations_year_idx` - Temporal analysis

**Concept queries:**
- `paper_concepts_concept_relevance_idx` - Find papers by concept
- `concepts_category_count_idx` - Top concepts by category

**Full-text search:**
- `papers_search_vector_idx` - GIN index for tsvector

**Performance:**
- `papers_quality_published_idx` - Leaderboards
- `benchmarks_task_dataset_value_idx` - Benchmark rankings

### Triggers (Auto-updating)

1. **papers_search_vector_trigger**
   - Automatically updates `search_vector` when title/abstract changes
   - Combines title (weight A), abstract (weight B), concepts (weight C)

2. **citation_count_trigger**
   - Automatically updates `citation_count` when citations added/removed
   - Updates `influential_citation_count` based on `is_influential` flag

3. **concept_paper_count_trigger**
   - Automatically updates concept `paper_count` when papers linked/unlinked
   - Updates `last_seen_date` for trending analysis

---

## Step 7: Monitoring and Maintenance

### Check database usage

In Supabase dashboard → **Settings** → **Database**:
- See current database size
- Monitor connection pool usage
- View slow queries

### Refresh materialized views

Views should be refreshed periodically (e.g., daily):

```bash
# Via script
python -m app.db.init_db refresh

# Or via SQL in Supabase dashboard
REFRESH MATERIALIZED VIEW CONCURRENTLY top_papers_by_citations;
REFRESH MATERIALIZED VIEW CONCURRENTLY trending_concepts;
```

### Monitor performance

```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Check table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Step 8: Backup and Recovery

### Automatic backups (Supabase)

- Free tier: Daily backups, 7-day retention
- Pro tier: Point-in-time recovery

### Manual backup

```bash
# Export data via Supabase dashboard
# Settings → Database → Database export

# Or via pg_dump
pg_dump "postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres" > backup.sql
```

### Restore

```bash
# Via Supabase dashboard
# Settings → Database → Database restore

# Or via psql
psql "postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres" < backup.sql
```

---

## Troubleshooting

### Error: "extension 'vector' does not exist"

**Solution**: Enable pgvector via Supabase SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Error: "password authentication failed"

**Solution**:
1. Check your password is correct in connection string
2. Reset database password in Supabase dashboard → Settings → Database

### Error: "too many connections"

**Solution**:
1. Supabase free tier has connection limits
2. Use connection pooling (already configured in database.py)
3. Or upgrade to Pro tier for more connections

### Slow vector queries

**Solution**:
1. Ensure HNSW index exists (Supabase recommended):
   ```sql
   SELECT indexname FROM pg_indexes WHERE tablename = 'papers' AND indexname LIKE '%embedding%';
   ```
2. If no index, create it:
   ```sql
   CREATE INDEX IF NOT EXISTS papers_embedding_idx ON papers USING hnsw (embedding vector_cosine_ops);
   ```

**Why HNSW?** Supabase recommends HNSW (Hierarchical Navigable Small World) over IVFFlat because:
- Adapts well to changing data - can be created immediately
- Better performance and robustness
- No parameter tuning needed (no 'lists' or 'probes')
- Self-optimizing as data grows

### Out of disk space (free tier)

**Solution**:
1. Free tier has 500MB limit
2. Clean old papers:
   ```sql
   DELETE FROM papers WHERE published_date < '2020-01-01';
   ```
3. Or upgrade to Pro tier (8GB included)

---

## Next Steps

After database setup is complete:

1. **✅ Phase 1: Database Layer** (DONE!)
   - [x] Supabase connection
   - [x] SQLAlchemy models
   - [x] Migration script

2. **Next: Phase 2: Services**
   - [ ] Embedding service (OpenAI)
   - [ ] Similarity search service
   - [ ] Citation graph service
   - [ ] Concept extraction service

3. **Then: Phase 3: API Endpoints**
   - [ ] GET /papers/similar/:id
   - [ ] GET /papers/:id/citations
   - [ ] GET /concepts/trending
   - [ ] GET /benchmarks/leaderboard

4. **Finally: Phase 4: Frontend**
   - [ ] Similar papers component
   - [ ] Citation graph visualization
   - [ ] Concept explorer
   - [ ] Benchmark leaderboards

---

## Useful Supabase Features

### Built-in REST API (optional)

Supabase auto-generates REST API for all tables:
```bash
# Get papers
curl https://xxxxx.supabase.co/rest/v1/papers \
  -H "apikey: YOUR_ANON_KEY"

# Search by concept
curl "https://xxxxx.supabase.co/rest/v1/paper_concepts?concept_id=eq.123" \
  -H "apikey: YOUR_ANON_KEY"
```

But we'll use our custom FastAPI for more control.

### Row Level Security (RLS)

For production, enable RLS in Supabase dashboard:
```sql
-- Allow public read access
ALTER TABLE papers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public papers read" ON papers
  FOR SELECT USING (true);

-- Restrict writes to service role
CREATE POLICY "Service papers write" ON papers
  FOR INSERT USING (auth.role() = 'service_role');
```

### Real-time subscriptions (optional)

Supabase supports real-time updates:
```javascript
// Subscribe to new papers
const subscription = supabase
  .from('papers')
  .on('INSERT', payload => {
    console.log('New paper:', payload.new)
  })
  .subscribe()
```

Useful for live dashboards!

---

## Performance Expectations

With Supabase + proper indexes:

| Query Type | Papers | Expected Time |
|------------|--------|---------------|
| Vector similarity | 100K | 20-50ms |
| Vector similarity | 1M | 50-100ms |
| Concept search | 1M | 10-30ms |
| Citation graph (1 hop) | 1M | 5-15ms |
| Citation graph (3 hops) | 1M | 50-200ms |
| Full-text search | 1M | 10-50ms |
| Benchmark leaderboard | 1M | 5-20ms |

**Goal**: All queries under 100ms for excellent UX.

---

## Cost Estimates

### Free tier (perfect for development)
- 500MB database
- 2GB bandwidth
- 50K monthly active users
- **Cost**: $0/month

### Pro tier (production)
- 8GB database
- 50GB bandwidth
- 100K monthly active users
- Daily backups
- **Cost**: $25/month

### Scale as needed
- Additional storage: $0.125/GB/month
- Additional bandwidth: $0.09/GB

For 1M papers with embeddings: ~10GB database = ~$25-30/month

---

**Setup complete!** Your knowledge graph is ready for data ingestion. 🚀
