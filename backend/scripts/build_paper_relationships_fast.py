#!/usr/bin/env python3
"""
Fast batch building of paper relationships using matrix multiplication.
Run from backend directory: python scripts/build_paper_relationships_fast.py

Instead of calling find_similar() for each paper (O(n² * d) with Python overhead),
this computes the full similarity matrix using numpy's optimized matmul (much faster).
"""
import asyncio
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db
from app.services.local_atlas_service import local_atlas_service


async def get_existing_relationships(db) -> set:
    """Get all existing relationships as (paper_a, paper_b) pairs."""
    query = """SELECT paper_a_id, paper_b_id FROM paper_relationships"""
    results = await db.fetch_all(query)
    return set((r["paper_a_id"], r["paper_b_id"]) for r in results)


async def get_concepts_batch(db, paper_ids: list) -> dict:
    """Get concepts for multiple papers at once."""
    if not paper_ids:
        return {}

    # Create placeholders for the IN clause
    placeholders = ", ".join([f":id_{i}" for i in range(len(paper_ids))])
    query = f"""
        SELECT id, concepts_array FROM papers
        WHERE id IN ({placeholders})
    """
    params = {f"id_{i}": pid for i, pid in enumerate(paper_ids)}

    results = await db.fetch_all(query, params)
    return {r["id"]: set(r["concepts_array"] or []) for r in results}


def compute_concept_similarity(concepts_a: set, concepts_b: set) -> float:
    """Compute Jaccard similarity between concept sets."""
    if not concepts_a or not concepts_b:
        return 0.0
    intersection = len(concepts_a & concepts_b)
    union = len(concepts_a | concepts_b)
    return intersection / union if union > 0 else 0.0


async def compute_all_relationships_fast(
    atlas_service,
    db,
    top_k: int = 8,
    min_similarity: float = 0.65,
    batch_size: int = 100,
    max_papers: int = 5000,
):
    """
    Efficiently compute all paper relationships using matrix multiplication.

    Strategy:
    1. Load all embeddings as a single matrix (N x D)
    2. Compute full similarity matrix: S = E @ E.T (N x N)
    3. For each row, get top-k indices above threshold
    4. Batch insert into database
    """
    start = time.time()

    # Get embeddings and IDs from atlas service
    embeddings = atlas_service._embeddings  # (N, D)
    record_ids = atlas_service._record_ids  # List of paper IDs

    if embeddings is None:
        print("ERROR: No embeddings loaded")
        return 0

    n_papers = len(record_ids)
    print(f"Computing relationships for {n_papers} papers with {embeddings.shape[1]}D embeddings")

    # Get existing relationships to skip
    existing = await get_existing_relationships(db)
    print(f"Found {len(existing)} existing relationships to skip")

    # Create ID to index mapping
    id_to_idx = {pid: i for i, pid in enumerate(record_ids) if pid}

    # Limit to max_papers for processing
    if max_papers and max_papers < n_papers:
        print(f"Limiting to first {max_papers} papers")
        n_papers = max_papers

    # Compute similarity matrix in chunks to save memory
    # For 27K papers with 768D: 27K*768*4 = 79MB per embedding
    # Full similarity matrix: 27K*27K*4 = 2.9GB
    # Use chunked approach to reduce memory

    chunk_size = 1000  # Process 1000 papers at a time
    total_relationships = 0
    processed_papers = 0

    # Prepare all relationships in memory first, then batch insert
    all_relationships = []

    print(f"\nProcessing in chunks of {chunk_size}...")

    for chunk_start in range(0, n_papers, chunk_size):
        chunk_end = min(chunk_start + chunk_size, n_papers)
        chunk_ids = record_ids[chunk_start:chunk_end]
        chunk_embeddings = embeddings[chunk_start:chunk_end]  # (chunk, D)

        # Compute similarities for this chunk against ALL papers
        # chunk_sims[i, j] = similarity between chunk[i] and papers[j]
        chunk_sims = chunk_embeddings @ embeddings.T  # (chunk, N)

        # Process each paper in chunk
        for local_idx, paper_id in enumerate(chunk_ids):
            if not paper_id:
                continue

            global_idx = chunk_start + local_idx
            sims = chunk_sims[local_idx]  # Similarities to all papers

            # Zero out self-similarity
            sims[global_idx] = 0

            # Get top-k indices above threshold
            above_threshold = np.where(sims >= min_similarity)[0]
            if len(above_threshold) == 0:
                continue

            # Get top-k from those above threshold
            top_indices = above_threshold[np.argsort(sims[above_threshold])[-top_k:]]

            for target_idx in top_indices:
                target_id = record_ids[target_idx]
                if not target_id:
                    continue

                sim_score = float(sims[target_idx])

                # Ensure ordering for constraint
                if paper_id < target_id:
                    pa, pb = paper_id, target_id
                else:
                    pa, pb = target_id, paper_id

                # Skip if already exists
                if (pa, pb) in existing:
                    continue

                all_relationships.append({
                    "paper_a": pa,
                    "paper_b": pb,
                    "semantic_sim": sim_score,
                })
                existing.add((pa, pb))  # Track to avoid duplicates

        processed_papers += len(chunk_ids)
        elapsed = time.time() - start
        rate = processed_papers / elapsed
        print(f"  Processed {processed_papers}/{n_papers} papers, found {len(all_relationships)} relationships ({rate:.0f} papers/s)")

    # Deduplicate (shouldn't be needed but safety check)
    unique_rels = {(r["paper_a"], r["paper_b"]): r for r in all_relationships}
    all_relationships = list(unique_rels.values())

    print(f"\nInserting {len(all_relationships)} unique relationships...")

    # Batch insert relationships
    insert_query = """
        INSERT INTO paper_relationships
        (paper_a_id, paper_b_id, semantic_similarity, concept_similarity, computed_at)
        VALUES (:paper_a, :paper_b, :semantic_sim, :concept_sim, :computed_at)
        ON CONFLICT (paper_a_id, paper_b_id) DO UPDATE SET
            semantic_similarity = EXCLUDED.semantic_similarity,
            computed_at = EXCLUDED.computed_at
    """

    now = datetime.utcnow()
    inserted = 0

    for i in range(0, len(all_relationships), batch_size):
        batch = all_relationships[i:i + batch_size]

        for rel in batch:
            try:
                await db.execute(insert_query, {
                    "paper_a": rel["paper_a"],
                    "paper_b": rel["paper_b"],
                    "semantic_sim": rel["semantic_sim"],
                    "concept_sim": 0.0,  # Skip concept similarity for speed
                    "computed_at": now
                })
                inserted += 1
            except Exception as e:
                print(f"  Error inserting {rel['paper_a']} - {rel['paper_b']}: {e}")

        if (i + batch_size) % 1000 == 0:
            print(f"  Inserted {inserted}/{len(all_relationships)} relationships")

    return inserted


async def main():
    parser = argparse.ArgumentParser(description="Build paper relationships (fast batch mode)")
    parser.add_argument("--max-papers", type=int, default=5000, help="Max papers to process")
    parser.add_argument("--top-k", type=int, default=8, help="Similar papers per paper")
    parser.add_argument("--min-sim", type=float, default=0.65, help="Minimum similarity threshold")
    parser.add_argument("--batch", type=int, default=100, help="DB batch size")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Building Paper Relationships (FAST MODE)")
    print(f"Max Papers: {args.max_papers}, Top-K: {args.top_k}, Min Similarity: {args.min_sim}")
    print("=" * 60)

    # Connect to database
    await connect_db()
    db = database

    # Get atlas service
    atlas_service = local_atlas_service
    if not atlas_service.enabled:
        print("ERROR: LocalAtlasService not enabled. Check embeddings.")
        return

    print(f"LocalAtlasService loaded with {len(atlas_service._records)} papers")

    if atlas_service._embeddings is None:
        print("ERROR: No embeddings available")
        return

    try:
        total_inserted = await compute_all_relationships_fast(
            atlas_service,
            db,
            top_k=args.top_k,
            min_similarity=args.min_sim,
            batch_size=args.batch,
            max_papers=args.max_papers,
        )

        elapsed = time.time() - start

        # Get final count
        count_query = "SELECT COUNT(*) as cnt FROM paper_relationships"
        result = await db.fetch_one(count_query)

        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Relationships inserted: {total_inserted}")
        print(f"Total in database: {result['cnt']}")
        print(f"Time: {elapsed:.1f}s")
        print("=" * 60)

    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
