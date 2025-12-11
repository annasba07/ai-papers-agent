#!/usr/bin/env python3
"""
Regenerate SPECTER2 embeddings cache with MPS acceleration.
Run from backend directory: python scripts/regenerate_embeddings.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


def get_device():
    """Get best available device."""
    if torch.backends.mps.is_available():
        print("Using Apple MPS (GPU)")
        return torch.device("mps")
    elif torch.cuda.is_available():
        print("Using CUDA (GPU)")
        return torch.device("cuda")
    else:
        print("Using CPU (slow!)")
        return torch.device("cpu")


def load_papers(catalog_path: Path) -> tuple[list[dict], list[str], list[str]]:
    """Load papers from catalog."""
    records = []
    with catalog_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    # Build search text for each paper
    ids = []
    texts = []
    for r in records:
        ids.append(r.get("id"))
        # Combine title + abstract for embedding
        title = r.get("title", "")
        abstract = r.get("abstract", "")
        texts.append(f"{title} {abstract}".strip())

    return records, ids, texts


def encode_with_specter2(texts: list[str], device: torch.device, batch_size: int = 32) -> np.ndarray:
    """Encode texts using SPECTER2 with progress bar."""
    from adapters import AutoAdapterModel
    from transformers import AutoTokenizer

    print("Loading SPECTER2 model...")
    base_model = "allenai/specter2_base"
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = AutoAdapterModel.from_pretrained(base_model)

    # Load and activate adapter
    adapter = model.load_adapter("allenai/specter2", source="hf")
    model.set_active_adapters(adapter)
    model.to(device)
    model.eval()
    print(f"Model loaded on {device}")

    embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size

    with torch.no_grad():
        for i in tqdm(range(0, len(texts), batch_size), total=total_batches, desc="Encoding"):
            batch = texts[i:i + batch_size]
            tokens = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            tokens = {k: v.to(device) for k, v in tokens.items()}

            outputs = model(**tokens)
            cls_emb = outputs.last_hidden_state[:, 0]
            cls_emb = F.normalize(cls_emb, p=2, dim=1)
            embeddings.append(cls_emb.cpu().numpy())

    return np.vstack(embeddings)


def main():
    start_time = time.time()

    # Paths
    atlas_path = Path(settings.ATLAS_DERIVED_DIR).expanduser().resolve()
    catalog_path = atlas_path / "papers_catalog.ndjson"
    cache_dir = Path(settings.ATLAS_EMBED_CACHE_DIR).expanduser().resolve()

    print(f"Atlas catalog: {catalog_path}")
    print(f"Cache dir: {cache_dir}")

    if not catalog_path.exists():
        print(f"ERROR: Catalog not found at {catalog_path}")
        sys.exit(1)

    cache_dir.mkdir(parents=True, exist_ok=True)

    # Load papers
    print("\nLoading papers...")
    records, ids, texts = load_papers(catalog_path)
    print(f"Loaded {len(records)} papers")

    # Get device
    device = get_device()

    # Encode
    print(f"\nEncoding {len(texts)} papers...")
    embeddings = encode_with_specter2(texts, device, batch_size=32)
    print(f"Embeddings shape: {embeddings.shape}")

    # Save
    embeddings_path = cache_dir / "specter2_embeddings.npy"
    ids_path = cache_dir / "specter2_ids.json"

    print(f"\nSaving to {embeddings_path}")
    np.save(embeddings_path, embeddings)

    print(f"Saving IDs to {ids_path}")
    with ids_path.open("w", encoding="utf-8") as f:
        json.dump(ids, f)

    elapsed = time.time() - start_time
    print(f"\nDone! Took {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"Papers: {len(ids)}, Embedding dim: {embeddings.shape[1]}")


if __name__ == "__main__":
    main()
