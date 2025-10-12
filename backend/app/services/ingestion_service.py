"""
Data ingestion service for populating the knowledge graph

Orchestrates the full pipeline:
1. Fetch papers from arXiv
2. Store in database
3. Extract concepts
4. Generate embeddings
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text

from app.db.database import database
from app.services.arxiv_service import arxiv_service
from app.services.embedding_service import get_embedding_service
from app.utils.logger import LoggerMixin


class IngestionService(LoggerMixin):
    """Service for ingesting papers into the knowledge graph"""

    def __init__(self):
        self.arxiv_service = arxiv_service
        self.embedding_service = get_embedding_service()
        self.log_info("Ingestion service initialized")

    async def ingest_papers(
        self,
        query: str = None,
        category: str = None,
        max_results: int = 100,
        generate_embeddings: bool = True,
        extract_concepts: bool = False
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
        if not database.is_connected:
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

            # Step 2: Store papers in database
            stored_papers = await self._store_papers(papers)
            stats["stored"] = stored_papers["stored"]
            stats["duplicates"] = stored_papers["duplicates"]
            stats["errors"] = stored_papers["errors"]

            # Step 3: Generate embeddings (if requested and papers were stored)
            if generate_embeddings and stats["stored"] > 0:
                self.log_info("Generating embeddings for new papers...")
                embedding_result = await self.embedding_service.embed_papers_batch(
                    papers[:stats["stored"]],
                    force_update=False
                )
                stats["embeddings_generated"] = embedding_result

            # Step 4: Extract concepts (if requested)
            if extract_concepts and stats["stored"] > 0:
                from app.services.concept_extraction_service import get_concept_extraction_service
                concept_service = get_concept_extraction_service()

                self.log_info("Extracting concepts from new papers...")
                concept_result = await concept_service.extract_concepts_batch(
                    papers[:stats["stored"]]
                )
                stats["concepts_extracted"] = concept_result["total_concepts"]

            self.log_info("Ingestion pipeline complete", stats=stats)
            return stats

        except Exception as e:
            self.log_error("Ingestion pipeline failed", error=e)
            stats["errors"] += 1
            raise

    async def _store_papers(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Store papers in database, handling duplicates

        Returns:
            Dict with stored, duplicates, errors counts
        """
        result = {
            "stored": 0,
            "duplicates": 0,
            "errors": 0
        }

        for paper in papers:
            try:
                # Check if paper already exists
                existing = await database.fetch_one(
                    text("SELECT id FROM papers WHERE id = :paper_id"),
                    {"paper_id": paper["id"]}
                )

                if existing:
                    result["duplicates"] += 1
                    self.log_debug(f"Paper {paper['id']} already exists, skipping")
                    continue

                # Insert new paper
                await database.execute(
                    text("""
                        INSERT INTO papers (
                            id, title, abstract, authors, published_date,
                            updated_date, category, ingested_at
                        ) VALUES (
                            :id, :title, :abstract, :authors, :published_date,
                            :updated_date, :category, CURRENT_TIMESTAMP
                        )
                    """),
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
                self.log_debug(f"Stored paper {paper['id']}: {paper['title'][:50]}...")

            except Exception as e:
                result["errors"] += 1
                self.log_error(f"Failed to store paper {paper.get('id', 'unknown')}", error=e)

        return result

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
            generate_embeddings=generate_embeddings
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
            result = await self._store_papers([paper])

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


def get_ingestion_service() -> IngestionService:
    """Get or create global ingestion service instance"""
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
