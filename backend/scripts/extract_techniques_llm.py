#!/usr/bin/env python3
"""
Extract method/technique names from papers using Gemini Flash 2.5.
Run from backend directory: python scripts/extract_techniques_llm.py

This script uses LLM to identify specific methods, algorithms, and techniques
mentioned in papers and links them to the techniques table.
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

sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai

from app.db.database import database, connect_db, disconnect_db
from app.core.config import settings

# Use the faster lite model for extraction
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
  {{
    "name": "LoRA",
    "method_type": "technique",
    "role": "uses",
    "confidence": 0.95
  }},
  {{
    "name": "LLaMA",
    "method_type": "architecture",
    "role": "uses",
    "confidence": 0.9
  }},
  {{
    "name": "QLoRA",
    "method_type": "technique",
    "role": "proposes",
    "confidence": 1.0
  }}
]
```

**Fields:**
- name: The technique/method name (use canonical name, e.g., "BERT" not "bert-base")
- method_type: One of: architecture, technique, algorithm, optimization, training_method, attention_mechanism
- role: "uses" (paper uses this technique) or "proposes" (paper introduces this as new)
- confidence: How confident you are (0.5-1.0)

**Rules:**
1. Only include specific, named techniques that appear in the paper
2. For each technique, determine if the paper uses it or proposes it
3. Use canonical names (e.g., "Transformer" not "transformer architecture")
4. Don't include datasets or evaluation metrics
5. Maximum 8 techniques per paper

**Output only valid JSON array:**
"""


async def get_papers_for_technique_extraction(db, limit: int = 100) -> list:
    """Get papers that need technique extraction."""
    query = """
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.published_date
        FROM papers p
        LEFT JOIN paper_techniques pt ON p.id = pt.paper_id
        WHERE pt.paper_id IS NULL
        AND p.abstract IS NOT NULL
        AND LENGTH(p.abstract) > 100
        ORDER BY p.published_date DESC
        LIMIT :limit
    """
    results = await db.fetch_all(query, {"limit": limit})
    return [dict(r) for r in results]


async def extract_techniques_llm(paper: dict, model) -> list:
    """Use LLM to extract techniques from paper."""
    prompt = TECHNIQUE_EXTRACTION_PROMPT.format(
        title=paper.get("title", ""),
        abstract=paper.get("abstract", "")[:2000]
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
            if item.get("name"):
                results.append({
                    "name": item["name"].strip(),
                    "method_type": item.get("method_type", "technique"),
                    "role": item.get("role", "uses"),
                    "confidence": min(1.0, max(0.5, float(item.get("confidence", 0.8))))
                })

        return results

    except Exception as e:
        print(f"  LLM extraction error: {e}")
        return []


async def ensure_technique_exists(db, name: str, method_type: str) -> int:
    """Ensure technique exists in database, create if not. Returns technique_id."""
    normalized = name.lower().strip()

    # Check if exists
    existing = await db.fetch_one(
        "SELECT id FROM techniques WHERE normalized_name = :name",
        {"name": normalized}
    )

    if existing:
        return existing["id"]

    # Create new technique
    result = await db.fetch_one(
        """
        INSERT INTO techniques (name, normalized_name, method_type, created_at)
        VALUES (:name, :normalized, :method_type, :now)
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


async def save_paper_techniques(db, paper_id: str, techniques: list) -> int:
    """Save extracted techniques to database."""
    saved = 0

    for tech in techniques:
        try:
            # Ensure technique exists
            technique_id = await ensure_technique_exists(
                db,
                tech["name"],
                tech["method_type"]
            )

            # Create paper-technique link
            await db.execute(
                """
                INSERT INTO paper_techniques (paper_id, technique_id, role, confidence, evidence_source)
                VALUES (:paper_id, :technique_id, :role, :confidence, 'llm_extraction')
                ON CONFLICT (paper_id, technique_id) DO UPDATE
                SET confidence = GREATEST(paper_techniques.confidence, EXCLUDED.confidence),
                    role = EXCLUDED.role
                """,
                {
                    "paper_id": paper_id,
                    "technique_id": technique_id,
                    "role": tech["role"],
                    "confidence": tech["confidence"]
                }
            )
            saved += 1

        except Exception as e:
            print(f"  Error saving technique {tech['name']}: {e}")

    return saved


async def get_technique_stats(db) -> dict:
    """Get current technique stats."""
    total_techniques = await db.fetch_one("SELECT COUNT(*) as cnt FROM techniques")
    total_links = await db.fetch_one("SELECT COUNT(*) as cnt FROM paper_techniques")
    papers_with_techniques = await db.fetch_one(
        "SELECT COUNT(DISTINCT paper_id) as cnt FROM paper_techniques"
    )
    total_papers = await db.fetch_one("SELECT COUNT(*) as cnt FROM papers")

    return {
        "total_techniques": total_techniques["cnt"],
        "total_links": total_links["cnt"],
        "papers_with_techniques": papers_with_techniques["cnt"],
        "total_papers": total_papers["cnt"],
    }


async def main():
    parser = argparse.ArgumentParser(description="Extract techniques using LLM")
    parser.add_argument("--limit", type=int, default=500, help="Max papers to process")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between papers (seconds)")
    parser.add_argument("--dry-run", action="store_true", help="Just count, don't process")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("Technique Extraction (LLM-based)")
    print(f"Model: {MODEL_NAME}")
    print(f"Limit: {args.limit}, Delay: {args.delay}s")
    print("=" * 60)

    # Initialize Gemini
    api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    if not api_key:
        print("ERROR: No Gemini API key found!")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"Initialized model: {MODEL_NAME}")

    await connect_db()
    db = database

    try:
        # Get current stats
        stats = await get_technique_stats(db)
        print(f"\nCurrent Status:")
        print(f"  Total techniques: {stats['total_techniques']}")
        print(f"  Paper-technique links: {stats['total_links']}")
        print(f"  Papers with techniques: {stats['papers_with_techniques']} / {stats['total_papers']}")

        # Get papers needing extraction
        papers = await get_papers_for_technique_extraction(db, args.limit)
        print(f"\nFound {len(papers)} papers needing technique extraction")

        if args.dry_run:
            print("\n[DRY RUN] Would process papers but not extracting.")
            return

        if not papers:
            print("No papers to process!")
            return

        # Process papers
        total_processed = 0
        total_techniques = 0
        total_saved = 0
        papers_with_results = 0

        for i, paper in enumerate(papers):
            print(f"\n[{i+1}/{len(papers)}] {paper['title'][:60]}...")

            # Extract techniques
            techniques = await extract_techniques_llm(paper, model)

            if techniques:
                papers_with_results += 1
                total_techniques += len(techniques)
                print(f"  Found {len(techniques)} techniques: {[t['name'] for t in techniques]}")

                # Save to database
                saved = await save_paper_techniques(db, paper["id"], techniques)
                total_saved += saved
                print(f"  Saved {saved} technique links")
            else:
                print(f"  No techniques found")

            total_processed += 1

            # Rate limiting
            if i < len(papers) - 1:
                await asyncio.sleep(args.delay)

        # Final stats
        elapsed = time.time() - start
        final_stats = await get_technique_stats(db)

        print("\n" + "=" * 60)
        print("Complete!")
        print(f"Papers processed: {total_processed}")
        print(f"Papers with techniques: {papers_with_results}")
        print(f"Techniques found: {total_techniques}")
        print(f"Links saved: {total_saved}")
        print(f"\nFinal stats:")
        print(f"  Total techniques: {final_stats['total_techniques']}")
        print(f"  Paper-technique links: {final_stats['total_links']}")
        print(f"  Coverage: {final_stats['papers_with_techniques']} / {final_stats['total_papers']} "
              f"({final_stats['papers_with_techniques'] / final_stats['total_papers'] * 100:.1f}%)")
        print(f"\nTime: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print("=" * 60)

    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
