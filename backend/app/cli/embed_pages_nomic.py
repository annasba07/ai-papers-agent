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
from typing import List

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
        self._images = self._gather_images()

    def _gather_images(self) -> List[Path]:
        if not self.images_root.exists():
            raise FileNotFoundError(f"Images root not found: {self.images_root}")
        images = sorted(self.images_root.rglob("*.png"))
        if not images:
            raise RuntimeError(f"No PNG files found under {self.images_root}")
        self.log_info("Found rendered pages", total=len(images))
        return images

    def run(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        embeddings_path = self.output_dir / "nomic_multimodal_embeddings.npy"
        ids_path = self.output_dir / "nomic_multimodal_ids.json"

        self.log_info("Loading Nomic model", model_id=self.model_id, device=str(self.device))
        processor = AutoProcessor.from_pretrained(self.model_id)
        model = AutoModel.from_pretrained(self.model_id, trust_remote_code=True)
        model.to(self.device)
        model.eval()

        all_vectors: List[np.ndarray] = []
        all_ids: List[str] = []

        def encode(images: List[Image.Image]) -> np.ndarray:
            inputs = processor(images=images, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                try:
                    outputs = model.get_image_features(**inputs)  # type: ignore[attr-defined]
                except AttributeError:
                    # Fallback for models returning a dict with 'image_embeds'
                    outputs = model(**inputs)
                    if isinstance(outputs, dict) and "image_embeds" in outputs:
                        embeds = outputs["image_embeds"]
                    else:
                        raise RuntimeError(
                            "Model output did not contain image features. "
                            "Ensure the selected model supports image embeddings."
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
                all_vectors.append(vectors)
                all_ids.extend(str(p.relative_to(self.images_root)) for p in batch_paths)
                batch.clear()
                batch_paths.clear()

        if batch:
            vectors = encode(batch)
            all_vectors.append(vectors)
            all_ids.extend(str(p.relative_to(self.images_root)) for p in batch_paths)

        embeddings = np.vstack(all_vectors)
        np.save(embeddings_path, embeddings)
        ids_path.write_text(json.dumps(all_ids, indent=2), encoding="utf-8")

        self.log_info(
            "Nomic embeddings generated",
            total_images=len(all_ids),
            embeddings_path=str(embeddings_path),
            ids_path=str(ids_path),
        )


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
