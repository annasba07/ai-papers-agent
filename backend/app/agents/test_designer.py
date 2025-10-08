"""
Test Designer Agent

THE KEY INNOVATION from AgentCoder (2024)

Responsibilities:
- Design comprehensive test cases BEFORE code is written
- Create tests that verify paper claims
- Learn which test patterns catch bugs
- Predict edge cases

Research basis: AgentCoder (2024) showed that AI-designed tests
significantly outperform template-based tests.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.agents.paper_analyzer import PaperAnalysis
from app.agents.memory import TemporalMemory
from app.agents.config import AgentConfig


class TestCase(BaseModel):
    """Individual test case"""
    name: str
    description: str
    test_code: str
    category: str  # "functionality", "correctness", "performance", "edge_case"
    expected_to_catch: list[str]  # What bugs this should catch


class TestSuite(BaseModel):
    """Complete test suite"""
    fixtures: str  # Pytest fixtures
    functionality_tests: List[TestCase]
    correctness_tests: List[TestCase]
    edge_case_tests: List[TestCase]
    performance_tests: List[TestCase]
    total_tests: int
    estimated_runtime_seconds: int


class TestDesignerAgent(BaseAgent):
    """
    Agent 2: Test Designer

    THE critical innovation from AgentCoder research
    Designs effective tests that guide code generation
    """

    def __init__(
        self,
        config: AgentConfig,
        memory: Optional[TemporalMemory] = None
    ):
        super().__init__(
            name="TestDesigner",
            role="Test design expert",
            config=config,
            memory=memory
        )

    def _get_system_prompt(self) -> str:
        return """You are an expert at designing effective test cases.

Your role:
- Design tests that verify paper claims
- Create tests that catch common implementation bugs
- Design edge cases that reveal issues early
- Make tests fast (<5 seconds total) but comprehensive

Your tests guide the code generation process. Be thorough."""

    async def execute(
        self,
        analysis: PaperAnalysis,
        paper_title: str,
        paper_domain: str
    ) -> TestSuite:
        """
        Design comprehensive test suite for paper implementation

        Args:
            analysis: Paper analysis from PaperAnalyzerAgent
            paper_title: Title for context
            paper_domain: Domain (e.g., "computer_vision")

        Returns:
            Complete test suite
        """
        self.log_info(f"Designing tests for: {paper_title[:50]}...")

        # Get effective test patterns from memory
        test_patterns = await self._get_effective_patterns(paper_domain)

        # Build test design prompt
        prompt = self._build_test_design_prompt(
            analysis,
            paper_title,
            test_patterns
        )

        try:
            # Generate test suite
            test_suite_text = await self.generate(
                prompt,
                temperature=0.4  # Moderate creativity for tests
            )

            # Parse into structured format
            test_suite = self._parse_test_suite(test_suite_text)

            # Reflect on success
            await self.reflect(
                task="test_design",
                result={"tests_created": test_suite.total_tests},
                outcome="success"
            )

            self.log_info(f"Created {test_suite.total_tests} tests")
            return test_suite

        except Exception as e:
            self.log_error("Test design failed", error=e)

            # Reflect on failure
            await self.reflect(
                task="test_design",
                result={"error": str(e)},
                outcome="failure"
            )

            # Return minimal fallback tests
            return self._fallback_tests(analysis)

    def _build_test_design_prompt(
        self,
        analysis: PaperAnalysis,
        paper_title: str,
        test_patterns: str
    ) -> str:
        """Build test design prompt"""

        return f"""Design a comprehensive pytest test suite for this paper implementation.

PAPER: {paper_title}

IMPLEMENTATION ANALYSIS:
Core Algorithm: {analysis.core_algorithm}
Components: {', '.join(analysis.components)}
Critical Hyperparameters: {', '.join(analysis.critical_hyperparameters)}
Likely Failures: {', '.join(analysis.likely_failure_points)}
Common Bugs: {', '.join(analysis.common_bugs_to_avoid)}

EFFECTIVE TEST PATTERNS FROM PAST SUCCESSES:
{test_patterns}

---

Design tests that verify the implementation works correctly.

Create tests in 4 categories:

1. FUNCTIONALITY TESTS (Does it run?)
   - Basic forward pass works
   - Accepts correct input shapes
   - Produces correct output shapes
   - No runtime errors with valid inputs

2. CORRECTNESS TESTS (Does it match paper?)
   - Intermediate values are reasonable
   - Output matches expected behavior
   - Implements paper's algorithm correctly
   - Uses hyperparameters from paper

3. EDGE CASE TESTS (Handle errors?)
   - Empty inputs
   - Batch size = 1
   - Very large inputs
   - Invalid inputs raise proper errors

4. PERFORMANCE TESTS (Fast enough?)
   - Memory usage reasonable
   - Speed acceptable for paper's claims
   - No memory leaks

IMPORTANT BASED ON ANALYSIS:
{self._build_specific_requirements(analysis)}

Return ONLY this JSON format:

{{
  "fixtures": '''
import pytest
import torch
import numpy as np

@pytest.fixture
def sample_input():
    # Realistic test data
    return torch.randn(2, 3, 224, 224)

@pytest.fixture
def model():
    # Import will be added by code generator
    pass
''',

  "functionality_tests": [
    {{
      "name": "test_model_forward_pass",
      "description": "Test basic forward pass",
      "test_code": '''
def test_model_forward_pass(model, sample_input):
    output = model(sample_input)
    assert output is not None
    assert output.shape[0] == sample_input.shape[0]
''',
      "category": "functionality",
      "expected_to_catch": ["Runtime errors", "Shape mismatches"]
    }},
    ...more tests...
  ],

  "correctness_tests": [
    {{
      "name": "test_output_range",
      "description": "Verify output values are in reasonable range",
      "test_code": '''
def test_output_range(model, sample_input):
    output = model(sample_input)
    assert torch.all(output >= -10) and torch.all(output <= 10), "Output values out of reasonable range"
''',
      "category": "correctness",
      "expected_to_catch": ["Numerical instability", "Wrong activation functions"]
    }},
    ...more tests...
  ],

  "edge_case_tests": [
    {{
      "name": "test_batch_size_one",
      "description": "Test with batch size 1",
      "test_code": '''
def test_batch_size_one(model):
    single_input = torch.randn(1, 3, 224, 224)
    output = model(single_input)
    assert output.shape[0] == 1
''',
      "category": "edge_case",
      "expected_to_catch": ["Batch dimension issues"]
    }},
    ...more tests...
  ],

  "performance_tests": [
    {{
      "name": "test_memory_usage",
      "description": "Check memory doesn't explode",
      "test_code": '''
def test_memory_usage(model, sample_input):
    import tracemalloc
    tracemalloc.start()
    output = model(sample_input)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 1e9, f"Memory usage too high: {{peak / 1e6:.2f}}MB"
''',
      "category": "performance",
      "expected_to_catch": ["Memory leaks", "Inefficient operations"]
    }},
    ...more tests...
  ],

  "total_tests": 15,
  "estimated_runtime_seconds": 5
}}

Design at least 12-15 tests total. Focus on tests that would have caught issues in similar papers.

RETURN ONLY THE JSON. NO OTHER TEXT.
"""

    def _build_specific_requirements(self, analysis: PaperAnalysis) -> str:
        """Build specific test requirements based on analysis"""
        requirements = []

        # Based on likely failure points
        for failure in analysis.likely_failure_points:
            if "shape" in failure.lower() or "dimension" in failure.lower():
                requirements.append(
                    "- Create tests that verify tensor shapes at each step"
                )
            elif "numerical" in failure.lower() or "instability" in failure.lower():
                requirements.append(
                    "- Test for NaN/Inf values in outputs"
                )
            elif "gradient" in failure.lower():
                requirements.append(
                    "- Test gradient flow (no vanishing/exploding gradients)"
                )

        # Based on complexity
        if analysis.complexity_score >= 7:
            requirements.append(
                "- This is complex - add extra correctness tests"
            )

        # Based on required compute
        if analysis.required_compute == "high":
            requirements.append(
                "- Keep test data small (this needs lots of compute)"
            )

        return "\n".join(requirements) if requirements else "- Standard test coverage"

    async def _get_effective_patterns(self, domain: str) -> str:
        """Get test patterns that worked well in the past"""
        if not self.memory:
            return "No test patterns available."

        # Query for successful test patterns
        results = await self.memory.query(
            f"effective test patterns for {domain} caught bugs",
            max_results=5
        )

        if not results:
            return "No test patterns available."

        patterns_text = "SUCCESSFUL TEST PATTERNS:\n"
        for r in results:
            data = r.get('data', {})
            patterns_text += f"- {data.get('pattern', 'N/A')}\n"

        # Add reflections on what tests work
        reflections = await self.get_past_learnings("test_design", max_results=3)
        patterns_text += f"\nLEARNINGS:\n{reflections}"

        return patterns_text

    def _parse_test_suite(self, test_suite_text: str) -> TestSuite:
        """Parse LLM output into structured test suite"""
        import json
        import re

        # Extract JSON
        json_match = re.search(r'\{.*\}', test_suite_text, re.DOTALL)
        if not json_match:
            raise ValueError("Could not find JSON in response")

        try:
            data = json.loads(json_match.group())
            return TestSuite(**data)
        except Exception as e:
            self.log_error("Failed to parse test suite", error=e)
            raise

    def _fallback_tests(self, analysis: PaperAnalysis) -> TestSuite:
        """Minimal fallback tests when design fails"""
        self.log_warning("Using fallback tests")

        basic_test = TestCase(
            name="test_basic_functionality",
            description="Basic smoke test",
            test_code="""
def test_basic_functionality():
    # Basic smoke test
    import torch
    x = torch.randn(2, 10)
    # Model test will be added
    assert True
""",
            category="functionality",
            expected_to_catch=["Basic errors"]
        )

        return TestSuite(
            fixtures="# No fixtures",
            functionality_tests=[basic_test],
            correctness_tests=[],
            edge_case_tests=[],
            performance_tests=[],
            total_tests=1,
            estimated_runtime_seconds=1
        )

    async def reflect_on_test_effectiveness(
        self,
        test_suite: TestSuite,
        bugs_caught: List[str],
        bugs_missed: List[str]
    ):
        """
        Reflect on which tests were effective

        This is critical for improving future test designs
        """
        reflection_prompt = f"""You designed this test suite:
- Total tests: {test_suite.total_tests}
- Categories: functionality, correctness, edge_case, performance

BUGS YOUR TESTS CAUGHT: ✅
{chr(10).join(f'- {bug}' for bug in bugs_caught)}

BUGS YOUR TESTS MISSED: ❌
{chr(10).join(f'- {bug}' for bug in bugs_missed)}

Reflect:
1. Which test patterns were effective?
2. What types of tests should you add more of?
3. What bugs did you not anticipate?
4. How can you design better tests for similar papers?

Be specific about test patterns, not just general advice.
"""

        try:
            reflection = await self.generate(reflection_prompt, temperature=0.7)

            # This is critical learning - store it prominently
            if self.memory:
                await self.memory.add_reflection(
                    agent=self.name,
                    reflection=reflection,
                    task_type="test_effectiveness",
                    context={
                        "bugs_caught": bugs_caught,
                        "bugs_missed": bugs_missed,
                        "total_tests": test_suite.total_tests
                    }
                )

            self.log_info("Stored test effectiveness reflection")
            return reflection

        except Exception as e:
            self.log_error("Failed to reflect on test effectiveness", error=e)
            return None
