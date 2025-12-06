"""
Supabase Client Integration

Provides easy access to Supabase features:
- Simple CRUD operations via PostgREST
- Real-time subscriptions
- Storage for file uploads
- Edge function invocation

Use alongside SQLAlchemy for:
- Complex queries → SQLAlchemy
- Simple CRUD → Supabase client
- Real-time → Supabase client
- File storage → Supabase client

Setup:
    Add to .env:
    SUPABASE_URL=https://xxxxx.supabase.co
    SUPABASE_ANON_KEY=eyJhbG...
    SUPABASE_SERVICE_KEY=eyJhbG... (for admin operations)
"""
import os
from typing import Optional, Any, Dict, List
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


# Lazy import to avoid issues if supabase not installed
_supabase_client = None
_supabase_admin_client = None


def _get_supabase():
    """Lazy import of supabase module"""
    try:
        from supabase import create_client, Client
        return create_client, Client
    except ImportError:
        return None, None


@lru_cache(maxsize=1)
def get_supabase_client():
    """
    Get Supabase client for regular operations

    Uses anon key - respects Row Level Security (RLS)
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    create_client, _ = _get_supabase()
    if create_client is None:
        return None

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        return None

    _supabase_client = create_client(url, key)
    return _supabase_client


@lru_cache(maxsize=1)
def get_supabase_admin():
    """
    Get Supabase admin client

    Uses service role key - bypasses RLS
    Use with caution for admin operations only
    """
    global _supabase_admin_client

    if _supabase_admin_client is not None:
        return _supabase_admin_client

    create_client, _ = _get_supabase()
    if create_client is None:
        return None

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        # Fall back to anon key if service key not available
        key = os.getenv("SUPABASE_ANON_KEY")
        if not key:
            return None

    _supabase_admin_client = create_client(url, key)
    return _supabase_admin_client


class SupabaseHelper:
    """
    Helper class for common Supabase operations

    Provides a simpler interface for CRUD operations
    while the raw client is available for advanced use.
    """

    def __init__(self, use_admin: bool = False):
        """
        Initialize helper

        Args:
            use_admin: If True, uses service role key (bypasses RLS)
        """
        if use_admin:
            self.client = get_supabase_admin()
        else:
            self.client = get_supabase_client()

        self.is_available = self.client is not None

    def table(self, name: str):
        """Get table reference for queries"""
        if not self.is_available:
            raise RuntimeError("Supabase client not configured")
        return self.client.table(name)

    # =========== CRUD Operations ===========

    async def insert(
        self,
        table: str,
        data: Dict[str, Any],
        returning: str = "representation"
    ) -> Optional[Dict]:
        """Insert a single row"""
        if not self.is_available:
            return None

        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Supabase insert error: {e}")
            return None

    async def insert_many(
        self,
        table: str,
        data: List[Dict[str, Any]]
    ) -> List[Dict]:
        """Insert multiple rows"""
        if not self.is_available:
            return []

        try:
            result = self.client.table(table).insert(data).execute()
            return result.data or []
        except Exception as e:
            print(f"Supabase insert_many error: {e}")
            return []

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        descending: bool = False
    ) -> List[Dict]:
        """Select rows with optional filters"""
        if not self.is_available:
            return []

        try:
            query = self.client.table(table).select(columns)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            if order_by:
                query = query.order(order_by, desc=descending)

            if limit:
                query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Supabase select error: {e}")
            return []

    async def select_one(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict]:
        """Select a single row"""
        results = await self.select(table, columns, filters, limit=1)
        return results[0] if results else None

    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> List[Dict]:
        """Update rows matching filters"""
        if not self.is_available:
            return []

        try:
            query = self.client.table(table).update(data)

            for key, value in filters.items():
                query = query.eq(key, value)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Supabase update error: {e}")
            return []

    async def upsert(
        self,
        table: str,
        data: Dict[str, Any],
        on_conflict: str = "id"
    ) -> Optional[Dict]:
        """Insert or update based on conflict"""
        if not self.is_available:
            return None

        try:
            result = (
                self.client.table(table)
                .upsert(data, on_conflict=on_conflict)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Supabase upsert error: {e}")
            return None

    async def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> List[Dict]:
        """Delete rows matching filters"""
        if not self.is_available:
            return []

        try:
            query = self.client.table(table).delete()

            for key, value in filters.items():
                query = query.eq(key, value)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Supabase delete error: {e}")
            return []

    # =========== Advanced Queries ===========

    async def rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Call a PostgreSQL function"""
        if not self.is_available:
            return None

        try:
            result = self.client.rpc(function_name, params or {}).execute()
            return result.data
        except Exception as e:
            print(f"Supabase RPC error: {e}")
            return None

    async def search_vector(
        self,
        table: str,
        column: str,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Semantic search using pgvector

        Requires a PostgreSQL function like:
        CREATE OR REPLACE FUNCTION match_documents(
            query_embedding vector(1536),
            match_threshold float,
            match_count int
        )
        """
        if not self.is_available:
            return []

        try:
            result = self.client.rpc(
                f"match_{table}",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": threshold,
                    "match_count": limit
                }
            ).execute()
            return result.data or []
        except Exception as e:
            print(f"Supabase vector search error: {e}")
            return []

    # =========== Storage ===========

    def storage(self, bucket: str):
        """Get storage bucket reference"""
        if not self.is_available:
            raise RuntimeError("Supabase client not configured")
        return self.client.storage.from_(bucket)

    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_data: bytes,
        content_type: str = "application/octet-stream"
    ) -> Optional[str]:
        """Upload a file to Supabase Storage"""
        if not self.is_available:
            return None

        try:
            result = (
                self.client.storage
                .from_(bucket)
                .upload(path, file_data, {"content-type": content_type})
            )
            # Return public URL
            return self.client.storage.from_(bucket).get_public_url(path)
        except Exception as e:
            print(f"Supabase upload error: {e}")
            return None

    async def download_file(
        self,
        bucket: str,
        path: str
    ) -> Optional[bytes]:
        """Download a file from Supabase Storage"""
        if not self.is_available:
            return None

        try:
            result = self.client.storage.from_(bucket).download(path)
            return result
        except Exception as e:
            print(f"Supabase download error: {e}")
            return None

    # =========== Real-time (sync only) ===========

    def subscribe(
        self,
        table: str,
        event: str = "*",
        callback=None
    ):
        """
        Subscribe to real-time changes

        Note: Real-time requires websocket connection,
        typically used in long-running processes.

        Args:
            table: Table name to subscribe to
            event: "INSERT", "UPDATE", "DELETE", or "*"
            callback: Function to call on changes
        """
        if not self.is_available:
            return None

        try:
            channel = (
                self.client.channel(f"changes_{table}")
                .on_postgres_changes(
                    event=event,
                    schema="public",
                    table=table,
                    callback=callback
                )
                .subscribe()
            )
            return channel
        except Exception as e:
            print(f"Supabase subscribe error: {e}")
            return None


# Convenience instances
supabase = SupabaseHelper(use_admin=False)
supabase_admin = SupabaseHelper(use_admin=True)


# =========== Agent Memory Shortcuts ===========

class AgentMemorySupabase:
    """
    Supabase-specific helper for agent memory operations

    Provides simple methods that map directly to the
    agent_memory_* tables.
    """

    def __init__(self):
        self.helper = SupabaseHelper(use_admin=True)

    async def add_reflection(
        self,
        agent_name: str,
        task_type: str,
        reflection: str,
        paper_category: Optional[str] = None,
        paper_id: Optional[str] = None,
        was_successful: bool = True,
        context: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Add an agent reflection"""
        return await self.helper.insert("agent_reflections", {
            "agent_name": agent_name,
            "task_type": task_type,
            "reflection": reflection,
            "paper_category": paper_category,
            "paper_id": paper_id,
            "was_successful": was_successful,
            "context": context
        })

    async def get_reflections(
        self,
        agent_name: str,
        task_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get recent reflections for an agent"""
        filters = {"agent_name": agent_name}
        if task_type:
            filters["task_type"] = task_type

        return await self.helper.select(
            "agent_reflections",
            filters=filters,
            order_by="created_at",
            descending=True,
            limit=limit
        )

    async def record_performance(
        self,
        paper_category: str,
        success: bool,
        tests_passed: int = 0,
        tests_total: int = 0,
        debug_iterations: int = 0,
        error_type: Optional[str] = None,
        paper_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Record a performance metric"""
        return await self.helper.insert("agent_performance_metrics", {
            "paper_category": paper_category,
            "paper_id": paper_id,
            "success": success,
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            "pass_rate": tests_passed / tests_total if tests_total > 0 else None,
            "debug_iterations": debug_iterations,
            "error_type": error_type
        })

    async def get_success_rate(
        self,
        paper_category: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get success rate statistics"""
        # This would be better as a PostgreSQL function
        # For now, fetch and compute client-side
        filters = {}
        if paper_category:
            filters["paper_category"] = paper_category

        metrics = await self.helper.select(
            "agent_performance_metrics",
            filters=filters,
            order_by="created_at",
            descending=True,
            limit=1000
        )

        if not metrics:
            return {"no_data": True}

        total = len(metrics)
        successes = sum(1 for m in metrics if m.get("success"))

        return {
            "total_attempts": total,
            "success_rate": successes / total if total > 0 else 0,
            "successes": successes,
            "failures": total - successes
        }


# Convenience instance
agent_memory_supabase = AgentMemorySupabase()
