#!/usr/bin/env python3
"""
Backfill deep analysis for papers using Gemini 2.5 Flash Lite.
Uses the DeepEnrichmentService with parallel processing.

Run: python scripts/backfill_deep_analysis.py --max-papers 3000
"""
import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import connect_db, disconnect_db
from app.services.deep_enrichment_service import get_deep_enrichment_service


async def main():
    parser = argparse.ArgumentParser(description="Backfill deep analysis for papers")
    parser.add_argument("--max-papers", type=int, default=3000, help="Max papers to process")
    parser.add_argument("--priority", type=str, default=None,
                        help="SQL filter for priority (e.g., 'impact_score >= 7')")
    args = parser.parse_args()

    print("=" * 60)
    print("Deep Analysis Backfill")
    print(f"Model: gemini-2.5-flash-lite")
    print(f"Max papers: {args.max_papers}")
    print(f"Priority filter: {args.priority or 'None'}")
    print("=" * 60)

    await connect_db()

    try:
        service = get_deep_enrichment_service()

        if not service.enabled:
            print("ERROR: Deep enrichment service not enabled (missing API key)")
            return

        status = service.get_status()
        print(f"\nService status:")
        print(f"  PDFs available: {status['pdf_count']}")
        print(f"  Model: {status['model']}")

        print(f"\nStarting deep enrichment with {args.max_papers} papers...")
        print("This uses 50 concurrent workers for parallel processing.\n")

        stats = await service.run_deep_enrichment(
            max_papers=args.max_papers,
            priority_filter=args.priority,
            skip_existing=True
        )

        print("\n" + "=" * 60)
        print("COMPLETE!")
        print(f"Processed: {stats.processed}")
        print(f"Succeeded: {stats.succeeded}")
        print(f"Failed: {stats.failed}")
        print(f"Skipped (no PDF): {stats.skipped_no_pdf}")
        print(f"Time: {stats.end_time - stats.start_time:.1f}s")
        if stats.processed > 0:
            print(f"Rate: {stats.processed / ((stats.end_time - stats.start_time) / 60):.1f} papers/min")
        print("=" * 60)

    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
