#!/usr/bin/env python3
"""
Backfill paper_processing_state timestamps based on actual data presence.

This script syncs the pipeline's tracking table with existing enrichment data
that was processed by standalone scripts before the pipeline was created.

The completeness_score column is auto-calculated by PostgreSQL based on which
timestamp columns are set.

Detection logic:
- embedding_at:     papers.embedding IS NOT NULL
- ai_analysis_at:   papers.ai_analysis IS NOT NULL
- citations_at:     papers.citation_count > 0
- concepts_at:      paper has entries in paper_concepts
- techniques_at:    paper has entries in paper_techniques
- benchmarks_at:    paper has entries in benchmarks
- github_at:        papers.external_signals->'github' IS NOT NULL
- deep_analysis_at: papers.deep_analysis IS NOT NULL AND != '{}'
- relationships_at: paper has entries in paper_relationships
"""

import asyncio
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import database


async def backfill_processing_state():
    """Backfill all processing state timestamps based on actual data."""

    await database.connect()

    try:
        print("=" * 60)
        print("Backfilling paper_processing_state from actual data")
        print("=" * 60)

        # Get current state before backfill
        before = await database.fetch_one("""
            SELECT
                COUNT(*) as total,
                AVG(completeness_score) as avg_score,
                COUNT(*) FILTER (WHERE completeness_score = 100) as fully_complete
            FROM paper_processing_state
        """)
        print(f"\nBefore backfill:")
        print(f"  Total papers: {before['total']}")
        print(f"  Avg completeness: {before['avg_score']:.1f}%")
        print(f"  Fully complete: {before['fully_complete']}")

        # 1. Backfill embedding_at
        print("\n[1/9] Backfilling embedding_at...")
        result = await database.execute("""
            UPDATE paper_processing_state pps
            SET embedding_at = NOW()
            FROM papers p
            WHERE pps.paper_id = p.id
            AND p.embedding IS NOT NULL
            AND pps.embedding_at IS NULL
        """)
        print(f"       Updated {result} rows")

        # 2. Backfill ai_analysis_at
        print("[2/9] Backfilling ai_analysis_at...")
        result = await database.execute("""
            UPDATE paper_processing_state pps
            SET ai_analysis_at = NOW()
            FROM papers p
            WHERE pps.paper_id = p.id
            AND p.ai_analysis IS NOT NULL
            AND pps.ai_analysis_at IS NULL
        """)
        print(f"       Updated {result} rows")

        # 3. Backfill citations_at (based on citation_count being populated)
        print("[3/9] Backfilling citations_at...")
        result = await database.execute("""
            UPDATE paper_processing_state pps
            SET citations_at = NOW()
            FROM papers p
            WHERE pps.paper_id = p.id
            AND p.citation_count IS NOT NULL
            AND p.citation_count > 0
            AND pps.citations_at IS NULL
        """)
        print(f"       Updated {result} rows")

        # 4. Backfill concepts_at
        print("[4/9] Backfilling concepts_at...")
        result = await database.execute("""
            UPDATE paper_processing_state pps
            SET concepts_at = NOW()
            WHERE pps.concepts_at IS NULL
            AND EXISTS (
                SELECT 1 FROM paper_concepts pc
                WHERE pc.paper_id = pps.paper_id
            )
        """)
        print(f"       Updated {result} rows")

        # 5. Backfill techniques_at
        print("[5/9] Backfilling techniques_at...")
        result = await database.execute("""
            UPDATE paper_processing_state pps
            SET techniques_at = NOW()
            WHERE pps.techniques_at IS NULL
            AND EXISTS (
                SELECT 1 FROM paper_techniques pt
                WHERE pt.paper_id = pps.paper_id
            )
        """)
        print(f"       Updated {result} rows")

        # 6. Backfill benchmarks_at
        print("[6/9] Backfilling benchmarks_at...")
        result = await database.execute("""
            UPDATE paper_processing_state pps
            SET benchmarks_at = NOW()
            WHERE pps.benchmarks_at IS NULL
            AND EXISTS (
                SELECT 1 FROM benchmarks b
                WHERE b.paper_id = pps.paper_id
            )
        """)
        print(f"       Updated {result} rows")

        # 7. Backfill github_at
        print("[7/9] Backfilling github_at...")
        result = await database.execute("""
            UPDATE paper_processing_state pps
            SET github_at = NOW()
            FROM papers p
            WHERE pps.paper_id = p.id
            AND p.external_signals->'github' IS NOT NULL
            AND p.external_signals->>'github' != 'null'
            AND pps.github_at IS NULL
        """)
        print(f"       Updated {result} rows")

        # 8. Backfill deep_analysis_at
        print("[8/9] Backfilling deep_analysis_at...")
        result = await database.execute("""
            UPDATE paper_processing_state pps
            SET deep_analysis_at = NOW()
            FROM papers p
            WHERE pps.paper_id = p.id
            AND p.deep_analysis IS NOT NULL
            AND p.deep_analysis::text != '{}'
            AND p.deep_analysis::text != 'null'
            AND pps.deep_analysis_at IS NULL
        """)
        print(f"       Updated {result} rows")

        # 9. Backfill relationships_at
        print("[9/9] Backfilling relationships_at...")
        result = await database.execute("""
            UPDATE paper_processing_state pps
            SET relationships_at = NOW()
            WHERE pps.relationships_at IS NULL
            AND EXISTS (
                SELECT 1 FROM paper_relationships pr
                WHERE pr.paper_a_id = pps.paper_id
                OR pr.paper_b_id = pps.paper_id
            )
        """)
        print(f"       Updated {result} rows")

        # Get state after backfill
        after = await database.fetch_one("""
            SELECT
                COUNT(*) as total,
                AVG(completeness_score) as avg_score,
                COUNT(*) FILTER (WHERE completeness_score = 100) as fully_complete,
                COUNT(*) FILTER (WHERE completeness_score >= 80) as above_80,
                COUNT(*) FILTER (WHERE completeness_score >= 50) as above_50
            FROM paper_processing_state
        """)

        print("\n" + "=" * 60)
        print("After backfill:")
        print(f"  Total papers: {after['total']}")
        print(f"  Avg completeness: {after['avg_score']:.1f}%")
        print(f"  Fully complete (100%): {after['fully_complete']}")
        print(f"  Above 80%: {after['above_80']}")
        print(f"  Above 50%: {after['above_50']}")
        print("=" * 60)

        # Show detailed breakdown
        breakdown = await database.fetch_all("""
            SELECT
                CASE
                    WHEN embedding_at IS NOT NULL THEN 'Yes' ELSE 'No'
                END as has_embedding,
                CASE
                    WHEN ai_analysis_at IS NOT NULL THEN 'Yes' ELSE 'No'
                END as has_ai_analysis,
                CASE
                    WHEN citations_at IS NOT NULL THEN 'Yes' ELSE 'No'
                END as has_citations,
                CASE
                    WHEN concepts_at IS NOT NULL THEN 'Yes' ELSE 'No'
                END as has_concepts,
                CASE
                    WHEN techniques_at IS NOT NULL THEN 'Yes' ELSE 'No'
                END as has_techniques,
                CASE
                    WHEN benchmarks_at IS NOT NULL THEN 'Yes' ELSE 'No'
                END as has_benchmarks,
                CASE
                    WHEN github_at IS NOT NULL THEN 'Yes' ELSE 'No'
                END as has_github,
                CASE
                    WHEN deep_analysis_at IS NOT NULL THEN 'Yes' ELSE 'No'
                END as has_deep_analysis,
                CASE
                    WHEN relationships_at IS NOT NULL THEN 'Yes' ELSE 'No'
                END as has_relationships,
                COUNT(*) as count
            FROM paper_processing_state
            GROUP BY 1,2,3,4,5,6,7,8,9
            ORDER BY count DESC
            LIMIT 10
        """)

        print("\nTop 10 enrichment patterns:")
        print("-" * 100)
        print(f"{'Embed':>6} {'AI':>4} {'Cite':>5} {'Conc':>5} {'Tech':>5} {'Bench':>6} {'GH':>4} {'Deep':>5} {'Rel':>4} | {'Count':>7}")
        print("-" * 100)
        for row in breakdown:
            print(f"{row['has_embedding']:>6} {row['has_ai_analysis']:>4} {row['has_citations']:>5} "
                  f"{row['has_concepts']:>5} {row['has_techniques']:>5} {row['has_benchmarks']:>6} "
                  f"{row['has_github']:>4} {row['has_deep_analysis']:>5} {row['has_relationships']:>4} | "
                  f"{row['count']:>7}")

        # Show stage-level stats
        stage_stats = await database.fetch_one("""
            SELECT
                COUNT(*) FILTER (WHERE embedding_at IS NOT NULL) as embedding,
                COUNT(*) FILTER (WHERE ai_analysis_at IS NOT NULL) as ai_analysis,
                COUNT(*) FILTER (WHERE citations_at IS NOT NULL) as citations,
                COUNT(*) FILTER (WHERE concepts_at IS NOT NULL) as concepts,
                COUNT(*) FILTER (WHERE techniques_at IS NOT NULL) as techniques,
                COUNT(*) FILTER (WHERE benchmarks_at IS NOT NULL) as benchmarks,
                COUNT(*) FILTER (WHERE github_at IS NOT NULL) as github,
                COUNT(*) FILTER (WHERE deep_analysis_at IS NOT NULL) as deep_analysis,
                COUNT(*) FILTER (WHERE relationships_at IS NOT NULL) as relationships,
                COUNT(*) as total
            FROM paper_processing_state
        """)

        total = stage_stats['total']
        print("\n" + "=" * 60)
        print("Stage completion rates:")
        print("-" * 60)
        for stage in ['embedding', 'ai_analysis', 'citations', 'concepts',
                      'techniques', 'benchmarks', 'github', 'deep_analysis', 'relationships']:
            count = stage_stats[stage]
            pct = (count / total * 100) if total > 0 else 0
            bar = '█' * int(pct / 2) + '░' * (50 - int(pct / 2))
            print(f"  {stage:15} {bar} {pct:5.1f}% ({count:,}/{total:,})")
        print("=" * 60)

    finally:
        await database.disconnect()


if __name__ == "__main__":
    asyncio.run(backfill_processing_state())
