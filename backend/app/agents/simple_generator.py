"""
Elegant Code Generator - Single-conversation approach

Key simplifications:
1. Claude self-orchestrates via extended context (not separate agents)
2. Tools are simple functions (not classes)
3. Memory is JSON (not graph database)
4. Self-correcting in single conversation
5. ~300 lines instead of 4,000

Based on learnings from complex multi-agent system, but simplified.
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

from anthropic import Anthropic


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
    Elegant code generator using Claude self-orchestration

    Instead of separate agent classes, Claude orchestrates itself
    through a single extended conversation with tool use.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required")

        self.client = Anthropic(api_key=self.api_key)
        self.memory_file = Path(__file__).parent / "memory.json"

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
        """Run conversation with Claude, handling tool use"""

        max_turns = 10  # Prevent infinite loops

        for turn in range(max_turns):
            print(f"🔄 Conversation turn {turn + 1}/{max_turns}")

            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-sonnet-4-20250514",
                max_tokens=16000,  # Extended for self-correction
                temperature=0.7,
                tools=[{
                    "name": "execute_tests",
                    "description": "Execute Python code and pytest tests in a sandbox. Returns test results and any errors.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "code_files": {
                                "type": "object",
                                "description": "Dict of filename: content for all Python files",
                                "properties": {
                                    "model.py": {"type": "string"},
                                    "config.py": {"type": "string"},
                                    "utils.py": {"type": "string"},
                                    "test_model.py": {"type": "string"}
                                },
                                "required": ["model.py", "test_model.py"]
                            },
                            "dependencies": {
                                "type": "array",
                                "description": "List of pip packages to install",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["code_files", "dependencies"]
                    }
                }],
                messages=messages
            )

            # Check if Claude is done (no tool use)
            if response.stop_reason == "end_turn":
                # Extract final result from last message
                final_text = next(
                    (block.text for block in response.content if hasattr(block, 'text')),
                    None
                )

                if final_text:
                    try:
                        # Try to parse JSON result
                        import re
                        json_match = re.search(r'\{.*\}', final_text, re.DOTALL)
                        if json_match:
                            return json.loads(json_match.group())
                        else:
                            return {"raw_response": final_text}
                    except:
                        return {"raw_response": final_text}

                return {"error": "No response from Claude"}

            # Handle tool use
            if response.stop_reason == "tool_use":
                tool_use_block = next(
                    block for block in response.content
                    if block.type == "tool_use"
                )

                # Execute the tool
                tool_result = await self._execute_tool(
                    tool_use_block.name,
                    tool_use_block.input
                )

                # Add assistant's response and tool result to conversation
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": json.dumps(tool_result)
                    }]
                })

                # Continue conversation
                continue

        return {"error": "Max conversation turns reached"}

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


# Global instance for easy access
_generator_instance = None

def get_simple_generator() -> SimpleCodeGenerator:
    """Get or create global generator instance"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = SimpleCodeGenerator()
    return _generator_instance
