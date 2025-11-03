"""
Local semantic search over the derived atlas dataset.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.core.config import settings
from app.utils.logger import LoggerMixin


class LocalAtlasService(LoggerMixin):
    """Semantic search across the locally curated paper atlas."""

    def __init__(self) -> None:
        self.enabled = False
        self._records: List[Dict] = []
        self._embeddings: Optional[np.ndarray] = None
        self._encoder = None

        atlas_path = Path(settings.ATLAS_DERIVED_DIR).expanduser().resolve()
        catalog_path = atlas_path / "papers_catalog.ndjson"

        if not catalog_path.exists():
            self.log_warning(
                "Atlas dataset not found; local semantic search disabled",
                path=str(catalog_path),
            )
            return

        try:
            with catalog_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    payload["_search_text"] = self._compose_search_text(payload)
                    payload["_published_dt"] = self._parse_datetime(payload.get("published"))
                    self._records.append(payload)
        except Exception as exc:  # pragma: no cover - defensive guard
            self.log_error("Failed loading atlas catalog", error=exc)
            return

        if not self._records:
            self.log_warning("Atlas catalog is empty; search disabled")
            return

        documents = [record["_search_text"] for record in self._records]

        try:
            from sentence_transformers import SentenceTransformer

            model_name = settings.ATLAS_EMBED_MODEL or "sentence-transformers/all-MiniLM-L6-v2"
            self._encoder = SentenceTransformer(model_name)
            embeddings = self._encoder.encode(
                documents,
                batch_size=settings.ATLAS_EMBED_BATCH_SIZE,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            self._embeddings = embeddings.astype(np.float32)
            self.enabled = True
            self.log_info(
                "Local atlas semantic index ready",
                paper_count=len(self._records),
                model=model_name,
            )
        except Exception as exc:  # pragma: no cover - fallback for missing model
            self.log_warning(
                "SentenceTransformer unavailable; reverting to keyword-only search",
                error=str(exc),
            )
            self._encoder = None
            self._embeddings = None
            self.enabled = True  # still allow lexical search

    # ------------------------------------------------------------------ #
    # Helpers

    @staticmethod
    def _compose_search_text(record: Dict) -> str:
        parts = [
            record.get("title", ""),
            record.get("abstract", ""),
            " ".join(record.get("authors", [])),
            record.get("category", ""),
        ]
        return " \n ".join(part for part in parts if part).lower()

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None

    def _semantic_scores(self, query: str) -> Optional[np.ndarray]:
        if not self._encoder or self._embeddings is None:
            return None

        query_vec = self._encoder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0].astype(np.float32)

        return np.dot(self._embeddings, query_vec)

    # ------------------------------------------------------------------ #
    # Public API

    def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        category: Optional[str] = None,
        max_age_days: Optional[int] = None,
    ) -> List[Dict]:
        """
        Return the most relevant atlas papers for a query.

        Args:
            query: free-form text describing the desired research.
            top_k: maximum number of results to return.
            category: optional arXiv category filter.
            max_age_days: discard papers older than this window.
        """
        if not self.enabled or not query.strip():
            return []

        query_lower = query.lower()
        scores = self._semantic_scores(query)
        now = datetime.utcnow()
        cutoff = now - timedelta(days=max_age_days) if max_age_days else None

        candidates: List[Tuple[int, float]] = []

        # Precompute lexical scores for fallback/hybrid ranking.
        for idx, record in enumerate(self._records):
            if category and record.get("category") != category:
                continue
            published_dt = record.get("_published_dt")
            if cutoff and published_dt and published_dt < cutoff:
                continue

            keyword_score = self._keyword_overlap(query_lower, record["_search_text"])
            semantic_score = scores[idx] if scores is not None else 0.0

            # Hybrid scoring: mostly semantic, with a small lexical boost.
            combined = (semantic_score * 0.85) + (keyword_score * 0.15)
            candidates.append((idx, combined))

        if not candidates:
            return []

        # Sort by score descending
        candidates.sort(key=lambda item: item[1], reverse=True)

        results: List[Dict] = []
        for idx, score in candidates[: top_k * 2]:  # grab some extras before dedup
            record = self._records[idx]
            enriched = dict(record)
            enriched["score"] = float(score)
            results.append(enriched)
            if len(results) >= top_k:
                break

        return results

    def recent_papers(
        self,
        *,
        limit: int = 20,
        category: Optional[str] = None,
        days: Optional[int] = None,
    ) -> List[Dict]:
        """Utility helper for compatibility endpoints."""
        if not self.enabled:
            return []

        cutoff = datetime.utcnow() - timedelta(days=days) if days else None
        filtered = []
        for record in self._records:
            if category and record.get("category") != category:
                continue
            published_dt = record.get("_published_dt")
            if cutoff and published_dt and published_dt < cutoff:
                continue
            filtered.append(record)

        filtered.sort(
            key=lambda rec: rec.get("_published_dt") or datetime.min,
            reverse=True,
        )
        return filtered[:limit]

    # ------------------------------------------------------------------ #
    # Lexical utilities

    @staticmethod
    def _keyword_overlap(query: str, document: str) -> float:
        query_tokens = {token for token in query.split() if len(token) > 2}
        if not query_tokens:
            return 0.0
        matches = sum(1 for token in query_tokens if token in document)
        return matches / len(query_tokens)


# Module-level singleton
local_atlas_service = LocalAtlasService()

