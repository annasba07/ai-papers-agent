"""
Test Executor Agent

Responsibilities:
- Execute code in isolated sandbox
- Run pytest tests
- Parse results and provide detailed feedback
- Ensure safety (no arbitrary code execution)

Based on AgentCoder (2024) execution patterns
"""
import asyncio
import tempfile
import os
import shutil
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.agents.code_generator import GeneratedCode
from app.agents.test_designer import TestSuite
from app.agents.config import AgentConfig
from app.utils.logger import LoggerMixin


class TestResult(BaseModel):
    """Individual test result"""
    name: str
    passed: bool
    duration: float
    error: Optional[str] = None
    stack_trace: Optional[str] = None


class ExecutionResult(BaseModel):
    """Complete execution results"""
    success: bool
    tests_passed: int
    tests_failed: int
    tests_total: int
    test_results: List[TestResult]
    stdout: str
    stderr: str
    execution_time: float
    error_summary: Optional[str] = None


class SimpleSandbox(LoggerMixin):
    """
    Simple sandbox for code execution
    Uses temporary directories and subprocess isolation

    TODO: Upgrade to Docker for production
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def execute_tests(
        self,
        code: GeneratedCode,
        tests: TestSuite
    ) -> ExecutionResult:
        """Execute tests in isolated environment"""

        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="agent_sandbox_")

        try:
            # Write files
            self._write_files(temp_dir, code, tests)

            # Install dependencies
            install_result = await self._install_dependencies(
                temp_dir,
                code.dependencies
            )

            if install_result.returncode != 0:
                return ExecutionResult(
                    success=False,
                    tests_passed=0,
                    tests_failed=0,
                    tests_total=0,
                    test_results=[],
                    stdout=install_result.stdout,
                    stderr=install_result.stderr,
                    execution_time=0,
                    error_summary="Failed to install dependencies"
                )

            # Run pytest
            test_result = await self._run_pytest(temp_dir)

            # Parse results
            execution_result = self._parse_pytest_output(
                test_result.stdout,
                test_result.stderr,
                test_result.returncode
            )

            return execution_result

        except asyncio.TimeoutError:
            self.log_error("Test execution timeout")
            return ExecutionResult(
                success=False,
                tests_passed=0,
                tests_failed=0,
                tests_total=0,
                test_results=[],
                stdout="",
                stderr="Execution timeout",
                execution_time=self.timeout,
                error_summary="Tests exceeded timeout limit"
            )

        except Exception as e:
            self.log_error("Test execution failed", error=e)
            return ExecutionResult(
                success=False,
                tests_passed=0,
                tests_failed=0,
                tests_total=0,
                test_results=[],
                stdout="",
                stderr=str(e),
                execution_time=0,
                error_summary=f"Execution error: {str(e)}"
            )

        finally:
            # Cleanup
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                self.log_warning(f"Failed to cleanup temp dir: {e}")

    def _write_files(
        self,
        temp_dir: str,
        code: GeneratedCode,
        tests: TestSuite
    ):
        """Write code and test files to temp directory"""

        # Write main code
        with open(os.path.join(temp_dir, "model.py"), "w") as f:
            f.write(code.main_code)

        # Write config
        with open(os.path.join(temp_dir, "config.py"), "w") as f:
            f.write(code.config_code)

        # Write utils if present
        if code.utils_code.strip():
            with open(os.path.join(temp_dir, "utils.py"), "w") as f:
                f.write(code.utils_code)

        # Write test file
        test_code = self._build_test_file(tests)
        with open(os.path.join(temp_dir, "test_model.py"), "w") as f:
            f.write(test_code)

        # Write __init__.py
        with open(os.path.join(temp_dir, "__init__.py"), "w") as f:
            f.write("")

    def _build_test_file(self, tests: TestSuite) -> str:
        """Build complete test file from test suite"""

        test_file = f"""
# Auto-generated test file
import pytest
import torch
import numpy as np
from model import *
from config import *

{tests.fixtures}

# Functionality Tests
"""
        for test in tests.functionality_tests:
            test_file += f"\n{test.test_code}\n"

        test_file += "\n# Correctness Tests\n"
        for test in tests.correctness_tests:
            test_file += f"\n{test.test_code}\n"

        test_file += "\n# Edge Case Tests\n"
        for test in tests.edge_case_tests:
            test_file += f"\n{test.test_code}\n"

        test_file += "\n# Performance Tests\n"
        for test in tests.performance_tests:
            test_file += f"\n{test.test_code}\n"

        return test_file

    async def _install_dependencies(
        self,
        temp_dir: str,
        dependencies: List[str]
    ):
        """Install dependencies in temp environment"""

        # Create requirements.txt
        req_file = os.path.join(temp_dir, "requirements.txt")
        with open(req_file, "w") as f:
            f.write("\n".join(dependencies))

        # Install with pip
        cmd = f"pip install -q -r {req_file} --target {temp_dir}"

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=60  # 1 minute for install
            )
            return type('Result', (), {
                'returncode': proc.returncode,
                'stdout': stdout.decode(),
                'stderr': stderr.decode()
            })()
        except asyncio.TimeoutError:
            proc.kill()
            raise

    async def _run_pytest(self, temp_dir: str):
        """Run pytest in temp directory"""

        cmd = f"cd {temp_dir} && python -m pytest test_model.py -v --tb=short --no-header"

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, 'PYTHONPATH': temp_dir}
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout
            )
            return type('Result', (), {
                'returncode': proc.returncode,
                'stdout': stdout.decode(),
                'stderr': stderr.decode()
            })()
        except asyncio.TimeoutError:
            proc.kill()
            raise

    def _parse_pytest_output(
        self,
        stdout: str,
        stderr: str,
        returncode: int
    ) -> ExecutionResult:
        """Parse pytest output into structured results"""

        test_results = []
        tests_passed = 0
        tests_failed = 0

        # Parse pytest output
        # Format: "test_name PASSED" or "test_name FAILED"
        lines = stdout.split('\n')

        for line in lines:
            if ' PASSED' in line or ' FAILED' in line:
                parts = line.split()
                if len(parts) >= 2:
                    test_name = parts[0].split('::')[-1]
                    passed = ' PASSED' in line

                    if passed:
                        tests_passed += 1
                    else:
                        tests_failed += 1

                    # Extract duration if present
                    duration = 0.0
                    for part in parts:
                        if 's' in part and part[:-1].replace('.', '').isdigit():
                            try:
                                duration = float(part[:-1])
                            except:
                                pass

                    # Extract error if failed
                    error = None
                    stack_trace = None
                    if not passed:
                        # Look for error details in subsequent lines
                        error = "Test failed"
                        if 'AssertionError' in stdout:
                            error = "Assertion failed"
                        elif 'Error' in stdout:
                            error = "Runtime error"

                    test_results.append(TestResult(
                        name=test_name,
                        passed=passed,
                        duration=duration,
                        error=error,
                        stack_trace=stack_trace
                    ))

        tests_total = tests_passed + tests_failed
        success = returncode == 0 and tests_failed == 0

        # Build error summary if tests failed
        error_summary = None
        if not success:
            if tests_failed > 0:
                error_summary = f"{tests_failed}/{tests_total} tests failed"
            elif "ModuleNotFoundError" in stderr:
                error_summary = "Missing module dependencies"
            elif "SyntaxError" in stderr:
                error_summary = "Syntax error in generated code"
            elif "ImportError" in stderr:
                error_summary = "Import error"
            else:
                error_summary = "Execution error"

        return ExecutionResult(
            success=success,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            tests_total=tests_total,
            test_results=test_results,
            stdout=stdout,
            stderr=stderr,
            execution_time=sum(t.duration for t in test_results),
            error_summary=error_summary
        )


class TestExecutorAgent(BaseAgent):
    """
    Agent 4: Test Executor

    Runs code in sandbox and provides detailed feedback
    """

    def __init__(self, config: AgentConfig):
        super().__init__(
            name="TestExecutor",
            role="Test execution expert",
            config=config,
            memory=None  # No memory needed for executor
        )
        self.sandbox = SimpleSandbox(timeout=config.timeout_seconds)

    def _get_system_prompt(self) -> str:
        return "You are a test execution agent."

    async def execute(
        self,
        code: GeneratedCode,
        tests: TestSuite
    ) -> ExecutionResult:
        """
        Execute tests against generated code

        Args:
            code: Generated code to test
            tests: Test suite to run

        Returns:
            Execution results with details
        """
        self.log_info("Executing tests in sandbox...")

        try:
            result = await self.sandbox.execute_tests(code, tests)

            if result.success:
                self.log_info(
                    f"✅ All tests passed ({result.tests_passed}/{result.tests_total})"
                )
            else:
                self.log_warning(
                    f"❌ Tests failed: {result.tests_failed}/{result.tests_total} failed"
                )

            return result

        except Exception as e:
            self.log_error("Test execution failed", error=e)

            return ExecutionResult(
                success=False,
                tests_passed=0,
                tests_failed=0,
                tests_total=0,
                test_results=[],
                stdout="",
                stderr=str(e),
                execution_time=0,
                error_summary=f"Executor error: {str(e)}"
            )
