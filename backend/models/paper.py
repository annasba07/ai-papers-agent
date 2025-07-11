"""
Paper models for Supabase database
Defines the schema and data structures for papers and related entities
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class ResearchSignificance(str, Enum):
    """Research significance levels"""
    BREAKTHROUGH = "breakthrough"
    SIGNIFICANT = "significant"
    INCREMENTAL = "incremental"
    MINOR = "minor"

class DifficultyLevel(str, Enum):
    """Implementation difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class PracticalApplicability(str, Enum):
    """Practical applicability levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ImplementationComplexity(str, Enum):
    """Implementation complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ReproductionDifficulty(str, Enum):
    """Reproduction difficulty levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Pydantic models for data validation and serialization

class Author(BaseModel):
    """Author information"""
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None

class ExtractedSection(BaseModel):
    """Extracted paper section"""
    section_name: str
    content: str
    page_numbers: List[int] = []
    
class ExtractedFigure(BaseModel):
    """Extracted figure/table"""
    figure_type: str  # "figure", "table", "equation"
    caption: str
    content: Optional[str] = None  # For tables, extracted text
    page_number: int
    figure_number: Optional[str] = None

class ReproducibilityAssessment(BaseModel):
    """Detailed reproducibility analysis"""
    reproducibility_score: float = Field(ge=0.0, le=1.0)
    code_availability: bool = False
    data_availability: bool = False
    hyperparameter_completeness: float = Field(ge=0.0, le=1.0)
    implementation_details_score: float = Field(ge=0.0, le=1.0)
    experimental_setup_clarity: float = Field(ge=0.0, le=1.0)
    missing_details: List[str] = []
    
class ResultsValidation(BaseModel):
    """Results quality assessment"""
    statistical_significance: bool = False
    baseline_quality: str  # "weak", "moderate", "strong"
    evaluation_completeness: float = Field(ge=0.0, le=1.0)
    failure_case_analysis: bool = False
    computational_cost_reported: bool = False
    comparison_fairness: float = Field(ge=0.0, le=1.0)
    result_reliability_score: float = Field(ge=0.0, le=1.0)

class AIAnalysis(BaseModel):
    """AI-generated analysis results"""
    # Basic summary
    summary: str
    key_contribution: str
    novelty: str
    
    # Technical analysis
    technical_innovation: str
    methodology_breakdown: str
    performance_highlights: str
    implementation_insights: str
    limitations: str
    
    # Research context
    research_context: str
    future_implications: str
    research_significance: ResearchSignificance
    impact_score: float = Field(ge=1.0, le=5.0)
    
    # Practical assessment
    practical_applicability: PracticalApplicability
    implementation_complexity: ImplementationComplexity
    has_code: bool
    difficulty_level: DifficultyLevel
    reading_time: int = Field(ge=1, description="Estimated reading time in minutes")
    reproduction_difficulty: ReproductionDifficulty
    
    # Enhanced analysis from full paper
    reproducibility_assessment: Optional[ReproducibilityAssessment] = None
    results_validation: Optional[ResultsValidation] = None
    computational_requirements: Optional[Dict[str, Any]] = None
    hidden_limitations: List[str] = []
    real_world_applicability: float = Field(ge=0.0, le=1.0, default=0.5)
    
    # Confidence and metadata
    confidence_score: float = Field(ge=0.0, le=1.0)
    analysis_version: str = "2.0"
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    full_text_analyzed: bool = False

class PaperCreate(BaseModel):
    """Paper creation model"""
    id: str = Field(description="arXiv ID")
    title: str
    authors: List[Author]
    published_date: datetime
    abstract: str
    categories: List[str]
    arxiv_url: str
    pdf_url: Optional[str] = None
    
class PaperUpdate(BaseModel):
    """Paper update model"""
    ai_analysis: Optional[AIAnalysis] = None
    vector_id: Optional[str] = None
    full_text: Optional[str] = None
    figures_extracted: bool = False
    last_analyzed: Optional[datetime] = None

class Paper(BaseModel):
    """Complete paper model"""
    id: str
    title: str
    authors: List[Author]
    published_date: datetime
    abstract: str
    categories: List[str]
    arxiv_url: str
    pdf_url: Optional[str] = None
    
    # Analysis results
    ai_analysis: Optional[AIAnalysis] = None
    vector_id: Optional[str] = None
    
    # Full paper content
    full_text: Optional[str] = None
    extracted_sections: Optional[Dict[str, ExtractedSection]] = None
    extracted_figures: Optional[List[ExtractedFigure]] = None
    
    # Processing status
    figures_extracted: bool = False
    full_text_processed: bool = False
    last_analyzed: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Topic(BaseModel):
    """Topic/research area model"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    parent_topic_id: Optional[int] = None
    
    # Trend data
    paper_count: int = 0
    momentum_score: float = Field(ge=0.0, le=1.0, default=0.5)
    trend_direction: str = "stable"  # "growing", "declining", "stable"
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProcessingQueue(BaseModel):
    """Background processing queue model"""
    id: Optional[int] = None
    paper_id: str
    task_type: str  # "analysis", "vector_embedding", "figure_extraction"
    status: str = "pending"  # "pending", "processing", "completed", "failed"
    priority: int = Field(ge=1, le=10, default=5)
    attempts: int = 0
    max_attempts: int = 3
    error_message: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Database table schemas for Supabase
SUPABASE_TABLES = {
    "papers": """
        CREATE TABLE papers (
            id VARCHAR PRIMARY KEY,
            title TEXT NOT NULL,
            authors JSONB NOT NULL,
            published_date TIMESTAMP WITH TIME ZONE NOT NULL,
            abstract TEXT NOT NULL,
            categories JSONB NOT NULL,
            arxiv_url VARCHAR NOT NULL,
            pdf_url VARCHAR,
            ai_analysis JSONB,
            vector_id VARCHAR,
            full_text TEXT,
            extracted_sections JSONB,
            extracted_figures JSONB,
            figures_extracted BOOLEAN DEFAULT FALSE,
            full_text_processed BOOLEAN DEFAULT FALSE,
            last_analyzed TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Indexes for performance
        CREATE INDEX idx_papers_published_date ON papers(published_date);
        CREATE INDEX idx_papers_categories ON papers USING gin(categories);
        CREATE INDEX idx_papers_title_search ON papers USING gin(to_tsvector('english', title));
        CREATE INDEX idx_papers_abstract_search ON papers USING gin(to_tsvector('english', abstract));
        CREATE INDEX idx_papers_full_text_search ON papers USING gin(to_tsvector('english', full_text));
        CREATE INDEX idx_papers_last_analyzed ON papers(last_analyzed);
        CREATE INDEX idx_papers_full_text_processed ON papers(full_text_processed);
    """,
    
    "topics": """
        CREATE TABLE topics (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL,
            description TEXT,
            parent_topic_id INTEGER REFERENCES topics(id),
            paper_count INTEGER DEFAULT 0,
            momentum_score REAL DEFAULT 0.5 CHECK (momentum_score >= 0 AND momentum_score <= 1),
            trend_direction VARCHAR DEFAULT 'stable' CHECK (trend_direction IN ('growing', 'declining', 'stable')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX idx_topics_name ON topics(name);
        CREATE INDEX idx_topics_parent ON topics(parent_topic_id);
    """,
    
    "processing_queue": """
        CREATE TABLE processing_queue (
            id SERIAL PRIMARY KEY,
            paper_id VARCHAR NOT NULL REFERENCES papers(id),
            task_type VARCHAR NOT NULL,
            status VARCHAR DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
            priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
            attempts INTEGER DEFAULT 0,
            max_attempts INTEGER DEFAULT 3,
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX idx_processing_queue_status ON processing_queue(status);
        CREATE INDEX idx_processing_queue_priority ON processing_queue(priority, created_at);
        CREATE INDEX idx_processing_queue_paper_id ON processing_queue(paper_id);
    """
}