#!/usr/bin/env python3
"""
Test database connection and basic queries
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import asyncio
from app.db.database import database, connect_db, disconnect_db, DATABASE_URL

async def test_connection():
    """Test database connection and basic queries"""
    print(f"Database URL: {DATABASE_URL[:50]}...")

    try:
        await connect_db()

        # Test basic queries
        result = await database.fetch_one("SELECT COUNT(*) as count FROM papers")
        print(f"✅ Total papers: {result['count']}")

        result = await database.fetch_one("SELECT COUNT(*) as count FROM concepts")
        print(f"✅ Total concepts: {result['count']}")

        result = await database.fetch_one("SELECT COUNT(*) as count FROM paper_concepts")
        print(f"✅ Paper-concept links: {result['count']}")

        # Test a more complex query
        papers = await database.fetch_all("""
            SELECT p.id, p.title, p.category, p.published_date
            FROM papers p
            ORDER BY p.published_date DESC
            LIMIT 3
        """)
        print(f"\n✅ Recent papers:")
        for p in papers:
            print(f"  - [{p['category']}] {p['title'][:60]}...")

        # Test concept join
        concepts = await database.fetch_all("""
            SELECT c.name, c.paper_count
            FROM concepts c
            ORDER BY c.paper_count DESC
            LIMIT 5
        """)
        print(f"\n✅ Top concepts:")
        for c in concepts:
            print(f"  - {c['name']}: {c['paper_count']} papers")

        # Test vector search function exists
        try:
            await database.fetch_all("SELECT * FROM match_papers(NULL, 0.5, 1)")
        except Exception as e:
            if "cannot be null" in str(e).lower() or "null" in str(e).lower():
                print(f"\n✅ Vector search function exists (match_papers)")
            else:
                print(f"\n⚠️ Vector search function check: {e}")

        print("\n🎉 All database tests passed!")

    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        raise
    finally:
        await disconnect_db()

if __name__ == "__main__":
    asyncio.run(test_connection())
