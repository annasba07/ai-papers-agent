"""
Redis caching service for paper analysis
"""
import json
import hashlib
import redis
from typing import Optional, Dict, Any
from app.core.config import settings
from app.utils.logger import LoggerMixin
from app.utils.exceptions import CacheException


class CacheService(LoggerMixin):
    """Service for handling Redis caching operations"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.log_info("Cache service initialized successfully")
        except Exception as e:
            self.log_error("Failed to initialize cache service", error=e)
            raise CacheException(f"Redis connection failed: {str(e)}", error_code="CACHE_INIT_ERROR")
    
    def _generate_cache_key(self, title: str, abstract: str, analysis_type: str = "full") -> str:
        """Generate a unique cache key for paper analysis"""
        content = f"{title}:{abstract}:{analysis_type}"
        return f"paper_analysis:{hashlib.md5(content.encode()).hexdigest()}"
    
    def get_cached_analysis(self, title: str, abstract: str, analysis_type: str = "full") -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis if available"""
        try:
            cache_key = self._generate_cache_key(title, abstract, analysis_type)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                self.log_debug("Cache hit", cache_key=cache_key)
                return json.loads(cached_data)
            else:
                self.log_debug("Cache miss", cache_key=cache_key)
                return None
        except Exception as e:
            self.log_error("Cache retrieval failed", error=e, analysis_type=analysis_type)
            return None
    
    def cache_analysis(self, title: str, abstract: str, analysis: Dict[str, Any], analysis_type: str = "full") -> None:
        """Cache analysis results with TTL"""
        try:
            cache_key = self._generate_cache_key(title, abstract, analysis_type)
            self.redis_client.setex(
                cache_key, 
                settings.REDIS_CACHE_TTL, 
                json.dumps(analysis)
            )
            self.log_debug("Analysis cached successfully", cache_key=cache_key, ttl=settings.REDIS_CACHE_TTL)
        except Exception as e:
            self.log_error("Cache storage failed", error=e, analysis_type=analysis_type)
    
    def invalidate_cache(self, title: str, abstract: str, analysis_type: str = "full") -> None:
        """Invalidate cached analysis"""
        try:
            cache_key = self._generate_cache_key(title, abstract, analysis_type)
            result = self.redis_client.delete(cache_key)
            if result:
                self.log_debug("Cache invalidated successfully", cache_key=cache_key)
            else:
                self.log_debug("Cache key not found for invalidation", cache_key=cache_key)
        except Exception as e:
            self.log_error("Cache invalidation failed", error=e, analysis_type=analysis_type)
    
    def clear_all_cache(self) -> None:
        """Clear all cached analysis data"""
        try:
            pattern = "paper_analysis:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                self.log_info(f"Cleared {deleted_count} cached analyses")
            else:
                self.log_info("No cached analyses to clear")
        except Exception as e:
            self.log_error("Cache clear failed", error=e)


# Global cache service instance
cache_service = CacheService()