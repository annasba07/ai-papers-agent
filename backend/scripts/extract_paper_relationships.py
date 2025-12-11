#!/usr/bin/env python3
"""
Extract semantic relationships between papers using LLM analysis.
Run from backend directory: python scripts/extract_paper_relationships.py

This script:
1. Finds papers with deep_analysis that haven't had relationships extracted
2. Uses LLM to extract typed relationships (improves, extends, contradicts, etc.)
3. Resolves paper titles to IDs and saves to paper_semantic_edges

Best run on high-impact papers first (by citation count).
"""
import asyncio
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import database, connect_db, disconnect_db
from app.services.relationship_extractor import get_relationship_service


async def get_papers_needing_extraction(db, limit: int = 50, min_citations: int = 10):
    """
    Get papers that need relationship extraction.

    Prioritizes:
    1. Papers with deep_analysis (have rich context)
    2. High citation count (more likely to have meaningful relationships)
    3. Haven't been processed yet
    """
    query = """
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.deep_analysis,
            p.citation_count
        FROM papers p
        LEFT JOIN (
            SELECT DISTINCT source_paper_id
            FROM paper_semantic_edges
            WHERE extraction_method = 'llm'
        ) pse ON p.id = pse.source_paper_id
        WHERE p.deep_analysis IS NOT NULL
        AND pse.source_paper_id IS NULL
        AND (p.citation_count >= :min_citations OR p.citation_count IS NULL)
        ORDER BY p.citation_count DESC NULLS LAST
        LIMIT :limit
    """

    results = await db.fetch_all(query, {
        "limit": limit,
        "min_citations": min_citations
    })

    return [
        {
            "id": r["id"],
            "title": r["title"],
            "abstract": r["abstract"],
            "deep_analysis": r["deep_analysis"],
            "citation_count": r["citation_count"]
        }
        for r in results
    ]


def get_related_work_text(paper: dict) -> str:
    """Extract related work section from deep_analysis if available."""
    deep = paper.get("deep_analysis") or {}

    # Try different possible locations
    sections = deep.get("sections") or {}
    if "related_work" in sections:
        return sections["related_work"]

    # Check for methodology comparisons
    methodology = deep.get("methodology") or {}
    if "comparison_to_prior_work" in methodology:
        return methodology["comparison_to_prior_work"]

    # Extract from key_contributions if it mentions prior work
    contributions = deep.get("key_contributions") or []
    if contributions:
        return "\n".join(contributions)

    return ""


async def extract_for_paper(paper: dict, service, db) -> dict:
    """Extract relationships for a single paper."""
    related_work = get_related_work_text(paper)

    result = await service.extract_and_save(paper, db, related_work)

    return result


async def main():
    parser = argparse.ArgumentParser(description="Extract paper relationships using LLM")
    parser.add_argument("--limit", type=int, default=50, help="Max papers to process")
    parser.add_argument("--min-citations", type=int, default=10, help="Min citations filter")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between papers (rate limiting)")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Paper Relationship Extraction")
    print("=" * 60)

    # Connect to database using async databases library
    await connect_db()
    db = database
    service = get_relationship_service()

    try:
        print(f"\nFetching papers needing extraction (limit={args.limit}, min_citations={args.min_citations})...")
        papers = await get_papers_needing_extraction(db, args.limit, args.min_citations)
        print(f"Found {len(papers)} papers to process")

        if not papers:
            print("No papers to process!")
            return

        # Process papers
        total_found = 0
        total_resolved = 0
        total_saved = 0
        errors = 0

        for i, paper in enumerate(papers):
            print(f"\n[{i+1}/{len(papers)}] {paper['title'][:60]}...")
            print(f"  Citations: {paper.get('citation_count', 'N/A')}")

            try:
                result = await extract_for_paper(paper, service, db)

                if result.get("success"):
                    found = result.get("relationships_found", 0)
                    resolved = result.get("relationships_resolved", 0)
                    saved = result.get("relationships_saved", 0)

                    total_found += found
                    total_resolved += resolved
                    total_saved += saved

                    print(f"  Found: {found}, Resolved: {resolved}, Saved: {saved}")
                else:
                    errors += 1
                    print(f"  Error: {result.get('error', 'Unknown')}")

            except Exception as e:
                errors += 1
                print(f"  Error: {e}")

            # Rate limiting delay
            if i < len(papers) - 1:
                await asyncio.sleep(args.delay)

        elapsed = time.time() - start
        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Papers processed: {len(papers)}")
        print(f"Relationships found: {total_found}")
        print(f"Relationships resolved: {total_resolved}")
        print(f"Relationships saved: {total_saved}")
        print(f"Errors: {errors}")
        print(f"Time: {elapsed:.1f}s")
        print("=" * 60)
    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
