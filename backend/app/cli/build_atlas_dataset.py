"""
Utility CLI that converts local atlas bootstrap dumps (NDJSON per window)
into derived datasets for the visual prototype.

Usage:
    python -m app.cli.build_atlas_dataset --input ../data/atlas_bootstrap --output ../data/derived
"""
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def iterate_ndjson_files(input_dir: Path) -> List[Path]:
    """Return a sorted list of NDJSON files inside the input directory."""
    return sorted(
        path
        for path in input_dir.glob("**/*.ndjson")
        if path.is_file()
    )


def sanitize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure dates are ISO strings and drop unused keys."""
    sanitized = dict(record)
    if isinstance(sanitized.get("published"), datetime):
        sanitized["published"] = sanitized["published"].isoformat()
    if sanitized.get("window_start") and isinstance(sanitized["window_start"], datetime):
        sanitized["window_start"] = sanitized["window_start"].isoformat()
    if sanitized.get("window_end") and isinstance(sanitized["window_end"], datetime):
        sanitized["window_end"] = sanitized["window_end"].isoformat()
    return sanitized


def build_datasets(input_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """Read raw dumps and build derived datasets and statistics."""
    files = iterate_ndjson_files(input_dir)
    if not files:
        raise FileNotFoundError(f"No NDJSON files found under {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    seen_ids = set()
    papers: List[Dict[str, Any]] = []
    category_month_counts: Dict[str, Counter] = defaultdict(Counter)
    author_counts: Counter = Counter()
    window_stats: List[Dict[str, Any]] = []

    for ndjson_path in files:
        path_parts = ndjson_path.relative_to(input_dir).parts
        category = path_parts[0] if len(path_parts) > 1 else "unknown"
        month_segment = path_parts[1] if len(path_parts) > 1 else "unknown"

        record_count = 0
        with ndjson_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                data = sanitize_record(json.loads(line))
                paper_id = data.get("id")
                if not paper_id or paper_id in seen_ids:
                    continue

                seen_ids.add(paper_id)
                papers.append(data)
                record_count += 1

                category_key = data.get("category") or category
                published = data.get("published")
                month = published[:7] if isinstance(published, str) and len(published) >= 7 else "unknown"
                category_month_counts[category_key][month] += 1

                for author in data.get("authors", []):
                    author_counts[author.strip()] += 1

        window_stats.append(
            {
                "path": str(ndjson_path),
                "category": category,
                "month_segment": month_segment,
                "records": record_count,
            }
        )

    # Sort papers chronologically (newest first)
    papers.sort(key=lambda p: p.get("published", ""), reverse=True)

    # Write combined papers catalog (NDJSON)
    catalog_path = output_dir / "papers_catalog.ndjson"
    with catalog_path.open("w", encoding="utf-8") as fh:
        for paper in papers:
            fh.write(json.dumps(paper, ensure_ascii=False) + "\n")

    # Write timeline per category
    category_timeline = {
        category: [
            {"month": month, "count": count}
            for month, count in sorted(month_counts.items())
        ]
        for category, month_counts in category_month_counts.items()
    }
    timeline_path = output_dir / "category_timeline.json"
    timeline_path.write_text(json.dumps(category_timeline, indent=2), encoding="utf-8")

    # Write author leaderboard
    top_authors = [
        {"author": author, "paper_count": count}
        for author, count in author_counts.most_common(200)
    ]
    authors_path = output_dir / "author_leaderboard.json"
    authors_path.write_text(json.dumps(top_authors, indent=2), encoding="utf-8")

    # Window summary
    window_summary_path = output_dir / "window_summary.json"
    window_summary_path.write_text(json.dumps(window_stats, indent=2), encoding="utf-8")

    stats = {
        "input_files": len(files),
        "unique_papers": len(papers),
        "categories": sorted(category_month_counts.keys()),
        "output_catalog": str(catalog_path),
        "output_timeline": str(timeline_path),
        "output_authors": str(authors_path),
    }
    stats_path = output_dir / "build_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Build derived datasets for atlas prototype.")
    parser.add_argument("--input", default="../data/atlas_bootstrap", help="Directory with raw NDJSON dumps.")
    parser.add_argument("--output", default="../data/derived", help="Directory to write derived datasets.")
    args = parser.parse_args()

    input_dir = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()

    stats = build_datasets(input_dir, output_dir)

    print("\nDerived dataset built successfully:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
