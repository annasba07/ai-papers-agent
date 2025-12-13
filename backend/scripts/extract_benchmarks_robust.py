#!/usr/bin/env python3
"""
Robust benchmark extraction using Gemini 2.5 Flash Lite.
Extracts benchmark results from papers and populates the benchmarks table.

Features:
- Comprehensive LLM prompt covering diverse benchmark types
- Auto-creates tasks and datasets as needed
- Validation and sanity checks on extracted values
- Parallel processing with semaphore rate limiting
- Deduplication and normalization

Run: python scripts/extract_benchmarks_robust.py --workers 15 --limit 5000
"""
import asyncio
import os
import sys
import time
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai

from app.db.database import database, connect_db, disconnect_db
from app.core.config import settings

MODEL_NAME = "gemini-2.5-flash-lite"

# Comprehensive benchmark extraction prompt
BENCHMARK_EXTRACTION_PROMPT = """You are a benchmark result extraction expert. Extract ALL quantitative benchmark results from this AI/ML research paper.

**Paper Title:** {title}

**Abstract:** {abstract}

**Deep Analysis (if available):** {deep_analysis}

**Your Task:**
Extract every benchmark result mentioned where the paper reports a numerical performance score. Look for:

1. **Vision benchmarks**: ImageNet (top-1/top-5), COCO (mAP, AP50), ADE20K (mIoU), Cityscapes, PASCAL VOC, etc.
2. **Language benchmarks**: MMLU, HellaSwag, WinoGrande, ARC, TruthfulQA, PIQA, BoolQ, etc.
3. **Code benchmarks**: HumanEval, MBPP, SWE-bench, CodeContests, APPS, etc.
4. **Math benchmarks**: GSM8K, MATH, MathQA, etc.
5. **QA benchmarks**: SQuAD, TriviaQA, NaturalQuestions, etc.
6. **Translation/NLP**: WMT, BLEU scores, GLUE, SuperGLUE, etc.
7. **Multimodal**: VQAv2, GQA, TextVQA, OKVQA, etc.
8. **Generation/Perplexity**: WikiText, C4, PTB perplexity, etc.
9. **Efficiency metrics**: FLOPs, latency, throughput, parameters

**Output Format (JSON array):**
```json
[
  {{
    "task": "Image Classification",
    "dataset": "ImageNet-1K",
    "metric": "top-1 accuracy",
    "value": 88.5,
    "model_name": "ViT-L/16",
    "model_size": "307M parameters",
    "is_best_result": true
  }},
  {{
    "task": "Language Understanding",
    "dataset": "MMLU",
    "metric": "accuracy",
    "value": 86.4,
    "model_name": "Llama-3-70B",
    "model_size": "70B",
    "is_best_result": true
  }}
]
```

**Field Requirements:**
- **task**: General task category (e.g., "Image Classification", "Question Answering", "Code Generation")
- **dataset**: Specific benchmark/dataset name (use canonical names like "ImageNet-1K" not "imagenet")
- **metric**: Specific metric measured (e.g., "top-1 accuracy", "mAP", "pass@1", "BLEU", "perplexity")
- **value**: Numerical value (convert percentages: 88.5% -> 88.5, keep perplexity as-is)
- **model_name**: Model/method name if mentioned (null if not clear)
- **model_size**: Model size if mentioned (null if not stated)
- **is_best_result**: true if this is the paper's best/main result for this benchmark

**Validation Rules:**
1. Only extract results EXPLICITLY stated in the text (no inference)
2. Accuracy/F1/mAP values should be 0-100 or 0-1 (convert 0.885 -> 88.5)
3. Perplexity values are typically 1-100 for word-level, higher for character-level
4. BLEU scores are typically 0-100
5. Skip results marked as "previous work" or "baseline" - only extract this paper's results
6. Maximum 10 benchmark results per paper
7. Use canonical dataset names (ImageNet-1K not imagenet-1k)

**Output only the JSON array, no other text:**
"""

# Known benchmark normalizations
DATASET_NORMALIZATIONS = {
    "imagenet": "ImageNet-1K",
    "imagenet-1k": "ImageNet-1K",
    "imagenet1k": "ImageNet-1K",
    "ilsvrc": "ImageNet-1K",
    "ilsvrc-2012": "ImageNet-1K",
    "imagenet-21k": "ImageNet-21K",
    "coco": "COCO",
    "ms-coco": "COCO",
    "coco2017": "COCO",
    "ade20k": "ADE20K",
    "cityscapes": "Cityscapes",
    "mmlu": "MMLU",
    "hellaswag": "HellaSwag",
    "winogrande": "WinoGrande",
    "arc": "ARC-Challenge",
    "arc-c": "ARC-Challenge",
    "arc-challenge": "ARC-Challenge",
    "arc-easy": "ARC-Easy",
    "truthfulqa": "TruthfulQA",
    "gsm8k": "GSM8K",
    "gsm-8k": "GSM8K",
    "math": "MATH",
    "humaneval": "HumanEval",
    "human-eval": "HumanEval",
    "mbpp": "MBPP",
    "swe-bench": "SWE-bench",
    "squad": "SQuAD",
    "squad2.0": "SQuAD 2.0",
    "squad-v2": "SQuAD 2.0",
    "triviaqa": "TriviaQA",
    "vqav2": "VQAv2",
    "vqa-v2": "VQAv2",
    "gqa": "GQA",
    "textvqa": "TextVQA",
    "okvqa": "OK-VQA",
    "wikitext": "WikiText-103",
    "wikitext-103": "WikiText-103",
    "glue": "GLUE",
    "superglue": "SuperGLUE",
    "piqa": "PIQA",
    "boolq": "BoolQ",
    "lambada": "LAMBADA",
}

TASK_NORMALIZATIONS = {
    "image classification": "Image Classification",
    "object detection": "Object Detection",
    "semantic segmentation": "Semantic Segmentation",
    "instance segmentation": "Instance Segmentation",
    "question answering": "Question Answering",
    "reading comprehension": "Reading Comprehension",
    "language modeling": "Language Modeling",
    "text generation": "Text Generation",
    "code generation": "Code Generation",
    "machine translation": "Machine Translation",
    "visual question answering": "Visual Question Answering",
    "commonsense reasoning": "Commonsense Reasoning",
    "math reasoning": "Math Reasoning",
    "natural language inference": "Natural Language Inference",
}


def normalize_dataset(name: str) -> str:
    """Normalize dataset name to canonical form."""
    if not name:
        return "Unknown"
    key = name.lower().strip().replace(" ", "-").replace("_", "-")
    return DATASET_NORMALIZATIONS.get(key, name)


def normalize_task(name: str) -> str:
    """Normalize task name to canonical form."""
    if not name:
        return "General"
    key = name.lower().strip()
    return TASK_NORMALIZATIONS.get(key, name.title())


def validate_value(value: float, metric: str) -> Tuple[bool, float]:
    """
    Validate and potentially fix benchmark values.
    Returns (is_valid, corrected_value).
    """
    if value is None:
        return False, 0.0

    metric_lower = metric.lower() if metric else ""

    # Handle percentage metrics
    if any(m in metric_lower for m in ["accuracy", "precision", "recall", "f1", "map", "miou", "ap", "pass@"]):
        # Convert 0-1 scale to 0-100 scale
        if 0 <= value <= 1:
            value = value * 100
        # Valid range for percentage metrics
        if 0 <= value <= 100:
            return True, round(value, 2)
        return False, 0.0

    # Handle perplexity (typically 1-1000, lower is better)
    if "perplexity" in metric_lower or "ppl" in metric_lower:
        if 0 < value < 10000:
            return True, round(value, 2)
        return False, 0.0

    # Handle BLEU scores (0-100)
    if "bleu" in metric_lower:
        if 0 <= value <= 100:
            return True, round(value, 2)
        return False, 0.0

    # Handle FLOPs/throughput (any positive number)
    if any(m in metric_lower for m in ["flop", "throughput", "latency", "param"]):
        if value > 0:
            return True, value
        return False, 0.0

    # Default: accept positive values
    if value > 0:
        return True, round(value, 4)
    return False, 0.0


class RobustBenchmarkExtractor:
    def __init__(self, workers: int = 15):
        self.workers = workers
        self.semaphore = asyncio.Semaphore(workers)
        self.model = None
        self.stats = {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "benchmarks_found": 0,
            "benchmarks_saved": 0,
            "invalid_values": 0,
        }
        self.lock = asyncio.Lock()
        self.task_cache: Dict[str, int] = {}
        self.dataset_cache: Dict[str, int] = {}

    async def init_model(self):
        """Initialize Gemini model."""
        api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("No Gemini API key found!")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(MODEL_NAME)

    async def get_or_create_task(self, task_name: str) -> Optional[int]:
        """Get or create a task entry."""
        normalized = normalize_task(task_name)

        if normalized in self.task_cache:
            return self.task_cache[normalized]

        # Check if exists
        existing = await database.fetch_one(
            "SELECT id FROM tasks WHERE name = :name",
            {"name": normalized}
        )

        if existing:
            self.task_cache[normalized] = existing["id"]
            return existing["id"]

        # Create new
        try:
            result = await database.fetch_one(
                """
                INSERT INTO tasks (name, created_at)
                VALUES (:name, :now)
                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
                """,
                {"name": normalized, "now": datetime.utcnow()}
            )
            self.task_cache[normalized] = result["id"]
            return result["id"]
        except Exception:
            # Race condition - try to fetch again
            existing = await database.fetch_one(
                "SELECT id FROM tasks WHERE name = :name",
                {"name": normalized}
            )
            if existing:
                self.task_cache[normalized] = existing["id"]
                return existing["id"]
            return None

    async def get_or_create_dataset(self, dataset_name: str) -> Optional[int]:
        """Get or create a dataset entry."""
        normalized = normalize_dataset(dataset_name)
        normalized_key = normalized.lower().replace(" ", "-").replace("_", "-")

        if normalized_key in self.dataset_cache:
            return self.dataset_cache[normalized_key]

        # Check if exists
        existing = await database.fetch_one(
            "SELECT id FROM datasets WHERE normalized_name = :name",
            {"name": normalized_key}
        )

        if existing:
            self.dataset_cache[normalized_key] = existing["id"]
            return existing["id"]

        # Create new
        try:
            result = await database.fetch_one(
                """
                INSERT INTO datasets (name, normalized_name, created_at)
                VALUES (:name, :normalized, :now)
                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
                """,
                {"name": normalized, "normalized": normalized_key, "now": datetime.utcnow()}
            )
            self.dataset_cache[normalized_key] = result["id"]
            return result["id"]
        except Exception:
            # Race condition
            existing = await database.fetch_one(
                "SELECT id FROM datasets WHERE normalized_name = :name",
                {"name": normalized_key}
            )
            if existing:
                self.dataset_cache[normalized_key] = existing["id"]
                return existing["id"]
            return None

    async def extract_benchmarks_llm(self, paper: dict) -> List[Dict[str, Any]]:
        """Use LLM to extract benchmarks with rate limiting."""
        async with self.semaphore:
            # Prepare deep analysis text
            deep = paper.get("deep_analysis") or {}
            if isinstance(deep, str):
                try:
                    deep = json.loads(deep)
                except json.JSONDecodeError:
                    deep = {}

            deep_text = ""
            if deep and isinstance(deep, dict):
                for key in ["results", "key_contributions", "methodology", "performance"]:
                    if key in deep:
                        deep_text += f"\n{key}: {deep[key]}"

            prompt = BENCHMARK_EXTRACTION_PROMPT.format(
                title=paper.get("title", ""),
                abstract=paper.get("abstract", "")[:3000],
                deep_analysis=deep_text[:2000] if deep_text else "Not available"
            )

            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(prompt)
                )
                response_text = response.text

                # Parse JSON from response
                json_match = re.search(r'\[[\s\S]*\]', response_text)
                if not json_match:
                    return []

                data = json.loads(json_match.group())
                results = []

                for item in data:
                    if not item.get("dataset") or item.get("value") is None:
                        continue

                    # Validate value
                    is_valid, corrected_value = validate_value(
                        float(item["value"]),
                        item.get("metric", "")
                    )

                    if not is_valid:
                        async with self.lock:
                            self.stats["invalid_values"] += 1
                        continue

                    results.append({
                        "task": normalize_task(item.get("task", "General")),
                        "dataset": normalize_dataset(item["dataset"]),
                        "metric": item.get("metric", "accuracy"),
                        "value": corrected_value,
                        "model_name": item.get("model_name"),
                        "model_size": item.get("model_size"),
                        "is_best_result": item.get("is_best_result", False),
                    })

                return results[:10]  # Max 10 per paper

            except Exception as e:
                return []

    async def save_benchmark(self, paper_id: str, benchmark: Dict[str, Any], published_date) -> bool:
        """Save a single benchmark to the database."""
        try:
            task_id = await self.get_or_create_task(benchmark["task"])
            dataset_id = await self.get_or_create_dataset(benchmark["dataset"])

            await database.execute(
                """
                INSERT INTO benchmarks
                (paper_id, task_id, dataset_id, task, dataset, metric, value,
                 model_name, model_size, reported_date, evidence_source, created_at)
                VALUES
                (:paper_id, :task_id, :dataset_id, :task, :dataset, :metric, :value,
                 :model_name, :model_size, :reported_date, 'llm_extraction', :now)
                ON CONFLICT (paper_id, task, dataset, metric, model_name)
                DO UPDATE SET value = GREATEST(benchmarks.value, EXCLUDED.value)
                """,
                {
                    "paper_id": paper_id,
                    "task_id": task_id,
                    "dataset_id": dataset_id,
                    "task": benchmark["task"],
                    "dataset": benchmark["dataset"],
                    "metric": benchmark["metric"],
                    "value": benchmark["value"],
                    "model_name": benchmark.get("model_name"),
                    "model_size": benchmark.get("model_size"),
                    "reported_date": published_date,
                    "now": datetime.utcnow(),
                }
            )
            return True
        except Exception as e:
            return False

    async def process_paper(self, paper: dict, idx: int, total: int) -> bool:
        """Process a single paper for benchmark extraction."""
        try:
            benchmarks = await self.extract_benchmarks_llm(paper)

            async with self.lock:
                self.stats["processed"] += 1

                if benchmarks:
                    self.stats["success"] += 1
                    self.stats["benchmarks_found"] += len(benchmarks)

                    # Save each benchmark
                    for bm in benchmarks:
                        if await self.save_benchmark(
                            paper["id"], bm, paper.get("published_date")
                        ):
                            self.stats["benchmarks_saved"] += 1

                    # Progress logging every 50 papers
                    if self.stats["processed"] % 50 == 0:
                        elapsed = time.time() - self.start_time
                        rate = self.stats["processed"] / (elapsed / 60)
                        print(f"[{self.stats['processed']}/{total}] "
                              f"Rate: {rate:.1f}/min | "
                              f"Found: {self.stats['benchmarks_found']} | "
                              f"Saved: {self.stats['benchmarks_saved']} | "
                              f"Invalid: {self.stats['invalid_values']}")
                else:
                    self.stats["failed"] += 1

            return True

        except Exception as e:
            async with self.lock:
                self.stats["processed"] += 1
                self.stats["failed"] += 1
            return False

    async def run(self, limit: int = 5000, priority_filter: Optional[str] = None):
        """Run benchmark extraction."""
        await connect_db()
        await self.init_model()

        # Build query - find papers with deep_analysis that likely have benchmarks
        # Prioritize papers that mention benchmark-related terms
        query = """
            SELECT p.id, p.title, p.abstract, p.deep_analysis, p.published_date
            FROM papers p
            LEFT JOIN benchmarks b ON p.id = b.paper_id
            WHERE b.paper_id IS NULL
            AND p.deep_analysis IS NOT NULL
            AND (
                p.abstract ~* 'accuracy|benchmark|ImageNet|MMLU|GSM8K|HumanEval|COCO|BLEU|perplexity|F1|mAP|state-of-the-art|SOTA'
                OR p.title ~* 'accuracy|benchmark|evaluation|performance'
            )
            ORDER BY p.citation_count DESC NULLS LAST, p.published_date DESC
            LIMIT :limit
        """

        papers = await database.fetch_all(query, {"limit": limit})
        papers = [dict(p) for p in papers]

        if not papers:
            print("No papers to process!")
            return

        print(f"Processing {len(papers)} papers with {self.workers} parallel workers...")
        print("Looking for benchmark results in papers with deep analysis.")
        print("=" * 60)

        self.start_time = time.time()

        # Process all papers concurrently
        tasks = [
            self.process_paper(paper, i, len(papers))
            for i, paper in enumerate(papers)
        ]

        await asyncio.gather(*tasks)

        elapsed = time.time() - self.start_time

        print("\n" + "=" * 60)
        print("BENCHMARK EXTRACTION COMPLETE!")
        print(f"Papers processed: {self.stats['processed']}")
        print(f"Papers with benchmarks: {self.stats['success']}")
        print(f"Papers without benchmarks: {self.stats['failed']}")
        print(f"Benchmark results found: {self.stats['benchmarks_found']}")
        print(f"Benchmark results saved: {self.stats['benchmarks_saved']}")
        print(f"Invalid values skipped: {self.stats['invalid_values']}")
        print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        if self.stats["processed"] > 0:
            print(f"Rate: {self.stats['processed'] / (elapsed / 60):.1f} papers/min")
        print("=" * 60)

        await disconnect_db()


async def main():
    parser = argparse.ArgumentParser(description="Robust benchmark extraction")
    parser.add_argument("--workers", type=int, default=15, help="Concurrent workers (default: 15)")
    parser.add_argument("--limit", type=int, default=5000, help="Max papers to process")
    args = parser.parse_args()

    print(f"Starting robust benchmark extraction with {args.workers} workers...")
    print(f"Model: {MODEL_NAME}")

    extractor = RobustBenchmarkExtractor(workers=args.workers)
    await extractor.run(limit=args.limit)


if __name__ == "__main__":
    asyncio.run(main())
