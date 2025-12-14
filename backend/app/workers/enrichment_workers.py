"""
Enrichment Workers - Concrete worker implementations

Three worker types based on rate limit domains:
1. LLMWorker - Gemini-based tasks (ai_analysis, concepts, techniques, benchmarks, deep_analysis)
2. ExternalAPIWorker - External API tasks (citations, github)
3. LocalWorker - Local processing tasks (embedding, relationships)
"""

import logging
import json
from typing import Optional, Dict, Any, List

from app.db.database import database
from app.workers.base_worker import BaseWorker, RateLimitError, update_processing_state
from app.services.pipeline.pipeline_service import JobType

logger = logging.getLogger(__name__)


class LLMWorker(BaseWorker):
    """
    Worker for Gemini LLM-based enrichment tasks.

    Handles: ai_analysis, concepts, techniques, benchmarks, deep_analysis
    """

    JOB_TYPES = [
        JobType.AI_ANALYSIS,
        JobType.CONCEPTS,
        JobType.TECHNIQUES,
        JobType.BENCHMARKS,
        JobType.DEEP_ANALYSIS,
    ]
    RATE_LIMIT_PROVIDER = "gemini"

    async def _process_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an LLM-based enrichment job."""
        job_type = job["job_type"]
        paper_id = job["paper_id"]

        # Get paper data
        paper = await self._get_paper(paper_id)
        if not paper:
            return {"error": f"Paper {paper_id} not found"}

        title = paper["title"]
        abstract = paper["abstract"] or ""

        result = None

        if job_type == JobType.AI_ANALYSIS:
            result = await self._enrich_ai_analysis(paper_id, title, abstract)
        elif job_type == JobType.CONCEPTS:
            result = await self._enrich_concepts(paper_id, title, abstract)
        elif job_type == JobType.TECHNIQUES:
            result = await self._enrich_techniques(paper_id, title, abstract)
        elif job_type == JobType.BENCHMARKS:
            result = await self._enrich_benchmarks(paper_id, title, abstract)
        elif job_type == JobType.DEEP_ANALYSIS:
            result = await self._enrich_deep_analysis(paper_id, paper)

        # Update processing state
        if result and not result.get("error"):
            await update_processing_state(paper_id, job_type, success=True)

        return result

    async def _get_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get paper data from database."""
        query = """
            SELECT id, title, abstract, published_date, code_repos
            FROM papers WHERE id = :paper_id
        """
        row = await database.fetch_one(query, {"paper_id": paper_id})
        return dict(row) if row else None

    async def _enrich_ai_analysis(
        self,
        paper_id: str,
        title: str,
        abstract: str
    ) -> Dict[str, Any]:
        """Generate AI analysis for a paper."""
        try:
            from app.services.ai_analysis_service import ai_analysis_service

            # Use generate_comprehensive_analysis which returns a dict
            analysis = await ai_analysis_service.generate_comprehensive_analysis(
                abstract=abstract,
                title=title
            )

            # Store in papers table as JSON
            query = """
                UPDATE papers
                SET ai_analysis = :analysis
                WHERE id = :paper_id
            """
            await database.execute(query, {
                "paper_id": paper_id,
                "analysis": json.dumps(analysis) if analysis else None
            })

            return {"success": True, "analysis_keys": len(analysis) if analysis else 0}

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                raise RateLimitError(str(e), backoff_seconds=60)
            raise

    async def _enrich_concepts(
        self,
        paper_id: str,
        title: str,
        abstract: str
    ) -> Dict[str, Any]:
        """Extract concepts from a paper."""
        try:
            from app.services.concept_extraction_service import get_concept_extraction_service

            service = get_concept_extraction_service()
            # extract_concepts_for_paper takes a paper dict with 'id', 'title', 'summary'
            paper_dict = {"id": paper_id, "title": title, "summary": abstract}
            concepts = await service.extract_concepts_for_paper(paper_dict)

            return {"success": True, "concepts_extracted": len(concepts) if concepts else 0}

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                raise RateLimitError(str(e), backoff_seconds=60)
            raise

    async def _enrich_techniques(
        self,
        paper_id: str,
        title: str,
        abstract: str
    ) -> Dict[str, Any]:
        """Extract techniques from a paper."""
        try:
            from app.services.technique_extraction_service import get_technique_extraction_service

            service = get_technique_extraction_service()
            # extract_techniques returns a TechniqueExtractionResult with .techniques list
            result = await service.extract_techniques(paper_id, title, abstract)
            techniques = result.techniques if result else []

            return {"success": True, "techniques_extracted": len(techniques)}

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                raise RateLimitError(str(e), backoff_seconds=60)
            raise

    async def _enrich_benchmarks(
        self,
        paper_id: str,
        title: str,
        abstract: str
    ) -> Dict[str, Any]:
        """Extract benchmark results from a paper.

        Note: Benchmark extraction is handled by batch scripts (extract_benchmarks_robust.py)
        which use Gemini to parse full paper PDFs. Skipping for now in pipeline workers.
        """
        # Benchmark extraction requires PDF parsing which is done by batch scripts
        # For pipeline workers, skip this stage and let batch scripts handle it
        return {"success": True, "skipped": True, "reason": "Benchmarks extracted via batch scripts"}

    async def _enrich_deep_analysis(
        self,
        paper_id: str,
        paper: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate deep analysis for a paper."""
        try:
            from app.services.deep_enrichment_service import get_deep_enrichment_service

            service = get_deep_enrichment_service()
            result = await service.enrich_single_paper(paper_id)

            return {"success": True, "has_deep_analysis": result is not None}

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                raise RateLimitError(str(e), backoff_seconds=60)
            raise


class ExternalAPIWorker(BaseWorker):
    """
    Worker for external API-based enrichment tasks.

    Handles: citations, github
    """

    JOB_TYPES = [JobType.CITATIONS, JobType.GITHUB]
    RATE_LIMIT_PROVIDER = "semantic_scholar"  # Default - overridden per job

    async def _process_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an external API enrichment job."""
        job_type = job["job_type"]
        paper_id = job["paper_id"]

        result = None

        if job_type == JobType.CITATIONS:
            self.RATE_LIMIT_PROVIDER = "semantic_scholar"
            result = await self._enrich_citations(paper_id)
        elif job_type == JobType.GITHUB:
            self.RATE_LIMIT_PROVIDER = "github"
            result = await self._enrich_github(paper_id)

        # Update processing state
        if result and not result.get("error"):
            await update_processing_state(paper_id, job_type, success=True)

        return result

    async def _enrich_citations(self, paper_id: str) -> Dict[str, Any]:
        """Fetch citation data from Semantic Scholar."""
        try:
            from app.services.citation_enrichment_service import get_citation_enrichment_service

            service = get_citation_enrichment_service()
            result = await service.enrich_single_paper(paper_id)

            return {
                "success": True,
                "citation_count": result.get("citation_count") if result else None
            }

        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                raise RateLimitError(str(e), backoff_seconds=120)
            raise

    async def _enrich_github(self, paper_id: str) -> Dict[str, Any]:
        """Fetch GitHub signals for a paper."""
        try:
            # Get paper's code repos
            query = "SELECT code_repos FROM papers WHERE id = :paper_id"
            row = await database.fetch_one(query, {"paper_id": paper_id})

            if not row or not row["code_repos"]:
                return {"success": True, "skipped": True, "reason": "No code repos"}

            from app.services.github_enrichment_service import get_github_enrichment_service

            service = get_github_enrichment_service()
            result = await service.enrich_paper(paper_id, row["code_repos"])

            return {"success": True, "github_enriched": result is not None}

        except Exception as e:
            if "403" in str(e) or "rate limit" in str(e).lower():
                raise RateLimitError(str(e), backoff_seconds=300)  # GitHub has hourly limit
            raise


class LocalWorker(BaseWorker):
    """
    Worker for local (no rate limit) enrichment tasks.

    Handles: embedding, relationships
    """

    JOB_TYPES = [JobType.EMBEDDING, JobType.RELATIONSHIPS]
    RATE_LIMIT_PROVIDER = "local"

    async def _process_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a local enrichment job."""
        job_type = job["job_type"]
        paper_id = job["paper_id"]

        result = None

        if job_type == JobType.EMBEDDING:
            result = await self._enrich_embedding(paper_id)
        elif job_type == JobType.RELATIONSHIPS:
            result = await self._enrich_relationships(paper_id)

        # Update processing state
        if result and not result.get("error"):
            await update_processing_state(paper_id, job_type, success=True)

        return result

    async def _enrich_embedding(self, paper_id: str) -> Dict[str, Any]:
        """Generate embedding for a paper."""
        try:
            # Check if embedding already exists in the papers table
            query = "SELECT id FROM papers WHERE id = :paper_id AND embedding IS NOT NULL LIMIT 1"
            existing = await database.fetch_one(query, {"paper_id": paper_id})

            if existing:
                return {"success": True, "skipped": True, "reason": "Embedding exists"}

            # Check if OPENAI_API_KEY is available before importing
            from app.core.config import settings
            if not settings.OPENAI_API_KEY:
                # Most papers already have Nomic embeddings from batch scripts
                # Skip gracefully if no OpenAI key is available
                return {"success": True, "skipped": True, "reason": "No OPENAI_API_KEY - use batch scripts for embeddings"}

            from app.services.embedding_service import get_embedding_service

            service = get_embedding_service()
            result = await service.embed_paper(paper_id)

            return {"success": True, "embedding_generated": result is not None}

        except Exception as e:
            raise

    async def _enrich_relationships(self, paper_id: str) -> Dict[str, Any]:
        """Build relationships for a paper based on embedding similarity."""
        try:
            # Check if paper has embedding in the papers table
            query = "SELECT embedding FROM papers WHERE id = :paper_id AND embedding IS NOT NULL LIMIT 1"
            embedding_row = await database.fetch_one(query, {"paper_id": paper_id})

            if not embedding_row:
                return {"success": False, "error": "No embedding found"}

            from app.services.relationship_service import get_relationship_service

            service = get_relationship_service()
            relationships = await service.build_relationships(paper_id)

            return {
                "success": True,
                "relationships_built": len(relationships) if relationships else 0
            }

        except Exception as e:
            raise


class CitationBatchWorker(BaseWorker):
    """
    Specialized worker for batch citation fetching.

    Uses Semantic Scholar's batch API which allows 500 papers per request.
    Much more efficient than single-paper requests.
    """

    JOB_TYPES = [JobType.CITATIONS]  # Only handles batch citation jobs
    RATE_LIMIT_PROVIDER = "semantic_scholar"
    BATCH_SIZE = 500

    async def _process_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a batch citation job."""
        # This worker overrides to fetch multiple papers at once
        # Job metadata should contain list of paper_ids to batch
        metadata = job.get("metadata", {})
        paper_ids = metadata.get("paper_ids", [job["paper_id"]])

        try:
            from app.services.citation_enrichment_service import get_citation_enrichment_service

            service = get_citation_enrichment_service()
            results = await service.enrich_papers_batch(paper_ids[:self.BATCH_SIZE])

            # Update processing state for each paper
            for paper_id in paper_ids[:self.BATCH_SIZE]:
                await update_processing_state(paper_id, JobType.CITATIONS, success=True)

            return {
                "success": True,
                "papers_processed": len(paper_ids[:self.BATCH_SIZE]),
                "results": results
            }

        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                raise RateLimitError(str(e), backoff_seconds=120)
            raise
