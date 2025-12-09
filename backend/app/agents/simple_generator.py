"""
Elegant Code Generator - Single-conversation approach

Key simplifications:
1. LLM self-orchestrates via extended context (not separate agents)
2. Tools are simple functions (not classes)
3. Memory is JSON (not graph database)
4. Self-correcting in single conversation
5. Multi-provider support (Claude, GPT-4, Gemini)

Based on learnings from complex multi-agent system, but simplified.

Environment Variables:
- CODE_GEN_PROVIDER: "anthropic" | "openai" | "gemini" (default: auto-detect)
- ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY: Provider API keys
"""
import asyncio
import os
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.agents.llm_providers import get_llm_provider, get_default_provider, BaseLLMProvider


class GenerationResult(BaseModel):
    """Result from code generation"""
    success: bool
    generation_time_seconds: float
    paper_id: str
    paper_title: str

    # Generated artifacts
    code: Optional[str] = None
    tests: Optional[str] = None
    config: Optional[str] = None
    example: Optional[str] = None
    readme: Optional[str] = None

    # Execution results
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0

    # Metadata
    complexity: Optional[int] = None
    debug_iterations: int = 0
    reflection: Optional[str] = None

    # Raw output
    conversation_history: List[Dict] = []


class SimpleCodeGenerator:
    """
    Elegant code generator using LLM self-orchestration

    Instead of separate agent classes, the LLM orchestrates itself
    through a single extended conversation with iterative debugging.

    Supports multiple providers: Claude, GPT-4, Gemini
    """

    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the code generator with specified or auto-detected provider

        Args:
            provider: "anthropic", "openai", or "gemini" (auto-detects if None)
            api_key: Optional API key (otherwise uses env vars)
        """
        self.provider_name = provider or get_default_provider()
        self.llm: BaseLLMProvider = get_llm_provider(
            provider=self.provider_name,
            api_key=api_key
        )
        self.memory_file = Path(__file__).parent / "memory.json"

        print(f"🤖 Code Generator initialized with {self.llm.provider_name} ({self.llm.get_model_name()})")

    async def generate(
        self,
        paper_title: str,
        paper_abstract: str,
        paper_id: str,
        paper_category: str = "cs.AI"
    ) -> GenerationResult:
        """
        Generate code from paper in single conversation

        Claude handles the entire pipeline:
        1. Analyze paper
        2. Design tests (TDD)
        3. Generate code
        4. Execute tests (via tool)
        5. Debug if needed
        6. Return complete package
        """
        start_time = datetime.now()

        print(f"🚀 Starting elegant code generation for: {paper_title[:60]}...")

        # Load past learnings
        learnings = self._load_learnings(paper_category)

        # Build the guiding prompt
        conversation = self._build_conversation(
            paper_title,
            paper_abstract,
            learnings
        )

        # Let Claude orchestrate itself
        try:
            result = await self._run_conversation(conversation)

            # Parse result
            generation_result = self._parse_result(
                result,
                paper_id,
                paper_title,
                start_time
            )

            # Save learning if successful
            if generation_result.success:
                self._save_learning(generation_result, paper_category)

            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"✅ Generation complete in {elapsed:.1f}s")

            return generation_result

        except Exception as e:
            print(f"❌ Generation failed: {e}")
            elapsed = (datetime.now() - start_time).total_seconds()

            return GenerationResult(
                success=False,
                generation_time_seconds=elapsed,
                paper_id=paper_id,
                paper_title=paper_title,
                readme=f"# Generation Failed\n\nError: {str(e)}"
            )

    def _build_conversation(
        self,
        paper_title: str,
        paper_abstract: str,
        learnings: List[Dict]
    ) -> List[Dict]:
        """Build conversation that guides Claude through pipeline"""

        learnings_text = self._format_learnings(learnings)

        prompt = f"""Generate working code for this AI research paper.

PAPER:
Title: {paper_title}
Abstract: {paper_abstract}

LEARNINGS FROM PAST GENERATIONS:
{learnings_text}

YOUR TASK:
Create a complete, working implementation of this paper's core algorithm.

PROCESS (follow exactly):

1. ANALYZE THE PAPER
   - Extract the core algorithm/method
   - Identify key components and their interactions
   - List hyperparameters from the paper
   - Assess complexity (1-10 scale)
   - Predict common implementation pitfalls

2. DESIGN TESTS FIRST (TDD - Test-Driven Development)
   This is critical! Write tests BEFORE code.

   Create 4 types of tests:
   a) Functionality tests: Does each component work?
   b) Correctness tests: Does output match expected behavior?
   c) Edge cases: Boundary conditions, empty inputs, etc.
   d) Performance tests: Basic benchmarks

   Use pytest format. Include fixtures if needed.

3. GENERATE CODE
   Write clean implementation that PASSES your tests:
   - model.py: Main implementation
   - config.py: Hyperparameters and configuration
   - utils.py: Helper functions (if needed)
   - example.py: Quick start usage example

   Use clear variable names, type hints, docstrings.
   Include paper citation in docstrings.

4. EXECUTE TESTS
   Use the execute_tests tool to run your code and tests.

   If tests fail:
   - Analyze the error carefully
   - Fix the specific issue (don't rewrite everything)
   - Execute again
   - Max 3 debug iterations

5. CREATE README
   Write a README.md with:
   - What this implements
   - Installation instructions
   - Quick start example
   - Test results summary

6. REFLECT
   Briefly reflect on:
   - What worked well?
   - What was challenging?
   - Key insights for future generations?

IMPORTANT NOTES:
- Tests MUST come before code (AgentCoder pattern)
- Keep code simple and readable
- Use paper's hyperparameters exactly
- Debug iteratively, not by rewriting
- Learn from failures

OUTPUT FORMAT:
Return a JSON object with:
{{
  "analysis": {{
    "core_algorithm": "...",
    "components": ["..."],
    "complexity": 7,
    "hyperparameters": {{}},
    "pitfalls": ["..."]
  }},
  "tests": "complete pytest test file",
  "code": {{
    "model": "model.py content",
    "config": "config.py content",
    "utils": "utils.py content",
    "example": "example.py content"
  }},
  "readme": "README.md content",
  "reflection": "What I learned...",
  "execution_results": {{
    "tests_total": 15,
    "tests_passed": 15,
    "tests_failed": 0,
    "debug_iterations": 1
  }}
}}

Begin! Think step by step and use the execute_tests tool when ready to test.
"""

        return [{"role": "user", "content": prompt}]

    async def _run_conversation(self, messages: List[Dict]) -> Dict:
        """
        Run code generation with iterative debugging

        Uses a simpler approach that works across all providers:
        1. Generate code in one shot
        2. Execute tests ourselves
        3. If tests fail, send debug prompt
        4. Repeat up to max_debug_iterations
        """
        import re

        max_debug_iterations = 3
        debug_iteration = 0

        # System prompt for code generation
        system_prompt = """You are an expert AI/ML code generator. You implement research papers as working Python code.

CRITICAL: Your response MUST be valid JSON only. No markdown, no explanations outside JSON.

When generating code:
- Use clean, readable Python with type hints
- Include docstrings with paper references
- Use paper's exact hyperparameters
- Write comprehensive pytest tests FIRST (TDD)"""

        print(f"🔄 Generating code with {self.llm.provider_name}...")

        # Step 1: Generate initial code
        response = await self.llm.generate(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=16000
        )

        response_text = response.text

        # Try to parse JSON
        result = self._extract_json(response_text)

        if not result:
            return {"raw_response": response_text}

        # Step 2: Execute tests if code was generated
        code = result.get('code', {})
        tests = result.get('tests')

        if code and tests:
            code_files = {
                'model.py': code.get('model', ''),
                'config.py': code.get('config', ''),
                'utils.py': code.get('utils', ''),
                'test_model.py': tests
            }

            # Filter out empty files
            code_files = {k: v for k, v in code_files.items() if v}

            if 'model.py' in code_files and 'test_model.py' in code_files:
                # Get dependencies from result
                deps = result.get('analysis', {}).get('hyperparameters', {}).get('dependencies', [])
                if not deps:
                    deps = ['torch', 'numpy', 'pytest']

                # Execute tests
                test_result = await self._execute_tests_impl(code_files, deps)

                # Update result with execution results
                result['execution_results'] = {
                    'tests_total': test_result.get('tests_total', 0),
                    'tests_passed': test_result.get('tests_passed', 0),
                    'tests_failed': test_result.get('tests_failed', 0),
                    'debug_iterations': 0
                }

                # Step 3: Debug if tests failed
                while not test_result.get('success') and debug_iteration < max_debug_iterations:
                    debug_iteration += 1
                    print(f"🔧 Debug iteration {debug_iteration}/{max_debug_iterations}")

                    # Create debug prompt
                    debug_prompt = f"""Your tests failed. Fix the issues.

ERROR OUTPUT:
{test_result.get('stderr', '')[:2000]}
{test_result.get('stdout', '')[:2000]}

CURRENT CODE:
model.py:
{code_files.get('model.py', '')[:3000]}

test_model.py:
{code_files.get('test_model.py', '')[:2000]}

Analyze the error and provide ONLY updated code as JSON:
{{
  "code": {{
    "model": "fixed model.py content",
    "config": "config.py content if changed",
    "utils": "utils.py content if changed"
  }},
  "tests": "fixed test_model.py content"
}}"""

                    # Get fix from LLM
                    fix_messages = [{"role": "user", "content": debug_prompt}]
                    fix_response = await self.llm.generate(
                        messages=fix_messages,
                        system_prompt="You are debugging Python code. Respond with JSON only.",
                        temperature=0.5,
                        max_tokens=8000
                    )

                    fix_result = self._extract_json(fix_response.text)

                    if fix_result:
                        # Update code files with fixes
                        if fix_result.get('code'):
                            for key, val in fix_result['code'].items():
                                if val:
                                    code_files[f'{key}.py' if not key.endswith('.py') else key] = val
                        if fix_result.get('tests'):
                            code_files['test_model.py'] = fix_result['tests']

                        # Re-run tests
                        test_result = await self._execute_tests_impl(code_files, deps)

                        # Update result
                        result['execution_results'] = {
                            'tests_total': test_result.get('tests_total', 0),
                            'tests_passed': test_result.get('tests_passed', 0),
                            'tests_failed': test_result.get('tests_failed', 0),
                            'debug_iterations': debug_iteration
                        }

                        # Update code in result
                        result['code'] = {
                            'model': code_files.get('model.py', ''),
                            'config': code_files.get('config.py', ''),
                            'utils': code_files.get('utils.py', ''),
                            'example': code_files.get('example.py', '')
                        }
                        result['tests'] = code_files.get('test_model.py', '')

        return result

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from LLM response text"""
        import re

        # Try to find JSON block
        try:
            # First try: direct JSON parse
            return json.loads(text)
        except:
            pass

        try:
            # Second try: find JSON in markdown code block
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except:
            pass

        try:
            # Third try: find any JSON object
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return None

    async def _execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Execute a tool call"""

        if tool_name == "execute_tests":
            return await self._execute_tests_impl(
                tool_input['code_files'],
                tool_input.get('dependencies', [])
            )

        return {"error": f"Unknown tool: {tool_name}"}

    async def _execute_tests_impl(
        self,
        code_files: Dict[str, str],
        dependencies: List[str]
    ) -> Dict:
        """Execute code and tests in temporary sandbox"""

        temp_dir = tempfile.mkdtemp(prefix="simple_sandbox_")

        try:
            print(f"  📦 Executing tests in sandbox...")

            # Write code files
            for filename, content in code_files.items():
                file_path = Path(temp_dir) / filename
                file_path.write_text(content)

            # Install dependencies
            if dependencies:
                install_cmd = f"pip install -q {' '.join(dependencies)} --target {temp_dir}"
                install_result = subprocess.run(
                    install_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if install_result.returncode != 0:
                    return {
                        "success": False,
                        "error": "Dependency installation failed",
                        "stderr": install_result.stderr
                    }

            # Run pytest
            test_cmd = f"cd {temp_dir} && python -m pytest test_model.py -v --tb=short"
            test_result = subprocess.run(
                test_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, 'PYTHONPATH': temp_dir}
            )

            # Parse results
            stdout = test_result.stdout
            stderr = test_result.stderr

            # Count tests
            passed = stdout.count(" PASSED")
            failed = stdout.count(" FAILED")
            total = passed + failed

            success = test_result.returncode == 0 and failed == 0

            result = {
                "success": success,
                "tests_total": total,
                "tests_passed": passed,
                "tests_failed": failed,
                "stdout": stdout[-1000:],  # Last 1000 chars
                "stderr": stderr[-1000:] if stderr else None
            }

            if success:
                print(f"  ✅ Tests passed: {passed}/{total}")
            else:
                print(f"  ❌ Tests failed: {failed}/{total}")

            return result

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test execution timeout (30s limit)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }
        finally:
            # Cleanup
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

    def _parse_result(
        self,
        result: Dict,
        paper_id: str,
        paper_title: str,
        start_time: datetime
    ) -> GenerationResult:
        """Parse Claude's result into GenerationResult"""

        elapsed = (datetime.now() - start_time).total_seconds()

        # Handle raw response (not JSON)
        if "raw_response" in result:
            return GenerationResult(
                success=False,
                generation_time_seconds=elapsed,
                paper_id=paper_id,
                paper_title=paper_title,
                readme=f"# Partial Result\n\n{result['raw_response'][:1000]}"
            )

        # Parse structured result
        exec_results = result.get('execution_results', {})
        code = result.get('code', {})

        return GenerationResult(
            success=exec_results.get('tests_failed', 1) == 0,
            generation_time_seconds=elapsed,
            paper_id=paper_id,
            paper_title=paper_title,
            code=code.get('model'),
            tests=result.get('tests'),
            config=code.get('config'),
            example=code.get('example'),
            readme=result.get('readme'),
            tests_total=exec_results.get('tests_total', 0),
            tests_passed=exec_results.get('tests_passed', 0),
            tests_failed=exec_results.get('tests_failed', 0),
            complexity=result.get('analysis', {}).get('complexity'),
            debug_iterations=exec_results.get('debug_iterations', 0),
            reflection=result.get('reflection')
        )

    def _load_learnings(self, category: str) -> List[Dict]:
        """Load past successful generations from JSON"""

        if not self.memory_file.exists():
            return []

        try:
            data = json.loads(self.memory_file.read_text())
            learnings = data.get('learnings', [])

            # Filter by category and get recent ones
            category_learnings = [
                l for l in learnings
                if l.get('category') == category
            ]

            return category_learnings[-5:]  # Last 5

        except Exception as e:
            print(f"⚠️  Failed to load learnings: {e}")
            return []

    def _save_learning(self, result: GenerationResult, category: str):
        """Save successful generation to memory"""

        try:
            # Load existing
            if self.memory_file.exists():
                data = json.loads(self.memory_file.read_text())
            else:
                data = {'learnings': []}

            # Add new learning
            data['learnings'].append({
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'paper_id': result.paper_id,
                'complexity': result.complexity,
                'tests_passed': result.tests_passed,
                'tests_total': result.tests_total,
                'debug_iterations': result.debug_iterations,
                'reflection': result.reflection
            })

            # Keep last 100 learnings
            data['learnings'] = data['learnings'][-100:]

            # Save
            self.memory_file.write_text(json.dumps(data, indent=2))
            print(f"💾 Saved learning to memory")

        except Exception as e:
            print(f"⚠️  Failed to save learning: {e}")

    def _format_learnings(self, learnings: List[Dict]) -> str:
        """Format learnings for prompt"""

        if not learnings:
            return "No past learnings yet - this is your first generation in this category!"

        formatted = []
        for i, learning in enumerate(learnings, 1):
            formatted.append(f"""
Learning {i}:
- Paper: {learning.get('paper_id')}
- Complexity: {learning.get('complexity')}/10
- Tests: {learning.get('tests_passed')}/{learning.get('tests_total')} passed
- Debug iterations: {learning.get('debug_iterations')}
- Reflection: {learning.get('reflection', 'N/A')[:200]}
""")

        return "\n".join(formatted)


# Global instance cache by provider
_generator_instances: Dict[str, SimpleCodeGenerator] = {}


def get_simple_generator(provider: Optional[str] = None) -> SimpleCodeGenerator:
    """
    Get or create global generator instance for a provider

    Args:
        provider: "anthropic", "openai", or "gemini" (auto-detects if None)

    Returns:
        SimpleCodeGenerator instance for the specified provider
    """
    global _generator_instances

    # Get provider (may auto-detect)
    actual_provider = provider or get_default_provider()

    # Create instance if needed
    if actual_provider not in _generator_instances:
        _generator_instances[actual_provider] = SimpleCodeGenerator(provider=actual_provider)

    return _generator_instances[actual_provider]
