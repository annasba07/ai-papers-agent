"""
Multi-Agent Code Generation System

Research-informed architecture based on:
- AgentCoder (2024): Test-driven multi-agent code generation
- Reflexion (2023): Verbal reinforcement learning
- SAGE (2024): Self-evolving agents with memory
- Graphiti (2024): Temporal knowledge graphs
"""

from .orchestrator import CodeGenerationOrchestrator, get_orchestrator, QuickStartResult
from .paper_analyzer import PaperAnalyzerAgent, PaperAnalysis
from .test_designer import TestDesignerAgent, TestSuite
from .code_generator import CodeGeneratorAgent, GeneratedCode
from .test_executor import TestExecutorAgent, ExecutionResult
from .debugger import DebuggerAgent, DebugResult
from .memory import TemporalMemory
from .config import AgentConfig, MemoryConfig, orchestrator_config

__all__ = [
    "CodeGenerationOrchestrator",
    "get_orchestrator",
    "QuickStartResult",
    "PaperAnalyzerAgent",
    "PaperAnalysis",
    "TestDesignerAgent",
    "TestSuite",
    "CodeGeneratorAgent",
    "GeneratedCode",
    "TestExecutorAgent",
    "ExecutionResult",
    "DebuggerAgent",
    "DebugResult",
    "TemporalMemory",
    "AgentConfig",
    "MemoryConfig",
    "orchestrator_config",
]
