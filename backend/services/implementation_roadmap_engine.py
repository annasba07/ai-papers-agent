"""
Implementation Roadmap Engine for Industry Researchers
Core use case: "What's the best technique to solve my specific problem?"
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from ..core.config import settings
from .knowledge_graph import knowledge_graph
from .supabase_service import supabase_service
from .database_manager import get_redis
import json

logger = logging.getLogger(__name__)

class ProblemConstraints(BaseModel):
    """Problem constraints and requirements"""
    domain: str
    problem_type: str
    constraints: List[str]  # e.g., ["real_time", "low_memory", "privacy_preserving"]
    data_characteristics: List[str]  # e.g., ["small_dataset", "noisy_labels", "multimodal"]
    success_criteria: List[str]  # e.g., [">95% accuracy", "<100ms latency", "interpretable"]
    team_expertise: str  # "beginner", "intermediate", "advanced"
    timeline: str  # "1-2 weeks", "1-3 months", "6+ months"

class TechniqueRecommendation(BaseModel):
    """Recommended technique with implementation details"""
    technique_name: str
    description: str
    success_rate: float  # 0.0 to 1.0 based on historical performance
    implementation_complexity: str  # "low", "medium", "high"
    estimated_timeline: str
    paper_references: List[str]  # Paper IDs
    code_repositories: List[str]  # GitHub URLs
    key_advantages: List[str]
    potential_pitfalls: List[str]
    resource_requirements: Dict[str, Any]

class ImplementationPhase(BaseModel):
    """Implementation phase with specific guidance"""
    phase_number: int
    phase_name: str
    duration: str
    objectives: List[str]
    deliverables: List[str]
    key_techniques: List[str]
    potential_blockers: List[str]
    success_criteria: List[str]
    fallback_options: List[str]

class RoadmapResult(BaseModel):
    """Complete implementation roadmap"""
    problem_analysis: ProblemConstraints
    primary_recommendation: TechniqueRecommendation
    alternative_approaches: List[TechniqueRecommendation]
    implementation_phases: List[ImplementationPhase]
    overall_success_probability: float
    total_estimated_timeline: str
    resource_summary: Dict[str, Any]
    risk_assessment: List[str]
    next_immediate_steps: List[str]
    methodology_explanation: str
    analysis_timestamp: datetime

class ImplementationRoadmapEngine:
    """Engine for generating implementation roadmaps"""
    
    def __init__(self):
        self.gemini_model = genai.GenerativeModel("gemini-1.5-flash") if settings.GEMINI_API_KEY else None
        self.redis = get_redis()
    
    async def generate_implementation_roadmap(
        self, 
        problem_description: str, 
        constraints: List[str] = [],
        expertise_level: str = "intermediate",
        timeline: str = "1-3 months"
    ) -> RoadmapResult:
        """
        Main entry point for implementation roadmap generation
        
        Args:
            problem_description: Natural language description of the problem
            constraints: List of constraints (e.g., ["real_time", "privacy_preserving"])
            expertise_level: Team expertise level
            timeline: Desired timeline
            
        Returns:
            RoadmapResult with complete implementation guidance
        """
        try:
            logger.info(f"Starting roadmap generation for: {problem_description[:100]}...")
            
            # Step 1: Analyze and structure the problem
            problem_analysis = await self._analyze_problem(problem_description, constraints, expertise_level, timeline)
            
            # Step 2: Find relevant techniques using knowledge graph
            technique_candidates = await self._find_relevant_techniques(problem_analysis)
            
            # Step 3: Rank techniques by success probability
            ranked_techniques = await self._rank_techniques(problem_analysis, technique_candidates)
            
            # Step 4: Generate implementation phases
            implementation_phases = await self._generate_implementation_phases(
                problem_analysis, ranked_techniques[0] if ranked_techniques else None
            )
            
            # Step 5: Calculate overall success probability
            success_probability = await self._calculate_success_probability(
                problem_analysis, ranked_techniques, implementation_phases
            )
            
            # Step 6: Generate resource requirements summary
            resource_summary = await self._generate_resource_summary(problem_analysis, ranked_techniques)
            
            # Step 7: Risk assessment
            risk_assessment = await self._assess_risks(problem_analysis, ranked_techniques, implementation_phases)
            
            # Step 8: Immediate next steps
            next_steps = await self._generate_immediate_steps(problem_analysis, ranked_techniques[0] if ranked_techniques else None)
            
            result = RoadmapResult(
                problem_analysis=problem_analysis,
                primary_recommendation=ranked_techniques[0] if ranked_techniques else self._fallback_technique(),
                alternative_approaches=ranked_techniques[1:4] if len(ranked_techniques) > 1 else [],
                implementation_phases=implementation_phases,
                overall_success_probability=success_probability,
                total_estimated_timeline=self._calculate_total_timeline(implementation_phases),
                resource_summary=resource_summary,
                risk_assessment=risk_assessment,
                next_immediate_steps=next_steps,
                methodology_explanation=self._create_methodology_explanation(len(technique_candidates)),
                analysis_timestamp=datetime.utcnow()
            )
            
            logger.info(f"Roadmap generation completed: success_probability={success_probability:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Implementation roadmap generation failed: {e}")
            return self._fallback_roadmap(problem_description, constraints, expertise_level, timeline)
    
    async def _analyze_problem(self, description: str, constraints: List[str], expertise: str, timeline: str) -> ProblemConstraints:
        """Analyze and structure the problem description"""
        
        problem_analysis_function = FunctionDeclaration(
            name="analyze_problem_structure",
            description="Analyze and structure a technical problem description",
            parameters={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Technical domain (e.g., computer_vision, nlp, time_series, recommendation_systems)"
                    },
                    "problem_type": {
                        "type": "string",
                        "description": "Specific type of problem (e.g., classification, detection, generation, optimization)"
                    },
                    "data_characteristics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Characteristics of the data (e.g., small_dataset, high_dimensional, noisy, real_time)"
                    },
                    "success_criteria": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "Success criteria mentioned or implied (e.g., accuracy targets, speed requirements)"
                    }
                },
                "required": ["domain", "problem_type", "data_characteristics", "success_criteria"]
            }
        )
        
        tool = Tool(function_declarations=[problem_analysis_function])
        
        prompt = f"""
        Analyze this technical problem and extract key structural information:
        
        Problem Description: "{description}"
        Given Constraints: {constraints}
        Team Expertise: {expertise}
        Timeline: {timeline}
        
        Extract:
        1. DOMAIN: What technical domain is this (computer vision, NLP, etc.)?
        2. PROBLEM TYPE: What type of problem (classification, detection, etc.)?
        3. DATA CHARACTERISTICS: What can you infer about the data?
        4. SUCCESS CRITERIA: What defines success for this problem?
        
        Be specific and technical in your analysis.
        """
        
        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                tools=[tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            if response.parts and response.parts[0].function_call:
                function_call = response.parts[0].function_call
                args = dict(function_call.args)
                
                return ProblemConstraints(
                    domain=args.get("domain", "machine_learning"),
                    problem_type=args.get("problem_type", "unknown"),
                    constraints=constraints,
                    data_characteristics=args.get("data_characteristics", []),
                    success_criteria=args.get("success_criteria", []),
                    team_expertise=expertise,
                    timeline=timeline
                )
            else:
                return self._fallback_problem_analysis(description, constraints, expertise, timeline)
                
        except Exception as e:
            logger.error(f"Problem analysis failed: {e}")
            return self._fallback_problem_analysis(description, constraints, expertise, timeline)
    
    async def _find_relevant_techniques(self, problem_analysis: ProblemConstraints) -> List[Dict[str, Any]]:
        """Find relevant techniques using knowledge graph and database queries"""
        try:
            # Search for papers in the domain
            domain_papers = await supabase_service.get_papers_by_categories([problem_analysis.domain], limit=100)
            
            # Extract techniques from AI analysis
            technique_counts = {}
            paper_technique_map = {}
            
            for paper in domain_papers:
                if paper.ai_analysis:
                    # Extract techniques from analysis (this would need to be enhanced)
                    # For now, we'll simulate technique extraction
                    techniques = self._extract_techniques_from_analysis(paper.ai_analysis)
                    paper_technique_map[paper.id] = techniques
                    
                    for technique in techniques:
                        if technique not in technique_counts:
                            technique_counts[technique] = {
                                "count": 0,
                                "papers": [],
                                "avg_impact": 0,
                                "success_rate": 0.5
                            }
                        technique_counts[technique]["count"] += 1
                        technique_counts[technique]["papers"].append(paper.id)
                        
                        # Use impact score if available
                        if hasattr(paper.ai_analysis, 'impact_score'):
                            current_avg = technique_counts[technique]["avg_impact"]
                            count = technique_counts[technique]["count"]
                            new_avg = (current_avg * (count - 1) + paper.ai_analysis.impact_score) / count
                            technique_counts[technique]["avg_impact"] = new_avg
            
            # Convert to list and sort by relevance
            techniques = []
            for technique_name, data in technique_counts.items():
                if data["count"] >= 2:  # Only techniques with multiple papers
                    techniques.append({
                        "name": technique_name,
                        "paper_count": data["count"],
                        "paper_ids": data["papers"][:5],  # Top 5 papers
                        "avg_impact": data["avg_impact"],
                        "estimated_success_rate": min(data["avg_impact"] / 5.0, 1.0)
                    })
            
            # Sort by combined score (impact + popularity)
            techniques.sort(key=lambda x: x["avg_impact"] * x["paper_count"], reverse=True)
            
            logger.info(f"Found {len(techniques)} relevant techniques")
            return techniques[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"Technique finding failed: {e}")
            return []
    
    def _extract_techniques_from_analysis(self, ai_analysis) -> List[str]:
        """Extract technique names from AI analysis (simplified)"""
        # This is a simplified extraction - in practice, this would be more sophisticated
        techniques = []
        
        if hasattr(ai_analysis, 'technical_innovation'):
            text = ai_analysis.technical_innovation.lower()
            # Simple keyword extraction (would be enhanced with NLP)
            common_techniques = [
                "transformer", "attention", "cnn", "lstm", "bert", "gpt", 
                "resnet", "unet", "gan", "vae", "reinforcement learning",
                "gradient boosting", "random forest", "svm", "neural network"
            ]
            
            for technique in common_techniques:
                if technique in text:
                    techniques.append(technique.title())
        
        return techniques
    
    async def _rank_techniques(self, problem_analysis: ProblemConstraints, technique_candidates: List[Dict[str, Any]]) -> List[TechniqueRecommendation]:
        """Rank techniques by suitability for the specific problem"""
        
        ranking_function = FunctionDeclaration(
            name="rank_techniques_for_problem",
            description="Rank techniques by suitability for a specific problem",
            parameters={
                "type": "object",
                "properties": {
                    "ranked_techniques": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "technique_name": {"type": "string"},
                                "suitability_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "implementation_complexity": {"type": "string", "enum": ["low", "medium", "high"]},
                                "estimated_timeline": {"type": "string"},
                                "key_advantages": {"type": "array", "items": {"type": "string"}},
                                "potential_pitfalls": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["technique_name", "suitability_score", "implementation_complexity", "estimated_timeline", "key_advantages", "potential_pitfalls"]
                        }
                    }
                },
                "required": ["ranked_techniques"]
            }
        )
        
        tool = Tool(function_declarations=[ranking_function])
        
        technique_names = [t["name"] for t in technique_candidates[:8]]  # Limit for LLM context
        
        prompt = f"""
        Rank these techniques for solving this specific problem:
        
        Problem: {problem_analysis.problem_type} in {problem_analysis.domain}
        Constraints: {problem_analysis.constraints}
        Data Characteristics: {problem_analysis.data_characteristics}
        Success Criteria: {problem_analysis.success_criteria}
        Team Expertise: {problem_analysis.team_expertise}
        Timeline: {problem_analysis.timeline}
        
        Available Techniques: {technique_names}
        
        For each technique, assess:
        1. Suitability score (0-1) for this specific problem
        2. Implementation complexity given team expertise
        3. Realistic timeline estimate
        4. Key advantages for this use case
        5. Potential pitfalls or challenges
        
        Rank by overall suitability for the problem.
        """
        
        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                tools=[tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            if response.parts and response.parts[0].function_call:
                function_call = response.parts[0].function_call
                ranked_data = function_call.args.get("ranked_techniques", [])
                
                recommendations = []
                for i, tech_data in enumerate(ranked_data):
                    # Find original technique data
                    original_tech = next((t for t in technique_candidates if t["name"] == tech_data["technique_name"]), {})
                    
                    recommendation = TechniqueRecommendation(
                        technique_name=tech_data["technique_name"],
                        description=f"Technique for {problem_analysis.problem_type} with {original_tech.get('paper_count', 0)} supporting papers",
                        success_rate=tech_data["suitability_score"],
                        implementation_complexity=tech_data["implementation_complexity"],
                        estimated_timeline=tech_data["estimated_timeline"],
                        paper_references=original_tech.get("paper_ids", []),
                        code_repositories=[],  # Would be populated from real data
                        key_advantages=tech_data["key_advantages"],
                        potential_pitfalls=tech_data["potential_pitfalls"],
                        resource_requirements=self._estimate_resources(tech_data["implementation_complexity"])
                    )
                    recommendations.append(recommendation)
                
                logger.info(f"Ranked {len(recommendations)} techniques")
                return recommendations
            else:
                return self._fallback_techniques(technique_candidates)
                
        except Exception as e:
            logger.error(f"Technique ranking failed: {e}")
            return self._fallback_techniques(technique_candidates)
    
    async def _generate_implementation_phases(self, problem_analysis: ProblemConstraints, primary_technique: Optional[TechniqueRecommendation]) -> List[ImplementationPhase]:
        """Generate step-by-step implementation phases"""
        
        if not primary_technique:
            return [self._fallback_phase()]
        
        phases_function = FunctionDeclaration(
            name="generate_implementation_phases",
            description="Generate step-by-step implementation phases",
            parameters={
                "type": "object",
                "properties": {
                    "phases": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "phase_name": {"type": "string"},
                                "duration": {"type": "string"},
                                "objectives": {"type": "array", "items": {"type": "string"}},
                                "deliverables": {"type": "array", "items": {"type": "string"}},
                                "key_techniques": {"type": "array", "items": {"type": "string"}},
                                "potential_blockers": {"type": "array", "items": {"type": "string"}},
                                "success_criteria": {"type": "array", "items": {"type": "string"}},
                                "fallback_options": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["phase_name", "duration", "objectives", "deliverables", "key_techniques", "potential_blockers", "success_criteria", "fallback_options"]
                        }
                    }
                },
                "required": ["phases"]
            }
        )
        
        tool = Tool(function_declarations=[phases_function])
        
        prompt = f"""
        Create a detailed implementation roadmap for this project:
        
        Problem: {problem_analysis.problem_type} in {problem_analysis.domain}
        Primary Technique: {primary_technique.technique_name}
        Team Expertise: {problem_analysis.team_expertise}
        Timeline: {problem_analysis.timeline}
        Constraints: {problem_analysis.constraints}
        
        Create 3-5 implementation phases with:
        1. Phase name and duration
        2. Clear objectives for each phase
        3. Specific deliverables
        4. Key techniques/methods to implement
        5. Potential blockers or challenges
        6. Success criteria for the phase
        7. Fallback options if the phase fails
        
        Make phases realistic and buildable, progressing from basic to advanced.
        """
        
        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                tools=[tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            if response.parts and response.parts[0].function_call:
                function_call = response.parts[0].function_call
                phases_data = function_call.args.get("phases", [])
                
                phases = []
                for i, phase_data in enumerate(phases_data):
                    phase = ImplementationPhase(
                        phase_number=i + 1,
                        phase_name=phase_data["phase_name"],
                        duration=phase_data["duration"],
                        objectives=phase_data["objectives"],
                        deliverables=phase_data["deliverables"],
                        key_techniques=phase_data["key_techniques"],
                        potential_blockers=phase_data["potential_blockers"],
                        success_criteria=phase_data["success_criteria"],
                        fallback_options=phase_data["fallback_options"]
                    )
                    phases.append(phase)
                
                logger.info(f"Generated {len(phases)} implementation phases")
                return phases
            else:
                return [self._fallback_phase()]
                
        except Exception as e:
            logger.error(f"Phase generation failed: {e}")
            return [self._fallback_phase()]
    
    async def _calculate_success_probability(
        self, 
        problem_analysis: ProblemConstraints,
        techniques: List[TechniqueRecommendation],
        phases: List[ImplementationPhase]
    ) -> float:
        """Calculate overall success probability"""
        try:
            base_probability = 0.6  # Base success rate
            
            # Technique quality adjustment
            if techniques:
                primary_success_rate = techniques[0].success_rate
                base_probability = (base_probability + primary_success_rate) / 2
            
            # Team expertise adjustment
            expertise_multipliers = {
                "beginner": 0.8,
                "intermediate": 1.0,
                "advanced": 1.2
            }
            base_probability *= expertise_multipliers.get(problem_analysis.team_expertise, 1.0)
            
            # Timeline realism adjustment
            if "weeks" in problem_analysis.timeline and len(phases) > 3:
                base_probability *= 0.8  # Ambitious timeline
            elif "months" in problem_analysis.timeline and len(phases) <= 3:
                base_probability *= 1.1  # Realistic timeline
            
            # Constraint complexity penalty
            if len(problem_analysis.constraints) > 3:
                base_probability *= 0.9
            
            return max(0.1, min(0.95, base_probability))
            
        except Exception as e:
            logger.error(f"Success probability calculation failed: {e}")
            return 0.6
    
    def _estimate_resources(self, complexity: str) -> Dict[str, Any]:
        """Estimate resource requirements based on complexity"""
        resource_templates = {
            "low": {
                "team_size": "1-2 developers",
                "compute_requirements": "Standard laptop/workstation",
                "data_requirements": "Small to medium datasets",
                "timeline": "1-4 weeks"
            },
            "medium": {
                "team_size": "2-3 developers + 1 ML engineer",
                "compute_requirements": "GPU workstation or cloud compute",
                "data_requirements": "Medium to large datasets",
                "timeline": "1-3 months"
            },
            "high": {
                "team_size": "3-5 developers + 2 ML engineers",
                "compute_requirements": "Multiple GPUs or cluster",
                "data_requirements": "Large datasets + infrastructure",
                "timeline": "3-6 months"
            }
        }
        
        return resource_templates.get(complexity, resource_templates["medium"])
    
    # Additional helper methods...
    
    def _fallback_roadmap(self, description: str, constraints: List[str], expertise: str, timeline: str) -> RoadmapResult:
        """Generate fallback roadmap when analysis fails"""
        return RoadmapResult(
            problem_analysis=ProblemConstraints(
                domain="machine_learning",
                problem_type="unknown",
                constraints=constraints,
                data_characteristics=[],
                success_criteria=[],
                team_expertise=expertise,
                timeline=timeline
            ),
            primary_recommendation=self._fallback_technique(),
            alternative_approaches=[],
            implementation_phases=[self._fallback_phase()],
            overall_success_probability=0.5,
            total_estimated_timeline="Unknown",
            resource_summary={"error": "Analysis failed"},
            risk_assessment=["Manual analysis recommended due to technical error"],
            next_immediate_steps=["Conduct manual literature review", "Consult with domain experts"],
            methodology_explanation="Analysis failed due to technical error. Manual review recommended.",
            analysis_timestamp=datetime.utcnow()
        )
    
    def _fallback_technique(self) -> TechniqueRecommendation:
        """Fallback technique recommendation"""
        return TechniqueRecommendation(
            technique_name="Manual Analysis Required",
            description="Technical analysis failed. Manual review recommended.",
            success_rate=0.5,
            implementation_complexity="medium",
            estimated_timeline="Unknown",
            paper_references=[],
            code_repositories=[],
            key_advantages=["Requires human expertise"],
            potential_pitfalls=["Time consuming"],
            resource_requirements={}
        )
    
    def _fallback_phase(self) -> ImplementationPhase:
        """Fallback implementation phase"""
        return ImplementationPhase(
            phase_number=1,
            phase_name="Manual Planning Phase",
            duration="1-2 weeks",
            objectives=["Conduct manual literature review", "Define technical approach"],
            deliverables=["Research summary", "Technical specification"],
            key_techniques=["Literature review", "Expert consultation"],
            potential_blockers=["Complex domain", "Limited expertise"],
            success_criteria=["Clear technical direction identified"],
            fallback_options=["Hire domain expert", "Use existing solutions"]
        )
    
    # Additional implementation methods would go here...

# Global implementation roadmap engine instance
implementation_roadmap_engine = ImplementationRoadmapEngine()