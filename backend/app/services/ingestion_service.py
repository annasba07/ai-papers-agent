"""
Data ingestion service for populating the knowledge graph

Orchestrates the full pipeline:
1. Fetch papers from arXiv
2. Store in database (or local dump)
3. Extract concepts
4. Generate embeddings
"""
import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import text

from app.db.database import database
from app.services.arxiv_service import arxiv_service
from app.services.embedding_service import get_embedding_service
from app.services import get_research_graph_service
from app.services.providers import (
    OpenAlexProvider,
    PapersWithCodeProvider,
    GitHubRepoProvider,
)
from app.services.providers.base import ProviderError
from app.utils.logger import LoggerMixin
from app.core.config import settings


class IngestionService(LoggerMixin):
    """Service for ingesting papers into the knowledge graph"""

    def __init__(
        self,
        openalex_provider: OpenAlexProvider | None = None,
        pwc_provider: PapersWithCodeProvider | None = None,
        github_provider: GitHubRepoProvider | None = None,
        local_dump_dir: Optional[str] = None
    ):
        self.arxiv_service = arxiv_service
        try:
            self.embedding_service = get_embedding_service()
        except ValueError as exc:
            self.log_warning(
                "Embedding service unavailable; embeddings will be skipped",
                error=str(exc)
            )
            self.embedding_service = None
        self.research_graph_service = get_research_graph_service()
        self.openalex_provider = openalex_provider or OpenAlexProvider()
        self.pwc_provider = pwc_provider or PapersWithCodeProvider()
        self.github_provider = github_provider or GitHubRepoProvider()
        env_dump_dir = local_dump_dir or os.getenv("LOCAL_DUMP_DIR")
        if env_dump_dir:
            self.local_dump_dir = Path(env_dump_dir).expanduser()
            self.local_dump_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.local_dump_dir = None
        self.use_local_dump = self.local_dump_dir is not None
        self.log_info(
            "Ingestion service initialized",
            local_dump=str(self.local_dump_dir) if self.local_dump_dir else None
        )

    @staticmethod
    def _shift_month(anchor: datetime, months: int) -> datetime:
        """Return a datetime representing the first day of the shifted month."""
        total_months = anchor.year * 12 + (anchor.month - 1) + months
        new_year = total_months // 12
        new_month = total_months % 12 + 1
        return datetime(new_year, new_month, 1)

    @staticmethod
    def _format_arxiv_datetime(dt: datetime) -> str:
        """Format datetime in arXiv API style: YYYYMMDDHHMM."""
        return dt.strftime("%Y%m%d%H%M")

    def _generate_time_windows(
        self,
        years: int,
        window_months: int
    ) -> List[Tuple[datetime, datetime]]:
        """
        Produce chronological month windows covering the last `years`.
        """
        if window_months < 1:
            raise ValueError("window_months must be >= 1")

        now = datetime.utcnow()
        window_start_anchor = datetime(now.year, now.month, 1)
        earliest_start = self._shift_month(window_start_anchor, -years * 12)

        windows = []
        current_start = earliest_start

        while current_start < now:
            next_start = self._shift_month(current_start, window_months)
            window_end = min(next_start - timedelta(minutes=1), now)
            windows.append((current_start, window_end))
            current_start = next_start

        return windows

    async def _fetch_papers_for_range(
        self,
        category: str,
        start: datetime,
        end: datetime,
    ) -> List[Dict[str, Any]]:
        query = (
            f"cat:{category} AND submittedDate:["
            f"{self._format_arxiv_datetime(start)} TO {self._format_arxiv_datetime(end)}]"
        )

        papers = await self.arxiv_service.search_papers(query, max_results=None)
        threshold = settings.ARXIV_SPLIT_THRESHOLD or 0
        min_days = settings.ARXIV_MIN_SPLIT_DAYS or 0
        delta = end - start

        if (
            threshold
            and len(papers) >= threshold
            and delta.days >= min_days
        ):
            mid = start + delta / 2
            mid = mid.replace(second=0, microsecond=0)
            if mid <= start or mid >= end:
                return papers

            first_end = mid
            second_start = mid + timedelta(minutes=1)

            first_half = await self._fetch_papers_for_range(category, start, first_end)
            second_half = await self._fetch_papers_for_range(category, second_start, end)

            merged: Dict[str, Dict[str, Any]] = {}
            for record in first_half + second_half:
                merged[record["id"]] = record
            return list(merged.values())

        return papers

    async def _ingest_window(
        self,
        category: str,
        start: datetime,
        end: datetime,
        generate_embeddings: bool,
        extract_concepts: bool,
    ) -> Dict[str, Any]:
        papers = await self._fetch_papers_for_range(category, start, end)
        stats = {
            "fetched": len(papers),
            "stored": 0,
            "duplicates": 0,
            "embeddings_generated": 0,
            "concepts_extracted": 0,
            "errors": 0,
            "dump_path": None,
        }

        if not papers:
            return stats

        storage_context = {
            "category": category,
            "window_start": start,
            "window_end": end,
        }

        if self.use_local_dump:
            dump_path, records = self._dump_to_local(papers, storage_context=storage_context)
            stats["dump_path"] = str(dump_path)
            stats["stored"] = len(records)
        else:
            store_result = await self._store_papers(papers, storage_context=storage_context)
            stats.update({
                "stored": store_result["stored"],
                "duplicates": store_result["duplicates"],
                "errors": store_result["errors"],
            })
            records = store_result["papers"]

            if (
                generate_embeddings
                and stats["stored"] > 0
                and self.embedding_service
            ):
                embedding_result = await self.embedding_service.embed_papers_batch(
                    records,
                    force_update=False,
                )
                stats["embeddings_generated"] = embedding_result
            elif generate_embeddings and self.embedding_service is None:
                self.log_warning("Embedding generation requested but service unavailable")

            if (
                extract_concepts
                and stats["stored"] > 0
                and not self.use_local_dump
            ):
                from app.services.concept_extraction_service import get_concept_extraction_service

                concept_service = get_concept_extraction_service()
                concept_result = await concept_service.extract_concepts_batch(records)
                stats["concepts_extracted"] = concept_result["total_concepts"]

        return stats

    async def ingest_papers(
        self,
        query: str = None,
        category: str = None,
        max_results: int = 100,
        generate_embeddings: bool = True,
        extract_concepts: bool = False,
        storage_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main ingestion pipeline

        Args:
            query: arXiv search query (e.g., "attention mechanisms")
            category: arXiv category (e.g., "cs.AI") - used if no query
            max_results: Maximum papers to fetch
            generate_embeddings: Whether to generate embeddings immediately
            extract_concepts: Whether to extract concepts (slower)

        Returns:
            Stats dict with counts
        """
        self.log_info(
            "Starting ingestion pipeline",
            query=query,
            category=category,
            max_results=max_results
        )

        # Connect to database
        if not self.use_local_dump and not database.is_connected:
            await database.connect()

        stats = {
            "fetched": 0,
            "stored": 0,
            "duplicates": 0,
            "embeddings_generated": 0,
            "concepts_extracted": 0,
            "errors": 0
        }

        try:
            # Step 1: Fetch papers from arXiv
            if query:
                papers = await self.arxiv_service.search_papers(query, max_results)
            elif category:
                papers = await self.arxiv_service.get_recent_papers(category, max_results)
            else:
                raise ValueError("Either query or category must be provided")

            stats["fetched"] = len(papers)
            self.log_info(f"Fetched {len(papers)} papers from arXiv")

            if not papers:
                return stats

            # Step 2: Store papers in database or local dump
            stored_papers = await self._store_papers(papers, storage_context=storage_context)
            stats["stored"] = stored_papers["stored"]
            stats["duplicates"] = stored_papers["duplicates"]
            stats["errors"] = stored_papers["errors"]
            stats["dump_path"] = stored_papers.get("dump_path")
            newly_stored = stored_papers["papers"]

            # Step 3: Generate embeddings (if requested and papers were stored)
            if (
                not self.use_local_dump
                and generate_embeddings
                and stats["stored"] > 0
                and self.embedding_service
            ):
                self.log_info("Generating embeddings for new papers...")
                embedding_result = await self.embedding_service.embed_papers_batch(
                    newly_stored,
                    force_update=False
                )
                stats["embeddings_generated"] = embedding_result
            elif generate_embeddings and self.embedding_service is None:
                self.log_warning("Embedding generation requested but service unavailable")

            # Step 4: Extract concepts (if requested)
            if (
                not self.use_local_dump
                and extract_concepts
                and stats["stored"] > 0
            ):
                from app.services.concept_extraction_service import get_concept_extraction_service
                concept_service = get_concept_extraction_service()

                self.log_info("Extracting concepts from new papers...")
                concept_result = await concept_service.extract_concepts_batch(
                    newly_stored
                )
                stats["concepts_extracted"] = concept_result["total_concepts"]

            # Step 5: Research graph enrichment scaffold
            if newly_stored and not self.use_local_dump:
                await self._enrich_research_graph(newly_stored)

            self.log_info("Ingestion pipeline complete", stats=stats)
            return stats

        except Exception as e:
            self.log_error("Ingestion pipeline failed", error=e)
            stats["errors"] += 1
            raise

    async def _store_papers(
        self,
        papers: List[Dict[str, Any]],
        storage_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """
        Store papers in database, handling duplicates

        Returns:
            Dict with stored, duplicates, errors counts
        """
        result = {
            "stored": 0,
            "duplicates": 0,
            "errors": 0,
            "papers": []
        }

        if self.use_local_dump and self.local_dump_dir:
            dump_path, sanitized_records = self._dump_to_local(papers, storage_context)
            result["stored"] = len(sanitized_records)
            result["papers"] = sanitized_records
            result["dump_path"] = str(dump_path)
            return result

        for paper in papers:
            try:
                # Check if paper already exists
                existing = await database.fetch_one(
                    "SELECT id FROM papers WHERE id = :paper_id",
                    {"paper_id": paper["id"]}
                )

                if existing:
                    result["duplicates"] += 1
                    self.log_debug(f"Paper {paper['id']} already exists, skipping")
                    continue

                # Insert new paper
                await database.execute(
                    """
                        INSERT INTO papers (
                            id, title, abstract, authors, published_date,
                            updated_date, category, ingested_at
                        ) VALUES (
                            :id, :title, :abstract, :authors, :published_date,
                            :updated_date, :category, CURRENT_TIMESTAMP
                        )
                    """,
                    {
                        "id": paper["id"],
                        "title": paper["title"],
                        "abstract": paper["summary"],
                        "authors": paper["authors"],  # Will be stored as JSONB
                        "published_date": paper["published"],
                        "updated_date": paper.get("updated", paper["published"]),
                        "category": paper["category"]
                    }
                )

                result["stored"] += 1
                sanitized = self._sanitize_paper_record(paper)
                result["papers"].append(sanitized)
                self.log_debug(f"Stored paper {paper['id']}: {paper['title'][:50]}...")

            except Exception as e:
                result["errors"] += 1
                self.log_error(f"Failed to store paper {paper.get('id', 'unknown')}", error=e)

        return result

    def _dump_to_local(
        self,
        papers: List[Dict[str, Any]],
        storage_context: Optional[Dict[str, Any]]
    ) -> Tuple[Path, List[Dict[str, Any]]]:
        if not self.local_dump_dir:
            raise RuntimeError("Local dump directory not configured")

        sanitized_records = [self._sanitize_paper_record(paper) for paper in papers]

        context = storage_context or {}
        category = context.get("category", "uncategorized")
        start_dt = self._ensure_datetime(context.get("window_start"))
        end_dt = self._ensure_datetime(context.get("window_end"))

        timestamp = datetime.utcnow()
        month_segment = start_dt.strftime("%Y-%m") if start_dt else timestamp.strftime("%Y-%m")
        window_dir = self.local_dump_dir / category / month_segment
        window_dir.mkdir(parents=True, exist_ok=True)

        start_label = start_dt.strftime("%Y%m%d") if start_dt else "na"
        end_label = end_dt.strftime("%Y%m%d") if end_dt else "na"
        file_name = f"papers_{start_label}_{end_label}_{timestamp.strftime('%Y%m%dT%H%M%S')}.ndjson"
        file_path = window_dir / file_name

        start_iso = start_dt.isoformat() if start_dt else None
        end_iso = end_dt.isoformat() if end_dt else None

        records_with_context: List[Dict[str, Any]] = []
        with file_path.open("w", encoding="utf-8") as fh:
            for record in sanitized_records:
                enriched = record.copy()
                if start_iso:
                    enriched["window_start"] = start_iso
                if end_iso:
                    enriched["window_end"] = end_iso
                if "category" not in enriched:
                    enriched["category"] = category
                records_with_context.append(enriched)
                fh.write(json.dumps(enriched, ensure_ascii=False) + "\n")

        self.log_info("Dumped papers to local file", path=str(file_path), count=len(papers))
        return file_path, records_with_context

    @staticmethod
    def _sanitize_paper_record(paper: Dict[str, Any]) -> Dict[str, Any]:
        published = paper.get("published")
        if isinstance(published, datetime):
            published_value = published.isoformat()
        else:
            published_value = published

        return {
            "id": paper.get("id"),
            "title": paper.get("title"),
            "abstract": paper.get("summary"),
            "authors": paper.get("authors", []),
            "published": published_value,
            "category": paper.get("category"),
            "link": paper.get("link"),
        }

    @staticmethod
    def _ensure_datetime(value: Any) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        return None

    async def _enrich_research_graph(self, papers: List[Dict[str, Any]]) -> None:
        """
        Placeholder for the Atlas enrichment layer. Currently logs intended operations.
        """
        paper_ids = [paper["id"] for paper in papers if paper.get("id")]
        if not paper_ids:
            return

        self.log_info("Enriching research graph for papers", paper_count=len(paper_ids))

        # Author + organisation enrichment
        try:
            author_payloads = await self.openalex_provider.fetch_authors_and_affiliations(paper_ids)
            for payload in author_payloads:
                await self.research_graph_service.upsert_authors(
                    payload.get("authors", []),
                    paper_id=payload.get("paper_id")
                )
        except ProviderError as exc:
            self.log_warning("Author enrichment failed", error=str(exc))
        except Exception as exc:  # noqa: BLE001
            self.log_warning("Unexpected author enrichment failure", error=str(exc))

        # Citation edges
        try:
            citation_edges = await self.openalex_provider.fetch_citation_edges(paper_ids)
            if citation_edges:
                self.log_debug("Citation enrichment ready", edges=len(citation_edges))
                # TODO: insert via bulk copy utility once implemented
        except Exception as exc:  # noqa: BLE001
            self.log_warning("Citation enrichment failed", error=str(exc))

        # Benchmarks and taxonomy seeds
        try:
            observations = await self.pwc_provider.fetch_benchmark_observations(paper_ids)
            if observations:
                self.log_debug("Benchmark enrichment ready", observations=len(observations))
                # TODO: call research_graph_service to persist benchmark rows
        except ProviderError as exc:
            self.log_warning("Benchmark enrichment failed", error=str(exc))
        except Exception as exc:  # noqa: BLE001
            self.log_warning("Unexpected benchmark enrichment failure", error=str(exc))

    async def ingest_by_category(
        self,
        category: str,
        max_results: int = 100,
        generate_embeddings: bool = True
    ) -> Dict[str, Any]:
        """
        Convenience method to ingest papers by category

        Args:
            category: arXiv category (e.g., 'cs.AI', 'cs.CV', 'cs.LG')
            max_results: Maximum papers to fetch
            generate_embeddings: Whether to generate embeddings

        Returns:
            Ingestion stats
        """
        return await self.ingest_papers(
            category=category,
            max_results=max_results,
            generate_embeddings=generate_embeddings,
            storage_context={"category": category}
        )

    async def ingest_recent_papers(
        self,
        categories: List[str] = ["cs.AI", "cs.LG", "cs.CV"],
        max_per_category: int = 50,
        generate_embeddings: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest recent papers from multiple categories

        Args:
            categories: List of arXiv categories
            max_per_category: Max papers per category
            generate_embeddings: Whether to generate embeddings

        Returns:
            Combined stats across all categories
        """
        self.log_info(f"Ingesting recent papers from {len(categories)} categories")

        combined_stats = {
            "fetched": 0,
            "stored": 0,
            "duplicates": 0,
            "embeddings_generated": 0,
            "errors": 0,
            "categories_processed": 0
        }

        for category in categories:
            try:
                self.log_info(f"Processing category: {category}")
                stats = await self.ingest_by_category(
                    category=category,
                    max_results=max_per_category,
                    generate_embeddings=generate_embeddings
                )

                combined_stats["fetched"] += stats["fetched"]
                combined_stats["stored"] += stats["stored"]
                combined_stats["duplicates"] += stats["duplicates"]
                combined_stats["embeddings_generated"] += stats["embeddings_generated"]
                combined_stats["errors"] += stats["errors"]
                combined_stats["categories_processed"] += 1

                # Rate limiting: small delay between categories
                await asyncio.sleep(1)

            except Exception as e:
                self.log_error(f"Failed to process category {category}", error=e)
                combined_stats["errors"] += 1

        self.log_info("Completed ingesting recent papers", stats=combined_stats)
        return combined_stats

    async def bootstrap_recent_atlas(
        self,
        categories: List[str],
        years: int = 3,
        window_months: int = 3,
        max_per_window: int = 200,
        generate_embeddings: bool = False,
        extract_concepts: bool = False,
        sleep_seconds: float = 0.5
    ) -> Dict[str, Any]:
        """
        Seed the research atlas with papers from the last N years (chunked by window).

        This focuses on recent research so we can demonstrate the rich atlas UX
        without ingesting the full historical corpus.
        """
        if years < 1:
            raise ValueError("years must be >= 1")

        windows = self._generate_time_windows(years=years, window_months=window_months)
        total_windows = len(windows)
        self.log_info(
            "Bootstrapping recent atlas",
            categories=len(categories),
            years=years,
            window_months=window_months,
            windows=total_windows
        )

        effective_max = max_per_window if (max_per_window and max_per_window > 0) else None

        summary = {
            "categories": categories,
            "years": years,
            "window_months": window_months,
            "max_per_window": effective_max,
            "total_windows": total_windows,
            "stats": [],
            "local_dump_dir": str(self.local_dump_dir) if self.local_dump_dir else None
        }

        for category in categories:
            category_stats = {
                "category": category,
                "windows_processed": 0,
                "fetched": 0,
                "stored": 0,
                "duplicates": 0,
                "errors": 0,
                "dumps": []
            }

            for start, end in windows:
                query = (
                    f"cat:{category} AND submittedDate:["
                    f"{self._format_arxiv_datetime(start)} TO {self._format_arxiv_datetime(end)}]"
                )

                self.log_info(
                    "Processing window",
                    category=category,
                    start=start.isoformat(),
                    end=end.isoformat(),
                    query=query
                )

                try:
                    stats = await self._ingest_window(
                        category=category,
                        start=start,
                        end=end,
                        generate_embeddings=generate_embeddings,
                        extract_concepts=extract_concepts,
                    )

                    category_stats["windows_processed"] += 1
                    category_stats["fetched"] += stats["fetched"]
                    category_stats["stored"] += stats["stored"]
                    category_stats["duplicates"] += stats["duplicates"]
                    category_stats["errors"] += stats["errors"]
                    if stats.get("dump_path"):
                        category_stats["dumps"].append(stats["dump_path"])

                    await asyncio.sleep(sleep_seconds)

                except Exception as exc:  # noqa: BLE001
                    self.log_error(
                        "Failed to process window",
                        category=category,
                        start=start.isoformat(),
                        end=end.isoformat(),
                        error=str(exc)
                    )
                    category_stats["errors"] += 1

            summary["stats"].append(category_stats)

        self.log_info("Bootstrap completed", summary=summary)
        return summary

    async def ingest_specific_paper(
        self,
        arxiv_id: str,
        generate_embedding: bool = True,
        extract_concepts: bool = False
    ) -> Dict[str, Any]:
        """
        Ingest a specific paper by arXiv ID

        Args:
            arxiv_id: arXiv paper ID (e.g., '2010.11929')
            generate_embedding: Whether to generate embedding
            extract_concepts: Whether to extract concepts

        Returns:
            Ingestion result
        """
        self.log_info(f"Ingesting specific paper: {arxiv_id}")

        if not database.is_connected:
            await database.connect()

        try:
            # Fetch paper from arXiv
            paper = await self.arxiv_service.get_paper_by_id(arxiv_id)

            if not paper:
                return {
                    "success": False,
                    "error": f"Paper {arxiv_id} not found on arXiv"
                }

            # Store paper
            result = await self._store_papers(
                [paper],
                storage_context={"category": paper.get("category"), "window_start": paper.get("published")}
            )

            response = {
                "success": result["stored"] > 0,
                "paper_id": arxiv_id,
                "already_existed": result["duplicates"] > 0,
                "embedding_generated": False,
                "concepts_extracted": False
            }

            # Generate embedding if paper was stored
            if result["stored"] > 0 and generate_embedding:
                await self.embedding_service.embed_paper(
                    paper_id=paper["id"],
                    title=paper["title"],
                    abstract=paper["summary"]
                )
                response["embedding_generated"] = True

            # Extract concepts if requested
            if result["stored"] > 0 and extract_concepts:
                from app.services.concept_extraction_service import get_concept_extraction_service
                concept_service = get_concept_extraction_service()

                await concept_service.extract_concepts_for_paper(paper)
                response["concepts_extracted"] = True

            return response

        except Exception as e:
            self.log_error(f"Failed to ingest paper {arxiv_id}", error=e)
            return {
                "success": False,
                "paper_id": arxiv_id,
                "error": str(e)
            }

    async def get_ingestion_stats(self) -> Dict[str, Any]:
        """
        Get statistics about ingested papers

        Returns:
            Stats about papers in database
        """
        if not database.is_connected:
            await database.connect()

        # Total papers
        total_result = await database.fetch_one(
            text("SELECT COUNT(*) as count FROM papers")
        )

        # Papers by category
        category_result = await database.fetch_all(
            text("""
                SELECT category, COUNT(*) as count
                FROM papers
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            """)
        )

        # Recent ingestions
        recent_result = await database.fetch_one(
            text("""
                SELECT COUNT(*) as count
                FROM papers
                WHERE ingested_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
            """)
        )

        # Embedding coverage
        embedding_result = await database.fetch_one(
            text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(embedding) as with_embedding,
                    ROUND(100.0 * COUNT(embedding) / COUNT(*), 2) as coverage_pct
                FROM papers
            """)
        )

        return {
            "total_papers": total_result["count"],
            "recent_24h": recent_result["count"],
            "by_category": [dict(r) for r in category_result],
            "embedding_coverage": {
                "total": embedding_result["total"],
                "with_embedding": embedding_result["with_embedding"],
                "coverage_percentage": float(embedding_result["coverage_pct"])
            }
        }


# Global instance
_ingestion_service: Optional[IngestionService] = None


def get_ingestion_service(**kwargs: Any) -> IngestionService:
    """Get or create global ingestion service instance"""
    global _ingestion_service
    if kwargs or _ingestion_service is None:
        _ingestion_service = IngestionService(**kwargs)
    return _ingestion_service
