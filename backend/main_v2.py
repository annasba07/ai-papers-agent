"""
AI Paper Digest v2.0 - Main FastAPI Application
Uses managed services architecture with Supabase, Neo4j AuraDB, Pinecone, and Upstash Redis
"""
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Internal imports
from core.config import settings, validate_required_services, get_database_config
from services.database_manager import db_manager
from services.supabase_service import supabase_service
from services.knowledge_graph import knowledge_graph
from models.paper import Paper, PaperCreate, AIAnalysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting AI Paper Digest v2.0...")
    
    try:
        # Validate configuration
        validate_required_services()
        logger.info("✅ Configuration validated")
        
        # Initialize database schemas
        await knowledge_graph.initialize_schema()
        logger.info("✅ Knowledge graph schema initialized")
        
        # Health check all services
        health_status = await db_manager.health_check()
        logger.info(f"📊 Service health: {health_status}")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down AI Paper Digest...")
        db_manager.close_connections()
        logger.info("✅ Connections closed")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Intelligent research decision-making platform for AI researchers",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    services: Dict[str, bool]
    configuration: Dict[str, bool]

class PaperSearchRequest(BaseModel):
    """Paper search request"""
    query: str = ""
    categories: List[str] = []
    days: int = 7
    limit: int = 20
    offset: int = 0

class ResearchViabilityRequest(BaseModel):
    """Research viability check request"""
    research_description: str
    domain: str = "machine_learning"
    timeframe_months: int = 12

class ImplementationRoadmapRequest(BaseModel):
    """Implementation roadmap request"""
    problem_description: str
    constraints: List[str] = []
    expertise_level: str = "intermediate"

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}",
        "documentation": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check for all services"""
    try:
        # Check service connections
        service_health = await db_manager.health_check()
        
        # Check configuration
        config_status = get_database_config()
        
        # Determine overall status
        all_services_healthy = all(service_health.values())
        status = "healthy" if all_services_healthy else "degraded"
        
        return HealthResponse(
            status=status,
            version=settings.PROJECT_VERSION,
            services=service_health,
            configuration=config_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Paper endpoints
@app.get(f"{settings.API_V1_STR}/papers", response_model=List[Paper])
async def get_papers(
    query: str = Query("", description="Search query"),
    categories: str = Query("", description="Comma-separated categories"),
    days: int = Query(7, description="Days to look back"),
    limit: int = Query(20, description="Number of papers to return"),
    offset: int = Query(0, description="Pagination offset")
):
    """Get papers with optional filtering"""
    try:
        # Parse categories
        category_list = [cat.strip() for cat in categories.split(",") if cat.strip()]
        
        # Calculate date range
        from datetime import datetime, timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Search papers
        if query:
            papers = await supabase_service.search_papers(query, limit, offset)
        elif category_list:
            papers = await supabase_service.get_papers_by_categories(category_list, limit, offset)
        else:
            papers = await supabase_service.get_papers_by_date_range(start_date, end_date, limit, offset)
        
        return papers
        
    except Exception as e:
        logger.error(f"Error getting papers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve papers")

@app.get(f"{settings.API_V1_STR}/papers/{{paper_id}}", response_model=Paper)
async def get_paper(paper_id: str):
    """Get a specific paper by ID"""
    try:
        paper = await supabase_service.get_paper(paper_id)
        
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        return paper
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve paper")

@app.post(f"{settings.API_V1_STR}/papers", response_model=Dict[str, str])
async def create_paper(
    paper_data: PaperCreate,
    background_tasks: BackgroundTasks
):
    """Create a new paper and queue for analysis"""
    try:
        # Create paper in Supabase
        paper_id = await supabase_service.create_paper(paper_data)
        
        if not paper_id:
            raise HTTPException(status_code=400, detail="Failed to create paper")
        
        # Create paper node in knowledge graph
        background_tasks.add_task(
            knowledge_graph.create_paper_node,
            paper_data.model_dump()
        )
        
        # Queue for AI analysis
        await supabase_service.add_to_processing_queue(
            paper_id, 
            "analysis", 
            priority=7
        )
        
        return {"message": "Paper created successfully", "id": paper_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating paper: {e}")
        raise HTTPException(status_code=500, detail="Failed to create paper")

# Research Intelligence endpoints
@app.post(f"{settings.API_V1_STR}/research/viability-check")
async def check_research_viability(request: ResearchViabilityRequest):
    """Academic researcher use case: Check research direction viability"""
    try:
        # Import here to avoid circular imports
        from services.research_viability_engine import research_viability_engine
        
        # Generate viability analysis
        result = await research_viability_engine.analyze_research_viability(
            research_description=request.research_description,
            domain=request.domain,
            timeframe_months=request.timeframe_months
        )
        
        # Convert to API response format
        return {
            "viability_score": result.viability_score,
            "confidence": result.confidence,
            "field_momentum": result.field_momentum,
            "competitive_threats": [
                {
                    "paper_id": threat.paper_id,
                    "title": threat.title,
                    "threat_level": threat.threat_level,
                    "published_date": threat.published_date.isoformat(),
                    "competing_techniques": threat.competing_techniques,
                    "advantage_description": threat.advantage_description
                }
                for threat in result.competitive_threats
            ],
            "opportunity_gaps": [
                {
                    "opportunity_type": gap.opportunity_type,
                    "description": gap.description,
                    "technique_combinations": gap.technique_combinations,
                    "potential_score": gap.potential_score,
                    "reasoning": gap.reasoning
                }
                for gap in result.opportunity_gaps
            ],
            "next_steps": result.next_steps,
            "methodology_explanation": result.methodology_explanation,
            "papers_analyzed": result.papers_analyzed,
            "analysis_timestamp": result.analysis_timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in viability check: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze research viability")

@app.post(f"{settings.API_V1_STR}/research/implementation-roadmap")
async def generate_implementation_roadmap(request: ImplementationRoadmapRequest):
    """Industry researcher use case: Generate implementation roadmap"""
    try:
        # Import here to avoid circular imports
        from services.implementation_roadmap_engine import implementation_roadmap_engine
        
        # Generate implementation roadmap
        result = await implementation_roadmap_engine.generate_implementation_roadmap(
            problem_description=request.problem_description,
            constraints=request.constraints,
            expertise_level=request.expertise_level
        )
        
        # Convert to API response format
        return {
            "problem_analysis": {
                "domain": result.problem_analysis.domain,
                "problem_type": result.problem_analysis.problem_type,
                "constraints": result.problem_analysis.constraints,
                "data_characteristics": result.problem_analysis.data_characteristics,
                "success_criteria": result.problem_analysis.success_criteria,
                "team_expertise": result.problem_analysis.team_expertise,
                "timeline": result.problem_analysis.timeline
            },
            "primary_recommendation": {
                "technique_name": result.primary_recommendation.technique_name,
                "description": result.primary_recommendation.description,
                "success_rate": result.primary_recommendation.success_rate,
                "implementation_complexity": result.primary_recommendation.implementation_complexity,
                "estimated_timeline": result.primary_recommendation.estimated_timeline,
                "paper_references": result.primary_recommendation.paper_references,
                "code_repositories": result.primary_recommendation.code_repositories,
                "key_advantages": result.primary_recommendation.key_advantages,
                "potential_pitfalls": result.primary_recommendation.potential_pitfalls,
                "resource_requirements": result.primary_recommendation.resource_requirements
            },
            "alternative_approaches": [
                {
                    "technique_name": alt.technique_name,
                    "success_rate": alt.success_rate,
                    "implementation_complexity": alt.implementation_complexity,
                    "estimated_timeline": alt.estimated_timeline
                }
                for alt in result.alternative_approaches
            ],
            "implementation_phases": [
                {
                    "phase_number": phase.phase_number,
                    "phase_name": phase.phase_name,
                    "duration": phase.duration,
                    "objectives": phase.objectives,
                    "deliverables": phase.deliverables,
                    "key_techniques": phase.key_techniques,
                    "potential_blockers": phase.potential_blockers,
                    "success_criteria": phase.success_criteria,
                    "fallback_options": phase.fallback_options
                }
                for phase in result.implementation_phases
            ],
            "overall_success_probability": result.overall_success_probability,
            "total_estimated_timeline": result.total_estimated_timeline,
            "resource_summary": result.resource_summary,
            "risk_assessment": result.risk_assessment,
            "next_immediate_steps": result.next_immediate_steps,
            "methodology_explanation": result.methodology_explanation,
            "analysis_timestamp": result.analysis_timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating roadmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate implementation roadmap")

# Analysis endpoints
@app.get(f"{settings.API_V1_STR}/trends/{{topic}}")
async def get_topic_trends(
    topic: str,
    timeframe_months: int = Query(12, description="Timeframe in months")
):
    """Get trend analysis for a specific topic"""
    try:
        trends = await knowledge_graph.get_topic_evolution(topic, timeframe_months)
        
        return {
            "topic": topic,
            "timeframe_months": timeframe_months,
            "trends": trends,
            "generated_at": "2024-01-15T10:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting trends for {topic}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trends")

# Administrative endpoints for backfill
@app.post(f"{settings.API_V1_STR}/admin/start-backfill")
async def start_historical_backfill(background_tasks: BackgroundTasks):
    """Start historical backfill process (admin only)"""
    try:
        # Import here to avoid circular imports
        from services.historical_backfill_service import historical_backfill_service
        
        # Check if backfill is already running
        status = await historical_backfill_service.get_backfill_status()
        if status.get("is_running"):
            raise HTTPException(status_code=400, detail="Backfill already in progress")
        
        # Start backfill in background
        background_tasks.add_task(historical_backfill_service.run_complete_backfill)
        
        # Get cost estimates
        estimates = await historical_backfill_service.estimate_backfill_cost()
        
        return {
            "message": "Historical backfill started",
            "estimates": estimates,
            "warning": "This is a long-running process that will take several weeks"
        }
        
    except Exception as e:
        logger.error(f"Error starting backfill: {e}")
        raise HTTPException(status_code=500, detail="Failed to start backfill")

@app.get(f"{settings.API_V1_STR}/admin/backfill-status")
async def get_backfill_status():
    """Get status of historical backfill process"""
    try:
        from services.historical_backfill_service import historical_backfill_service
        
        status = await historical_backfill_service.get_backfill_status()
        estimates = await historical_backfill_service.estimate_backfill_cost()
        
        return {
            "status": status,
            "estimates": estimates
        }
        
    except Exception as e:
        logger.error(f"Error getting backfill status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get backfill status")

@app.post(f"{settings.API_V1_STR}/admin/ingest-recent")
async def ingest_recent_papers(days: int = 7):
    """Manually trigger ingestion of recent papers"""
    try:
        from services.arxiv_ingestion_service import arxiv_ingestion_service
        
        # Fetch and ingest recent papers
        papers = await arxiv_ingestion_service.fetch_recent_papers(days=days, max_results=500)
        stats = await arxiv_ingestion_service.ingest_and_process_papers(papers)
        
        return {
            "message": f"Ingested papers from last {days} days",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error ingesting recent papers: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest recent papers")

@app.post(f"{settings.API_V1_STR}/admin/process-paper-full")
async def process_paper_full(paper_id: str, background_tasks: BackgroundTasks):
    """Trigger full paper processing pipeline (PDF extraction + enhanced analysis)"""
    try:
        # Verify paper exists
        paper = await supabase_service.get_paper(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Queue PDF extraction first
        await supabase_service.add_to_processing_queue(
            paper_id=paper_id,
            task_type="pdf_extraction",
            priority=8
        )
        
        # Queue enhanced analysis after PDF extraction
        await supabase_service.add_to_processing_queue(
            paper_id=paper_id,
            task_type="enhanced_analysis",
            priority=7
        )
        
        # Queue vector embedding
        await supabase_service.add_to_processing_queue(
            paper_id=paper_id,
            task_type="vector_embedding",
            priority=6
        )
        
        return {
            "message": "Full paper processing queued",
            "paper_id": paper_id,
            "tasks": ["pdf_extraction", "enhanced_analysis", "vector_embedding"]
        }
        
    except Exception as e:
        logger.error(f"Error queuing full paper processing: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue processing")

@app.get(f"{settings.API_V1_STR}/admin/pdf-extraction-stats")
async def get_pdf_extraction_stats():
    """Get PDF extraction system statistics"""
    try:
        from services.pdf_extraction_service import pdf_extraction_service
        
        stats = await pdf_extraction_service.get_extraction_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting PDF extraction stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get extraction stats")

# Background processing endpoints (for webhooks)
@app.post(f"{settings.API_V1_STR}/webhooks/process-paper")
async def process_paper_webhook(request: Dict[str, Any]):
    """Webhook endpoint for background paper processing"""
    try:
        paper_id = request.get("paper_id")
        task_type = request.get("task_type", "analysis")
        
        if not paper_id:
            raise HTTPException(status_code=400, detail="paper_id required")
        
        # Get paper data
        paper = await supabase_service.get_paper(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Process based on task_type
        if task_type == "analysis":
            # Import here to avoid circular imports
            from services.ai_analysis_service import ai_analysis_service
            from models.paper import PaperUpdate
            
            # Generate AI analysis
            paper_data = {
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": [author.model_dump() for author in paper.authors],
                "published_date": paper.published_date,
                "categories": paper.categories
            }
            
            ai_analysis = await ai_analysis_service.analyze_paper(paper_data)
            
            # Update paper with analysis
            update_data = PaperUpdate(
                ai_analysis=ai_analysis,
                last_analyzed=datetime.utcnow()
            )
            
            success = await supabase_service.update_paper(paper_id, update_data)
            
            if success:
                # Create knowledge graph relationships
                await knowledge_graph.create_paper_node(paper_data)
                await knowledge_graph.create_author_relationships(
                    paper_id, 
                    [{"name": author.name, "affiliation": author.affiliation} for author in paper.authors]
                )
                
                logger.info(f"Successfully processed paper {paper_id}")
                return {"status": "completed", "paper_id": paper_id, "confidence": ai_analysis.confidence_score}
            else:
                logger.error(f"Failed to update paper {paper_id}")
                return {"status": "failed", "paper_id": paper_id, "error": "Database update failed"}
        
        elif task_type == "pdf_extraction":
            # Import here to avoid circular imports
            from services.pdf_extraction_service import pdf_extraction_service
            from models.paper import PaperUpdate
            
            # Extract PDF content
            if paper.pdf_url:
                extraction_result = await pdf_extraction_service.process_paper_pdf(paper_id, paper.pdf_url)
                
                if "error" not in extraction_result:
                    # Update paper with extracted content
                    update_data = PaperUpdate(
                        full_text=extraction_result["full_text"],
                        extracted_sections=extraction_result["sections"],
                        extracted_figures=extraction_result["figures"],
                        full_text_processed=True
                    )
                    
                    success = await supabase_service.update_paper(paper_id, update_data)
                    
                    if success:
                        logger.info(f"Successfully extracted PDF content for {paper_id}")
                        return {"status": "completed", "paper_id": paper_id, "stats": extraction_result["processing_stats"]}
                    else:
                        return {"status": "failed", "paper_id": paper_id, "error": "Database update failed"}
                else:
                    return {"status": "failed", "paper_id": paper_id, "error": extraction_result["error"]}
            else:
                return {"status": "failed", "paper_id": paper_id, "error": "No PDF URL available"}
        
        elif task_type == "enhanced_analysis":
            # Import here to avoid circular imports
            from services.enhanced_ai_analysis_service import enhanced_ai_analysis_service
            from models.paper import PaperUpdate
            
            # Prepare comprehensive paper data
            paper_data = {
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": [author.model_dump() for author in paper.authors],
                "published_date": paper.published_date,
                "categories": paper.categories,
                "full_text": paper.full_text,
                "extracted_sections": paper.extracted_sections,
                "extracted_figures": paper.extracted_figures
            }
            
            # Generate enhanced analysis
            ai_analysis = await enhanced_ai_analysis_service.analyze_paper_comprehensive(paper_data)
            
            # Update paper with analysis
            update_data = PaperUpdate(
                ai_analysis=ai_analysis,
                last_analyzed=datetime.utcnow()
            )
            
            success = await supabase_service.update_paper(paper_id, update_data)
            
            if success:
                logger.info(f"Successfully completed enhanced analysis for {paper_id}")
                return {"status": "completed", "paper_id": paper_id, "confidence": ai_analysis.confidence_score}
            else:
                return {"status": "failed", "paper_id": paper_id, "error": "Database update failed"}
        
        elif task_type == "vector_embedding":
            # Import here to avoid circular imports
            from services.vector_search_service import vector_search_service
            from models.paper import PaperUpdate
            
            # Generate vector embedding
            paper_data = {
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": [author.model_dump() for author in paper.authors],
                "published_date": paper.published_date,
                "categories": paper.categories
            }
            
            vector_id = await vector_search_service.create_paper_embedding(paper_data)
            
            if vector_id:
                # Update paper with vector ID
                update_data = PaperUpdate(vector_id=vector_id)
                success = await supabase_service.update_paper(paper_id, update_data)
                
                if success:
                    logger.info(f"Successfully created vector embedding for {paper_id}")
                    return {"status": "completed", "paper_id": paper_id, "vector_id": vector_id}
                else:
                    return {"status": "failed", "paper_id": paper_id, "error": "Database update failed"}
            else:
                return {"status": "failed", "paper_id": paper_id, "error": "Vector embedding generation failed"}
        
        else:
            logger.warning(f"Unknown task type: {task_type}")
            return {"status": "failed", "paper_id": paper_id, "error": f"Unknown task type: {task_type}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in webhook processing: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )