"""
GitHub Enrichment Service

Fetches and enriches papers with GitHub repository data:
- Stars, forks, issues, contributors
- Last commit date
- Language, license
- README quality signals

This creates external signals that enable:
- "Show me papers with actively maintained code"
- "Papers with most GitHub stars"
- "Recently updated implementations"
"""
import asyncio
import aiohttp
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.utils.logger import LoggerMixin
from app.core.config import settings


class GitHubRepoInfo(BaseModel):
    """Information about a GitHub repository"""
    url: str
    owner: str
    repo: str
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    watchers: int = 0
    language: Optional[str] = None
    license: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None  # Last commit
    topics: List[str] = []
    contributors_count: Optional[int] = None
    is_archived: bool = False
    is_fork: bool = False
    default_branch: str = "main"


class GitHubEnricher(LoggerMixin):
    """
    Enriches papers with GitHub repository data.

    Uses GitHub API to fetch stats for repositories associated with papers.
    """

    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize enricher.

        Args:
            github_token: GitHub personal access token for higher rate limits
        """
        self.token = github_token or getattr(settings, 'GITHUB_TOKEN', None)
        self.base_url = "https://api.github.com"
        self.rate_limit_remaining = 60  # Unauthenticated limit
        self.rate_limit_reset = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Papers-Agent/1.0"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def extract_github_urls(self, paper: Dict[str, Any]) -> List[str]:
        """
        Extract GitHub URLs from paper data.

        Checks:
        - code_repos field
        - abstract
        - deep_analysis.extracted_artifacts.github_urls
        """
        urls = set()

        # Check code_repos field
        code_repos = paper.get("code_repos") or []
        if isinstance(code_repos, str):
            try:
                code_repos = json.loads(code_repos)
            except json.JSONDecodeError:
                code_repos = []
        if isinstance(code_repos, list):
            for repo in code_repos:
                if isinstance(repo, dict):
                    url = repo.get("url", "")
                else:
                    url = str(repo)
                if "github.com" in url:
                    urls.add(url)

        # Check deep_analysis
        deep = paper.get("deep_analysis") or {}
        if isinstance(deep, str):
            try:
                deep = json.loads(deep)
            except json.JSONDecodeError:
                deep = {}
        artifacts = deep.get("extracted_artifacts") or {}
        github_urls = artifacts.get("github_urls") or []
        for url in github_urls:
            if "github.com" in url:
                urls.add(url)

        # Check abstract for GitHub URLs
        abstract = paper.get("abstract", "")
        github_pattern = r'https?://github\.com/[\w\-]+/[\w\-\.]+'
        for match in re.finditer(github_pattern, abstract):
            urls.add(match.group())

        return list(urls)

    def parse_github_url(self, url: str) -> Optional[tuple]:
        """
        Parse GitHub URL to extract owner and repo.

        Returns (owner, repo) or None if invalid.
        """
        # Handle various URL formats
        patterns = [
            r'github\.com/([^/]+)/([^/\s\?#]+)',
            r'github\.com:([^/]+)/([^/\s\?#]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner = match.group(1)
                repo = match.group(2)
                # Clean up repo name
                repo = repo.rstrip('.git')
                return (owner, repo)

        return None

    async def fetch_repo_info(
        self,
        owner: str,
        repo: str,
        session: aiohttp.ClientSession
    ) -> Optional[GitHubRepoInfo]:
        """
        Fetch repository information from GitHub API.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            async with session.get(url, headers=self._get_headers()) as response:
                # Update rate limit info
                self.rate_limit_remaining = int(
                    response.headers.get("X-RateLimit-Remaining", 0)
                )
                reset_time = response.headers.get("X-RateLimit-Reset")
                if reset_time:
                    self.rate_limit_reset = datetime.fromtimestamp(int(reset_time))

                if response.status == 404:
                    self.log_debug(f"Repo not found: {owner}/{repo}")
                    return None

                if response.status == 403 and self.rate_limit_remaining == 0:
                    self.log_warning(
                        f"Rate limit exceeded. Resets at {self.rate_limit_reset}"
                    )
                    return None

                if response.status != 200:
                    self.log_warning(f"GitHub API error {response.status} for {owner}/{repo}")
                    return None

                data = await response.json()

                # Extract license
                license_info = data.get("license") or {}
                license_name = license_info.get("spdx_id") or license_info.get("name")

                return GitHubRepoInfo(
                    url=data.get("html_url", f"https://github.com/{owner}/{repo}"),
                    owner=owner,
                    repo=repo,
                    stars=data.get("stargazers_count", 0),
                    forks=data.get("forks_count", 0),
                    open_issues=data.get("open_issues_count", 0),
                    watchers=data.get("watchers_count", 0),
                    language=data.get("language"),
                    license=license_name,
                    description=data.get("description"),
                    created_at=data.get("created_at"),
                    updated_at=data.get("updated_at"),
                    pushed_at=data.get("pushed_at"),
                    topics=data.get("topics", []),
                    is_archived=data.get("archived", False),
                    is_fork=data.get("fork", False),
                    default_branch=data.get("default_branch", "main")
                )

        except asyncio.TimeoutError:
            self.log_warning(f"Timeout fetching {owner}/{repo}")
            return None
        except Exception as e:
            self.log_error(f"Error fetching {owner}/{repo}", error=e)
            return None

    async def fetch_contributors_count(
        self,
        owner: str,
        repo: str,
        session: aiohttp.ClientSession
    ) -> Optional[int]:
        """
        Fetch contributor count for a repository.

        Uses the contributors endpoint with per_page=1 and reads total from headers.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        params = {"per_page": 1, "anon": "true"}

        try:
            async with session.get(
                url,
                headers=self._get_headers(),
                params=params
            ) as response:
                if response.status != 200:
                    return None

                # Parse Link header to get total count
                link_header = response.headers.get("Link", "")
                if 'rel="last"' in link_header:
                    # Extract page number from last link
                    match = re.search(r'page=(\d+)>; rel="last"', link_header)
                    if match:
                        return int(match.group(1))

                # If no pagination, count from response
                data = await response.json()
                return len(data)

        except Exception as e:
            self.log_debug(f"Error fetching contributors for {owner}/{repo}: {e}")
            return None

    async def enrich_paper(
        self,
        paper: Dict[str, Any],
        session: Optional[aiohttp.ClientSession] = None
    ) -> Dict[str, Any]:
        """
        Enrich a single paper with GitHub data.

        Returns the external_signals dict to store.
        """
        github_urls = self.extract_github_urls(paper)

        if not github_urls:
            return {"github": {"repos": [], "total_stars": 0, "updated_at": None}}

        close_session = False
        if session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            session = aiohttp.ClientSession(timeout=timeout)
            close_session = True

        try:
            repos = []
            total_stars = 0

            for url in github_urls:
                parsed = self.parse_github_url(url)
                if not parsed:
                    continue

                owner, repo_name = parsed

                # Fetch repo info
                info = await self.fetch_repo_info(owner, repo_name, session)
                if not info:
                    continue

                # Fetch contributors (optional, skip if rate limited)
                if self.rate_limit_remaining > 10:
                    info.contributors_count = await self.fetch_contributors_count(
                        owner, repo_name, session
                    )

                repos.append({
                    "url": info.url,
                    "owner": info.owner,
                    "repo": info.repo,
                    "stars": info.stars,
                    "forks": info.forks,
                    "open_issues": info.open_issues,
                    "language": info.language,
                    "license": info.license,
                    "pushed_at": info.pushed_at,
                    "is_archived": info.is_archived,
                    "contributors": info.contributors_count,
                    "topics": info.topics
                })

                total_stars += info.stars

                # Respect rate limits
                if self.rate_limit_remaining < 5:
                    self.log_warning("Approaching rate limit, stopping enrichment")
                    break

            return {
                "github": {
                    "repos": repos,
                    "total_stars": total_stars,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }

        finally:
            if close_session:
                await session.close()

    async def enrich_papers_batch(
        self,
        papers: List[Dict[str, Any]],
        batch_size: int = 10,
        delay_between_batches: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Enrich multiple papers with GitHub data.

        Args:
            papers: List of paper dicts
            batch_size: Number of papers to process concurrently
            delay_between_batches: Seconds to wait between batches

        Returns:
            List of (paper_id, external_signals) tuples
        """
        results = []

        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:

            for i in range(0, len(papers), batch_size):
                batch = papers[i:i + batch_size]

                tasks = [
                    self.enrich_paper(paper, session)
                    for paper in batch
                ]

                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for paper, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        self.log_error(
                            f"Error enriching {paper.get('id')}",
                            error=result
                        )
                        result = {"github": {"repos": [], "total_stars": 0}}

                    results.append({
                        "paper_id": paper.get("id"),
                        "signals": result
                    })

                # Check rate limit and delay if needed
                if self.rate_limit_remaining < 20:
                    delay = 60  # Wait longer when low on rate limit
                else:
                    delay = delay_between_batches

                if i + batch_size < len(papers):
                    await asyncio.sleep(delay)

        return results

    async def save_signals(
        self,
        paper_id: str,
        signals: Dict[str, Any],
        db
    ) -> bool:
        """
        Save external signals to database.

        Merges with existing signals rather than replacing.
        """
        try:
            # Merge with existing signals
            query = """
                UPDATE papers
                SET external_signals = COALESCE(external_signals, '{}'::jsonb) || :signals
                WHERE id = :paper_id
            """

            await db.execute(query, {
                "paper_id": paper_id,
                "signals": json.dumps(signals)
            })

            return True

        except Exception as e:
            self.log_error(f"Error saving signals for {paper_id}", error=e)
            return False


class ExternalSignalsService(LoggerMixin):
    """
    High-level service for managing external signals.
    """

    def __init__(self):
        self.github = GitHubEnricher()

    async def get_paper_signals(
        self,
        paper_id: str,
        db
    ) -> Dict[str, Any]:
        """Get external signals for a paper"""
        query = """
            SELECT external_signals FROM papers WHERE id = :paper_id
        """

        result = await db.fetch_one(query, {"paper_id": paper_id})

        if result and result["external_signals"]:
            return result["external_signals"]

        return {}

    async def refresh_github_signals(
        self,
        paper: Dict[str, Any],
        db
    ) -> Dict[str, Any]:
        """
        Refresh GitHub signals for a paper.
        """
        signals = await self.github.enrich_paper(paper)

        if signals.get("github", {}).get("repos"):
            await self.github.save_signals(paper.get("id"), signals, db)

        return signals

    async def get_papers_with_high_github_activity(
        self,
        db,
        min_stars: int = 100,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get papers with high GitHub activity.
        """
        query = """
            SELECT
                id,
                title,
                category,
                published_date,
                citation_count,
                (external_signals->'github'->>'total_stars')::int as github_stars,
                external_signals->'github'->'repos' as repos
            FROM papers
            WHERE external_signals IS NOT NULL
            AND (external_signals->'github'->>'total_stars')::int >= :min_stars
            ORDER BY (external_signals->'github'->>'total_stars')::int DESC
            LIMIT :limit
        """

        results = await db.fetch_all(query, {
            "min_stars": min_stars,
            "limit": limit
        })

        return [
            {
                "id": r["id"],
                "title": r["title"],
                "category": r["category"],
                "published_date": r["published_date"].isoformat() if r["published_date"] else None,
                "citation_count": r["citation_count"],
                "github_stars": r["github_stars"],
                "repos": r["repos"]
            }
            for r in results
        ]


# Singleton instance
_signals_service = None

def get_external_signals_service() -> ExternalSignalsService:
    """Get singleton external signals service instance"""
    global _signals_service
    if _signals_service is None:
        _signals_service = ExternalSignalsService()
    return _signals_service
