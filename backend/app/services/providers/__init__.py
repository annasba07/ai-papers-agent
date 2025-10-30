"""
Provider adapters for external data sources feeding the research graph.

These are intentionally lightweight wrappers. Each adapter should:
- expose async methods that return the schema models in app.schemas.research_graph
- handle API quirks, pagination, retries, and rate limits internally
- surface telemetry via LoggerMixin to aid observability
"""

from .openalex_provider import OpenAlexProvider
from .pwc_provider import PapersWithCodeProvider
from .github_provider import GitHubRepoProvider

__all__ = [
    "OpenAlexProvider",
    "PapersWithCodeProvider",
    "GitHubRepoProvider",
]
