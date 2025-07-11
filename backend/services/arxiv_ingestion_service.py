"""
arXiv Paper Ingestion Service
Handles fetching, parsing, and initial processing of papers from arXiv API
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

import httpx
import xmltodict

from ..core.config import settings
from ..models.paper import PaperCreate, Author
from .supabase_service import supabase_service
from .database_manager import get_redis

logger = logging.getLogger(__name__)

class ArxivIngestionService:
    """Service for ingesting papers from arXiv"""
    
    def __init__(self):
        self.base_url = settings.ARXIV_API_BASE_URL
        self.redis = get_redis()
        # Focused AI/ML/Robotics categories only
        self.ai_ml_categories = {
            # Core AI/ML
            "cs.AI": "Artificial Intelligence",
            "cs.LG": "Machine Learning", 
            "cs.CV": "Computer Vision and Pattern Recognition",
            "cs.CL": "Computation and Language (NLP)",
            "cs.NE": "Neural and Evolutionary Computing",
            
            # AI/ML/Robotics adjacent
            "stat.ML": "Machine Learning (Statistics)",
            "cs.RO": "Robotics",  # Modern robotics is AI/ML heavy
            "cs.IR": "Information Retrieval",  # Modern IR uses ML
        }
        
        # AI/ML/Robotics keywords for additional filtering
        self.ai_ml_keywords = {
            "neural", "deep learning", "machine learning", "artificial intelligence",
            "transformer", "attention", "CNN", "RNN", "LSTM", "GAN", "VAE",
            "reinforcement learning", "supervised learning", "unsupervised learning",
            "computer vision", "natural language processing", "NLP", "CV",
            "classification", "regression", "clustering", "embedding", "feature",
            "model", "algorithm", "training", "inference", "prediction",
            "optimization", "gradient", "backpropagation", "neural network",
            "robotics", "robot", "autonomous", "navigation", "manipulation",
            "motion planning", "SLAM", "localization", "sensor fusion",
            "robotic arm", "mobile robot", "humanoid", "drone", "UAV"
        }
    
    async def fetch_recent_papers(self, days: int = 1, max_results: int = 100) -> List[PaperCreate]:
        """
        Fetch recent papers from arXiv
        
        Args:
            days: Number of days back to fetch
            max_results: Maximum papers to fetch
            
        Returns:
            List of PaperCreate objects
        """
        try:
            logger.info(f"Fetching papers from last {days} days, max {max_results}")
            
            # Build search query for recent papers
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Create category filter for AI/ML only
            category_query = " OR ".join([f"cat:{cat}" for cat in self.ai_ml_categories.keys()])
            
            # arXiv API query
            search_query = f"({category_query}) AND submittedDate:[{start_date.strftime('%Y%m%d')}* TO {end_date.strftime('%Y%m%d')}*]"
            
            params = {
                "search_query": search_query,
                "sortBy": "submittedDate",
                "sortOrder": "descending", 
                "max_results": max_results
            }
            
            # Fetch from arXiv API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
            
            # Parse XML response
            papers = await self._parse_arxiv_response(response.text)
            
            logger.info(f"Successfully fetched {len(papers)} papers from arXiv")
            return papers
            
        except Exception as e:
            logger.error(f"Failed to fetch papers from arXiv: {e}")
            return []
    
    async def fetch_papers_by_query(self, query: str, max_results: int = 50) -> List[PaperCreate]:
        """
        Fetch papers by search query
        
        Args:
            query: Search query string
            max_results: Maximum papers to fetch
            
        Returns:
            List of PaperCreate objects
        """
        try:
            logger.info(f"Searching arXiv for: {query}")
            
            params = {
                "search_query": query,
                "sortBy": "relevance",
                "sortOrder": "descending",
                "max_results": max_results
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
            
            papers = await self._parse_arxiv_response(response.text)
            
            logger.info(f"Found {len(papers)} papers for query: {query}")
            return papers
            
        except Exception as e:
            logger.error(f"Failed to search arXiv: {e}")
            return []
    
    async def fetch_papers_by_categories(self, categories: List[str], days: int = 7, max_results: int = 100) -> List[PaperCreate]:
        """
        Fetch papers by specific categories
        
        Args:
            categories: List of arXiv categories
            days: Number of days back
            max_results: Maximum papers to fetch
            
        Returns:
            List of PaperCreate objects
        """
        try:
            # Validate categories
            valid_categories = [cat for cat in categories if cat in self.ai_ml_categories]
            if not valid_categories:
                logger.warning(f"No valid categories provided: {categories}")
                return []
            
            logger.info(f"Fetching papers for categories: {valid_categories}")
            
            # Build category query
            if len(valid_categories) == 1:
                category_query = f"cat:{valid_categories[0]}"
            else:
                category_query = " OR ".join([f"cat:{cat}" for cat in valid_categories])
            
            # Add date filter if specified
            if days > 0:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=days)
                date_filter = f" AND submittedDate:[{start_date.strftime('%Y%m%d')}* TO {end_date.strftime('%Y%m%d')}*]"
                search_query = f"({category_query}){date_filter}"
            else:
                search_query = f"({category_query})"
            
            params = {
                "search_query": search_query,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": max_results
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
            
            papers = await self._parse_arxiv_response(response.text)
            
            logger.info(f"Fetched {len(papers)} papers for categories {valid_categories}")
            return papers
            
        except Exception as e:
            logger.error(f"Failed to fetch papers by categories: {e}")
            return []
    
    async def _parse_arxiv_response(self, xml_text: str) -> List[PaperCreate]:
        """Parse arXiv API XML response into PaperCreate objects"""
        try:
            # Parse XML to dict
            parsed = xmltodict.parse(xml_text)
            feed = parsed.get("feed", {})
            entries = feed.get("entry", [])
            
            # Handle single entry case
            if not isinstance(entries, list):
                entries = [entries] if entries else []
            
            papers = []
            for entry in entries:
                try:
                    paper = await self._parse_entry(entry)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Failed to parse entry: {e}")
                    continue
            
            return papers
            
        except Exception as e:
            logger.error(f"Failed to parse arXiv response: {e}")
            return []
    
    async def _parse_entry(self, entry: Dict[str, Any]) -> Optional[PaperCreate]:
        """Parse a single arXiv entry into PaperCreate object"""
        try:
            # Extract basic info
            arxiv_id = entry["id"].split("/")[-1]  # Extract ID from URL
            title = entry["title"].strip()
            
            # Clean up title (remove newlines and extra spaces)
            title = " ".join(title.split())
            
            # Extract authors
            authors_data = entry.get("author", [])
            if not isinstance(authors_data, list):
                authors_data = [authors_data]
            
            authors = []
            for author_data in authors_data:
                if isinstance(author_data, dict):
                    name = author_data.get("name", "Unknown")
                    # Extract affiliation if available
                    affiliation = None
                    if "arxiv:affiliation" in author_data:
                        affiliation = author_data["arxiv:affiliation"]
                    
                    authors.append(Author(name=name, affiliation=affiliation))
                else:
                    # Handle simple string author
                    authors.append(Author(name=str(author_data)))
            
            # Extract dates
            published_str = entry.get("published", "")
            if published_str:
                published_date = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
            else:
                published_date = datetime.utcnow()
            
            # Extract abstract
            abstract = entry.get("summary", "").strip()
            abstract = " ".join(abstract.split())  # Clean whitespace
            
            # Extract categories
            category_data = entry.get("category", [])
            if not isinstance(category_data, list):
                category_data = [category_data]
            
            categories = []
            for cat_data in category_data:
                if isinstance(cat_data, dict):
                    categories.append(cat_data.get("@term", ""))
                else:
                    categories.append(str(cat_data))
            
            # Filter to only include our target AI/ML categories
            categories = [cat for cat in categories if cat in self.ai_ml_categories]
            
            # Additional AI/ML/Robotics relevance check
            if not self._is_ai_ml_relevant(title, abstract):
                logger.debug(f"Paper {arxiv_id} not AI/ML/Robotics relevant, skipping")
                return None
            
            # Extract URLs
            links = entry.get("link", [])
            if not isinstance(links, list):
                links = [links]
            
            arxiv_url = ""
            pdf_url = ""
            
            for link in links:
                if isinstance(link, dict):
                    href = link.get("@href", "")
                    link_type = link.get("@type", "")
                    title_attr = link.get("@title", "")
                    
                    if "abs" in href:
                        arxiv_url = href
                    elif "pdf" in href or link_type == "application/pdf":
                        pdf_url = href
            
            # Validate required fields
            if not arxiv_id or not title or not abstract or not categories:
                logger.warning(f"Missing required fields for paper: {arxiv_id}")
                return None
            
            # Create PaperCreate object
            paper = PaperCreate(
                id=arxiv_id,
                title=title,
                authors=authors,
                published_date=published_date,
                abstract=abstract,
                categories=categories,
                arxiv_url=arxiv_url,
                pdf_url=pdf_url
            )
            
            return paper
            
        except Exception as e:
            logger.error(f"Failed to parse entry: {e}")
            return None
    
    def _is_ai_ml_relevant(self, title: str, abstract: str) -> bool:
        """
        Check if paper is truly AI/ML/Robotics relevant based on content
        
        Args:
            title: Paper title
            abstract: Paper abstract
            
        Returns:
            True if paper is AI/ML/Robotics relevant
        """
        try:
            # Combine title and abstract for analysis
            content = f"{title} {abstract}".lower()
            
            # Count AI/ML/Robotics keyword matches
            keyword_matches = sum(1 for keyword in self.ai_ml_keywords if keyword in content)
            
            # Relevance thresholds
            if keyword_matches >= 3:
                return True  # Strong AI/ML/Robotics relevance
            elif keyword_matches >= 1:
                # Check for strong AI/ML/Robotics indicators
                strong_indicators = [
                    "neural network", "deep learning", "machine learning", 
                    "artificial intelligence", "transformer", "CNN", "RNN",
                    "supervised learning", "unsupervised learning", "reinforcement learning",
                    "autonomous robot", "robotic system", "robot learning"
                ]
                return any(indicator in content for indicator in strong_indicators)
            else:
                # Check for domain-specific AI/ML/Robotics applications
                application_indicators = [
                    "computer vision", "natural language processing", "speech recognition",
                    "image classification", "object detection", "language model",
                    "recommendation system", "anomaly detection", "predictive model",
                    "autonomous navigation", "robotic control", "motion planning",
                    "robot learning", "human-robot interaction", "robotic perception"
                ]
                return any(indicator in content for indicator in application_indicators)
                
        except Exception as e:
            logger.warning(f"Relevance check failed: {e}")
            return True  # Default to including if check fails
    
    async def ingest_and_process_papers(self, papers: List[PaperCreate]) -> Dict[str, int]:
        """
        Ingest papers into database and queue for processing
        
        Args:
            papers: List of papers to ingest
            
        Returns:
            Dictionary with ingestion statistics
        """
        stats = {
            "total": len(papers),
            "created": 0,
            "skipped": 0,
            "failed": 0,
            "queued_for_analysis": 0
        }
        
        for paper in papers:
            try:
                # Check if paper already exists
                existing_paper = await supabase_service.get_paper(paper.id)
                
                if existing_paper:
                    stats["skipped"] += 1
                    logger.debug(f"Paper {paper.id} already exists, skipping")
                    continue
                
                # Create paper in database
                created_id = await supabase_service.create_paper(paper)
                
                if created_id:
                    stats["created"] += 1
                    
                    # Queue for AI analysis (high priority for new papers)
                    queued = await supabase_service.add_to_processing_queue(
                        paper_id=created_id,
                        task_type="analysis",
                        priority=8  # High priority for new papers
                    )
                    
                    if queued:
                        stats["queued_for_analysis"] += 1
                    
                    logger.info(f"Successfully ingested paper: {paper.id} - {paper.title[:50]}...")
                else:
                    stats["failed"] += 1
                    logger.error(f"Failed to create paper: {paper.id}")
                    
            except Exception as e:
                stats["failed"] += 1
                logger.error(f"Failed to ingest paper {paper.id}: {e}")
        
        logger.info(f"Ingestion complete: {stats}")
        return stats
    
    async def run_daily_ingestion(self) -> Dict[str, int]:
        """Run daily paper ingestion process"""
        try:
            logger.info("Starting daily paper ingestion...")
            
            # Fetch papers from yesterday and today
            papers = await self.fetch_recent_papers(days=2, max_results=200)
            
            if not papers:
                logger.warning("No papers fetched during daily ingestion")
                return {"total": 0, "created": 0, "skipped": 0, "failed": 0, "queued_for_analysis": 0}
            
            # Ingest and process papers
            stats = await self.ingest_and_process_papers(papers)
            
            # Cache the last ingestion time
            await self.redis.set("last_ingestion_time", datetime.utcnow().isoformat())
            
            logger.info(f"Daily ingestion completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Daily ingestion failed: {e}")
            return {"total": 0, "created": 0, "skipped": 0, "failed": 1, "queued_for_analysis": 0}
    
    async def get_ingestion_status(self) -> Dict[str, Any]:
        """Get status of paper ingestion system"""
        try:
            # Get last ingestion time
            last_ingestion = await self.redis.get("last_ingestion_time")
            
            # Get pending queue items
            pending_analysis = await supabase_service.get_next_queue_item("analysis")
            
            # Get papers needing analysis
            papers_needing_analysis = await supabase_service.get_papers_needing_analysis(limit=1)
            
            return {
                "last_ingestion": last_ingestion,
                "papers_pending_analysis": len(papers_needing_analysis),
                "queue_has_pending": pending_analysis is not None,
                "system_status": "healthy" if last_ingestion else "not_initialized"
            }
            
        except Exception as e:
            logger.error(f"Failed to get ingestion status: {e}")
            return {
                "last_ingestion": None,
                "papers_pending_analysis": -1,
                "queue_has_pending": False,
                "system_status": "error"
            }

# Global arXiv ingestion service instance
arxiv_ingestion_service = ArxivIngestionService()