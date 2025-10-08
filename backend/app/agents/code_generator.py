"""
Code Generator Agent

Responsibilities:
- Generate clean, working code from paper analysis
- Write code to pass designed tests (TDD approach)
- Learn from successful implementations
- Follow proven patterns

Based on AgentCoder (2024) test-driven generation
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.agents.paper_analyzer import PaperAnalysis
from app.agents.test_designer import TestSuite
from app.agents.memory import TemporalMemory
from app.agents.config import AgentConfig


class GeneratedCode(BaseModel):
    """Generated code artifacts"""
    main_code: str
    config_code: str
    utils_code: str
    example_code: str
    dependencies: list[str]
    framework: str  # "pytorch", "tensorflow", "jax"


class CodeGeneratorAgent(BaseAgent):
    """
    Agent 3: Code Generator

    Generates code using TDD approach - write code to pass tests
    """

    def __init__(
        self,
        config: AgentConfig,
        memory: Optional[TemporalMemory] = None
    ):
        super().__init__(
            name="CodeGenerator",
            role="Expert ML engineer",
            config=config,
            memory=memory
        )

    def _get_system_prompt(self) -> str:
        return """You are an expert ML engineer who writes clean, production-quality code.

Your approach:
- Write code that passes the provided tests
- Follow best practices (type hints, docstrings, clean structure)
- Use hyperparameters from the paper
- Make it educational - others will learn from your code

Code quality matters. This will be used by researchers."""

    async def execute(
        self,
        analysis: PaperAnalysis,
        test_suite: TestSuite,
        paper_title: str,
        attempt: int = 1
    ) -> GeneratedCode:
        """
        Generate code from paper analysis and test suite

        Args:
            analysis: Paper analysis
            test_suite: Test suite to satisfy
            paper_title: For context
            attempt: Which attempt (1, 2, 3...)

        Returns:
            Generated code artifacts
        """
        self.log_info(f"Generating code (attempt {attempt}): {paper_title[:50]}...")

        # Get successful patterns
        patterns = await self._get_successful_patterns(analysis.components[0] if analysis.components else "model")

        # Build generation prompt
        prompt = self._build_generation_prompt(
            analysis,
            test_suite,
            paper_title,
            patterns,
            attempt
        )

        try:
            # Generate code
            code_text = await self.generate(
                prompt,
                temperature=0.5,  # Balance creativity and precision
                max_tokens=6000  # Longer for code
            )

            # Parse into structured format
            generated = self._parse_generated_code(code_text)

            self.log_info(f"Generated {len(generated.main_code)} chars of code")
            return generated

        except Exception as e:
            self.log_error("Code generation failed", error=e)
            raise

    def _build_generation_prompt(
        self,
        analysis: PaperAnalysis,
        test_suite: TestSuite,
        paper_title: str,
        patterns: str,
        attempt: int
    ) -> str:
        """Build code generation prompt"""

        return f"""Generate a complete PyTorch implementation of this paper.

PAPER: {paper_title}

ANALYSIS:
Core Algorithm: {analysis.core_algorithm}
Steps: {', '.join(analysis.step_by_step_procedure[:3])}...
Components: {', '.join(analysis.components)}
Hyperparameters: {analysis.hyperparameters}
Dependencies: {', '.join(analysis.dependencies)}

YOUR CODE MUST PASS THESE TESTS:
{self._format_tests_summary(test_suite)}

SUCCESSFUL PATTERNS TO FOLLOW:
{patterns}

ATTEMPT #{attempt}
{self._get_attempt_guidance(attempt)}

---

Generate complete, working code in this structure:

1. CONFIG (config.py):
```python
# Hyperparameters from paper with citations
class Config:
    # From paper Section X.Y
    learning_rate = {analysis.hyperparameters.get('learning_rate', '3e-4')}
    # ... other hyperparameters
```

2. MAIN MODEL (model.py):
```python
import torch
import torch.nn as nn

class {self._get_model_name(paper_title)}(nn.Module):
    \"\"\"
    Implementation of: {paper_title}

    Key innovation: {analysis.core_algorithm[:100]}...

    Args:
        ...
    \"\"\"
    def __init__(self, ...):
        super().__init__()
        # Implementation following paper architecture
        ...

    def forward(self, x):
        # Follows paper's algorithm
        ...
        return output
```

3. UTILS (utils.py):
```python
# Helper functions if needed
def preprocess(...):
    pass
```

4. EXAMPLE (example.py):
```python
# Quick start example
if __name__ == "__main__":
    model = {self._get_model_name(paper_title)}()
    sample = torch.randn(2, ...)
    output = model(sample)
    print(f"Output shape: {{output.shape}}")
```

REQUIREMENTS:
- Use PyTorch
- Include ALL hyperparameters from paper analysis
- Add inline comments citing paper sections
- Make it pass the tests
- Keep it under 300 lines total
- Add docstrings
- Use type hints

CRITICAL: Your code must make these tests pass:
{self._highlight_critical_tests(test_suite)}

Return ONLY this JSON:
{{
  "main_code": "complete model.py content",
  "config_code": "complete config.py content",
  "utils_code": "complete utils.py content (or empty string)",
  "example_code": "complete example.py content",
  "dependencies": ["torch==2.1.0", "numpy==1.24.3"],
  "framework": "pytorch"
}}

RETURN ONLY JSON. NO OTHER TEXT.
"""

    def _format_tests_summary(self, test_suite: TestSuite) -> str:
        """Format tests for prompt"""
        summary = f"Total {test_suite.total_tests} tests:\n"

        for test in test_suite.functionality_tests[:2]:
            summary += f"- {test.name}: {test.description}\n"

        for test in test_suite.correctness_tests[:2]:
            summary += f"- {test.name}: {test.description}\n"

        summary += f"... and {test_suite.total_tests - 4} more tests"
        return summary

    def _highlight_critical_tests(self, test_suite: TestSuite) -> str:
        """Highlight most critical tests"""
        critical = []

        if test_suite.functionality_tests:
            critical.append(f"✓ {test_suite.functionality_tests[0].name}")
        if test_suite.correctness_tests:
            critical.append(f"✓ {test_suite.correctness_tests[0].name}")

        return "\n".join(critical)

    def _get_model_name(self, paper_title: str) -> str:
        """Extract a reasonable model name from title"""
        # Simple heuristic - take first meaningful word
        words = paper_title.split()
        for word in words:
            if len(word) > 3 and word[0].isupper():
                return word + "Model"
        return "PaperModel"

    def _get_attempt_guidance(self, attempt: int) -> str:
        """Provide guidance based on attempt number"""
        if attempt == 1:
            return "First attempt - be thorough and follow the paper closely."
        elif attempt == 2:
            return "Second attempt - the first version had issues. Simplify if needed."
        else:
            return "Final attempt - focus on making tests pass, even if simplified."

    async def _get_successful_patterns(self, component_type: str) -> str:
        """Get code patterns that worked in the past"""
        if not self.memory:
            return "No patterns available."

        results = await self.memory.query(
            f"successful code patterns for {component_type}",
            max_results=3
        )

        if not results:
            return "Standard ML patterns."

        patterns_text = "PATTERNS THAT WORKED:\n"
        for r in results:
            patterns_text += f"- {r.get('data', {}).get('pattern', 'N/A')}\n"

        return patterns_text

    def _parse_generated_code(self, code_text: str) -> GeneratedCode:
        """Parse LLM output into structured code"""
        import json
        import re

        json_match = re.search(r'\{.*\}', code_text, re.DOTALL)
        if not json_match:
            raise ValueError("Could not find JSON in response")

        try:
            data = json.loads(json_match.group())
            return GeneratedCode(**data)
        except Exception as e:
            self.log_error("Failed to parse generated code", error=e)
            raise
