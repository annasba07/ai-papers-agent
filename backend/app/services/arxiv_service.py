"""
arXiv API service for fetching research papers
"""
import feedparser
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import quote_plus
from app.core.config import settings
from app.utils.logger import LoggerMixin
from app.utils.exceptions import ArxivAPIException


class ArxivService(LoggerMixin):
    """Service for interacting with arXiv API"""
    
    def __init__(self):
        self.base_url = settings.ARXIV_API_BASE_URL
        self.max_results = settings.ARXIV_MAX_RESULTS
        self.log_info("arXiv service initialized")
    
    async def search_papers(self, query: str, max_results: int | None = None) -> List[Dict[str, Any]]:
        """Search for papers on arXiv, supporting pagination for large result sets."""
        target_total = max_results if (max_results and max_results > 0) else None
        batch_size = self.max_results
        encoded_query = quote_plus(query)

        collected: List[Dict[str, Any]] = []
        start = 0

        self.log_info("Searching arXiv papers", query=query, max_results=target_total)

        try:
            while True:
                if target_total is not None and len(collected) >= target_total:
                    break

                remaining = None if target_total is None else target_total - len(collected)
                current_batch = batch_size if remaining is None else min(batch_size, remaining)

                search_url = (
                    f"{self.base_url}?search_query={encoded_query}&start={start}"
                    f"&max_results={current_batch}&sortBy=submittedDate&sortOrder=descending"
                )

                feed = await asyncio.to_thread(feedparser.parse, search_url)
                entries = feed.entries or []

                if not entries:
                    if start == 0:
                        self.log_warning("No papers found for query", query=query)
                    break

                for entry in entries:
                    collected.append(
                        {
                            "id": entry.id.split("/")[-1],
                            "title": entry.title,
                            "authors": [author.name for author in entry.authors],
                            "summary": entry.summary,
                            "published": datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ"),
                            "link": entry.link,
                            "category": entry.tags[0].term if entry.tags else "Unknown",
                        }
                    )

                self.log_debug(
                    "Fetched arXiv batch",
                    query=query,
                    batch_size=len(entries),
                    start=start,
                    collected=len(collected),
                )

                if len(entries) < current_batch:
                    # No more results beyond this point
                    break

                start += current_batch

            self.log_info("Successfully retrieved papers", found_papers=len(collected), query=query)
            return collected

        except Exception as e:
            self.log_error("arXiv search failed", error=e, query=query)
            raise ArxivAPIException(f"arXiv search failed: {str(e)}", error_code="ARXIV_SEARCH_ERROR")
    
    async def get_recent_papers(self, category: str = "cs.AI", max_results: int = None) -> List[Dict[str, Any]]:
        """Get recent papers from a specific category"""
        if max_results is None:
            max_results = self.max_results
        
        self.log_info("Fetching recent papers", category=category, max_results=max_results)
        query = f"cat:{category}"
        return await self.search_papers(query, max_results)
    
    async def get_paper_by_id(self, arxiv_id: str) -> Dict[str, Any]:
        """Get a specific paper by arXiv ID"""
        search_url = f"{self.base_url}?id_list={arxiv_id}"
        
        self.log_info("Fetching paper by ID", arxiv_id=arxiv_id)
        
        try:
            feed = await asyncio.to_thread(feedparser.parse, search_url)
            
            if feed.entries:
                entry = feed.entries[0]
                paper = {
                    'id': entry.id.split('/')[-1],
                    'title': entry.title,
                    'authors': [author.name for author in entry.authors],
                    'summary': entry.summary,
                    'published': datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ'),
                    'link': entry.link,
                    'category': entry.tags[0].term if entry.tags else 'Unknown'
                }
                self.log_info("Successfully retrieved paper", arxiv_id=arxiv_id, title=paper['title'])
                return paper
            
            self.log_warning("Paper not found", arxiv_id=arxiv_id)
            return None
            
        except Exception as e:
            self.log_error("Paper fetch failed", error=e, arxiv_id=arxiv_id)
            raise ArxivAPIException(f"Paper fetch failed: {str(e)}", error_code="ARXIV_FETCH_ERROR")


# Global arXiv service instance
arxiv_service = ArxivService()
