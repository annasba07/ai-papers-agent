#!/usr/bin/env python3
"""
Build citation network between papers using Semantic Scholar.
Run from backend directory: python scripts/build_citation_network.py

This script:
1. Updates citation counts for papers missing them
2. Builds citation edges between papers in our database
"""
import asyncio
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db
from app.services.citation_enrichment_service import get_citation_enrichment_service


async def main():
    parser = argparse.ArgumentParser(description="Build citation network")
    parser.add_argument("--max-papers", type=int, default=1000, help="Max papers to process")
    parser.add_argument("--update-counts", action="store_true", help="Update citation counts first")
    parser.add_argument("--build-edges", action="store_true", help="Build citation edges")
    parser.add_argument("--all", action="store_true", help="Do both update-counts and build-edges")
    args = parser.parse_args()

    if args.all:
        args.update_counts = True
        args.build_edges = True

    if not args.update_counts and not args.build_edges:
        print("Specify --update-counts, --build-edges, or --all")
        return

    start = time.time()
    print("=" * 60)
    print("Citation Network Builder")
    print(f"Max papers: {args.max_papers}")
    print("=" * 60)

    # Connect to database
    await connect_db()

    # Get service
    service = get_citation_enrichment_service()

    try:
        # Step 1: Update citation counts
        if args.update_counts:
            print("\n--- Updating Citation Counts ---")

            # Check how many need updating
            result = await database.fetch_one(
                "SELECT COUNT(*) FROM papers WHERE citation_count = 0 OR citation_count IS NULL"
            )
            needs_update = result[0] if result else 0
            print(f"Papers needing citation count update: {needs_update}")

            if needs_update > 0:
                stats = await service.run_citation_enrichment(
                    max_papers=args.max_papers,
                    skip_enriched=True,
                )
                print(f"Citation count update results: {stats.to_dict()}")
            else:
                print("All papers already have citation counts!")

        # Step 2: Build citation edges
        if args.build_edges:
            print("\n--- Building Citation Edges ---")

            # Check current edge count
            result = await database.fetch_one("SELECT COUNT(*) FROM citations")
            current_edges = result[0] if result else 0
            print(f"Current citation edges: {current_edges}")

            # Build edges
            edge_stats = await service.build_internal_citation_graph(
                max_papers=args.max_papers
            )
            print(f"Edge building results: {edge_stats}")

            # Check new edge count
            result = await database.fetch_one("SELECT COUNT(*) FROM citations")
            new_edges = result[0] if result else 0
            print(f"New citation edges: {new_edges} (+{new_edges - current_edges})")

        elapsed = time.time() - start
        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Time: {elapsed:.1f}s")
        print("=" * 60)

    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
