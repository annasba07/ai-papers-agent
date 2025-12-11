#!/usr/bin/env python3
"""
Enrich papers with GitHub repository signals.
Run from backend directory: python scripts/enrich_github_signals.py

This script:
1. Finds papers with GitHub URLs (from code_repos or deep_analysis)
2. Fetches repository stats from GitHub API
3. Saves external_signals to database

Supports rate limiting and can be run incrementally.
"""
import asyncio
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db
from app.services.github_enricher import GitHubEnricher, get_external_signals_service


async def get_papers_needing_enrichment(db, limit: int = 100, force_refresh: bool = False):
    """
    Get papers that have GitHub URLs but no external signals.

    Args:
        db: Database connection
        limit: Max papers to fetch
        force_refresh: Re-enrich papers even if they have signals
    """
    if force_refresh:
        # Get papers with code_repos that contain github.com
        query = """
            SELECT
                id,
                title,
                code_repos,
                deep_analysis,
                external_signals
            FROM papers
            WHERE (
                code_repos::text LIKE '%github.com%'
                OR deep_analysis::text LIKE '%github.com%'
            )
            ORDER BY citation_count DESC NULLS LAST
            LIMIT :limit
        """
    else:
        # Get papers that need enrichment (no external_signals or stale)
        query = """
            SELECT
                id,
                title,
                code_repos,
                deep_analysis,
                external_signals
            FROM papers
            WHERE (
                code_repos::text LIKE '%github.com%'
                OR deep_analysis::text LIKE '%github.com%'
            )
            AND (
                external_signals IS NULL
                OR external_signals->>'github' IS NULL
                OR (external_signals->'github'->>'updated_at')::timestamp < NOW() - INTERVAL '7 days'
            )
            ORDER BY citation_count DESC NULLS LAST
            LIMIT :limit
        """

    results = await db.fetch_all(query, {"limit": limit})

    return [
        {
            "id": r["id"],
            "title": r["title"],
            "code_repos": r["code_repos"],
            "deep_analysis": r["deep_analysis"],
            "external_signals": r["external_signals"]
        }
        for r in results
    ]


async def enrich_batch(papers: list, db, enricher: GitHubEnricher):
    """Enrich a batch of papers."""
    results = await enricher.enrich_papers_batch(papers, batch_size=5, delay_between_batches=2.0)

    saved = 0
    for result in results:
        paper_id = result["paper_id"]
        signals = result["signals"]

        if signals.get("github", {}).get("repos"):
            success = await enricher.save_signals(paper_id, signals, db)
            if success:
                saved += 1

    return saved


async def main():
    parser = argparse.ArgumentParser(description="Enrich papers with GitHub signals")
    parser.add_argument("--limit", type=int, default=100, help="Max papers to process")
    parser.add_argument("--force", action="store_true", help="Re-enrich even with existing signals")
    parser.add_argument("--batch-size", type=int, default=10, help="Papers per batch")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("GitHub Signals Enrichment")
    print("=" * 60)

    # Connect to database using async databases library
    await connect_db()
    db = database
    enricher = GitHubEnricher()

    try:
        # Check for GitHub token
        if enricher.token:
            print(f"GitHub Token: Found (authenticated mode)")
        else:
            print("GitHub Token: Not found (unauthenticated - 60 req/hr limit)")
            print("Set GITHUB_TOKEN env var for higher limits")

        print(f"\nFetching papers needing enrichment (limit={args.limit})...")
        papers = await get_papers_needing_enrichment(db, args.limit, args.force)
        print(f"Found {len(papers)} papers with GitHub URLs")

        if not papers:
            print("No papers to enrich!")
            return

        # Process in batches
        total_saved = 0
        batch_size = args.batch_size

        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]
            print(f"\nProcessing batch {i // batch_size + 1}/{(len(papers) + batch_size - 1) // batch_size}...")

            try:
                saved = await enrich_batch(batch, db, enricher)
                total_saved += saved
                print(f"  Saved {saved} papers")

                # Check rate limit
                if enricher.rate_limit_remaining < 10:
                    wait_time = 60
                    if enricher.rate_limit_reset:
                        wait_time = max(60, (enricher.rate_limit_reset - datetime.now()).seconds + 5)
                    print(f"  Rate limit low ({enricher.rate_limit_remaining}), waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)

            except Exception as e:
                print(f"  Error: {e}")
                continue

        elapsed = time.time() - start
        print("\n" + "=" * 60)
        print(f"Complete!")
        print(f"Papers processed: {len(papers)}")
        print(f"Papers enriched: {total_saved}")
        print(f"Time: {elapsed:.1f}s")
        print("=" * 60)
    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
