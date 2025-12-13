#!/usr/bin/env python3
"""
Build paper relationships from semantic similarity.
Run from backend directory: python scripts/build_paper_relationships.py

This script uses existing embeddings to populate the paper_relationships table
with semantic similarity scores between papers.
"""
import asyncio
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db
from app.services.local_atlas_service import local_atlas_service


async def get_papers_without_relationships(db, atlas_service, limit: int = 1000) -> list:
    """
    Get papers from catalog that don't have relationships computed yet.
    Uses catalog IDs since those match the embeddings.
    """
    # Get all IDs from the catalog (these have embeddings)
    catalog_ids = set(r.get("id") for r in atlas_service._records if r.get("id"))

    # Get IDs that already have relationships
    query = """
        SELECT DISTINCT paper_a_id FROM paper_relationships
    """
    results = await db.fetch_all(query)
    processed_ids = set(r["paper_a_id"] for r in results)

    # Get papers without relationships
    unprocessed = catalog_ids - processed_ids

    # Return limited list
    return list(unprocessed)[:limit]


async def get_concepts_for_paper(db, paper_id: str) -> set:
    """Get concepts array for a paper."""
    query = """
        SELECT concepts_array FROM papers WHERE id = :paper_id
    """
    result = await db.fetch_one(query, {"paper_id": paper_id})
    if result and result["concepts_array"]:
        return set(result["concepts_array"])
    return set()


def compute_concept_similarity(concepts_a: set, concepts_b: set) -> float:
    """Compute Jaccard similarity between concept sets."""
    if not concepts_a or not concepts_b:
        return 0.0
    intersection = len(concepts_a & concepts_b)
    union = len(concepts_a | concepts_b)
    return intersection / union if union > 0 else 0.0


async def build_relationships_for_paper(
    paper_id: str,
    atlas_service,
    db,
    top_k: int = 10,
    min_similarity: float = 0.5
) -> int:
    """Build relationships for a single paper using similarity search."""
    saved = 0

    try:
        # Get similar papers using existing embeddings
        similar = atlas_service.find_similar(paper_id, top_k=top_k)

        if not similar:
            return 0

        # Get concepts for source paper
        concepts_a = await get_concepts_for_paper(db, paper_id)

        for sim_paper in similar:
            sim_id = sim_paper.get("id")
            sim_score = sim_paper.get("similarity_score", 0.0)

            # Skip self-relationships and low similarity
            if sim_id == paper_id or sim_score < min_similarity:
                continue

            # Get concepts for target paper
            concepts_b = await get_concepts_for_paper(db, sim_id)
            concept_sim = compute_concept_similarity(concepts_a, concepts_b)

            # Insert relationship (only one direction to satisfy constraint: paper_a < paper_b)
            # The constraint ensures no duplicates in either direction
            if paper_id < sim_id:
                pa, pb = paper_id, sim_id
            else:
                pa, pb = sim_id, paper_id

            insert_query = """
                INSERT INTO paper_relationships
                (paper_a_id, paper_b_id, semantic_similarity, concept_similarity, computed_at)
                VALUES (:paper_a, :paper_b, :semantic_sim, :concept_sim, :computed_at)
                ON CONFLICT (paper_a_id, paper_b_id) DO UPDATE SET
                    semantic_similarity = EXCLUDED.semantic_similarity,
                    concept_similarity = EXCLUDED.concept_similarity,
                    computed_at = EXCLUDED.computed_at
            """

            now = datetime.utcnow()

            await db.execute(insert_query, {
                "paper_a": pa,
                "paper_b": pb,
                "semantic_sim": float(sim_score),
                "concept_sim": float(concept_sim),
                "computed_at": now
            })

            saved += 1

    except Exception as e:
        print(f"  Error processing {paper_id}: {e}")

    return saved


async def main():
    parser = argparse.ArgumentParser(description="Build paper relationships from similarity")
    parser.add_argument("--limit", type=int, default=500, help="Max papers to process")
    parser.add_argument("--top-k", type=int, default=8, help="Similar papers per paper")
    parser.add_argument("--min-sim", type=float, default=0.6, help="Minimum similarity threshold")
    parser.add_argument("--batch", type=int, default=50, help="Batch size for progress reporting")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Building Paper Relationships")
    print(f"Limit: {args.limit}, Top-K: {args.top_k}, Min Similarity: {args.min_sim}")
    print("=" * 60)

    # Connect to database
    await connect_db()
    db = database

    # Get atlas service (module-level singleton)
    atlas_service = local_atlas_service
    if not atlas_service.enabled:
        print("ERROR: LocalAtlasService not enabled. Check embeddings.")
        return

    print(f"LocalAtlasService loaded with {len(atlas_service._records)} papers")

    try:
        # Get papers to process (from catalog, not PostgreSQL)
        print(f"\nFetching papers from catalog without relationships...")
        papers = await get_papers_without_relationships(db, atlas_service, args.limit)
        print(f"Found {len(papers)} papers to process")

        if not papers:
            # Check existing count
            count_query = "SELECT COUNT(*) as cnt FROM paper_relationships"
            result = await db.fetch_one(count_query)
            print(f"Already have {result['cnt']} relationships in database")
            return

        # Process papers
        total_relationships = 0

        for i, paper_id in enumerate(papers):
            saved = await build_relationships_for_paper(
                paper_id,
                atlas_service,
                db,
                top_k=args.top_k,
                min_similarity=args.min_sim
            )
            total_relationships += saved

            if (i + 1) % args.batch == 0:
                elapsed = time.time() - start
                rate = (i + 1) / elapsed
                print(f"  [{i+1}/{len(papers)}] {total_relationships} relationships, {rate:.1f} papers/s")

        elapsed = time.time() - start

        # Get final count
        count_query = "SELECT COUNT(*) as cnt FROM paper_relationships"
        result = await db.fetch_one(count_query)

        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Papers processed: {len(papers)}")
        print(f"Relationships created: {total_relationships}")
        print(f"Total in database: {result['cnt']}")
        print(f"Time: {elapsed:.1f}s ({len(papers)/elapsed:.1f} papers/s)")
        print("=" * 60)

    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
