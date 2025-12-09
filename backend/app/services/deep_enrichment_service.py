"""
Deep Enrichment Service (Tier 2)

Performs deep multimodal analysis of papers using full PDF content.
Uses Gemini Flash to analyze the main content (excluding appendix) including:
- Full methodology understanding
- Figure and table analysis
- Experimental results extraction
- Architecture diagram interpretation
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv

from app.db.database import database
from app.utils.logger import LoggerMixin

load_dotenv()

# Configuration
MODEL_NAME = "gemini-2.5-flash-lite"  # Cost-efficient model
PDF_DIR = Path("/Users/kaizen/Software-Projects/ai-papers-agent/data/papers_pdf")
MAX_PAGES = 15  # Skip appendix by limiting to main content
BATCH_SIZE = 100  # Larger batches for parallel processing
CONCURRENT_WORKERS = 50  # Optimal for this hardware - 100 workers showed diminishing returns
DELAY_BETWEEN_BATCHES = 2.0  # Small delay between batches


# Deep analysis prompt - much richer than abstract-only
DEEP_ANALYSIS_PROMPT = """Analyze this research paper PDF thoroughly. You have access to the full paper content including figures, tables, and methodology details.

Provide a comprehensive analysis as a JSON object with these fields:

{{
  "executive_summary": "3-4 sentence summary capturing the key contribution and results",

  "problem_statement": "What specific problem does this paper address? (2-3 sentences)",
  "proposed_solution": "How does the paper solve this problem? Key approach. (2-3 sentences)",

  "methodology": {{
    "approach": "Detailed description of the methodology (3-5 sentences)",
    "architecture": "Description of any model/system architecture if applicable",
    "key_components": ["List of 3-5 key technical components or innovations"],
    "training_details": "Training procedure, datasets, hyperparameters if mentioned"
  }},

  "experimental_results": {{
    "benchmarks": ["List of benchmarks/datasets used for evaluation"],
    "key_metrics": {{"metric_name": "value or comparison"}},
    "performance_summary": "2-3 sentence summary of main results",
    "comparisons": "How does it compare to baselines/prior work?"
  }},

  "figures_analysis": [
    {{
      "figure_id": "Figure 1",
      "description": "What this figure shows",
      "key_insight": "Main takeaway from this figure"
    }}
  ],

  "technical_depth": {{
    "mathematical_rigor": "<low|medium|high>",
    "implementation_detail": "<low|medium|high>",
    "reproducibility_score": <1-10>,
    "code_availability": "<yes|no|partial|unknown>"
  }},

  "novelty_assessment": {{
    "novelty_type": "<architectural|algorithmic|application|dataset|theoretical|empirical>",
    "novelty_description": "What's genuinely new here (2-3 sentences)",
    "prior_work_relation": "How it builds on or differs from prior work"
  }},

  "practical_implications": {{
    "use_cases": ["List of 2-4 practical applications"],
    "deployment_considerations": "What's needed to deploy this in practice",
    "scalability": "How well does this scale?",
    "limitations": ["List of 2-4 limitations mentioned or apparent"]
  }},

  "impact_assessment": {{
    "impact_score": <1-10, USE THE RUBRIC BELOW>,
    "impact_rationale": "1-2 sentence justification for the score based on the rubric criteria",
    "research_significance": "<incremental|moderate|significant|breakthrough>",
    "industry_relevance": "<low|medium|high>",
    "citation_potential": "<low|medium|high>"
  }},

  "reader_guidance": {{
    "difficulty_level": "<beginner|intermediate|advanced|expert>",
    "prerequisites": ["List of 2-4 prerequisite knowledge areas"],
    "reading_time_minutes": <estimated minutes>,
    "key_sections": ["Most important sections to read"]
  }},

  "extracted_artifacts": {{
    "github_urls": ["Any GitHub/code URLs found in the paper"],
    "datasets_mentioned": ["Datasets used or introduced"],
    "models_mentioned": ["Pre-trained models referenced"],
    "key_equations": ["Most important equation descriptions, not LaTeX"]
  }}
}}

=== IMPACT SCORE RUBRIC (Be rigorous - most papers should score 4-6) ===

**1-2 (Minimal Impact):**
- Minor variation on existing work with no clear advantage
- Replication study or trivial extension
- Very narrow applicability, unlikely to be cited
- Example: "We apply method X to dataset Y with similar results"

**3-4 (Low Impact):**
- Modest improvement over baselines (5-15% on standard metrics)
- Solid execution but limited novelty
- Useful for specialists in a narrow subfield
- Example: "New regularization technique with small gains on CIFAR-10"

**5-6 (Moderate Impact - MOST PAPERS BELONG HERE):**
- Meaningful improvement (15-30% or new capability)
- Novel combination of existing ideas OR good solution to practical problem
- Will be cited by researchers in the subfield
- Example: "Efficient transformer variant that's 2x faster with comparable accuracy"

**7-8 (High Impact):**
- Significant advancement (30%+ improvement OR enables new applications)
- Novel methodology with broad applicability beyond one dataset/task
- Likely industry adoption, will influence the field for 2-3 years
- Example: "New training paradigm that works across multiple domains"

**9 (Very High Impact - Rare):**
- Major conceptual advance that changes how we approach problems
- Opens significant new research directions
- Will be highly cited (500+ citations expected)
- Example: "Attention mechanisms, Diffusion models, RLHF"

**10 (Transformative - Extremely Rare):**
- Paradigm shift that reshapes the entire field
- Enables previously impossible capabilities
- Will be cited 1000+ times, becomes standard reference
- Example: "Attention Is All You Need, ResNet, BERT, GPT-3, AlphaFold"

SCORING GUIDELINES:
- Default assumption: paper is 5 (moderate) until evidence suggests otherwise
- Ask: "Will this change how people work in 2 years?" If no → likely 4-6
- Ask: "Is this a new idea or better execution of existing idea?" Execution → lower score
- Compare mentally to landmark papers you know - most papers are NOT landmark papers
- Industry applicability alone doesn't make high impact without research novelty

Respond ONLY with the JSON object. Be thorough but concise."""


@dataclass
class DeepEnrichmentStats:
    """Statistics for a deep enrichment run."""
    total_papers: int = 0
    processed: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped_no_pdf: int = 0
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
            "skipped_no_pdf": self.skipped_no_pdf,
            "elapsed_seconds": round(elapsed, 1),
            "papers_per_minute": round(self.processed / (elapsed / 60), 2) if elapsed > 0 else 0,
            "success_rate": round(100 * self.succeeded / self.processed, 1) if self.processed > 0 else 0,
            "recent_errors": self.errors[-5:],
        }


class DeepEnrichmentService(LoggerMixin):
    """
    Service for deep PDF-based paper analysis.

    Uses Gemini's multimodal capabilities to analyze full paper content,
    including figures, tables, and methodology sections.
    """

    def __init__(self) -> None:
        self._model: Optional[genai.GenerativeModel] = None
        self._is_running = False
        self._should_stop = False
        self._current_stats: Optional[DeepEnrichmentStats] = None
        self._pdf_dir = PDF_DIR
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the Gemini model for multimodal analysis."""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.log_warning("No Gemini API key found, deep enrichment disabled")
            return

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2,  # Slightly higher for richer analysis
            ),
        )
        self.log_info(f"Initialized Gemini model for deep analysis: {MODEL_NAME}")

    @property
    def enabled(self) -> bool:
        return self._model is not None

    @property
    def is_running(self) -> bool:
        return self._is_running

    def get_status(self) -> Dict[str, Any]:
        """Get current deep enrichment status."""
        return {
            "enabled": self.enabled,
            "is_running": self._is_running,
            "model": MODEL_NAME,
            "pdf_dir": str(self._pdf_dir),
            "pdf_count": len(list(self._pdf_dir.glob("*.pdf"))) if self._pdf_dir.exists() else 0,
            "stats": self._current_stats.to_dict() if self._current_stats else None,
        }

    def stop(self) -> None:
        """Signal the enrichment to stop after current paper."""
        self._should_stop = True
        self.log_info("Stop requested for deep enrichment")

    def _get_pdf_path(self, paper_id: str) -> Optional[Path]:
        """Get the PDF path for a paper ID."""
        # Try with and without version suffix
        candidates = [
            self._pdf_dir / f"{paper_id}.pdf",
            self._pdf_dir / f"{paper_id.replace('/', '_')}.pdf",
        ]

        # Also try base ID without version
        base_id = paper_id.split("v")[0] if "v" in paper_id else paper_id
        candidates.append(self._pdf_dir / f"{base_id}.pdf")

        for path in candidates:
            if path.exists():
                return path
        return None

    def _truncate_pdf(self, pdf_path: Path, max_pages: int = MAX_PAGES) -> bytes:
        """
        Truncate PDF to first N pages (skip appendix).

        Returns the truncated PDF as bytes.
        """
        try:
            import pypdf

            reader = pypdf.PdfReader(str(pdf_path))
            writer = pypdf.PdfWriter()

            # Take first max_pages or all pages if fewer
            pages_to_include = min(len(reader.pages), max_pages)

            for i in range(pages_to_include):
                writer.add_page(reader.pages[i])

            # Write to bytes buffer
            buffer = io.BytesIO()
            writer.write(buffer)
            buffer.seek(0)
            return buffer.read()

        except Exception as e:
            self.log_warning(f"PDF truncation failed, using full PDF: {e}")
            # Fall back to full PDF
            return pdf_path.read_bytes()

    async def _analyze_pdf(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a PDF using Gemini's multimodal capabilities.
        """
        if not self._model:
            return None

        try:
            # Truncate PDF to main content
            pdf_bytes = self._truncate_pdf(pdf_path)

            # Create a temporary file for the truncated PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name

            try:
                # Upload file to Gemini (run in thread to avoid blocking event loop)
                uploaded_file = await asyncio.to_thread(
                    genai.upload_file,
                    path=tmp_path,
                    mime_type="application/pdf"
                )

                # Wait for file to be processed (run get_file in thread)
                while uploaded_file.state.name == "PROCESSING":
                    await asyncio.sleep(1)
                    uploaded_file = await asyncio.to_thread(
                        genai.get_file, uploaded_file.name
                    )

                if uploaded_file.state.name != "ACTIVE":
                    self.log_warning(f"File upload failed: {uploaded_file.state.name}")
                    return None

                # Generate analysis
                response = await self._model.generate_content_async([
                    uploaded_file,
                    DEEP_ANALYSIS_PROMPT
                ])

                # Clean up uploaded file (run in thread)
                try:
                    await asyncio.to_thread(genai.delete_file, uploaded_file.name)
                except Exception:
                    pass  # Ignore cleanup errors

                result = json.loads(response.text)
                return result

            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)

        except json.JSONDecodeError as e:
            self.log_warning(f"JSON parse error in deep analysis: {e}")
            return None
        except Exception as e:
            self.log_warning(f"Deep analysis error: {e}")
            return None

    async def _update_paper(
        self,
        paper_id: str,
        deep_analysis: Dict[str, Any],
    ) -> bool:
        """Update a paper in the database with deep analysis."""
        try:
            query = """
                UPDATE papers
                SET deep_analysis = :deep_analysis, updated_at = :updated_at
                WHERE id = :paper_id
            """
            await database.execute(query, {
                "paper_id": paper_id,
                "deep_analysis": json.dumps(deep_analysis),
                "updated_at": datetime.utcnow(),
            })
            return True
        except Exception as e:
            self.log_warning(f"DB update failed for {paper_id}: {e}")
            return False

    async def enrich_single_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Perform deep enrichment on a single paper.

        Returns the analysis if successful, None otherwise.
        """
        if not self.enabled:
            return None

        pdf_path = self._get_pdf_path(paper_id)
        if not pdf_path:
            self.log_warning(f"No PDF found for paper: {paper_id}")
            return None

        self.log_info(f"Starting deep analysis for {paper_id}")
        analysis = await self._analyze_pdf(pdf_path)

        if analysis:
            await self._update_paper(paper_id, analysis)
            self.log_info(f"Deep analysis complete for {paper_id}")

        return analysis

    async def _process_single_paper(
        self,
        paper_id: str,
        pdf_path: Path,
        stats: DeepEnrichmentStats,
        semaphore: asyncio.Semaphore,
    ) -> None:
        """Process a single paper with semaphore for concurrency control."""
        async with semaphore:
            if self._should_stop:
                return

            try:
                analysis = await self._analyze_pdf(pdf_path)
                if analysis:
                    success = await self._update_paper(paper_id, analysis)
                    if success:
                        stats.succeeded += 1
                    else:
                        stats.failed += 1
                else:
                    stats.failed += 1
            except Exception as e:
                stats.failed += 1
                stats.errors.append(f"{paper_id}: {str(e)[:80]}")
            finally:
                stats.processed += 1

    async def run_deep_enrichment(
        self,
        max_papers: Optional[int] = None,
        priority_filter: Optional[str] = None,
        skip_existing: bool = True,
    ) -> DeepEnrichmentStats:
        """
        Run deep enrichment on papers with parallel processing.

        Args:
            max_papers: Maximum papers to process (None = all eligible)
            priority_filter: SQL filter for priority (e.g., "impact_score >= 7")
            skip_existing: Skip papers that already have deep_analysis

        Returns:
            DeepEnrichmentStats with results
        """
        if not self.enabled:
            raise RuntimeError("Deep enrichment service not enabled (no API key)")

        if self._is_running:
            raise RuntimeError("Deep enrichment already running")

        self._is_running = True
        self._should_stop = False
        stats = DeepEnrichmentStats(start_time=time.time())
        self._current_stats = stats

        # Semaphore for controlling concurrency
        semaphore = asyncio.Semaphore(CONCURRENT_WORKERS)

        try:
            # Build query to find papers to process
            where_clauses = []
            if skip_existing:
                where_clauses.append("deep_analysis IS NULL")
            if priority_filter:
                where_clauses.append(f"({priority_filter})")

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            # Count total
            count_query = f"SELECT COUNT(*) FROM papers WHERE {where_sql}"
            result = await database.fetch_one(count_query)
            stats.total_papers = result[0] if result else 0

            if max_papers:
                stats.total_papers = min(stats.total_papers, max_papers)

            self.log_info(f"Starting parallel deep enrichment of {stats.total_papers} papers ({CONCURRENT_WORKERS} workers)")

            # Process papers in batches with parallel workers
            offset = 0
            while offset < stats.total_papers and not self._should_stop:
                # Fetch batch of paper IDs
                query = f"""
                    SELECT id FROM papers
                    WHERE {where_sql}
                    ORDER BY
                        CASE WHEN ai_analysis->>'impactScore' IS NOT NULL
                             THEN (ai_analysis->>'impactScore')::int
                             ELSE 0 END DESC,
                        published_date DESC
                    LIMIT :limit OFFSET :offset
                """
                papers = await database.fetch_all(
                    query, {"limit": BATCH_SIZE, "offset": offset}
                )

                if not papers:
                    break

                # Build list of tasks for papers with PDFs
                tasks = []
                for paper in papers:
                    if self._should_stop:
                        break

                    paper_id = paper["id"]
                    pdf_path = self._get_pdf_path(paper_id)

                    if not pdf_path:
                        stats.skipped_no_pdf += 1
                        continue

                    # Create task for parallel processing
                    task = self._process_single_paper(paper_id, pdf_path, stats, semaphore)
                    tasks.append(task)

                # Process batch in parallel
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                # Progress logging
                pct = round(100 * stats.processed / stats.total_papers, 1) if stats.total_papers > 0 else 0
                self.log_info(
                    f"Deep enrichment progress: {stats.processed}/{stats.total_papers} ({pct}%) "
                    f"- Success: {stats.succeeded}, Failed: {stats.failed}"
                )

                offset += BATCH_SIZE

                # Small delay between batches to avoid overwhelming the API
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)

            stats.end_time = time.time()
            self.log_info(f"Deep enrichment complete: {stats.to_dict()}")
            return stats

        finally:
            self._is_running = False


# Module-level singleton
_deep_enrichment_service: Optional[DeepEnrichmentService] = None


def get_deep_enrichment_service() -> DeepEnrichmentService:
    """Get or create the deep enrichment service singleton."""
    global _deep_enrichment_service
    if _deep_enrichment_service is None:
        _deep_enrichment_service = DeepEnrichmentService()
    return _deep_enrichment_service
