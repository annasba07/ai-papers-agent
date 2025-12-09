"""
Configuration for multi-agent system

Supports multiple LLM providers via environment variables:
- CODE_GEN_PROVIDER: "anthropic" | "openai" | "gemini" (default: "gemini")
- CODE_GEN_MODEL: Override default model for the provider
- ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY: Provider API keys
"""
import os
from pydantic import BaseModel, Field
from typing import Optional

# Default models for each provider
DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "gemini": "gemini-2.5-flash-lite",
}


def get_default_provider() -> str:
    """Get provider from env or auto-detect based on available API keys"""
    configured = os.getenv("CODE_GEN_PROVIDER")
    if configured:
        return configured.lower()

    # Auto-detect: prefer gemini > openai > anthropic
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"

    return "gemini"  # Default, will fail gracefully if no key


def get_default_model(provider: str) -> str:
    """Get default model for a provider"""
    return os.getenv("CODE_GEN_MODEL") or DEFAULT_MODELS.get(provider, "gemini-2.5-flash-lite")


class AgentConfig(BaseModel):
    """Configuration for individual agents"""

    # LLM Configuration - now environment-aware
    llm_provider: str = Field(default_factory=get_default_provider)
    llm_model: str = Field(default_factory=lambda: get_default_model(get_default_provider()))
    temperature: float = 0.7
    max_tokens: int = 4000

    # Retry Configuration
    max_retries: int = 3
    retry_delay: float = 2.0

    # Timeout Configuration
    timeout_seconds: int = 60

    def model_post_init(self, __context) -> None:
        """Ensure model matches provider after initialization"""
        if self.llm_model == get_default_model("gemini"):  # Was set to default
            self.llm_model = get_default_model(self.llm_provider)


class MemoryConfig(BaseModel):
    """Configuration for temporal knowledge graph memory"""

    # Neo4j Configuration
    neo4j_uri: Optional[str] = "bolt://localhost:7687"
    neo4j_user: Optional[str] = "neo4j"
    neo4j_password: Optional[str] = None

    # Memory Settings
    enable_memory: bool = False  # Start with in-memory fallback
    memory_ttl_days: int = 90  # Temporal decay
    max_context_items: int = 10  # Max items to retrieve from memory


class SandboxConfig(BaseModel):
    """Configuration for code execution sandbox"""

    # Sandbox Settings
    sandbox_type: str = "docker"  # or "e2b"
    timeout_seconds: int = 30
    memory_limit_gb: int = 2
    cpu_limit: float = 1.0

    # Python Environment
    python_version: str = "3.11"
    base_packages: list[str] = Field(default_factory=lambda: [
        "torch==2.1.0",
        "numpy==1.24.3",
        "pytest==8.3.4"
    ])


class OrchestratorConfig(BaseModel):
    """Configuration for orchestrator"""

    # Agent Configuration
    agent_config: AgentConfig = Field(default_factory=AgentConfig)
    memory_config: MemoryConfig = Field(default_factory=MemoryConfig)
    sandbox_config: SandboxConfig = Field(default_factory=SandboxConfig)

    # Pipeline Configuration
    max_debug_iterations: int = 3
    enable_reflection: bool = True
    enable_meta_optimization: bool = False  # Future feature

    # Monitoring
    enable_monitoring: bool = False
    langsmith_api_key: Optional[str] = None


# Global config instance
orchestrator_config = OrchestratorConfig()
