"""
Enhanced AI Analysis Service with Full Paper Content Support
Provides deeper insights by analyzing complete paper content including methodology, results, and limitations
"""
import logging
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from ..core.config import settings
from ..models.paper import (
    AIAnalysis, ExtractedSection, ExtractedFigure, 
    ReproducibilityAssessment, ResultsValidation,
    ResearchSignificance, DifficultyLevel, PracticalApplicability, 
    ImplementationComplexity, ReproductionDifficulty
)
from .database_manager import get_redis

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class EnhancedAIAnalysisService:
    """Enhanced AI analysis service with full paper content support"""
    
    def __init__(self):
        self.redis = get_redis()
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
        
    async def analyze_paper_comprehensive(self, paper_data: Dict[str, Any]) -> AIAnalysis:
        """
        Comprehensive paper analysis using full content
        
        Args:
            paper_data: Complete paper data including full text and sections
            
        Returns:
            Enhanced AIAnalysis with detailed insights
        """
        try:
            logger.info(f"Starting comprehensive analysis for paper {paper_data['id']}")
            
            # Check if we have full paper content
            has_full_content = (
                paper_data.get('full_text') or 
                paper_data.get('extracted_sections')
            )
            
            if has_full_content:
                return await self._analyze_with_full_content(paper_data)
            else:
                return await self._analyze_with_abstract_only(paper_data)
                
        except Exception as e:
            logger.error(f"Comprehensive analysis failed for {paper_data['id']}: {e}")
            raise
    
    async def _analyze_with_full_content(self, paper_data: Dict[str, Any]) -> AIAnalysis:
        """Analysis with full paper content"""
        
        # Extract key sections
        methodology_content = self._extract_methodology_content(paper_data)
        results_content = self._extract_results_content(paper_data)
        limitations_content = self._extract_limitations_content(paper_data)
        
        # Run parallel analyses
        basic_analysis_task = self._generate_basic_analysis(paper_data)
        reproducibility_task = self._assess_reproducibility(paper_data, methodology_content)
        results_validation_task = self._validate_results(paper_data, results_content)
        implementation_task = self._assess_implementation_complexity(paper_data, methodology_content)
        
        # Wait for all analyses to complete
        basic_analysis, reproducibility, results_validation, implementation_assessment = await asyncio.gather(
            basic_analysis_task,
            reproducibility_task,
            results_validation_task,
            implementation_task
        )
        
        # Combine all insights
        return AIAnalysis(
            # Basic analysis
            summary=basic_analysis["summary"],
            key_contribution=basic_analysis["key_contribution"],
            novelty=basic_analysis["novelty"],
            
            # Technical analysis
            technical_innovation=basic_analysis["technical_innovation"],
            methodology_breakdown=basic_analysis["methodology_breakdown"],
            performance_highlights=basic_analysis["performance_highlights"],
            implementation_insights=implementation_assessment["implementation_insights"],
            limitations=basic_analysis["limitations"],
            
            # Research context
            research_context=basic_analysis["research_context"],
            future_implications=basic_analysis["future_implications"],
            research_significance=ResearchSignificance(basic_analysis["research_significance"]),
            impact_score=basic_analysis["impact_score"],
            
            # Practical assessment
            practical_applicability=PracticalApplicability(basic_analysis["practical_applicability"]),
            implementation_complexity=ImplementationComplexity(implementation_assessment["complexity_level"]),
            has_code=basic_analysis["has_code"],
            difficulty_level=DifficultyLevel(basic_analysis["difficulty_level"]),
            reading_time=basic_analysis["reading_time"],
            reproduction_difficulty=ReproductionDifficulty(reproducibility["overall_difficulty"]),
            
            # Enhanced analysis from full paper
            reproducibility_assessment=reproducibility["assessment"],
            results_validation=results_validation,
            computational_requirements=implementation_assessment["computational_requirements"],
            hidden_limitations=self._extract_hidden_limitations(limitations_content),
            real_world_applicability=implementation_assessment["real_world_score"],
            
            # Metadata
            confidence_score=0.9,  # Higher confidence with full content
            analysis_version="2.1",
            generated_at=datetime.utcnow(),
            full_text_analyzed=True
        )
    
    async def _analyze_with_abstract_only(self, paper_data: Dict[str, Any]) -> AIAnalysis:
        """Fallback analysis with only abstract"""
        
        basic_analysis = await self._generate_basic_analysis(paper_data)
        
        return AIAnalysis(
            # Basic analysis
            summary=basic_analysis["summary"],
            key_contribution=basic_analysis["key_contribution"],
            novelty=basic_analysis["novelty"],
            
            # Technical analysis
            technical_innovation=basic_analysis["technical_innovation"],
            methodology_breakdown=basic_analysis["methodology_breakdown"],
            performance_highlights=basic_analysis["performance_highlights"],
            implementation_insights=basic_analysis["implementation_insights"],
            limitations=basic_analysis["limitations"],
            
            # Research context
            research_context=basic_analysis["research_context"],
            future_implications=basic_analysis["future_implications"],
            research_significance=ResearchSignificance(basic_analysis["research_significance"]),
            impact_score=basic_analysis["impact_score"],
            
            # Practical assessment
            practical_applicability=PracticalApplicability(basic_analysis["practical_applicability"]),
            implementation_complexity=ImplementationComplexity(basic_analysis["implementation_complexity"]),
            has_code=basic_analysis["has_code"],
            difficulty_level=DifficultyLevel(basic_analysis["difficulty_level"]),
            reading_time=basic_analysis["reading_time"],
            reproduction_difficulty=ReproductionDifficulty(basic_analysis["reproduction_difficulty"]),
            
            # Limited analysis without full content
            real_world_applicability=0.5,  # Default uncertainty
            
            # Metadata
            confidence_score=0.6,  # Lower confidence without full content
            analysis_version="2.1",
            generated_at=datetime.utcnow(),
            full_text_analyzed=False
        )
    
    async def _generate_basic_analysis(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic analysis using LLM function calling"""
        
        basic_analysis_function = FunctionDeclaration(
            name="analyze_research_paper",
            description="Comprehensive analysis of a research paper",
            parameters={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Executive summary of the paper"},
                    "key_contribution": {"type": "string", "description": "Main contribution or innovation"},
                    "novelty": {"type": "string", "description": "What makes this work novel"},
                    "technical_innovation": {"type": "string", "description": "Technical approach explanation"},
                    "methodology_breakdown": {"type": "string", "description": "How the method works"},
                    "performance_highlights": {"type": "string", "description": "Key results and achievements"},
                    "implementation_insights": {"type": "string", "description": "Implementation considerations"},
                    "limitations": {"type": "string", "description": "Stated limitations"},
                    "research_context": {"type": "string", "description": "How this fits in the research landscape"},
                    "future_implications": {"type": "string", "description": "Future research directions"},
                    "research_significance": {"type": "string", "enum": ["breakthrough", "significant", "incremental", "minor"]},
                    "impact_score": {"type": "number", "minimum": 1, "maximum": 5},
                    "practical_applicability": {"type": "string", "enum": ["high", "medium", "low"]},
                    "implementation_complexity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "has_code": {"type": "boolean"},
                    "difficulty_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
                    "reading_time": {"type": "integer", "minimum": 1},
                    "reproduction_difficulty": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["summary", "key_contribution", "novelty", "technical_innovation", "methodology_breakdown", "performance_highlights", "implementation_insights", "limitations", "research_context", "future_implications", "research_significance", "impact_score", "practical_applicability", "implementation_complexity", "has_code", "difficulty_level", "reading_time", "reproduction_difficulty"]
            }
        )
        
        tool = Tool(function_declarations=[basic_analysis_function])
        
        # Build content for analysis
        content = f"""
        Title: {paper_data['title']}
        Abstract: {paper_data['abstract']}
        Categories: {', '.join(paper_data.get('categories', []))}
        """
        
        # Add full text if available
        if paper_data.get('full_text'):
            content += f"\n\nFull Text (first 8000 chars): {paper_data['full_text'][:8000]}"
        
        # Add extracted sections if available
        if paper_data.get('extracted_sections'):
            for section_name, section in paper_data['extracted_sections'].items():
                content += f"\n\n{section_name.upper()} SECTION:\n{section.content[:2000]}"
        
        prompt = f"""
        Analyze this research paper comprehensively. Focus on technical depth, practical applicability, and research significance.
        
        {content}
        
        Provide detailed analysis using the function call.
        """
        
        response = await self.gemini_model.generate_content_async(
            prompt,
            tools=[tool],
            tool_config={'function_calling_config': {'mode': 'ANY'}}
        )
        
        # Extract function call result
        if response.candidates[0].content.parts[0].function_call:
            result = dict(response.candidates[0].content.parts[0].function_call.args)
            logger.info(f"✅ Generated basic analysis with {len(result)} insights")
            return result
        else:
            raise Exception("No function call in LLM response")
    
    async def _assess_reproducibility(self, paper_data: Dict[str, Any], methodology_content: str) -> Dict[str, Any]:
        """Assess reproducibility based on methodology section"""
        
        reproducibility_function = FunctionDeclaration(
            name="assess_reproducibility",
            description="Assess the reproducibility of research based on methodology details",
            parameters={
                "type": "object",
                "properties": {
                    "reproducibility_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "code_availability": {"type": "boolean"},
                    "data_availability": {"type": "boolean"},
                    "hyperparameter_completeness": {"type": "number", "minimum": 0, "maximum": 1},
                    "implementation_details_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "experimental_setup_clarity": {"type": "number", "minimum": 0, "maximum": 1},
                    "missing_details": {"type": "array", "items": {"type": "string"}},
                    "overall_difficulty": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["reproducibility_score", "code_availability", "data_availability", "hyperparameter_completeness", "implementation_details_score", "experimental_setup_clarity", "missing_details", "overall_difficulty"]
            }
        )
        
        tool = Tool(function_declarations=[reproducibility_function])
        
        prompt = f"""
        Assess the reproducibility of this research paper based on the methodology and experimental details.
        
        Title: {paper_data['title']}
        Methodology Content: {methodology_content}
        
        Look for:
        - Code availability mentions
        - Dataset details and availability
        - Hyperparameter specifications
        - Implementation details
        - Experimental setup clarity
        - Missing critical details
        
        Rate each aspect from 0-1 and provide overall difficulty assessment.
        """
        
        response = await self.gemini_model.generate_content_async(
            prompt,
            tools=[tool],
            tool_config={'function_calling_config': {'mode': 'ANY'}}
        )
        
        if response.candidates[0].content.parts[0].function_call:
            result = dict(response.candidates[0].content.parts[0].function_call.args)
            
            # Create ReproducibilityAssessment object
            assessment = ReproducibilityAssessment(
                reproducibility_score=result["reproducibility_score"],
                code_availability=result["code_availability"],
                data_availability=result["data_availability"],
                hyperparameter_completeness=result["hyperparameter_completeness"],
                implementation_details_score=result["implementation_details_score"],
                experimental_setup_clarity=result["experimental_setup_clarity"],
                missing_details=result["missing_details"]
            )
            
            return {
                "assessment": assessment,
                "overall_difficulty": result["overall_difficulty"]
            }
        else:
            # Return default assessment
            return {
                "assessment": ReproducibilityAssessment(
                    reproducibility_score=0.5,
                    missing_details=["Full methodology not available"]
                ),
                "overall_difficulty": "medium"
            }
    
    async def _validate_results(self, paper_data: Dict[str, Any], results_content: str) -> ResultsValidation:
        """Validate results quality and reliability"""
        
        results_function = FunctionDeclaration(
            name="validate_results",
            description="Validate the quality and reliability of research results",
            parameters={
                "type": "object",
                "properties": {
                    "statistical_significance": {"type": "boolean"},
                    "baseline_quality": {"type": "string", "enum": ["weak", "moderate", "strong"]},
                    "evaluation_completeness": {"type": "number", "minimum": 0, "maximum": 1},
                    "failure_case_analysis": {"type": "boolean"},
                    "computational_cost_reported": {"type": "boolean"},
                    "comparison_fairness": {"type": "number", "minimum": 0, "maximum": 1},
                    "result_reliability_score": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["statistical_significance", "baseline_quality", "evaluation_completeness", "failure_case_analysis", "computational_cost_reported", "comparison_fairness", "result_reliability_score"]
            }
        )
        
        tool = Tool(function_declarations=[results_function])
        
        prompt = f"""
        Validate the quality and reliability of results in this research paper.
        
        Title: {paper_data['title']}
        Results Content: {results_content}
        
        Assess:
        - Statistical significance of results
        - Quality of baseline comparisons
        - Completeness of evaluation
        - Analysis of failure cases
        - Computational cost reporting
        - Fairness of comparisons
        - Overall reliability
        """
        
        response = await self.gemini_model.generate_content_async(
            prompt,
            tools=[tool],
            tool_config={'function_calling_config': {'mode': 'ANY'}}
        )
        
        if response.candidates[0].content.parts[0].function_call:
            result = dict(response.candidates[0].content.parts[0].function_call.args)
            
            return ResultsValidation(
                statistical_significance=result["statistical_significance"],
                baseline_quality=result["baseline_quality"],
                evaluation_completeness=result["evaluation_completeness"],
                failure_case_analysis=result["failure_case_analysis"],
                computational_cost_reported=result["computational_cost_reported"],
                comparison_fairness=result["comparison_fairness"],
                result_reliability_score=result["result_reliability_score"]
            )
        else:
            return ResultsValidation(
                statistical_significance=False,
                baseline_quality="moderate",
                evaluation_completeness=0.5,
                failure_case_analysis=False,
                computational_cost_reported=False,
                comparison_fairness=0.5,
                result_reliability_score=0.5
            )
    
    async def _assess_implementation_complexity(self, paper_data: Dict[str, Any], methodology_content: str) -> Dict[str, Any]:
        """Assess implementation complexity and computational requirements"""
        
        implementation_function = FunctionDeclaration(
            name="assess_implementation",
            description="Assess implementation complexity and computational requirements",
            parameters={
                "type": "object",
                "properties": {
                    "complexity_level": {"type": "string", "enum": ["low", "medium", "high"]},
                    "implementation_insights": {"type": "string"},
                    "computational_requirements": {
                        "type": "object",
                        "properties": {
                            "gpu_required": {"type": "boolean"},
                            "memory_gb": {"type": "number"},
                            "training_time": {"type": "string"},
                            "inference_speed": {"type": "string"}
                        }
                    },
                    "real_world_score": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["complexity_level", "implementation_insights", "computational_requirements", "real_world_score"]
            }
        )
        
        tool = Tool(function_declarations=[implementation_function])
        
        prompt = f"""
        Assess the implementation complexity and computational requirements of this research.
        
        Title: {paper_data['title']}
        Methodology: {methodology_content}
        
        Consider:
        - Implementation difficulty
        - Computational requirements
        - Real-world applicability
        - Practical deployment challenges
        """
        
        response = await self.gemini_model.generate_content_async(
            prompt,
            tools=[tool],
            tool_config={'function_calling_config': {'mode': 'ANY'}}
        )
        
        if response.candidates[0].content.parts[0].function_call:
            result = dict(response.candidates[0].content.parts[0].function_call.args)
            return result
        else:
            return {
                "complexity_level": "medium",
                "implementation_insights": "Implementation details not fully available",
                "computational_requirements": {
                    "gpu_required": True,
                    "memory_gb": 16,
                    "training_time": "unknown",
                    "inference_speed": "unknown"
                },
                "real_world_score": 0.5
            }
    
    def _extract_methodology_content(self, paper_data: Dict[str, Any]) -> str:
        """Extract methodology section content"""
        sections = paper_data.get('extracted_sections', {})
        
        # Look for methodology-related sections
        methodology_keys = ['methodology', 'method', 'approach', 'methods']
        for key in methodology_keys:
            if key in sections:
                return sections[key].content
        
        # Fallback to full text search
        full_text = paper_data.get('full_text', '')
        if full_text:
            # Simple extraction of methodology section
            lines = full_text.split('\n')
            methodology_lines = []
            in_methodology = False
            
            for line in lines:
                line_lower = line.lower().strip()
                if any(keyword in line_lower for keyword in ['methodology', 'method', 'approach']):
                    in_methodology = True
                elif in_methodology and any(keyword in line_lower for keyword in ['results', 'experiment', 'evaluation']):
                    break
                elif in_methodology:
                    methodology_lines.append(line)
            
            return '\n'.join(methodology_lines)
        
        return ""
    
    def _extract_results_content(self, paper_data: Dict[str, Any]) -> str:
        """Extract results section content"""
        sections = paper_data.get('extracted_sections', {})
        
        # Look for results-related sections
        results_keys = ['results', 'experiments', 'evaluation', 'experimental_results']
        for key in results_keys:
            if key in sections:
                return sections[key].content
        
        return ""
    
    def _extract_limitations_content(self, paper_data: Dict[str, Any]) -> str:
        """Extract limitations section content"""
        sections = paper_data.get('extracted_sections', {})
        
        # Look for limitations-related sections
        limitations_keys = ['limitations', 'discussion', 'conclusion']
        for key in limitations_keys:
            if key in sections:
                return sections[key].content
        
        return ""
    
    def _extract_hidden_limitations(self, limitations_content: str) -> List[str]:
        """Extract hidden limitations from text"""
        # Simple keyword-based extraction
        hidden_limitations = []
        
        if "computational cost" in limitations_content.lower():
            hidden_limitations.append("High computational requirements")
        
        if "memory" in limitations_content.lower():
            hidden_limitations.append("Memory constraints")
        
        if "dataset" in limitations_content.lower() and "small" in limitations_content.lower():
            hidden_limitations.append("Limited dataset size")
        
        if "generalization" in limitations_content.lower():
            hidden_limitations.append("Generalization concerns")
        
        return hidden_limitations

# Global enhanced AI analysis service instance
enhanced_ai_analysis_service = EnhancedAIAnalysisService()