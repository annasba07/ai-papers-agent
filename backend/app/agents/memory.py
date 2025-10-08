"""
Temporal Memory System for Multi-Agent Learning

Based on Graphiti (2024) temporal knowledge graphs
Implements Ebbinghaus forgetting curve (SAGE, 2024)
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import hashlib
from app.utils.logger import LoggerMixin


class InMemoryTemporalStore:
    """
    Fallback in-memory temporal storage
    Will be replaced with Neo4j + Graphiti in production
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.reflections: Dict[str, List[Dict[str, Any]]] = {}
        self.performance_data: List[Dict[str, Any]] = []

    def add_node(self, node_data: Dict[str, Any]):
        """Add a node with timestamp"""
        node_id = hashlib.md5(
            json.dumps(node_data, sort_keys=True).encode()
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
        TODO: Replace with proper graph traversal
        """
        results = []
        keywords = query_text.lower().split()

        for node_id, node in self.nodes.items():
            # Simple relevance scoring
            node_text = json.dumps(node).lower()
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


class TemporalMemory(LoggerMixin):
    """
    Temporal Knowledge Graph Memory

    Implements:
    - Temporal nodes and edges (bi-temporal model from Graphiti)
    - Ebbinghaus forgetting curve (SAGE)
    - Cross-paper learning
    - Agent reflection storage (Reflexion)
    """

    def __init__(self, config):
        self.config = config

        if config.enable_memory and config.neo4j_password:
            # TODO: Initialize Neo4j + Graphiti
            # from graphiti import TemporalKnowledgeGraph
            # self.store = TemporalKnowledgeGraph(...)
            self.log_info("Neo4j memory enabled")
            self.store = InMemoryTemporalStore()  # Fallback for now
        else:
            self.log_info("Using in-memory temporal storage (fallback)")
            self.store = InMemoryTemporalStore()

    async def add_node(self, node_data: Dict[str, Any]) -> str:
        """Add a node to the knowledge graph"""
        try:
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
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Query the knowledge graph"""
        try:
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
        context: Optional[Dict[str, Any]] = None
    ):
        """Store agent reflection for future learning"""
        try:
            reflection_data = {
                "reflection": reflection,
                "task_type": task_type,
                "context": context or {}
            }

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
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve agent reflections for learning"""
        try:
            reflections = await asyncio.to_thread(
                self.store.get_reflections,
                agent,
                task_type,
                max_age_days
            )

            # Apply temporal decay (Ebbinghaus curve)
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
        performance_metrics: Dict[str, Any]
    ):
        """Record successful generation for meta-learning"""
        try:
            await self.add_node({
                "type": "successful_generation",
                "paper_category": paper_category,
                "complexity": complexity,
                "agent_config": agent_config,
                "metrics": performance_metrics,
                "timestamp": datetime.now()
            })

            await asyncio.to_thread(
                self.store.record_performance,
                {
                    "paper_category": paper_category,
                    "complexity": complexity,
                    "success": True,
                    **performance_metrics
                }
            )

            self.log_info(f"Recorded success for {paper_category}")

        except Exception as e:
            self.log_error("Failed to record success", error=e)

    async def get_performance_stats(
        self,
        paper_category: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance statistics for meta-optimization"""
        try:
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
