#!/usr/bin/env python3
"""
Capture daily metric snapshots for temporal tracking.
Run from backend directory: python scripts/capture_metric_snapshots.py

This script captures point-in-time metrics for papers:
- Citation count and velocity
- GitHub stars/forks
- HuggingFace downloads
- Buzz score (composite metric)

Should be run daily (cron job) to build up temporal data.
"""
import asyncio
import sys
import time
import argparse
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db
from app.services.temporal_tracker import get_temporal_service


async def get_papers_needing_snapshot(db, limit: int = None, today_only: bool = True):
    """
    Get papers that need metric snapshots.

    Args:
        db: Database connection
        limit: Max papers to fetch (None = all)
        today_only: Only get papers without today's snapshot
    """
    if today_only:
        query = """
            SELECT
                p.id,
                p.title,
                p.citation_count,
                p.influential_citation_count,
                p.quality_score,
                p.published_date,
                p.external_signals
            FROM papers p
            LEFT JOIN metric_snapshots ms ON p.id = ms.paper_id
                AND ms.snapshot_date = CURRENT_DATE
            WHERE ms.paper_id IS NULL
            ORDER BY p.citation_count DESC NULLS LAST
            LIMIT :limit
        """
    else:
        query = """
            SELECT
                p.id,
                p.title,
                p.citation_count,
                p.influential_citation_count,
                p.quality_score,
                p.published_date,
                p.external_signals
            FROM papers p
            ORDER BY p.citation_count DESC NULLS LAST
            LIMIT :limit
        """

    results = await db.fetch_all(query, {"limit": limit or 100000})

    return [
        {
            "id": r["id"],
            "title": r["title"],
            "citation_count": r["citation_count"],
            "influential_citation_count": r["influential_citation_count"],
            "quality_score": r["quality_score"],
            "published_date": r["published_date"],
            "external_signals": r["external_signals"]
        }
        for r in results
    ]


async def main():
    parser = argparse.ArgumentParser(description="Capture daily metric snapshots")
    parser.add_argument("--limit", type=int, default=None, help="Max papers to process (default: all)")
    parser.add_argument("--force", action="store_true", help="Re-capture even if today's snapshot exists")
    parser.add_argument("--batch-size", type=int, default=100, help="Papers per batch logging")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Daily Metric Snapshot Capture")
    print(f"Date: {date.today().isoformat()}")
    print("=" * 60)

    # Connect to database using async databases library
    await connect_db()
    db = database
    service = get_temporal_service()

    try:
        print(f"\nFetching papers needing snapshots...")
        papers = await get_papers_needing_snapshot(db, args.limit, not args.force)
        print(f"Found {len(papers)} papers to process")

        if not papers:
            print("No papers need snapshots today!")
            return

        # Process papers
        captured = 0
        errors = 0
        batch_count = 0

        for i, paper in enumerate(papers):
            try:
                snapshot = await service.tracker.capture_snapshot(paper, db)
                if snapshot:
                    captured += 1
                    batch_count += 1

                # Progress logging
                if batch_count >= args.batch_size:
                    batch_count = 0
                    print(f"  Progress: {i+1}/{len(papers)} ({captured} captured)")

            except Exception as e:
                errors += 1
                if errors <= 10:  # Only print first 10 errors
                    print(f"  Error for {paper['id']}: {e}")

        elapsed = time.time() - start
        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Papers processed: {len(papers)}")
        print(f"Snapshots captured: {captured}")
        print(f"Errors: {errors}")
        print(f"Time: {elapsed:.1f}s")
        print(f"Rate: {len(papers)/elapsed:.1f} papers/sec")
        print("=" * 60)
    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
