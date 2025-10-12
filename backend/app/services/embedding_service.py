"""
Embedding service for generating and managing vector embeddings

Uses OpenAI text-embedding-3-small (1536 dimensions) for:
- Paper semantic search
- Concept similarity
- Related paper discovery
"""
import asyncio
import hashlib
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import openai
from sqlalchemy import text

from app.db.database import database
from app.core.config import settings


class EmbeddingService:
    """Service for generating and caching embeddings"""

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"
        self.dimensions = 1536
        self.max_batch_size = 100  # OpenAI limit
        self.cache: Dict[str, List[float]] = {}

    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key from text hash"""
        return hashlib.md5(text.encode()).hexdigest()

    async def generate_embedding(
        self,
        text: str,
        use_cache: bool = True
    ) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed
            use_cache: Whether to use in-memory cache

        Returns:
            1536-dimensional embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.dimensions

        # Check cache
        if use_cache:
            cache_key = self._generate_cache_key(text)
            if cache_key in self.cache:
                return self.cache[cache_key]

        try:
            # Generate embedding via OpenAI
            response = await self.client.embeddings.create(
                model=self.model,
                input=text[:8000],  # Truncate to token limit
                encoding_format="float"
            )

            embedding = response.data[0].embedding

            # Cache result
            if use_cache:
                self.cache[cache_key] = embedding

            return embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector on error
            return [0.0] * self.dimensions

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        use_cache: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient)

        Args:
            texts: List of texts to embed
            use_cache: Whether to use in-memory cache

        Returns:
            List of 1536-dimensional embedding vectors
        """
        if not texts:
            return []

        # Filter out empty texts and track indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)

        if not valid_texts:
            return [[0.0] * self.dimensions] * len(texts)

        embeddings = [None] * len(texts)

        # Check cache first
        uncached_texts = []
        uncached_indices = []
        for i, text in zip(valid_indices, valid_texts):
            cache_key = self._generate_cache_key(text)
            if use_cache and cache_key in self.cache:
                embeddings[i] = self.cache[cache_key]
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Generate embeddings for uncached texts in batches
        for batch_start in range(0, len(uncached_texts), self.max_batch_size):
            batch_end = min(batch_start + self.max_batch_size, len(uncached_texts))
            batch_texts = uncached_texts[batch_start:batch_end]
            batch_indices = uncached_indices[batch_start:batch_end]

            try:
                # Truncate texts to token limit
                truncated_texts = [text[:8000] for text in batch_texts]

                response = await self.client.embeddings.create(
                    model=self.model,
                    input=truncated_texts,
                    encoding_format="float"
                )

                # Store results
                for i, data in enumerate(response.data):
                    embedding = data.embedding
                    original_index = batch_indices[i]
                    embeddings[original_index] = embedding

                    # Cache result
                    if use_cache:
                        cache_key = self._generate_cache_key(batch_texts[i])
                        self.cache[cache_key] = embedding

            except Exception as e:
                print(f"Error generating batch embeddings: {e}")
                # Fill with zero vectors
                for i in batch_indices:
                    if embeddings[i] is None:
                        embeddings[i] = [0.0] * self.dimensions

        # Fill any remaining None values with zero vectors
        for i in range(len(embeddings)):
            if embeddings[i] is None:
                embeddings[i] = [0.0] * self.dimensions

        return embeddings

    async def embed_paper(
        self,
        paper_id: str,
        title: str,
        abstract: str,
        force_update: bool = False
    ) -> bool:
        """
        Generate and store embedding for a paper

        Args:
            paper_id: arXiv ID
            title: Paper title
            abstract: Paper abstract
            force_update: Whether to regenerate if embedding exists

        Returns:
            True if successful
        """
        try:
            # Check if embedding already exists
            if not force_update:
                result = await database.fetch_one(
                    text("SELECT embedding FROM papers WHERE id = :paper_id"),
                    {"paper_id": paper_id}
                )
                if result and result["embedding"] is not None:
                    return True  # Already has embedding

            # Combine title and abstract for richer embedding
            combined_text = f"{title}\n\n{abstract}"

            # Generate embedding
            embedding = await self.generate_embedding(combined_text)

            # Store in database
            await database.execute(
                text("""
                    UPDATE papers
                    SET embedding = :embedding::vector,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :paper_id
                """),
                {
                    "paper_id": paper_id,
                    "embedding": str(embedding)
                }
            )

            return True

        except Exception as e:
            print(f"Error embedding paper {paper_id}: {e}")
            return False

    async def embed_papers_batch(
        self,
        papers: List[Dict[str, Any]],
        force_update: bool = False
    ) -> int:
        """
        Generate and store embeddings for multiple papers

        Args:
            papers: List of paper dicts with 'id', 'title', 'abstract'
            force_update: Whether to regenerate existing embeddings

        Returns:
            Number of papers successfully embedded
        """
        if not papers:
            return 0

        # Filter papers that need embeddings
        papers_to_embed = []
        if not force_update:
            for paper in papers:
                result = await database.fetch_one(
                    text("SELECT embedding FROM papers WHERE id = :paper_id"),
                    {"paper_id": paper["id"]}
                )
                if not result or result["embedding"] is None:
                    papers_to_embed.append(paper)
        else:
            papers_to_embed = papers

        if not papers_to_embed:
            return 0  # All papers already have embeddings

        print(f"Generating embeddings for {len(papers_to_embed)} papers...")

        # Combine title and abstract for each paper
        texts = [
            f"{paper['title']}\n\n{paper['abstract']}"
            for paper in papers_to_embed
        ]

        # Generate embeddings in batch
        embeddings = await self.generate_embeddings_batch(texts)

        # Store in database
        success_count = 0
        for paper, embedding in zip(papers_to_embed, embeddings):
            try:
                await database.execute(
                    text("""
                        UPDATE papers
                        SET embedding = :embedding::vector,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :paper_id
                    """),
                    {
                        "paper_id": paper["id"],
                        "embedding": str(embedding)
                    }
                )
                success_count += 1
            except Exception as e:
                print(f"Error storing embedding for {paper['id']}: {e}")

        print(f"Successfully embedded {success_count}/{len(papers_to_embed)} papers")
        return success_count

    async def embed_concept(
        self,
        concept_id: int,
        concept_name: str,
        concept_description: Optional[str] = None
    ) -> bool:
        """
        Generate and store embedding for a concept

        Args:
            concept_id: Concept database ID
            concept_name: Concept name
            concept_description: Optional description for richer embedding

        Returns:
            True if successful
        """
        try:
            # Use description if available, otherwise just name
            text = concept_description if concept_description else concept_name

            # Generate embedding
            embedding = await self.generate_embedding(text)

            # Store in database
            await database.execute(
                text("""
                    UPDATE concepts
                    SET embedding = :embedding::vector
                    WHERE id = :concept_id
                """),
                {
                    "concept_id": concept_id,
                    "embedding": str(embedding)
                }
            )

            return True

        except Exception as e:
            print(f"Error embedding concept {concept_id}: {e}")
            return False

    async def backfill_embeddings(
        self,
        batch_size: int = 100,
        max_papers: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Backfill embeddings for papers that don't have them

        Args:
            batch_size: Number of papers to process per batch
            max_papers: Maximum papers to process (None = all)

        Returns:
            Dict with 'total', 'success', 'failed' counts
        """
        print("Starting embedding backfill...")

        # Get papers without embeddings
        query = """
            SELECT id, title, abstract
            FROM papers
            WHERE embedding IS NULL
            ORDER BY published_date DESC
        """
        if max_papers:
            query += f" LIMIT {max_papers}"

        papers_to_embed = await database.fetch_all(text(query))

        if not papers_to_embed:
            print("All papers already have embeddings!")
            return {"total": 0, "success": 0, "failed": 0}

        total = len(papers_to_embed)
        print(f"Found {total} papers without embeddings")

        success_count = 0
        failed_count = 0

        # Process in batches
        for i in range(0, total, batch_size):
            batch = papers_to_embed[i:i + batch_size]
            batch_papers = [dict(p) for p in batch]

            print(f"Processing batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}...")

            success = await self.embed_papers_batch(batch_papers)
            success_count += success
            failed_count += len(batch) - success

            # Rate limiting: small delay between batches
            await asyncio.sleep(0.5)

        print(f"Backfill complete: {success_count} success, {failed_count} failed")

        return {
            "total": total,
            "success": success_count,
            "failed": failed_count
        }

    async def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get statistics about embeddings in database

        Returns:
            Dict with counts and coverage percentage
        """
        result = await database.fetch_one(
            text("""
                SELECT
                    COUNT(*) as total_papers,
                    COUNT(embedding) as papers_with_embedding,
                    ROUND(100.0 * COUNT(embedding) / COUNT(*), 2) as coverage_percentage
                FROM papers
            """)
        )

        concept_result = await database.fetch_one(
            text("""
                SELECT
                    COUNT(*) as total_concepts,
                    COUNT(embedding) as concepts_with_embedding
                FROM concepts
            """)
        )

        return {
            "papers": {
                "total": result["total_papers"],
                "with_embedding": result["papers_with_embedding"],
                "coverage_percentage": float(result["coverage_percentage"])
            },
            "concepts": {
                "total": concept_result["total_concepts"],
                "with_embedding": concept_result["concepts_with_embedding"]
            }
        }


# Global instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


# Convenience functions
async def embed_paper(paper_id: str, title: str, abstract: str) -> bool:
    """Embed a single paper"""
    service = get_embedding_service()
    return await service.embed_paper(paper_id, title, abstract)


async def backfill_embeddings(batch_size: int = 100, max_papers: Optional[int] = None):
    """Backfill embeddings for papers without them"""
    service = get_embedding_service()
    return await service.backfill_embeddings(batch_size, max_papers)


async def get_embedding_stats():
    """Get embedding coverage statistics"""
    service = get_embedding_service()
    return await service.get_embedding_stats()
