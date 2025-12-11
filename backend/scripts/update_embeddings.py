#!/usr/bin/env python3
"""
Incremental SPECTER2 embeddings update - only encodes NEW papers.
Run from backend directory: python scripts/update_embeddings.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.core.config import settings


def get_device():
    if torch.backends.mps.is_available():
        print("Using Apple MPS (GPU)")
        return torch.device("mps")
    elif torch.cuda.is_available():
        print("Using CUDA")
        return torch.device("cuda")
    else:
        print("Using CPU")
        return torch.device("cpu")


def load_papers(catalog_path: Path) -> dict[str, dict]:
    """Load papers as id -> record dict."""
    papers = {}
    with catalog_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    r = json.loads(line)
                    papers[r.get("id")] = r
                except json.JSONDecodeError:
                    continue
    return papers


def encode_batch(texts: list[str], tokenizer, model, device) -> np.ndarray:
    """Encode a batch of texts."""
    with torch.no_grad():
        tokens = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        tokens = {k: v.to(device) for k, v in tokens.items()}
        outputs = model(**tokens)
        cls_emb = outputs.last_hidden_state[:, 0]
        cls_emb = F.normalize(cls_emb, p=2, dim=1)
        return cls_emb.cpu().numpy()


def main():
    start = time.time()

    # Paths
    atlas_path = Path(settings.ATLAS_DERIVED_DIR).expanduser().resolve()
    catalog_path = atlas_path / "papers_catalog.ndjson"
    cache_dir = Path(settings.ATLAS_EMBED_CACHE_DIR).expanduser().resolve()
    embeddings_path = cache_dir / "specter2_embeddings.npy"
    ids_path = cache_dir / "specter2_ids.json"

    # Load current papers
    print("Loading papers catalog...")
    current_papers = load_papers(catalog_path)
    print(f"Current papers: {len(current_papers)}")

    # Load existing cache
    if not embeddings_path.exists() or not ids_path.exists():
        print("No existing cache found - run regenerate_embeddings.py instead")
        sys.exit(1)

    existing_embeddings = np.load(embeddings_path)
    existing_ids = json.loads(ids_path.read_text())
    print(f"Cached embeddings: {len(existing_ids)} papers, shape {existing_embeddings.shape}")

    # Find new papers
    existing_set = set(existing_ids)
    new_papers = {pid: p for pid, p in current_papers.items() if pid not in existing_set}

    if not new_papers:
        print("No new papers to encode!")
        return

    print(f"\nNew papers to encode: {len(new_papers)}")

    # Prepare texts for new papers
    new_ids = list(new_papers.keys())
    new_texts = [
        f"{p.get('title', '')} {p.get('abstract', '')}".strip()
        for p in new_papers.values()
    ]

    # Load model
    device = get_device()
    print("\nLoading SPECTER2...")
    from adapters import AutoAdapterModel
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("allenai/specter2_base")
    model = AutoAdapterModel.from_pretrained("allenai/specter2_base")
    adapter = model.load_adapter("allenai/specter2", source="hf")
    model.set_active_adapters(adapter)
    model.to(device)
    model.eval()

    # Encode new papers
    print(f"\nEncoding {len(new_texts)} new papers...")
    batch_size = 32
    new_embeddings = []

    for i in tqdm(range(0, len(new_texts), batch_size)):
        batch = new_texts[i:i + batch_size]
        emb = encode_batch(batch, tokenizer, model, device)
        new_embeddings.append(emb)

    new_embeddings = np.vstack(new_embeddings)
    print(f"New embeddings shape: {new_embeddings.shape}")

    # Merge
    all_embeddings = np.vstack([existing_embeddings, new_embeddings])
    all_ids = existing_ids + new_ids

    print(f"\nMerged: {len(all_ids)} papers, embeddings shape {all_embeddings.shape}")

    # Save
    print(f"Saving to {embeddings_path}")
    np.save(embeddings_path, all_embeddings)

    print(f"Saving IDs to {ids_path}")
    with ids_path.open("w", encoding="utf-8") as f:
        json.dump(all_ids, f)

    elapsed = time.time() - start
    print(f"\nDone! Added {len(new_papers)} papers in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
