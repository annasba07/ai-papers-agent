"""
Database models for paper entities
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Paper(Base):
    """Paper model for storing arXiv papers and analysis"""
    
    __tablename__ = "papers"
    
    id = Column(String, primary_key=True, index=True)  # arXiv ID
    title = Column(String, index=True, nullable=False)
    authors = Column(JSON, nullable=False)  # Store as JSON array
    published = Column(DateTime, nullable=False)
    original_summary = Column(Text, nullable=False)
    ai_summary_json = Column(JSON)  # Store AI analysis as JSON object
    category = Column(String, index=True)
    link = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Paper(id='{self.id}', title='{self.title[:50]}...')>"