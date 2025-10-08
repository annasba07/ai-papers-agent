"""
Test Script for Multi-Agent Code Generation System

This script tests the multi-agent system locally without requiring the API server.

Usage:
    python test_agent_system.py --paper-id 2010.11929
    python test_agent_system.py --paper-id 2303.08774 --verbose
"""
import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents import get_orchestrator
from app.services.arxiv_service import arxiv_service
from app.services.ai_analysis_service import ai_analysis_service


async def test_code_generation(paper_id: str, verbose: bool = False):
    """
    Test the multi-agent code generation system with a real paper

    Args:
        paper_id: arXiv paper ID (e.g., "2010.11929")
        verbose: Print detailed logs
    """
    print(f"\n{'='*80}")
    print(f"🧪 Testing Multi-Agent Code Generation System")
    print(f"{'='*80}\n")

    start_time = datetime.now()

    try:
        # STEP 1: Fetch paper from arXiv
        print(f"📄 Step 1: Fetching paper {paper_id} from arXiv...")
        paper = await arxiv_service.get_paper_by_id(paper_id)

        if not paper:
            print(f"❌ Error: Could not find paper {paper_id}")
            return

        print(f"✅ Found: {paper['title'][:80]}...")
        print(f"   Authors: {', '.join(paper.get('authors', [])[:3])}...")
        print(f"   Category: {paper.get('category', 'N/A')}")

        # STEP 2: Generate AI summary
        print(f"\n🤖 Step 2: Generating AI analysis...")
        ai_summary = await ai_analysis_service.generate_comprehensive_analysis(
            paper.get('summary', ''),
            paper.get('title', ''),
            paper.get('authors', []),
            paper_id
        )
        print(f"✅ AI analysis complete")

        if verbose:
            print(f"\nKey Concepts: {ai_summary.get('keyConcepts', [])[:3]}")
            print(f"Novelty: {ai_summary.get('novelty', '')[:100]}...")

        # STEP 3: Initialize orchestrator
        print(f"\n🎭 Step 3: Initializing multi-agent orchestrator...")
        orchestrator = get_orchestrator()
        print(f"✅ Orchestrator ready with 5 agents")

        # STEP 4: Generate code
        print(f"\n💻 Step 4: Generating code (this may take 60-120 seconds)...")
        print(f"   Pipeline: Analyze → Design Tests → Generate Code → Execute → Debug")

        result = await orchestrator.generate_quick_start(
            paper_title=paper['title'],
            paper_abstract=paper['summary'],
            paper_summary=ai_summary,
            paper_id=paper_id,
            paper_category=paper.get('category', 'cs.AI')
        )

        # STEP 5: Display results
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"\n{'='*80}")
        print(f"📊 RESULTS")
        print(f"{'='*80}\n")

        if result.success:
            print(f"✅ SUCCESS - All tests passing!")
        else:
            print(f"⚠️  PARTIAL SUCCESS - Some tests failed")

        print(f"\n⏱️  Total Time: {elapsed:.1f}s")
        print(f"🔄 Debug Iterations: {result.debug_iterations}")

        if result.tests:
            print(f"\n🧪 Tests:")
            print(f"   Total: {result.tests.total_tests}")
            if result.test_results:
                print(f"   Passed: {result.test_results.tests_passed}")
                print(f"   Failed: {result.test_results.tests_failed}")

        if result.code:
            print(f"\n💾 Generated Code:")
            print(f"   Main code: {len(result.code.main_code)} chars")
            print(f"   Config: {len(result.code.config_code)} chars")
            print(f"   Framework: {result.code.framework}")
            print(f"   Dependencies: {', '.join(result.code.dependencies[:5])}")

        if verbose and result.system_reflection:
            print(f"\n🤔 System Reflection:")
            print(f"   {result.system_reflection}")

        # Save results to file
        output_dir = Path("test_outputs")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"{paper_id.replace('.', '_')}_result.json"

        with open(output_file, "w") as f:
            json.dump({
                "paper_id": paper_id,
                "paper_title": result.paper_title,
                "success": result.success,
                "generation_time_seconds": result.generation_time_seconds,
                "debug_iterations": result.debug_iterations,
                "tests_total": result.tests.total_tests if result.tests else 0,
                "tests_passed": result.test_results.tests_passed if result.test_results else 0,
                "tests_failed": result.test_results.tests_failed if result.test_results else 0,
                "code_length": len(result.code.main_code) if result.code else 0,
                "dependencies": result.code.dependencies if result.code else [],
                "framework": result.code.framework if result.code else None,
            }, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        # Save code files
        if result.code:
            code_dir = output_dir / f"{paper_id.replace('.', '_')}_code"
            code_dir.mkdir(exist_ok=True)

            (code_dir / "model.py").write_text(result.code.main_code)
            (code_dir / "config.py").write_text(result.code.config_code)
            (code_dir / "utils.py").write_text(result.code.utils_code)
            (code_dir / "example.py").write_text(result.code.example_code)
            (code_dir / "README.md").write_text(result.readme or "")

            print(f"💾 Code saved to: {code_dir}/")

        print(f"\n{'='*80}")

        return result

    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        if verbose:
            traceback.print_exc()
        return None


async def run_benchmark(paper_ids: list[str]):
    """
    Run benchmark on multiple papers

    Args:
        paper_ids: List of arXiv paper IDs to test
    """
    print(f"\n{'='*80}")
    print(f"📊 Running Benchmark on {len(paper_ids)} papers")
    print(f"{'='*80}\n")

    results = []

    for i, paper_id in enumerate(paper_ids, 1):
        print(f"\n[{i}/{len(paper_ids)}] Testing paper: {paper_id}")
        result = await test_code_generation(paper_id, verbose=False)

        if result:
            results.append({
                "paper_id": paper_id,
                "success": result.success,
                "time": result.generation_time_seconds,
                "debug_iterations": result.debug_iterations,
                "tests_passed": result.test_results.tests_passed if result.test_results else 0,
                "tests_total": result.tests.total_tests if result.tests else 0,
            })

        # Small delay between papers
        await asyncio.sleep(2)

    # Print summary
    print(f"\n{'='*80}")
    print(f"📊 BENCHMARK SUMMARY")
    print(f"{'='*80}\n")

    if results:
        success_count = sum(1 for r in results if r["success"])
        avg_time = sum(r["time"] for r in results) / len(results)
        avg_debug = sum(r["debug_iterations"] for r in results) / len(results)

        print(f"Papers tested: {len(results)}")
        print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        print(f"Average time: {avg_time:.1f}s")
        print(f"Average debug iterations: {avg_debug:.1f}")

        print(f"\nIndividual Results:")
        for r in results:
            status = "✅" if r["success"] else "⚠️"
            print(f"  {status} {r['paper_id']}: {r['time']:.1f}s, "
                  f"{r['tests_passed']}/{r['tests_total']} tests, "
                  f"{r['debug_iterations']} debug iters")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test the multi-agent code generation system"
    )
    parser.add_argument(
        "--paper-id",
        type=str,
        help="arXiv paper ID to test (e.g., 2010.11929)"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run benchmark on multiple papers"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed logs"
    )

    args = parser.parse_args()

    if args.benchmark:
        # Benchmark papers of varying complexity
        benchmark_papers = [
            "2010.11929",  # CLIP (moderate complexity)
            "2303.08774",  # GPT-4 Technical Report (high complexity)
            "2106.09685",  # LoRA (low-moderate complexity)
            "2307.09288",  # Llama 2 (high complexity)
            "2001.08361",  # DALL-E (moderate complexity)
        ]
        asyncio.run(run_benchmark(benchmark_papers))

    elif args.paper_id:
        asyncio.run(test_code_generation(args.paper_id, args.verbose))

    else:
        print("Error: Please provide --paper-id or --benchmark")
        print("\nExamples:")
        print("  python test_agent_system.py --paper-id 2010.11929")
        print("  python test_agent_system.py --paper-id 2303.08774 --verbose")
        print("  python test_agent_system.py --benchmark")
        sys.exit(1)
