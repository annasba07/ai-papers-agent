"""
Daily Paper Ingestion Service

Fetches new papers from arXiv daily and appends them to the local atlas.
Supports:
- Multiple category ingestion
- Deduplication against existing papers
- Incremental embedding generation
- Hot-reload of in-memory atlas
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


class DailyIngestionService(LoggerMixin):
    """
    Service for daily paper ingestion from arXiv.

    Fetches recent papers, deduplicates, appends to atlas,
    and optionally generates embeddings.
    """

    def __init__(self) -> None:
        self._last_run: Optional[datetime] = None
        self._last_stats: Dict = {}
        self._is_running: bool = False

        # Paths
        self._atlas_dir = Path(settings.ATLAS_DERIVED_DIR).expanduser().resolve()
        self._catalog_path = self._atlas_dir / "papers_catalog.ndjson"
        self._embeddings_dir = Path(settings.ATLAS_EMBED_CACHE_DIR).expanduser().resolve()

        self.log_info("Daily ingestion service initialized")

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def last_run(self) -> Optional[datetime]:
        return self._last_run

    @property
    def last_stats(self) -> Dict:
        return self._last_stats

    def _load_existing_ids(self) -> Set[str]:
        """Load existing paper IDs from catalog for deduplication."""
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

            self.log_info(f"Loaded {len(existing_ids)} existing paper IDs")
            return existing_ids

        except Exception as e:
            self.log_error("Failed to load existing IDs", error=e)
            return existing_ids

    def _format_paper_for_catalog(self, paper: Dict) -> Dict:
        """Format arXiv paper data for catalog storage."""
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

    async def _fetch_recent_papers(
        self,
        categories: List[str],
        max_per_category: int = 100,
        days_back: int = 2
    ) -> List[Dict]:
        """Fetch recent papers from arXiv for given categories."""
        all_papers: List[Dict] = []

        for category in categories:
            try:
                self.log_info(f"Fetching papers for category: {category}")

                # Query for recent papers in category
                papers = await arxiv_service.get_recent_papers(
                    category=category,
                    max_results=max_per_category
                )

                # Filter to papers from last N days
                cutoff = datetime.utcnow() - timedelta(days=days_back)
                recent = [
                    p for p in papers
                    if p.get("published") and p["published"] >= cutoff
                ]

                all_papers.extend(recent)
                self.log_info(f"Found {len(recent)} recent papers in {category}")

                # Rate limiting - be nice to arXiv
                await asyncio.sleep(1.0)

            except Exception as e:
                self.log_error(f"Failed to fetch {category}", error=e)
                continue

        return all_papers

    async def run_ingestion(
        self,
        categories: Optional[List[str]] = None,
        max_per_category: int = 100,
        days_back: int = 2,
        generate_embeddings: bool = False
    ) -> Dict:
        """
        Run the daily ingestion process.

        Args:
            categories: List of arXiv categories to fetch (default: from settings)
            max_per_category: Max papers to fetch per category
            days_back: How many days back to look for papers
            generate_embeddings: Whether to generate embeddings for new papers

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

            self.log_info(
                "Starting daily ingestion",
                categories=len(categories),
                max_per_category=max_per_category,
                days_back=days_back
            )

            # Load existing paper IDs for deduplication
            existing_ids = self._load_existing_ids()

            # Fetch recent papers
            fetched_papers = await self._fetch_recent_papers(
                categories=categories,
                max_per_category=max_per_category,
                days_back=days_back
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

            # Append to catalog
            appended_count = 0
            if new_papers:
                appended_count = await self._append_to_catalog(new_papers)

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
                "papers_appended": appended_count,
                "embeddings_generated": embeddings_generated,
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
