"""
Database connection and session management for Supabase PostgreSQL

Uses asyncpg via databases library for async operations.
"""
import os
from typing import Optional
from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Supabase connection URL from environment
DATABASE_URL = os.getenv(
    "SUPABASE_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql://localhost/ai_papers")
)

# For async operations (FastAPI)
database = Database(
    DATABASE_URL,
    min_size=5,
    max_size=20
)

# For SQLAlchemy models
engine = create_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
metadata = MetaData()


async def connect_db():
    """Connect to database on startup"""
    await database.connect()
    print(f"✅ Connected to Supabase PostgreSQL")


async def disconnect_db():
    """Disconnect from database on shutdown"""
    await database.disconnect()
    print("👋 Disconnected from database")


async def get_db():
    """Get database connection for dependency injection"""
    return database


def get_sync_db():
    """Get synchronous database session (for migrations, etc.)"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
