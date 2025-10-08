"""
Code Generation Orchestrator

Coordinates all agents to generate working code from papers.

Implements:
- AgentCoder pipeline (test-driven generation)
- Reflexion loops (learning from failures)
- Parallel agent execution where possible
- System-level reflection

Based on research: AgentCoder (2024), Reflexion (2023), SAGE (2024)
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.agents.config import AgentConfig, MemoryConfig, orchestrator_config
from app.agents.memory import TemporalMemory
from app.agents.paper_analyzer import PaperAnalyzerAgent, PaperAnalysis
from app.agents.test_designer import TestDesignerAgent, TestSuite
from app.agents.code_generator import CodeGeneratorAgent, GeneratedCode
from app.agents.test_executor import TestExecutorAgent, ExecutionResult
from app.agents.debugger import DebuggerAgent, DebugResult
from app.utils.logger import LoggerMixin


class QuickStartResult(BaseModel):
    """Final result from code generation"""

    # Status
    success: bool
    generation_time_seconds: float

    # Core outputs
    code: Optional[GeneratedCode] = None
    tests: Optional[TestSuite] = None
    test_results: Optional[ExecutionResult] = None

    # Metadata
    paper_title: str
    paper_id: str
    analysis_summary: Optional[str] = None

    # Debug info
    debug_iterations: int = 0
    total_attempts: int = 1

    # Learning
    system_reflection: Optional[str] = None

    # For display
    readme: Optional[str] = None


class CodeGenerationOrchestrator(LoggerMixin):
    """
    Main orchestrator for multi-agent code generation

    Implements the full AgentCoder pipeline:
    1. Analyze paper
    2. Design tests
    3. Generate code
    4. Execute tests
    5. Debug if needed (with reflection)
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        memory_config: Optional[MemoryConfig] = None
    ):
        # Use global config if not provided
        self.agent_config = config or orchestrator_config.agent_config
        self.memory_config = memory_config or orchestrator_config.memory_config

        # Initialize memory
        self.memory = TemporalMemory(self.memory_config)

        # Initialize agents
        self.paper_analyzer = PaperAnalyzerAgent(
            self.agent_config,
            self.memory
        )
        self.test_designer = TestDesignerAgent(
            self.agent_config,
            self.memory
        )
        self.code_generator = CodeGeneratorAgent(
            self.agent_config,
            self.memory
        )
        self.test_executor = TestExecutorAgent(
            self.agent_config
        )
        self.debugger = DebuggerAgent(
            self.agent_config,
            self.memory
        )

        self.log_info("Orchestrator initialized with 5 agents")

    async def generate_quick_start(
        self,
        paper_title: str,
        paper_abstract: str,
        paper_summary: Dict[str, Any],
        paper_id: str,
        paper_category: str = "cs.AI"
    ) -> QuickStartResult:
        """
        Generate working code from a paper

        This is the main entry point for code generation.

        Args:
            paper_title: Paper title
            paper_abstract: Paper abstract
            paper_summary: Existing AI summary from your system
            paper_id: arXiv ID
            paper_category: arXiv category

        Returns:
            Complete quick start with code, tests, and results
        """
        start_time = datetime.now()
        self.log_info(f"🚀 Starting code generation for: {paper_title[:60]}...")

        try:
            # STAGE 1: Analyze Paper
            self.log_info("📋 Stage 1: Analyzing paper...")
            analysis = await self._stage_1_analyze(
                paper_title,
                paper_abstract,
                paper_summary,
                paper_category
            )

            # STAGE 2: Design Tests (AgentCoder pattern)
            self.log_info("🧪 Stage 2: Designing tests...")
            tests = await self._stage_2_design_tests(
                analysis,
                paper_title,
                paper_category
            )

            # STAGE 3: Generate Code
            self.log_info("💻 Stage 3: Generating code...")
            code = await self._stage_3_generate_code(
                analysis,
                tests,
                paper_title
            )

            # STAGE 4: Execute Tests
            self.log_info("🏃 Stage 4: Running tests...")
            execution = await self._stage_4_execute_tests(
                code,
                tests
            )

            # STAGE 5: Debug if needed (with reflection)
            if not execution.success:
                self.log_info("🐛 Stage 5: Debugging failures...")
                debug_result = await self._stage_5_debug(
                    code,
                    execution,
                    analysis,
                    tests
                )

                if debug_result.success:
                    code = debug_result.final_code
                    execution = debug_result.final_execution
                    self.log_info("✅ Debugging successful!")
                else:
                    self.log_warning("⚠️ Could not fix all issues")
                    # Use best attempt
                    if debug_result.final_code:
                        code = debug_result.final_code
                    if debug_result.final_execution:
                        execution = debug_result.final_execution

                debug_iterations = debug_result.iterations
            else:
                debug_iterations = 0
                self.log_info("✅ All tests passed on first try!")

            # STAGE 6: Generate README
            readme = self._generate_readme(
                paper_title,
                analysis,
                code,
                tests,
                execution
            )

            # STAGE 7: System-level reflection
            system_reflection = await self._system_reflection(
                analysis,
                tests,
                execution,
                debug_iterations
            )

            # STAGE 8: Store success in memory
            if execution.success:
                await self._store_success(
                    paper_category,
                    analysis,
                    execution,
                    debug_iterations
                )

            # Calculate total time
            elapsed = (datetime.now() - start_time).total_seconds()

            self.log_info(f"🎉 Generation complete in {elapsed:.1f}s")

            return QuickStartResult(
                success=execution.success,
                generation_time_seconds=elapsed,
                code=code,
                tests=tests,
                test_results=execution,
                paper_title=paper_title,
                paper_id=paper_id,
                analysis_summary=analysis.core_algorithm[:200],
                debug_iterations=debug_iterations,
                total_attempts=1 + debug_iterations,
                system_reflection=system_reflection,
                readme=readme
            )

        except Exception as e:
            self.log_error("Code generation failed", error=e)

            elapsed = (datetime.now() - start_time).total_seconds()

            return QuickStartResult(
                success=False,
                generation_time_seconds=elapsed,
                paper_title=paper_title,
                paper_id=paper_id,
                analysis_summary=f"Generation failed: {str(e)}",
                readme=f"# Generation Failed\n\nError: {str(e)}"
            )

    async def _stage_1_analyze(
        self,
        paper_title: str,
        paper_abstract: str,
        paper_summary: Dict[str, Any],
        paper_category: str
    ) -> PaperAnalysis:
        """Stage 1: Paper Analysis"""

        analysis = await self.paper_analyzer.execute(
            paper_title=paper_title,
            paper_abstract=paper_abstract,
            paper_summary=paper_summary,
            paper_category=paper_category
        )

        self.log_info(f"Analysis complete - Complexity: {analysis.complexity_score}/10")
        return analysis

    async def _stage_2_design_tests(
        self,
        analysis: PaperAnalysis,
        paper_title: str,
        paper_domain: str
    ) -> TestSuite:
        """Stage 2: Test Design (AgentCoder pattern)"""

        tests = await self.test_designer.execute(
            analysis=analysis,
            paper_title=paper_title,
            paper_domain=paper_domain
        )

        self.log_info(f"Test suite created - {tests.total_tests} tests")
        return tests

    async def _stage_3_generate_code(
        self,
        analysis: PaperAnalysis,
        tests: TestSuite,
        paper_title: str,
        attempt: int = 1
    ) -> GeneratedCode:
        """Stage 3: Code Generation"""

        code = await self.code_generator.execute(
            analysis=analysis,
            test_suite=tests,
            paper_title=paper_title,
            attempt=attempt
        )

        self.log_info(f"Code generated - {len(code.main_code)} chars")
        return code

    async def _stage_4_execute_tests(
        self,
        code: GeneratedCode,
        tests: TestSuite
    ) -> ExecutionResult:
        """Stage 4: Test Execution"""

        execution = await self.test_executor.execute(
            code=code,
            tests=tests
        )

        if execution.success:
            self.log_info("✅ All tests passed!")
        else:
            self.log_warning(
                f"❌ {execution.tests_failed}/{execution.tests_total} tests failed"
            )

        return execution

    async def _stage_5_debug(
        self,
        code: GeneratedCode,
        execution: ExecutionResult,
        analysis: PaperAnalysis,
        tests: TestSuite,
        max_iterations: int = 3
    ) -> DebugResult:
        """Stage 5: Debugging with Reflection"""

        debug_result = await self.debugger.execute(
            code=code,
            execution_result=execution,
            analysis=analysis,
            test_executor=self.test_executor,
            test_suite=tests,
            max_iterations=max_iterations
        )

        return debug_result

    async def _system_reflection(
        self,
        analysis: PaperAnalysis,
        tests: TestSuite,
        execution: ExecutionResult,
        debug_iterations: int
    ) -> str:
        """System-level reflection on the generation process"""

        if execution.success:
            reflection = f"""Generation successful!
- Paper complexity: {analysis.complexity_score}/10
- Tests created: {tests.total_tests}
- Debug iterations: {debug_iterations}
- All {execution.tests_total} tests passing

This generation will improve future attempts."""
        else:
            reflection = f"""Generation partially successful.
- Paper complexity: {analysis.complexity_score}/10
- Tests created: {tests.total_tests}
- Tests passing: {execution.tests_passed}/{execution.tests_total}
- Debug iterations: {debug_iterations}

This teaches us about edge cases."""

        return reflection

    async def _store_success(
        self,
        paper_category: str,
        analysis: PaperAnalysis,
        execution: ExecutionResult,
        debug_iterations: int
    ):
        """Store successful generation for learning"""

        await self.memory.record_success(
            paper_category=paper_category,
            complexity=analysis.complexity_score,
            agent_config={
                "model": self.agent_config.llm_model,
                "debug_iterations": debug_iterations
            },
            performance_metrics={
                "tests_passed": execution.tests_passed,
                "tests_total": execution.tests_total,
                "execution_time": execution.execution_time,
                "iterations": debug_iterations
            }
        )

    def _generate_readme(
        self,
        paper_title: str,
        analysis: PaperAnalysis,
        code: GeneratedCode,
        tests: TestSuite,
        execution: ExecutionResult
    ) -> str:
        """Generate README for the quick start"""

        status_emoji = "✅" if execution.success else "⚠️"

        readme = f"""# {paper_title} - Quick Start Implementation

{status_emoji} **Status**: {"Working" if execution.success else "Partial"} ({execution.tests_passed}/{execution.tests_total} tests passing)

## 🎯 What This Implements

{analysis.core_algorithm[:300]}...

## 📦 Installation

```bash
pip install {' '.join(code.dependencies)}
```

## 🚀 Quick Start

```python
{code.example_code}
```

## 🧪 Tests

This implementation includes {tests.total_tests} comprehensive tests:
- {len(tests.functionality_tests)} functionality tests
- {len(tests.correctness_tests)} correctness tests
- {len(tests.edge_case_tests)} edge case tests
- {len(tests.performance_tests)} performance tests

Run tests:
```bash
pytest test_model.py -v
```

## ⚙️ Configuration

Hyperparameters from paper:
```python
{code.config_code[:300]}
...
```

## 📊 Complexity

- Implementation complexity: {analysis.complexity_score}/10
- Estimated implementation time: {analysis.estimated_implementation_time_hours}h
- Required compute: {analysis.required_compute}

## ⚠️ Important Notes

{chr(10).join(f'- {gotcha}' for gotcha in analysis.gotchas[:3])}

## 🤖 Generated by AI Paper Digest

This code was generated using multi-agent system based on:
- AgentCoder (2024): Test-driven generation
- Reflexion (2023): Learning from errors
- SAGE (2024): Memory-augmented agents

[Create your own quick starts →](https://aipaperdigest.com)
"""

        return readme


# Create global orchestrator instance for easy import
_global_orchestrator = None

def get_orchestrator() -> CodeGenerationOrchestrator:
    """Get or create global orchestrator instance"""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = CodeGenerationOrchestrator()
    return _global_orchestrator
