"""
Render PDF pages to images for multimodal indexing.

Example usage:
    python -m app.cli.render_pdf_pages \
        --catalog ../data/derived_12mo/papers_catalog.ndjson \
        --pdf-root ../data/papers_pdf \
        --output-root ../data/rendered_pages \
        --dpi 144
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import fitz  # PyMuPDF
from tqdm import tqdm

from app.utils.logger import LoggerMixin


class PDFRenderer(LoggerMixin):
    def __init__(
        self,
        catalog_path: Path,
        pdf_root: Path,
        output_root: Path,
        dpi: int,
        max_pages: Optional[int],
    ) -> None:
        self.catalog_path = catalog_path
        self.pdf_root = pdf_root
        self.output_root = output_root
        self.dpi = dpi
        self.max_pages = max_pages
        self.records = self._load_catalog()

    def _load_catalog(self) -> List[Dict]:
        self.log_info("Loading catalog", path=str(self.catalog_path))
        records: List[Dict] = []
        with self.catalog_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
        self.log_info("Catalog loaded", total=len(records))
        return records

    def _paper_id(self, record: Dict) -> Optional[str]:
        paper_id = record.get("id") or record.get("paper_id") or record.get("uid")
        return paper_id

    def _pdf_path(self, record: Dict) -> Optional[Path]:
        candidates: List[Path] = []
        # Some catalogs may already store a local path
        if record.get("pdf_path"):
            candidates.append(Path(record["pdf_path"]))

        paper_id = self._paper_id(record)
        if paper_id:
            safe_id = paper_id.replace("/", "_")
            candidates.append(self.pdf_root / f"{safe_id}.pdf")
            if "v" in safe_id:
                base = safe_id.split("v")[0]
                candidates.append(self.pdf_root / f"{base}.pdf")

        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
        return None

    def render(self) -> None:
        if not self.pdf_root.exists():
            raise FileNotFoundError(f"PDF root not found: {self.pdf_root}")
        self.output_root.mkdir(parents=True, exist_ok=True)
        manifest_path = self.output_root / "render_manifest.jsonl"
        rendered = 0
        skipped = 0
        with manifest_path.open("w", encoding="utf-8") as manifest:
            for record in tqdm(self.records, desc="Rendering PDFs"):
                pdf_path = self._pdf_path(record)
                if not pdf_path:
                    skipped += 1
                    continue
                paper_id = self._paper_id(record)
                if not paper_id:
                    skipped += 1
                    continue

                safe_id = paper_id.replace("/", "_")
                target_dir = self.output_root / safe_id
                target_dir.mkdir(parents=True, exist_ok=True)

                try:
                    doc = fitz.open(pdf_path)
                except Exception as exc:  # pragma: no cover - corrupted PDF
                    self.log_warning(
                        "Failed to open PDF",
                        paper_id=paper_id,
                        pdf=str(pdf_path),
                        error=str(exc),
                    )
                    skipped += 1
                    continue

                zoom = self.dpi / 72.0
                matrix = fitz.Matrix(zoom, zoom)
                total_pages = doc.page_count
                limit = min(total_pages, self.max_pages) if self.max_pages else total_pages
                for page_idx in range(limit):
                    page = doc.load_page(page_idx)
                    pix = page.get_pixmap(matrix=matrix, clip=None, annots=False)
                    out_path = target_dir / f"page_{page_idx+1:03}.png"
                    pix.save(out_path)
                    manifest.write(
                        json.dumps(
                            {
                                "paper_id": paper_id,
                                "page": page_idx + 1,
                                "image_path": str(out_path.relative_to(self.output_root)),
                                "pdf_path": str(pdf_path),
                            }
                        )
                        + "\n"
                    )
                    rendered += 1
                doc.close()

        self.log_info(
            "Rendering complete",
            rendered_images=rendered,
            skipped_entries=skipped,
            manifest=str(manifest_path),
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG images.")
    parser.add_argument("--catalog", required=True, help="Path to papers_catalog.ndjson")
    parser.add_argument("--pdf-root", required=True, help="Root directory with PDFs")
    parser.add_argument("--output-root", required=True, help="Directory to store images")
    parser.add_argument("--dpi", type=int, default=144, help="Rendering DPI")
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Optional max pages per PDF (defaults to all pages)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    renderer = PDFRenderer(
        catalog_path=Path(args.catalog),
        pdf_root=Path(args.pdf_root),
        output_root=Path(args.output_root),
        dpi=args.dpi,
        max_pages=args.max_pages,
    )
    renderer.render()


if __name__ == "__main__":
    main()
