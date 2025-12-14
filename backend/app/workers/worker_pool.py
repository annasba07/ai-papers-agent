"""
Worker Pool Manager - Manages in-process worker pools

Provides API for starting/stopping worker pools with configurable counts.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.workers.base_worker import BaseWorker
from app.workers.enrichment_workers import (
    LLMWorker,
    ExternalAPIWorker,
    LocalWorker,
    CitationBatchWorker,
)
from app.services.pipeline.rate_limiter import initialize_rate_limiters

logger = logging.getLogger(__name__)


# Default worker configuration
DEFAULT_WORKER_CONFIG = {
    "llm": {
        "count": 15,  # Gemini ~60 req/min, 15 workers with 1s delay each
        "worker_class": LLMWorker,
    },
    "citations": {
        "count": 2,  # Batch API is efficient
        "worker_class": ExternalAPIWorker,
    },
    "github": {
        "count": 3,  # 5000 req/hr limit
        "worker_class": ExternalAPIWorker,
    },
    "local": {
        "count": 4,  # CPU-bound operations
        "worker_class": LocalWorker,
    },
}


class WorkerPoolManager:
    """
    Manages pools of workers for the enrichment pipeline.

    Can start/stop pools of workers, monitor their status,
    and adjust pool sizes dynamically.
    """

    def __init__(self):
        self._workers: Dict[str, List[BaseWorker]] = {}
        self._tasks: Dict[str, List[asyncio.Task]] = {}
        self._running = False
        self._started_at: Optional[datetime] = None
        self._config: Dict[str, Dict[str, Any]] = {}

    async def start(
        self,
        config: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Start worker pools.

        Args:
            config: Optional configuration override. Format:
                {
                    "llm": {"count": 10},
                    "citations": {"count": 2},
                    ...
                }

        Returns:
            Status of started workers
        """
        if self._running:
            return {"error": "Worker pool already running"}

        # Initialize rate limiters
        await initialize_rate_limiters()

        self._config = config or DEFAULT_WORKER_CONFIG
        self._running = True
        self._started_at = datetime.utcnow()

        results = {}

        for pool_name, pool_config in self._config.items():
            count = pool_config.get("count", 1)
            worker_class = pool_config.get("worker_class")

            if not worker_class:
                # Get worker class from defaults
                default_config = DEFAULT_WORKER_CONFIG.get(pool_name, {})
                worker_class = default_config.get("worker_class")

            if not worker_class:
                logger.warning(f"No worker class for pool {pool_name}")
                continue

            self._workers[pool_name] = []
            self._tasks[pool_name] = []

            for i in range(count):
                worker = worker_class(worker_id=f"{pool_name}-{i}")
                self._workers[pool_name].append(worker)

                # Start worker task
                task = asyncio.create_task(worker.start())
                self._tasks[pool_name].append(task)

            results[pool_name] = {
                "started": count,
                "worker_class": worker_class.__name__,
                "job_types": worker_class.JOB_TYPES
            }

            logger.info(f"Started {count} {pool_name} workers")

        return {
            "status": "started",
            "pools": results,
            "started_at": self._started_at.isoformat()
        }

    async def stop(self, timeout: float = 30.0) -> Dict[str, Any]:
        """
        Gracefully stop all worker pools.

        Args:
            timeout: Maximum time to wait for workers to stop

        Returns:
            Status of stopped workers
        """
        if not self._running:
            return {"error": "Worker pool not running"}

        self._running = False
        results = {}

        for pool_name, workers in self._workers.items():
            # Signal all workers to stop
            for worker in workers:
                await worker.stop()

            # Wait for tasks to complete
            tasks = self._tasks.get(pool_name, [])
            if tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    # Cancel remaining tasks
                    for task in tasks:
                        if not task.done():
                            task.cancel()

            results[pool_name] = {
                "stopped": len(workers),
                "stats": [w.get_status() for w in workers]
            }

            logger.info(f"Stopped {len(workers)} {pool_name} workers")

        self._workers.clear()
        self._tasks.clear()
        self._started_at = None

        return {
            "status": "stopped",
            "pools": results
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current status of all worker pools."""
        pools = {}

        for pool_name, workers in self._workers.items():
            pool_stats = {
                "count": len(workers),
                "workers": []
            }

            total_processed = 0
            total_failed = 0

            for worker in workers:
                status = worker.get_status()
                pool_stats["workers"].append(status)
                total_processed += status.get("jobs_processed", 0)
                total_failed += status.get("jobs_failed", 0)

            pool_stats["total_processed"] = total_processed
            pool_stats["total_failed"] = total_failed
            pools[pool_name] = pool_stats

        return {
            "running": self._running,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "uptime_seconds": (datetime.utcnow() - self._started_at).total_seconds() if self._started_at else 0,
            "pools": pools
        }

    async def scale_pool(
        self,
        pool_name: str,
        count: int
    ) -> Dict[str, Any]:
        """
        Scale a worker pool to a new count.

        Args:
            pool_name: Name of the pool to scale
            count: New worker count

        Returns:
            Status of scaling operation
        """
        if not self._running:
            return {"error": "Worker pool not running"}

        if pool_name not in self._workers:
            return {"error": f"Pool {pool_name} not found"}

        current_count = len(self._workers[pool_name])

        if count == current_count:
            return {"status": "unchanged", "count": current_count}

        if count > current_count:
            # Add workers
            config = self._config.get(pool_name, {})
            worker_class = config.get("worker_class")

            if not worker_class:
                default_config = DEFAULT_WORKER_CONFIG.get(pool_name, {})
                worker_class = default_config.get("worker_class")

            if not worker_class:
                return {"error": f"No worker class for pool {pool_name}"}

            for i in range(current_count, count):
                worker = worker_class(worker_id=f"{pool_name}-{i}")
                self._workers[pool_name].append(worker)
                task = asyncio.create_task(worker.start())
                self._tasks[pool_name].append(task)

            logger.info(f"Scaled {pool_name} pool from {current_count} to {count} workers")

            return {
                "status": "scaled_up",
                "previous": current_count,
                "current": count,
                "added": count - current_count
            }

        else:
            # Remove workers
            workers_to_remove = self._workers[pool_name][count:]
            self._workers[pool_name] = self._workers[pool_name][:count]

            tasks_to_cancel = self._tasks[pool_name][count:]
            self._tasks[pool_name] = self._tasks[pool_name][:count]

            for worker in workers_to_remove:
                await worker.stop()

            for task in tasks_to_cancel:
                if not task.done():
                    task.cancel()

            logger.info(f"Scaled {pool_name} pool from {current_count} to {count} workers")

            return {
                "status": "scaled_down",
                "previous": current_count,
                "current": count,
                "removed": current_count - count
            }

    @property
    def is_running(self) -> bool:
        """Check if the worker pool is running."""
        return self._running


# Singleton instance
_worker_pool: Optional[WorkerPoolManager] = None


def get_worker_pool() -> WorkerPoolManager:
    """Get or create the worker pool manager singleton."""
    global _worker_pool
    if _worker_pool is None:
        _worker_pool = WorkerPoolManager()
    return _worker_pool
