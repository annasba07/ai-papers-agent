"""
Optional hybrid reranking service for contextual search.
"""
from __future__ import annotations

from typing import List, Dict, Optional
import numpy as np

from app.core.config import settings
from app.utils.logger import LoggerMixin


class RerankService(LoggerMixin):
    """Combine local E5 embeddings and optional OpenAI embeddings for reranking."""

    def __init__(self) -> None:
        self.e5_model_name = settings.RERANK_E5_MODEL
        self.e5_batch_size = settings.RERANK_E5_BATCH_SIZE
        self.e5_prompt = settings.RERANK_E5_PROMPT
        self.e5_weight = settings.RERANK_E5_WEIGHT
        self.openai_model = settings.OPENAI_RERANK_MODEL
        self.openai_weight = settings.OPENAI_RERANK_WEIGHT

        self._e5_encoder = None
        self._openai_client = None

        if self.e5_model_name:
            try:
                from sentence_transformers import SentenceTransformer

                self._e5_encoder = SentenceTransformer(self.e5_model_name)
                self.log_info(
                    "E5 reranker ready",
                    model=self.e5_model_name,
                )
            except Exception as exc:  # pragma: no cover - optional dependency
                self.log_warning(
                    "Failed to load E5 reranker model",
                    error=str(exc),
                    model=self.e5_model_name,
                )
                self._e5_encoder = None

        if self.openai_model:
            try:
                from openai import OpenAI

                self._openai_client = OpenAI()
                self.log_info(
                    "OpenAI reranker enabled",
                    model=self.openai_model,
                )
            except Exception as exc:  # pragma: no cover - optional dependency
                self.log_warning(
                    "OpenAI client unavailable; disabling OpenAI rerank",
                    error=str(exc),
                )
                self._openai_client = None

    def rerank(self, query: str, papers: List[Dict], top_k: int) -> List[Dict]:
        """
        Return a reranked list of papers.

        Args:
            query: user query / project description
            papers: list of papers with keys (title, summary, etc.)
            top_k: limit number of papers to rerank
        """
        if not papers:
            return papers

        scores_accumulator: Optional[np.ndarray] = None
        weights_total = 0.0
        limit = min(top_k, len(papers))
        candidate_texts = [
            (paper.get("title", "") + " " + (paper.get("summary") or paper.get("abstract") or "")).strip()
            for paper in papers[:limit]
        ]

        if self._e5_encoder and self.e5_weight > 0:
            try:
                e5_scores = self._score_with_e5(query, candidate_texts)
                if e5_scores is not None:
                    scores_accumulator = (
                        e5_scores * self.e5_weight
                        if scores_accumulator is None
                        else scores_accumulator + e5_scores * self.e5_weight
                    )
                    weights_total += self.e5_weight
            except Exception as exc:  # pragma: no cover - degrade gracefully
                self.log_warning("E5 rerank failed", error=str(exc))

        if self._openai_client and self.openai_weight > 0:
            try:
                openai_scores = self._score_with_openai(query, candidate_texts)
                if openai_scores is not None:
                    scores_accumulator = (
                        openai_scores * self.openai_weight
                        if scores_accumulator is None
                        else scores_accumulator + openai_scores * self.openai_weight
                    )
                    weights_total += self.openai_weight
            except Exception as exc:  # pragma: no cover - degrade gracefully
                self.log_warning("OpenAI rerank failed", error=str(exc))

        if scores_accumulator is None or weights_total == 0:
            return papers

        combined_scores = scores_accumulator / weights_total
        scored_pairs = list(zip(combined_scores.tolist(), papers[:limit]))
        scored_pairs.sort(key=lambda item: item[0], reverse=True)
        reranked = []
        for score, paper in scored_pairs:
            paper = dict(paper)
            paper["rerank_score"] = float(score)
            reranked.append(paper)
        reranked.extend(papers[limit:])
        return reranked

    # ------------------------------------------------------------------ #
    # Private helpers

    def _score_with_e5(self, query: str, documents: List[str]) -> Optional[np.ndarray]:
        if not self._e5_encoder:
            return None

        instruct_query = f"{self.e5_prompt}{query}".strip()
        query_vec = self._e5_encoder.encode(
            [instruct_query],
            batch_size=1,
            normalize_embeddings=True,
        )[0]
        doc_vecs = self._e5_encoder.encode(
            documents,
            batch_size=self.e5_batch_size,
            normalize_embeddings=True,
        )
        return doc_vecs @ query_vec

    def _score_with_openai(self, query: str, documents: List[str]) -> Optional[np.ndarray]:
        if not self._openai_client:
            return None

        inputs = [query, *documents]
        response = self._openai_client.embeddings.create(
            model=self.openai_model,
            input=inputs,
        )
        embeddings = [np.asarray(item.embedding, dtype=np.float32) for item in response.data]
        query_vec = embeddings[0]
        doc_vecs = np.vstack(embeddings[1:])

        # Normalize for cosine similarity
        query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-12)
        doc_norms = doc_vecs / (np.linalg.norm(doc_vecs, axis=1, keepdims=True) + 1e-12)
        return doc_norms @ query_norm


_rerank_service: Optional[RerankService] = None


def get_rerank_service() -> RerankService:
    global _rerank_service
    if _rerank_service is None:
        _rerank_service = RerankService()
    return _rerank_service
