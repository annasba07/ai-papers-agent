"""
Paper Enrichment Service

Orchestrates multiple data providers to enrich paper records with:
- Citation data (OpenAlex)
- Code repositories (Papers With Code, GitHub)
- Benchmark results (Papers With Code)
- Technique extraction (LLM + heuristics)

This service is the main entry point for enriching paper data.
"""
from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Any

from pydantic import BaseModel

from app.utils.logger import LoggerMixin
from app.services.providers.openalex_provider import (
    get_openalex_provider,
    CitationInfo,
    OpenAlexWork
)
from app.services.providers.pwc_provider import (
    get_pwc_provider,
    PWCPaper,
    PWCRepository,
    PWCResult
)
from app.services.technique_extraction_service import (
    get_technique_extraction_service,
    TechniqueExtractionResult
)


class EnrichedPaper(BaseModel):
    """Fully enriched paper data"""
    # Core paper data
    paper_id: str
    title: str
    abstract: Optional[str] = None

    # Citation data (OpenAlex)
    cited_by_count: Optional[int] = None
    references_count: Optional[int] = None
    concepts: List[Dict[str, Any]] = []
    openalex_id: Optional[str] = None

    # Code repositories (PWC)
    has_code: bool = False
    official_repo: Optional[Dict[str, Any]] = None
    community_repos: List[Dict[str, Any]] = []

    # Benchmark results (PWC)
    benchmark_results: List[Dict[str, Any]] = []
    tasks: List[str] = []
    methods: List[str] = []

    # Technique extraction
    techniques: List[Dict[str, Any]] = []
    architecture_type: Optional[str] = None
    task_domains: List[str] = []
    novelty_type: Optional[str] = None

    # Enrichment metadata
    enrichment_sources: List[str] = []


class EnrichmentService(LoggerMixin):
    """
    Orchestrates paper enrichment from multiple data sources.

    Combines:
    - OpenAlex: Citations, references, concepts
    - Papers With Code: Repositories, benchmarks, tasks
    - Technique Extraction: LLM-extracted techniques
    """

    def __init__(self):
        self.openalex = get_openalex_provider()
        self.pwc = get_pwc_provider()
        self.technique_extractor = get_technique_extraction_service()
        self.log_info("Enrichment service initialized")

    async def enrich_paper(
        self,
        paper_id: str,
        title: str,
        abstract: str,
        include_citations: bool = True,
        include_code: bool = True,
        include_benchmarks: bool = True,
        include_techniques: bool = True
    ) -> EnrichedPaper:
        """
        Enrich a single paper with data from all sources.

        Args:
            paper_id: arXiv paper ID
            title: Paper title
            abstract: Paper abstract
            include_citations: Fetch citation data from OpenAlex
            include_code: Fetch code repos from PWC
            include_benchmarks: Fetch benchmark results from PWC
            include_techniques: Extract techniques

        Returns:
            EnrichedPaper with all available data
        """
        self.log_info(f"Enriching paper", paper_id=paper_id)

        result = EnrichedPaper(
            paper_id=paper_id,
            title=title,
            abstract=abstract
        )

        # Build list of enrichment tasks
        tasks = []
        task_names = []

        if include_citations:
            tasks.append(self.openalex.get_citation_info(paper_id))
            task_names.append("citations")

        if include_code:
            tasks.append(self.pwc.get_repositories(paper_id))
            task_names.append("repositories")

        if include_benchmarks:
            tasks.append(self.pwc.get_paper_by_arxiv_id(paper_id))
            task_names.append("pwc_paper")
            tasks.append(self.pwc.get_paper_results(paper_id))
            task_names.append("benchmarks")

        if include_techniques:
            tasks.append(
                self.technique_extractor.extract_techniques(paper_id, title, abstract)
            )
            task_names.append("techniques")

        # Execute all tasks concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for i, (name, res) in enumerate(zip(task_names, results)):
                if isinstance(res, Exception):
                    self.log_warning(f"Enrichment task failed", task=name, error=str(res))
                    continue

                if name == "citations" and res:
                    citation_info: CitationInfo = res
                    result.cited_by_count = citation_info.cited_by_count
                    result.references_count = citation_info.references_count
                    result.concepts = citation_info.concepts
                    result.openalex_id = citation_info.openalex_id
                    result.enrichment_sources.append("openalex")

                elif name == "repositories" and res:
                    repos: List[PWCRepository] = res
                    result.has_code = len(repos) > 0
                    for repo in repos:
                        repo_dict = repo.model_dump()
                        if repo.is_official and result.official_repo is None:
                            result.official_repo = repo_dict
                        else:
                            result.community_repos.append(repo_dict)
                    if repos:
                        result.enrichment_sources.append("pwc_repos")

                elif name == "pwc_paper" and res:
                    pwc_paper: PWCPaper = res
                    result.tasks = pwc_paper.tasks
                    result.methods = pwc_paper.methods

                elif name == "benchmarks" and res:
                    benchmarks: List[PWCResult] = res
                    result.benchmark_results = [b.model_dump() for b in benchmarks]
                    if benchmarks:
                        result.enrichment_sources.append("pwc_benchmarks")

                elif name == "techniques" and res:
                    extraction: TechniqueExtractionResult = res
                    result.techniques = [t.model_dump() for t in extraction.techniques]
                    result.architecture_type = extraction.architecture_type
                    result.task_domains = extraction.task_domains
                    result.novelty_type = extraction.novelty_type
                    result.enrichment_sources.append(f"technique_{extraction.extraction_method}")

        self.log_info(
            f"Paper enriched",
            paper_id=paper_id,
            sources=result.enrichment_sources
        )

        return result

    async def batch_enrich_papers(
        self,
        papers: List[Dict[str, Any]],
        include_citations: bool = True,
        include_code: bool = True,
        include_benchmarks: bool = True,
        include_techniques: bool = True,
        concurrency: int = 3
    ) -> Dict[str, EnrichedPaper]:
        """
        Enrich multiple papers efficiently.

        Args:
            papers: List of paper dicts with id, title, abstract/summary
            include_*: What data to fetch
            concurrency: Max concurrent enrichments

        Returns:
            Dict mapping paper_id to EnrichedPaper
        """
        self.log_info(f"Batch enriching papers", count=len(papers))

        semaphore = asyncio.Semaphore(concurrency)

        async def enrich_one(paper: Dict[str, Any]) -> tuple:
            async with semaphore:
                result = await self.enrich_paper(
                    paper_id=paper.get("id", ""),
                    title=paper.get("title", ""),
                    abstract=paper.get("abstract", paper.get("summary", "")),
                    include_citations=include_citations,
                    include_code=include_code,
                    include_benchmarks=include_benchmarks,
                    include_techniques=include_techniques
                )
                return paper.get("id", ""), result

        tasks = [enrich_one(p) for p in papers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {}
        for result in results:
            if isinstance(result, Exception):
                self.log_warning(f"Paper enrichment failed", error=str(result))
                continue
            paper_id, enriched = result
            output[paper_id] = enriched

        self.log_info(f"Batch enrichment complete", enriched=len(output), total=len(papers))
        return output

    async def get_citation_graph(
        self,
        paper_id: str,
        depth: int = 1,
        max_papers: int = 20
    ) -> Dict[str, Any]:
        """
        Build a citation graph around a paper.

        Args:
            paper_id: Center paper arXiv ID
            depth: How many hops to traverse (1 = direct citations only)
            max_papers: Max papers to include

        Returns:
            Graph data with nodes and edges
        """
        nodes = []
        edges = []
        seen_ids = set()

        async def add_paper(arxiv_id: str, level: int):
            if arxiv_id in seen_ids or len(nodes) >= max_papers:
                return
            seen_ids.add(arxiv_id)

            work = await self.openalex.get_work_by_arxiv_id(arxiv_id)
            if not work:
                return

            nodes.append({
                "id": arxiv_id,
                "title": work.title,
                "cited_by_count": work.cited_by_count,
                "level": level,
                "openalex_id": work.openalex_id
            })

            if level < depth:
                # Get citing papers
                citing = await self.openalex.get_citing_papers(arxiv_id, limit=5)
                for c in citing:
                    if c.arxiv_id and c.arxiv_id not in seen_ids:
                        edges.append({
                            "source": c.arxiv_id,
                            "target": arxiv_id,
                            "type": "cites"
                        })
                        await add_paper(c.arxiv_id, level + 1)

                # Get references
                refs = await self.openalex.get_references(arxiv_id, limit=5)
                for r in refs:
                    if r.arxiv_id and r.arxiv_id not in seen_ids:
                        edges.append({
                            "source": arxiv_id,
                            "target": r.arxiv_id,
                            "type": "cites"
                        })
                        await add_paper(r.arxiv_id, level + 1)

        await add_paper(paper_id, 0)

        return {
            "center": paper_id,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }


# Module-level singleton
_enrichment_service: Optional[EnrichmentService] = None


def get_enrichment_service() -> EnrichmentService:
    """Get or create enrichment service singleton"""
    global _enrichment_service
    if _enrichment_service is None:
        _enrichment_service = EnrichmentService()
    return _enrichment_service
