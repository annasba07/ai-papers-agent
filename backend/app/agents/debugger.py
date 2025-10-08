"""
Debugger Agent

Responsibilities:
- Fix code based on test failures
- Use reflection to learn from bugs
- Iteratively improve code
- Provide detailed fix explanations

Based on Reflexion (2023) verbal reinforcement learning
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.agents.paper_analyzer import PaperAnalysis
from app.agents.code_generator import GeneratedCode
from app.agents.test_executor import ExecutionResult
from app.agents.memory import TemporalMemory
from app.agents.config import AgentConfig


class DebugIteration(BaseModel):
    """Single debug iteration"""
    iteration: int
    analysis: str
    fixes_applied: List[str]
    fixed_code: GeneratedCode


class DebugResult(BaseModel):
    """Final debug result"""
    success: bool
    iterations: int
    final_code: Optional[GeneratedCode] = None
    debug_history: List[DebugIteration]
    final_execution: Optional[ExecutionResult] = None
    reflection: Optional[str] = None


class DebuggerAgent(BaseAgent):
    """
    Agent 5: Debugger

    Uses reflection to fix code iteratively
    Learns from bugs to improve future generations
    """

    def __init__(
        self,
        config: AgentConfig,
        memory: Optional[TemporalMemory] = None
    ):
        super().__init__(
            name="Debugger",
            role="Debugging expert",
            config=config,
            memory=memory
        )

    def _get_system_prompt(self) -> str:
        return """You are an expert at debugging ML code.

Your approach:
1. Carefully analyze test failures
2. Identify root causes
3. Apply minimal fixes
4. Explain what you changed and why

Be precise. Other engineers will learn from your debugging."""

    async def execute(
        self,
        code: GeneratedCode,
        execution_result: ExecutionResult,
        analysis: PaperAnalysis,
        test_executor,  # TestExecutorAgent instance
        test_suite,  # TestSuite
        max_iterations: int = 3
    ) -> DebugResult:
        """
        Debug code through iterative reflection

        Args:
            code: Initial code that failed
            execution_result: Failed execution results
            analysis: Paper analysis for context
            test_executor: To re-run tests
            test_suite: Test suite
            max_iterations: Max debug attempts

        Returns:
            Debug result with final code
        """
        self.log_info(f"Starting debug process (max {max_iterations} iterations)...")

        debug_history = []
        current_code = code
        current_execution = execution_result

        for iteration in range(1, max_iterations + 1):
            self.log_info(f"Debug iteration {iteration}/{max_iterations}")

            # If tests pass, we're done
            if current_execution.success:
                self.log_info("✅ All tests passing after debug!")

                # Reflect on successful debug
                reflection = await self._reflect_on_success(
                    analysis,
                    code,
                    current_code,
                    debug_history
                )

                return DebugResult(
                    success=True,
                    iterations=iteration - 1,
                    final_code=current_code,
                    debug_history=debug_history,
                    final_execution=current_execution,
                    reflection=reflection
                )

            # Analyze failures and fix
            debug_iter = await self._debug_iteration(
                current_code,
                current_execution,
                analysis,
                iteration
            )

            debug_history.append(debug_iter)

            # Update code
            current_code = debug_iter.fixed_code

            # Re-run tests
            self.log_info("Re-running tests with fixed code...")
            current_execution = await test_executor.execute(
                current_code,
                test_suite
            )

        # Max iterations reached
        self.log_warning(f"Debug incomplete after {max_iterations} iterations")

        # Deep reflection on failure
        reflection = await self._reflect_on_failure(
            analysis,
            code,
            current_code,
            current_execution,
            debug_history
        )

        return DebugResult(
            success=False,
            iterations=max_iterations,
            final_code=current_code,
            debug_history=debug_history,
            final_execution=current_execution,
            reflection=reflection
        )

    async def _debug_iteration(
        self,
        code: GeneratedCode,
        execution: ExecutionResult,
        analysis: PaperAnalysis,
        iteration: int
    ) -> DebugIteration:
        """Single debug iteration"""

        # Build debug prompt
        prompt = self._build_debug_prompt(
            code,
            execution,
            analysis,
            iteration
        )

        # Generate fix
        debug_response = await self.generate(
            prompt,
            temperature=0.4,
            max_tokens=4000
        )

        # Parse response
        fixed_code, fixes_applied = self._parse_debug_response(
            debug_response,
            code
        )

        return DebugIteration(
            iteration=iteration,
            analysis=debug_response[:500],  # First 500 chars
            fixes_applied=fixes_applied,
            fixed_code=fixed_code
        )

    def _build_debug_prompt(
        self,
        code: GeneratedCode,
        execution: ExecutionResult,
        analysis: PaperAnalysis,
        iteration: int
    ) -> str:
        """Build debugging prompt"""

        # Summarize failures
        failed_tests = [t for t in execution.test_results if not t.passed]
        failure_summary = "\n".join([
            f"- {t.name}: {t.error or 'Failed'}"
            for t in failed_tests[:5]  # Top 5 failures
        ])

        # Get error details from stderr
        error_details = execution.stderr if execution.stderr else "No stderr"

        return f"""Debug this code that's failing tests.

PAPER CONTEXT:
Title: (from analysis)
Core Algorithm: {analysis.core_algorithm[:200]}...
Key Components: {', '.join(analysis.components[:3])}

CURRENT CODE:
```python
{code.main_code[:1500]}
... (truncated)
```

TEST FAILURES ({execution.tests_failed}/{execution.tests_total}):
{failure_summary}

ERROR OUTPUT:
{error_details[:500]}

STDOUT:
{execution.stdout[:500]}

DEBUG ITERATION #{iteration}

Analyze and fix:

1. ROOT CAUSE ANALYSIS:
   What's actually wrong? Be specific.
   - Is it a logic bug?
   - Shape mismatch?
   - Missing import?
   - Wrong hyperparameter?

2. THE FIX:
   What minimal changes will fix this?
   Don't rewrite everything - just fix the bug.

3. WHY IT FIXES IT:
   Explain how your fix addresses the root cause.

Return your response in this format:

ANALYSIS:
[Your root cause analysis]

FIXES:
1. [First fix description]
2. [Second fix description]
...

FIXED CODE JSON:
{{
  "main_code": "fixed model.py content",
  "config_code": "fixed config.py content (or original if unchanged)",
  "utils_code": "fixed utils.py content (or original if unchanged)",
  "example_code": "original example code",
  "dependencies": {code.dependencies},
  "framework": "{code.framework}"
}}

Focus on minimal, surgical fixes. Don't introduce new bugs.
"""

    def _parse_debug_response(
        self,
        response: str,
        original_code: GeneratedCode
    ) -> tuple[GeneratedCode, List[str]]:
        """Parse debug response into fixed code and fixes list"""

        import json
        import re

        # Extract fixes list
        fixes = []
        fixes_section = re.search(r'FIXES:(.*?)(?:FIXED CODE|$)', response, re.DOTALL)
        if fixes_section:
            fix_lines = fixes_section.group(1).strip().split('\n')
            fixes = [
                line.strip('- ').strip('1234567890. ').strip()
                for line in fix_lines
                if line.strip()
            ]

        # Extract JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                fixed_code = GeneratedCode(**data)
                return fixed_code, fixes
            except Exception as e:
                self.log_error("Failed to parse fixed code", error=e)

        # Fallback: return original code
        self.log_warning("Could not parse fixed code, returning original")
        return original_code, ["Failed to parse debug response"]

    async def _reflect_on_success(
        self,
        analysis: PaperAnalysis,
        original_code: GeneratedCode,
        fixed_code: GeneratedCode,
        debug_history: List[DebugIteration]
    ) -> str:
        """Reflect on successful debugging"""

        reflection_prompt = f"""You successfully debugged this code in {len(debug_history)} iterations.

Original bugs:
{self._summarize_debug_history(debug_history)}

Reflect (3-4 sentences):
1. What was the root cause?
2. What pattern should you remember?
3. How can you avoid this bug in future generations?

Be specific and actionable.
"""

        try:
            reflection = await self.generate(
                reflection_prompt,
                temperature=0.7
            )

            # Store reflection
            if self.memory:
                await self.memory.add_reflection(
                    agent=self.name,
                    reflection=reflection,
                    task_type="successful_debug",
                    context={
                        "iterations": len(debug_history),
                        "bug_types": [fix for iter in debug_history for fix in iter.fixes_applied]
                    }
                )

            return reflection

        except Exception as e:
            self.log_error("Failed to generate reflection", error=e)
            return "Debug completed successfully"

    async def _reflect_on_failure(
        self,
        analysis: PaperAnalysis,
        original_code: GeneratedCode,
        final_code: GeneratedCode,
        final_execution: ExecutionResult,
        debug_history: List[DebugIteration]
    ) -> str:
        """Deep reflection on debugging failure"""

        reflection_prompt = f"""You tried to debug this code but failed after {len(debug_history)} iterations.

Paper complexity: {analysis.complexity_score}/10

Debug attempts:
{self._summarize_debug_history(debug_history)}

Final failures:
{final_execution.error_summary}

Deeply reflect (5-6 sentences):
1. Why couldn't you fix it?
2. Was the original code too broken?
3. Should you have started over?
4. What would you do differently?
5. What does this teach you about code generation?

Be brutally honest - this is critical learning.
"""

        try:
            reflection = await self.generate(
                reflection_prompt,
                temperature=0.8
            )

            # Store critical reflection
            if self.memory:
                await self.memory.add_reflection(
                    agent=self.name,
                    reflection=reflection,
                    task_type="failed_debug",
                    context={
                        "iterations": len(debug_history),
                        "complexity": analysis.complexity_score,
                        "final_error": final_execution.error_summary
                    }
                )

            return reflection

        except Exception as e:
            self.log_error("Failed to generate failure reflection", error=e)
            return "Debug failed - needs review"

    def _summarize_debug_history(
        self,
        debug_history: List[DebugIteration]
    ) -> str:
        """Summarize debug iterations"""

        summary = []
        for iter in debug_history:
            fixes = ', '.join(iter.fixes_applied[:3])  # Top 3 fixes
            summary.append(f"Iteration {iter.iteration}: {fixes}")

        return '\n'.join(summary)
