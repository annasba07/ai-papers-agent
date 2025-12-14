"""
Base Worker - Abstract base class for all pipeline workers

Workers are long-running async tasks that:
1. Claim jobs from the queue using FOR UPDATE SKIP LOCKED
2. Execute the job's enrichment task
3. Report success/failure back to the database
4. Handle retries with exponential backoff
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.db.database import database
from app.services.pipeline.rate_limiter import RateLimiter, get_rate_limiter

logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """
    Abstract base class for pipeline workers.

    Subclasses must implement:
    - JOB_TYPES: List of job types this worker handles
    - RATE_LIMIT_PROVIDER: Provider name for rate limiting
    - _process_job(): The actual job processing logic
    """

    # Override in subclasses
    JOB_TYPES: List[str] = []
    RATE_LIMIT_PROVIDER: str = "local"
    HEARTBEAT_INTERVAL: int = 30  # seconds
    IDLE_SLEEP: float = 1.0  # seconds to sleep when no jobs

    def __init__(self, worker_id: Optional[str] = None):
        self.worker_id = worker_id or f"{self.__class__.__name__}-{uuid.uuid4().hex[:8]}"
        self.rate_limiter: RateLimiter = get_rate_limiter()
        self._running = False
        self._current_job_id: Optional[int] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._jobs_processed = 0
        self._jobs_failed = 0
        self._started_at: Optional[datetime] = None

    async def start(self) -> None:
        """Start the worker's main loop."""
        self._running = True
        self._started_at = datetime.utcnow()
        logger.info(f"Worker {self.worker_id} starting (types: {self.JOB_TYPES})")

        # Start heartbeat task
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        try:
            while self._running:
                job = await self._get_next_job()

                if job:
                    self._current_job_id = job["id"]
                    try:
                        await self._execute_job(job)
                    finally:
                        self._current_job_id = None
                else:
                    # No jobs available - sleep briefly
                    await asyncio.sleep(self.IDLE_SLEEP)
        except asyncio.CancelledError:
            logger.info(f"Worker {self.worker_id} cancelled")
        except Exception as e:
            logger.error(f"Worker {self.worker_id} error: {e}", exc_info=True)
        finally:
            self._running = False
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
            logger.info(f"Worker {self.worker_id} stopped (processed: {self._jobs_processed}, failed: {self._jobs_failed})")

    async def stop(self) -> None:
        """Gracefully stop the worker."""
        logger.info(f"Worker {self.worker_id} stopping...")
        self._running = False

    def get_status(self) -> Dict[str, Any]:
        """Get current worker status."""
        return {
            "worker_id": self.worker_id,
            "job_types": self.JOB_TYPES,
            "rate_limit_provider": self.RATE_LIMIT_PROVIDER,
            "running": self._running,
            "current_job_id": self._current_job_id,
            "jobs_processed": self._jobs_processed,
            "jobs_failed": self._jobs_failed,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "uptime_seconds": (datetime.utcnow() - self._started_at).total_seconds() if self._started_at else 0
        }

    async def _get_next_job(self) -> Optional[Dict[str, Any]]:
        """
        Get the next available job from the queue.

        Uses PostgreSQL's FOR UPDATE SKIP LOCKED for distributed coordination.
        """
        if not self.JOB_TYPES:
            logger.warning(f"Worker {self.worker_id} has no JOB_TYPES defined")
            return None

        # Build job types array literal for PostgreSQL
        # We embed the array directly in the query to avoid parameter binding issues
        # with the databases library and PostgreSQL CAST syntax
        job_types_literal = "ARRAY[" + ",".join(f"'{jt}'" for jt in self.JOB_TYPES) + "]::job_type[]"

        # Use string formatting for the array literal (safe - job types are hardcoded)
        query = f"""
            SELECT * FROM get_next_job(:worker_id, {job_types_literal})
        """

        try:
            row = await database.fetch_one(query, {
                "worker_id": self.worker_id
            })

            if row and row["id"]:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting next job: {e}")
            return None

    async def _execute_job(self, job: Dict[str, Any]) -> None:
        """Execute a job with rate limiting and error handling."""
        job_id = job["id"]
        job_type = job["job_type"]
        paper_id = job.get("paper_id")

        logger.info(f"Worker {self.worker_id} processing job {job_id} ({job_type}) for paper {paper_id}")

        try:
            # Acquire rate limit permission
            if not await self.rate_limiter.acquire(self.RATE_LIMIT_PROVIDER, timeout=60):
                # Rate limit timeout - reschedule job
                await self._fail_job(job_id, "Rate limit timeout", reschedule=True)
                return

            # Process the job
            result = await self._process_job(job)

            # Mark as complete
            await self._complete_job(job_id, result)
            self._jobs_processed += 1
            logger.info(f"Job {job_id} completed successfully")

        except RateLimitError as e:
            # External API rate limit hit
            await self.rate_limiter.report_rate_limit_hit(
                self.RATE_LIMIT_PROVIDER,
                backoff_seconds=e.backoff_seconds
            )
            await self._fail_job(job_id, str(e), reschedule=True)
            self._jobs_failed += 1

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            await self._fail_job(job_id, str(e), error_details={"traceback": str(e)})
            self._jobs_failed += 1

    async def _complete_job(
        self,
        job_id: int,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark a job as completed."""
        query = "SELECT complete_job(:job_id, :result)"
        await database.execute(query, {
            "job_id": job_id,
            "result": json.dumps(result or {})
        })

    async def _fail_job(
        self,
        job_id: int,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None,
        reschedule: bool = False
    ) -> None:
        """Mark a job as failed (will retry if under max_retries)."""
        if reschedule:
            # Just reset to pending for immediate retry
            query = """
                UPDATE processing_jobs
                SET status = 'pending',
                    worker_id = NULL,
                    started_at = NULL
                WHERE id = :job_id
            """
            await database.execute(query, {"job_id": job_id})
        else:
            # Use the fail_job function which handles retry logic
            query = "SELECT fail_job(:job_id, :error, :error_details)"
            await database.execute(query, {
                "job_id": job_id,
                "error": error_message,
                "error_details": json.dumps(error_details or {})
            })

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats while processing."""
        while self._running:
            try:
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                if self._current_job_id:
                    await self._send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Heartbeat error: {e}")

    async def _send_heartbeat(self) -> None:
        """Update heartbeat timestamp for current job."""
        if self._current_job_id:
            query = """
                UPDATE processing_jobs
                SET heartbeat_at = NOW()
                WHERE id = :job_id
                AND worker_id = :worker_id
            """
            await database.execute(query, {
                "job_id": self._current_job_id,
                "worker_id": self.worker_id
            })

    @abstractmethod
    async def _process_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a job and return the result.

        Args:
            job: The job record from processing_jobs table

        Returns:
            Optional result dict to store in the job

        Raises:
            RateLimitError: If external API rate limit hit
            Exception: For any processing error
        """
        pass


class RateLimitError(Exception):
    """Raised when an external API rate limit is hit."""

    def __init__(self, message: str, backoff_seconds: int = 60):
        super().__init__(message)
        self.backoff_seconds = backoff_seconds


async def update_processing_state(
    paper_id: str,
    stage: str,
    success: bool = True
) -> None:
    """
    Update the paper_processing_state after completing a stage.

    Args:
        paper_id: The paper ID
        stage: The stage name (e.g., 'embedding', 'ai_analysis')
        success: Whether the stage completed successfully
    """
    if success:
        # Map stage names to column names
        column_map = {
            "embedding": "embedding_at",
            "ai_analysis": "ai_analysis_at",
            "citations": "citations_at",
            "concepts": "concepts_at",
            "techniques": "techniques_at",
            "benchmarks": "benchmarks_at",
            "github": "github_at",
            "deep_analysis": "deep_analysis_at",
            "relationships": "relationships_at",
        }

        column = column_map.get(stage)
        if column:
            query = f"""
                UPDATE paper_processing_state
                SET {column} = NOW(),
                    updated_at = NOW()
                WHERE paper_id = :paper_id
            """
            await database.execute(query, {"paper_id": paper_id})
