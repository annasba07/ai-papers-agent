"""
Configuration management for AI Paper Digest
Handles environment variables and settings for managed services
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    PROJECT_NAME: str = "AI Paper Digest"
    PROJECT_VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://ai-paper-digest.vercel.app"  # Add your Vercel domain
    ]
    
    # AI/ML API Keys
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # Managed Database Services
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # Neo4j AuraDB
    NEO4J_URI: Optional[str] = None
    NEO4J_USER: Optional[str] = None
    NEO4J_PASSWORD: Optional[str] = None
    
    # Pinecone
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-east-1-aws"
    PINECONE_INDEX_NAME: str = "ai-papers"
    
    # Upstash Redis
    UPSTASH_REDIS_URL: Optional[str] = None
    
    # Background Job Processing
    QSTASH_TOKEN: Optional[str] = None
    QSTASH_CURRENT_SIGNING_KEY: Optional[str] = None
    QSTASH_NEXT_SIGNING_KEY: Optional[str] = None
    
    # External APIs
    ARXIV_API_BASE_URL: str = "http://export.arxiv.org/api/query"
    REPLICATE_API_TOKEN: Optional[str] = None
    
    # Application settings
    PAPERS_FETCH_LIMIT: int = 50
    ANALYSIS_BATCH_SIZE: int = 5
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    BACKGROUND_TASK_TIMEOUT: int = 300  # 5 minutes
    
    # Rate limiting
    GEMINI_REQUESTS_PER_MINUTE: int = 60
    OPENAI_REQUESTS_PER_MINUTE: int = 50
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("DEBUG", pre=True)
    def parse_debug(cls, v):
        """Parse debug flag from environment variable"""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        # Environment variable prefixes
        env_prefix = ""

# Create global settings instance
settings = Settings()

# Validation helpers
def validate_required_services():
    """Validate that required services are configured"""
    missing_services = []
    
    # Check critical services
    if not settings.GEMINI_API_KEY:
        missing_services.append("GEMINI_API_KEY")
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        missing_services.append("Supabase (URL and ANON_KEY)")
    
    if missing_services:
        raise ValueError(
            f"Missing required configuration for: {', '.join(missing_services)}. "
            "Please check your .env file."
        )

def get_database_config() -> dict:
    """Get database configuration for health checks"""
    return {
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY),
        "neo4j_configured": bool(settings.NEO4J_URI and settings.NEO4J_USER and settings.NEO4J_PASSWORD),
        "pinecone_configured": bool(settings.PINECONE_API_KEY),
        "redis_configured": bool(settings.UPSTASH_REDIS_URL),
    }