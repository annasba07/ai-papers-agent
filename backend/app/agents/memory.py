"""
Temporal Memory System for Multi-Agent Learning

Based on Graphiti (2024) temporal knowledge graphs
Implements Ebbinghaus forgetting curve (SAGE, 2024)

Supports both:
- In-memory storage (development/fallback)
- PostgreSQL persistent storage (production)
"""
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import json
import hashlib
from app.utils.logger import LoggerMixin


class InMemoryTemporalStore:
    """
    Fallback in-memory temporal storage
    Used when database is not configured
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.reflections: Dict[str, List[Dict[str, Any]]] = {}
        self.performance_data: List[Dict[str, Any]] = []

    def add_node(self, node_data: Dict[str, Any]):
        """Add a node with timestamp"""
        node_id = hashlib.md5(
            json.dumps(node_data, sort_keys=True, default=str).encode()
        ).hexdigest()

        self.nodes[node_id] = {
            **node_data,
            "created_at": datetime.now(),
            "access_count": 0,
            "last_accessed": datetime.now()
        }

        return node_id

    def query(self, query_text: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Simple keyword-based query
        """
        results = []
        keywords = query_text.lower().split()

        for node_id, node in self.nodes.items():
            # Simple relevance scoring
            node_text = json.dumps(node, default=str).lower()
            score = sum(1 for kw in keywords if kw in node_text)

            if score > 0:
                # Update access patterns
                self.nodes[node_id]["access_count"] += 1
                self.nodes[node_id]["last_accessed"] = datetime.now()

                results.append({
                    "node_id": node_id,
                    "data": node,
                    "relevance": score
                })

        # Sort by relevance and recency
        results.sort(
            key=lambda x: (
                x["relevance"],
                x["data"]["last_accessed"]
            ),
            reverse=True
        )

        return results[:max_results]

    def add_reflection(self, agent: str, reflection_data: Dict[str, Any]):
        """Store agent reflection for learning"""
        if agent not in self.reflections:
            self.reflections[agent] = []

        self.reflections[agent].append({
            **reflection_data,
            "timestamp": datetime.now()
        })

    def get_reflections(
        self,
        agent: str,
        task_type: Optional[str] = None,
        max_age_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Retrieve agent reflections with temporal decay"""
        if agent not in self.reflections:
            return []

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        reflections = []

        for reflection in self.reflections[agent]:
            if reflection["timestamp"] > cutoff_date:
                if task_type is None or reflection.get("task_type") == task_type:
                    reflections.append(reflection)

        # Sort by recency
        reflections.sort(key=lambda x: x["timestamp"], reverse=True)

        return reflections

    def record_performance(self, performance_data: Dict[str, Any]):
        """Record performance metrics for meta-learning"""
        self.performance_data.append({
            **performance_data,
            "timestamp": datetime.now()
        })

    async def add_node_async(self, node_data: Dict[str, Any]) -> str:
        """Async wrapper for add_node"""
        return self.add_node(node_data)

    async def query_async(
        self,
        query_text: str,
        max_results: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Async wrapper for query"""
        return self.query(query_text, max_results)

    async def add_reflection_async(
        self,
        agent: str,
        reflection_data: Dict[str, Any]
    ) -> int:
        """Async wrapper for add_reflection"""
        self.add_reflection(agent, reflection_data)
        return len(self.reflections.get(agent, []))

    async def get_reflections_async(
        self,
        agent: str,
        task_type: Optional[str] = None,
        max_age_days: int = 30,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Async wrapper for get_reflections"""
        return self.get_reflections(agent, task_type, max_age_days)

    async def record_performance_async(
        self,
        performance_data: Dict[str, Any]
    ) -> int:
        """Async wrapper for record_performance"""
        self.record_performance(performance_data)
        return len(self.performance_data)

    async def get_performance_stats(
        self,
        paper_category: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance statistics"""
        cutoff = datetime.now() - timedelta(days=days)

        relevant_data = [
            d for d in self.performance_data
            if d["timestamp"] > cutoff
            and (paper_category is None or d.get("paper_category") == paper_category)
        ]

        if not relevant_data:
            return {"no_data": True}

        total = len(relevant_data)
        successes = sum(1 for d in relevant_data if d.get("success"))

        return {
            "total_attempts": total,
            "success_rate": successes / total if total > 0 else 0,
            "avg_iterations": sum(d.get("iterations", 0) for d in relevant_data) / total,
            "common_failures": self._analyze_failures(relevant_data)
        }

    def _analyze_failures(self, data: List[Dict[str, Any]]) -> List[str]:
        """Analyze common failure patterns"""
        failures = [d for d in data if not d.get("success")]
        if not failures:
            return []

        error_types = {}
        for f in failures:
            error = f.get("error_type", "unknown")
            error_types[error] = error_types.get(error, 0) + 1

        sorted_errors = sorted(
            error_types.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [error for error, _ in sorted_errors[:5]]


class TemporalMemory(LoggerMixin):
    """
    Temporal Knowledge Graph Memory

    Implements:
    - Temporal nodes and edges (bi-temporal model from Graphiti)
    - Ebbinghaus forgetting curve (SAGE)
    - Cross-paper learning
    - Agent reflection storage (Reflexion)

    Supports persistent storage via PostgreSQL when database is configured.
    """

    def __init__(self, config):
        self.config = config
        self._use_persistent = False

        # Try to use persistent storage if database is configured
        database_url = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")

        if config.enable_memory and database_url:
            try:
                from app.services.agent_memory_store import get_persistent_store
                self.store = get_persistent_store()
                self._use_persistent = True
                self.log_info("Using PostgreSQL persistent memory storage")
            except Exception as e:
                self.log_warning(f"Failed to init persistent store: {e}, using in-memory")
                self.store = InMemoryTemporalStore()
        else:
            self.log_info("Using in-memory temporal storage (fallback)")
            self.store = InMemoryTemporalStore()

    async def add_node(self, node_data: Dict[str, Any]) -> str:
        """Add a node to the knowledge graph"""
        try:
            if self._use_persistent:
                node_id = await self.store.add_node_async(node_data)
            else:
                node_id = await asyncio.to_thread(
                    self.store.add_node,
                    node_data
                )
            self.log_debug(f"Added node: {node_id}")
            return node_id
        except Exception as e:
            self.log_error("Failed to add node", error=e)
            return ""

    async def query(
        self,
        query_text: str,
        max_results: int = 10,
        node_type: Optional[str] = None,
        paper_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query the knowledge graph"""
        try:
            if self._use_persistent:
                results = await self.store.query_async(
                    query_text,
                    max_results,
                    node_type=node_type,
                    paper_category=paper_category
                )
            else:
                results = await asyncio.to_thread(
                    self.store.query,
                    query_text,
                    max_results
                )
            self.log_debug(f"Query returned {len(results)} results")
            return results
        except Exception as e:
            self.log_error("Failed to query", error=e)
            return []

    async def add_reflection(
        self,
        agent: str,
        reflection: str,
        task_type: str,
        context: Optional[Dict[str, Any]] = None,
        paper_category: Optional[str] = None,
        paper_id: Optional[str] = None,
        was_successful: bool = True
    ):
        """Store agent reflection for future learning"""
        try:
            reflection_data = {
                "reflection": reflection,
                "task_type": task_type,
                "context": context or {},
                "paper_category": paper_category,
                "paper_id": paper_id,
                "was_successful": was_successful
            }

            if self._use_persistent:
                await self.store.add_reflection_async(agent, reflection_data)
            else:
                await asyncio.to_thread(
                    self.store.add_reflection,
                    agent,
                    reflection_data
                )

            self.log_info(f"Stored reflection for {agent}")
        except Exception as e:
            self.log_error("Failed to store reflection", error=e)

    async def get_reflections(
        self,
        agent: str,
        task_type: Optional[str] = None,
        max_age_days: int = 30,
        max_results: int = 5,
        paper_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve agent reflections for learning"""
        try:
            if self._use_persistent:
                reflections = await self.store.get_reflections_async(
                    agent,
                    task_type,
                    max_age_days,
                    max_results=max_results,
                    paper_category=paper_category
                )
                # Persistent store already applies decay scoring
                return reflections[:max_results]
            else:
                reflections = await asyncio.to_thread(
                    self.store.get_reflections,
                    agent,
                    task_type,
                    max_age_days
                )

                # Apply temporal decay (Ebbinghaus curve) for in-memory store
                current_time = datetime.now()
                scored_reflections = []

                for reflection in reflections:
                    age_days = (current_time - reflection["timestamp"]).days
                    # Ebbinghaus forgetting curve: R = e^(-t/S)
                    # S = strength (we use 10 days as baseline)
                    decay_factor = 2.718 ** (-age_days / 10)

                    scored_reflections.append({
                        **reflection,
                        "relevance_score": decay_factor
                    })

                # Sort by relevance
                scored_reflections.sort(
                    key=lambda x: x["relevance_score"],
                    reverse=True
                )

                return scored_reflections[:max_results]

        except Exception as e:
            self.log_error("Failed to get reflections", error=e)
            return []

    async def record_success(
        self,
        paper_category: str,
        complexity: int,
        agent_config: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        paper_id: Optional[str] = None
    ):
        """Record successful generation for meta-learning"""
        try:
            # Add to knowledge graph
            await self.add_node({
                "type": "successful_generation",
                "paper_category": paper_category,
                "paper_id": paper_id,
                "complexity": complexity,
                "agent_config": agent_config,
                "metrics": performance_metrics,
                "timestamp": datetime.now()
            })

            # Record performance metric
            performance_data = {
                "paper_category": paper_category,
                "paper_id": paper_id,
                "complexity": complexity,
                "success": True,
                "agent_config": agent_config,
                **performance_metrics
            }

            if self._use_persistent:
                await self.store.record_performance_async(performance_data)
            else:
                await asyncio.to_thread(
                    self.store.record_performance,
                    performance_data
                )

            self.log_info(f"Recorded success for {paper_category}")

        except Exception as e:
            self.log_error("Failed to record success", error=e)

    async def record_failure(
        self,
        paper_category: str,
        complexity: int,
        error_type: str,
        error_message: str,
        failure_stage: str,
        agent_config: Optional[Dict[str, Any]] = None,
        paper_id: Optional[str] = None
    ):
        """Record failed generation for learning from errors"""
        try:
            performance_data = {
                "paper_category": paper_category,
                "paper_id": paper_id,
                "complexity": complexity,
                "success": False,
                "error_type": error_type,
                "error_message": error_message,
                "failure_stage": failure_stage,
                "agent_config": agent_config
            }

            if self._use_persistent:
                await self.store.record_performance_async(performance_data)
            else:
                await asyncio.to_thread(
                    self.store.record_performance,
                    performance_data
                )

            self.log_info(f"Recorded failure for {paper_category}: {error_type}")

        except Exception as e:
            self.log_error("Failed to record failure", error=e)

    async def get_performance_stats(
        self,
        paper_category: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance statistics for meta-optimization"""
        try:
            if self._use_persistent:
                return await self.store.get_performance_stats(paper_category, days)
            else:
                # Fallback for in-memory store
                cutoff = datetime.now() - timedelta(days=days)

                relevant_data = [
                    d for d in self.store.performance_data
                    if d["timestamp"] > cutoff
                    and (paper_category is None or d.get("paper_category") == paper_category)
                ]

                if not relevant_data:
                    return {"no_data": True}

                total = len(relevant_data)
                successes = sum(1 for d in relevant_data if d.get("success"))

                return {
                    "total_attempts": total,
                    "success_rate": successes / total if total > 0 else 0,
                    "avg_iterations": sum(d.get("iterations", 0) for d in relevant_data) / total,
                    "common_failures": self._analyze_failures(relevant_data)
                }

        except Exception as e:
            self.log_error("Failed to get performance stats", error=e)
            return {"error": str(e)}

    async def get_applicable_patterns(
        self,
        pattern_type: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get learned patterns applicable to current task"""
        if self._use_persistent:
            try:
                return await self.store.get_applicable_patterns(pattern_type, domain)
            except Exception as e:
                self.log_error(f"Failed to get patterns: {e}")
                return []
        return []

    async def add_learning_pattern(
        self,
        pattern_name: str,
        pattern_type: str,
        description: str,
        template: Optional[str] = None,
        examples: Optional[List[Dict[str, Any]]] = None
    ):
        """Add a learned pattern for future use"""
        if self._use_persistent:
            try:
                await self.store.add_learning_pattern(
                    pattern_name,
                    pattern_type,
                    description,
                    template,
                    examples
                )
                self.log_info(f"Added learning pattern: {pattern_name}")
            except Exception as e:
                self.log_error(f"Failed to add pattern: {e}")

    def _analyze_failures(self, data: List[Dict[str, Any]]) -> List[str]:
        """Analyze common failure patterns"""
        failures = [d for d in data if not d.get("success")]
        if not failures:
            return []

        # Simple pattern extraction
        error_types = {}
        for f in failures:
            error = f.get("error_type", "unknown")
            error_types[error] = error_types.get(error, 0) + 1

        # Sort by frequency
        sorted_errors = sorted(
            error_types.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [error for error, _ in sorted_errors[:5]]
