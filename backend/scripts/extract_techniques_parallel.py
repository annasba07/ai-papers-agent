#!/usr/bin/env python3
"""
PARALLEL technique extraction using Gemini Flash 2.5 Lite.
Uses asyncio.Semaphore for concurrent API calls.

Run: python scripts/extract_techniques_parallel.py --workers 15
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
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai

from app.db.database import database, connect_db, disconnect_db
from app.core.config import settings

MODEL_NAME = "gemini-2.5-flash-lite"

TECHNIQUE_EXTRACTION_PROMPT = """Analyze this AI/ML research paper and extract the specific techniques, methods, and models mentioned.

**Paper Title:** {title}

**Abstract:** {abstract}

**Task:**
Extract up to 8 specific techniques, methods, architectures, or models that are:
1. **Used** by this paper (existing techniques they build upon)
2. **Proposed** by this paper (new contributions)

Focus on NAMED techniques like: Transformer, GPT, BERT, LoRA, RLHF, Chain-of-Thought, Diffusion Models, RAG, etc.
DO NOT include generic terms like "deep learning" or "neural network" - only specific named methods.

**Output Format (JSON):**
```json
[
  {{"name": "LoRA", "method_type": "technique", "role": "uses", "confidence": 0.95}},
  {{"name": "LLaMA", "method_type": "architecture", "role": "uses", "confidence": 0.9}}
]
```

**Fields:**
- name: The technique/method name (use canonical name)
- method_type: One of: architecture, technique, algorithm, optimization, training_method, attention_mechanism
- role: "uses" or "proposes"
- confidence: 0.5-1.0

**Rules:**
1. Only include specific, named techniques
2. Use canonical names (e.g., "Transformer" not "transformer architecture")
3. Don't include datasets or evaluation metrics
4. Maximum 8 techniques per paper

**Output only valid JSON array:**
"""


class ParallelTechniqueExtractor:
    def __init__(self, workers: int = 10):
        self.workers = workers
        self.semaphore = asyncio.Semaphore(workers)
        self.model = None
        self.stats = {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "techniques_found": 0,
            "links_created": 0
        }
        self.lock = asyncio.Lock()

    async def init_model(self):
        api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("No Gemini API key found!")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(MODEL_NAME)

    async def extract_techniques_llm(self, paper: dict) -> list:
        """Use LLM to extract techniques with semaphore for rate limiting."""
        async with self.semaphore:
            prompt = TECHNIQUE_EXTRACTION_PROMPT.format(
                title=paper.get("title", ""),
                abstract=paper.get("abstract", "")[:2000]
            )

            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(prompt)
                )
                response_text = response.text

                # Parse JSON
                json_match = re.search(r'\[[\s\S]*\]', response_text)
                if not json_match:
                    return []

                data = json.loads(json_match.group())
                results = []

                for item in data:
                    if item.get("name"):
                        results.append({
                            "name": item["name"].strip(),
                            "method_type": item.get("method_type", "technique"),
                            "role": item.get("role", "uses"),
                            "confidence": min(1.0, max(0.5, float(item.get("confidence", 0.8))))
                        })

                return results

            except Exception as e:
                return []

    async def ensure_technique_exists(self, name: str, method_type: str) -> int:
        """Ensure technique exists, return ID."""
        normalized = name.lower().strip()

        existing = await database.fetch_one(
            "SELECT id FROM techniques WHERE normalized_name = :name",
            {"name": normalized}
        )

        if existing:
            return existing["id"]

        try:
            result = await database.fetch_one(
                """
                INSERT INTO techniques (name, normalized_name, method_type, created_at)
                VALUES (:name, :normalized, :method_type, :now)
                ON CONFLICT (normalized_name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
                """,
                {
                    "name": name,
                    "normalized": normalized,
                    "method_type": method_type,
                    "now": datetime.utcnow()
                }
            )
            return result["id"]
        except Exception:
            # Race condition - fetch again
            existing = await database.fetch_one(
                "SELECT id FROM techniques WHERE normalized_name = :name",
                {"name": normalized}
            )
            return existing["id"] if existing else None

    async def save_paper_techniques(self, paper_id: str, techniques: list) -> int:
        """Save techniques to DB."""
        saved = 0

        for tech in techniques:
            try:
                technique_id = await self.ensure_technique_exists(
                    tech["name"],
                    tech["method_type"]
                )

                if technique_id:
                    await database.execute(
                        """
                        INSERT INTO paper_techniques (paper_id, technique_id, role, confidence, evidence_source)
                        VALUES (:paper_id, :technique_id, :role, :confidence, 'llm_extraction')
                        ON CONFLICT (paper_id, technique_id) DO UPDATE
                        SET confidence = GREATEST(paper_techniques.confidence, EXCLUDED.confidence)
                        """,
                        {
                            "paper_id": paper_id,
                            "technique_id": technique_id,
                            "role": tech["role"],
                            "confidence": tech["confidence"]
                        }
                    )
                    saved += 1
            except Exception:
                pass

        return saved

    async def process_paper(self, paper: dict, idx: int, total: int) -> bool:
        """Process a single paper."""
        try:
            techniques = await self.extract_techniques_llm(paper)

            async with self.lock:
                self.stats["processed"] += 1

                if techniques:
                    saved = await self.save_paper_techniques(paper["id"], techniques)
                    self.stats["success"] += 1
                    self.stats["techniques_found"] += len(techniques)
                    self.stats["links_created"] += saved

                    if self.stats["processed"] % 50 == 0:
                        print(f"[{self.stats['processed']}/{total}] "
                              f"Rate: {self.stats['processed'] / ((time.time() - self.start_time) / 60):.1f}/min | "
                              f"Techniques: {self.stats['techniques_found']} | "
                              f"Links: {self.stats['links_created']}")
                else:
                    self.stats["failed"] += 1

            return True

        except Exception as e:
            async with self.lock:
                self.stats["processed"] += 1
                self.stats["failed"] += 1
            return False

    async def run(self, limit: int = 10000):
        """Run parallel extraction."""
        await connect_db()
        await self.init_model()

        # Get papers needing extraction
        query = """
            SELECT p.id, p.title, p.abstract
            FROM papers p
            LEFT JOIN paper_techniques pt ON p.id = pt.paper_id
            WHERE pt.paper_id IS NULL
            AND p.abstract IS NOT NULL
            AND LENGTH(p.abstract) > 100
            ORDER BY p.published_date DESC
            LIMIT :limit
        """

        papers = await database.fetch_all(query, {"limit": limit})
        papers = [dict(p) for p in papers]

        if not papers:
            print("No papers to process!")
            return

        print(f"Processing {len(papers)} papers with {self.workers} parallel workers...")
        print("=" * 60)

        self.start_time = time.time()

        # Process all papers concurrently with semaphore limiting
        tasks = [
            self.process_paper(paper, i, len(papers))
            for i, paper in enumerate(papers)
        ]

        await asyncio.gather(*tasks)

        elapsed = time.time() - self.start_time

        print("\n" + "=" * 60)
        print("COMPLETE!")
        print(f"Processed: {self.stats['processed']}")
        print(f"Success: {self.stats['success']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Techniques found: {self.stats['techniques_found']}")
        print(f"Links created: {self.stats['links_created']}")
        print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"Rate: {self.stats['processed'] / (elapsed / 60):.1f} papers/min")
        print("=" * 60)

        await disconnect_db()


async def main():
    parser = argparse.ArgumentParser(description="Parallel technique extraction")
    parser.add_argument("--workers", type=int, default=15, help="Concurrent workers (default: 15)")
    parser.add_argument("--limit", type=int, default=10000, help="Max papers to process")
    args = parser.parse_args()

    print(f"Starting parallel extraction with {args.workers} workers...")

    extractor = ParallelTechniqueExtractor(workers=args.workers)
    await extractor.run(limit=args.limit)


if __name__ == "__main__":
    asyncio.run(main())
