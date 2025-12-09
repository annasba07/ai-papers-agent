"""
OpenAlex Provider - Citation and metadata enrichment

OpenAlex is a free, open catalog of the global research system.
- 250M+ works indexed
- No API key required (optional email for higher rate limits)
- Provides: citations, references, authors, concepts, institutions

API Docs: https://docs.openalex.org/
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Sequence, Dict, Any, List, Optional

import httpx
from pydantic import BaseModel

from app.schemas.research_graph import TechniqueUpsert
from app.core.config import settings
from .base import BaseProvider


class OpenAlexWork(BaseModel):
    """Parsed work data from OpenAlex"""
    openalex_id: str
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    title: str
    publication_date: Optional[str] = None
    cited_by_count: int = 0
    references_count: int = 0
    reference_ids: List[str] = []
    concepts: List[Dict[str, Any]] = []
    authors: List[Dict[str, Any]] = []
    abstract: Optional[str] = None
    is_open_access: bool = False


class CitationInfo(BaseModel):
    """Citation data for a paper"""
    paper_id: str
    cited_by_count: int
    references_count: int
    reference_ids: List[str] = []
    openalex_id: Optional[str] = None
    concepts: List[Dict[str, Any]] = []


class OpenAlexProvider(BaseProvider):
    """
    Fetches citation, author, organisation, and topic metadata from OpenAlex.

    Rate Limits:
    - Without email: 100K requests/day, 10/second
    - With email (polite pool): Higher limits
    """

    BASE_URL = "https://api.openalex.org"

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        self._client: Optional[httpx.AsyncClient] = None
        # Use email for polite pool if configured
        self._email = getattr(settings, 'OPENALEX_EMAIL', None)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None or self._client.is_closed:
            params = {}
            if self._email:
                params["mailto"] = self._email

            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={"Accept": "application/json"},
                params=params,
                timeout=30.0
            )
        return self._client

    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_work_by_arxiv_id(self, arxiv_id: str, title: Optional[str] = None) -> Optional[OpenAlexWork]:
        """
        Get work data by arXiv ID using location-based search.

        The OpenAlex API no longer supports ids.arxiv filter, so we use
        primary_location.landing_page_url or title search as fallback.

        Args:
            arxiv_id: arXiv paper ID (e.g., "2106.09685")
            title: Optional title for more accurate matching

        Returns:
            OpenAlexWork with metadata, or None if not found
        """
        # Normalize ID (remove version suffix)
        clean_id = arxiv_id.split("v")[0]

        try:
            client = await self._get_client()

            # Strategy 1: Search by arXiv URL in locations
            # OpenAlex indexes arxiv papers with their URL in locations
            arxiv_url = f"https://arxiv.org/abs/{clean_id}"
            response = await client.get(
                "/works",
                params={
                    "filter": f"locations.landing_page_url:{arxiv_url}",
                    "per_page": 1
                }
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if results:
                return self._parse_work(results[0], arxiv_id)

            # Strategy 2: Try with indexed_in:arxiv filter and arXiv ID in title/search
            response = await client.get(
                "/works",
                params={
                    "filter": "indexed_in:arxiv",
                    "search": clean_id,
                    "per_page": 5
                }
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            for result in results:
                # Check if arXiv ID appears in any location URL
                locations = result.get("locations", [])
                for loc in locations:
                    landing_page = loc.get("landing_page_url", "") or ""
                    if clean_id in landing_page:
                        return self._parse_work(result, arxiv_id)

            # Strategy 3: If title provided, search by title within arxiv-indexed works
            if title:
                # Clean title for search
                search_title = title[:100].replace('"', '')
                response = await client.get(
                    "/works",
                    params={
                        "filter": "indexed_in:arxiv",
                        "search": search_title,
                        "per_page": 5
                    }
                )
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                if results:
                    # Return the top result (highest relevance)
                    return self._parse_work(results[0], arxiv_id)

            self.log_debug(f"No OpenAlex record for arXiv:{clean_id}")
            return None

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                self.log_warning("OpenAlex rate limit exceeded")
            else:
                self.log_error(f"OpenAlex API error: {e.response.status_code}")
            return None
        except Exception as e:
            self.log_error("OpenAlex request failed", error=str(e))
            return None

    async def fetch_citation_edges(self, paper_ids: Sequence[str]) -> List[Dict[str, Any]]:
        """
        Return citation edges for the supplied paper IDs.

        Returns list of:
        {
            "source_id": "arxiv_id",
            "target_id": "openalex_work_id",
            "edge_type": "cites"
        }
        """
        if not paper_ids:
            return []

        self.log_info("Fetching citation edges from OpenAlex", paper_count=len(paper_ids))

        edges = []
        # Process in batches to avoid rate limits
        batch_size = 5

        for i in range(0, len(paper_ids), batch_size):
            batch = paper_ids[i:i + batch_size]
            tasks = [self.get_work_by_arxiv_id(pid) for pid in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for paper_id, result in zip(batch, results):
                if isinstance(result, Exception):
                    self.log_warning(f"Failed to fetch {paper_id}", error=str(result))
                    continue
                if result is None:
                    continue

                # Create edges for each reference
                for ref_id in result.reference_ids:
                    edges.append({
                        "source_id": paper_id,
                        "target_id": ref_id,
                        "edge_type": "cites"
                    })

            # Small delay between batches
            if i + batch_size < len(paper_ids):
                await asyncio.sleep(0.1)

        self.log_info("Fetched citation edges", edge_count=len(edges))
        return edges

    async def get_citation_info(self, arxiv_id: str) -> Optional[CitationInfo]:
        """
        Get citation counts and references for a paper.

        Args:
            arxiv_id: arXiv paper ID

        Returns:
            CitationInfo with counts and reference IDs
        """
        work = await self.get_work_by_arxiv_id(arxiv_id)
        if not work:
            return None

        return CitationInfo(
            paper_id=arxiv_id,
            cited_by_count=work.cited_by_count,
            references_count=work.references_count,
            reference_ids=work.reference_ids,
            openalex_id=work.openalex_id,
            concepts=work.concepts
        )

    async def batch_get_citations(
        self,
        arxiv_ids: List[str],
        concurrency: int = 5
    ) -> Dict[str, Optional[CitationInfo]]:
        """
        Get citation data for multiple papers efficiently.

        Args:
            arxiv_ids: List of arXiv IDs
            concurrency: Max concurrent requests

        Returns:
            Dict mapping arxiv_id to CitationInfo
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def fetch_one(arxiv_id: str) -> tuple:
            async with semaphore:
                data = await self.get_citation_info(arxiv_id)
                await asyncio.sleep(0.05)  # Respect rate limits
                return arxiv_id, data

        tasks = [fetch_one(aid) for aid in arxiv_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {}
        for result in results:
            if isinstance(result, Exception):
                continue
            arxiv_id, data = result
            output[arxiv_id] = data

        return output

    async def get_citing_papers(
        self,
        arxiv_id: str,
        limit: int = 25
    ) -> List[OpenAlexWork]:
        """
        Get papers that cite this paper.

        Args:
            arxiv_id: arXiv paper ID
            limit: Max papers to return

        Returns:
            List of citing papers
        """
        work = await self.get_work_by_arxiv_id(arxiv_id)
        if not work:
            return []

        try:
            client = await self._get_client()
            response = await client.get(
                "/works",
                params={
                    "filter": f"cites:{work.openalex_id}",
                    "sort": "cited_by_count:desc",
                    "per_page": min(limit, 100)
                }
            )
            response.raise_for_status()
            data = response.json()

            return [self._parse_work(w) for w in data.get("results", [])]

        except Exception as e:
            self.log_error("Failed to get citing papers", error=str(e))
            return []

    async def get_references(
        self,
        arxiv_id: str,
        limit: int = 50
    ) -> List[OpenAlexWork]:
        """
        Get papers that this paper references.

        Args:
            arxiv_id: arXiv paper ID
            limit: Max papers to return

        Returns:
            List of referenced papers
        """
        work = await self.get_work_by_arxiv_id(arxiv_id)
        if not work or not work.reference_ids:
            return []

        try:
            client = await self._get_client()
            ref_ids = work.reference_ids[:limit]
            ref_ids_str = "|".join(ref_ids)

            response = await client.get(
                "/works",
                params={
                    "filter": f"ids.openalex:{ref_ids_str}",
                    "per_page": limit
                }
            )
            response.raise_for_status()
            data = response.json()

            return [self._parse_work(w) for w in data.get("results", [])]

        except Exception as e:
            self.log_error("Failed to get references", error=str(e))
            return []

    async def fetch_authors_and_affiliations(
        self,
        paper_ids: Sequence[str]
    ) -> List[Dict[str, Any]]:
        """
        Return author records enriched with affiliation data.
        """
        if not paper_ids:
            return []

        self.log_info("Fetching authors from OpenAlex", paper_count=len(paper_ids))

        results = []
        batch_size = 5

        for i in range(0, len(paper_ids), batch_size):
            batch = paper_ids[i:i + batch_size]
            tasks = [self.get_work_by_arxiv_id(pid) for pid in batch]
            works = await asyncio.gather(*tasks, return_exceptions=True)

            for paper_id, work in zip(batch, works):
                if isinstance(work, Exception) or work is None:
                    continue

                authors_data = []
                for idx, author in enumerate(work.authors):
                    author_record = {
                        "full_name": author.get("name", "Unknown"),
                        "normalized_name": author.get("name", "").lower().replace(" ", "_"),
                        "orcid": author.get("orcid"),
                        "homepage": None,
                        "author_order": idx + 1,
                        "is_corresponding": idx == 0  # Assume first author
                    }

                    if author.get("institution"):
                        author_record["primary_affiliation"] = {
                            "name": author["institution"],
                            "kind": "university",
                            "region": None,
                            "homepage": None
                        }

                    authors_data.append(author_record)

                results.append({
                    "paper_id": paper_id,
                    "authors": authors_data
                })

            if i + batch_size < len(paper_ids):
                await asyncio.sleep(0.1)

        self.log_info("Fetched author data", paper_count=len(results))
        return results

    async def fetch_related_techniques(
        self,
        paper_ids: Sequence[str]
    ) -> List[TechniqueUpsert]:
        """
        Return technique descriptors inferred from OpenAlex concepts.
        """
        if not paper_ids:
            return []

        self.log_info("Extracting techniques from OpenAlex concepts", paper_count=len(paper_ids))

        techniques_map: Dict[str, TechniqueUpsert] = {}

        for paper_id in paper_ids:
            work = await self.get_work_by_arxiv_id(paper_id)
            if not work:
                continue

            for concept in work.concepts:
                name = concept.get("name", "")
                if not name or concept.get("level", 0) < 2:
                    # Skip very broad concepts
                    continue

                normalized = name.lower().replace(" ", "_").replace("-", "_")

                if normalized not in techniques_map:
                    techniques_map[normalized] = TechniqueUpsert(
                        name=name,
                        normalized_name=normalized,
                        method_type=self._infer_method_type(name),
                        maturity_score=min(concept.get("score", 0.5) * 10, 10.0),
                        description=None,
                        evidence_source="openalex"
                    )

        return list(techniques_map.values())

    def _parse_work(self, work: Dict[str, Any], arxiv_id: Optional[str] = None) -> OpenAlexWork:
        """Parse OpenAlex API response into OpenAlexWork model"""

        # Parse authors
        authors = []
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            institutions = authorship.get("institutions", [])

            authors.append({
                "name": author.get("display_name", "Unknown"),
                "openalex_id": author.get("id"),
                "orcid": author.get("orcid"),
                "institution": institutions[0].get("display_name") if institutions else None
            })

        # Parse concepts
        concepts = []
        for concept in work.get("concepts", []):
            concepts.append({
                "name": concept.get("display_name", ""),
                "score": concept.get("score", 0.0),
                "level": concept.get("level", 0),
                "openalex_id": concept.get("id")
            })
        concepts.sort(key=lambda c: c["score"], reverse=True)

        # Parse references
        references = work.get("referenced_works", [])

        # Extract arxiv ID if not provided
        if not arxiv_id:
            ids = work.get("ids", {})
            arxiv_id = ids.get("arxiv", "").replace("https://arxiv.org/abs/", "")

        return OpenAlexWork(
            openalex_id=work.get("id", ""),
            arxiv_id=arxiv_id,
            doi=work.get("doi", "").replace("https://doi.org/", "") if work.get("doi") else None,
            title=work.get("title", "Untitled"),
            publication_date=work.get("publication_date"),
            cited_by_count=work.get("cited_by_count", 0),
            references_count=len(references),
            reference_ids=references,
            concepts=concepts[:10],
            authors=authors,
            abstract=self._reconstruct_abstract(work.get("abstract_inverted_index")),
            is_open_access=work.get("open_access", {}).get("is_oa", False)
        )

    def _reconstruct_abstract(self, inverted_index: Optional[Dict]) -> Optional[str]:
        """Reconstruct abstract from OpenAlex's inverted index format"""
        if not inverted_index:
            return None

        try:
            words_with_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    words_with_positions.append((pos, word))

            words_with_positions.sort(key=lambda x: x[0])
            return " ".join(word for _, word in words_with_positions)
        except Exception:
            return None

    def _infer_method_type(self, concept_name: str) -> Optional[str]:
        """Infer method type from concept name"""
        name_lower = concept_name.lower()

        if any(kw in name_lower for kw in ["transformer", "attention"]):
            return "transformer"
        elif any(kw in name_lower for kw in ["diffusion", "score matching"]):
            return "diffusion"
        elif any(kw in name_lower for kw in ["cnn", "convolution"]):
            return "convolutional"
        elif any(kw in name_lower for kw in ["rnn", "lstm", "gru", "recurrent"]):
            return "recurrent"
        elif any(kw in name_lower for kw in ["gan", "generative adversarial"]):
            return "generative"
        elif any(kw in name_lower for kw in ["reinforcement", "rl", "policy"]):
            return "reinforcement_learning"

        return None


# Module-level singleton
_openalex_provider: Optional[OpenAlexProvider] = None


def get_openalex_provider() -> OpenAlexProvider:
    """Get or create OpenAlex provider singleton"""
    global _openalex_provider
    if _openalex_provider is None:
        _openalex_provider = OpenAlexProvider()
    return _openalex_provider
