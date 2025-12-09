"""
Batch Enrichment Service

Enriches all papers with AI-generated analysis using Gemini 2.5 Flash Lite.
Extracts GitHub URLs from abstracts and populates code_repos.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv

from app.db.database import database
from app.utils.logger import LoggerMixin

load_dotenv()


# Model configuration
MODEL_NAME = "gemini-2.5-flash-lite"
BATCH_SIZE = 50  # Papers per batch
REQUESTS_PER_MINUTE = 1500  # Gemini rate limit for Flash Lite
DELAY_BETWEEN_BATCHES = 2.0  # Seconds between batches


# GitHub/GitLab URL extraction patterns
CODE_URL_PATTERNS = [
    r'github\.com/[\w\-\.]+/[\w\-\.]+',
    r'gitlab\.com/[\w\-\.]+/[\w\-\.]+',
    r'huggingface\.co/[\w\-\.]+/[\w\-\.]+',
    r'bitbucket\.org/[\w\-\.]+/[\w\-\.]+',
]


# Analysis prompt template
ANALYSIS_PROMPT = """Analyze this research paper and provide a structured analysis.

Title: {title}

Abstract: {abstract}

Provide your analysis as a JSON object with these exact fields:
{{
  "summary": "2-3 sentence concise summary of what the paper does",
  "novelty": "What's novel about this approach (1-2 sentences)",
  "technicalInnovation": "Key technical contribution (1-2 sentences)",
  "keyContribution": "Main contribution to the field (1 sentence)",
  "methodologyBreakdown": "How the methodology works (2-3 sentences)",
  "performanceHighlights": "Key performance results mentioned (1-2 sentences)",
  "implementationInsights": "Implementation complexity and requirements (1-2 sentences)",
  "researchContext": "What research area/field this belongs to (1 sentence)",
  "futureImplications": "Future impact and directions (1-2 sentences)",
  "limitations": "Current limitations mentioned or implied (1-2 sentences)",
  "impactScore": <integer 1-10, where 10 is groundbreaking>,
  "difficultyLevel": "<beginner|intermediate|advanced>",
  "readingTime": <estimated minutes to read and understand>,
  "hasCode": <true if code/implementation is mentioned, false otherwise>,
  "implementationComplexity": "<low|medium|high>",
  "practicalApplicability": "<low|medium|high>",
  "researchSignificance": "<incremental|significant|breakthrough>",
  "reproductionDifficulty": "<low|medium|high>"
}}

Respond ONLY with the JSON object, no other text."""


@dataclass
class EnrichmentStats:
    """Statistics for an enrichment run."""
    total_papers: int = 0
    processed: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    code_repos_found: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        elapsed = 0
        if self.start_time:
            end = self.end_time or time.time()
            elapsed = end - self.start_time
        return {
            "total_papers": self.total_papers,
            "processed": self.processed,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "skipped": self.skipped,
            "code_repos_found": self.code_repos_found,
            "elapsed_seconds": round(elapsed, 1),
            "papers_per_second": round(self.processed / elapsed, 2) if elapsed > 0 else 0,
            "success_rate": round(100 * self.succeeded / self.processed, 1) if self.processed > 0 else 0,
            "recent_errors": self.errors[-5:],
        }


class BatchEnrichmentService(LoggerMixin):
    """
    Service for batch enriching papers with AI analysis.

    Uses Gemini 2.5 Flash Lite for cost-efficient processing of large paper sets.
    """

    def __init__(self) -> None:
        self._model: Optional[genai.GenerativeModel] = None
        self._is_running = False
        self._should_stop = False
        self._current_stats: Optional[EnrichmentStats] = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the Gemini model."""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.log_warning("No Gemini API key found, enrichment disabled")
            return

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,  # Low temperature for consistent structured output
            ),
        )
        self.log_info(f"Initialized Gemini model: {MODEL_NAME}")

    @property
    def enabled(self) -> bool:
        return self._model is not None

    @property
    def is_running(self) -> bool:
        return self._is_running

    def get_status(self) -> Dict[str, Any]:
        """Get current enrichment status."""
        return {
            "enabled": self.enabled,
            "is_running": self._is_running,
            "model": MODEL_NAME,
            "stats": self._current_stats.to_dict() if self._current_stats else None,
        }

    def stop(self) -> None:
        """Signal the enrichment to stop after current batch."""
        self._should_stop = True
        self.log_info("Stop requested, will finish current batch")

    def extract_code_urls(self, text: str) -> List[str]:
        """Extract code repository URLs from text."""
        urls = []
        for pattern in CODE_URL_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                url = f"https://{match}"
                if url not in urls:
                    urls.append(url)
        return urls

    async def _analyze_paper(self, title: str, abstract: str) -> Optional[Dict[str, Any]]:
        """Generate AI analysis for a single paper."""
        if not self._model:
            return None

        prompt = ANALYSIS_PROMPT.format(title=title, abstract=abstract[:4000])

        try:
            response = await self._model.generate_content_async(prompt)
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError as e:
            self.log_warning(f"JSON parse error: {e}")
            return None
        except Exception as e:
            self.log_warning(f"Analysis error: {e}")
            return None

    async def _update_paper(
        self,
        paper_id: str,
        ai_analysis: Optional[Dict[str, Any]],
        code_repos: List[str],
    ) -> bool:
        """Update a paper in the database with enrichment data."""
        try:
            updates = []
            params = {"paper_id": paper_id}

            if ai_analysis:
                updates.append("ai_analysis = :ai_analysis")
                params["ai_analysis"] = json.dumps(ai_analysis)

            if code_repos:
                updates.append("code_repos = :code_repos")
                params["code_repos"] = json.dumps(code_repos)

            if not updates:
                return True

            updates.append("updated_at = :updated_at")
            params["updated_at"] = datetime.utcnow()

            query = f"UPDATE papers SET {', '.join(updates)} WHERE id = :paper_id"
            await database.execute(query, params)
            return True
        except Exception as e:
            self.log_warning(f"DB update failed for {paper_id}: {e}")
            return False

    async def enrich_batch(
        self,
        papers: List[Dict[str, Any]],
        stats: EnrichmentStats,
    ) -> None:
        """Enrich a batch of papers."""
        tasks = []
        for paper in papers:
            paper_id = paper["id"]
            title = paper["title"]
            abstract = paper["abstract"]

            # Extract code URLs from abstract
            code_repos = self.extract_code_urls(abstract)
            if code_repos:
                stats.code_repos_found += 1

            # Create analysis task
            async def process_paper(pid, t, a, repos):
                analysis = await self._analyze_paper(t, a)
                success = await self._update_paper(pid, analysis, repos)
                return success, analysis is not None

            tasks.append(process_paper(paper_id, title, abstract, code_repos))

        # Process batch concurrently (but respect rate limits)
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            stats.processed += 1
            if isinstance(result, Exception):
                stats.failed += 1
                stats.errors.append(str(result)[:100])
            elif result[0]:  # success
                if result[1]:  # had analysis
                    stats.succeeded += 1
                else:
                    stats.failed += 1
            else:
                stats.failed += 1

    async def run_enrichment(
        self,
        batch_size: int = BATCH_SIZE,
        max_papers: Optional[int] = None,
        skip_existing: bool = True,
    ) -> EnrichmentStats:
        """
        Run batch enrichment on all papers.

        Args:
            batch_size: Papers to process per batch
            max_papers: Maximum papers to process (None = all)
            skip_existing: Skip papers that already have ai_analysis

        Returns:
            EnrichmentStats with results
        """
        if not self.enabled:
            raise RuntimeError("Enrichment service not enabled (no API key)")

        if self._is_running:
            raise RuntimeError("Enrichment already running")

        self._is_running = True
        self._should_stop = False
        stats = EnrichmentStats(start_time=time.time())
        self._current_stats = stats

        try:
            # Count total papers to process
            if skip_existing:
                count_query = "SELECT COUNT(*) FROM papers WHERE ai_analysis IS NULL"
            else:
                count_query = "SELECT COUNT(*) FROM papers"

            result = await database.fetch_one(count_query)
            stats.total_papers = result[0] if result else 0

            if max_papers:
                stats.total_papers = min(stats.total_papers, max_papers)

            self.log_info(f"Starting enrichment of {stats.total_papers} papers")

            offset = 0
            while offset < stats.total_papers and not self._should_stop:
                # Fetch batch
                if skip_existing:
                    query = """
                        SELECT id, title, abstract
                        FROM papers
                        WHERE ai_analysis IS NULL
                        ORDER BY published_date DESC
                        LIMIT :limit OFFSET :offset
                    """
                else:
                    query = """
                        SELECT id, title, abstract
                        FROM papers
                        ORDER BY published_date DESC
                        LIMIT :limit OFFSET :offset
                    """

                papers = await database.fetch_all(
                    query, {"limit": batch_size, "offset": offset}
                )

                if not papers:
                    break

                papers_list = [dict(p) for p in papers]

                # Process batch
                await self.enrich_batch(papers_list, stats)

                offset += batch_size

                # Log progress
                pct = round(100 * stats.processed / stats.total_papers, 1)
                self.log_info(
                    f"Progress: {stats.processed}/{stats.total_papers} ({pct}%) "
                    f"- Success: {stats.succeeded}, Failed: {stats.failed}"
                )

                # Rate limit delay
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)

            stats.end_time = time.time()
            self.log_info(f"Enrichment complete: {stats.to_dict()}")
            return stats

        finally:
            self._is_running = False

    async def enrich_single_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Enrich a single paper by ID.

        Returns the analysis if successful, None otherwise.
        """
        if not self.enabled:
            return None

        # Fetch paper
        query = "SELECT id, title, abstract FROM papers WHERE id = :paper_id"
        paper = await database.fetch_one(query, {"paper_id": paper_id})

        if not paper:
            return None

        # Extract code URLs
        code_repos = self.extract_code_urls(paper["abstract"])

        # Generate analysis
        analysis = await self._analyze_paper(paper["title"], paper["abstract"])

        # Update database
        if analysis or code_repos:
            await self._update_paper(paper_id, analysis, code_repos)

        return analysis


# Module-level singleton
_enrichment_service: Optional[BatchEnrichmentService] = None


def get_enrichment_service() -> BatchEnrichmentService:
    """Get or create the enrichment service singleton."""
    global _enrichment_service
    if _enrichment_service is None:
        _enrichment_service = BatchEnrichmentService()
    return _enrichment_service
