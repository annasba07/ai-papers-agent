"""
Adapter for the OpenAlex API (https://docs.openalex.org/)

At this stage we only define the contract and logging. Actual HTTP calls,
pagination, and error handling will be layered in future iterations.
"""
from __future__ import annotations

from typing import Sequence, Dict, Any, List

from app.schemas.research_graph import TechniqueUpsert
from .base import BaseProvider


class OpenAlexProvider(BaseProvider):
    """
    Fetches citation, author, organisation, and topic metadata from OpenAlex.
    """

    async def fetch_citation_edges(self, paper_ids: Sequence[str]) -> List[Dict[str, Any]]:
        """
        Return citation edges for the supplied paper IDs.

        Each edge should match the shape required by app.db.models.Citation.
        """
        if not paper_ids:
            return []

        self.log_debug("OpenAlex citation fetch (stub)", paper_count=len(paper_ids))
        return []

    async def fetch_authors_and_affiliations(
        self,
        paper_ids: Sequence[str]
    ) -> List[Dict[str, Any]]:
        """
        Return author records enriched with affiliation data.

        Contract:
        [
            {
                "paper_id": "...",
                "authors": [
                    {
                        "full_name": "...",
                        "normalized_name": "...",
                        "orcid": "...",
                        "homepage": "...",
                        "primary_affiliation": {
                            "name": "...",
                            "kind": "...",
                            "region": "...",
                            "homepage": "..."
                        },
                        "author_order": 1,
                        "is_corresponding": false
                    },
                    ...
                ]
            }
        ]
        """
        if not paper_ids:
            return []

        self.log_debug("OpenAlex author fetch (stub)", paper_count=len(paper_ids))
        return []

    async def fetch_related_techniques(
        self,
        paper_ids: Sequence[str]
    ) -> List[TechniqueUpsert]:
        """
        Return technique descriptors inferred from OpenAlex concepts.
        """
        if not paper_ids:
            return []

        self.log_debug("OpenAlex technique fetch (stub)", paper_count=len(paper_ids))
        return []
