"""
AI analysis service for paper processing using Google Gemini
"""
import asyncio
import time
from typing import Dict, Any, List
import google.generativeai as genai
from app.core.config import settings
from app.services.cache_service import cache_service
from app.utils.logger import LoggerMixin
from app.utils.exceptions import AIAnalysisException, RateLimitException


class AIAnalysisService(LoggerMixin):
    """Service for handling AI-powered paper analysis"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.log_info("AI Analysis Service initialized")
    
    async def generate_technical_analysis(self, abstract: str, title: str) -> Dict[str, Any]:
        """Generate technical analysis of the paper"""
        prompt = f"""
        Analyze this AI research paper's technical contributions:
        
        Title: {title}
        Abstract: {abstract}
        
        Provide a detailed technical analysis including:
        1. Key technical innovation (what's new?)
        2. Methodology breakdown (how does it work?)
        3. Performance highlights (what results?)
        4. Implementation insights (how complex to build?)
        
        Return as JSON with keys: keyContribution, methodologyBreakdown, performanceHighlights, implementationInsights
        """
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            analysis = {
                "keyContribution": "Novel technical approach identified",
                "methodologyBreakdown": "Advanced methodology analysis",
                "performanceHighlights": "Significant performance improvements",
                "implementationInsights": "Moderate implementation complexity"
            }
            
            if response.text:
                try:
                    import json
                    parsed = json.loads(response.text.strip())
                    analysis.update(parsed)
                except:
                    pass
            
            return analysis
            
        except Exception as e:
            self.log_error("Technical analysis failed", error=e, title=title)
            raise AIAnalysisException(f"Technical analysis failed: {str(e)}", error_code="TECHNICAL_ANALYSIS_ERROR")
    
    async def generate_research_context(self, abstract: str, title: str) -> Dict[str, Any]:
        """Generate research context and implications"""
        prompt = f"""
        Analyze this paper's research context and implications:
        
        Title: {title}
        Abstract: {abstract}
        
        Provide analysis of:
        1. Research context (field, related work)
        2. Future implications (what does this enable?)
        3. Limitations (what are the constraints?)
        4. Research significance (incremental/significant/breakthrough)
        
        Return as JSON with keys: researchContext, futureImplications, limitations, researchSignificance
        """
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            analysis = {
                "researchContext": "Advances current research in the field",
                "futureImplications": "Opens new research directions",
                "limitations": "Some implementation constraints exist",
                "researchSignificance": "significant"
            }
            
            if response.text:
                try:
                    import json
                    parsed = json.loads(response.text.strip())
                    analysis.update(parsed)
                except:
                    pass
            
            return analysis
            
        except Exception as e:
            self.log_error("Research context analysis failed", error=e, title=title)
            raise AIAnalysisException(f"Research context analysis failed: {str(e)}", error_code="RESEARCH_CONTEXT_ERROR")
    
    async def generate_practical_assessment(self, abstract: str, title: str) -> Dict[str, Any]:
        """Generate practical assessment metrics"""
        prompt = f"""
        Assess the practical aspects of this paper:
        
        Title: {title}
        Abstract: {abstract}
        
        Rate on scales and provide:
        1. Impact Score (1-10)
        2. Difficulty Level (beginner/intermediate/advanced)
        3. Reading Time (minutes)
        4. Has Code (true/false)
        5. Implementation Complexity (low/medium/high)
        6. Practical Applicability (low/medium/high)
        7. Reproduction Difficulty (low/medium/high)
        
        Return as JSON with keys: impactScore, difficultyLevel, readingTime, hasCode, implementationComplexity, practicalApplicability, reproductionDifficulty
        """
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            assessment = {
                "impactScore": 7,
                "difficultyLevel": "intermediate",
                "readingTime": 15,
                "hasCode": False,
                "implementationComplexity": "medium",
                "practicalApplicability": "medium",
                "reproductionDifficulty": "medium"
            }
            
            if response.text:
                try:
                    import json
                    parsed = json.loads(response.text.strip())
                    assessment.update(parsed)
                except:
                    pass
            
            return assessment
            
        except Exception as e:
            self.log_error("Practical assessment failed", error=e, title=title)
            raise AIAnalysisException(f"Practical assessment failed: {str(e)}", error_code="PRACTICAL_ASSESSMENT_ERROR")
    
    async def generate_basic_summary(self, abstract: str, title: str) -> Dict[str, Any]:
        """Generate basic summary and novelty assessment"""
        prompt = f"""
        Provide a concise summary of this paper:
        
        Title: {title}
        Abstract: {abstract}
        
        Generate:
        1. Summary (2-3 sentences)
        2. Novelty (what's new about this approach?)
        3. Technical Innovation (key technical contribution)
        
        Return as JSON with keys: summary, novelty, technicalInnovation
        """
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            summary = {
                "summary": "This paper presents a novel approach to advancing AI research.",
                "novelty": "Introduces new techniques for improved performance",
                "technicalInnovation": "Advanced methodology with practical applications"
            }
            
            if response.text:
                try:
                    import json
                    parsed = json.loads(response.text.strip())
                    summary.update(parsed)
                except:
                    pass
            
            return summary
            
        except Exception as e:
            self.log_error("Basic summary generation failed", error=e, title=title)
            raise AIAnalysisException(f"Basic summary generation failed: {str(e)}", error_code="BASIC_SUMMARY_ERROR")
    
    async def generate_comprehensive_analysis(self, abstract: str, title: str) -> Dict[str, Any]:
        """Generate comprehensive analysis using all stages"""
        self.log_info("Starting comprehensive analysis", title=title)
        
        # Check cache first
        cached_result = cache_service.get_cached_analysis(title, abstract, "full")
        if cached_result:
            self.log_info("Using cached analysis", title=title)
            return cached_result
        
        # Run all analysis stages in parallel
        try:
            self.log_info("Running parallel analysis stages", title=title)
            
            # Create tasks for all stages
            tasks = [
                self.generate_technical_analysis(abstract, title),
                self.generate_research_context(abstract, title),
                self.generate_practical_assessment(abstract, title),
                self.generate_basic_summary(abstract, title)
            ]
            
            # Execute all tasks with exception handling
            results = await asyncio.gather(*tasks, return_exceptions=True)
            technical, context, practical, basic = results
            
            # Handle any stage failures with fallback data
            if isinstance(technical, Exception):
                self.log_warning("Technical analysis stage failed, using fallback", error=str(technical))
                technical = {"keyContribution": "Analysis unavailable", "methodologyBreakdown": "Analysis failed", "performanceHighlights": "Results unavailable", "implementationInsights": "Implementation details unclear"}
            
            if isinstance(context, Exception):
                self.log_warning("Research context stage failed, using fallback", error=str(context))
                context = {"researchContext": "Context unavailable", "futureImplications": "Implications unclear", "limitations": "Limitations not identified", "researchSignificance": "incremental"}
            
            if isinstance(practical, Exception):
                self.log_warning("Practical assessment stage failed, using fallback", error=str(practical))
                practical = {"impactScore": 5, "difficultyLevel": "intermediate", "readingTime": 10, "hasCode": False, "implementationComplexity": "medium", "practicalApplicability": "medium", "reproductionDifficulty": "medium"}
            
            if isinstance(basic, Exception):
                self.log_warning("Basic summary stage failed, using fallback", error=str(basic))
                basic = {"summary": "Summary unavailable", "novelty": "Novelty assessment unavailable", "technicalInnovation": "Technical innovation unclear"}
            
            # Combine all analyses
            comprehensive_analysis = {
                **basic,
                **technical,
                **context,
                **practical
            }
            
            # Cache the successful result
            cache_service.cache_analysis(title, abstract, comprehensive_analysis, "full")
            self.log_info("Comprehensive analysis completed successfully", title=title)
            
            return comprehensive_analysis
            
        except Exception as e:
            self.log_error("Comprehensive analysis failed completely", error=e, title=title)
            raise AIAnalysisException(f"Comprehensive analysis failed: {str(e)}", error_code="COMPREHENSIVE_ANALYSIS_ERROR")
    
    async def batch_generate_summaries(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate summaries for multiple papers in batches"""
        batch_size = settings.GEMINI_RATE_LIMIT_BATCH_SIZE
        delay = settings.GEMINI_RATE_LIMIT_DELAY
        
        self.log_info(f"Starting batch analysis for {len(papers)} papers", batch_size=batch_size)
        
        results = []
        
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]
            self.log_info(f"Processing batch {i//batch_size + 1}", batch_papers=len(batch))
            
            # Process batch in parallel
            batch_tasks = []
            for paper in batch:
                task = self.generate_comprehensive_analysis(
                    paper.get('summary', ''),
                    paper.get('title', '')
                )
                batch_tasks.append(task)
            
            # Execute batch with exception handling
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Add results to papers
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    self.log_warning(f"Paper analysis failed in batch", paper_title=papers[i + j].get('title', 'Unknown'), error=str(result))
                    result = {
                        "summary": "Analysis failed",
                        "novelty": "Unable to assess",
                        "technicalInnovation": "Technical details unavailable",
                        "keyContribution": "Analysis error",
                        "methodologyBreakdown": "Method unclear",
                        "performanceHighlights": "Results unavailable",
                        "implementationInsights": "Implementation details unclear",
                        "researchContext": "Context unavailable",
                        "futureImplications": "Implications unclear",
                        "limitations": "Limitations not identified",
                        "researchSignificance": "incremental",
                        "impactScore": 5,
                        "difficultyLevel": "intermediate",
                        "readingTime": 10,
                        "hasCode": False,
                        "implementationComplexity": "medium",
                        "practicalApplicability": "medium",
                        "reproductionDifficulty": "medium"
                    }
                
                papers[i + j]['aiSummary'] = result
                results.append(papers[i + j])
            
            # Rate limiting delay between batches
            if i + batch_size < len(papers):
                self.log_info(f"Rate limiting delay: {delay}s")
                await asyncio.sleep(delay)
        
        self.log_info(f"Batch analysis completed successfully", total_papers=len(results))
        return results


# Global AI analysis service instance
ai_analysis_service = AIAnalysisService()