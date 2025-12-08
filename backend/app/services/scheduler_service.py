"""
Scheduler Service for Background Jobs

Uses APScheduler to run periodic tasks like daily paper ingestion.
Integrates with FastAPI lifecycle events.
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.utils.logger import LoggerMixin
from app.services.daily_ingestion_service import get_daily_ingestion_service
from app.core.config import settings


class SchedulerService(LoggerMixin):
    """
    Manages scheduled background tasks.

    Currently supports:
    - Daily paper ingestion from arXiv
    """

    def __init__(self) -> None:
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._enabled = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"
        self._ingestion_hour = int(os.getenv("INGESTION_HOUR", "6"))  # 6 AM UTC by default
        self._ingestion_minute = int(os.getenv("INGESTION_MINUTE", "0"))

        self.log_info(
            "Scheduler service initialized",
            enabled=self._enabled,
            ingestion_time=f"{self._ingestion_hour:02d}:{self._ingestion_minute:02d} UTC"
        )

    @property
    def is_running(self) -> bool:
        return self._scheduler is not None and self._scheduler.running

    def start(self) -> None:
        """Start the scheduler."""
        if not self._enabled:
            self.log_info("Scheduler is disabled. Set ENABLE_SCHEDULER=true to enable.")
            return

        if self._scheduler is not None:
            self.log_warning("Scheduler already initialized")
            return

        self._scheduler = AsyncIOScheduler()

        # Add daily ingestion job
        self._scheduler.add_job(
            self._run_daily_ingestion,
            CronTrigger(hour=self._ingestion_hour, minute=self._ingestion_minute),
            id="daily_ingestion",
            name="Daily Paper Ingestion",
            replace_existing=True,
            max_instances=1,  # Prevent overlapping runs
        )

        self._scheduler.start()
        self.log_info(
            "Scheduler started",
            jobs=len(self._scheduler.get_jobs()),
            next_run=self._get_next_run_time()
        )

    def stop(self) -> None:
        """Stop the scheduler gracefully."""
        if self._scheduler is not None:
            self._scheduler.shutdown(wait=True)
            self._scheduler = None
            self.log_info("Scheduler stopped")

    def _get_next_run_time(self) -> Optional[str]:
        """Get the next scheduled run time."""
        if self._scheduler is None:
            return None

        job = self._scheduler.get_job("daily_ingestion")
        if job and job.next_run_time:
            return job.next_run_time.isoformat()
        return None

    async def _run_daily_ingestion(self) -> None:
        """Execute the daily ingestion job."""
        self.log_info("Starting scheduled daily ingestion")

        try:
            service = get_daily_ingestion_service()
            stats = await service.run_ingestion(
                categories=settings.DEFAULT_AI_CATEGORIES,
                max_per_category=100,
                days_back=2,
                generate_embeddings=False
            )

            self.log_info(
                "Scheduled ingestion complete",
                papers_new=stats.get("papers_new", 0),
                papers_appended=stats.get("papers_appended", 0)
            )

        except Exception as e:
            self.log_error("Scheduled ingestion failed", error=e)

    def get_status(self) -> dict:
        """Get current scheduler status."""
        jobs = []
        if self._scheduler is not None:
            for job in self._scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                })

        return {
            "enabled": self._enabled,
            "is_running": self.is_running,
            "ingestion_time_utc": f"{self._ingestion_hour:02d}:{self._ingestion_minute:02d}",
            "jobs": jobs,
        }

    async def run_ingestion_now(self) -> dict:
        """Manually trigger the ingestion job (for testing)."""
        await self._run_daily_ingestion()
        return get_daily_ingestion_service().last_stats


# Module-level singleton
_scheduler_service: Optional[SchedulerService] = None


def get_scheduler_service() -> SchedulerService:
    """Get or create the scheduler service singleton."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
