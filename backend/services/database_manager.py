"""
Database Manager for Multi-Database Architecture
Manages connections to Supabase, Neo4j AuraDB, Pinecone, and Upstash Redis
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Managed service imports
from supabase import create_client, Client as SupabaseClient
from neo4j import GraphDatabase, Driver as Neo4jDriver
from pinecone import Pinecone, ServerlessSpec
import redis
from redis import Redis

# Internal imports
from ..core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Centralized database manager for all managed services
    """
    
    def __init__(self):
        self._supabase: Optional[SupabaseClient] = None
        self._neo4j: Optional[Neo4jDriver] = None
        self._pinecone: Optional[Pinecone] = None
        self._redis: Optional[Redis] = None
        
        # Initialize connections
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize all database connections"""
        try:
            # Supabase connection
            if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
                self._supabase = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
                logger.info("✅ Supabase connected successfully")
            else:
                logger.warning("⚠️ Supabase credentials missing")
            
            # Neo4j AuraDB connection
            if settings.NEO4J_URI and settings.NEO4J_USER and settings.NEO4J_PASSWORD:
                self._neo4j = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
                # Test connection
                with self._neo4j.session() as session:
                    session.run("RETURN 1")
                logger.info("✅ Neo4j AuraDB connected successfully")
            else:
                logger.warning("⚠️ Neo4j AuraDB credentials missing")
            
            # Pinecone connection
            if settings.PINECONE_API_KEY:
                self._pinecone = Pinecone(api_key=settings.PINECONE_API_KEY)
                logger.info("✅ Pinecone connected successfully")
            else:
                logger.warning("⚠️ Pinecone API key missing")
            
            # Redis connection (Upstash)
            if settings.UPSTASH_REDIS_URL:
                self._redis = redis.from_url(
                    settings.UPSTASH_REDIS_URL,
                    decode_responses=True
                )
                # Test connection
                self._redis.ping()
                logger.info("✅ Upstash Redis connected successfully")
            else:
                logger.warning("⚠️ Upstash Redis URL missing")
                
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            raise
    
    @property
    def supabase(self) -> SupabaseClient:
        """Get Supabase client"""
        if not self._supabase:
            raise RuntimeError("Supabase not initialized")
        return self._supabase
    
    @property
    def neo4j(self) -> Neo4jDriver:
        """Get Neo4j driver"""
        if not self._neo4j:
            raise RuntimeError("Neo4j not initialized")
        return self._neo4j
    
    @property
    def pinecone(self) -> Pinecone:
        """Get Pinecone client"""
        if not self._pinecone:
            raise RuntimeError("Pinecone not initialized")
        return self._pinecone
    
    @property
    def redis(self) -> Redis:
        """Get Redis client"""
        if not self._redis:
            raise RuntimeError("Redis not initialized")
        return self._redis
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all database connections"""
        health_status = {}
        
        # Check Supabase
        try:
            if self._supabase:
                # Simple query to test connection
                result = self._supabase.table('papers').select('id').limit(1).execute()
                health_status['supabase'] = True
            else:
                health_status['supabase'] = False
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            health_status['supabase'] = False
        
        # Check Neo4j
        try:
            if self._neo4j:
                with self._neo4j.session() as session:
                    session.run("RETURN 1")
                health_status['neo4j'] = True
            else:
                health_status['neo4j'] = False
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            health_status['neo4j'] = False
        
        # Check Pinecone
        try:
            if self._pinecone:
                # List indexes to test connection
                self._pinecone.list_indexes()
                health_status['pinecone'] = True
            else:
                health_status['pinecone'] = False
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            health_status['pinecone'] = False
        
        # Check Redis
        try:
            if self._redis:
                self._redis.ping()
                health_status['redis'] = True
            else:
                health_status['redis'] = False
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health_status['redis'] = False
        
        return health_status
    
    def close_connections(self):
        """Close all database connections"""
        try:
            if self._neo4j:
                self._neo4j.close()
                logger.info("Neo4j connection closed")
            
            if self._redis:
                self._redis.close()
                logger.info("Redis connection closed")
                
            # Supabase and Pinecone don't need explicit closing
            logger.info("All database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for easy access
def get_supabase() -> SupabaseClient:
    """Get Supabase client instance"""
    return db_manager.supabase

def get_neo4j() -> Neo4jDriver:
    """Get Neo4j driver instance"""
    return db_manager.neo4j

def get_pinecone() -> Pinecone:
    """Get Pinecone client instance"""
    return db_manager.pinecone

def get_redis() -> Redis:
    """Get Redis client instance"""
    return db_manager.redis