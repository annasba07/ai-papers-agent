"""
Local semantic search over the derived atlas dataset.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import torch
import torch.nn.functional as F

from app.core.config import settings
from app.utils.logger import LoggerMixin


# Query embedding cache - shared across instances
# Max 500 queries, evicts least recently used
_QUERY_CACHE_SIZE = 500
_query_embedding_cache: Dict[str, Tuple[np.ndarray, float]] = {}
_query_cache_hits = 0
_query_cache_misses = 0


class LocalAtlasService(LoggerMixin):
    """Semantic search across the locally curated paper atlas."""

    def __init__(self) -> None:
        self.enabled = False
        self._records: List[Dict] = []
        self._embeddings: Optional[np.ndarray] = None
        self._encoder = None
        self._encoder_type: str = "sentence-transformers"
        self._record_ids: List[Optional[str]] = []
        self._active_cache_label: Optional[str] = None
        self._stats: Dict[str, object] = {}
        self._timeline: Dict[str, List[Dict[str, object]]] = {}
        self._author_leaderboard: List[Dict[str, object]] = []
        self._default_cache_label: Optional[str] = (
            settings.ATLAS_EMBED_CACHE_LABEL.strip() if settings.ATLAS_EMBED_CACHE_LABEL else None
        )

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

        self._load_summary_files(atlas_path)
        self._record_ids = [record.get("id") for record in self._records]
        documents = [record["_search_text"] for record in self._records]
        cache_dir = Path(settings.ATLAS_EMBED_CACHE_DIR).expanduser().resolve()
        self._cache_dir = cache_dir
        try:
            model_name = settings.ATLAS_EMBED_MODEL or "sentence-transformers/all-MiniLM-L6-v2"
            self._model_name = model_name
            cached_embeddings, label_used = self._load_cached_embeddings(cache_dir, model_name, self._default_cache_label)

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
            # Validate embedding dimensions match encoder output
            encoder_dim = self._get_encoder_dimension()
            embed_dim = embeddings.shape[1] if len(embeddings.shape) > 1 else 0

            if encoder_dim and embed_dim and encoder_dim != embed_dim:
                self.log_warning(
                    "Embedding dimension mismatch - trying compatible cache",
                    cache_dim=embed_dim,
                    encoder_dim=encoder_dim,
                    cache_label=label_used,
                )
                # Try to find a compatible cache
                compatible_embeddings, compatible_label = self._find_compatible_cache(
                    cache_dir, encoder_dim
                )
                if compatible_embeddings is not None:
                    embeddings = compatible_embeddings
                    label_used = compatible_label
                    self.log_info(
                        "Using compatible embedding cache",
                        label=compatible_label,
                        dimension=embeddings.shape[1],
                    )
                else:
                    # No compatible cache found - need to re-encode or use lexical only
                    self.log_warning(
                        "No compatible embedding cache found - semantic search disabled",
                        encoder_dim=encoder_dim,
                    )
                    self._encoder = None
                    self._embeddings = None
                    self.enabled = True  # Still allow lexical search
                    return

            self._embeddings = embeddings.astype(np.float32)
            self._active_cache_label = label_used or self._default_cache_label
            self.enabled = True
            self.log_info(
                "Local atlas semantic index ready",
                paper_count=len(self._records),
                model=model_name,
                cached=bool(cached_embeddings is not None),
                embedding_dim=self._embeddings.shape[1] if self._embeddings is not None else None,
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

    def _get_encoder_dimension(self) -> Optional[int]:
        """Get the output dimension of the current encoder."""
        if self._encoder is None:
            return None
        if self._encoder_type == "specter2":
            # SPECTER2 produces 768-dimensional embeddings
            return 768
        else:
            # SentenceTransformer models have a get_sentence_embedding_dimension method
            try:
                return self._encoder.get_sentence_embedding_dimension()
            except AttributeError:
                return None

    def _find_compatible_cache(
        self, cache_dir: Path, target_dim: int
    ) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """Find a cached embedding file with matching dimensions."""
        if not cache_dir.exists():
            return None, None

        for ids_path in sorted(cache_dir.glob("*_ids.json")):
            label = ids_path.name.replace("_ids.json", "")
            embeddings_path = cache_dir / f"{label}_embeddings.npy"
            if not embeddings_path.exists():
                continue

            try:
                ids = json.loads(ids_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            # Check if IDs match
            if len(ids) != len(self._record_ids):
                continue
            if any((rid or "") != (cached_id or "") for rid, cached_id in zip(self._record_ids, ids)):
                continue

            # Load and check dimensions
            try:
                embeddings = np.load(embeddings_path)
                embed_dim = embeddings.shape[1] if len(embeddings.shape) > 1 else 0
                if embed_dim == target_dim:
                    self.log_info(
                        "Found compatible embedding cache",
                        label=label,
                        dimension=embed_dim,
                    )
                    return embeddings, label
            except Exception:
                continue

        return None, None

    def _get_query_embedding(self, query: str) -> np.ndarray:
        """
        Get query embedding with LRU caching.

        Caches embeddings to avoid expensive model inference on repeated queries.
        Typical speedup: 200-3000ms → 0.1ms on cache hit.
        """
        global _query_embedding_cache, _query_cache_hits, _query_cache_misses

        # Create cache key from query + encoder type + active cache label
        cache_key = hashlib.md5(
            f"{query}:{self._encoder_type}:{self._active_cache_label}".encode()
        ).hexdigest()

        # Check cache
        if cache_key in _query_embedding_cache:
            _query_cache_hits += 1
            embedding, _ = _query_embedding_cache[cache_key]
            return embedding

        # Cache miss - compute embedding
        _query_cache_misses += 1
        start_time = time.time()

        if self._encoder_type == "specter2":
            query_vec = self._encoder.encode([query])[0].astype(np.float32)
        else:
            query_vec = self._encoder.encode(
                [query],
                convert_to_numpy=True,
                normalize_embeddings=True,
            )[0].astype(np.float32)

        encode_time = time.time() - start_time

        # Evict oldest entries if cache is full
        if len(_query_embedding_cache) >= _QUERY_CACHE_SIZE:
            # Remove oldest entry by timestamp
            oldest_key = min(_query_embedding_cache.keys(),
                           key=lambda k: _query_embedding_cache[k][1])
            del _query_embedding_cache[oldest_key]

        # Store in cache with timestamp
        _query_embedding_cache[cache_key] = (query_vec, time.time())

        if encode_time > 0.1:  # Log slow encodings (>100ms)
            self.log_info(
                "Query embedding computed",
                encode_time_ms=round(encode_time * 1000, 1),
                cache_size=len(_query_embedding_cache),
                hit_rate=round(_query_cache_hits / max(1, _query_cache_hits + _query_cache_misses) * 100, 1),
            )

        return query_vec

    def _semantic_scores(self, query: str) -> Optional[np.ndarray]:
        """Compute semantic similarity scores for all papers."""
        if not self._encoder or self._embeddings is None:
            return None

        query_vec = self._get_query_embedding(query)
        return np.dot(self._embeddings, query_vec)

    def get_cache_stats(self) -> Dict[str, object]:
        """Return query embedding cache statistics."""
        global _query_embedding_cache, _query_cache_hits, _query_cache_misses
        total = _query_cache_hits + _query_cache_misses
        return {
            "cache_size": len(_query_embedding_cache),
            "max_size": _QUERY_CACHE_SIZE,
            "hits": _query_cache_hits,
            "misses": _query_cache_misses,
            "hit_rate": round(_query_cache_hits / max(1, total) * 100, 2),
        }

    # ------------------------------------------------------------------ #
    # Public API

    def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        category: Optional[str] = None,
        max_age_days: Optional[int] = None,
        embedding_label: Optional[str] = None,
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

        label_requested = (embedding_label or "").strip() or None
        if label_requested:
            if not self.ensure_embedding_cache(label_requested):
                raise ValueError(f"Unknown embedding cache '{label_requested}'.")

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

    def find_similar(
        self,
        paper_id: str,
        *,
        top_k: int = 10,
        category: Optional[str] = None,
        exclude_same_authors: bool = False,
    ) -> List[Dict]:
        """
        Find papers similar to a given paper using embedding similarity.

        Args:
            paper_id: The ID of the paper to find similar papers for.
            top_k: Maximum number of similar papers to return.
            category: Optional arXiv category filter.
            exclude_same_authors: If True, exclude papers by the same authors.

        Returns:
            List of similar papers with similarity scores.
        """
        if not self.enabled or self._embeddings is None:
            return []

        # Normalize paper_id (remove version suffix if present)
        base_id = paper_id.split("v")[0] if "v" in paper_id else paper_id

        # Find the paper's index
        paper_idx: Optional[int] = None
        paper_authors: Set[str] = set()
        for idx, record_id in enumerate(self._record_ids):
            record_base_id = record_id.split("v")[0] if record_id and "v" in record_id else record_id
            if record_base_id == base_id:
                paper_idx = idx
                paper_authors = set(self._records[idx].get("authors", []))
                break

        if paper_idx is None:
            self.log_warning("Paper not found for similarity search", paper_id=paper_id)
            return []

        # Get the paper's embedding and compute similarities
        paper_embedding = self._embeddings[paper_idx]
        similarities = np.dot(self._embeddings, paper_embedding)

        # Build candidates with filters
        candidates: List[Tuple[int, float]] = []
        for idx, score in enumerate(similarities):
            if idx == paper_idx:  # Skip the query paper itself
                continue

            record = self._records[idx]

            # Category filter
            if category and record.get("category") != category:
                continue

            # Same-author filter
            if exclude_same_authors:
                record_authors = set(record.get("authors", []))
                if record_authors & paper_authors:  # Any overlap
                    continue

            candidates.append((idx, float(score)))

        # Sort by similarity descending
        candidates.sort(key=lambda item: item[1], reverse=True)

        # Build results
        results: List[Dict] = []
        for idx, score in candidates[:top_k]:
            record = self._records[idx]
            results.append({
                "id": record.get("id"),
                "title": record.get("title"),
                "abstract": record.get("abstract"),
                "authors": record.get("authors"),
                "published": record.get("published"),
                "category": record.get("category"),
                "link": record.get("link"),
                "similarity_score": round(score, 4),
            })

        return results

    def get_paper_by_id(self, paper_id: str) -> Optional[Dict]:
        """Get a paper by its ID."""
        if not self.enabled:
            return None

        base_id = paper_id.split("v")[0] if "v" in paper_id else paper_id

        for idx, record_id in enumerate(self._record_ids):
            record_base_id = record_id.split("v")[0] if record_id and "v" in record_id else record_id
            if record_base_id == base_id:
                record = self._records[idx]
                return {
                    "id": record.get("id"),
                    "title": record.get("title"),
                    "abstract": record.get("abstract"),
                    "authors": record.get("authors"),
                    "published": record.get("published"),
                    "category": record.get("category"),
                    "link": record.get("link"),
                }
        return None

    # ------------------------------------------------------------------ #
    # Lexical utilities

    @staticmethod
    def _keyword_overlap(query: str, document: str) -> float:
        query_tokens = {token for token in query.split() if len(token) > 2}
        if not query_tokens:
            return 0.0
        matches = sum(1 for token in query_tokens if token in document)
        return matches / len(query_tokens)

    def _load_cached_embeddings(
        self,
        cache_dir: Path,
        model_name: str,
        preferred_label: Optional[str] = None,
    ) -> Tuple[Optional[np.ndarray], Optional[str]]:
        if not cache_dir.exists():
            return None, None

        candidates: List[str] = []
        if preferred_label:
            candidates.append(preferred_label.strip())
        elif settings.ATLAS_EMBED_CACHE_LABEL:
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
            return embeddings, candidate
        return None, None

    def ensure_embedding_cache(self, label: Optional[str]) -> bool:
        normalized = (label or "").strip() or None
        if normalized == self._active_cache_label:
            return True
        embeddings, used_label = self._load_cached_embeddings(self._cache_dir, self._model_name, normalized)
        if embeddings is None:
            return False
        self._embeddings = embeddings.astype(np.float32)
        self._active_cache_label = used_label or normalized
        self.log_info("Switched atlas embedding cache", label=self._active_cache_label)
        return True

    def list_embedding_caches(self) -> List[Dict[str, object]]:
        caches: List[Dict[str, object]] = []
        if not self._cache_dir.exists():
            return caches
        for ids_path in sorted(self._cache_dir.glob("*_ids.json")):
            label = ids_path.name.replace("_ids.json", "")
            embeddings_path = self._cache_dir / f"{label}_embeddings.npy"
            if not embeddings_path.exists():
                continue
            try:
                ids = json.loads(ids_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            caches.append(
                {
                    "label": label,
                    "paper_count": len(ids),
                    "active": label == (self._active_cache_label or self._default_cache_label),
                }
            )
        return caches

    def _load_summary_files(self, atlas_path: Path) -> None:
        stats_path = atlas_path / "build_stats.json"
        timeline_path = atlas_path / "category_timeline.json"
        authors_path = atlas_path / "author_leaderboard.json"
        if stats_path.exists():
            try:
                self._stats = json.loads(stats_path.read_text(encoding="utf-8"))
            except Exception:
                self._stats = {}
        if timeline_path.exists():
            try:
                self._timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
            except Exception:
                self._timeline = {}
        if authors_path.exists():
            try:
                self._author_leaderboard = json.loads(authors_path.read_text(encoding="utf-8"))
            except Exception:
                self._author_leaderboard = []

    def list_papers(
        self,
        *,
        limit: int = 40,
        category: Optional[str] = None,
        days: Optional[int] = None,
        query: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        lowered = query.lower().strip() if query else ""
        cutoff = None
        if days and days > 0:
            cutoff = datetime.utcnow() - timedelta(days=days)
        items: List[Dict[str, object]] = []
        for record in self._records:
            if category and category != "all" and record.get("category") != category:
                continue
            published_dt = record.get("_published_dt")
            if cutoff and published_dt and published_dt < cutoff:
                continue
            if lowered and lowered not in record.get("_search_text", ""):
                continue
            items.append(record)
        items.sort(key=lambda rec: rec.get("_published_dt") or datetime.min, reverse=True)
        sanitized = [
            {
                "id": rec.get("id"),
                "title": rec.get("title"),
                "abstract": rec.get("abstract"),
                "authors": rec.get("authors"),
                "published": rec.get("published"),
                "category": rec.get("category"),
                "link": rec.get("link"),
            }
            for rec in items[:limit]
        ]
        return sanitized

    def get_summary(self) -> Dict[str, object]:
        top_categories: List[Dict[str, object]] = []
        if self._timeline:
            top_categories = (
                sorted(
                    (
                        {
                            "category": category,
                            "total": sum(point.get("count", 0) for point in points),
                        }
                        for category, points in self._timeline.items()
                    ),
                    key=lambda item: item["total"],
                    reverse=True,
                )[:10]
            )
        return {
            "stats": self._stats,
            "topCategories": top_categories,
            "topAuthors": self._author_leaderboard[:15],
            "timeline": self._timeline,
        }


class Specter2Encoder:
    """Wrapper for producing SPECTER2 retrieval embeddings."""

    def __init__(self, adapter_name: str) -> None:
        from adapters import AutoAdapterModel
        from transformers import AutoTokenizer

        # Use MPS on Apple Silicon, CUDA on NVIDIA, or fall back to CPU
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

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


# Module-level singleton with lazy initialization
_local_atlas_service: Optional[LocalAtlasService] = None


def get_local_atlas_service() -> LocalAtlasService:
    """Get the local atlas service singleton (lazy initialization)."""
    global _local_atlas_service
    if _local_atlas_service is None:
        _local_atlas_service = LocalAtlasService()
    return _local_atlas_service


# Backwards compatibility - lazy proxy
class _LazyLocalAtlasService:
    """Lazy proxy for backwards compatibility with 'local_atlas_service' import."""

    def __getattr__(self, name):
        return getattr(get_local_atlas_service(), name)


local_atlas_service = _LazyLocalAtlasService()
