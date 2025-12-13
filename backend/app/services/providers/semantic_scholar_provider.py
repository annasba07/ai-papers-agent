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
            self._request_delay = 1.1  # API key allows 1 req/sec, add buffer for safety
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
        Get citation counts for multiple papers using the batch endpoint.

        Uses POST /paper/batch to fetch up to 500 papers per request,
        dramatically more efficient than individual lookups.

        Args:
            arxiv_ids: List of arXiv IDs
            concurrency: Ignored (kept for API compatibility)

        Returns:
            Dict mapping arxiv_id to citation data
        """
        results = {}
        batch_size = 500  # Semantic Scholar max batch size

        # Clean IDs and prepare batches
        cleaned_ids = []
        id_mapping = {}  # Map cleaned ID to original
        for arxiv_id in arxiv_ids:
            clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
            cleaned_ids.append(clean_id)
            id_mapping[clean_id] = arxiv_id

        # Process in batches
        for i in range(0, len(cleaned_ids), batch_size):
            batch = cleaned_ids[i:i + batch_size]
            batch_results = await self._fetch_batch_citations(batch)

            # Map results back to original IDs
            for clean_id, data in batch_results.items():
                original_id = id_mapping.get(clean_id, clean_id)
                results[original_id] = data

            self.log_info(
                f"Batch {i//batch_size + 1}: fetched {len(batch_results)} papers"
            )

        return results

    async def _fetch_batch_citations(
        self,
        arxiv_ids: List[str],
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Fetch citations for a batch of papers using POST /paper/batch.

        Args:
            arxiv_ids: List of clean arXiv IDs (no version suffix)

        Returns:
            Dict mapping arxiv_id to citation data
        """
        results = {}

        try:
            await self._rate_limit()
            client = await self._get_client()

            # Format IDs for batch endpoint (arXiv:{id} format)
            paper_ids = [f"arXiv:{aid}" for aid in arxiv_ids]

            response = await client.post(
                "/paper/batch",
                params={"fields": "paperId,externalIds,title,citationCount,influentialCitationCount,year"},
                json={"ids": paper_ids}
            )

            if response.status_code == 429:
                self.log_warning("Rate limit hit on batch endpoint, backing off 120s")
                await asyncio.sleep(120)
                import time
                self._last_request_time = time.time()
                return results

            response.raise_for_status()
            data = response.json()

            # Process results - API returns list in same order as input
            for idx, paper_data in enumerate(data):
                arxiv_id = arxiv_ids[idx] if idx < len(arxiv_ids) else None

                if paper_data is None:
                    # Paper not found in Semantic Scholar
                    if arxiv_id:
                        results[arxiv_id] = None
                    continue

                # Extract arXiv ID from external IDs if available
                external_ids = paper_data.get("externalIds", {}) or {}
                found_arxiv_id = external_ids.get("ArXiv") or arxiv_id

                if found_arxiv_id:
                    results[found_arxiv_id] = {
                        "paper_id": found_arxiv_id,
                        "semantic_scholar_id": paper_data.get("paperId"),
                        "title": paper_data.get("title"),
                        "citation_count": paper_data.get("citationCount", 0),
                        "influential_citation_count": paper_data.get("influentialCitationCount", 0),
                        "year": paper_data.get("year"),
                    }

            return results

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                self.log_warning("Rate limit hit, backing off 120s")
                await asyncio.sleep(120)
            else:
                self.log_error(f"Batch API error: {e.response.status_code}")
            return results
        except Exception as e:
            self.log_error("Batch request failed", error=str(e))
            return results

    async def batch_get_references(
        self,
        arxiv_ids: List[str],
        max_refs_per_paper: int = 100,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get references for multiple papers using the batch endpoint.

        Uses POST /paper/batch with references field to fetch up to 500 papers
        per request. Each paper returns up to max_refs_per_paper references.

        This is MUCH more efficient than individual /references calls:
        - Individual: 2000 papers = 2000 API calls
        - Batch: 2000 papers = 4 API calls (500 per batch)

        Args:
            arxiv_ids: List of arXiv IDs
            max_refs_per_paper: Max references per paper (Semantic Scholar caps this)

        Returns:
            Dict mapping arxiv_id to list of reference dicts with arXiv IDs
        """
        results = {}
        batch_size = 500  # Semantic Scholar max batch size

        # Clean IDs and prepare mapping
        cleaned_ids = []
        id_mapping = {}
        for arxiv_id in arxiv_ids:
            clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
            cleaned_ids.append(clean_id)
            id_mapping[clean_id] = arxiv_id

        # Process in batches
        for i in range(0, len(cleaned_ids), batch_size):
            batch = cleaned_ids[i:i + batch_size]
            batch_results = await self._fetch_batch_references(batch)

            # Map results back to original IDs
            for clean_id, refs in batch_results.items():
                original_id = id_mapping.get(clean_id, clean_id)
                results[original_id] = refs

            self.log_info(
                f"Batch refs {i//batch_size + 1}: fetched {len(batch_results)} papers"
            )

        return results

    async def _fetch_batch_references(
        self,
        arxiv_ids: List[str],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch references for a batch of papers using POST /paper/batch.

        Args:
            arxiv_ids: List of clean arXiv IDs (no version suffix)

        Returns:
            Dict mapping arxiv_id to list of reference info dicts
        """
        results = {}
        max_retries = 3

        for attempt in range(max_retries):
            try:
                await self._rate_limit()
                client = await self._get_client()

                # Format IDs for batch endpoint
                paper_ids = [f"arXiv:{aid}" for aid in arxiv_ids]

                # Request references.externalIds to get arXiv IDs of referenced papers
                response = await client.post(
                    "/paper/batch",
                    params={"fields": "paperId,externalIds,references,references.externalIds,references.title"},
                    json={"ids": paper_ids}
                )

                if response.status_code == 429:
                    wait_time = 30 * (2 ** attempt)
                    self.log_warning(f"Rate limit on batch refs, backing off {wait_time}s (attempt {attempt+1})")
                    await asyncio.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = response.json()

                # Process results
                for idx, paper_data in enumerate(data):
                    arxiv_id = arxiv_ids[idx] if idx < len(arxiv_ids) else None

                    if paper_data is None or arxiv_id is None:
                        if arxiv_id:
                            results[arxiv_id] = []
                        continue

                    # Extract references with arXiv IDs
                    refs = []
                    for ref in paper_data.get("references", []) or []:
                        if ref is None:
                            continue
                        external_ids = ref.get("externalIds", {}) or {}
                        ref_arxiv = external_ids.get("ArXiv")
                        if ref_arxiv:
                            refs.append({
                                "arxiv_id": ref_arxiv,
                                "title": ref.get("title"),
                                "paper_id": ref.get("paperId"),
                            })

                    # Also check source paper's arXiv ID
                    source_external = paper_data.get("externalIds", {}) or {}
                    source_arxiv = source_external.get("ArXiv") or arxiv_id
                    results[source_arxiv] = refs

                return results

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = 30 * (2 ** attempt)
                    self.log_warning(f"Rate limit (exception), backing off {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                self.log_error(f"Batch refs API error: {e.response.status_code}")
                return results
            except Exception as e:
                self.log_error("Batch refs request failed", error=str(e))
                return results

        return results

    async def batch_get_paper_details(
        self,
        arxiv_ids: List[str],
        fields: List[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get paper details for multiple papers using the batch endpoint.

        Uses POST /paper/batch to fetch details for up to 500 papers per request.

        Args:
            arxiv_ids: List of arXiv IDs
            fields: List of fields to request (default: citationCount, referenceCount)

        Returns:
            Dict mapping arxiv_id to dict of requested fields
        """
        if fields is None:
            fields = ["citationCount", "referenceCount"]

        results = {}
        batch_size = 500

        # Clean IDs and prepare mapping
        cleaned_ids = []
        id_mapping = {}
        for arxiv_id in arxiv_ids:
            clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
            cleaned_ids.append(clean_id)
            id_mapping[clean_id] = arxiv_id

        # Process in batches
        for i in range(0, len(cleaned_ids), batch_size):
            batch = cleaned_ids[i:i + batch_size]
            max_retries = 3

            for attempt in range(max_retries):
                try:
                    await self._rate_limit()
                    client = await self._get_client()

                    paper_ids = [f"arXiv:{aid}" for aid in batch]
                    fields_str = ",".join(fields)

                    response = await client.post(
                        "/paper/batch",
                        params={"fields": fields_str},
                        json={"ids": paper_ids}
                    )

                    if response.status_code == 429:
                        wait_time = 30 * (2 ** attempt)
                        self.log_warning(f"Rate limit on batch details, backing off {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue

                    response.raise_for_status()
                    data = response.json()

                    # Process results
                    for idx, paper in enumerate(data):
                        if paper is None:
                            continue
                        clean_id = batch[idx]
                        original_id = id_mapping.get(clean_id, clean_id)
                        results[original_id] = paper

                    self.log_info(f"Batch details {i//batch_size + 1}: fetched {len([p for p in data if p])} papers")
                    break

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and attempt < max_retries - 1:
                        wait_time = 30 * (2 ** attempt)
                        await asyncio.sleep(wait_time)
                        continue
                    self.log_error(f"Batch details API error: {e.response.status_code}")
                    break
                except Exception as e:
                    self.log_error("Batch details request failed", error=str(e))
                    break

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
        limit: int = 50,
        max_retries: int = 3
    ) -> List[SemanticScholarPaper]:
        """
        Get papers that cite this paper.

        Args:
            arxiv_id: arXiv paper ID
            limit: Max citations to return
            max_retries: Max retries for rate limit errors

        Returns:
            List of citing papers
        """
        clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

        for attempt in range(max_retries):
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

                if response.status_code == 429:
                    # Exponential backoff: 5s, 10s, 20s
                    wait_time = 5 * (2 ** attempt)
                    self.log_warning(f"Rate limit hit, backing off {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = response.json()

                papers = []
                for cit in data.get("data", []):
                    citing_paper = cit.get("citingPaper")
                    if citing_paper and citing_paper.get("paperId"):
                        papers.append(self._parse_paper(citing_paper))

                return papers

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = 5 * (2 ** attempt)
                    self.log_warning(f"Rate limit hit (exception), backing off {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                self.log_error("Failed to get citations", error=str(e))
                return []
            except Exception as e:
                self.log_error("Failed to get citations", error=str(e))
                return []

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
