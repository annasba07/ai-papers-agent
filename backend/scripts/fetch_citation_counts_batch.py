#!/usr/bin/env python3
"""
Fetch citation counts using Semantic Scholar batch API.
Run from backend directory: python scripts/fetch_citation_counts_batch.py

Uses the batch API to efficiently fetch citation counts for papers missing them.
14K papers = 28 API calls (500 per batch) = ~1 minute!
"""
import asyncio
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db
from app.services.providers.semantic_scholar_provider import get_semantic_scholar_provider


async def get_papers_missing_citations(db, limit: int = None) -> list:
    """Get paper IDs that are missing citation counts."""
    query = """
        SELECT id FROM papers
        WHERE citation_count = 0 OR citation_count IS NULL
        ORDER BY published_date DESC
    """
    if limit:
        query += f" LIMIT {limit}"
    rows = await db.fetch_all(query)
    return [row["id"] for row in rows]


async def main():
    parser = argparse.ArgumentParser(description="Fetch citation counts (BATCH API)")
    parser.add_argument("--max-papers", type=int, default=None, help="Max papers to process (None = all)")
    parser.add_argument("--batch-size", type=int, default=500, help="Papers per batch API call")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Citation Count Fetcher (BATCH MODE)")
    print(f"Max Papers: {args.max_papers or 'ALL'}, Batch Size: {args.batch_size}")
    print("=" * 60)

    await connect_db()
    db = database
    provider = get_semantic_scholar_provider()

    try:
        # Get papers missing citation counts
        print("\nFinding papers missing citation counts...")
        paper_ids = await get_papers_missing_citations(db, args.max_papers)
        print(f"Found {len(paper_ids)} papers without citation counts")

        if not paper_ids:
            print("No papers to update!")
            return

        # Stats
        stats = {
            "papers_processed": 0,
            "updated": 0,
            "not_found": 0,
            "api_calls": 0,
        }

        # Process in batches
        for i in range(0, len(paper_ids), args.batch_size):
            batch = paper_ids[i:i + args.batch_size]
            batch_start = time.time()

            print(f"\nBatch {i//args.batch_size + 1}: Fetching for {len(batch)} papers...")

            # Use the batch API to get paper details with citation counts
            paper_data = await provider.batch_get_paper_details(batch, fields=["citationCount"])
            stats["api_calls"] += 1

            # Update citation counts in database
            for paper_id, details in paper_data.items():
                stats["papers_processed"] += 1
                citation_count = details.get("citationCount", 0)

                if citation_count is not None:
                    try:
                        await db.execute(
                            "UPDATE papers SET citation_count = :count WHERE id = :id",
                            {"count": citation_count, "id": paper_id}
                        )
                        stats["updated"] += 1
                    except Exception as e:
                        print(f"  Error updating {paper_id}: {e}")
                else:
                    stats["not_found"] += 1

            batch_time = time.time() - batch_start
            print(f"  Processed in {batch_time:.1f}s - Updated: {stats['updated']}")

        # Final stats
        elapsed = time.time() - start
        result = await db.fetch_one(
            "SELECT COUNT(*) as cnt FROM papers WHERE citation_count > 0"
        )

        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Papers processed: {stats['papers_processed']}")
        print(f"Citation counts updated: {stats['updated']}")
        print(f"Not found in Semantic Scholar: {stats['not_found']}")
        print(f"Papers with citations in DB: {result['cnt']}")
        print(f"API calls made: {stats['api_calls']}")
        print(f"Time: {elapsed:.1f}s")
        print("=" * 60)

    finally:
        await provider.close()
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
