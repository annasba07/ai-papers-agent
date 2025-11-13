"""
Local semantic search over the derived atlas dataset.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F

from app.core.config import settings
from app.utils.logger import LoggerMixin


class LocalAtlasService(LoggerMixin):
    """Semantic search across the locally curated paper atlas."""

    def __init__(self) -> None:
        self.enabled = False
        self._records: List[Dict] = []
        self._embeddings: Optional[np.ndarray] = None
        self._encoder = None
        self._encoder_type: str = "sentence-transformers"
        self._record_ids: List[Optional[str]] = []

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

        self._record_ids = [record.get("id") for record in self._records]
        documents = [record["_search_text"] for record in self._records]
        cache_dir = Path(settings.ATLAS_EMBED_CACHE_DIR).expanduser().resolve()

        try:
            model_name = settings.ATLAS_EMBED_MODEL or "sentence-transformers/all-MiniLM-L6-v2"
            cached_embeddings = self._load_cached_embeddings(cache_dir, model_name)

            if model_name.startswith("allenai/specter2"):
                self._encoder_type = "specter2"
                self._encoder = Specter2Encoder(model_name)
                embeddings = (
                    cached_embeddings
                    if cached_embeddings is not None
                    else self._encoder.encode(
                        documents,
                        batch_size=min(settings.ATLAS_EMBED_BATCH_SIZE, 16),
                    )
                )
            else:
                from sentence_transformers import SentenceTransformer

                self._encoder = SentenceTransformer(model_name)
                embeddings = (
                    cached_embeddings
                    if cached_embeddings is not None
                    else self._encoder.encode(
                        documents,
                        batch_size=settings.ATLAS_EMBED_BATCH_SIZE,
                        convert_to_numpy=True,
                        normalize_embeddings=True,
                        show_progress_bar=False,
                    )
                )
            self._embeddings = embeddings.astype(np.float32)
            self.enabled = True
            self.log_info(
                "Local atlas semantic index ready",
                paper_count=len(self._records),
                model=model_name,
                cached=bool(cached_embeddings is not None),
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

        if self._encoder_type == "specter2":
            query_vec = self._encoder.encode([query])[0].astype(np.float32)
        else:
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

    def _load_cached_embeddings(self, cache_dir: Path, model_name: str) -> Optional[np.ndarray]:
        if not cache_dir.exists():
            return None

        candidates: List[str] = []
        if settings.ATLAS_EMBED_CACHE_LABEL:
            candidates.append(settings.ATLAS_EMBED_CACHE_LABEL.strip())

        if model_name.startswith("allenai/specter2"):
            candidates.append("specter2")

        safe_name = model_name.split("/")[-1]
        candidates.extend(
            [
                safe_name,
                model_name.replace("/", "_"),
            ]
        )

        seen = []
        for candidate in candidates:
            if not candidate:
                continue
            if candidate in seen:
                continue
            seen.append(candidate)
            embeddings_path = cache_dir / f"{candidate}_embeddings.npy"
            ids_path = cache_dir / f"{candidate}_ids.json"
            if not embeddings_path.exists() or not ids_path.exists():
                continue
            try:
                cached_ids = json.loads(ids_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if len(cached_ids) != len(self._record_ids):
                continue
            if any((rid or "") != (cached_id or "") for rid, cached_id in zip(self._record_ids, cached_ids)):
                continue
            try:
                embeddings = np.load(embeddings_path)
            except Exception:
                continue
            self.log_info(
                "Loaded cached atlas embeddings",
                path=str(embeddings_path),
                label=candidate,
            )
            return embeddings
        return None


class Specter2Encoder:
    """Wrapper for producing SPECTER2 retrieval embeddings."""

    def __init__(self, adapter_name: str) -> None:
        from adapters import AutoAdapterModel
        from transformers import AutoTokenizer

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        base_model_name = "allenai/specter2_base"
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.model = AutoAdapterModel.from_pretrained(base_model_name)

        adapter_to_load = adapter_name or "allenai/specter2"
        loaded_adapter = self.model.load_adapter(adapter_to_load, source="hf")
        self.model.set_active_adapters(loaded_adapter)
        self.model.to(self.device)
        self.model.eval()

    def encode(self, texts: List[str], batch_size: int = 16) -> np.ndarray:
        embeddings: List[np.ndarray] = []
        with torch.no_grad():
            for start in range(0, len(texts), batch_size):
                batch = texts[start : start + batch_size]
                tokenized = self.tokenizer(
                    batch,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt",
                )
                tokenized = {k: v.to(self.device) for k, v in tokenized.items()}
                outputs = self.model(**tokenized)
                cls_embeddings = outputs.last_hidden_state[:, 0]
                cls_embeddings = F.normalize(cls_embeddings, p=2, dim=1)
                embeddings.append(cls_embeddings.cpu().numpy())
        if not embeddings:
            return np.zeros((0, self.model.config.hidden_size), dtype=np.float32)
        return np.vstack(embeddings)


# Module-level singleton
local_atlas_service = LocalAtlasService()
