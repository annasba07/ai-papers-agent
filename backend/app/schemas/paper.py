"""
Pydantic schemas for paper data validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResearchSignificance(str, Enum):
    INCREMENTAL = "incremental"
    SIGNIFICANT = "significant"
    BREAKTHROUGH = "breakthrough"


class AIAnalysisSchema(BaseModel):
    """Schema for AI analysis results"""
    summary: str = Field(..., description="Concise summary of the paper")
    novelty: str = Field(..., description="What's novel about this approach")
    technicalInnovation: str = Field(..., description="Key technical contribution")
    keyContribution: str = Field(..., description="Main contribution to the field")
    methodologyBreakdown: str = Field(..., description="How the methodology works")
    performanceHighlights: str = Field(..., description="Key performance results")
    implementationInsights: str = Field(..., description="Implementation complexity details")
    researchContext: str = Field(..., description="Research field context")
    futureImplications: str = Field(..., description="Future impact and directions")
    limitations: str = Field(..., description="Current limitations")
    impactScore: int = Field(..., ge=1, le=10, description="Impact score 1-10")
    difficultyLevel: DifficultyLevel = Field(..., description="Reading difficulty level")
    readingTime: int = Field(..., ge=1, description="Estimated reading time in minutes")
    hasCode: bool = Field(..., description="Whether code is available")
    implementationComplexity: ComplexityLevel = Field(..., description="Implementation complexity")
    practicalApplicability: ComplexityLevel = Field(..., description="Practical applicability level")
    researchSignificance: ResearchSignificance = Field(..., description="Research significance level")
    reproductionDifficulty: ComplexityLevel = Field(..., description="Reproduction difficulty")


class PaperBase(BaseModel):
    """Base schema for paper data"""
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of authors")
    summary: str = Field(..., description="Paper abstract/summary")
    published: datetime = Field(..., description="Publication date")
    link: str = Field(..., description="Link to paper")
    category: Optional[str] = Field(None, description="arXiv category")


class PaperCreate(PaperBase):
    """Schema for creating a new paper"""
    pass


class PaperUpdate(BaseModel):
    """Schema for updating paper data"""
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    summary: Optional[str] = None
    published: Optional[datetime] = None
    link: Optional[str] = None
    category: Optional[str] = None
    ai_analysis: Optional[AIAnalysisSchema] = None


class PaperResponse(PaperBase):
    """Schema for paper response"""
    id: str = Field(..., description="arXiv ID")
    aiSummary: Optional[AIAnalysisSchema] = Field(None, description="AI analysis results")
    fetched_at: Optional[datetime] = Field(None, description="When paper was fetched")
    
    class Config:
        from_attributes = True


class PaperSearchParams(BaseModel):
    """Schema for paper search parameters"""
    query: str = Field(..., description="Search query")
    max_results: int = Field(10, ge=1, le=50, description="Maximum results")
    enhance_with_ai: bool = Field(False, description="Whether to enhance with AI analysis")


class BatchAnalysisRequest(BaseModel):
    """Schema for batch analysis request"""
    papers: List[Dict[str, Any]] = Field(..., description="List of papers to analyze")

    class Config:
        schema_extra = {
            "example": {
                "papers": [
                    {
                        "title": "Attention Is All You Need",
                        "summary": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks..."
                    }
                ]
            }
        }


class EmbeddingCacheInfo(BaseModel):
    label: str
    paper_count: int
    active: bool = False


class ContextualSearchRequest(BaseModel):
    """Schema for contextual search request"""
    description: str = Field(..., min_length=10, description="Project description to find relevant papers")
    embedding_label: Optional[str] = Field(None, description="Optional embedding cache label to use")
    fast_mode: bool = Field(
        False,
        description="Skip reranking and AI synthesis for faster results (retrieval only)"
    )
    skip_reranking: bool = Field(
        False,
        description="Skip reranking step to save 500-2000ms latency"
    )
    skip_synthesis: bool = Field(
        False,
        description="Skip AI synthesis step to save 2-5s latency (just return papers)"
    )

    class Config:
        schema_extra = {
            "example": {
                "description": "I am building a mobile app that identifies plant species from a photo taken by the user. I need to know the best models for high-accuracy, on-device image classification.",
                "embedding_label": "specter2",
                "fast_mode": False,
            }
        }


class ContextualSearchTiming(BaseModel):
    """Timing breakdown for contextual search performance analysis"""
    total_ms: float = Field(..., description="Total request time in milliseconds")
    retrieval_ms: float = Field(0, description="Atlas search time in milliseconds")
    rerank_ms: float = Field(0, description="Reranking time in milliseconds")
    synthesis_ms: float = Field(0, description="AI synthesis time in milliseconds")
    mode: str = Field("full", description="fast|skip_rerank|skip_synthesis|full")


class ContextualSearchResponse(BaseModel):
    """Schema for contextual search response"""
    analysis: str = Field(..., description="AI-generated analysis and recommendations")
    papers: List[Dict[str, Any]] = Field(..., description="Relevant papers found")
    timing: Optional[ContextualSearchTiming] = Field(None, description="Performance timing breakdown")
