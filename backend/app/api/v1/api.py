"""
API v1 router configuration
"""
from fastapi import APIRouter
from app.api.v1.endpoints import papers, knowledge_graph, enrichment, trends, agent_memory, atlas_db, ingestion, discovery

api_router = APIRouter()
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(knowledge_graph.router, prefix="/knowledge-graph", tags=["knowledge-graph"])
api_router.include_router(enrichment.router, tags=["enrichment"])
api_router.include_router(trends.router, tags=["trends"])
api_router.include_router(agent_memory.router, tags=["agent-memory"])
api_router.include_router(atlas_db.router, tags=["atlas-database"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(discovery.router, tags=["discovery"])