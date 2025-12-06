"""
Papers With Code Provider - Benchmark and code repository data

Papers With Code is a free resource with:
- Paper → Code repository mappings
- Benchmark results (SOTA tracking)
- Task/method taxonomies
- Dataset information

API Docs: https://paperswithcode.com/api/v1/docs/
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Sequence, List, Dict, Any, Optional

import httpx
from pydantic import BaseModel

from app.schemas.research_graph import (
    BenchmarkObservation,
    TaskUpsert,
    DatasetUpsert,
    TechniqueUpsert,
)
from .base import BaseProvider


class PWCPaper(BaseModel):
    """Paper data from Papers With Code"""
    pwc_id: str
    arxiv_id: Optional[str] = None
    title: str
    abstract: Optional[str] = None
    url_abs: Optional[str] = None
    url_pdf: Optional[str] = None
    published: Optional[str] = None
    authors: List[str] = []
    tasks: List[str] = []
    methods: List[str] = []


class PWCRepository(BaseModel):
    """Code repository from Papers With Code"""
    url: str
    owner: str
    name: str
    stars: int = 0
    framework: Optional[str] = None
    is_official: bool = False
    description: Optional[str] = None


class PWCResult(BaseModel):
    """Benchmark result from Papers With Code"""
    task: str
    dataset: str
    metric: str
    value: float
    model_name: Optional[str] = None
    paper_title: Optional[str] = None
    paper_arxiv_id: Optional[str] = None


class PapersWithCodeProvider(BaseProvider):
    """
    Fetches benchmark data and taxonomy mappings from Papers With Code.

    Features:
    - Paper → Code repository mappings
    - Benchmark results and SOTA tracking
    - Task/method/dataset taxonomies
    """

    BASE_URL = "https://paperswithcode.com/api/v1"

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={"Accept": "application/json"},
                timeout=30.0
            )
        return self._client

    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_paper_by_arxiv_id(self, arxiv_id: str) -> Optional[PWCPaper]:
        """
        Get paper data by arXiv ID.

        Args:
            arxiv_id: arXiv paper ID (e.g., "2106.09685")

        Returns:
            PWCPaper with metadata, or None if not found
        """
        clean_id = arxiv_id.split("v")[0]

        try:
            client = await self._get_client()
            response = await client.get(f"/papers/{clean_id}/")
            response.raise_for_status()
            data = response.json()

            return PWCPaper(
                pwc_id=data.get("id", ""),
                arxiv_id=data.get("arxiv_id"),
                title=data.get("title", ""),
                abstract=data.get("abstract"),
                url_abs=data.get("url_abs"),
                url_pdf=data.get("url_pdf"),
                published=data.get("published"),
                authors=data.get("authors", []),
                tasks=[t.get("task", "") for t in data.get("tasks", [])],
                methods=[m.get("name", "") for m in data.get("methods", [])]
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                self.log_debug(f"No PWC record for arXiv:{clean_id}")
            else:
                self.log_error(f"PWC API error: {e.response.status_code}")
            return None
        except Exception as e:
            self.log_error("PWC request failed", error=str(e))
            return None

    async def get_repositories(self, arxiv_id: str) -> List[PWCRepository]:
        """
        Get code repositories for a paper.

        Args:
            arxiv_id: arXiv paper ID

        Returns:
            List of code repositories
        """
        clean_id = arxiv_id.split("v")[0]

        try:
            client = await self._get_client()
            response = await client.get(f"/papers/{clean_id}/repositories/")
            response.raise_for_status()
            data = response.json()

            repos = []
            for repo in data.get("results", data if isinstance(data, list) else []):
                repos.append(PWCRepository(
                    url=repo.get("url", ""),
                    owner=repo.get("owner", ""),
                    name=repo.get("name", ""),
                    stars=repo.get("stars", 0),
                    framework=repo.get("framework"),
                    is_official=repo.get("is_official", False),
                    description=repo.get("description")
                ))

            return repos

        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                self.log_error(f"PWC repo fetch error: {e.response.status_code}")
            return []
        except Exception as e:
            self.log_error("PWC repo fetch failed", error=str(e))
            return []

    async def get_paper_results(self, arxiv_id: str) -> List[PWCResult]:
        """
        Get benchmark results for a paper.

        Args:
            arxiv_id: arXiv paper ID

        Returns:
            List of benchmark results
        """
        clean_id = arxiv_id.split("v")[0]

        try:
            client = await self._get_client()
            response = await client.get(f"/papers/{clean_id}/results/")
            response.raise_for_status()
            data = response.json()

            results = []
            for result in data.get("results", data if isinstance(data, list) else []):
                results.append(PWCResult(
                    task=result.get("task", ""),
                    dataset=result.get("dataset", ""),
                    metric=result.get("metric", ""),
                    value=float(result.get("value", 0)),
                    model_name=result.get("model"),
                    paper_title=result.get("paper_title"),
                    paper_arxiv_id=result.get("paper_arxiv_id")
                ))

            return results

        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                self.log_error(f"PWC results fetch error: {e.response.status_code}")
            return []
        except Exception as e:
            self.log_error("PWC results fetch failed", error=str(e))
            return []

    async def fetch_benchmark_observations(
        self,
        paper_ids: Sequence[str]
    ) -> List[BenchmarkObservation]:
        """
        Fetch benchmark observations for multiple papers.

        Args:
            paper_ids: List of arXiv paper IDs

        Returns:
            List of BenchmarkObservation records
        """
        if not paper_ids:
            return []

        self.log_info("Fetching PWC benchmark data", paper_count=len(paper_ids))

        observations = []
        batch_size = 5

        for i in range(0, len(paper_ids), batch_size):
            batch = paper_ids[i:i + batch_size]
            tasks = [self.get_paper_results(pid) for pid in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for paper_id, result in zip(batch, results):
                if isinstance(result, Exception):
                    self.log_warning(f"Failed to fetch results for {paper_id}")
                    continue

                for r in result:
                    observations.append(BenchmarkObservation(
                        paper_id=paper_id,
                        task=r.task,
                        dataset=r.dataset,
                        metric=r.metric,
                        value=r.value,
                        model_name=r.model_name,
                        evidence_source="paperswithcode"
                    ))

            if i + batch_size < len(paper_ids):
                await asyncio.sleep(0.1)

        self.log_info("Fetched benchmark observations", count=len(observations))
        return observations

    async def get_sota_for_task(
        self,
        task: str,
        dataset: Optional[str] = None,
        limit: int = 10
    ) -> List[PWCResult]:
        """
        Get SOTA results for a task (optionally on a specific dataset).

        Args:
            task: Task name (e.g., "Image Classification")
            dataset: Optional dataset name (e.g., "ImageNet")
            limit: Max results to return

        Returns:
            List of SOTA results sorted by performance
        """
        try:
            client = await self._get_client()

            # Search for task
            task_slug = task.lower().replace(" ", "-")
            response = await client.get(
                f"/evaluations/",
                params={
                    "task": task_slug,
                    "ordering": "-metric_value",
                    "page_size": limit
                }
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("results", []):
                if dataset and item.get("dataset", "").lower() != dataset.lower():
                    continue

                results.append(PWCResult(
                    task=task,
                    dataset=item.get("dataset", ""),
                    metric=item.get("metric", ""),
                    value=float(item.get("metric_value", 0)),
                    model_name=item.get("model"),
                    paper_title=item.get("paper_title"),
                    paper_arxiv_id=item.get("paper_arxiv_id")
                ))

            return results[:limit]

        except Exception as e:
            self.log_error("Failed to fetch SOTA", error=str(e), task=task)
            return []

    async def fetch_taxonomy_entities(self) -> dict:
        """
        Return canonical lists of tasks, datasets, and techniques from PWC.

        Returns:
            {
                "tasks": List[TaskUpsert],
                "datasets": List[DatasetUpsert],
                "techniques": List[TechniqueUpsert]
            }
        """
        self.log_info("Fetching PWC taxonomy entities")

        tasks = await self._fetch_tasks()
        datasets = await self._fetch_datasets()
        methods = await self._fetch_methods()

        return {
            "tasks": tasks,
            "datasets": datasets,
            "techniques": methods,
        }

    async def _fetch_tasks(self, limit: int = 100) -> List[TaskUpsert]:
        """Fetch task taxonomy from PWC"""
        try:
            client = await self._get_client()
            response = await client.get(
                "/tasks/",
                params={"page_size": limit}
            )
            response.raise_for_status()
            data = response.json()

            tasks = []
            for item in data.get("results", []):
                tasks.append(TaskUpsert(
                    name=item.get("name", ""),
                    taxonomy_path=item.get("area"),
                    modality=self._infer_modality(item.get("name", "")),
                    description=item.get("description")
                ))

            return tasks

        except Exception as e:
            self.log_error("Failed to fetch PWC tasks", error=str(e))
            return []

    async def _fetch_datasets(self, limit: int = 100) -> List[DatasetUpsert]:
        """Fetch dataset taxonomy from PWC"""
        try:
            client = await self._get_client()
            response = await client.get(
                "/datasets/",
                params={"page_size": limit}
            )
            response.raise_for_status()
            data = response.json()

            datasets = []
            for item in data.get("results", []):
                name = item.get("name", "")
                datasets.append(DatasetUpsert(
                    name=name,
                    normalized_name=name.lower().replace(" ", "_").replace("-", "_"),
                    modality=self._infer_modality(name),
                    url=item.get("url"),
                    metadata={
                        "full_name": item.get("full_name"),
                        "homepage": item.get("homepage")
                    }
                ))

            return datasets

        except Exception as e:
            self.log_error("Failed to fetch PWC datasets", error=str(e))
            return []

    async def _fetch_methods(self, limit: int = 100) -> List[TechniqueUpsert]:
        """Fetch method/technique taxonomy from PWC"""
        try:
            client = await self._get_client()
            response = await client.get(
                "/methods/",
                params={"page_size": limit}
            )
            response.raise_for_status()
            data = response.json()

            methods = []
            for item in data.get("results", []):
                name = item.get("name", "")
                methods.append(TechniqueUpsert(
                    name=name,
                    normalized_name=name.lower().replace(" ", "_").replace("-", "_"),
                    method_type=self._infer_method_type(name),
                    description=item.get("description"),
                    evidence_source="paperswithcode"
                ))

            return methods

        except Exception as e:
            self.log_error("Failed to fetch PWC methods", error=str(e))
            return []

    async def batch_get_paper_info(
        self,
        arxiv_ids: List[str],
        include_repos: bool = True,
        include_results: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get paper info, repositories, and results for multiple papers.

        Args:
            arxiv_ids: List of arXiv IDs
            include_repos: Whether to fetch code repositories
            include_results: Whether to fetch benchmark results

        Returns:
            Dict mapping arxiv_id to paper data
        """
        output = {}

        for arxiv_id in arxiv_ids:
            paper = await self.get_paper_by_arxiv_id(arxiv_id)
            if not paper:
                continue

            info: Dict[str, Any] = {
                "paper": paper.model_dump(),
                "repositories": [],
                "results": []
            }

            if include_repos:
                repos = await self.get_repositories(arxiv_id)
                info["repositories"] = [r.model_dump() for r in repos]

            if include_results:
                results = await self.get_paper_results(arxiv_id)
                info["results"] = [r.model_dump() for r in results]

            output[arxiv_id] = info

            # Respect rate limits
            await asyncio.sleep(0.1)

        return output

    def _infer_modality(self, name: str) -> Optional[str]:
        """Infer modality from name"""
        name_lower = name.lower()

        if any(kw in name_lower for kw in ["image", "vision", "visual", "photo", "pixel"]):
            return "vision"
        elif any(kw in name_lower for kw in ["text", "language", "nlp", "word", "sentence"]):
            return "text"
        elif any(kw in name_lower for kw in ["audio", "speech", "sound", "voice"]):
            return "audio"
        elif any(kw in name_lower for kw in ["video", "temporal"]):
            return "video"
        elif any(kw in name_lower for kw in ["multimodal", "cross-modal"]):
            return "multimodal"

        return None

    def _infer_method_type(self, name: str) -> Optional[str]:
        """Infer method type from name"""
        name_lower = name.lower()

        if any(kw in name_lower for kw in ["transformer", "attention", "bert", "gpt"]):
            return "transformer"
        elif any(kw in name_lower for kw in ["diffusion", "score", "ddpm"]):
            return "diffusion"
        elif any(kw in name_lower for kw in ["cnn", "convolution", "resnet", "vgg"]):
            return "convolutional"
        elif any(kw in name_lower for kw in ["rnn", "lstm", "gru", "recurrent"]):
            return "recurrent"
        elif any(kw in name_lower for kw in ["gan", "generative adversarial"]):
            return "generative"
        elif any(kw in name_lower for kw in ["reinforcement", "rl", "policy", "q-learning"]):
            return "reinforcement_learning"
        elif any(kw in name_lower for kw in ["contrastive", "clip", "simclr"]):
            return "contrastive"

        return None


# Module-level singleton
_pwc_provider: Optional[PapersWithCodeProvider] = None


def get_pwc_provider() -> PapersWithCodeProvider:
    """Get or create PWC provider singleton"""
    global _pwc_provider
    if _pwc_provider is None:
        _pwc_provider = PapersWithCodeProvider()
    return _pwc_provider
