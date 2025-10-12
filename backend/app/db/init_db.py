"""
Database initialization script for Supabase PostgreSQL

Creates all tables, indexes, and triggers for the knowledge graph.

Usage:
    python -m app.db.init_db
"""
import asyncio
import os
from sqlalchemy import text
from app.db.database import database, engine
from app.db.models import Base


# SQL for pgvector extension and triggers
EXTENSION_SQL = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
"""

TRIGGERS_SQL = """
-- Auto-update search_vector on paper insert/update
CREATE OR REPLACE FUNCTION papers_search_vector_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.abstract, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.concepts_array, ' '), '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS papers_search_vector_update ON papers;
CREATE TRIGGER papers_search_vector_update
    BEFORE INSERT OR UPDATE ON papers
    FOR EACH ROW EXECUTE FUNCTION papers_search_vector_trigger();

-- Auto-update citation counts
CREATE OR REPLACE FUNCTION update_citation_count() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Increment cited paper's citation count
        UPDATE papers
        SET citation_count = citation_count + 1,
            influential_citation_count = CASE
                WHEN NEW.is_influential THEN influential_citation_count + 1
                ELSE influential_citation_count
            END
        WHERE id = NEW.cited_paper_id;
    ELSIF TG_OP = 'DELETE' THEN
        -- Decrement cited paper's citation count
        UPDATE papers
        SET citation_count = GREATEST(0, citation_count - 1),
            influential_citation_count = CASE
                WHEN OLD.is_influential THEN GREATEST(0, influential_citation_count - 1)
                ELSE influential_citation_count
            END
        WHERE id = OLD.cited_paper_id;
    ELSIF TG_OP = 'UPDATE' AND OLD.is_influential != NEW.is_influential THEN
        -- Update influential count if flag changed
        UPDATE papers
        SET influential_citation_count = CASE
            WHEN NEW.is_influential THEN influential_citation_count + 1
            ELSE GREATEST(0, influential_citation_count - 1)
        END
        WHERE id = NEW.cited_paper_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS citation_count_trigger ON citations;
CREATE TRIGGER citation_count_trigger
    AFTER INSERT OR DELETE OR UPDATE ON citations
    FOR EACH ROW EXECUTE FUNCTION update_citation_count();

-- Auto-update concept paper counts
CREATE OR REPLACE FUNCTION update_concept_paper_count() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE concepts
        SET paper_count = paper_count + 1,
            last_seen_date = CURRENT_TIMESTAMP
        WHERE id = NEW.concept_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE concepts
        SET paper_count = GREATEST(0, paper_count - 1)
        WHERE id = OLD.concept_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS concept_paper_count_trigger ON paper_concepts;
CREATE TRIGGER concept_paper_count_trigger
    AFTER INSERT OR DELETE ON paper_concepts
    FOR EACH ROW EXECUTE FUNCTION update_concept_paper_count();
"""

# Materialized views for common queries
VIEWS_SQL = """
-- Top papers by citations (refreshed periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS top_papers_by_citations AS
SELECT
    id,
    title,
    category,
    citation_count,
    influential_citation_count,
    quality_score,
    published_date
FROM papers
WHERE citation_count > 0
ORDER BY citation_count DESC
LIMIT 1000;

CREATE INDEX IF NOT EXISTS top_papers_by_citations_idx
    ON top_papers_by_citations(citation_count DESC);

-- Trending concepts (papers in last 30 days)
CREATE MATERIALIZED VIEW IF NOT EXISTS trending_concepts AS
SELECT
    c.id,
    c.name,
    c.category,
    COUNT(DISTINCT pc.paper_id) as recent_paper_count,
    AVG(pc.relevance) as avg_relevance
FROM concepts c
JOIN paper_concepts pc ON c.id = pc.concept_id
JOIN papers p ON pc.paper_id = p.id
WHERE p.published_date > CURRENT_DATE - INTERVAL '30 days'
GROUP BY c.id, c.name, c.category
HAVING COUNT(DISTINCT pc.paper_id) >= 3
ORDER BY recent_paper_count DESC
LIMIT 500;

CREATE INDEX IF NOT EXISTS trending_concepts_idx
    ON trending_concepts(recent_paper_count DESC);
"""


async def create_extensions():
    """Create required PostgreSQL extensions"""
    print("📦 Creating PostgreSQL extensions...")
    try:
        async with database.transaction():
            await database.execute(text(EXTENSION_SQL))
        print("✅ Extensions created successfully")
    except Exception as e:
        print(f"⚠️  Extension creation warning (may already exist): {e}")


def create_tables():
    """Create all tables using SQLAlchemy models"""
    print("📊 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")


async def create_triggers():
    """Create triggers for auto-updating denormalized fields"""
    print("⚡ Creating triggers...")
    try:
        async with database.transaction():
            await database.execute(text(TRIGGERS_SQL))
        print("✅ Triggers created successfully")
    except Exception as e:
        print(f"❌ Trigger creation failed: {e}")
        raise


async def create_views():
    """Create materialized views for common queries"""
    print("👁️  Creating materialized views...")
    try:
        async with database.transaction():
            await database.execute(text(VIEWS_SQL))
        print("✅ Views created successfully")
    except Exception as e:
        print(f"⚠️  View creation warning: {e}")


async def verify_setup():
    """Verify database setup by running simple queries"""
    print("\n🔍 Verifying database setup...")

    try:
        # Check pgvector
        result = await database.fetch_one(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        if result:
            print("✅ pgvector extension is active")
        else:
            print("❌ pgvector extension not found")
            return False

        # Check tables
        tables = ['papers', 'concepts', 'paper_concepts', 'citations', 'benchmarks']
        for table in tables:
            result = await database.fetch_one(
                text(f"SELECT COUNT(*) as count FROM {table}")
            )
            print(f"✅ Table '{table}' exists (rows: {result['count']})")

        # Check indexes
        result = await database.fetch_all(
            text("""
                SELECT tablename, indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND tablename IN ('papers', 'concepts', 'citations')
                ORDER BY tablename, indexname
            """)
        )
        print(f"✅ Created {len(result)} indexes")

        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


async def init_database():
    """Initialize the complete database"""
    print("=" * 60)
    print("🚀 Initializing Knowledge Graph Database")
    print("=" * 60)

    # Connect to database
    await database.connect()
    print("✅ Connected to Supabase PostgreSQL\n")

    try:
        # Step 1: Extensions
        await create_extensions()

        # Step 2: Tables
        create_tables()

        # Step 3: Triggers
        await create_triggers()

        # Step 4: Views
        await create_views()

        # Step 5: Verify
        success = await verify_setup()

        print("\n" + "=" * 60)
        if success:
            print("🎉 Database initialization complete!")
            print("\nNext steps:")
            print("1. Add SUPABASE_DATABASE_URL to .env")
            print("2. Run embedding service to populate vectors")
            print("3. Ingest papers from arXiv")
            print("4. Start querying the knowledge graph!")
        else:
            print("⚠️  Initialization completed with warnings")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        raise
    finally:
        await database.disconnect()


async def drop_all_tables():
    """Drop all tables (use with caution!)"""
    print("⚠️  WARNING: Dropping all tables...")
    response = input("Are you sure? Type 'yes' to confirm: ")
    if response.lower() != 'yes':
        print("Aborted.")
        return

    await database.connect()
    try:
        # Drop views first
        await database.execute(text("DROP MATERIALIZED VIEW IF EXISTS top_papers_by_citations CASCADE"))
        await database.execute(text("DROP MATERIALIZED VIEW IF EXISTS trending_concepts CASCADE"))

        # Drop triggers
        await database.execute(text("DROP TRIGGER IF EXISTS papers_search_vector_update ON papers"))
        await database.execute(text("DROP TRIGGER IF EXISTS citation_count_trigger ON citations"))
        await database.execute(text("DROP TRIGGER IF EXISTS concept_paper_count_trigger ON paper_concepts"))

        # Drop tables
        Base.metadata.drop_all(bind=engine)

        print("✅ All tables dropped")
    finally:
        await database.disconnect()


async def refresh_views():
    """Refresh materialized views"""
    print("🔄 Refreshing materialized views...")
    await database.connect()
    try:
        await database.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY top_papers_by_citations"))
        await database.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY trending_concepts"))
        print("✅ Views refreshed")
    finally:
        await database.disconnect()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "drop":
            asyncio.run(drop_all_tables())
        elif command == "refresh":
            asyncio.run(refresh_views())
        else:
            print(f"Unknown command: {command}")
            print("Available commands: drop, refresh")
    else:
        # Default: initialize database
        asyncio.run(init_database())
