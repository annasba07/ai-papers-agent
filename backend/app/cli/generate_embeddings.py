"""
Generate and cache embeddings for a papers catalog using different models.

Usage:
    python -m app.cli.generate_embeddings --catalog ../data/derived_12mo/papers_catalog.ndjson \
        --output ../data/embeddings --model specter2 --model openai
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import List, Optional

import numpy as np
import requests
from tqdm import tqdm

from app.utils.logger import LoggerMixin


class EmbeddingGenerator(LoggerMixin):
    def __init__(self, catalog_path: Path, output_dir: Path, args: argparse.Namespace):
        self.catalog_path = catalog_path
        self.output_dir = output_dir
        self.args = args
        self.records = self._load_catalog()

    def _load_catalog(self) -> List[dict]:
        self.log_info("Loading catalog", path=str(self.catalog_path))
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found at {self.catalog_path}")

        records: List[dict] = []
        with self.catalog_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                records.append(json.loads(line))
        self.log_info("Catalog loaded", total=len(records))
        return records

    def generate(self, model_name: str, batch_size: int = 32) -> None:
        model_key = model_name.lower()
        if model_key == "specter2":
            self._generate_specter2(batch_size)
        elif model_key == "openai":
            self._generate_openai(batch_size)
        elif model_key == "voyage":
            self._generate_voyage(batch_size)
        elif model_key in {"qwen", "qwen3"}:
            self._generate_qwen(batch_size)
        else:
            raise ValueError(
                f"Unsupported model '{model_name}'. Use 'specter2', 'openai', 'voyage', or 'qwen'."
            )

    def _generate_specter2(self, batch_size: int) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("SentenceTransformer not available for SPECTER embeddings.") from exc

        model_name = "sentence-transformers/allenai-specter"
        encoder = SentenceTransformer(model_name, device="cpu")
        texts = [
            f"{record.get('title', '')} {record.get('abstract', '')}".strip()
            for record in self.records
        ]
        self.log_info("Encoding with SPECTER (sentence-transformers)", documents=len(texts), model=model_name)
        embeddings = encoder.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        self._save_embeddings("specter2", embeddings)

    def _generate_openai(self, batch_size: int) -> None:
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("OpenAI client not installed.") from exc

        client = OpenAI()
        texts = [
            f"{record.get('title', '')} {record.get('abstract', '')}".strip()
            for record in self.records
        ]

        all_vectors: List[np.ndarray] = []
        self.log_info("Encoding with OpenAI embeddings", documents=len(texts))
        for start in tqdm(range(0, len(texts), batch_size), desc="OpenAI embeddings"):
            batch = texts[start : start + batch_size]
            response = client.embeddings.create(
                model="text-embedding-3-large",
                input=batch,
            )
            vectors = [np.asarray(item.embedding, dtype=np.float32) for item in response.data]
            all_vectors.append(np.vstack(vectors))

        embeddings = np.vstack(all_vectors)
        self._save_embeddings("openai_text-embedding-3-large", embeddings)

    def _generate_voyage(self, batch_size: int) -> None:
        api_key = self.args.voyage_api_key or self._env("VOYAGE_API_KEY")
        model_name = self.args.voyage_model
        if not api_key:
            raise RuntimeError("VOYAGE_API_KEY not provided. Set env var or --voyage-api-key.")

        texts = [
            f"{record.get('title', '')} {record.get('abstract', '')}".strip()
            for record in self.records
        ]
        try:
            import voyageai
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "voyageai package not installed. Run `pip install voyageai`."
            ) from exc

        client = voyageai.Client(api_key=api_key, max_retries=0)
        embeddings_store: List[np.ndarray] = []
        self.log_info(
            "Encoding with Voyage",
            model=model_name,
            documents=len(texts),
            batch_size=batch_size,
        )
        for start in tqdm(range(0, len(texts), batch_size), desc="Voyage embeddings"):
            batch = texts[start : start + batch_size]
            result = client.embed(
                batch,
                model=model_name,
                input_type="document",
                output_dimension=self.args.voyage_dimension,
                truncation=True,
            )
            vectors = [
                np.asarray(embedding, dtype=np.float32) for embedding in result.embeddings
            ]
            embeddings_store.append(np.vstack(vectors))
            import time

            time.sleep(max(self.args.voyage_sleep, 0.0))

        embeddings = np.vstack(embeddings_store)
        label = model_name.replace(".", "_")
        self._save_embeddings(f"voyage_{label}", embeddings)

    def _generate_qwen(self, batch_size: int) -> None:
        endpoint = self.args.qwen_endpoint or self._env("QWEN_EMBED_ENDPOINT")
        if not endpoint:
            raise RuntimeError(
                "Qwen endpoint not provided. Set QWEN_EMBED_ENDPOINT or use --qwen-endpoint."
            )

        model_name = self.args.qwen_model
        api_key = self.args.qwen_api_key or self._env("QWEN_API_KEY")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        texts = [
            f"{record.get('title', '')} {record.get('abstract', '')}".strip()
            for record in self.records
        ]
        embeddings_store: List[np.ndarray] = []
        self.log_info("Encoding with Qwen", endpoint=endpoint, model=model_name)
        for start in tqdm(range(0, len(texts), batch_size), desc="Qwen embeddings"):
            batch = texts[start : start + batch_size]
            response = requests.post(
                endpoint,
                headers=headers,
                json={
                    "model": model_name,
                    "input": batch,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            vectors = [
                np.asarray(item["embedding"], dtype=np.float32) for item in data["data"]
            ]
            embeddings_store.append(np.vstack(vectors))

        embeddings = np.vstack(embeddings_store)
        label = model_name.split("/")[-1].replace(".", "_")
        self._save_embeddings(f"qwen_{label}", embeddings)

    def _env(self, key: str) -> Optional[str]:
        import os

        value = os.environ.get(key)
        return value.strip() if value else None

    def _save_embeddings(self, label: str, embeddings: np.ndarray) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.output_dir / f"{label}_embeddings.npy"
        ids_path = self.output_dir / f"{label}_ids.json"
        np.save(file_path, embeddings)
        ids_path.write_text(
            json.dumps([record.get("id") for record in self.records], indent=2),
            encoding="utf-8",
        )
        self.log_info("Embeddings saved", path=str(file_path), shape=embeddings.shape)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate embeddings for evaluation.")
    parser.add_argument("--catalog", required=True, help="Path to papers_catalog.ndjson")
    parser.add_argument("--output", required=True, help="Directory to store embeddings")
    parser.add_argument(
        "--model",
        action="append",
        required=True,
        help=(
            "Embedding model to use ('specter2', 'openai', 'voyage', 'qwen'). "
            "Can be specified multiple times."
        ),
    )
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for local encoders/API")
    parser.add_argument("--voyage-model", default="voyage-3.5", help="Voyage model name")
    parser.add_argument("--voyage-api-key", help="Voyage API key (falls back to VOYAGE_API_KEY)")
    parser.add_argument(
        "--voyage-sleep",
        type=float,
        default=1.0,
        help="Seconds to sleep after each Voyage request to respect RPM limits",
    )
    parser.add_argument(
        "--voyage-dimension",
        type=int,
        default=None,
        help="Optional Voyage output dimension (e.g., 512 or 1024)",
    )
    parser.add_argument("--qwen-endpoint", help="Qwen/TEI embedding endpoint URL")
    parser.add_argument("--qwen-model", default="Qwen/Qwen3-Embedding-8B", help="Qwen model id")
    parser.add_argument("--qwen-api-key", help="Qwen endpoint bearer token")
    args = parser.parse_args()

    generator = EmbeddingGenerator(Path(args.catalog), Path(args.output), args)
    for model in args.model:
        generator.generate(model, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
