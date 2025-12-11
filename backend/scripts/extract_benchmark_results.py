#!/usr/bin/env python3
"""
Extract benchmark results from papers and populate SOTA history.
Run from backend directory: python scripts/extract_benchmark_results.py

This script:
1. Finds papers that mention common benchmarks
2. Uses LLM to extract numerical results
3. Populates sota_history table

Enables queries like "What's SOTA on ImageNet?" and "Show SOTA progression".
"""
import asyncio
import os
import sys
import time
import json
import re
import argparse
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai

from app.db.database import database, connect_db, disconnect_db
from app.services.benchmark_service import get_benchmark_service

MODEL_NAME = "gemini-2.5-flash-lite"


# Common benchmark patterns to search for
BENCHMARK_PATTERNS = {
    "imagenet": r"ImageNet[- ]?(1K|1000)?(?:\s+(?:top[- ]?[15]|accuracy|validation))?\s*[:\-=]?\s*(\d+\.?\d*)\s*%?",
    "mmlu": r"MMLU[:\-=]?\s*(\d+\.?\d*)\s*%?",
    "humaneval": r"HumanEval[:\-=]?\s*(\d+\.?\d*)\s*%?",
    "gsm8k": r"GSM8K[:\-=]?\s*(\d+\.?\d*)\s*%?",
    "mt-bench": r"MT[- ]?Bench[:\-=]?\s*(\d+\.?\d*)",
    "glue": r"(?:Super)?GLUE[:\-=]?\s*(\d+\.?\d*)",
    "squad": r"SQuAD[- ]?(?:2\.0|v2)?[:\-=]?\s*(\d+\.?\d*)",
    "coco": r"COCO[:\-=]?\s*(?:mAP)?\s*(\d+\.?\d*)",
    "cityscapes": r"Cityscapes[:\-=]?\s*(?:mIoU)?\s*(\d+\.?\d*)",
    "wmt": r"WMT\d{2,4}[:\-=]?\s*(?:BLEU)?\s*(\d+\.?\d*)",
}

BENCHMARK_SLUG_MAP = {
    "imagenet": "imagenet-top1",
    "mmlu": "mmlu",
    "humaneval": "humaneval",
    "gsm8k": "gsm8k",
    "mt-bench": "mt-bench",
    "glue": "superglue",
    "squad": "squad-v2",
    "coco": "coco-detection",
    "cityscapes": "cityscapes-seg",
    "wmt": "wmt-translation",
}


EXTRACTION_PROMPT = """Extract benchmark results from this paper's abstract and analysis.

**Paper Title:** {title}

**Abstract:** {abstract}

**Analysis (if available):** {analysis}

**Task:**
Find any benchmark results mentioned in the paper. For each benchmark found, extract:
1. Benchmark name (e.g., ImageNet, MMLU, HumanEval)
2. Metric value (the numerical score)
3. Model name (if mentioned)
4. Whether this is claimed as a new SOTA

**Output Format (JSON):**
```json
[
  {{
    "benchmark": "ImageNet",
    "metric_name": "top-1 accuracy",
    "value": 88.5,
    "model_name": "ViT-L/16",
    "is_sota_claim": true
  }}
]
```

**Rules:**
1. Only include results that are clearly stated in the text
2. Don't infer or calculate results
3. If multiple results for same benchmark, include the best one
4. Convert percentages to decimal if needed (88.5% -> 88.5)
5. Maximum 5 benchmark results per paper

**Output only valid JSON array:**
"""


async def get_papers_with_benchmark_mentions(db, limit: int = 100):
    """
    Get papers that mention common benchmarks.
    """
    # Build search pattern
    benchmark_names = "|".join([
        "ImageNet", "MMLU", "HumanEval", "GSM8K", "MT-Bench",
        "GLUE", "SuperGLUE", "SQuAD", "COCO", "Cityscapes", "WMT"
    ])

    query = f"""
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.deep_analysis,
            p.published_date,
            p.citation_count
        FROM papers p
        LEFT JOIN sota_history sh ON p.id = sh.paper_id
        WHERE (
            p.abstract ~* :pattern
            OR p.title ~* :pattern
            OR p.deep_analysis::text ~* :pattern
        )
        AND sh.paper_id IS NULL
        ORDER BY p.citation_count DESC NULLS LAST
        LIMIT :limit
    """

    results = await db.fetch_all(query, {
        "pattern": benchmark_names,
        "limit": limit
    })

    return [
        {
            "id": r["id"],
            "title": r["title"],
            "abstract": r["abstract"],
            "deep_analysis": r["deep_analysis"],
            "published_date": r["published_date"],
            "citation_count": r["citation_count"]
        }
        for r in results
    ]


def quick_extract_results(paper: dict) -> list:
    """
    Quick regex-based extraction of benchmark results.
    Faster than LLM but less accurate.
    """
    results = []
    text_to_search = f"{paper.get('title', '')} {paper.get('abstract', '')}"

    deep = paper.get("deep_analysis") or {}
    if deep:
        text_to_search += " " + json.dumps(deep)

    for benchmark_key, pattern in BENCHMARK_PATTERNS.items():
        matches = re.finditer(pattern, text_to_search, re.IGNORECASE)
        for match in matches:
            try:
                # Get the numerical value
                groups = match.groups()
                value_str = groups[-1]  # Last group is usually the number
                value = float(value_str)

                results.append({
                    "benchmark_slug": BENCHMARK_SLUG_MAP.get(benchmark_key, benchmark_key),
                    "value": value,
                    "model_name": None  # Regex can't easily get this
                })
            except (ValueError, IndexError):
                continue

    return results


async def llm_extract_results(paper: dict, model) -> list:
    """
    Use LLM to extract benchmark results.
    More accurate but slower and costs tokens.
    """
    deep = paper.get("deep_analysis") or {}
    analysis_text = ""

    # Ensure deep is a dict
    if isinstance(deep, str):
        try:
            deep = json.loads(deep)
        except json.JSONDecodeError:
            deep = {}

    if deep and isinstance(deep, dict):
        # Extract key sections
        for key in ["key_contributions", "methodology", "results"]:
            if key in deep:
                analysis_text += f"\n{key}: {deep[key]}"

    prompt = EXTRACTION_PROMPT.format(
        title=paper.get("title", ""),
        abstract=paper.get("abstract", ""),
        analysis=analysis_text[:2000] if analysis_text else "Not available"
    )

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(prompt)
        )
        response_text = response.text

        # Parse JSON from response
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if not json_match:
            return []

        data = json.loads(json_match.group())
        results = []

        for item in data:
            benchmark = item.get("benchmark", "").lower()
            # Map to our slugs
            slug = None
            for key, pattern_slug in BENCHMARK_SLUG_MAP.items():
                if key in benchmark:
                    slug = pattern_slug
                    break

            if slug and item.get("value"):
                results.append({
                    "benchmark_slug": slug,
                    "value": float(item["value"]),
                    "model_name": item.get("model_name")
                })

        return results

    except Exception as e:
        print(f"  LLM extraction error: {e}")
        return []


async def save_benchmark_results(
    paper: dict,
    results: list,
    benchmark_service,
    db
) -> int:
    """Save extracted benchmark results to database."""
    saved = 0

    for result in results:
        try:
            success = await benchmark_service.add_sota_entry(
                benchmark_slug=result["benchmark_slug"],
                paper_id=paper["id"],
                value=result["value"],
                db=db,
                achieved_date=paper.get("published_date"),
                model_name=result.get("model_name"),
                is_verified=False  # Auto-extracted, needs verification
            )
            if success:
                saved += 1
        except Exception as e:
            print(f"  Error saving {result['benchmark_slug']}: {e}")

    return saved


async def main():
    parser = argparse.ArgumentParser(description="Extract benchmark results from papers")
    parser.add_argument("--limit", type=int, default=100, help="Max papers to process")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM for extraction (more accurate, slower)")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between papers (for LLM rate limiting)")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Benchmark Result Extraction")
    print(f"Mode: {'LLM-based' if args.use_llm else 'Regex-based (fast)'}")
    print("=" * 60)

    # Connect to database using async databases library
    await connect_db()
    db = database
    benchmark_service = get_benchmark_service()

    try:
        model = None
        if args.use_llm:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("ERROR: No Gemini API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY")
                return
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(MODEL_NAME)
            print(f"Initialized Gemini model: {MODEL_NAME}")

        print(f"\nFetching papers mentioning benchmarks (limit={args.limit})...")
        papers = await get_papers_with_benchmark_mentions(db, args.limit)
        print(f"Found {len(papers)} papers to process")

        if not papers:
            print("No papers to process!")
            return

        # Process papers
        total_results = 0
        total_saved = 0
        papers_with_results = 0

        for i, paper in enumerate(papers):
            print(f"\n[{i+1}/{len(papers)}] {paper['title'][:60]}...")

            # Extract results
            if args.use_llm and model:
                results = await llm_extract_results(paper, model)
                await asyncio.sleep(args.delay)
            else:
                results = quick_extract_results(paper)

            if results:
                papers_with_results += 1
                total_results += len(results)
                print(f"  Found {len(results)} benchmark results")

                # Save results
                saved = await save_benchmark_results(paper, results, benchmark_service, db)
                total_saved += saved
                print(f"  Saved {saved} results")
            else:
                print(f"  No benchmark results found")

        elapsed = time.time() - start
        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Papers processed: {len(papers)}")
        print(f"Papers with results: {papers_with_results}")
        print(f"Results found: {total_results}")
        print(f"Results saved: {total_saved}")
        print(f"Time: {elapsed:.1f}s")
        print("=" * 60)
    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
