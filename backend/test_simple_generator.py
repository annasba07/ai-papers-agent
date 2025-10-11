"""
Test Script for Simple Code Generator

Tests the elegant single-conversation approach and compares with complex approach.

Usage:
    python test_simple_generator.py --paper-id 2010.11929
    python test_simple_generator.py --paper-id 2010.11929 --compare
"""
import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.simple_generator import get_simple_generator
from app.services.arxiv_service import arxiv_service
from app.services.ai_analysis_service import ai_analysis_service


async def test_simple_generation(paper_id: str, verbose: bool = False):
    """
    Test the simple code generator with a real paper

    Args:
        paper_id: arXiv paper ID (e.g., "2010.11929")
        verbose: Print detailed logs
    """
    print(f"\n{'='*80}")
    print(f"🧪 Testing Simple Code Generator")
    print(f"{'='*80}\n")

    start_time = datetime.now()

    try:
        # STEP 1: Fetch paper from arXiv
        print(f"📄 Step 1: Fetching paper {paper_id} from arXiv...")
        paper = await arxiv_service.get_paper_by_id(paper_id)

        if not paper:
            print(f"❌ Error: Could not find paper {paper_id}")
            return None

        print(f"✅ Found: {paper['title'][:80]}...")
        print(f"   Authors: {', '.join(paper.get('authors', [])[:3])}...")
        print(f"   Category: {paper.get('category', 'N/A')}")

        # STEP 2: Get simple generator
        print(f"\n🤖 Step 2: Initializing simple generator...")
        generator = get_simple_generator()
        print(f"✅ Generator ready (single-conversation approach)")

        # STEP 3: Generate code
        print(f"\n💻 Step 3: Generating code (Claude self-orchestrates)...")
        print(f"   Approach: Extended context + tool use")

        result = await generator.generate(
            paper_title=paper['title'],
            paper_abstract=paper['summary'],
            paper_id=paper_id,
            paper_category=paper.get('category', 'cs.AI')
        )

        # STEP 4: Display results
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

        if result.complexity:
            print(f"📈 Complexity: {result.complexity}/10")

        print(f"\n🧪 Tests:")
        print(f"   Total: {result.tests_total}")
        print(f"   Passed: {result.tests_passed}")
        print(f"   Failed: {result.tests_failed}")

        if result.code:
            print(f"\n💾 Generated Code:")
            print(f"   Model: {len(result.code)} chars")
            if result.config:
                print(f"   Config: {len(result.config)} chars")
            if result.example:
                print(f"   Example: {len(result.example)} chars")

        if verbose and result.reflection:
            print(f"\n🤔 Reflection:")
            print(f"   {result.reflection[:200]}...")

        # Save results to file
        output_dir = Path("test_outputs_simple")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"{paper_id.replace('.', '_')}_result.json"

        with open(output_file, "w") as f:
            json.dump({
                "approach": "simple",
                "paper_id": paper_id,
                "paper_title": result.paper_title,
                "success": result.success,
                "generation_time_seconds": result.generation_time_seconds,
                "complexity": result.complexity,
                "debug_iterations": result.debug_iterations,
                "tests_total": result.tests_total,
                "tests_passed": result.tests_passed,
                "tests_failed": result.tests_failed,
                "code_length": len(result.code) if result.code else 0,
                "reflection": result.reflection
            }, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        # Save code files
        if result.code:
            code_dir = output_dir / f"{paper_id.replace('.', '_')}_code"
            code_dir.mkdir(exist_ok=True)

            (code_dir / "model.py").write_text(result.code)
            if result.config:
                (code_dir / "config.py").write_text(result.config)
            if result.tests:
                (code_dir / "test_model.py").write_text(result.tests)
            if result.example:
                (code_dir / "example.py").write_text(result.example)
            if result.readme:
                (code_dir / "README.md").write_text(result.readme)

            print(f"💾 Code saved to: {code_dir}/")

        print(f"\n{'='*80}")

        return result

    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        if verbose:
            traceback.print_exc()
        return None


async def compare_approaches(paper_id: str):
    """
    Compare simple vs complex approaches

    Args:
        paper_id: arXiv paper ID to test both approaches on
    """
    print(f"\n{'='*80}")
    print(f"⚖️  Comparing Simple vs Complex Approaches")
    print(f"{'='*80}\n")

    results = {}

    # Test simple approach
    print("Testing SIMPLE approach...")
    simple_result = await test_simple_generation(paper_id)
    results['simple'] = simple_result

    # Test complex approach (if available)
    print("\n" + "="*80)
    print("Testing COMPLEX approach...")
    try:
        from app.agents import get_orchestrator

        paper = await arxiv_service.get_paper_by_id(paper_id)
        ai_summary = await ai_analysis_service.generate_comprehensive_analysis(
            paper.get('summary', ''),
            paper.get('title', '')
        )

        orchestrator = get_orchestrator()
        complex_result = await orchestrator.generate_quick_start(
            paper_title=paper['title'],
            paper_abstract=paper['summary'],
            paper_summary=ai_summary,
            paper_id=paper_id,
            paper_category=paper.get('category', 'cs.AI')
        )
        results['complex'] = complex_result
    except Exception as e:
        print(f"⚠️  Complex approach not available or failed: {e}")
        results['complex'] = None

    # Compare
    print(f"\n{'='*80}")
    print(f"📊 COMPARISON")
    print(f"{'='*80}\n")

    if results['simple'] and results['complex']:
        print(f"{'Metric':<30} {'Simple':<20} {'Complex':<20}")
        print(f"{'-'*70}")
        print(f"{'Success':<30} {str(results['simple'].success):<20} {str(results['complex'].success):<20}")
        print(f"{'Time (seconds)':<30} {results['simple'].generation_time_seconds:<20.1f} {results['complex'].generation_time_seconds:<20.1f}")
        print(f"{'Tests Passed':<30} {f\"{results['simple'].tests_passed}/{results['simple'].tests_total}\":<20} {f\"{results['complex'].test_results.tests_passed}/{results['complex'].test_results.tests_total}\":<20}")
        print(f"{'Debug Iterations':<30} {results['simple'].debug_iterations:<20} {results['complex'].debug_iterations:<20}")

        # Winner
        simple_time = results['simple'].generation_time_seconds
        complex_time = results['complex'].generation_time_seconds
        simple_pass_rate = results['simple'].tests_passed / max(results['simple'].tests_total, 1)
        complex_pass_rate = results['complex'].test_results.tests_passed / max(results['complex'].test_results.tests_total, 1)

        print(f"\n🏆 Winner:")
        if simple_pass_rate > complex_pass_rate:
            print(f"   ✅ Simple (better test pass rate)")
        elif complex_pass_rate > simple_pass_rate:
            print(f"   ✅ Complex (better test pass rate)")
        elif simple_time < complex_time:
            print(f"   ✅ Simple (faster, same quality)")
        else:
            print(f"   ✅ Tie (same quality and time)")

    elif results['simple']:
        print("Only simple approach completed successfully")
        print(f"Simple: {results['simple'].tests_passed}/{results['simple'].tests_total} tests in {results['simple'].generation_time_seconds:.1f}s")

    else:
        print("⚠️  Could not compare approaches")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test the simple code generator"
    )
    parser.add_argument(
        "--paper-id",
        type=str,
        default="2010.11929",
        help="arXiv paper ID to test (default: 2010.11929 - CLIP)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare simple vs complex approaches"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed logs"
    )

    args = parser.parse_args()

    if args.compare:
        asyncio.run(compare_approaches(args.paper_id))
    else:
        asyncio.run(test_simple_generation(args.paper_id, args.verbose))
