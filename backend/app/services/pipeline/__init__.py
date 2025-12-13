"""
Scalable Paper Enrichment Pipeline

This package provides a worker-based, API-driven enrichment pipeline that handles:
- Backfill: One-time processing of existing papers
- New Papers: Ongoing enrichment of newly ingested papers
- On-demand: Manual enrichment requests via API

Both flows coexist using priority-based scheduling.
"""

from .rate_limiter import RateLimiter, get_rate_limiter
from .pipeline_service import PipelineService, get_pipeline_service, JobPriority

__all__ = [
    "RateLimiter",
    "get_rate_limiter",
    "PipelineService",
    "get_pipeline_service",
    "JobPriority",
]
