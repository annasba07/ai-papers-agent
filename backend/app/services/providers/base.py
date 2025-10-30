"""
Common base utilities for external data providers.
"""
from __future__ import annotations

from typing import Any, Dict

from app.utils.logger import LoggerMixin


class ProviderError(RuntimeError):
    """Generic exception for provider failures."""


class ProviderConfig(dict):
    """
    Simple config holder. Extend or swap with pydantic settings once
    we stabilise configuration needs (API keys, rate limits, etc.).
    """

    def require(self, key: str) -> Any:
        if key not in self:
            raise ProviderError(f"Missing provider config key: {key}")
        return self[key]


class BaseProvider(LoggerMixin):
    """Minimal base class offering logging helpers and config access."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = ProviderConfig(config or {})
