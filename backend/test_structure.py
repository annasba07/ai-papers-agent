"""
Structure test for multi-agent system
Tests that all components are properly imported and configured
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all agent modules can be imported"""
    print("🧪 Testing imports...")

    try:
        from app.agents import (
            get_orchestrator,
            CodeGenerationOrchestrator,
            PaperAnalyzerAgent,
            TestDesignerAgent,
            CodeGeneratorAgent,
            TestExecutorAgent,
            DebuggerAgent,
            TemporalMemory,
            AgentConfig,
            QuickStartResult
        )
        print("✅ All agent classes imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration is valid"""
    print("\n🧪 Testing configuration...")

    try:
        from app.agents.config import orchestrator_config

        print(f"  Model: {orchestrator_config.agent_config.llm_model}")
        print(f"  Temperature: {orchestrator_config.agent_config.temperature}")
        print(f"  Max tokens: {orchestrator_config.agent_config.max_tokens}")
        print(f"  Max debug iterations: {orchestrator_config.max_debug_iterations}")
        print(f"  Memory enabled: {orchestrator_config.memory_config.enable_memory}")
        print("✅ Configuration valid")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_orchestrator_creation():
    """Test orchestrator can be created"""
    print("\n🧪 Testing orchestrator creation...")

    try:
        from app.agents import get_orchestrator

        orchestrator = get_orchestrator()
        print(f"  Orchestrator created: {orchestrator.__class__.__name__}")
        print(f"  Paper Analyzer: {orchestrator.paper_analyzer.__class__.__name__}")
        print(f"  Test Designer: {orchestrator.test_designer.__class__.__name__}")
        print(f"  Code Generator: {orchestrator.code_generator.__class__.__name__}")
        print(f"  Test Executor: {orchestrator.test_executor.__class__.__name__}")
        print(f"  Debugger: {orchestrator.debugger.__class__.__name__}")
        print(f"  Memory: {orchestrator.memory.__class__.__name__}")
        print("✅ Orchestrator created with all 5 agents")
        return True
    except Exception as e:
        print(f"❌ Orchestrator creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_system():
    """Test memory system"""
    print("\n🧪 Testing memory system...")

    try:
        from app.agents.memory import TemporalMemory
        from app.agents.config import MemoryConfig

        config = MemoryConfig()
        memory = TemporalMemory(config)

        print(f"  Memory type: {memory.__class__.__name__}")
        print(f"  Store type: {memory.store.__class__.__name__}")
        print(f"  TTL days: {config.memory_ttl_days}")
        print("✅ Memory system initialized")
        return True
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False


def test_api_endpoint():
    """Test API endpoint exists"""
    print("\n🧪 Testing API endpoint...")

    try:
        from app.api.v1.endpoints import papers

        # Check if generate_code_for_paper exists
        if hasattr(papers, 'generate_code_for_paper'):
            print("  ✅ generate_code_for_paper endpoint found")
        else:
            print("  ❌ generate_code_for_paper endpoint not found")
            return False

        # Check router
        if hasattr(papers, 'router'):
            routes = [route.path for route in papers.router.routes]
            print(f"  Available routes: {len(routes)}")
            if '/{paper_id}/generate-code' in routes:
                print("  ✅ /generate-code route registered")
            else:
                print(f"  ⚠️  Routes: {routes}")

        print("✅ API endpoint structure valid")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pydantic_models():
    """Test all Pydantic models"""
    print("\n🧪 Testing Pydantic models...")

    try:
        from app.agents.paper_analyzer import PaperAnalysis
        from app.agents.test_designer import TestSuite, TestCase
        from app.agents.code_generator import GeneratedCode
        from app.agents.test_executor import ExecutionResult, TestResult
        from app.agents.debugger import DebugResult, DebugIteration
        from app.agents.orchestrator import QuickStartResult

        print("  ✅ PaperAnalysis")
        print("  ✅ TestSuite, TestCase")
        print("  ✅ GeneratedCode")
        print("  ✅ ExecutionResult, TestResult")
        print("  ✅ DebugResult, DebugIteration")
        print("  ✅ QuickStartResult")
        print("✅ All Pydantic models importable")
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Test file structure"""
    print("\n🧪 Testing file structure...")

    backend_dir = Path(__file__).parent
    agents_dir = backend_dir / "app" / "agents"

    required_files = [
        "__init__.py",
        "base.py",
        "config.py",
        "memory.py",
        "orchestrator.py",
        "paper_analyzer.py",
        "test_designer.py",
        "code_generator.py",
        "test_executor.py",
        "debugger.py"
    ]

    all_exist = True
    for file in required_files:
        file_path = agents_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} missing")
            all_exist = False

    if all_exist:
        print("✅ All required files present")
        return True
    else:
        print("❌ Some files missing")
        return False


def main():
    """Run all tests"""
    print("="*80)
    print("🤖 Multi-Agent System Structure Test")
    print("="*80)
    print()

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Pydantic Models", test_pydantic_models),
        ("Memory System", test_memory_system),
        ("Orchestrator Creation", test_orchestrator_creation),
        ("API Endpoint", test_api_endpoint),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results.append((name, False))

    print("\n" + "="*80)
    print("📊 Test Results Summary")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print()
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 All tests passed! System structure is valid.")
        print("\n📝 Next steps:")
        print("  1. Set ANTHROPIC_API_KEY in backend/.env")
        print("  2. Set GEMINI_API_KEY in backend/.env")
        print("  3. Run: python test_agent_system.py --paper-id 2010.11929")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
