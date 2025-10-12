"""
Concept extraction service using AI to identify research concepts

Extracts concepts from papers and populates the knowledge graph:
- Identifies key techniques, architectures, datasets, tasks
- Assigns relevance scores
- Builds concept relationships
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from sqlalchemy import text
import google.generativeai as genai

from app.db.database import database
from app.core.config import settings
from app.utils.logger import LoggerMixin


class ConceptExtractionService(LoggerMixin):
    """Service for extracting concepts from research papers"""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.log_info("Concept extraction service initialized")

    async def extract_concepts_for_paper(
        self,
        paper: Dict[str, Any],
        max_concepts: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract concepts from a single paper

        Args:
            paper: Paper dict with 'id', 'title', 'summary'
            max_concepts: Maximum concepts to extract

        Returns:
            List of extracted concepts with relevance scores
        """
        self.log_info(f"Extracting concepts for paper: {paper['id']}")

        try:
            # Generate concepts using Gemini
            concepts = await self._generate_concepts(
                title=paper["title"],
                abstract=paper["summary"],
                max_concepts=max_concepts
            )

            if not concepts:
                self.log_warning(f"No concepts extracted for paper {paper['id']}")
                return []

            # Store concepts in database
            await self._store_concepts(paper["id"], concepts)

            self.log_info(f"Extracted {len(concepts)} concepts for paper {paper['id']}")
            return concepts

        except Exception as e:
            self.log_error(f"Concept extraction failed for {paper['id']}", error=e)
            return []

    async def _generate_concepts(
        self,
        title: str,
        abstract: str,
        max_concepts: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Use Gemini to extract concepts from paper

        Returns:
            List of concepts with name, category, relevance
        """
        prompt = f"""
Analyze this research paper and extract the key concepts, techniques, and contributions.

Title: {title}
Abstract: {abstract}

Extract up to {max_concepts} concepts and categorize them. For each concept, provide:
1. name - The concept name (e.g., "Transformer", "Attention Mechanism", "BERT")
2. category - Type of concept (choose from: architecture, technique, dataset, task, metric, application)
3. relevance - How central is this concept to the paper? (0.0 to 1.0, where 1.0 is core contribution)

Return ONLY a valid JSON array of objects with these fields. Example format:
[
  {{"name": "Transformer Architecture", "category": "architecture", "relevance": 1.0}},
  {{"name": "Self-Attention", "category": "technique", "relevance": 0.9}},
  {{"name": "Machine Translation", "category": "task", "relevance": 0.8}}
]

Return ONLY the JSON array, no other text.
"""

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)

            if not response.text:
                return []

            # Parse JSON response
            text = response.text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            concepts = json.loads(text)

            # Validate and normalize concepts
            valid_concepts = []
            for concept in concepts:
                if isinstance(concept, dict) and "name" in concept:
                    valid_concepts.append({
                        "name": concept["name"].strip(),
                        "category": concept.get("category", "technique"),
                        "relevance": float(concept.get("relevance", 0.5))
                    })

            return valid_concepts[:max_concepts]

        except json.JSONDecodeError as e:
            self.log_error("Failed to parse concept JSON", error=e, response=response.text[:200])
            # Fallback: extract simple concepts from title
            return self._extract_simple_concepts(title, abstract)
        except Exception as e:
            self.log_error("Concept generation failed", error=e)
            return []

    def _extract_simple_concepts(self, title: str, abstract: str) -> List[Dict[str, Any]]:
        """
        Fallback: Extract simple concepts using keyword matching

        Returns basic concepts if AI extraction fails
        """
        # Common AI/ML concepts to look for
        concept_keywords = {
            "transformer": "architecture",
            "attention": "technique",
            "bert": "architecture",
            "gpt": "architecture",
            "neural network": "architecture",
            "deep learning": "technique",
            "machine learning": "technique",
            "reinforcement learning": "technique",
            "supervised learning": "technique",
            "unsupervised learning": "technique",
            "classification": "task",
            "regression": "task",
            "generation": "task",
            "translation": "task",
            "imagenet": "dataset",
            "coco": "dataset",
            "accuracy": "metric",
            "f1 score": "metric"
        }

        text_lower = (title + " " + abstract).lower()
        concepts = []

        for keyword, category in concept_keywords.items():
            if keyword in text_lower:
                concepts.append({
                    "name": keyword.title(),
                    "category": category,
                    "relevance": 0.6  # Medium relevance for keyword matches
                })

        return concepts[:5]  # Return top 5 matches

    async def _store_concepts(
        self,
        paper_id: str,
        concepts: List[Dict[str, Any]]
    ) -> None:
        """
        Store concepts and their relationships in database

        Creates concept entries and paper_concepts relationships
        """
        if not database.is_connected:
            await database.connect()

        for concept_data in concepts:
            try:
                concept_name = concept_data["name"]
                normalized_name = concept_name.lower().strip()
                category = concept_data.get("category", "technique")
                relevance = concept_data.get("relevance", 0.5)

                # Insert or get concept
                # First, check if concept exists
                existing_concept = await database.fetch_one(
                    text("SELECT id FROM concepts WHERE normalized_name = :name"),
                    {"name": normalized_name}
                )

                if existing_concept:
                    concept_id = existing_concept["id"]
                else:
                    # Insert new concept
                    result = await database.fetch_one(
                        text("""
                            INSERT INTO concepts (name, normalized_name, category, first_seen_date)
                            VALUES (:name, :normalized_name, :category, CURRENT_TIMESTAMP)
                            RETURNING id
                        """),
                        {
                            "name": concept_name,
                            "normalized_name": normalized_name,
                            "category": category
                        }
                    )
                    concept_id = result["id"]

                # Insert paper-concept relationship
                await database.execute(
                    text("""
                        INSERT INTO paper_concepts (paper_id, concept_id, relevance, extraction_method)
                        VALUES (:paper_id, :concept_id, :relevance, 'ai_extraction')
                        ON CONFLICT (paper_id, concept_id) DO UPDATE
                        SET relevance = EXCLUDED.relevance
                    """),
                    {
                        "paper_id": paper_id,
                        "concept_id": concept_id,
                        "relevance": relevance
                    }
                )

                # Update paper's concepts_array for full-text search
                await database.execute(
                    text("""
                        UPDATE papers
                        SET concepts_array = ARRAY(
                            SELECT c.name
                            FROM paper_concepts pc
                            JOIN concepts c ON pc.concept_id = c.id
                            WHERE pc.paper_id = :paper_id
                        )
                        WHERE id = :paper_id
                    """),
                    {"paper_id": paper_id}
                )

            except Exception as e:
                self.log_error(f"Failed to store concept: {concept_name}", error=e)

    async def extract_concepts_batch(
        self,
        papers: List[Dict[str, Any]],
        max_concepts_per_paper: int = 10,
        batch_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Extract concepts for multiple papers

        Args:
            papers: List of paper dicts
            max_concepts_per_paper: Max concepts per paper
            batch_delay: Delay between papers (rate limiting)

        Returns:
            Stats dict
        """
        self.log_info(f"Extracting concepts for {len(papers)} papers")

        stats = {
            "papers_processed": 0,
            "total_concepts": 0,
            "failed": 0
        }

        for paper in papers:
            try:
                concepts = await self.extract_concepts_for_paper(
                    paper,
                    max_concepts=max_concepts_per_paper
                )

                stats["papers_processed"] += 1
                stats["total_concepts"] += len(concepts)

                # Rate limiting
                await asyncio.sleep(batch_delay)

            except Exception as e:
                stats["failed"] += 1
                self.log_error(f"Failed to process paper {paper.get('id')}", error=e)

        self.log_info("Batch concept extraction complete", stats=stats)
        return stats

    async def get_concept_stats(self) -> Dict[str, Any]:
        """
        Get statistics about concepts in database

        Returns:
            Stats about concepts and coverage
        """
        if not database.is_connected:
            await database.connect()

        # Total concepts
        total = await database.fetch_one(
            text("SELECT COUNT(*) as count FROM concepts")
        )

        # Concepts by category
        by_category = await database.fetch_all(
            text("""
                SELECT category, COUNT(*) as count
                FROM concepts
                GROUP BY category
                ORDER BY count DESC
            """)
        )

        # Top concepts by paper count
        top_concepts = await database.fetch_all(
            text("""
                SELECT name, category, paper_count
                FROM concepts
                ORDER BY paper_count DESC
                LIMIT 20
            """)
        )

        # Papers with concepts
        papers_with_concepts = await database.fetch_one(
            text("""
                SELECT COUNT(DISTINCT paper_id) as count
                FROM paper_concepts
            """)
        )

        return {
            "total_concepts": total["count"],
            "by_category": [dict(r) for r in by_category],
            "top_concepts": [dict(r) for r in top_concepts],
            "papers_with_concepts": papers_with_concepts["count"]
        }

    async def backfill_concepts(
        self,
        max_papers: Optional[int] = None,
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Backfill concepts for papers that don't have them

        Args:
            max_papers: Maximum papers to process (None = all)
            batch_size: Papers to process per batch

        Returns:
            Stats dict
        """
        self.log_info("Starting concept backfill")

        if not database.is_connected:
            await database.connect()

        # Get papers without concepts
        query = """
            SELECT p.id, p.title, p.abstract as summary
            FROM papers p
            LEFT JOIN paper_concepts pc ON p.id = pc.paper_id
            WHERE pc.paper_id IS NULL
            ORDER BY p.published_date DESC
        """

        if max_papers:
            query += f" LIMIT {max_papers}"

        papers = await database.fetch_all(text(query))

        if not papers:
            self.log_info("No papers need concept extraction")
            return {"papers_processed": 0, "total_concepts": 0, "failed": 0}

        self.log_info(f"Found {len(papers)} papers without concepts")

        # Process in batches
        papers_list = [dict(p) for p in papers]
        return await self.extract_concepts_batch(
            papers_list,
            max_concepts_per_paper=10,
            batch_delay=1.0
        )


# Global instance
_concept_extraction_service: Optional[ConceptExtractionService] = None


def get_concept_extraction_service() -> ConceptExtractionService:
    """Get or create global concept extraction service instance"""
    global _concept_extraction_service
    if _concept_extraction_service is None:
        _concept_extraction_service = ConceptExtractionService()
    return _concept_extraction_service
