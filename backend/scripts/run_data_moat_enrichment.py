#!/usr/bin/env python3
"""
Master script to run all data moat enrichment jobs.
Run from backend directory: python scripts/run_data_moat_enrichment.py

This orchestrates all the enrichment steps:
1. GitHub signals enrichment
2. Paper relationship extraction
3. Benchmark result extraction
4. Daily metric snapshots

Can be run as a daily cron job or manually.
"""
import asyncio
import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).parent


def run_script(script_name: str, args: list = None, timeout: int = 3600):
    """Run a Python script and capture output."""
    script_path = SCRIPTS_DIR / script_name

    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(
            cmd,
            cwd=SCRIPTS_DIR.parent,  # backend directory
            capture_output=False,  # Stream output directly
            timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"ERROR: {script_name} timed out after {timeout}s")
        return False
    except Exception as e:
        print(f"ERROR: Failed to run {script_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run all data moat enrichment jobs")
    parser.add_argument("--github", action="store_true", help="Run GitHub enrichment")
    parser.add_argument("--relationships", action="store_true", help="Run relationship extraction")
    parser.add_argument("--benchmarks", action="store_true", help="Run benchmark extraction")
    parser.add_argument("--snapshots", action="store_true", help="Run metric snapshots")
    parser.add_argument("--all", action="store_true", help="Run all enrichment jobs")
    parser.add_argument("--limit", type=int, default=50, help="Limit papers per job")
    parser.add_argument("--quick", action="store_true", help="Quick mode (smaller limits)")
    args = parser.parse_args()

    # If no specific job selected, show help
    if not any([args.github, args.relationships, args.benchmarks, args.snapshots, args.all]):
        parser.print_help()
        print("\nExample usage:")
        print("  python scripts/run_data_moat_enrichment.py --all")
        print("  python scripts/run_data_moat_enrichment.py --github --limit 100")
        print("  python scripts/run_data_moat_enrichment.py --quick --all")
        return

    start = time.time()
    print("=" * 70)
    print("DATA MOAT ENRICHMENT PIPELINE")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    # Set limits
    limit = 10 if args.quick else args.limit
    results = {}

    # 1. GitHub Signals
    if args.github or args.all:
        success = run_script(
            "enrich_github_signals.py",
            ["--limit", str(limit)]
        )
        results["GitHub Signals"] = "OK" if success else "FAILED"

    # 2. Paper Relationships
    if args.relationships or args.all:
        success = run_script(
            "extract_paper_relationships.py",
            ["--limit", str(limit), "--min-citations", "5"]
        )
        results["Paper Relationships"] = "OK" if success else "FAILED"

    # 3. Benchmark Results
    if args.benchmarks or args.all:
        success = run_script(
            "extract_benchmark_results.py",
            ["--limit", str(limit)]  # Use regex mode by default (faster)
        )
        results["Benchmark Results"] = "OK" if success else "FAILED"

    # 4. Metric Snapshots
    if args.snapshots or args.all:
        snapshot_limit = str(limit * 10) if not args.quick else str(limit * 2)
        success = run_script(
            "capture_metric_snapshots.py",
            ["--limit", snapshot_limit]
        )
        results["Metric Snapshots"] = "OK" if success else "FAILED"

    # Summary
    elapsed = time.time() - start
    print("\n" + "=" * 70)
    print("ENRICHMENT PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\nResults:")
    for job, status in results.items():
        status_icon = "+" if status == "OK" else "-"
        print(f"  [{status_icon}] {job}: {status}")
    print(f"\nTotal time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print("=" * 70)


if __name__ == "__main__":
    main()
