"""
SQLAlchemy models for Agent Memory Persistence

Provides persistent storage for:
- Temporal knowledge graph nodes
- Agent reflections for learning
- Performance metrics for meta-optimization

Based on SAGE (2024) memory-augmented learning patterns
"""
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    from sqlalchemy import Text as Vector

from app.db.database import Base


class AgentMemoryNode(Base):
    """
    Temporal knowledge graph node for cross-paper learning

    Stores learned patterns, successful strategies, and domain knowledge
    that agents accumulate across paper implementations.
    """
    __tablename__ = "agent_memory_nodes"

    id = Column(String(64), primary_key=True, comment="MD5 hash of node content")

    # Node type classification
    node_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="successful_generation, pattern, strategy, etc."
    )

    # Content storage
    content = Column(JSONB, nullable=False, comment="Full node data")

    # Categorization
    paper_category = Column(String(50), nullable=True, index=True)
    technique_domain = Column(String(100), nullable=True, index=True)

    # Temporal tracking (bi-temporal model from Graphiti)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)

    # Access patterns for relevance scoring
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Relevance scoring
    importance_score = Column(Float, default=1.0)
    decay_rate = Column(Float, default=0.1, comment="Ebbinghaus decay rate S")

    # Optional embedding for semantic search
    embedding = Column(Vector(1536), nullable=True)

    # Searchable text for keyword matching
    searchable_text = Column(Text, nullable=True)

    __table_args__ = (
        Index('agent_memory_nodes_type_category_idx', 'node_type', 'paper_category'),
        Index('agent_memory_nodes_created_idx', 'created_at'),
        Index('agent_memory_nodes_access_idx', 'last_accessed', 'access_count'),
    )


class AgentReflection(Base):
    """
    Agent reflection storage for Reflexion-style learning

    Captures what agents learned from each task to improve
    future performance on similar problems.
    """
    __tablename__ = "agent_reflections"

    id = Column(Integer, primary_key=True)

    # Which agent created this reflection
    agent_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="paper_analyzer, test_designer, code_generator, debugger"
    )

    # What type of task this relates to
    task_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="analysis, test_design, code_generation, debugging"
    )

    # The actual reflection content
    reflection = Column(Text, nullable=False)

    # Context in which reflection was made
    context = Column(JSONB, nullable=True)

    # Paper metadata for filtering
    paper_category = Column(String(50), nullable=True, index=True)
    paper_id = Column(String(50), nullable=True, index=True)
    complexity_level = Column(Integer, nullable=True)

    # Outcome tracking
    was_successful = Column(Boolean, default=True)
    improvement_noted = Column(Text, nullable=True)

    # Temporal tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relevance for future retrieval
    usefulness_score = Column(Float, default=1.0)
    times_retrieved = Column(Integer, default=0)

    __table_args__ = (
        Index('agent_reflections_agent_task_idx', 'agent_name', 'task_type'),
        Index('agent_reflections_category_idx', 'paper_category', 'task_type'),
        Index('agent_reflections_success_idx', 'was_successful', 'created_at'),
    )


class AgentPerformanceMetric(Base):
    """
    Performance tracking for meta-learning and optimization

    Records outcomes of code generation attempts to identify
    patterns in what works well for different paper types.
    """
    __tablename__ = "agent_performance_metrics"

    id = Column(Integer, primary_key=True)

    # Paper identification
    paper_id = Column(String(50), nullable=True, index=True)
    paper_category = Column(String(50), nullable=False, index=True)

    # Complexity assessment
    complexity_score = Column(Integer, nullable=True)
    estimated_difficulty = Column(String(20), nullable=True)

    # Outcome
    success = Column(Boolean, nullable=False, index=True)
    partial_success = Column(Boolean, default=False)

    # Metrics
    tests_passed = Column(Integer, default=0)
    tests_total = Column(Integer, default=0)
    pass_rate = Column(Float, nullable=True)

    # Effort tracking
    debug_iterations = Column(Integer, default=0)
    total_llm_calls = Column(Integer, default=0)
    execution_time_seconds = Column(Float, nullable=True)

    # Error analysis
    error_type = Column(String(100), nullable=True, index=True)
    error_message = Column(Text, nullable=True)
    failure_stage = Column(
        String(50),
        nullable=True,
        comment="analysis, test_design, generation, execution, debugging"
    )

    # Agent configuration used
    agent_config = Column(JSONB, nullable=True)
    model_used = Column(String(50), nullable=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('agent_performance_category_success_idx', 'paper_category', 'success'),
        Index('agent_performance_error_idx', 'error_type', 'failure_stage'),
        Index('agent_performance_time_idx', 'created_at', 'success'),
    )


class AgentLearningPattern(Base):
    """
    Extracted patterns from successful generations

    Higher-level abstractions learned from multiple papers
    that can guide future implementations.
    """
    __tablename__ = "agent_learning_patterns"

    id = Column(Integer, primary_key=True)

    # Pattern identification
    pattern_name = Column(String(200), nullable=False)
    pattern_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="code_structure, test_strategy, debug_technique, architecture"
    )

    # Pattern content
    description = Column(Text, nullable=False)
    template = Column(Text, nullable=True)
    examples = Column(JSONB, nullable=True)

    # Applicability
    applicable_domains = Column(JSONB, nullable=True)
    applicable_complexity = Column(JSONB, nullable=True)
    prerequisites = Column(JSONB, nullable=True)

    # Effectiveness tracking
    times_applied = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    last_applied = Column(DateTime, nullable=True)

    # Metadata
    discovered_from_papers = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Active/deprecated status
    is_active = Column(Boolean, default=True, index=True)

    __table_args__ = (
        Index('agent_learning_patterns_type_active_idx', 'pattern_type', 'is_active'),
        Index('agent_learning_patterns_success_idx', 'success_rate', 'times_applied'),
    )


class AgentSession(Base):
    """
    Tracks individual code generation sessions

    Provides session-level context for correlating
    reflections, metrics, and nodes.
    """
    __tablename__ = "agent_sessions"

    id = Column(String(36), primary_key=True, comment="UUID")

    # Paper info
    paper_id = Column(String(50), nullable=False, index=True)
    paper_title = Column(Text, nullable=True)
    paper_category = Column(String(50), nullable=True, index=True)

    # Session timing
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Overall outcome
    status = Column(
        String(20),
        default="in_progress",
        index=True,
        comment="in_progress, success, partial_success, failed"
    )

    # Summary metrics
    stages_completed = Column(Integer, default=0)
    total_reflections = Column(Integer, default=0)
    final_test_pass_rate = Column(Float, nullable=True)

    # Configuration snapshot
    config_snapshot = Column(JSONB, nullable=True)

    # System reflection
    system_reflection = Column(Text, nullable=True)
    lessons_learned = Column(JSONB, nullable=True)

    __table_args__ = (
        Index('agent_sessions_status_time_idx', 'status', 'started_at'),
        Index('agent_sessions_paper_idx', 'paper_id', 'started_at'),
    )
