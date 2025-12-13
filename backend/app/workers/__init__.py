"""
Worker implementations for the enrichment pipeline.

Workers are long-running processes that claim jobs from the queue
and execute enrichment tasks.
"""

from .base_worker import BaseWorker
from .worker_pool import WorkerPoolManager, get_worker_pool

__all__ = [
    "BaseWorker",
    "WorkerPoolManager",
    "get_worker_pool",
]
