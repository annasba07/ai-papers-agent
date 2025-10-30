"""
Research graph enrichment service

Provides orchestration primitives for populating the extended ontology:
- Techniques, tasks, datasets, organisations, authors
- Relationships (paper associations, technique graphs, benchmark links)
- Trend & novelty signals

Each public method is intentionally thin and focuses on IO contracts.
Implementation will live behind adapters (OpenAlex, PapersWithCode, GitHub, etc.)
"""
from __future__ import annotations

from typing import Iterable, Sequence, Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy import text

from app.db.database import database
from app.utils.logger import LoggerMixin


class ResearchGraphService(LoggerMixin):
    """
    Coordinates enrichment of the living research graph.

    The service is intentionally split into small async methods to make
    them easy to schedule (Celery/Temporal) and test independently.
    """

    async def upsert_techniques(self, techniques: Sequence[Dict[str, Any]]) -> int:
        """
        Insert or update technique records.

        Expected shape per technique dict:
        {
            "name": "...",
            "normalized_name": "...",
            "method_type": "diffusion" | "transformer" | ...,
            "emergence_date": datetime | str,
            "maturity_score": 0.0-1.0,
            "description": "...",
            "embedding": List[float] (optional)
        }
        """
        if not techniques:
            return 0

        await self._ensure_connection()
        inserted = 0

        query = text("""
            INSERT INTO techniques (
                name,
                normalized_name,
                method_type,
                emergence_date,
                maturity_score,
                description,
                embedding
            )
            VALUES (
                :name,
                :normalized_name,
                :method_type,
                :emergence_date,
                :maturity_score,
                :description,
                :embedding
            )
            ON CONFLICT (name)
            DO UPDATE SET
                normalized_name = EXCLUDED.normalized_name,
                method_type = COALESCE(EXCLUDED.method_type, techniques.method_type),
                emergence_date = COALESCE(EXCLUDED.emergence_date, techniques.emergence_date),
                maturity_score = GREATEST(techniques.maturity_score, EXCLUDED.maturity_score),
                description = COALESCE(EXCLUDED.description, techniques.description),
                embedding = COALESCE(EXCLUDED.embedding, techniques.embedding),
                updated_at = CURRENT_TIMESTAMP
            RETURNING id;
        """)

        for technique in techniques:
            params = technique.copy()
            # normalize datetime if provided as str
            emergence_date = params.get("emergence_date")
            if isinstance(emergence_date, str):
                params["emergence_date"] = datetime.fromisoformat(emergence_date)
            inserted += 1 if await database.execute(query, params) else 0

        self.log_info("Upserted techniques", count=inserted)
        return inserted

    async def upsert_tasks(self, tasks: Sequence[Dict[str, Any]]) -> int:
        """
        Insert or update task definitions (taxonomy-aligned).
        """
        if not tasks:
            return 0

        await self._ensure_connection()
        query = text("""
            INSERT INTO tasks (
                name,
                taxonomy_path,
                modality,
                application_domain,
                description
            )
            VALUES (
                :name,
                :taxonomy_path,
                :modality,
                :application_domain,
                :description
            )
            ON CONFLICT (name)
            DO UPDATE SET
                taxonomy_path = COALESCE(EXCLUDED.taxonomy_path, tasks.taxonomy_path),
                modality = COALESCE(EXCLUDED.modality, tasks.modality),
                application_domain = COALESCE(EXCLUDED.application_domain, tasks.application_domain),
                description = COALESCE(EXCLUDED.description, tasks.description),
                updated_at = CURRENT_TIMESTAMP;
        """)

        for task in tasks:
            await database.execute(query, task)

        self.log_info("Upserted tasks", count=len(tasks))
        return len(tasks)

    async def upsert_datasets(self, datasets: Sequence[Dict[str, Any]]) -> int:
        """
        Insert/update datasets with metadata & optional embeddings.
        """
        if not datasets:
            return 0

        await self._ensure_connection()
        query = text("""
            INSERT INTO datasets (
                name,
                normalized_name,
                modality,
                sample_count,
                license,
                maintainer,
                url,
                embedding,
                metadata
            )
            VALUES (
                :name,
                :normalized_name,
                :modality,
                :sample_count,
                :license,
                :maintainer,
                :url,
                :embedding,
                :metadata
            )
            ON CONFLICT (name)
            DO UPDATE SET
                normalized_name = EXCLUDED.normalized_name,
                modality = COALESCE(EXCLUDED.modality, datasets.modality),
                sample_count = COALESCE(EXCLUDED.sample_count, datasets.sample_count),
                license = COALESCE(EXCLUDED.license, datasets.license),
                maintainer = COALESCE(EXCLUDED.maintainer, datasets.maintainer),
                url = COALESCE(EXCLUDED.url, datasets.url),
                embedding = COALESCE(EXCLUDED.embedding, datasets.embedding),
                metadata = COALESCE(EXCLUDED.metadata, datasets.metadata),
                updated_at = CURRENT_TIMESTAMP;
        """)

        for dataset in datasets:
            await database.execute(query, dataset)

        self.log_info("Upserted datasets", count=len(datasets))
        return len(datasets)

    async def link_paper_entities(
        self,
        paper_id: str,
        techniques: Optional[Sequence[Dict[str, Any]]] = None,
        tasks: Optional[Iterable[int]] = None,
        datasets: Optional[Iterable[int]] = None,
    ) -> None:
        """
        Attach techniques/tasks/datasets to a paper.

        techniques payload: [{"technique_id": 1, "role": "core", "confidence": 0.9}, ...]
        """
        await self._ensure_connection()

        if techniques:
            await self._link_paper_techniques(paper_id, techniques)
        if tasks:
            await self._link_paper_tasks(paper_id, tasks)
        if datasets:
            await self._link_paper_datasets(paper_id, datasets)

    async def upsert_authors(
        self,
        authors: Sequence[Dict[str, Any]],
        paper_id: Optional[str] = None
    ) -> List[int]:
        """
        Upsert authors and optionally connect them to a paper.
        """
        if not authors:
            return []

        await self._ensure_connection()
        author_ids: List[int] = []

        insert_author = text("""
            INSERT INTO authors (
                full_name,
                normalized_name,
                orcid,
                homepage,
                primary_affiliation_id,
                stats
            )
            VALUES (
                :full_name,
                :normalized_name,
                :orcid,
                :homepage,
                :primary_affiliation_id,
                :stats
            )
            ON CONFLICT (orcid)
            DO UPDATE SET
                full_name = COALESCE(EXCLUDED.full_name, authors.full_name),
                normalized_name = COALESCE(EXCLUDED.normalized_name, authors.normalized_name),
                homepage = COALESCE(EXCLUDED.homepage, authors.homepage),
                primary_affiliation_id = COALESCE(EXCLUDED.primary_affiliation_id, authors.primary_affiliation_id),
                stats = COALESCE(EXCLUDED.stats, authors.stats),
                updated_at = CURRENT_TIMESTAMP
            RETURNING id;
        """)

        link_author = text("""
            INSERT INTO paper_authors (
                paper_id,
                author_id,
                author_order,
                is_corresponding
            )
            VALUES (:paper_id, :author_id, :author_order, :is_corresponding)
            ON CONFLICT (paper_id, author_id) DO NOTHING;
        """)

        for author in authors:
            author_id = await database.fetch_val(insert_author, author)
            if author_id is None:
                continue

            author_ids.append(author_id)
            if paper_id:
                await database.execute(
                    link_author,
                    {
                        "paper_id": paper_id,
                        "author_id": author_id,
                        "author_order": author.get("author_order"),
                        "is_corresponding": author.get("is_corresponding", False),
                    }
                )

        self.log_info("Upserted authors", count=len(author_ids))
        return author_ids

    async def attach_benchmark_results(
        self,
        technique_id: int,
        benchmark_ids: Sequence[int],
        delta_from_sota: Optional[float] = None,
        sota_paper_id: Optional[str] = None
    ) -> None:
        """
        Link a technique to one or more benchmark rows.
        """
        if not benchmark_ids:
            return

        await self._ensure_connection()
        query = text("""
            INSERT INTO technique_benchmarks (
                technique_id,
                benchmark_id,
                delta_from_sota,
                sota_paper_id
            )
            VALUES (:technique_id, :benchmark_id, :delta_from_sota, :sota_paper_id)
            ON CONFLICT (technique_id, benchmark_id)
            DO UPDATE SET
                delta_from_sota = COALESCE(EXCLUDED.delta_from_sota, technique_benchmarks.delta_from_sota),
                sota_paper_id = COALESCE(EXCLUDED.sota_paper_id, technique_benchmarks.sota_paper_id),
                created_at = technique_benchmarks.created_at;
        """)

        for benchmark_id in benchmark_ids:
            await database.execute(
                query,
                {
                    "technique_id": technique_id,
                    "benchmark_id": benchmark_id,
                    "delta_from_sota": delta_from_sota,
                    "sota_paper_id": sota_paper_id,
                }
            )

        self.log_debug(
            "Linked technique to benchmarks",
            technique_id=technique_id,
            benchmark_count=len(benchmark_ids)
        )

    async def record_technique_relationships(
        self,
        relationships: Sequence[Dict[str, Any]]
    ) -> None:
        """
        Upsert relationships between techniques. Each entry:
        {
            "technique_a_id": 1,
            "technique_b_id": 2,
            "relation_type": "extends",
            "weight": 0.8,
            "first_seen_paper_id": "2010.12345"
        }
        """
        if not relationships:
            return

        await self._ensure_connection()
        query = text("""
            INSERT INTO technique_relationships (
                technique_a_id,
                technique_b_id,
                relation_type,
                weight,
                first_seen_paper_id
            )
            VALUES (
                LEAST(:technique_a_id, :technique_b_id),
                GREATEST(:technique_a_id, :technique_b_id),
                :relation_type,
                :weight,
                :first_seen_paper_id
            )
            ON CONFLICT (technique_a_id, technique_b_id)
            DO UPDATE SET
                relation_type = EXCLUDED.relation_type,
                weight = COALESCE(EXCLUDED.weight, technique_relationships.weight),
                first_seen_paper_id = COALESCE(EXCLUDED.first_seen_paper_id, technique_relationships.first_seen_paper_id),
                created_at = technique_relationships.created_at;
        """)

        for rel in relationships:
            await database.execute(query, rel)

        self.log_info("Recorded technique relationships", count=len(relationships))

    async def refresh_trending_metrics(self) -> None:
        """
        Stub method for scheduled computation of:
        - Technique momentum (paper velocity, citation acceleration)
        - Dataset adoption curves
        - Hot topics derived from concepts/tasks

        Implementation will live in dedicated analytic jobs; this method
        acts as an orchestration hook for invoking them.
        """
        self.log_debug("Triggering trending metrics refresh (stub)")

    async def _link_paper_techniques(
        self,
        paper_id: str,
        techniques: Sequence[Dict[str, Any]]
    ) -> None:
        query = text("""
            INSERT INTO paper_techniques (
                paper_id,
                technique_id,
                role,
                confidence,
                evidence_source,
                notes
            )
            VALUES (
                :paper_id,
                :technique_id,
                :role,
                :confidence,
                :evidence_source,
                :notes
            )
            ON CONFLICT (paper_id, technique_id)
            DO UPDATE SET
                role = COALESCE(EXCLUDED.role, paper_techniques.role),
                confidence = COALESCE(EXCLUDED.confidence, paper_techniques.confidence),
                evidence_source = COALESCE(EXCLUDED.evidence_source, paper_techniques.evidence_source),
                notes = COALESCE(EXCLUDED.notes, paper_techniques.notes);
        """)

        for technique in techniques:
            payload = {
                "paper_id": paper_id,
                "technique_id": technique["technique_id"],
                "role": technique.get("role"),
                "confidence": technique.get("confidence", 1.0),
                "evidence_source": technique.get("evidence_source"),
                "notes": technique.get("notes"),
            }
            await database.execute(query, payload)

    async def _link_paper_tasks(self, paper_id: str, task_ids: Iterable[int]) -> None:
        query = text("""
            INSERT INTO paper_tasks (paper_id, task_id)
            VALUES (:paper_id, :task_id)
            ON CONFLICT (paper_id, task_id) DO NOTHING;
        """)
        for task_id in task_ids:
            await database.execute(query, {"paper_id": paper_id, "task_id": task_id})

    async def _link_paper_datasets(self, paper_id: str, dataset_ids: Iterable[int]) -> None:
        query = text("""
            INSERT INTO paper_datasets (paper_id, dataset_id)
            VALUES (:paper_id, :dataset_id)
            ON CONFLICT (paper_id, dataset_id) DO NOTHING;
        """)
        for dataset_id in dataset_ids:
            await database.execute(query, {"paper_id": paper_id, "dataset_id": dataset_id})

    async def _ensure_connection(self) -> None:
        if not database.is_connected:
            await database.connect()


# Global singleton helper
_research_graph_service: Optional[ResearchGraphService] = None


def get_research_graph_service() -> ResearchGraphService:
    global _research_graph_service
    if _research_graph_service is None:
        _research_graph_service = ResearchGraphService()
    return _research_graph_service
