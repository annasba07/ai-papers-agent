"""
Agent Memory API Endpoints

Provides access to agent learning data, performance metrics,
and pattern retrieval for monitoring and debugging.
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.agents.config import orchestrator_config
from app.agents.memory import TemporalMemory


router = APIRouter(prefix="/agent-memory")


# Response Models
class PerformanceStats(BaseModel):
    total_attempts: int = 0
    success_rate: float = 0.0
    avg_iterations: float = 0.0
    avg_pass_rate: Optional[float] = None
    avg_execution_time: Optional[float] = None
    common_failures: List[str] = []
    no_data: bool = False


class ReflectionResponse(BaseModel):
    id: Optional[int] = None
    reflection: str
    task_type: str
    context: Optional[dict] = None
    paper_category: Optional[str] = None
    was_successful: bool = True
    timestamp: Optional[str] = None
    relevance_score: Optional[float] = None


class PatternResponse(BaseModel):
    id: int
    name: str
    type: str
    description: str
    template: Optional[str] = None
    examples: Optional[List[dict]] = None
    success_rate: Optional[float] = None
    times_applied: int = 0


class MemoryNodeResponse(BaseModel):
    node_id: str
    data: dict
    relevance: float


class MemorySummaryResponse(BaseModel):
    storage_type: str
    total_nodes: int
    total_reflections: int
    total_performance_records: int
    performance_by_category: dict


# Memory singleton
_memory: Optional[TemporalMemory] = None


def get_memory() -> TemporalMemory:
    """Get or create memory instance"""
    global _memory
    if _memory is None:
        _memory = TemporalMemory(orchestrator_config.memory_config)
    return _memory


@router.get("/stats", response_model=PerformanceStats)
async def get_performance_stats(
    paper_category: Optional[str] = Query(
        None,
        description="Filter by paper category (e.g., cs.AI, cs.LG)"
    ),
    days: int = Query(30, ge=1, le=365, description="Time window in days")
):
    """
    Get agent performance statistics

    Returns success rates, common failure patterns, and other metrics
    for code generation attempts.
    """
    memory = get_memory()
    stats = await memory.get_performance_stats(paper_category, days)

    if stats.get("error"):
        raise HTTPException(status_code=500, detail=stats["error"])

    return PerformanceStats(
        total_attempts=stats.get("total_attempts", 0),
        success_rate=stats.get("success_rate", 0.0),
        avg_iterations=stats.get("avg_iterations", 0.0),
        avg_pass_rate=stats.get("avg_pass_rate"),
        avg_execution_time=stats.get("avg_execution_time"),
        common_failures=stats.get("common_failures", []),
        no_data=stats.get("no_data", False)
    )


@router.get("/reflections/{agent_name}", response_model=List[ReflectionResponse])
async def get_agent_reflections(
    agent_name: str,
    task_type: Optional[str] = Query(
        None,
        description="Filter by task type (analysis, test_design, code_generation, debugging)"
    ),
    paper_category: Optional[str] = Query(
        None,
        description="Filter by paper category"
    ),
    max_age_days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get reflections for a specific agent

    Reflections capture what agents learned from each task,
    enabling continuous improvement.
    """
    valid_agents = ["paper_analyzer", "test_designer", "code_generator", "debugger", "orchestrator"]
    if agent_name not in valid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent name. Valid agents: {valid_agents}"
        )

    memory = get_memory()
    reflections = await memory.get_reflections(
        agent_name,
        task_type=task_type,
        max_age_days=max_age_days,
        max_results=limit,
        paper_category=paper_category
    )

    return [
        ReflectionResponse(
            id=r.get("id"),
            reflection=r.get("reflection", ""),
            task_type=r.get("task_type", "unknown"),
            context=r.get("context"),
            paper_category=r.get("paper_category"),
            was_successful=r.get("was_successful", True),
            timestamp=str(r.get("timestamp", "")) if r.get("timestamp") else None,
            relevance_score=r.get("relevance_score")
        )
        for r in reflections
    ]


@router.get("/patterns", response_model=List[PatternResponse])
async def get_learning_patterns(
    pattern_type: Optional[str] = Query(
        None,
        description="Filter by pattern type (code_structure, test_strategy, debug_technique, architecture)"
    ),
    domain: Optional[str] = Query(
        None,
        description="Filter by applicable domain"
    ),
    min_success_rate: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    Get learned patterns

    Patterns are higher-level abstractions learned from successful
    code generation that can guide future implementations.
    """
    memory = get_memory()
    patterns = await memory.get_applicable_patterns(pattern_type, domain)

    # Filter by success rate
    filtered = [
        p for p in patterns
        if p.get("success_rate") is None or p.get("success_rate", 0) >= min_success_rate
    ]

    return [
        PatternResponse(
            id=p.get("id", 0),
            name=p.get("name", ""),
            type=p.get("type", ""),
            description=p.get("description", ""),
            template=p.get("template"),
            examples=p.get("examples"),
            success_rate=p.get("success_rate"),
            times_applied=p.get("times_applied", 0)
        )
        for p in filtered
    ]


@router.get("/query", response_model=List[MemoryNodeResponse])
async def query_memory(
    q: str = Query(..., min_length=1, description="Search query"),
    node_type: Optional[str] = Query(
        None,
        description="Filter by node type (successful_generation, pattern, strategy)"
    ),
    paper_category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Query the agent memory knowledge graph

    Search for relevant nodes based on keywords and filters.
    Results are scored by relevance and temporal decay.
    """
    memory = get_memory()
    results = await memory.query(
        q,
        max_results=limit,
        node_type=node_type,
        paper_category=paper_category
    )

    return [
        MemoryNodeResponse(
            node_id=r.get("node_id", ""),
            data=r.get("data", {}),
            relevance=r.get("relevance", 0.0)
        )
        for r in results
    ]


@router.get("/summary", response_model=MemorySummaryResponse)
async def get_memory_summary():
    """
    Get a summary of the agent memory state

    Returns counts and storage information for monitoring.
    """
    memory = get_memory()

    # Determine storage type
    storage_type = "postgresql" if memory._use_persistent else "in_memory"

    # For in-memory, we can count directly
    if not memory._use_persistent:
        total_nodes = len(memory.store.nodes)
        total_reflections = sum(
            len(refs) for refs in memory.store.reflections.values()
        )
        total_performance = len(memory.store.performance_data)

        # Count by category
        category_counts = {}
        for perf in memory.store.performance_data:
            cat = perf.get("paper_category", "unknown")
            if cat not in category_counts:
                category_counts[cat] = {"total": 0, "success": 0}
            category_counts[cat]["total"] += 1
            if perf.get("success"):
                category_counts[cat]["success"] += 1

        return MemorySummaryResponse(
            storage_type=storage_type,
            total_nodes=total_nodes,
            total_reflections=total_reflections,
            total_performance_records=total_performance,
            performance_by_category=category_counts
        )

    # For persistent storage, we need to query the database
    try:
        from app.db.database import database
        from sqlalchemy import select, func
        from app.db.agent_memory_models import (
            AgentMemoryNode,
            AgentReflection,
            AgentPerformanceMetric
        )

        # Count nodes
        node_count = await database.fetch_val(
            select(func.count(AgentMemoryNode.id))
        )

        # Count reflections
        reflection_count = await database.fetch_val(
            select(func.count(AgentReflection.id))
        )

        # Count performance records
        perf_count = await database.fetch_val(
            select(func.count(AgentPerformanceMetric.id))
        )

        # Performance by category
        category_query = select(
            AgentPerformanceMetric.paper_category,
            func.count(AgentPerformanceMetric.id).label("total"),
            func.sum(
                func.cast(AgentPerformanceMetric.success, Integer)
            ).label("successes")
        ).group_by(AgentPerformanceMetric.paper_category)

        from sqlalchemy import Integer
        rows = await database.fetch_all(category_query)
        category_counts = {
            row["paper_category"]: {
                "total": row["total"],
                "success": row["successes"] or 0
            }
            for row in rows
        }

        return MemorySummaryResponse(
            storage_type=storage_type,
            total_nodes=node_count or 0,
            total_reflections=reflection_count or 0,
            total_performance_records=perf_count or 0,
            performance_by_category=category_counts
        )

    except Exception as e:
        return MemorySummaryResponse(
            storage_type=storage_type,
            total_nodes=0,
            total_reflections=0,
            total_performance_records=0,
            performance_by_category={"error": str(e)}
        )
