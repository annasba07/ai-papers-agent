"""
AI Analysis Service with Structured LLM Outputs
Uses function calling for reliable, structured insights from research papers
"""
import logging
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from abc import ABC, abstractmethod

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
import openai

from ..core.config import settings
from ..models.paper import AIAnalysis, ResearchSignificance, DifficultyLevel, PracticalApplicability, ImplementationComplexity, ReproductionDifficulty
from .database_manager import get_redis

logger = logging.getLogger(__name__)

# Configure AI services
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY

class InsightGenerator(ABC):
    """Base class for insight generation plugins"""
    
    @abstractmethod
    async def generate_insight(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific insight from paper data"""
        pass
    
    @abstractmethod
    def get_insight_type(self) -> str:
        """Get the type of insight this generator produces"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get list of required input fields"""
        pass

class TechnicalAnalysisGenerator(InsightGenerator):
    """Generates technical innovation and methodology insights"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def generate_insight(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical analysis using function calling"""
        
        # Define function schema for structured output
        technical_analysis_function = FunctionDeclaration(
            name="analyze_technical_innovation",
            description="Analyze the technical innovation and methodology of a research paper",
            parameters={
                "type": "object",
                "properties": {
                    "technical_innovation": {
                        "type": "string",
                        "description": "Detailed explanation of the core technical mechanism or approach"
                    },
                    "methodology_breakdown": {
                        "type": "string", 
                        "description": "Step-by-step breakdown of how the proposed method works"
                    },
                    "performance_highlights": {
                        "type": "string",
                        "description": "Key performance results and what makes them significant"
                    },
                    "implementation_insights": {
                        "type": "string",
                        "description": "Practical insights about implementation complexity and requirements"
                    },
                    "limitations": {
                        "type": "string",
                        "description": "Key limitations or potential issues with the approach"
                    },
                    "reproduction_difficulty": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "How difficult would this be to reproduce accurately"
                    }
                },
                "required": ["technical_innovation", "methodology_breakdown", "performance_highlights", "implementation_insights", "limitations", "reproduction_difficulty"]
            }
        )
        
        tool = Tool(function_declarations=[technical_analysis_function])
        
        prompt = f"""
        Analyze the technical innovation in this research paper with deep technical focus.
        
        Title: {paper_data['title']}
        Abstract: {paper_data['abstract']}
        
        Focus on:
        1. CORE TECHNICAL INNOVATION: What specific technical mechanism is introduced?
        2. METHODOLOGY: How does the algorithm/architecture work step-by-step?
        3. PERFORMANCE: What are the key quantitative results and why are they significant?
        4. IMPLEMENTATION: What would it actually take to implement this?
        5. LIMITATIONS: What are the technical limitations or failure modes?
        6. REPRODUCTION: How difficult would this be to reproduce accurately?
        
        Provide detailed technical analysis suitable for expert researchers.
        """
        
        try:
            response = await self.llm_client.generate_content_async(
                prompt,
                tools=[tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            # Extract function call result
            if response.parts and response.parts[0].function_call:
                function_call = response.parts[0].function_call
                return dict(function_call.args)
            else:
                logger.warning("No function call in technical analysis response")
                return self._fallback_analysis()
                
        except Exception as e:
            logger.error(f"Technical analysis failed: {e}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when function calling fails"""
        return {
            "technical_innovation": "Technical analysis unavailable due to processing error.",
            "methodology_breakdown": "Methodology analysis unavailable due to processing error.",
            "performance_highlights": "Performance analysis unavailable due to processing error.",
            "implementation_insights": "Implementation analysis unavailable due to processing error.",
            "limitations": "Limitations analysis unavailable due to processing error.",
            "reproduction_difficulty": "medium"
        }
    
    def get_insight_type(self) -> str:
        return "technical_analysis"
    
    def get_dependencies(self) -> List[str]:
        return ["title", "abstract"]

class ResearchContextGenerator(InsightGenerator):
    """Generates research positioning and significance insights"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def generate_insight(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate research context analysis"""
        
        research_context_function = FunctionDeclaration(
            name="analyze_research_context",
            description="Analyze how this research fits in the broader landscape",
            parameters={
                "type": "object",
                "properties": {
                    "research_context": {
                        "type": "string",
                        "description": "How this work relates to and builds upon existing research"
                    },
                    "future_implications": {
                        "type": "string",
                        "description": "What this enables for future research or applications"
                    },
                    "research_significance": {
                        "type": "string",
                        "enum": ["breakthrough", "significant", "incremental", "minor"],
                        "description": "Level of research significance"
                    },
                    "impact_score": {
                        "type": "number",
                        "minimum": 1.0,
                        "maximum": 5.0,
                        "description": "Impact potential on 1-5 scale"
                    }
                },
                "required": ["research_context", "future_implications", "research_significance", "impact_score"]
            }
        )
        
        tool = Tool(function_declarations=[research_context_function])
        
        prompt = f"""
        Analyze how this research paper fits in the broader research landscape.
        
        Title: {paper_data['title']}
        Abstract: {paper_data['abstract']}
        
        Focus on:
        1. RESEARCH POSITIONING: How does this build on existing work?
        2. FUTURE IMPLICATIONS: What new research directions does this enable?
        3. SIGNIFICANCE: Is this incremental improvement, significant advance, or breakthrough?
        4. IMPACT: Rate impact potential 1-5 based on novelty and significance
        
        Consider the work's position in the field's development trajectory.
        """
        
        try:
            response = await self.llm_client.generate_content_async(
                prompt,
                tools=[tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            if response.parts and response.parts[0].function_call:
                function_call = response.parts[0].function_call
                return dict(function_call.args)
            else:
                return self._fallback_context()
                
        except Exception as e:
            logger.error(f"Research context analysis failed: {e}")
            return self._fallback_context()
    
    def _fallback_context(self) -> Dict[str, Any]:
        return {
            "research_context": "Research context analysis unavailable due to processing error.",
            "future_implications": "Future implications analysis unavailable due to processing error.",
            "research_significance": "incremental",
            "impact_score": 3.0
        }
    
    def get_insight_type(self) -> str:
        return "research_context"
    
    def get_dependencies(self) -> List[str]:
        return ["title", "abstract"]

class PracticalAssessmentGenerator(InsightGenerator):
    """Generates practical applicability and implementation insights"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def generate_insight(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate practical assessment"""
        
        practical_assessment_function = FunctionDeclaration(
            name="assess_practical_applicability",
            description="Assess the real-world applicability and implementation feasibility",
            parameters={
                "type": "object",
                "properties": {
                    "practical_applicability": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "How useful for real-world applications"
                    },
                    "implementation_complexity": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "How difficult to implement from scratch"
                    },
                    "has_code": {
                        "type": "boolean",
                        "description": "Likelihood of code/implementation being available"
                    },
                    "difficulty_level": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                        "description": "Skill level needed to understand this"
                    },
                    "reading_time": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Realistic time to read and understand the full paper in minutes"
                    }
                },
                "required": ["practical_applicability", "implementation_complexity", "has_code", "difficulty_level", "reading_time"]
            }
        )
        
        tool = Tool(function_declarations=[practical_assessment_function])
        
        prompt = f"""
        Assess the practical applicability and implementation feasibility of this research.
        
        Title: {paper_data['title']}
        Abstract: {paper_data['abstract']}
        
        Focus on:
        1. PRACTICAL VALUE: How useful for real-world applications?
        2. IMPLEMENTATION: How difficult to implement from scratch?
        3. ACCESSIBILITY: What skill level needed to understand?
        4. RESOURCES: Realistic time to read and implement?
        5. CODE AVAILABILITY: Likelihood of implementations being available?
        
        Consider production readiness vs research prototype level.
        """
        
        try:
            response = await self.llm_client.generate_content_async(
                prompt,
                tools=[tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            if response.parts and response.parts[0].function_call:
                function_call = response.parts[0].function_call
                return dict(function_call.args)
            else:
                return self._fallback_practical()
                
        except Exception as e:
            logger.error(f"Practical assessment failed: {e}")
            return self._fallback_practical()
    
    def _fallback_practical(self) -> Dict[str, Any]:
        return {
            "practical_applicability": "medium",
            "implementation_complexity": "medium",
            "has_code": False,
            "difficulty_level": "intermediate",
            "reading_time": 15
        }
    
    def get_insight_type(self) -> str:
        return "practical_assessment"
    
    def get_dependencies(self) -> List[str]:
        return ["title", "abstract"]

class BasicSummaryGenerator(InsightGenerator):
    """Generates basic summary and novelty assessment"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def generate_insight(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic summary"""
        
        summary_function = FunctionDeclaration(
            name="generate_summary",
            description="Generate concise summary and novelty assessment",
            parameters={
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "A concise, one-paragraph summary of the paper"
                    },
                    "key_contribution": {
                        "type": "string",
                        "description": "A single sentence describing the core contribution"
                    },
                    "novelty": {
                        "type": "string",
                        "description": "A single sentence explaining what is novel about this work"
                    }
                },
                "required": ["summary", "key_contribution", "novelty"]
            }
        )
        
        tool = Tool(function_declarations=[summary_function])
        
        prompt = f"""
        Create a concise summary for busy AI researchers.
        
        Title: {paper_data['title']}
        Abstract: {paper_data['abstract']}
        
        Provide:
        1. SUMMARY: One clear paragraph explaining what this paper does
        2. KEY CONTRIBUTION: One sentence capturing the main contribution  
        3. NOVELTY: One sentence explaining what's new/different
        
        Write for expert audience who needs quick insights.
        """
        
        try:
            response = await self.llm_client.generate_content_async(
                prompt,
                tools=[tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            if response.parts and response.parts[0].function_call:
                function_call = response.parts[0].function_call
                return dict(function_call.args)
            else:
                return self._fallback_summary()
                
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return self._fallback_summary()
    
    def _fallback_summary(self) -> Dict[str, Any]:
        return {
            "summary": "Could not generate summary due to an error.",
            "key_contribution": "N/A",
            "novelty": "N/A"
        }
    
    def get_insight_type(self) -> str:
        return "basic_summary"
    
    def get_dependencies(self) -> List[str]:
        return ["title", "abstract"]

class AIAnalysisService:
    """Main AI analysis service with plugin architecture"""
    
    def __init__(self):
        # Initialize LLM clients
        self.gemini_model = genai.GenerativeModel("gemini-1.5-flash") if settings.GEMINI_API_KEY else None
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        
        # Initialize Redis for caching
        self.redis = get_redis()
        
        # Initialize insight generators
        self.insight_generators = {
            "technical_analysis": TechnicalAnalysisGenerator(self.gemini_model),
            "research_context": ResearchContextGenerator(self.gemini_model),
            "practical_assessment": PracticalAssessmentGenerator(self.gemini_model),
            "basic_summary": BasicSummaryGenerator(self.gemini_model)
        }
    
    def _get_cache_key(self, paper_id: str, analysis_type: str) -> str:
        """Generate cache key for analysis results"""
        return f"analysis:{paper_id}:{analysis_type}:v2"
    
    async def _get_cached_analysis(self, paper_id: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis result"""
        try:
            cache_key = self._get_cache_key(paper_id, analysis_type)
            cached_result = await self.redis.get(cache_key)
            
            if cached_result:
                logger.info(f"Cache HIT for {analysis_type}: {paper_id}")
                return json.loads(cached_result)
            else:
                logger.info(f"Cache MISS for {analysis_type}: {paper_id}")
                return None
                
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    async def _cache_analysis(self, paper_id: str, analysis_type: str, result: Dict[str, Any], ttl: int = 86400):
        """Cache analysis result with TTL"""
        try:
            cache_key = self._get_cache_key(paper_id, analysis_type)
            await self.redis.setex(cache_key, ttl, json.dumps(result))
            logger.info(f"Cached {analysis_type}: {paper_id}")
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    async def analyze_paper(self, paper_data: Dict[str, Any]) -> AIAnalysis:
        """Generate comprehensive analysis for a paper"""
        paper_id = paper_data.get("id", "unknown")
        
        try:
            logger.info(f"Starting comprehensive analysis for: {paper_id}")
            
            # Check if full analysis is cached
            cached_full = await self._get_cached_analysis(paper_id, "full")
            if cached_full:
                return AIAnalysis(**cached_full)
            
            # Run all analysis stages in parallel
            analysis_tasks = {}
            for insight_type, generator in self.insight_generators.items():
                # Check individual cache first
                cached_insight = await self._get_cached_analysis(paper_id, insight_type)
                if cached_insight:
                    analysis_tasks[insight_type] = cached_insight
                else:
                    analysis_tasks[insight_type] = generator.generate_insight(paper_data)
            
            # Wait for all uncached analyses to complete
            pending_tasks = {k: v for k, v in analysis_tasks.items() if not isinstance(v, dict)}
            if pending_tasks:
                completed_tasks = await asyncio.gather(*pending_tasks.values(), return_exceptions=True)
                
                # Update analysis_tasks with completed results
                for i, (insight_type, _) in enumerate(pending_tasks.items()):
                    result = completed_tasks[i]
                    if isinstance(result, Exception):
                        logger.error(f"Analysis failed for {insight_type}: {result}")
                        # Use fallback from generator
                        result = self.insight_generators[insight_type]._fallback_analysis() if hasattr(self.insight_generators[insight_type], '_fallback_analysis') else {}
                    
                    analysis_tasks[insight_type] = result
                    
                    # Cache individual result
                    await self._cache_analysis(paper_id, insight_type, result)
            
            # Combine all results into AIAnalysis
            combined_analysis = {}
            
            # Basic summary
            if "basic_summary" in analysis_tasks:
                combined_analysis.update(analysis_tasks["basic_summary"])
            
            # Technical analysis  
            if "technical_analysis" in analysis_tasks:
                combined_analysis.update(analysis_tasks["technical_analysis"])
            
            # Research context
            if "research_context" in analysis_tasks:
                combined_analysis.update(analysis_tasks["research_context"])
            
            # Practical assessment
            if "practical_assessment" in analysis_tasks:
                combined_analysis.update(analysis_tasks["practical_assessment"])
            
            # Calculate confidence score based on successful analyses
            successful_analyses = sum(1 for result in analysis_tasks.values() if isinstance(result, dict) and "error" not in result)
            confidence_score = successful_analyses / len(self.insight_generators)
            combined_analysis["confidence_score"] = confidence_score
            
            # Add metadata
            combined_analysis["analysis_version"] = "2.0"
            combined_analysis["generated_at"] = datetime.utcnow()
            
            # Create AIAnalysis object
            ai_analysis = AIAnalysis(**combined_analysis)
            
            # Cache full analysis
            await self._cache_analysis(paper_id, "full", combined_analysis)
            
            logger.info(f"Analysis completed for {paper_id} with confidence {confidence_score:.2f}")
            return ai_analysis
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed for {paper_id}: {e}")
            # Return minimal analysis
            return AIAnalysis(
                summary="Analysis failed due to processing error.",
                key_contribution="N/A",
                novelty="N/A",
                technical_innovation="Analysis unavailable.",
                methodology_breakdown="Analysis unavailable.",
                performance_highlights="Analysis unavailable.",
                implementation_insights="Analysis unavailable.",
                limitations="Analysis unavailable.",
                research_context="Analysis unavailable.",
                future_implications="Analysis unavailable.",
                research_significance=ResearchSignificance.INCREMENTAL,
                impact_score=3.0,
                practical_applicability=PracticalApplicability.MEDIUM,
                implementation_complexity=ImplementationComplexity.MEDIUM,
                has_code=False,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                reading_time=15,
                reproduction_difficulty=ReproductionDifficulty.MEDIUM,
                confidence_score=0.1
            )

# Global AI analysis service instance
ai_analysis_service = AIAnalysisService()