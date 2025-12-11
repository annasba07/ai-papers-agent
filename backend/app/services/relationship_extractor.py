"""
Paper Relationship Extractor

Extracts typed semantic relationships between papers using LLM analysis.
Relationships include: improves, extends, contradicts, applies, simplifies,
explains, implements, surveys, replicates, criticizes.

This creates the knowledge graph edges that enable queries like:
- "What papers built on this work?"
- "What approaches contradict this finding?"
- "Show me the lineage of this technique"
"""
import asyncio
import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel

import google.generativeai as genai

from app.utils.logger import LoggerMixin

MODEL_NAME = "gemini-2.5-flash-lite"


class ExtractedRelationship(BaseModel):
    """A single extracted relationship"""
    target_paper_id: str
    target_paper_title: str
    relationship_type: str
    description: str
    evidence_section: Optional[str] = None
    evidence_snippet: Optional[str] = None
    confidence: float = 0.8


class RelationshipExtractionResult(BaseModel):
    """Result of relationship extraction for a paper"""
    source_paper_id: str
    relationships: List[ExtractedRelationship]
    extraction_time: float
    error: Optional[str] = None


# Valid relationship types
RELATIONSHIP_TYPES = [
    "improves",      # Paper B achieves better results than Paper A
    "extends",       # Paper B extends the method/theory from Paper A
    "builds_on",     # Paper B uses Paper A as foundation
    "contradicts",   # Paper B's findings contradict Paper A
    "applies",       # Paper B applies Paper A's method to new domain/task
    "simplifies",    # Paper B achieves similar results with simpler approach
    "explains",      # Paper B provides theoretical justification for Paper A
    "implements",    # Paper B provides implementation of Paper A
    "surveys",       # Paper B surveys/reviews Paper A
    "replicates",    # Paper B attempts to replicate Paper A
    "criticizes",    # Paper B critiques methodology/claims of Paper A
    "compares_to",   # Paper B uses Paper A as baseline/comparison
]


EXTRACTION_PROMPT = """Analyze the following paper and extract meaningful relationships to other papers it references.

**Source Paper:**
Title: {title}
Abstract: {abstract}

**Key sections from paper (if available):**
{related_work_section}

**Task:**
Identify papers that this work has MEANINGFUL relationships with. Focus on:
1. Papers this work directly IMPROVES upon (better results, enhanced method)
2. Papers this work EXTENDS (builds on their method/theory)
3. Papers this work CONTRADICTS (different findings)
4. Papers whose methods this work APPLIES to new domains
5. Papers this work SIMPLIFIES (achieves similar results more efficiently)
6. Papers this work provides EXPLANATION for (theoretical justification)

**Output Format (JSON array):**
```json
[
  {{
    "target_paper_title": "Exact title of the referenced paper",
    "relationship_type": "one of: improves, extends, builds_on, contradicts, applies, simplifies, explains, implements, compares_to",
    "description": "Brief description of HOW this relationship manifests (e.g., 'Improves accuracy by 3% by using modified attention mechanism')",
    "evidence_snippet": "Quote from the paper that supports this relationship",
    "confidence": 0.9
  }}
]
```

**Rules:**
1. Only extract CLEAR, MEANINGFUL relationships (not just "cites")
2. The description should explain WHAT the improvement/extension/etc. is
3. Include only relationships you're confident about (confidence > 0.6)
4. Maximum 10 relationships per paper
5. Focus on the MOST IMPORTANT relationships

**Output only valid JSON array, no other text:**
"""


class RelationshipExtractor(LoggerMixin):
    """
    Extracts typed semantic relationships between papers.

    Uses LLM to analyze paper content and identify meaningful
    relationships like "improves", "contradicts", "applies", etc.
    """

    def __init__(self):
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the Gemini model."""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.log_warning("No Gemini API key found, relationship extraction disabled")
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(MODEL_NAME)
            self.log_info(f"Initialized Gemini model for relationship extraction: {MODEL_NAME}")
        except Exception as e:
            self.log_error("Failed to initialize Gemini model", error=e)
            self.model = None

    async def _generate(self, prompt: str) -> str:
        """Generate response from LLM."""
        if not self.model:
            raise ValueError("Model not initialized - missing API key")

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt)
        )
        return response.text

    async def extract_relationships(
        self,
        paper: Dict[str, Any],
        related_work_text: Optional[str] = None
    ) -> RelationshipExtractionResult:
        """
        Extract relationships for a single paper.

        Args:
            paper: Paper dict with id, title, abstract, and optionally full text
            related_work_text: Optional related work section text

        Returns:
            RelationshipExtractionResult with extracted relationships
        """
        start_time = datetime.now()
        paper_id = paper.get("id", "unknown")

        try:
            # Build prompt
            prompt = EXTRACTION_PROMPT.format(
                title=paper.get("title", ""),
                abstract=paper.get("abstract", ""),
                related_work_section=related_work_text or "Not available"
            )

            # Call LLM
            response = await self._generate(prompt)

            # Parse response
            relationships = self._parse_response(response, paper_id)

            elapsed = (datetime.now() - start_time).total_seconds()

            return RelationshipExtractionResult(
                source_paper_id=paper_id,
                relationships=relationships,
                extraction_time=elapsed
            )

        except Exception as e:
            self.log_error(f"Relationship extraction failed for {paper_id}", error=e)
            elapsed = (datetime.now() - start_time).total_seconds()
            return RelationshipExtractionResult(
                source_paper_id=paper_id,
                relationships=[],
                extraction_time=elapsed,
                error=str(e)
            )

    def _parse_response(
        self,
        response: str,
        source_paper_id: str
    ) -> List[ExtractedRelationship]:
        """Parse LLM response into structured relationships"""
        relationships = []

        try:
            # Extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', response)
            if not json_match:
                self.log_warning(f"No JSON array found in response for {source_paper_id}")
                return []

            data = json.loads(json_match.group())

            for item in data:
                # Validate relationship type
                rel_type = item.get("relationship_type", "").lower()
                if rel_type not in RELATIONSHIP_TYPES:
                    rel_type = "builds_on"  # Default

                # Create relationship
                rel = ExtractedRelationship(
                    target_paper_id="",  # Will be resolved later
                    target_paper_title=item.get("target_paper_title", ""),
                    relationship_type=rel_type,
                    description=item.get("description", ""),
                    evidence_snippet=item.get("evidence_snippet"),
                    confidence=min(1.0, max(0.0, item.get("confidence", 0.8)))
                )

                if rel.target_paper_title and rel.description:
                    relationships.append(rel)

        except json.JSONDecodeError as e:
            self.log_error(f"JSON parse error for {source_paper_id}", error=e)
        except Exception as e:
            self.log_error(f"Parse error for {source_paper_id}", error=e)

        return relationships[:10]  # Max 10 relationships

    async def resolve_paper_ids(
        self,
        relationships: List[ExtractedRelationship],
        db
    ) -> List[ExtractedRelationship]:
        """
        Resolve paper titles to IDs in our database.

        Uses fuzzy matching to find papers that match the extracted titles.
        """
        resolved = []

        for rel in relationships:
            if not rel.target_paper_title:
                continue

            # Try to find paper by title (fuzzy match)
            query = """
                SELECT id, title,
                       similarity(title, :search_title) as sim
                FROM papers
                WHERE similarity(title, :search_title) > 0.3
                ORDER BY sim DESC
                LIMIT 1
            """

            try:
                result = await db.fetch_one(
                    query,
                    {"search_title": rel.target_paper_title}
                )

                if result:
                    rel.target_paper_id = result["id"]
                    resolved.append(rel)
                else:
                    self.log_debug(
                        f"Could not resolve paper: {rel.target_paper_title[:50]}..."
                    )
            except Exception as e:
                self.log_warning(f"Error resolving paper title: {e}")

        return resolved

    async def save_relationships(
        self,
        source_paper_id: str,
        relationships: List[ExtractedRelationship],
        db
    ) -> int:
        """
        Save extracted relationships to database.

        Returns number of relationships saved.
        """
        saved = 0

        for rel in relationships:
            if not rel.target_paper_id:
                continue

            try:
                query = """
                    INSERT INTO paper_semantic_edges
                    (source_paper_id, target_paper_id, relationship_type,
                     description, evidence_snippet, confidence, extraction_method)
                    VALUES (:source, :target, :rel_type, :description,
                            :evidence, :confidence, 'llm')
                    ON CONFLICT (source_paper_id, target_paper_id, relationship_type)
                    DO UPDATE SET
                        description = EXCLUDED.description,
                        confidence = EXCLUDED.confidence,
                        extracted_at = NOW()
                """

                await db.execute(query, {
                    "source": source_paper_id,
                    "target": rel.target_paper_id,
                    "rel_type": rel.relationship_type,
                    "description": rel.description,
                    "evidence": rel.evidence_snippet,
                    "confidence": rel.confidence
                })

                saved += 1

            except Exception as e:
                self.log_error(f"Error saving relationship: {e}")

        return saved


class RelationshipService(LoggerMixin):
    """
    High-level service for managing paper relationships.
    """

    def __init__(self):
        self.extractor = RelationshipExtractor()

    async def get_paper_relationships(
        self,
        paper_id: str,
        db
    ) -> Dict[str, Any]:
        """
        Get all relationships for a paper (both directions).
        """
        query = """
            SELECT * FROM get_paper_relationships(:paper_id)
        """

        results = await db.fetch_all(query, {"paper_id": paper_id})

        outgoing = []
        incoming = []

        for row in results:
            rel = {
                "paper_id": row["related_paper_id"],
                "title": row["related_paper_title"],
                "relationship_type": row["relationship_type"],
                "description": row["description"],
                "confidence": row["confidence"]
            }

            if row["direction"] == "outgoing":
                outgoing.append(rel)
            else:
                incoming.append(rel)

        return {
            "paper_id": paper_id,
            "builds_on": outgoing,  # Papers this one builds on
            "built_upon_by": incoming  # Papers that build on this one
        }

    async def get_paper_lineage(
        self,
        paper_id: str,
        db,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Get the full lineage tree for a paper.

        Returns ancestors (what it builds on) and descendants (what builds on it).
        """
        # Get ancestors (papers this one builds on, recursively)
        ancestors_query = """
            WITH RECURSIVE lineage AS (
                -- Base case: direct relationships
                SELECT
                    target_paper_id as paper_id,
                    source_paper_id as child_id,
                    relationship_type,
                    description,
                    1 as depth
                FROM paper_semantic_edges
                WHERE source_paper_id = :paper_id
                AND relationship_type IN ('improves', 'extends', 'builds_on')

                UNION ALL

                -- Recursive case
                SELECT
                    pse.target_paper_id,
                    pse.source_paper_id,
                    pse.relationship_type,
                    pse.description,
                    l.depth + 1
                FROM paper_semantic_edges pse
                JOIN lineage l ON pse.source_paper_id = l.paper_id
                WHERE l.depth < :max_depth
                AND pse.relationship_type IN ('improves', 'extends', 'builds_on')
            )
            SELECT DISTINCT ON (l.paper_id)
                l.paper_id,
                l.relationship_type,
                l.description,
                l.depth,
                p.title,
                p.published_date,
                p.citation_count
            FROM lineage l
            JOIN papers p ON l.paper_id = p.id
            ORDER BY l.paper_id, l.depth
        """

        ancestors = await db.fetch_all(
            ancestors_query,
            {"paper_id": paper_id, "max_depth": max_depth}
        )

        # Get descendants (papers that build on this)
        descendants_query = """
            WITH RECURSIVE lineage AS (
                SELECT
                    source_paper_id as paper_id,
                    target_paper_id as parent_id,
                    relationship_type,
                    description,
                    1 as depth
                FROM paper_semantic_edges
                WHERE target_paper_id = :paper_id
                AND relationship_type IN ('improves', 'extends', 'builds_on')

                UNION ALL

                SELECT
                    pse.source_paper_id,
                    pse.target_paper_id,
                    pse.relationship_type,
                    pse.description,
                    l.depth + 1
                FROM paper_semantic_edges pse
                JOIN lineage l ON pse.target_paper_id = l.paper_id
                WHERE l.depth < :max_depth
                AND pse.relationship_type IN ('improves', 'extends', 'builds_on')
            )
            SELECT DISTINCT ON (l.paper_id)
                l.paper_id,
                l.relationship_type,
                l.description,
                l.depth,
                p.title,
                p.published_date,
                p.citation_count
            FROM lineage l
            JOIN papers p ON l.paper_id = p.id
            ORDER BY l.paper_id, l.depth
        """

        descendants = await db.fetch_all(
            descendants_query,
            {"paper_id": paper_id, "max_depth": max_depth}
        )

        return {
            "paper_id": paper_id,
            "ancestors": [
                {
                    "paper_id": r["paper_id"],
                    "title": r["title"],
                    "relationship": r["relationship_type"],
                    "description": r["description"],
                    "depth": r["depth"],
                    "published_date": r["published_date"].isoformat() if r["published_date"] else None,
                    "citation_count": r["citation_count"]
                }
                for r in ancestors
            ],
            "descendants": [
                {
                    "paper_id": r["paper_id"],
                    "title": r["title"],
                    "relationship": r["relationship_type"],
                    "description": r["description"],
                    "depth": r["depth"],
                    "published_date": r["published_date"].isoformat() if r["published_date"] else None,
                    "citation_count": r["citation_count"]
                }
                for r in descendants
            ]
        }

    async def extract_and_save(
        self,
        paper: Dict[str, Any],
        db,
        related_work_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract relationships for a paper and save to database.
        """
        # Extract
        result = await self.extractor.extract_relationships(paper, related_work_text)

        if result.error:
            return {
                "paper_id": paper.get("id"),
                "success": False,
                "error": result.error,
                "relationships_found": 0
            }

        # Resolve paper IDs
        resolved = await self.extractor.resolve_paper_ids(
            result.relationships,
            db
        )

        # Save
        saved = await self.extractor.save_relationships(
            paper.get("id"),
            resolved,
            db
        )

        return {
            "paper_id": paper.get("id"),
            "success": True,
            "relationships_found": len(result.relationships),
            "relationships_resolved": len(resolved),
            "relationships_saved": saved,
            "extraction_time": result.extraction_time
        }


# Singleton instance
_relationship_service = None

def get_relationship_service() -> RelationshipService:
    """Get singleton relationship service instance"""
    global _relationship_service
    if _relationship_service is None:
        _relationship_service = RelationshipService()
    return _relationship_service
