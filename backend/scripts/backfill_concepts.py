#!/usr/bin/env python3
"""
Backfill concepts for papers using Gemini Flash 2.5.
Run from backend directory: python scripts/backfill_concepts.py

This script uses the existing ConceptExtractionService to extract concepts
for papers that don't have them yet.
"""
import asyncio
import os
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db
from app.services.concept_extraction_service import get_concept_extraction_service
from app.core.config import settings


async def get_papers_without_concepts(db, limit: int = None, offset: int = 0) -> list:
    """Get papers that don't have concepts extracted yet."""
    query = """
        SELECT p.id, p.title, p.abstract as summary
        FROM papers p
        LEFT JOIN paper_concepts pc ON p.id = pc.paper_id
        WHERE pc.paper_id IS NULL
        AND p.abstract IS NOT NULL
        AND LENGTH(p.abstract) > 100
        ORDER BY p.published_date DESC
        OFFSET :offset
    """
    if limit:
        query += f" LIMIT {limit}"

    rows = await db.fetch_all(query, {"offset": offset})
    return [dict(r) for r in rows]


async def get_concept_stats(db) -> dict:
    """Get current concept extraction stats."""
    total_papers = await db.fetch_one("SELECT COUNT(*) as cnt FROM papers")
    with_concepts = await db.fetch_one(
        "SELECT COUNT(DISTINCT paper_id) as cnt FROM paper_concepts"
    )
    total_concepts = await db.fetch_one("SELECT COUNT(*) as cnt FROM concepts")

    return {
        "total_papers": total_papers["cnt"],
        "papers_with_concepts": with_concepts["cnt"],
        "papers_without_concepts": total_papers["cnt"] - with_concepts["cnt"],
        "total_concepts": total_concepts["cnt"],
    }


async def main():
    parser = argparse.ArgumentParser(description="Backfill concepts using Gemini")
    parser.add_argument("--limit", type=int, default=1000, help="Max papers to process")
    parser.add_argument("--batch-size", type=int, default=10, help="Papers per batch")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between papers (seconds)")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N papers")
    parser.add_argument("--dry-run", action="store_true", help="Just count papers, don't process")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Concept Extraction Backfill")
    print(f"Model: {settings.GEMINI_MODEL}")
    print(f"Limit: {args.limit}, Batch: {args.batch_size}, Delay: {args.delay}s")
    print("=" * 60)

    await connect_db()
    db = database

    try:
        # Get current stats
        stats = await get_concept_stats(db)
        print(f"\nCurrent Status:")
        print(f"  Total papers: {stats['total_papers']}")
        print(f"  With concepts: {stats['papers_with_concepts']}")
        print(f"  Without concepts: {stats['papers_without_concepts']}")
        print(f"  Total concepts: {stats['total_concepts']}")

        if args.dry_run:
            print("\n[DRY RUN] Would process papers but not extracting.")
            return

        if stats['papers_without_concepts'] == 0:
            print("\nAll papers already have concepts!")
            return

        # Get the service
        service = get_concept_extraction_service()

        # Process in chunks to avoid memory issues
        total_processed = 0
        total_concepts_extracted = 0
        total_failed = 0

        papers_to_process = min(args.limit, stats['papers_without_concepts'])
        print(f"\nProcessing {papers_to_process} papers...")

        while total_processed < papers_to_process:
            # Get next batch
            batch_limit = min(args.batch_size, papers_to_process - total_processed)
            papers = await get_papers_without_concepts(
                db,
                limit=batch_limit,
                offset=args.offset
            )

            if not papers:
                print("No more papers to process!")
                break

            batch_num = (total_processed // args.batch_size) + 1
            print(f"\nBatch {batch_num}: Processing {len(papers)} papers...")
            batch_start = time.time()

            # Process batch using the service
            for i, paper in enumerate(papers):
                try:
                    concepts = await service.extract_concepts_for_paper(
                        paper, max_concepts=10
                    )
                    total_concepts_extracted += len(concepts)
                    total_processed += 1

                    print(f"  [{total_processed}/{papers_to_process}] "
                          f"{paper['title'][:50]}... -> {len(concepts)} concepts")

                    # Rate limiting
                    if i < len(papers) - 1:  # Don't sleep after last paper
                        await asyncio.sleep(args.delay)

                except Exception as e:
                    total_failed += 1
                    print(f"  ERROR processing {paper['id']}: {e}")
                    await asyncio.sleep(args.delay)

            batch_time = time.time() - batch_start
            rate = len(papers) / batch_time if batch_time > 0 else 0
            print(f"  Batch done in {batch_time:.1f}s ({rate:.1f} papers/sec)")

        # Final stats
        elapsed = time.time() - start
        final_stats = await get_concept_stats(db)

        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Papers processed: {total_processed}")
        print(f"Concepts extracted: {total_concepts_extracted}")
        print(f"Failed: {total_failed}")
        print(f"Success rate: {(total_processed - total_failed) / max(1, total_processed) * 100:.1f}%")
        print(f"\nFinal coverage:")
        print(f"  Papers with concepts: {final_stats['papers_with_concepts']} "
              f"({final_stats['papers_with_concepts'] / final_stats['total_papers'] * 100:.1f}%)")
        print(f"  Total concepts: {final_stats['total_concepts']}")
        print(f"\nTime: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print("=" * 60)

    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
