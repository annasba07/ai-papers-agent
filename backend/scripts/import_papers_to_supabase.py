#!/usr/bin/env python3
"""
Import papers from NDJSON file to Supabase PostgreSQL

Usage:
    python scripts/import_papers_to_supabase.py [--limit N] [--batch-size N]

Examples:
    # Import all papers
    python scripts/import_papers_to_supabase.py

    # Import first 1000 papers
    python scripts/import_papers_to_supabase.py --limit 1000

    # Import with smaller batches (for debugging)
    python scripts/import_papers_to_supabase.py --batch-size 50
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Generator, Dict, Any, List
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get database URL from environment"""
    url = os.getenv('SUPABASE_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not url:
        raise ValueError("No DATABASE_URL or SUPABASE_DATABASE_URL found in environment")
    return url


def read_papers_ndjson(filepath: Path, limit: int = None) -> Generator[Dict[str, Any], None, None]:
    """Read papers from NDJSON file"""
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if limit and count >= limit:
                break
            try:
                paper = json.loads(line.strip())
                yield paper
                count += 1
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping invalid JSON line: {e}")
                continue


def transform_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
    """Transform paper from NDJSON format to database schema"""
    # Parse published date
    published_str = paper.get('published', '')
    try:
        if 'T' in published_str:
            published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
        else:
            published_date = datetime.strptime(published_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        published_date = datetime.now()

    # Clean the arXiv ID (remove version suffix for primary ID)
    arxiv_id = paper.get('id', '')

    # Extract authors as JSON
    authors = paper.get('authors', [])
    if isinstance(authors, str):
        authors = [authors]

    return {
        'id': arxiv_id,
        'title': paper.get('title', '').replace('\n', ' ').strip(),
        'abstract': paper.get('abstract', '').strip(),
        'authors': json.dumps(authors),
        'published_date': published_date,
        'category': paper.get('category', 'cs.AI'),
        'citation_count': 0,
        'influential_citation_count': 0,
        'quality_score': 0.0,
    }


def batch_insert_papers(conn, papers: List[Dict[str, Any]]) -> int:
    """Insert papers in batch, handling conflicts"""
    if not papers:
        return 0

    insert_sql = """
        INSERT INTO papers (
            id, title, abstract, authors, published_date, category,
            citation_count, influential_citation_count, quality_score
        ) VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            abstract = EXCLUDED.abstract,
            authors = EXCLUDED.authors,
            updated_at = NOW()
    """

    # Prepare values as tuples
    values = [
        (
            p['id'],
            p['title'],
            p['abstract'],
            p['authors'],
            p['published_date'],
            p['category'],
            p['citation_count'],
            p['influential_citation_count'],
            p['quality_score']
        )
        for p in papers
    ]

    with conn.cursor() as cur:
        execute_values(cur, insert_sql, values, page_size=100)
        conn.commit()

    return len(papers)


def extract_and_insert_concepts(conn, papers: List[Dict[str, Any]]) -> int:
    """Extract concepts from paper titles/abstracts and insert them"""
    # This is a simplified concept extraction - in production you'd use NLP
    # For now, we'll extract common AI/ML terms
    ai_terms = {
        'transformer': ('architecture', 'Transformer'),
        'attention': ('technique', 'Attention Mechanism'),
        'llm': ('architecture', 'Large Language Model'),
        'gpt': ('architecture', 'GPT'),
        'bert': ('architecture', 'BERT'),
        'diffusion': ('architecture', 'Diffusion Model'),
        'reinforcement learning': ('technique', 'Reinforcement Learning'),
        'neural network': ('architecture', 'Neural Network'),
        'cnn': ('architecture', 'Convolutional Neural Network'),
        'convolutional': ('architecture', 'Convolutional Neural Network'),
        'graph neural': ('architecture', 'Graph Neural Network'),
        'fine-tuning': ('technique', 'Fine-Tuning'),
        'fine tuning': ('technique', 'Fine-Tuning'),
        'prompt': ('technique', 'Prompt Engineering'),
        'chain of thought': ('technique', 'Chain of Thought'),
        'rlhf': ('technique', 'RLHF'),
        'vision transformer': ('architecture', 'Vision Transformer'),
        'vit': ('architecture', 'Vision Transformer'),
        'mixture of experts': ('architecture', 'Mixture of Experts'),
        'moe': ('architecture', 'Mixture of Experts'),
        'self-supervised': ('technique', 'Self-Supervised Learning'),
        'contrastive': ('technique', 'Contrastive Learning'),
        'autoencoder': ('architecture', 'Autoencoder'),
        'variational': ('architecture', 'Variational Autoencoder'),
        'generative': ('technique', 'Generative Model'),
        'multimodal': ('technique', 'Multimodal'),
        'embedding': ('technique', 'Embedding'),
        'retrieval': ('technique', 'Retrieval'),
        'rag': ('technique', 'Retrieval Augmented Generation'),
    }

    paper_concepts = []

    for paper in papers:
        text = f"{paper['title']} {paper['abstract']}".lower()
        paper_id = paper['id']

        for term, (category, name) in ai_terms.items():
            if term in text:
                paper_concepts.append({
                    'paper_id': paper_id,
                    'concept_name': name,
                    'concept_category': category,
                    'relevance': 0.8 if term in paper['title'].lower() else 0.5
                })

    if not paper_concepts:
        return 0

    # First, ensure concepts exist
    concept_names = list(set(pc['concept_name'] for pc in paper_concepts))

    with conn.cursor() as cur:
        # Upsert concepts
        for pc in paper_concepts:
            cur.execute("""
                INSERT INTO concepts (name, normalized_name, category, paper_count)
                VALUES (%s, %s, %s, 0)
                ON CONFLICT (name) DO NOTHING
            """, (
                pc['concept_name'],
                pc['concept_name'].lower().replace(' ', '_'),
                pc['concept_category']
            ))

        # Link papers to concepts
        for pc in paper_concepts:
            cur.execute("""
                INSERT INTO paper_concepts (paper_id, concept_id, relevance)
                SELECT %s, c.id, %s
                FROM concepts c
                WHERE c.name = %s
                ON CONFLICT (paper_id, concept_id) DO UPDATE SET relevance = EXCLUDED.relevance
            """, (pc['paper_id'], pc['relevance'], pc['concept_name']))

        conn.commit()

    return len(paper_concepts)


def update_concept_counts(conn):
    """Update paper counts for all concepts"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE concepts c
            SET paper_count = (
                SELECT COUNT(*) FROM paper_concepts pc WHERE pc.concept_id = c.id
            )
        """)
        conn.commit()


def main():
    parser = argparse.ArgumentParser(description='Import papers to Supabase')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of papers to import')
    parser.add_argument('--batch-size', type=int, default=500, help='Batch size for inserts')
    parser.add_argument('--ndjson', type=str, default=None, help='Path to NDJSON file')
    parser.add_argument('--skip-concepts', action='store_true', help='Skip concept extraction')
    args = parser.parse_args()

    # Find NDJSON file
    if args.ndjson:
        ndjson_path = Path(args.ndjson)
    else:
        # Default path from .env or fallback
        derived_dir = os.getenv('ATLAS_DERIVED_DIR', '../data/derived_12mo')
        ndjson_path = Path(__file__).parent.parent.parent / derived_dir.lstrip('../') / 'papers_catalog.ndjson'

    if not ndjson_path.exists():
        logger.error(f"NDJSON file not found: {ndjson_path}")
        sys.exit(1)

    logger.info(f"Reading papers from: {ndjson_path}")

    # Connect to database
    db_url = get_database_url()
    logger.info(f"Connecting to database...")

    conn = psycopg2.connect(db_url)
    logger.info("Connected to database")

    try:
        # Process papers in batches
        total_imported = 0
        total_concepts = 0
        batch = []

        for paper in read_papers_ndjson(ndjson_path, limit=args.limit):
            transformed = transform_paper(paper)
            batch.append(transformed)

            if len(batch) >= args.batch_size:
                imported = batch_insert_papers(conn, batch)
                total_imported += imported

                if not args.skip_concepts:
                    concepts = extract_and_insert_concepts(conn, batch)
                    total_concepts += concepts

                logger.info(f"Imported {total_imported} papers, {total_concepts} concept links...")
                batch = []

        # Import remaining batch
        if batch:
            imported = batch_insert_papers(conn, batch)
            total_imported += imported

            if not args.skip_concepts:
                concepts = extract_and_insert_concepts(conn, batch)
                total_concepts += concepts

        # Update concept counts
        if not args.skip_concepts:
            logger.info("Updating concept counts...")
            update_concept_counts(conn)

        logger.info(f"Import complete! Total papers: {total_imported}, Concept links: {total_concepts}")

        # Print summary
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM papers")
            paper_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM concepts")
            concept_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM paper_concepts")
            link_count = cur.fetchone()[0]

            cur.execute("SELECT category, COUNT(*) FROM papers GROUP BY category ORDER BY COUNT(*) DESC LIMIT 10")
            top_categories = cur.fetchall()

        logger.info(f"\nDatabase Summary:")
        logger.info(f"  Total papers: {paper_count}")
        logger.info(f"  Total concepts: {concept_count}")
        logger.info(f"  Paper-concept links: {link_count}")
        logger.info(f"\nTop categories:")
        for cat, count in top_categories:
            logger.info(f"  {cat}: {count}")

    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == '__main__':
    main()
