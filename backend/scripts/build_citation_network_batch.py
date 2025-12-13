#!/usr/bin/env python3
"""
Build citation network using Semantic Scholar BATCH API.
Run from backend directory: python scripts/build_citation_network_batch.py

This is 500x more efficient than individual API calls:
- Individual: 27,000 papers = 27,000 API calls (7.5 hours at 1/sec)
- Batch: 27,000 papers = 54 API calls (< 2 minutes!)

Strategy:
1. Get all paper IDs from our database
2. Use batch API to get references for 500 papers at a time
3. For each paper, check if its references are in our DB
4. Create citation edge: citing_paper -> referenced_paper
"""
import asyncio
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db
from app.services.providers.semantic_scholar_provider import get_semantic_scholar_provider


async def get_all_paper_ids(db) -> set:
    """Get all paper IDs from database (normalized without version)."""
    query = "SELECT id FROM papers"
    rows = await db.fetch_all(query)
    return {normalize_id(row["id"]) for row in rows}


def normalize_id(paper_id: str) -> str:
    """Remove version suffix from arXiv ID."""
    return paper_id.split("v")[0] if "v" in paper_id else paper_id


async def get_existing_citations(db) -> set:
    """Get existing citation edges as (citing, cited) pairs."""
    query = "SELECT citing_paper_id, cited_paper_id FROM citations"
    rows = await db.fetch_all(query)
    return {(normalize_id(r["citing_paper_id"]), normalize_id(r["cited_paper_id"])) for r in rows}


async def find_paper_with_prefix(db, arxiv_prefix: str) -> str | None:
    """Find actual paper ID that starts with this prefix."""
    query = "SELECT id FROM papers WHERE id LIKE :pattern LIMIT 1"
    row = await db.fetch_one(query, {"pattern": f"{arxiv_prefix}%"})
    return row["id"] if row else None


async def main():
    parser = argparse.ArgumentParser(description="Build citation network (BATCH API)")
    parser.add_argument("--max-papers", type=int, default=None, help="Max papers to process (None = all)")
    parser.add_argument("--batch-size", type=int, default=500, help="Papers per batch API call")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Citation Network Builder (BATCH MODE)")
    print(f"Max Papers: {args.max_papers or 'ALL'}, Batch Size: {args.batch_size}")
    print("=" * 60)

    await connect_db()
    db = database
    provider = get_semantic_scholar_provider()

    try:
        # Get all our paper IDs
        print("\nLoading paper IDs from database...")
        our_paper_ids = await get_all_paper_ids(db)
        print(f"Found {len(our_paper_ids)} papers in database")

        # Get existing citations to skip
        existing_citations = await get_existing_citations(db)
        print(f"Found {len(existing_citations)} existing citation edges")

        # Convert to list for batching
        paper_list = list(our_paper_ids)
        if args.max_papers:
            paper_list = paper_list[:args.max_papers]

        print(f"\nProcessing {len(paper_list)} papers...")

        # Stats
        stats = {
            "papers_processed": 0,
            "refs_found": 0,
            "internal_refs": 0,
            "edges_created": 0,
            "api_calls": 0,
        }

        # Process in batches
        for i in range(0, len(paper_list), args.batch_size):
            batch = paper_list[i:i + args.batch_size]
            batch_start = time.time()

            # Fetch references for this batch (single API call for up to 500 papers!)
            print(f"\nBatch {i//args.batch_size + 1}: Fetching references for {len(batch)} papers...")
            refs_by_paper = await provider.batch_get_references(batch)
            stats["api_calls"] += 1

            # Process each paper's references
            for paper_id, refs in refs_by_paper.items():
                stats["papers_processed"] += 1
                stats["refs_found"] += len(refs)

                for ref in refs:
                    ref_arxiv = ref.get("arxiv_id")
                    if not ref_arxiv:
                        continue

                    ref_normalized = normalize_id(ref_arxiv)

                    # Check if this reference is in our database
                    if ref_normalized in our_paper_ids:
                        stats["internal_refs"] += 1

                        # Skip if edge already exists
                        citing_norm = normalize_id(paper_id)
                        if (citing_norm, ref_normalized) in existing_citations:
                            continue

                        # Find actual paper IDs with version suffixes
                        citing_actual = await find_paper_with_prefix(db, citing_norm)
                        cited_actual = await find_paper_with_prefix(db, ref_normalized)

                        if citing_actual and cited_actual:
                            # Create citation edge: paper_id cites ref_arxiv
                            try:
                                await db.execute(
                                    """
                                    INSERT INTO citations (citing_paper_id, cited_paper_id, created_at)
                                    VALUES (:citing, :cited, :now)
                                    ON CONFLICT (citing_paper_id, cited_paper_id) DO NOTHING
                                    """,
                                    {
                                        "citing": citing_actual,
                                        "cited": cited_actual,
                                        "now": datetime.utcnow(),
                                    }
                                )
                                stats["edges_created"] += 1
                                existing_citations.add((citing_norm, ref_normalized))
                            except Exception as e:
                                print(f"  Error inserting edge: {e}")

            batch_time = time.time() - batch_start
            print(f"  Processed batch in {batch_time:.1f}s")
            print(f"  Running totals: {stats['internal_refs']} internal refs, {stats['edges_created']} new edges")

        # Final stats
        elapsed = time.time() - start
        final_count = await db.fetch_one("SELECT COUNT(*) as cnt FROM citations")

        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Papers processed: {stats['papers_processed']}")
        print(f"Total references found: {stats['refs_found']}")
        print(f"Internal references (both papers in DB): {stats['internal_refs']}")
        print(f"New citation edges created: {stats['edges_created']}")
        print(f"Total citation edges in DB: {final_count['cnt']}")
        print(f"API calls made: {stats['api_calls']} (vs {stats['papers_processed']} with individual calls)")
        print(f"Time: {elapsed:.1f}s")
        print(f"Efficiency: {stats['papers_processed'] / max(1, stats['api_calls']):.0f}x faster than individual calls")
        print("=" * 60)

    finally:
        await provider.close()
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
