"""
Daily Paper Ingestion Service

Fetches new papers from arXiv daily and inserts them to PostgreSQL.
Supports:
- Multiple category ingestion
- Deduplication against existing papers
- Auto-creation of enrichment jobs via database triggers
- Optional NDJSON backup for offline analysis

The pipeline flow:
1. Fetch papers from arXiv
2. Deduplicate against PostgreSQL
3. Insert new papers to PostgreSQL
4. Database triggers auto-create enrichment jobs
5. Workers process jobs automatically
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
import asyncio

import numpy as np

from app.core.config import settings
from app.utils.logger import LoggerMixin
from app.services.arxiv_service import arxiv_service
from app.db.database import database


class DailyIngestionService(LoggerMixin):
    """
    Service for daily paper ingestion from arXiv.

    Fetches recent papers, deduplicates against PostgreSQL,
    and inserts new papers directly to the database.
    Database triggers then auto-create enrichment jobs.
    """

    def __init__(self) -> None:
        self._last_run: Optional[datetime] = None
        self._last_stats: Dict = {}
        self._is_running: bool = False

        # Paths for optional NDJSON backup
        self._atlas_dir = Path(settings.ATLAS_DERIVED_DIR).expanduser().resolve()
        self._catalog_path = self._atlas_dir / "papers_catalog.ndjson"
        self._embeddings_dir = Path(settings.ATLAS_EMBED_CACHE_DIR).expanduser().resolve()

        self.log_info("Daily ingestion service initialized (PostgreSQL mode)")

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def last_run(self) -> Optional[datetime]:
        return self._last_run

    @property
    def last_stats(self) -> Dict:
        return self._last_stats

    async def _load_existing_ids_from_db(self) -> Set[str]:
        """Load existing paper IDs from PostgreSQL for deduplication."""
        existing_ids: Set[str] = set()

        try:
            query = "SELECT id FROM papers"
            rows = await database.fetch_all(query)

            for row in rows:
                paper_id = row["id"]
                # Normalize ID (remove version suffix)
                base_id = paper_id.split("v")[0] if "v" in paper_id else paper_id
                existing_ids.add(base_id)

            self.log_info(f"Loaded {len(existing_ids)} existing paper IDs from PostgreSQL")
            return existing_ids

        except Exception as e:
            self.log_error("Failed to load existing IDs from PostgreSQL", error=e)
            return existing_ids

    def _load_existing_ids(self) -> Set[str]:
        """Load existing paper IDs from NDJSON catalog (fallback/backup)."""
        existing_ids: Set[str] = set()

        if not self._catalog_path.exists():
            return existing_ids

        try:
            with self._catalog_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        paper = json.loads(line)
                        paper_id = paper.get("id", "")
                        # Normalize ID (remove version suffix)
                        base_id = paper_id.split("v")[0] if "v" in paper_id else paper_id
                        existing_ids.add(base_id)
                    except json.JSONDecodeError:
                        continue

            self.log_info(f"Loaded {len(existing_ids)} existing paper IDs from NDJSON")
            return existing_ids

        except Exception as e:
            self.log_error("Failed to load existing IDs from NDJSON", error=e)
            return existing_ids

    def _format_paper_for_catalog(self, paper: Dict) -> Dict:
        """Format arXiv paper data for NDJSON catalog storage."""
        # Ensure datetime is serialized as string
        published = paper.get("published")
        if isinstance(published, datetime):
            published = published.isoformat()

        return {
            "id": paper.get("id", ""),
            "title": paper.get("title", "").replace("\n", " ").strip(),
            "authors": paper.get("authors", []),
            "summary": paper.get("summary", "").replace("\n", " ").strip(),
            "published": published,
            "link": paper.get("link", ""),
            "category": paper.get("category", "Unknown"),
            "ingested_at": datetime.utcnow().isoformat(),
        }

    def _format_paper_for_database(self, paper: Dict) -> Dict:
        """Format arXiv paper data for PostgreSQL insertion."""
        published = paper.get("published")
        if isinstance(published, str):
            try:
                if 'T' in published:
                    published = datetime.fromisoformat(published.replace('Z', '+00:00'))
                else:
                    published = datetime.strptime(published, '%Y-%m-%d')
            except (ValueError, TypeError):
                published = datetime.utcnow()

        authors = paper.get("authors", [])
        if isinstance(authors, str):
            authors = [authors]

        return {
            "id": paper.get("id", ""),
            "title": paper.get("title", "").replace("\n", " ").strip(),
            "abstract": paper.get("summary", "").replace("\n", " ").strip(),
            "authors": json.dumps(authors),
            "published_date": published,
            "category": paper.get("category", "cs.AI"),
            "citation_count": 0,
            "influential_citation_count": 0,
            "quality_score": 0.0,
        }

    async def _insert_to_database(self, papers: List[Dict], batch_size: int = 100) -> int:
        """
        Insert new papers directly to PostgreSQL.

        This triggers the auto-creation of:
        1. paper_processing_state (via trigger_paper_processing_state)
        2. enrichment jobs (via trigger_auto_create_enrichment_jobs)

        Returns:
            Number of papers successfully inserted
        """
        if not papers:
            return 0

        inserted = 0

        # Process in batches
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]

            try:
                for paper in batch:
                    formatted = self._format_paper_for_database(paper)

                    # Use INSERT ... ON CONFLICT to handle duplicates gracefully
                    query = """
                        INSERT INTO papers (
                            id, title, abstract, authors, published_date, category,
                            citation_count, influential_citation_count, quality_score
                        ) VALUES (
                            :id, :title, :abstract, :authors, :published_date, :category,
                            :citation_count, :influential_citation_count, :quality_score
                        )
                        ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            abstract = EXCLUDED.abstract,
                            authors = EXCLUDED.authors,
                            updated_at = NOW()
                        RETURNING id
                    """

                    result = await database.fetch_one(query, formatted)
                    if result:
                        inserted += 1

                self.log_info(f"Inserted batch {i // batch_size + 1}: {len(batch)} papers")

            except Exception as e:
                self.log_error(f"Failed to insert batch {i // batch_size + 1}", error=e)
                continue

        self.log_info(f"Inserted {inserted} papers to PostgreSQL (triggers will auto-create jobs)")
        return inserted

    async def _fetch_recent_papers(
        self,
        categories: List[str],
        max_per_category: int = 1000,
        days_back: int = 2,
        since_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Fetch recent papers from arXiv for given categories.

        Args:
            categories: List of arXiv categories
            max_per_category: Safety limit per category (default 1000)
            days_back: Fallback if since_date not provided
            since_date: Absolute date cutoff - preferred over days_back

        Returns:
            List of papers from all categories since the cutoff date
        """
        all_papers: List[Dict] = []

        # Determine date cutoff
        if since_date is None:
            since_date = datetime.utcnow() - timedelta(days=days_back)

        self.log_info(
            f"Fetching papers since {since_date.isoformat()}",
            categories=len(categories),
            max_per_category=max_per_category
        )

        for category in categories:
            try:
                self.log_info(f"Fetching papers for category: {category}")

                # Use date-based cutoff - fetches ALL papers since that date
                papers = await arxiv_service.get_recent_papers(
                    category=category,
                    max_results=max_per_category,
                    since_date=since_date
                )

                all_papers.extend(papers)
                self.log_info(f"Found {len(papers)} papers in {category} since {since_date.date()}")

                # Rate limiting - be nice to arXiv
                await asyncio.sleep(1.0)

            except Exception as e:
                self.log_error(f"Failed to fetch {category}", error=e)
                continue

        return all_papers

    async def run_ingestion(
        self,
        categories: Optional[List[str]] = None,
        max_per_category: int = 50000,
        days_back: int = 2,
        since_date: Optional[datetime] = None,
        generate_embeddings: bool = False,
        write_ndjson_backup: bool = False
    ) -> Dict:
        """
        Run the daily ingestion process.

        Fetches papers from arXiv, deduplicates against PostgreSQL,
        and inserts new papers directly to the database.
        Database triggers auto-create enrichment jobs for processing.

        Args:
            categories: List of arXiv categories to fetch (default: from settings)
            max_per_category: Safety limit for papers per category (default: 50000)
            days_back: Fallback for how many days back (if since_date not provided)
            since_date: Absolute date cutoff - fetch ALL papers since this date (preferred)
            generate_embeddings: Whether to generate embeddings for new papers
            write_ndjson_backup: Also write to NDJSON catalog file (for backup/offline analysis)

        Returns:
            Dictionary with ingestion statistics
        """
        if self._is_running:
            return {
                "status": "already_running",
                "message": "Ingestion is already in progress"
            }

        self._is_running = True
        start_time = datetime.utcnow()

        try:
            # Use default categories if not specified
            if categories is None:
                categories = settings.DEFAULT_AI_CATEGORIES

            # Determine effective date cutoff
            effective_since = since_date
            if effective_since is None:
                effective_since = datetime.utcnow() - timedelta(days=days_back)

            self.log_info(
                "Starting daily ingestion (PostgreSQL mode)",
                categories=len(categories),
                max_per_category=max_per_category,
                since_date=effective_since.isoformat()
            )

            # Load existing paper IDs from PostgreSQL for deduplication
            existing_ids = await self._load_existing_ids_from_db()

            # Fetch recent papers with date cutoff
            fetched_papers = await self._fetch_recent_papers(
                categories=categories,
                max_per_category=max_per_category,
                since_date=effective_since
            )

            # Deduplicate
            new_papers: List[Dict] = []
            for paper in fetched_papers:
                paper_id = paper.get("id", "")
                base_id = paper_id.split("v")[0] if "v" in paper_id else paper_id

                if base_id and base_id not in existing_ids:
                    new_papers.append(paper)
                    existing_ids.add(base_id)  # Prevent duplicates within batch

            self.log_info(f"Found {len(new_papers)} new papers after deduplication")

            # Insert to PostgreSQL (triggers auto-create enrichment jobs)
            inserted_count = 0
            if new_papers:
                inserted_count = await self._insert_to_database(new_papers)

            # Optionally write to NDJSON backup
            ndjson_count = 0
            if write_ndjson_backup and new_papers:
                ndjson_count = await self._append_to_catalog(new_papers)

            # Generate embeddings if requested
            embeddings_generated = 0
            if generate_embeddings and new_papers:
                embeddings_generated = await self._generate_embeddings_for_new(new_papers)

            # Update stats
            end_time = datetime.utcnow()
            self._last_run = end_time
            self._last_stats = {
                "status": "success",
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "duration_seconds": (end_time - start_time).total_seconds(),
                "categories_processed": len(categories),
                "papers_fetched": len(fetched_papers),
                "papers_new": len(new_papers),
                "papers_inserted_db": inserted_count,
                "papers_ndjson_backup": ndjson_count,
                "embeddings_generated": embeddings_generated,
                "jobs_created": inserted_count * 9,  # 9 enrichment stages per paper
            }

            self.log_info("Daily ingestion complete", stats=self._last_stats)
            return self._last_stats

        except Exception as e:
            self.log_error("Daily ingestion failed", error=e)
            self._last_stats = {
                "status": "error",
                "error": str(e),
                "started_at": start_time.isoformat(),
            }
            return self._last_stats

        finally:
            self._is_running = False

    async def _append_to_catalog(self, papers: List[Dict]) -> int:
        """Append new papers to the catalog file."""
        if not papers:
            return 0

        # Ensure directory exists
        self._atlas_dir.mkdir(parents=True, exist_ok=True)

        appended = 0
        try:
            with self._catalog_path.open("a", encoding="utf-8") as f:
                for paper in papers:
                    formatted = self._format_paper_for_catalog(paper)
                    f.write(json.dumps(formatted) + "\n")
                    appended += 1

            self.log_info(f"Appended {appended} papers to catalog")
            return appended

        except Exception as e:
            self.log_error("Failed to append to catalog", error=e)
            return appended

    async def _generate_embeddings_for_new(self, papers: List[Dict]) -> int:
        """
        Generate embeddings for new papers.

        Note: This is a placeholder. Full implementation would:
        1. Load the embedding model
        2. Generate embeddings for new papers
        3. Append to the cached embeddings file
        """
        # For now, just log - full embedding generation is expensive
        # and should be done via the CLI tools
        self.log_info(
            f"Embedding generation requested for {len(papers)} papers. "
            "Run 'python -m app.cli.generate_embeddings --incremental' to generate."
        )
        return 0

    def get_status(self) -> Dict:
        """Get current service status."""
        return {
            "is_running": self._is_running,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "last_stats": self._last_stats,
            "catalog_path": str(self._catalog_path),
            "catalog_exists": self._catalog_path.exists(),
        }


# Module-level singleton
_daily_ingestion_service: Optional[DailyIngestionService] = None


def get_daily_ingestion_service() -> DailyIngestionService:
    """Get or create the daily ingestion service singleton."""
    global _daily_ingestion_service
    if _daily_ingestion_service is None:
        _daily_ingestion_service = DailyIngestionService()
    return _daily_ingestion_service
