"""
CLI tool for data ingestion pipeline

Usage:
    python -m app.cli.ingest --help
    python -m app.cli.ingest --category cs.AI --max 100
    python -m app.cli.ingest --query "attention mechanisms" --max 50
    python -m app.cli.ingest --backfill-embeddings
    python -m app.cli.ingest --backfill-concepts
    python -m app.cli.ingest --recent --categories cs.AI cs.LG cs.CV
    python -m app.cli.ingest --paper 2010.11929
    python -m app.cli.ingest --stats
"""
import asyncio
import sys
import argparse
import os
from datetime import datetime
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, '/Users/kaizen/Software-Projects/ai-papers-agent/backend')

from app.db.database import database
from app.services.ingestion_service import get_ingestion_service
from app.services.embedding_service import get_embedding_service
from app.services.concept_extraction_service import get_concept_extraction_service


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_stats(stats: dict, title: str = "Results"):
    """Print formatted statistics"""
    print(f"\n📊 {title}:")
    print("-" * 50)
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        elif isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")
    print("-" * 50 + "\n")


async def ingest_by_category(category: str, max_results: int, embeddings: bool, concepts: bool):
    """Ingest papers by category"""
    print_header(f"Ingesting Papers from Category: {category}")

    service = get_ingestion_service()

    stats = await service.ingest_papers(
        category=category,
        max_results=max_results,
        generate_embeddings=embeddings,
        extract_concepts=concepts
    )

    print_stats(stats, f"Ingestion Complete - {category}")


async def ingest_by_query(query: str, max_results: int, embeddings: bool, concepts: bool):
    """Ingest papers by search query"""
    print_header(f"Searching arXiv: {query}")

    service = get_ingestion_service()

    stats = await service.ingest_papers(
        query=query,
        max_results=max_results,
        generate_embeddings=embeddings,
        extract_concepts=concepts
    )

    print_stats(stats, f"Ingestion Complete - Query: {query}")


async def ingest_recent(categories: List[str], max_per_category: int, embeddings: bool):
    """Ingest recent papers from multiple categories"""
    print_header(f"Ingesting Recent Papers from {len(categories)} Categories")

    service = get_ingestion_service()

    stats = await service.ingest_recent_papers(
        categories=categories,
        max_per_category=max_per_category,
        generate_embeddings=embeddings
    )

    print_stats(stats, "Recent Papers Ingestion Complete")


async def bootstrap_recent_atlas(
    categories: List[str],
    years: int,
    window_months: int,
    max_per_window: int,
    embeddings: bool,
    extract_concepts: bool,
    dump_dir: Optional[str]
):
    """Seed the atlas with the last N years of papers."""
    print_header(
        f"Bootstrapping Atlas ({years} years, {window_months}-month windows)"
    )

    service = get_ingestion_service(local_dump_dir=dump_dir)

    summary = await service.bootstrap_recent_atlas(
        categories=categories,
        years=years,
        window_months=window_months,
        max_per_window=max_per_window,
        generate_embeddings=embeddings,
        extract_concepts=extract_concepts
    )

    context_stats = {
        "categories": ", ".join(summary["categories"]),
        "windows": summary["total_windows"],
        "max_per_window": summary["max_per_window"]
    }
    if summary.get("local_dump_dir"):
        context_stats["local_dump_dir"] = summary["local_dump_dir"]
    print_stats(context_stats, "Bootstrap Parameters")

    print("\n📦 Category Breakdown")
    print("-" * 50)
    for stat in summary["stats"]:
        print(
            f"{stat['category']}: "
            f"windows={stat['windows_processed']}, "
            f"stored={stat['stored']}, "
            f"duplicates={stat['duplicates']}, "
            f"errors={stat['errors']}"
        )
        if stat.get("dumps"):
            example = stat["dumps"][-1]
            print(f"     dumps: {len(stat['dumps'])} files (latest: {example})")
    print("-" * 50 + "\n")


async def ingest_specific_paper(arxiv_id: str, embeddings: bool, concepts: bool):
    """Ingest a specific paper by ID"""
    print_header(f"Ingesting Paper: {arxiv_id}")

    service = get_ingestion_service()

    result = await service.ingest_specific_paper(
        arxiv_id=arxiv_id,
        generate_embedding=embeddings,
        extract_concepts=concepts
    )

    if result.get("success"):
        print("✅ Paper ingested successfully!")
        if result.get("already_existed"):
            print("   (Paper already existed in database)")
        if result.get("embedding_generated"):
            print("   ✓ Embedding generated")
        if result.get("concepts_extracted"):
            print("   ✓ Concepts extracted")
    else:
        print(f"❌ Failed to ingest paper: {result.get('error', 'Unknown error')}")


async def backfill_embeddings(batch_size: int, max_papers: int):
    """Backfill embeddings for papers without them"""
    print_header("Backfilling Embeddings")

    service = get_embedding_service()

    print(f"📊 Batch size: {batch_size}")
    if max_papers:
        print(f"📊 Max papers: {max_papers}")
    else:
        print("📊 Processing all papers without embeddings")

    stats = await service.backfill_embeddings(
        batch_size=batch_size,
        max_papers=max_papers
    )

    print_stats(stats, "Embedding Backfill Complete")


async def backfill_concepts(batch_size: int, max_papers: int):
    """Backfill concepts for papers without them"""
    print_header("Backfilling Concepts")

    service = get_concept_extraction_service()

    print(f"📊 Batch size: {batch_size}")
    if max_papers:
        print(f"📊 Max papers: {max_papers}")
    else:
        print("📊 Processing all papers without concepts")

    stats = await service.backfill_concepts(
        max_papers=max_papers,
        batch_size=batch_size
    )

    print_stats(stats, "Concept Backfill Complete")


async def show_stats():
    """Show ingestion statistics"""
    print_header("Knowledge Graph Statistics")

    ingestion_service = get_ingestion_service()
    embedding_service = get_embedding_service()
    concept_service = get_concept_extraction_service()

    # Get stats from all services
    ingestion_stats = await ingestion_service.get_ingestion_stats()
    embedding_stats = await embedding_service.get_embedding_stats()
    concept_stats = await concept_service.get_concept_stats()

    print("📚 PAPERS:")
    print(f"   Total papers: {ingestion_stats['total_papers']}")
    print(f"   Ingested (last 24h): {ingestion_stats['recent_24h']}")
    print()

    print("📊 BY CATEGORY:")
    for cat in ingestion_stats['by_category'][:5]:
        print(f"   {cat['category']}: {cat['count']} papers")
    print()

    print("🔍 EMBEDDINGS:")
    emb = embedding_stats['papers']
    print(f"   Papers with embeddings: {emb['with_embedding']}/{emb['total']}")
    print(f"   Coverage: {emb['coverage_percentage']}%")
    print()

    print("🏷️  CONCEPTS:")
    print(f"   Total concepts: {concept_stats['total_concepts']}")
    print(f"   Papers with concepts: {concept_stats['papers_with_concepts']}")
    print()

    print("📈 TOP CONCEPTS:")
    for concept in concept_stats['top_concepts'][:10]:
        print(f"   {concept['name']} ({concept['category']}): {concept['paper_count']} papers")
    print()


async def main():
    parser = argparse.ArgumentParser(
        description="AI Papers Knowledge Graph - Data Ingestion Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest 100 papers from cs.AI category
  python -m app.cli.ingest --category cs.AI --max 100

  # Search and ingest papers about attention mechanisms
  python -m app.cli.ingest --query "attention mechanisms" --max 50

  # Ingest recent papers from multiple categories
  python -m app.cli.ingest --recent --categories cs.AI cs.LG cs.CV --max-per 30

  # Bootstrap atlas with last 3 years (quarterly windows)
  python -m app.cli.ingest --bootstrap-atlas --years 3 --window-months 3 --max-window 200

  # Ingest a specific paper
  python -m app.cli.ingest --paper 2010.11929

  # Backfill embeddings for papers without them
  python -m app.cli.ingest --backfill-embeddings --max 1000

  # Backfill concepts for papers without them
  python -m app.cli.ingest --backfill-concepts --max 500

  # Show statistics
  python -m app.cli.ingest --stats
        """
    )

    # Ingestion modes
    parser.add_argument("--category", help="arXiv category (e.g., cs.AI, cs.CV, cs.LG)")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--recent", action="store_true", help="Ingest recent papers from multiple categories")
    parser.add_argument("--bootstrap-atlas", action="store_true", help="Seed atlas with the last N years of research")
    parser.add_argument("--paper", help="Specific paper ID to ingest")

    # Options
    parser.add_argument("--max", type=int, default=100, help="Maximum papers to fetch (default: 100)")
    parser.add_argument("--max-per", type=int, default=50, help="Max papers per category for --recent mode")
    parser.add_argument("--categories", nargs="+", default=["cs.AI", "cs.LG", "cs.CV"],
                       help="Categories for --recent mode (default: cs.AI cs.LG cs.CV)")
    parser.add_argument("--years", type=int, default=3, help="Number of years for --bootstrap-atlas (default: 3)")
    parser.add_argument("--window-months", type=int, default=3, help="Months per window for --bootstrap-atlas (default: 3)")
    parser.add_argument("--max-window", type=int, default=200, help="Max papers per window for --bootstrap-atlas (default: 200)")
    parser.add_argument("--dump-dir", help="Write raw paper dumps to this directory (local bootstrap mode)")

    # Processing flags
    parser.add_argument("--no-embeddings", action="store_true", help="Skip embedding generation")
    parser.add_argument("--extract-concepts", action="store_true", help="Extract concepts (slower)")

    # Backfill modes
    parser.add_argument("--backfill-embeddings", action="store_true", help="Backfill embeddings")
    parser.add_argument("--backfill-concepts", action="store_true", help="Backfill concepts")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for backfill (default: 100)")

    # Stats
    parser.add_argument("--stats", action="store_true", help="Show knowledge graph statistics")

    args = parser.parse_args()

    dump_mode_enabled = bool(args.dump_dir or os.getenv("LOCAL_DUMP_DIR"))
    db_connected = False
    if not (args.bootstrap_atlas and dump_mode_enabled):
        await database.connect()
        db_connected = True

    try:
        # Determine mode
        if args.stats:
            await show_stats()

        elif args.backfill_embeddings:
            await backfill_embeddings(
                batch_size=args.batch_size,
                max_papers=args.max if args.max != 100 else None
            )

        elif args.backfill_concepts:
            await backfill_concepts(
                batch_size=args.batch_size,
                max_papers=args.max if args.max != 100 else None
            )

        elif args.paper:
            await ingest_specific_paper(
                arxiv_id=args.paper,
                embeddings=not args.no_embeddings,
                concepts=args.extract_concepts
            )

        elif args.recent:
            await ingest_recent(
                categories=args.categories,
                max_per_category=args.max_per,
                embeddings=not args.no_embeddings
            )

        elif args.bootstrap_atlas:
            await bootstrap_recent_atlas(
                categories=args.categories,
                years=args.years,
                window_months=args.window_months,
                max_per_window=args.max_window,
                embeddings=not args.no_embeddings,
                extract_concepts=args.extract_concepts,
                dump_dir=args.dump_dir
            )

        elif args.category:
            await ingest_by_category(
                category=args.category,
                max_results=args.max,
                embeddings=not args.no_embeddings,
                concepts=args.extract_concepts
            )

        elif args.query:
            await ingest_by_query(
                query=args.query,
                max_results=args.max,
                embeddings=not args.no_embeddings,
                concepts=args.extract_concepts
            )

        else:
            parser.print_help()
            print("\n❌ Please specify a mode: --category, --query, --recent, --paper, --backfill-*, or --stats")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if db_connected:
            await database.disconnect()


if __name__ == "__main__":
    print_header(f"AI Papers Knowledge Graph - Ingestion Tool")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    asyncio.run(main())

    print(f"\n✅ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
