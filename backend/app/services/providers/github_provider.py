"""
Adapter for GitHub API interactions (REST or GraphQL depending on scope).

Focus areas:
- Repository metadata enrichment (stars, forks, languages, recent activity)
- Contributor insights (organisation overlap)
- Issue/pull request signals (maintenance health)
"""
from __future__ import annotations

from typing import Sequence, List, Dict, Any

from .base import BaseProvider


class GitHubRepoProvider(BaseProvider):
    """
    Fetches and normalises GitHub repository metadata.
    """

    async def fetch_repository_metadata(
        self,
        repo_urls: Sequence[str]
    ) -> List[Dict[str, Any]]:
        """
        Return normalised metadata for the requested repositories.

        Expected fields:
        {
            "url": "...",
            "stars": 123,
            "forks": 45,
            "last_updated": "2024-08-01T12:00:00Z",
            "primary_language": "Python",
            "open_issues": 12,
            "license": "mit",
            "contributors": [
                {"login": "...", "contributions": 10}
            ]
        }
        """
        if not repo_urls:
            return []

        self.log_debug("GitHub metadata fetch (stub)", repo_count=len(repo_urls))
        return []

    async def fetch_repo_activity(
        self,
        repo_urls: Sequence[str]
    ) -> List[Dict[str, Any]]:
        """
        Provide lightweight activity signals (commits, releases, issues) for trends.
        """
        if not repo_urls:
            return []

        self.log_debug("GitHub activity fetch (stub)", repo_count=len(repo_urls))
        return []
