"""
API v1 router configuration
"""
from fastapi import APIRouter
from app.api.v1.endpoints import papers, knowledge_graph

api_router = APIRouter()
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(knowledge_graph.router, tags=["knowledge-graph"])