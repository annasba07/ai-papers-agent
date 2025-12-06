"""
Persistent Agent Memory Store

Provides database-backed storage for agent memory,
replacing the InMemoryTemporalStore with PostgreSQL persistence.

Implements:
- Temporal knowledge graph storage
- Agent reflection persistence
- Performance metric tracking
- Ebbinghaus forgetting curve for relevance scoring
"""
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from math import exp

from sqlalchemy import select, update, and_, or_, func, desc
from sqlalchemy.dialects.postgresql import insert

from app.db.database import database, engine
from app.db.agent_memory_models import (
    AgentMemoryNode,
    AgentReflection,
    AgentPerformanceMetric,
    AgentLearningPattern,
    AgentSession,
)
from app.utils.logger import LoggerMixin


class PersistentMemoryStore(LoggerMixin):
    """
    PostgreSQL-backed persistent memory store

    Provides the same interface as InMemoryTemporalStore
    but with durable storage and advanced querying.
    """

    def __init__(self):
        self._session_id: Optional[str] = None

    def start_session(
        self,
        paper_id: str,
        paper_title: str = "",
        paper_category: str = "",
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new generation session"""
        session_id = str(uuid.uuid4())
        self._session_id = session_id
        return session_id

    async def start_session_async(
        self,
        paper_id: str,
        paper_title: str = "",
        paper_category: str = "",
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new generation session (async)"""
        session_id = str(uuid.uuid4())
        self._session_id = session_id

        query = AgentSession.__table__.insert().values(
            id=session_id,
            paper_id=paper_id,
            paper_title=paper_title,
            paper_category=paper_category,
            started_at=datetime.utcnow(),
            status="in_progress",
            config_snapshot=config
        )

        try:
            await database.execute(query)
            self.log_info(f"Started session {session_id} for paper {paper_id}")
        except Exception as e:
            self.log_error(f"Failed to create session: {e}")

        return session_id

    async def complete_session(
        self,
        session_id: str,
        status: str,
        system_reflection: str = "",
        lessons_learned: Optional[Dict[str, Any]] = None,
        final_test_pass_rate: Optional[float] = None
    ):
        """Mark a session as complete"""
        now = datetime.utcnow()

        # Get started_at for duration calculation
        select_query = select(AgentSession).where(AgentSession.id == session_id)
        session = await database.fetch_one(select_query)

        duration = None
        if session and session["started_at"]:
            duration = (now - session["started_at"]).total_seconds()

        update_query = (
            update(AgentSession)
            .where(AgentSession.id == session_id)
            .values(
                completed_at=now,
                duration_seconds=duration,
                status=status,
                system_reflection=system_reflection,
                lessons_learned=lessons_learned,
                final_test_pass_rate=final_test_pass_rate
            )
        )

        try:
            await database.execute(update_query)
            self.log_info(f"Completed session {session_id} with status {status}")
        except Exception as e:
            self.log_error(f"Failed to complete session: {e}")

    def add_node(self, node_data: Dict[str, Any]) -> str:
        """Add a node to the knowledge graph (sync wrapper)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new task in the running loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.add_node_async(node_data)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(self.add_node_async(node_data))
        except RuntimeError:
            return asyncio.run(self.add_node_async(node_data))

    async def add_node_async(self, node_data: Dict[str, Any]) -> str:
        """Add a node to the knowledge graph"""
        # Generate deterministic ID from content
        node_id = hashlib.md5(
            json.dumps(node_data, sort_keys=True, default=str).encode()
        ).hexdigest()

        # Extract metadata
        node_type = node_data.get("type", "generic")
        paper_category = node_data.get("paper_category")
        technique_domain = node_data.get("technique_domain")

        # Create searchable text
        searchable_text = " ".join(
            str(v) for v in node_data.values()
            if isinstance(v, (str, int, float))
        )

        now = datetime.utcnow()

        # Use upsert to handle duplicates
        stmt = insert(AgentMemoryNode.__table__).values(
            id=node_id,
            node_type=node_type,
            content=node_data,
            paper_category=paper_category,
            technique_domain=technique_domain,
            created_at=now,
            valid_from=now,
            access_count=0,
            last_accessed=now,
            searchable_text=searchable_text[:10000] if searchable_text else None
        ).on_conflict_do_update(
            index_elements=['id'],
            set_=dict(
                access_count=AgentMemoryNode.access_count + 1,
                last_accessed=now
            )
        )

        try:
            await database.execute(stmt)
            self.log_debug(f"Added/updated node: {node_id}")
        except Exception as e:
            self.log_error(f"Failed to add node: {e}")

        return node_id

    def query(self, query_text: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Query nodes (sync wrapper)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.query_async(query_text, max_results)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self.query_async(query_text, max_results)
                )
        except RuntimeError:
            return asyncio.run(self.query_async(query_text, max_results))

    async def query_async(
        self,
        query_text: str,
        max_results: int = 10,
        node_type: Optional[str] = None,
        paper_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query the knowledge graph with relevance scoring"""
        keywords = query_text.lower().split()

        # Build query conditions
        conditions = []

        if node_type:
            conditions.append(AgentMemoryNode.node_type == node_type)

        if paper_category:
            conditions.append(AgentMemoryNode.paper_category == paper_category)

        # Only get nodes within valid time range
        now = datetime.utcnow()
        conditions.append(AgentMemoryNode.valid_from <= now)
        conditions.append(
            or_(
                AgentMemoryNode.valid_until.is_(None),
                AgentMemoryNode.valid_until > now
            )
        )

        # Build the query
        query = select(AgentMemoryNode)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(
            desc(AgentMemoryNode.last_accessed),
            desc(AgentMemoryNode.access_count)
        ).limit(max_results * 3)  # Fetch more for filtering

        try:
            rows = await database.fetch_all(query)
        except Exception as e:
            self.log_error(f"Query failed: {e}")
            return []

        # Score and filter results
        results = []
        for row in rows:
            # Keyword relevance scoring
            searchable = (row["searchable_text"] or "").lower()
            content_str = json.dumps(row["content"]).lower()
            score = sum(
                1 for kw in keywords
                if kw in searchable or kw in content_str
            )

            if score > 0 or not keywords:
                # Apply temporal decay (Ebbinghaus curve)
                age_days = (now - row["created_at"]).days
                decay_rate = row["decay_rate"] or 0.1
                decay_factor = exp(-age_days * decay_rate / 30)  # 30-day baseline

                # Combine scores
                relevance = (score + 1) * decay_factor * (1 + row["access_count"] * 0.1)

                results.append({
                    "node_id": row["id"],
                    "data": {
                        **row["content"],
                        "created_at": row["created_at"],
                        "last_accessed": row["last_accessed"],
                        "access_count": row["access_count"]
                    },
                    "relevance": relevance
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)

        # Update access patterns for returned results
        for result in results[:max_results]:
            await self._update_access(result["node_id"])

        return results[:max_results]

    async def _update_access(self, node_id: str):
        """Update access count and timestamp for a node"""
        query = (
            update(AgentMemoryNode)
            .where(AgentMemoryNode.id == node_id)
            .values(
                access_count=AgentMemoryNode.access_count + 1,
                last_accessed=datetime.utcnow()
            )
        )
        try:
            await database.execute(query)
        except Exception as e:
            self.log_debug(f"Failed to update access: {e}")

    def add_reflection(self, agent: str, reflection_data: Dict[str, Any]):
        """Store agent reflection (sync wrapper)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.add_reflection_async(agent, reflection_data)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self.add_reflection_async(agent, reflection_data)
                )
        except RuntimeError:
            return asyncio.run(self.add_reflection_async(agent, reflection_data))

    async def add_reflection_async(
        self,
        agent: str,
        reflection_data: Dict[str, Any]
    ) -> int:
        """Store agent reflection for learning"""
        query = AgentReflection.__table__.insert().values(
            agent_name=agent,
            task_type=reflection_data.get("task_type", "unknown"),
            reflection=reflection_data.get("reflection", ""),
            context=reflection_data.get("context"),
            paper_category=reflection_data.get("paper_category"),
            paper_id=reflection_data.get("paper_id"),
            complexity_level=reflection_data.get("complexity_level"),
            was_successful=reflection_data.get("was_successful", True),
            improvement_noted=reflection_data.get("improvement_noted"),
            created_at=datetime.utcnow()
        )

        try:
            result = await database.execute(query)
            self.log_debug(f"Added reflection for {agent}")
            return result
        except Exception as e:
            self.log_error(f"Failed to add reflection: {e}")
            return -1

    def get_reflections(
        self,
        agent: str,
        task_type: Optional[str] = None,
        max_age_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Retrieve agent reflections (sync wrapper)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.get_reflections_async(agent, task_type, max_age_days)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self.get_reflections_async(agent, task_type, max_age_days)
                )
        except RuntimeError:
            return asyncio.run(
                self.get_reflections_async(agent, task_type, max_age_days)
            )

    async def get_reflections_async(
        self,
        agent: str,
        task_type: Optional[str] = None,
        max_age_days: int = 30,
        max_results: int = 20,
        paper_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve agent reflections with temporal decay"""
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

        conditions = [
            AgentReflection.agent_name == agent,
            AgentReflection.created_at > cutoff_date
        ]

        if task_type:
            conditions.append(AgentReflection.task_type == task_type)

        if paper_category:
            conditions.append(AgentReflection.paper_category == paper_category)

        query = (
            select(AgentReflection)
            .where(and_(*conditions))
            .order_by(desc(AgentReflection.created_at))
            .limit(max_results)
        )

        try:
            rows = await database.fetch_all(query)
        except Exception as e:
            self.log_error(f"Failed to get reflections: {e}")
            return []

        reflections = []
        for row in rows:
            reflections.append({
                "id": row["id"],
                "reflection": row["reflection"],
                "task_type": row["task_type"],
                "context": row["context"],
                "paper_category": row["paper_category"],
                "was_successful": row["was_successful"],
                "timestamp": row["created_at"],
                "usefulness_score": row["usefulness_score"]
            })

        return reflections

    def record_performance(self, performance_data: Dict[str, Any]):
        """Record performance metrics (sync wrapper)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.record_performance_async(performance_data)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self.record_performance_async(performance_data)
                )
        except RuntimeError:
            return asyncio.run(self.record_performance_async(performance_data))

    async def record_performance_async(
        self,
        performance_data: Dict[str, Any]
    ) -> int:
        """Record performance metrics for meta-learning"""
        tests_passed = performance_data.get("tests_passed", 0)
        tests_total = performance_data.get("tests_total", 0)
        pass_rate = tests_passed / tests_total if tests_total > 0 else None

        query = AgentPerformanceMetric.__table__.insert().values(
            paper_id=performance_data.get("paper_id"),
            paper_category=performance_data.get("paper_category", "unknown"),
            complexity_score=performance_data.get("complexity"),
            success=performance_data.get("success", False),
            tests_passed=tests_passed,
            tests_total=tests_total,
            pass_rate=pass_rate,
            debug_iterations=performance_data.get("iterations", 0),
            execution_time_seconds=performance_data.get("execution_time"),
            error_type=performance_data.get("error_type"),
            error_message=performance_data.get("error_message"),
            failure_stage=performance_data.get("failure_stage"),
            agent_config=performance_data.get("agent_config"),
            model_used=performance_data.get("model"),
            created_at=datetime.utcnow()
        )

        try:
            result = await database.execute(query)
            self.log_debug(f"Recorded performance metric")
            return result
        except Exception as e:
            self.log_error(f"Failed to record performance: {e}")
            return -1

    async def get_performance_stats(
        self,
        paper_category: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance statistics for meta-optimization"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        conditions = [AgentPerformanceMetric.created_at > cutoff]

        if paper_category:
            conditions.append(
                AgentPerformanceMetric.paper_category == paper_category
            )

        # Get aggregate stats
        query = select(
            func.count(AgentPerformanceMetric.id).label("total"),
            func.sum(
                func.cast(AgentPerformanceMetric.success, Integer)
            ).label("successes"),
            func.avg(AgentPerformanceMetric.debug_iterations).label("avg_iterations"),
            func.avg(AgentPerformanceMetric.pass_rate).label("avg_pass_rate"),
            func.avg(
                AgentPerformanceMetric.execution_time_seconds
            ).label("avg_execution_time")
        ).where(and_(*conditions))

        try:
            row = await database.fetch_one(query)
        except Exception as e:
            self.log_error(f"Failed to get performance stats: {e}")
            return {"error": str(e)}

        if not row or row["total"] == 0:
            return {"no_data": True}

        total = row["total"]
        successes = row["successes"] or 0

        # Get common failures
        failures = await self._get_common_failures(conditions)

        return {
            "total_attempts": total,
            "success_rate": successes / total if total > 0 else 0,
            "avg_iterations": float(row["avg_iterations"] or 0),
            "avg_pass_rate": float(row["avg_pass_rate"] or 0),
            "avg_execution_time": float(row["avg_execution_time"] or 0),
            "common_failures": failures
        }

    async def _get_common_failures(
        self,
        base_conditions: list
    ) -> List[str]:
        """Analyze common failure patterns"""
        failure_conditions = base_conditions + [
            AgentPerformanceMetric.success == False
        ]

        query = (
            select(
                AgentPerformanceMetric.error_type,
                func.count(AgentPerformanceMetric.id).label("count")
            )
            .where(and_(*failure_conditions))
            .group_by(AgentPerformanceMetric.error_type)
            .order_by(desc("count"))
            .limit(5)
        )

        try:
            rows = await database.fetch_all(query)
            return [row["error_type"] for row in rows if row["error_type"]]
        except Exception as e:
            self.log_error(f"Failed to get common failures: {e}")
            return []

    async def add_learning_pattern(
        self,
        pattern_name: str,
        pattern_type: str,
        description: str,
        template: Optional[str] = None,
        examples: Optional[List[Dict[str, Any]]] = None,
        applicable_domains: Optional[List[str]] = None
    ) -> int:
        """Add a learned pattern for future use"""
        query = AgentLearningPattern.__table__.insert().values(
            pattern_name=pattern_name,
            pattern_type=pattern_type,
            description=description,
            template=template,
            examples=examples,
            applicable_domains=applicable_domains,
            times_applied=0,
            is_active=True,
            created_at=datetime.utcnow()
        )

        try:
            result = await database.execute(query)
            self.log_info(f"Added learning pattern: {pattern_name}")
            return result
        except Exception as e:
            self.log_error(f"Failed to add learning pattern: {e}")
            return -1

    async def get_applicable_patterns(
        self,
        pattern_type: Optional[str] = None,
        domain: Optional[str] = None,
        min_success_rate: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Get patterns applicable to current task"""
        conditions = [
            AgentLearningPattern.is_active == True
        ]

        if pattern_type:
            conditions.append(AgentLearningPattern.pattern_type == pattern_type)

        if min_success_rate > 0:
            conditions.append(
                or_(
                    AgentLearningPattern.success_rate.is_(None),
                    AgentLearningPattern.success_rate >= min_success_rate
                )
            )

        query = (
            select(AgentLearningPattern)
            .where(and_(*conditions))
            .order_by(
                desc(AgentLearningPattern.success_rate),
                desc(AgentLearningPattern.times_applied)
            )
            .limit(10)
        )

        try:
            rows = await database.fetch_all(query)
        except Exception as e:
            self.log_error(f"Failed to get patterns: {e}")
            return []

        patterns = []
        for row in rows:
            # Check domain applicability if specified
            applicable_domains = row["applicable_domains"] or []
            if domain and applicable_domains and domain not in applicable_domains:
                continue

            patterns.append({
                "id": row["id"],
                "name": row["pattern_name"],
                "type": row["pattern_type"],
                "description": row["description"],
                "template": row["template"],
                "examples": row["examples"],
                "success_rate": row["success_rate"],
                "times_applied": row["times_applied"]
            })

        return patterns

    async def update_pattern_effectiveness(
        self,
        pattern_id: int,
        was_successful: bool
    ):
        """Update a pattern's effectiveness after use"""
        # Get current stats
        select_query = select(AgentLearningPattern).where(
            AgentLearningPattern.id == pattern_id
        )
        pattern = await database.fetch_one(select_query)

        if not pattern:
            return

        times_applied = (pattern["times_applied"] or 0) + 1
        current_rate = pattern["success_rate"] or 0.5

        # Compute new success rate (exponential moving average)
        alpha = 0.3  # Weight for new observation
        new_rate = alpha * (1.0 if was_successful else 0.0) + (1 - alpha) * current_rate

        update_query = (
            update(AgentLearningPattern)
            .where(AgentLearningPattern.id == pattern_id)
            .values(
                times_applied=times_applied,
                success_rate=new_rate,
                last_applied=datetime.utcnow()
            )
        )

        try:
            await database.execute(update_query)
        except Exception as e:
            self.log_error(f"Failed to update pattern effectiveness: {e}")


# Global store instance
_persistent_store: Optional[PersistentMemoryStore] = None


def get_persistent_store() -> PersistentMemoryStore:
    """Get or create the persistent memory store"""
    global _persistent_store
    if _persistent_store is None:
        _persistent_store = PersistentMemoryStore()
    return _persistent_store
