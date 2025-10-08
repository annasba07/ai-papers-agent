"""
Code Detection Service - Find implementations for research papers
Detects GitHub repos, official code, community implementations
"""
import re
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from app.core.config import settings
from app.utils.logger import LoggerMixin


class CodeRepository:
    """Represents a code repository for a paper"""

    def __init__(
        self,
        url: str,
        stars: int,
        forks: int,
        last_updated: datetime,
        description: str,
        is_official: bool = False,
        language: str = "Unknown"
    ):
        self.url = url
        self.stars = stars
        self.forks = forks
        self.last_updated = last_updated
        self.description = description
        self.is_official = is_official
        self.language = language
        self.quality_score = self._calculate_quality_score()

    def _calculate_quality_score(self) -> float:
        """
        Calculate repository quality score (0-10)
        Factors: stars, recency, official status, activity
        """
        score = 0.0

        # Stars (max 4 points)
        if self.stars >= 1000:
            score += 4.0
        elif self.stars >= 100:
            score += 3.0
        elif self.stars >= 10:
            score += 2.0
        else:
            score += 1.0

        # Recency (max 2 points)
        days_old = (datetime.now() - self.last_updated).days
        if days_old < 30:
            score += 2.0
        elif days_old < 180:
            score += 1.5
        elif days_old < 365:
            score += 1.0
        else:
            score += 0.5

        # Official repo bonus (2 points)
        if self.is_official:
            score += 2.0

        # Activity (forks indicate usage) (max 2 points)
        if self.forks >= 100:
            score += 2.0
        elif self.forks >= 10:
            score += 1.0
        else:
            score += 0.5

        return min(score, 10.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "url": self.url,
            "stars": self.stars,
            "forks": self.forks,
            "lastUpdated": self.last_updated.isoformat(),
            "description": self.description,
            "isOfficial": self.is_official,
            "language": self.language,
            "qualityScore": round(self.quality_score, 2)
        }


class CodeDetectionService(LoggerMixin):
    """Service for detecting code implementations of research papers"""

    # Common GitHub URL patterns
    GITHUB_PATTERNS = [
        r'github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)',
        r'https?://(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)',
    ]

    def __init__(self):
        self.log_info("Code Detection Service initialized")

    async def detect_code_from_paper(
        self,
        title: str,
        abstract: str,
        authors: List[str],
        arxiv_id: str
    ) -> Dict[str, Any]:
        """
        Detect all code repositories related to a paper

        Returns:
            {
                "hasCode": bool,
                "officialRepo": Repository or None,
                "communityRepos": List[Repository],
                "totalRepos": int
            }
        """
        self.log_info("Detecting code for paper", title=title[:50])

        # 1. Extract GitHub links from abstract/paper
        extracted_links = self._extract_github_links(abstract)

        # 2. Search GitHub for paper title
        search_results = await self._search_github(title, authors)

        # 3. Combine and deduplicate
        all_repos = self._merge_and_dedupe(extracted_links, search_results)

        # 4. Classify official vs community
        official_repo = self._identify_official_repo(all_repos, authors)
        community_repos = [r for r in all_repos if r != official_repo]

        # 5. Sort by quality
        community_repos.sort(key=lambda r: r.quality_score, reverse=True)

        return {
            "hasCode": len(all_repos) > 0,
            "officialRepo": official_repo.to_dict() if official_repo else None,
            "communityRepos": [r.to_dict() for r in community_repos[:10]],  # Top 10
            "totalRepos": len(all_repos)
        }

    def _extract_github_links(self, text: str) -> List[str]:
        """Extract GitHub repository URLs from text"""
        links = []
        for pattern in self.GITHUB_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                user, repo = match.groups()
                url = f"https://github.com/{user}/{repo}"
                if url not in links:
                    links.append(url)

        self.log_debug(f"Extracted {len(links)} GitHub links from text")
        return links

    async def _search_github(
        self,
        title: str,
        authors: List[str]
    ) -> List[CodeRepository]:
        """
        Search GitHub for repositories matching paper title
        Uses GitHub Search API
        """
        repos = []

        # Clean title for search
        search_query = self._clean_title_for_search(title)

        # Search combinations: title + "pytorch", title + "tensorflow", etc.
        frameworks = ["pytorch", "tensorflow", "jax", "implementation"]

        for framework in frameworks[:2]:  # Limit to avoid rate limits
            query = f"{search_query} {framework}"
            try:
                results = await self._github_search_api(query, max_results=5)
                repos.extend(results)
            except Exception as e:
                self.log_warning(f"GitHub search failed for '{query}'", error=str(e))

        return repos

    def _clean_title_for_search(self, title: str) -> str:
        """Clean paper title for GitHub search"""
        # Remove common paper words
        title = re.sub(r'\b(via|using|for|with|and|the|of|in|on)\b', '', title, flags=re.IGNORECASE)
        # Remove special characters
        title = re.sub(r'[^\w\s]', '', title)
        # Remove extra spaces
        title = ' '.join(title.split())
        return title.strip()

    async def _github_search_api(
        self,
        query: str,
        max_results: int = 10
    ) -> List[CodeRepository]:
        """
        Call GitHub Search API
        Note: Requires GITHUB_TOKEN in settings for higher rate limits
        """
        repos = []

        # GitHub API endpoint
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": max_results
        }

        headers = {"Accept": "application/vnd.github.v3+json"}

        # Add GitHub token if available (optional)
        github_token = getattr(settings, 'GITHUB_TOKEN', None)
        if github_token:
            headers["Authorization"] = f"token {github_token}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                for item in data.get("items", []):
                    repo = CodeRepository(
                        url=item["html_url"],
                        stars=item["stargazers_count"],
                        forks=item["forks_count"],
                        last_updated=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")),
                        description=item.get("description", ""),
                        language=item.get("language", "Unknown")
                    )
                    repos.append(repo)

                self.log_debug(f"GitHub API returned {len(repos)} repos for '{query}'")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                self.log_warning("GitHub API rate limit exceeded")
            else:
                self.log_error("GitHub API request failed", status=e.response.status_code)
        except Exception as e:
            self.log_error("GitHub search failed", error=str(e))

        return repos

    def _merge_and_dedupe(
        self,
        extracted_links: List[str],
        search_results: List[CodeRepository]
    ) -> List[CodeRepository]:
        """Merge extracted links with search results, removing duplicates"""
        # Convert extracted links to Repository objects (we'd need to fetch their data)
        # For now, just use search results
        # TODO: Fetch repo data for extracted links

        # Deduplicate by URL
        seen_urls = set()
        unique_repos = []

        for repo in search_results:
            if repo.url not in seen_urls:
                seen_urls.add(repo.url)
                unique_repos.append(repo)

        return unique_repos

    def _identify_official_repo(
        self,
        repos: List[CodeRepository],
        authors: List[str]
    ) -> Optional[CodeRepository]:
        """
        Identify the official repository
        Heuristics:
        - Repo owner matches author name
        - Highest stars
        - Most recent
        """
        if not repos:
            return None

        # Check if any repo owner matches author
        for repo in repos:
            owner = repo.url.split("/")[3].lower()
            for author in authors:
                # Simple name matching (first or last name)
                author_parts = author.lower().split()
                if any(part in owner for part in author_parts if len(part) > 3):
                    repo.is_official = True
                    return repo

        # If no author match, return highest quality repo
        return max(repos, key=lambda r: r.quality_score)


# Global service instance
code_detection_service = CodeDetectionService()
