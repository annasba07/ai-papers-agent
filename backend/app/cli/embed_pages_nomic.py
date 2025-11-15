"""
Generate multimodal embeddings for rendered PDF pages using Nomic's multimodal encoder.

Example usage:
    python -m app.cli.embed_pages_nomic \
        --images-root ../data/rendered_pages \
        --output ../embeddings \
        --model-id nomic-ai/nomic-embed-multimodal-v1.5 \
        --device cuda \
        --batch-size 8
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Set, Tuple

import numpy as np
import torch
from PIL import Image
from tqdm import tqdm
from transformers import AutoModel, AutoProcessor  # type: ignore

from app.utils.logger import LoggerMixin


class NomicMultimodalEmbedder(LoggerMixin):
    def __init__(
        self,
        images_root: Path,
        output_dir: Path,
        model_id: str,
        device: str,
        batch_size: int,
    ) -> None:
        self.images_root = images_root
        self.output_dir = output_dir
        self.model_id = model_id
        self.device = torch.device(device)
        self.batch_size = batch_size
        self.shards_dir = self.output_dir / "nomic_chunks"
        self.shards_dir.mkdir(parents=True, exist_ok=True)
        self.processed_ids, self.next_shard_index = self._load_existing_shards()
        self._images = self._gather_images()

    def _gather_images(self) -> List[Path]:
        if not self.images_root.exists():
            raise FileNotFoundError(f"Images root not found: {self.images_root}")
        manifest = self.images_root / "render_manifest.jsonl"
        images: List[Path] = []
        if manifest.exists():
            with manifest.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    rel_path = record.get("image_path")
                    if rel_path:
                        candidate = self.images_root / rel_path
                        rel = str(candidate.relative_to(self.images_root))
                        if rel not in self.processed_ids:
                            images.append(candidate)
        else:
            for path in sorted(self.images_root.rglob("*.png")):
                rel = str(path.relative_to(self.images_root))
                if rel not in self.processed_ids:
                    images.append(path)
        if not images:
            raise RuntimeError("No unprocessed images found under rendered_pages. Remove shards to restart.")
        self.log_info("Found rendered pages", total=len(images))
        return images

    def _load_existing_shards(self) -> Tuple[Set[str], int]:
        processed: Set[str] = set()
        shard_index = 0
        existing = sorted(self.shards_dir.glob("chunk_*.npz"))
        for shard in existing:
            try:
                data = np.load(shard, allow_pickle=True)
                ids = data["ids"]
                processed.update(ids.tolist())
            except Exception as exc:  # pragma: no cover - corrupted shard
                self.log_warning("Failed to read shard", shard=str(shard), error=str(exc))
        if existing:
            shard_index = max(int(f.stem.split("_")[-1]) for f in existing) + 1
        self.log_info("Existing shards loaded", processed=len(processed), next_index=shard_index)
        return processed, shard_index

    def run(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.log_info("Loading Nomic model", model_id=self.model_id, device=str(self.device))
        processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
        model = AutoModel.from_pretrained(self.model_id, trust_remote_code=True)
        model.to(self.device)
        model.eval()

        shard_size = max(1, 2048 // max(1, self.batch_size))
        shard_vectors: List[np.ndarray] = []
        shard_ids: List[str] = []
        shard_index = self.next_shard_index

        def encode(images: List[Image.Image]) -> np.ndarray:
            inputs = processor(images=images, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                try:
                    outputs = model.get_image_features(**inputs)  # type: ignore[attr-defined]
                except AttributeError:
                    # Fallback for models returning a dict with 'image_embeds'
                    outputs = model(**inputs)
                    embeds = None
                    if isinstance(outputs, dict):
                        if "image_embeds" in outputs:
                            embeds = outputs["image_embeds"]
                        elif "last_hidden_state" in outputs:
                            embeds = outputs["last_hidden_state"]
                    elif hasattr(outputs, "image_embeds"):
                        embeds = outputs.image_embeds  # type: ignore[attr-defined]
                    elif hasattr(outputs, "last_hidden_state"):
                        embeds = outputs.last_hidden_state  # type: ignore[attr-defined]
                    if embeds is None:
                        raise RuntimeError(
                            "Model output did not contain identifiable image embeddings. "
                            "Ensure the selected model exposes image features."
                        )
                else:
                    embeds = outputs

            if isinstance(embeds, torch.Tensor):
                vectors = embeds.detach().cpu().numpy()
            else:
                raise RuntimeError("Unexpected embedding output type")
            return vectors

        batch: List[Image.Image] = []
        batch_paths: List[Path] = []
        for image_path in tqdm(self._images, desc="Embedding pages"):
            image = Image.open(image_path).convert("RGB")
            batch.append(image)
            batch_paths.append(image_path)
            if len(batch) >= self.batch_size:
                vectors = encode(batch)
                shard_vectors.append(vectors.astype(np.float16))
                shard_ids.extend(str(p.relative_to(self.images_root)) for p in batch_paths)
                batch.clear()
                batch_paths.clear()
                if sum(vec.shape[0] for vec in shard_vectors) >= shard_size:
                    self._flush_shard(shard_index, shard_vectors, shard_ids)
                    shard_index += 1
                    shard_vectors.clear()
                    shard_ids.clear()

        if batch:
            vectors = encode(batch)
            shard_vectors.append(vectors.astype(np.float16))
            shard_ids.extend(str(p.relative_to(self.images_root)) for p in batch_paths)

        if shard_vectors:
            self._flush_shard(shard_index, shard_vectors, shard_ids)
            shard_index += 1

        self.log_info(
            "Nomic embeddings sharded",
            shards=shard_index,
            output=str(self.shards_dir),
            remaining=len(self._images),
        )

    def _flush_shard(
        self,
        shard_index: int,
        shard_vectors: List[np.ndarray],
        shard_ids: List[str],
    ) -> None:
        vectors = np.vstack(shard_vectors)
        shard_path = self.shards_dir / f"chunk_{shard_index:05}.npz"
        np.savez_compressed(shard_path, embeddings=vectors, ids=np.array(shard_ids, dtype=object))
        self.log_info("Shard written", shard=str(shard_path), count=len(shard_ids))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embed rendered pages using Nomic multimodal model.")
    parser.add_argument("--images-root", required=True, help="Root directory with rendered PNGs")
    parser.add_argument("--output", required=True, help="Directory to store embeddings")
    parser.add_argument(
        "--model-id",
        default="nomic-ai/nomic-embed-multimodal-v1.5",
        help="Hugging Face model id for Nomic multimodal embeddings",
    )
    parser.add_argument("--device", default="cpu", help="torch device, e.g., 'cpu' or 'cuda'")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size for encoding")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    embedder = NomicMultimodalEmbedder(
        images_root=Path(args.images_root),
        output_dir=Path(args.output),
        model_id=args.model_id,
        device=args.device,
        batch_size=args.batch_size,
    )
    embedder.run()


if __name__ == "__main__":
    main()
