"""
Configuration for multi-agent system
"""
from pydantic import BaseModel, Field
from typing import Optional


class AgentConfig(BaseModel):
    """Configuration for individual agents"""

    # LLM Configuration
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.7
    max_tokens: int = 4000

    # Retry Configuration
    max_retries: int = 3
    retry_delay: float = 2.0

    # Timeout Configuration
    timeout_seconds: int = 60


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
