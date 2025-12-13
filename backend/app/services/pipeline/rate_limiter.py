"""
Rate Limiter - Distributed Rate Limit Coordination

Coordinates rate limits across workers using database-backed tracking.
Provides local delay enforcement and backoff support for 429 responses.
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.db.database import database

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for a rate-limited provider."""
    max_requests: int
    window_seconds: int
    min_delay_between_requests: float = 0.0


# Default rate limit configurations
RATE_LIMIT_CONFIGS: Dict[str, RateLimitConfig] = {
    "gemini": RateLimitConfig(
        max_requests=60,
        window_seconds=60,
        min_delay_between_requests=1.0  # 1 req/sec max
    ),
    "semantic_scholar": RateLimitConfig(
        max_requests=100,  # Conservative - batch API is separate
        window_seconds=60,
        min_delay_between_requests=0.1
    ),
    "github": RateLimitConfig(
        max_requests=5000,
        window_seconds=3600,  # Per hour
        min_delay_between_requests=0.1
    ),
    "openalex": RateLimitConfig(
        max_requests=10,
        window_seconds=1,
        min_delay_between_requests=0.1
    ),
    "local": RateLimitConfig(
        max_requests=10000,
        window_seconds=60,
        min_delay_between_requests=0.0  # No limit
    ),
}


class RateLimiter:
    """
    Coordinates rate limits across distributed workers.

    Uses the rate_limit_tracking table for coordination and
    local tracking for immediate delay enforcement.
    """

    def __init__(self):
        self._local_last_request: Dict[str, float] = {}
        self._configs = RATE_LIMIT_CONFIGS.copy()

    async def initialize_provider(self, provider: str) -> None:
        """Initialize rate limit tracking for a provider in the database."""
        config = self._configs.get(provider)
        if not config:
            logger.warning(f"No rate limit config for provider: {provider}")
            return

        query = """
            INSERT INTO rate_limit_tracking (
                provider, requests_count, window_start,
                window_seconds, max_requests
            ) VALUES (
                :provider, 0, NOW(), :window_seconds, :max_requests
            )
            ON CONFLICT (provider) DO UPDATE SET
                max_requests = :max_requests,
                window_seconds = :window_seconds
        """
        await database.execute(query, {
            "provider": provider,
            "window_seconds": config.window_seconds,
            "max_requests": config.max_requests
        })

    async def acquire(self, provider: str, timeout: float = 30.0) -> bool:
        """
        Acquire permission to make a request.

        Returns True if permission granted, False if timed out waiting.
        Handles both local delay and distributed coordination.
        """
        start_time = time.time()
        config = self._configs.get(provider, RateLimitConfig(1000, 60))

        while time.time() - start_time < timeout:
            # Check for backoff first
            backoff_until = await self._get_backoff_until(provider)
            if backoff_until and backoff_until > datetime.utcnow():
                wait_seconds = (backoff_until - datetime.utcnow()).total_seconds()
                if wait_seconds > 0:
                    logger.info(f"Rate limiter backing off {provider} for {wait_seconds:.1f}s")
                    await asyncio.sleep(min(wait_seconds, timeout - (time.time() - start_time)))
                    continue

            # Enforce local minimum delay
            last_request = self._local_last_request.get(provider, 0)
            elapsed = time.time() - last_request
            if elapsed < config.min_delay_between_requests:
                await asyncio.sleep(config.min_delay_between_requests - elapsed)

            # Try to increment counter in database
            success = await self._try_increment(provider, config)
            if success:
                self._local_last_request[provider] = time.time()
                return True

            # Rate limited - wait a bit and retry
            await asyncio.sleep(0.5)

        logger.warning(f"Rate limiter timeout for {provider}")
        return False

    async def _try_increment(self, provider: str, config: RateLimitConfig) -> bool:
        """Try to increment the request counter, resetting window if expired."""
        # First, check if window needs reset
        reset_query = """
            UPDATE rate_limit_tracking
            SET requests_count = 0,
                window_start = NOW()
            WHERE provider = :provider
            AND window_start + (window_seconds || ' seconds')::INTERVAL < NOW()
            RETURNING provider
        """
        reset_result = await database.fetch_one(reset_query, {"provider": provider})

        # Now try to increment if under limit
        increment_query = """
            UPDATE rate_limit_tracking
            SET requests_count = requests_count + 1,
                last_request_at = NOW()
            WHERE provider = :provider
            AND requests_count < max_requests
            RETURNING requests_count
        """
        result = await database.fetch_one(increment_query, {"provider": provider})
        return result is not None

    async def _get_backoff_until(self, provider: str) -> Optional[datetime]:
        """Get the backoff deadline for a provider."""
        query = """
            SELECT backoff_until
            FROM rate_limit_tracking
            WHERE provider = :provider
        """
        row = await database.fetch_one(query, {"provider": provider})
        return row["backoff_until"] if row and row["backoff_until"] else None

    async def report_rate_limit_hit(
        self,
        provider: str,
        backoff_seconds: int = 60
    ) -> None:
        """
        Report that we hit a rate limit (e.g., received 429).

        Sets a backoff period during which no requests should be made.
        """
        logger.warning(f"Rate limit hit for {provider}, backing off {backoff_seconds}s")

        query = """
            UPDATE rate_limit_tracking
            SET backoff_until = NOW() + (:backoff_seconds || ' seconds')::INTERVAL,
                requests_count = max_requests  -- Max out counter
            WHERE provider = :provider
        """
        await database.execute(query, {
            "provider": provider,
            "backoff_seconds": backoff_seconds
        })

    async def clear_backoff(self, provider: str) -> None:
        """Clear backoff for a provider."""
        query = """
            UPDATE rate_limit_tracking
            SET backoff_until = NULL
            WHERE provider = :provider
        """
        await database.execute(query, {"provider": provider})

    async def get_stats(self, provider: str) -> Dict[str, Any]:
        """Get current rate limit statistics for a provider."""
        query = """
            SELECT
                provider,
                requests_count,
                max_requests,
                window_start,
                window_seconds,
                last_request_at,
                backoff_until,
                CASE
                    WHEN window_start + (window_seconds || ' seconds')::INTERVAL > NOW()
                    THEN EXTRACT(EPOCH FROM (
                        window_start + (window_seconds || ' seconds')::INTERVAL - NOW()
                    ))
                    ELSE 0
                END as seconds_until_reset
            FROM rate_limit_tracking
            WHERE provider = :provider
        """
        row = await database.fetch_one(query, {"provider": provider})

        if not row:
            return {"provider": provider, "error": "Not initialized"}

        return {
            "provider": row["provider"],
            "requests_count": row["requests_count"],
            "max_requests": row["max_requests"],
            "remaining": max(0, row["max_requests"] - row["requests_count"]),
            "window_seconds": row["window_seconds"],
            "seconds_until_reset": int(row["seconds_until_reset"]),
            "last_request_at": row["last_request_at"].isoformat() if row["last_request_at"] else None,
            "backoff_until": row["backoff_until"].isoformat() if row["backoff_until"] else None,
            "is_backed_off": bool(row["backoff_until"] and row["backoff_until"] > datetime.utcnow())
        }

    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get rate limit statistics for all providers."""
        query = """
            SELECT
                provider,
                requests_count,
                max_requests,
                window_start,
                window_seconds,
                last_request_at,
                backoff_until
            FROM rate_limit_tracking
        """
        rows = await database.fetch_all(query)

        return {
            row["provider"]: {
                "requests_count": row["requests_count"],
                "max_requests": row["max_requests"],
                "remaining": max(0, row["max_requests"] - row["requests_count"]),
                "last_request_at": row["last_request_at"].isoformat() if row["last_request_at"] else None,
                "is_backed_off": bool(row["backoff_until"] and row["backoff_until"] > datetime.utcnow())
            }
            for row in rows
        }


# Singleton instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the rate limiter singleton."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


async def initialize_rate_limiters() -> None:
    """Initialize all rate limit providers in the database."""
    limiter = get_rate_limiter()
    for provider in RATE_LIMIT_CONFIGS.keys():
        await limiter.initialize_provider(provider)
    logger.info(f"Initialized rate limiters for: {list(RATE_LIMIT_CONFIGS.keys())}")
