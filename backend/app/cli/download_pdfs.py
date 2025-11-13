"""
Download PDFs for the atlas catalog from arXiv.

Usage:
    python -m app.cli.download_pdfs \
        --catalog ../data/derived_12mo/papers_catalog.ndjson \
        --output-root ../data/papers_pdf \
        --rate-limit 1.0
"""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

import requests
from tqdm import tqdm

from app.utils.logger import LoggerMixin

ARXIV_PRIMARY_TEMPLATE = "https://export.arxiv.org/pdf/{arxiv_id}.pdf"
ARXIV_FALLBACK_TEMPLATE = "https://arxiv.org/pdf/{arxiv_id}.pdf"
HTML_SENTINEL = b"<html"


class PDFDownloader(LoggerMixin):
    def __init__(
        self,
        catalog_path: Path,
        output_root: Path,
        overwrite: bool,
        rate_limit: float,
        timeout: float,
        max_retries: int,
        limit: Optional[int],
        id_allowlist: Optional[Set[str]],
        user_agent: str,
        base_url: str,
    ) -> None:
        self.catalog_path = catalog_path
        self.output_root = output_root
        self.overwrite = overwrite
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.max_retries = max_retries
        self.limit = limit
        self.id_allowlist = id_allowlist
        self.user_agent = user_agent
        self.base_url = base_url
        self.records = self._load_catalog()

    def _load_catalog(self) -> List[Dict]:
        self.log_info("Loading catalog", path=str(self.catalog_path))
        records: List[Dict] = []
        with self.catalog_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                records.append(json.loads(line))
        if self.id_allowlist:
            records = [record for record in records if self._paper_id(record) in self.id_allowlist]
        if self.limit:
            records = records[: self.limit]
        self.log_info("Catalog entries", total=len(records))
        return records

    def _paper_id(self, record: Dict) -> Optional[str]:
        return (record.get("id") or record.get("paper_id") or "").strip() or None

    def _pdf_url(self, record: Dict) -> Optional[str]:
        arxiv_id = self._paper_id(record)
        if not arxiv_id:
            return None
        if self.base_url:
            return self.base_url.format(arxiv_id=arxiv_id)
        return ARXIV_PRIMARY_TEMPLATE.format(arxiv_id=arxiv_id)

    def _target_path(self, record: Dict) -> Optional[Path]:
        arxiv_id = self._paper_id(record)
        if not arxiv_id:
            return None
        safe_id = arxiv_id.replace("/", "_")
        return self.output_root / f"{safe_id}.pdf"

    def _candidate_urls(self, arxiv_id: str) -> Iterable[str]:
        if self.base_url:
            yield self.base_url.format(arxiv_id=arxiv_id)
        yield ARXIV_PRIMARY_TEMPLATE.format(arxiv_id=arxiv_id)
        yield ARXIV_FALLBACK_TEMPLATE.format(arxiv_id=arxiv_id)

    def _response_is_pdf(self, response: requests.Response, first_chunk: bytes) -> bool:
        content_type = response.headers.get("Content-Type", "").lower()
        if "pdf" in content_type:
            return True
        return HTML_SENTINEL not in first_chunk.lower()

    def download(self) -> None:
        self.output_root.mkdir(parents=True, exist_ok=True)
        session = requests.Session()
        session.headers.update({"User-Agent": self.user_agent})
        downloaded = 0
        skipped = 0
        failed = 0

        for record in tqdm(self.records, desc="Downloading PDFs"):
            arxiv_id = self._paper_id(record)
            target = self._target_path(record)
            if not arxiv_id or not target:
                skipped += 1
                continue

            if target.exists() and not self.overwrite:
                skipped += 1
                continue

            success = False
            for attempt in range(self.max_retries):
                for url in self._candidate_urls(arxiv_id):
                    try:
                        response = session.get(url, timeout=self.timeout, stream=True)
                    except requests.RequestException as exc:
                        self.log_warning(
                            "PDF request failed",
                            pdf=url,
                            attempt=attempt + 1,
                            error=str(exc),
                        )
                        time.sleep(self.rate_limit)
                        continue

                    if response.status_code != 200:
                        self.log_warning(
                            "HTTP error when downloading PDF",
                            pdf=url,
                            status=response.status_code,
                            attempt=attempt + 1,
                        )
                        time.sleep(self.rate_limit)
                        continue

                    temp_path = target.with_suffix(".part")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        with temp_path.open("wb") as handle:
                            first_chunk: Optional[bytes] = None
                            wrote_bytes = 0
                            for chunk in response.iter_content(chunk_size=4096):
                                if not chunk:
                                    continue
                                if first_chunk is None:
                                    first_chunk = chunk
                                    if not self._response_is_pdf(response, first_chunk):
                                        self.log_warning(
                                            "Received HTML instead of PDF",
                                            pdf=url,
                                            attempt=attempt + 1,
                                        )
                                        raise ValueError("HTML payload detected")
                                handle.write(chunk)
                                wrote_bytes += len(chunk)
                            if wrote_bytes == 0:
                                raise ValueError("Empty response body")
                        temp_path.replace(target)
                        downloaded += 1
                        success = True
                        break
                    except ValueError as exc:
                        temp_path.unlink(missing_ok=True)
                        self.log_warning("Invalid PDF payload", pdf=url, error=str(exc))
                    except requests.RequestException as exc:
                        temp_path.unlink(missing_ok=True)
                        self.log_warning("Stream interrupted", pdf=url, error=str(exc))
                    except OSError as exc:
                        temp_path.unlink(missing_ok=True)
                        self.log_warning("File write failed", pdf=url, error=str(exc))
                    time.sleep(self.rate_limit)

                if success:
                    break

            if not success:
                failed += 1
            sleep = max(self.rate_limit, 0.0) + random.uniform(0, 0.25)
            time.sleep(sleep)

        self.log_info(
            "PDF download complete",
            downloaded=downloaded,
            skipped=skipped,
            failed=failed,
            output=str(self.output_root),
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download PDFs for the atlas catalog.")
    parser.add_argument("--catalog", required=True, help="Path to papers_catalog.ndjson")
    parser.add_argument("--output-root", required=True, help="Directory to store PDFs")
    parser.add_argument("--overwrite", action="store_true", help="Re-download existing PDFs")
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Seconds to sleep between requests",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retries per PDF",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional limit for debugging (download only first N entries)",
    )
    parser.add_argument(
        "--id-file",
        help="Optional path to newline-delimited arXiv IDs to download",
    )
    parser.add_argument(
        "--user-agent",
        default="AI-Atlas-PDF-Downloader/1.0 (+https://example.com)",
        help="User agent header for arXiv requests",
    )
    parser.add_argument(
        "--base-url",
        default=ARXIV_PRIMARY_TEMPLATE,
        help="Primary PDF template (use export.arxiv.org for friendlier bulk pulls)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    id_allowlist: Optional[Set[str]] = None
    if args.id_file:
        id_path = Path(args.id_file)
        if not id_path.exists():
            raise FileNotFoundError(f"ID file not found: {id_path}")
        with id_path.open("r", encoding="utf-8") as handle:
            id_allowlist = {line.strip() for line in handle if line.strip()}
    downloader = PDFDownloader(
        catalog_path=Path(args.catalog),
        output_root=Path(args.output_root),
        overwrite=args.overwrite,
        rate_limit=args.rate_limit,
        timeout=args.timeout,
        max_retries=args.max_retries,
        limit=args.limit,
        id_allowlist=id_allowlist,
        user_agent=args.user_agent,
        base_url=args.base_url,
    )
    downloader.download()


if __name__ == "__main__":
    main()
