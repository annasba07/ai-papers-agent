"""
Adapter for Papers With Code (https://paperswithcode.com/api)

Responsible for surfacing benchmark metrics, tasks, datasets, and
technique aliases referenced in SOTA tables.
"""
from __future__ import annotations

from typing import Sequence, List

from app.schemas.research_graph import (
    BenchmarkObservation,
    TaskUpsert,
    DatasetUpsert,
    TechniqueUpsert,
)
from .base import BaseProvider


class PapersWithCodeProvider(BaseProvider):
    """
    Fetches benchmark data and taxonomy mappings from Papers With Code.
    """

    async def fetch_benchmark_observations(
        self,
        paper_ids: Sequence[str]
    ) -> List[BenchmarkObservation]:
        if not paper_ids:
            return []

        self.log_debug("PWC benchmark fetch (stub)", paper_count=len(paper_ids))
        return []

    async def fetch_taxonomy_entities(self) -> dict:
        """
        Return canonical lists of tasks, datasets, and techniques present in PWC.

        Expected shape:
        {
            "tasks": List[TaskUpsert],
            "datasets": List[DatasetUpsert],
            "techniques": List[TechniqueUpsert]
        }
        """
        self.log_debug("PWC taxonomy fetch (stub)")
        return {
            "tasks": [],
            "datasets": [],
            "techniques": [],
        }
