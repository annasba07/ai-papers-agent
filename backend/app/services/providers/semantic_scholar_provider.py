"""
Semantic Scholar Provider - Citation and metadata enrichment

Semantic Scholar indexes over 200M papers with excellent arXiv coverage.
- Much better arXiv coverage than OpenAlex
- Direct arXiv ID lookup support
- Rate limits: 100 requests/5 min (public), higher with API key

API Docs: https://api.semanticscholar.org/api-docs/
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

import httpx
from pydantic import BaseModel
from dotenv import load_dotenv

from .base import BaseProvider

load_dotenv()


class SemanticScholarPaper(BaseModel):
    """Parsed paper data from Semantic Scholar"""
    semantic_scholar_id: str
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    title: str
    publication_date: Optional[str] = None
    cited_by_count: int = 0
    reference_count: int = 0
    references: List[Dict[str, Any]] = []
    citations: List[Dict[str, Any]] = []
    authors: List[Dict[str, Any]] = []
    abstract: Optional[str] = None
    venue: Optional[str] = None
    year: Optional[int] = None
    influential_citation_count: int = 0
    fields_of_study: List[str] = []
    is_open_access: bool = False
    open_access_pdf_url: Optional[str] = None


class SemanticScholarProvider(BaseProvider):
    """
    Fetches citation and metadata from Semantic Scholar.

    Features:
    - Direct arXiv ID lookup
    - Citation count and references
    - Influential citation count
    - Fields of study

    Rate Limits (without API key):
    - 100 requests per 5 minutes
    - 1 request per second recommended
    """

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    # Default fields to fetch for papers
    PAPER_FIELDS = [
        "paperId",
        "externalIds",
        "title",
        "abstract",
        "venue",
        "year",
        "publicationDate",
        "citationCount",
        "referenceCount",
        "influentialCitationCount",
        "fieldsOfStudy",
        "isOpenAccess",
        "openAccessPdf",
        "authors",
        "authors.name",
        "authors.authorId",
    ]

    # Additional fields when fetching references/citations
    REFERENCE_FIELDS = [
        "paperId",
        "externalIds",
        "title",
        "year",
        "citationCount",
    ]

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        self._client: Optional[httpx.AsyncClient] = None
        self._api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self._last_request_time = 0.0
        # Public rate limit: 100 req/5min officially, but they have strict burst limits
        # Testing shows 429 errors even with 6s delay - need 30s+ for reliable operation
        self._request_delay = 30.0
        self._consecutive_successes = 0
        self._backoff_multiplier = 1.0

        if self._api_key:
            self.log_info("Semantic Scholar API key configured")
            self._request_delay = 0.5  # Much faster with API key
        else:
            self.log_info("Semantic Scholar using public rate limits (30s delay for reliability)")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None or self._client.is_closed:
            headers = {"Accept": "application/json"}
            if self._api_key:
                headers["x-api-key"] = self._api_key

            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=headers,
                timeout=30.0
            )
        return self._client

    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _rate_limit(self):
        """Enforce rate limiting between requests"""
        import time
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._request_delay:
            await asyncio.sleep(self._request_delay - elapsed)
        self._last_request_time = time.time()

    async def get_paper_by_arxiv_id(self, arxiv_id: str) -> Optional[SemanticScholarPaper]:
        """
        Get paper data by arXiv ID.

        Args:
            arxiv_id: arXiv paper ID (e.g., "2106.09685" or "2106.09685v1")

        Returns:
            SemanticScholarPaper with metadata, or None if not found
        """
        # Normalize ID (remove version suffix)
        clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

        try:
            await self._rate_limit()
            client = await self._get_client()

            # Semantic Scholar uses arXiv:{id} format
            fields_str = ",".join(self.PAPER_FIELDS)
            response = await client.get(
                f"/paper/arXiv:{clean_id}",
                params={"fields": fields_str}
            )

            if response.status_code == 404:
                self.log_debug(f"Paper not found in Semantic Scholar: arXiv:{clean_id}")
                return None

            response.raise_for_status()
            data = response.json()

            return self._parse_paper(data, arxiv_id)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                self.log_warning("Semantic Scholar rate limit hit, backing off")
                await asyncio.sleep(60)  # Back off for a minute
            elif e.response.status_code != 404:
                self.log_error(f"Semantic Scholar API error: {e.response.status_code}")
            return None
        except Exception as e:
            self.log_error("Semantic Scholar request failed", error=str(e))
            return None

    async def get_citation_count(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Get just citation count for a paper (minimal API call).

        Args:
            arxiv_id: arXiv paper ID

        Returns:
            Dict with citation data or None
        """
        clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

        try:
            await self._rate_limit()
            client = await self._get_client()

            response = await client.get(
                f"/paper/arXiv:{clean_id}",
                params={"fields": "paperId,title,citationCount,influentialCitationCount,year"}
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

            return {
                "paper_id": arxiv_id,
                "semantic_scholar_id": data.get("paperId"),
                "title": data.get("title"),
                "citation_count": data.get("citationCount", 0),
                "influential_citation_count": data.get("influentialCitationCount", 0),
                "year": data.get("year"),
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                self.log_warning("Rate limit hit, backing off 120s")
                await asyncio.sleep(120)  # Back off longer
                import time
                self._last_request_time = time.time()  # Reset timer after backoff
            return None
        except Exception as e:
            self.log_error("Request failed", error=str(e))
            return None

    async def batch_get_citations(
        self,
        arxiv_ids: List[str],
        concurrency: int = 1,  # Keep low to avoid rate limits
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Get citation counts for multiple papers.

        Uses batch endpoint if available, otherwise sequential requests.

        Args:
            arxiv_ids: List of arXiv IDs
            concurrency: Max concurrent requests (default 1 for rate limits)

        Returns:
            Dict mapping arxiv_id to citation data
        """
        results = {}

        # Process sequentially to respect rate limits
        for arxiv_id in arxiv_ids:
            data = await self.get_citation_count(arxiv_id)
            results[arxiv_id] = data

            if data:
                self.log_debug(
                    f"Got citations for {arxiv_id}",
                    citations=data.get("citation_count", 0)
                )

        return results

    async def get_paper_references(
        self,
        arxiv_id: str,
        limit: int = 50
    ) -> List[SemanticScholarPaper]:
        """
        Get papers that this paper cites (its references).

        Args:
            arxiv_id: arXiv paper ID
            limit: Max references to return

        Returns:
            List of referenced papers
        """
        clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

        try:
            await self._rate_limit()
            client = await self._get_client()

            fields_str = ",".join(self.REFERENCE_FIELDS)
            response = await client.get(
                f"/paper/arXiv:{clean_id}/references",
                params={"fields": fields_str, "limit": min(limit, 1000)}
            )

            if response.status_code == 404:
                return []

            response.raise_for_status()
            data = response.json()

            papers = []
            for ref in data.get("data", []):
                cited_paper = ref.get("citedPaper")
                if cited_paper and cited_paper.get("paperId"):
                    papers.append(self._parse_paper(cited_paper))

            return papers

        except Exception as e:
            self.log_error("Failed to get references", error=str(e))
            return []

    async def get_paper_citations(
        self,
        arxiv_id: str,
        limit: int = 50
    ) -> List[SemanticScholarPaper]:
        """
        Get papers that cite this paper.

        Args:
            arxiv_id: arXiv paper ID
            limit: Max citations to return

        Returns:
            List of citing papers
        """
        clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

        try:
            await self._rate_limit()
            client = await self._get_client()

            fields_str = ",".join(self.REFERENCE_FIELDS)
            response = await client.get(
                f"/paper/arXiv:{clean_id}/citations",
                params={"fields": fields_str, "limit": min(limit, 1000)}
            )

            if response.status_code == 404:
                return []

            response.raise_for_status()
            data = response.json()

            papers = []
            for cit in data.get("data", []):
                citing_paper = cit.get("citingPaper")
                if citing_paper and citing_paper.get("paperId"):
                    papers.append(self._parse_paper(citing_paper))

            return papers

        except Exception as e:
            self.log_error("Failed to get citations", error=str(e))
            return []

    def _parse_paper(
        self,
        data: Dict[str, Any],
        arxiv_id: Optional[str] = None
    ) -> SemanticScholarPaper:
        """Parse Semantic Scholar API response into model"""

        # Extract external IDs
        external_ids = data.get("externalIds", {}) or {}
        parsed_arxiv_id = arxiv_id or external_ids.get("ArXiv")
        doi = external_ids.get("DOI")

        # Parse authors
        authors = []
        for author in data.get("authors", []):
            authors.append({
                "name": author.get("name", "Unknown"),
                "semantic_scholar_id": author.get("authorId"),
            })

        # Parse open access info
        is_oa = data.get("isOpenAccess", False)
        oa_pdf = None
        if data.get("openAccessPdf"):
            oa_pdf = data["openAccessPdf"].get("url")

        return SemanticScholarPaper(
            semantic_scholar_id=data.get("paperId", ""),
            arxiv_id=parsed_arxiv_id,
            doi=doi,
            title=data.get("title", "Untitled"),
            abstract=data.get("abstract"),
            venue=data.get("venue"),
            year=data.get("year"),
            publication_date=data.get("publicationDate"),
            cited_by_count=data.get("citationCount", 0),
            reference_count=data.get("referenceCount", 0),
            influential_citation_count=data.get("influentialCitationCount", 0),
            fields_of_study=data.get("fieldsOfStudy") or [],
            authors=authors,
            is_open_access=is_oa,
            open_access_pdf_url=oa_pdf,
        )


# Module-level singleton
_semantic_scholar_provider: Optional[SemanticScholarProvider] = None


def get_semantic_scholar_provider() -> SemanticScholarProvider:
    """Get or create Semantic Scholar provider singleton"""
    global _semantic_scholar_provider
    if _semantic_scholar_provider is None:
        _semantic_scholar_provider = SemanticScholarProvider()
    return _semantic_scholar_provider
