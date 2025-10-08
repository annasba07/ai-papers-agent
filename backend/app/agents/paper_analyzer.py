"""
Paper Analyzer Agent

Responsibilities:
- Deep analysis of research papers
- Extract implementation requirements
- Predict implementation difficulty
- Learn from past analyses (Reflexion pattern)

Based on research findings from multi-agent surveys (2024-2025)
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.agents.memory import TemporalMemory
from app.agents.config import AgentConfig


class PaperAnalysis(BaseModel):
    """Structured output from paper analysis"""

    # Core Algorithm
    core_algorithm: str
    step_by_step_procedure: list[str]
    key_equations: list[str]

    # Architecture
    components: list[str]
    component_connections: str
    architecture_diagram_description: str

    # Hyperparameters
    hyperparameters: Dict[str, Any]
    critical_hyperparameters: list[str]

    # Implementation Details
    dependencies: list[str]
    mathematical_operations: list[str]
    gotchas: list[str]

    # Difficulty Assessment
    complexity_score: int  # 1-10
    estimated_implementation_time_hours: int
    required_compute: str  # "low", "medium", "high"

    # Predictions
    likely_failure_points: list[str]
    common_bugs_to_avoid: list[str]


class PaperAnalyzerAgent(BaseAgent):
    """
    Agent 1: Deep Paper Analysis

    Uses reflection and memory to improve analysis quality over time
    """

    def __init__(
        self,
        config: AgentConfig,
        memory: Optional[TemporalMemory] = None
    ):
        super().__init__(
            name="PaperAnalyzer",
            role="Research paper analysis expert",
            config=config,
            memory=memory
        )

    def _get_system_prompt(self) -> str:
        return """You are an expert at analyzing research papers for implementation.

Your role:
- Deep-read papers and extract ALL implementation details
- Identify what's explicitly stated vs what's implied
- Predict common implementation pitfalls
- Assess complexity accurately

You must be thorough and precise. Other agents depend on your analysis."""

    async def execute(
        self,
        paper_title: str,
        paper_abstract: str,
        paper_summary: Dict[str, Any],
        paper_category: str
    ) -> PaperAnalysis:
        """
        Analyze a paper for implementation

        Args:
            paper_title: Title of the paper
            paper_abstract: Abstract text
            paper_summary: AI-generated summary from existing system
            paper_category: arXiv category (e.g., "cs.CV")

        Returns:
            Structured analysis
        """
        self.log_info(f"Analyzing paper: {paper_title[:50]}...")

        # Get learnings from similar papers
        past_learnings = await self._get_domain_learnings(paper_category)

        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            paper_title,
            paper_abstract,
            paper_summary,
            past_learnings
        )

        try:
            # Generate analysis
            analysis_text = await self.generate(
                prompt,
                temperature=0.3  # Lower temperature for precision
            )

            # Parse into structured format
            analysis = self._parse_analysis(analysis_text)

            # Reflect on success
            await self.reflect(
                task="paper_analysis",
                result={"summary": f"Analyzed {paper_title}"},
                outcome="success"
            )

            return analysis

        except Exception as e:
            self.log_error("Analysis failed", error=e)

            # Reflect on failure
            await self.reflect(
                task="paper_analysis",
                result={"error": str(e)},
                outcome="failure"
            )

            # Return minimal fallback analysis
            return self._fallback_analysis(paper_title, paper_abstract)

    def _build_analysis_prompt(
        self,
        title: str,
        abstract: str,
        summary: Dict[str, Any],
        past_learnings: str
    ) -> str:
        """Build comprehensive analysis prompt"""

        return f"""Analyze this research paper for implementation:

PAPER TITLE:
{title}

ABSTRACT:
{abstract}

EXISTING AI ANALYSIS:
Key Contribution: {summary.get('keyContribution', 'N/A')}
Methodology: {summary.get('methodologyBreakdown', 'N/A')}
Technical Innovation: {summary.get('technicalInnovation', 'N/A')}
Implementation Insights: {summary.get('implementationInsights', 'N/A')}

LEARNINGS FROM SIMILAR PAPERS:
{past_learnings}

---

Provide a comprehensive implementation analysis in this EXACT JSON format:

{{
  "core_algorithm": "What is the main algorithmic innovation? Describe in detail.",

  "step_by_step_procedure": [
    "Step 1: ...",
    "Step 2: ...",
    "..."
  ],

  "key_equations": [
    "Equation 1: description (if mentioned)",
    "..."
  ],

  "components": [
    "Component 1: description",
    "Component 2: description",
    "..."
  ],

  "component_connections": "How do components connect? Describe data flow.",

  "architecture_diagram_description": "Describe the architecture as if drawing a diagram",

  "hyperparameters": {{
    "learning_rate": "value or typical range",
    "batch_size": "value or typical range",
    "...": "other hyperparameters from paper"
  }},

  "critical_hyperparameters": [
    "Which hyperparameters are most important?",
    "Which ones significantly affect results?"
  ],

  "dependencies": [
    "PyTorch/TensorFlow/JAX",
    "numpy",
    "other required libraries"
  ],

  "mathematical_operations": [
    "Matrix multiplication",
    "Convolution",
    "Attention mechanism",
    "..."
  ],

  "gotchas": [
    "Implementation detail 1 that's crucial but not obvious",
    "Common mistake people make",
    "..."
  ],

  "complexity_score": 7,  // 1-10, where 10 is extremely complex

  "estimated_implementation_time_hours": 20,  // Realistic estimate for an experienced engineer

  "required_compute": "medium",  // "low", "medium", or "high"

  "likely_failure_points": [
    "Tensor shape mismatch in component X",
    "Numerical instability in operation Y",
    "..."
  ],

  "common_bugs_to_avoid": [
    "Forgetting to normalize inputs",
    "Wrong dimension order",
    "..."
  ]
}}

Based on similar papers you've analyzed, anticipate issues and be specific about implementation details.

RETURN ONLY THE JSON. NO OTHER TEXT.
"""

    async def _get_domain_learnings(self, paper_category: str) -> str:
        """Get learnings from similar papers in this domain"""
        if not self.memory:
            return "No past learnings available."

        # Query memory for similar papers
        results = await self.memory.query(
            f"successful implementations in {paper_category}",
            max_results=5
        )

        if not results:
            return "No past learnings available."

        # Get reflections
        reflections = await self.get_past_learnings("paper_analysis", max_results=3)

        learnings_text = f"PAST SUCCESSES:\n"
        for r in results:
            data = r.get('data', {})
            learnings_text += f"- Paper in {paper_category}: {data.get('notes', 'N/A')}\n"

        learnings_text += f"\nPAST REFLECTIONS:\n{reflections}"

        return learnings_text

    def _parse_analysis(self, analysis_text: str) -> PaperAnalysis:
        """Parse LLM output into structured analysis"""
        import json
        import re

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
        if not json_match:
            raise ValueError("Could not find JSON in response")

        try:
            data = json.loads(json_match.group())
            return PaperAnalysis(**data)
        except Exception as e:
            self.log_error("Failed to parse analysis", error=e)
            raise

    def _fallback_analysis(
        self,
        title: str,
        abstract: str
    ) -> PaperAnalysis:
        """Minimal fallback analysis when main analysis fails"""
        self.log_warning("Using fallback analysis")

        return PaperAnalysis(
            core_algorithm="Algorithm details unclear - manual review needed",
            step_by_step_procedure=["Step 1: Review paper manually"],
            key_equations=[],
            components=["Main model component"],
            component_connections="Unknown - needs analysis",
            architecture_diagram_description="Standard neural network architecture",
            hyperparameters={"learning_rate": "1e-3", "batch_size": "32"},
            critical_hyperparameters=["learning_rate"],
            dependencies=["torch", "numpy"],
            mathematical_operations=["Standard ML operations"],
            gotchas=["Review paper carefully for implementation details"],
            complexity_score=7,
            estimated_implementation_time_hours=40,
            required_compute="medium",
            likely_failure_points=["Unclear architecture may cause issues"],
            common_bugs_to_avoid=["Verify all implementation details"]
        )

    async def reflect_on_code_failure(
        self,
        paper_title: str,
        analysis: PaperAnalysis,
        failure_reason: str
    ):
        """
        Special reflection when generated code fails

        This helps improve future analyses
        """
        reflection_prompt = f"""You previously analyzed this paper:
{paper_title}

Your analysis:
- Complexity score: {analysis.complexity_score}
- Estimated time: {analysis.estimated_implementation_time_hours}h
- Predicted failures: {analysis.likely_failure_points}

The generated code FAILED with:
{failure_reason}

Deeply reflect:
1. What did you miss in your analysis?
2. What implementation detail was unclear?
3. Was your complexity estimate accurate?
4. What should you look for more carefully next time?
5. How would you analyze this paper differently now?

Be brutally honest and specific.
"""

        try:
            reflection = await self.generate(
                reflection_prompt,
                temperature=0.7
            )

            # Store this critical learning
            if self.memory:
                await self.memory.add_reflection(
                    agent=self.name,
                    reflection=reflection,
                    task_type="paper_analysis_post_failure",
                    context={
                        "paper_title": paper_title,
                        "failure_reason": failure_reason,
                        "complexity_score": analysis.complexity_score
                    }
                )

            self.log_info("Stored critical reflection on code failure")
            return reflection

        except Exception as e:
            self.log_error("Failed to reflect on code failure", error=e)
            return None
