#!/usr/bin/env python3
"""
Load embeddings from numpy files into PostgreSQL pgvector column.
Run from backend directory: python scripts/load_embeddings_to_db.py
"""
import asyncio
import sys
import time
import json
import argparse
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db


async def main():
    parser = argparse.ArgumentParser(description="Load embeddings into DB")
    parser.add_argument("--embeddings", type=str, required=True, help="Path to embeddings .npy file")
    parser.add_argument("--ids", type=str, required=True, help="Path to IDs .json file")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for DB updates")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Embedding Loader")
    print(f"Embeddings: {args.embeddings}")
    print(f"IDs: {args.ids}")
    print("=" * 60)

    # Load embeddings and IDs
    print("\nLoading embeddings from disk...")
    embeddings = np.load(args.embeddings)
    with open(args.ids) as f:
        paper_ids = json.load(f)

    print(f"Loaded {len(paper_ids)} embeddings with dimension {embeddings.shape[1]}")

    await connect_db()
    db = database

    try:
        stats = {"updated": 0, "not_found": 0, "errors": 0}

        # Process in batches
        for i in range(0, len(paper_ids), args.batch_size):
            batch_ids = paper_ids[i:i + args.batch_size]
            batch_embeddings = embeddings[i:i + args.batch_size]
            batch_start = time.time()

            for j, (paper_id, emb) in enumerate(zip(batch_ids, batch_embeddings)):
                # Convert embedding to pgvector format: '[0.1, 0.2, ...]'
                emb_str = '[' + ','.join(str(x) for x in emb.tolist()) + ']'

                try:
                    result = await db.execute(
                        "UPDATE papers SET embedding = :emb WHERE id = :id",
                        {"emb": emb_str, "id": paper_id}
                    )
                    # Check if any row was updated
                    if result:
                        stats["updated"] += 1
                    else:
                        stats["not_found"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    if stats["errors"] < 5:
                        print(f"  Error updating {paper_id}: {e}")

            batch_time = time.time() - batch_start
            print(f"Batch {i // args.batch_size + 1}: {len(batch_ids)} papers in {batch_time:.1f}s - Updated: {stats['updated']}")

        # Final stats
        elapsed = time.time() - start
        result = await db.fetch_one(
            "SELECT COUNT(*) as cnt FROM papers WHERE embedding IS NOT NULL"
        )

        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Embeddings updated: {stats['updated']}")
        print(f"Not found in DB: {stats['not_found']}")
        print(f"Errors: {stats['errors']}")
        print(f"Papers with embeddings in DB: {result['cnt']}")
        print(f"Time: {elapsed:.1f}s")
        print("=" * 60)

    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
