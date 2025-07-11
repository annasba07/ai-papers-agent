"""
Historical Backfill Service for arXiv Papers
Handles one-time ingestion of historical papers with intelligent prioritization
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from .arxiv_ingestion_service import arxiv_ingestion_service
from .supabase_service import supabase_service
from .database_manager import get_redis
from ..core.config import settings

logger = logging.getLogger(__name__)

class HistoricalBackfillService:
    """Service for historical paper backfill with intelligent prioritization"""
    
    def __init__(self):
        self.redis = get_redis()
        self.batch_size = 50  # Papers per batch
        self.delay_between_batches = 30  # seconds
        
    async def run_complete_backfill(self) -> Dict[str, Any]:
        """
        Run complete historical backfill in phases
        
        Returns:
            Summary statistics of backfill process
        """
        logger.info("🚀 Starting complete historical backfill...")
        
        total_stats = {
            "phase1_recent": {},
            "phase2_foundational": {},
            "phase3_historical": {},
            "total_papers_processed": 0,
            "total_cost_estimate": 0,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None
        }
        
        try:
            # Phase 1: Recent high-impact papers (2023-2024)
            logger.info("📊 Phase 1: Recent high-impact papers (2023-2024)")
            phase1_stats = await self.backfill_recent_papers()
            total_stats["phase1_recent"] = phase1_stats
            
            # Save progress
            await self._save_backfill_progress("phase1_complete", total_stats)
            
            # Phase 2: Citation-rich foundational papers (2020-2022)
            logger.info("📚 Phase 2: Foundational papers (2020-2022)")
            phase2_stats = await self.backfill_foundational_papers()
            total_stats["phase2_foundational"] = phase2_stats
            
            # Save progress
            await self._save_backfill_progress("phase2_complete", total_stats)
            
            # Phase 3: Complete historical coverage (2015-2019)
            logger.info("🏛️ Phase 3: Historical coverage (2015-2019)")
            phase3_stats = await self.backfill_historical_papers()
            total_stats["phase3_historical"] = phase3_stats
            
            # Calculate totals
            total_stats["total_papers_processed"] = (
                phase1_stats.get("created", 0) +
                phase2_stats.get("created", 0) +
                phase3_stats.get("created", 0)
            )
            
            total_stats["total_cost_estimate"] = total_stats["total_papers_processed"] * 0.03  # $0.03 per paper
            total_stats["end_time"] = datetime.utcnow().isoformat()
            
            # Save final results
            await self._save_backfill_progress("complete", total_stats)
            
            logger.info(f"✅ Complete backfill finished: {total_stats['total_papers_processed']} papers processed")
            return total_stats
            
        except Exception as e:
            logger.error(f"❌ Backfill failed: {e}")
            total_stats["error"] = str(e)
            total_stats["end_time"] = datetime.utcnow().isoformat()
            return total_stats
    
    async def backfill_recent_papers(self) -> Dict[str, int]:
        """Phase 1: Backfill recent papers (2023-2024)"""
        stats = {"total": 0, "created": 0, "skipped": 0, "failed": 0}
        
        categories = ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.NE", "stat.ML", "cs.RO", "cs.IR"]
        
        # Process 2023 and 2024 by month
        for year in [2023, 2024]:
            end_month = 12 if year == 2023 else datetime.utcnow().month
            
            for month in range(1, end_month + 1):
                try:
                    logger.info(f"Processing {year}-{month:02d}...")
                    
                    # Fetch papers for this month
                    papers = await arxiv_ingestion_service.fetch_papers_by_categories(
                        categories=categories,
                        days=0,  # No date filter, we'll use search query
                        max_results=2000
                    )
                    
                    # Filter by month (arXiv API doesn't support month-level filtering well)
                    month_papers = [
                        paper for paper in papers 
                        if paper.published_date.year == year and paper.published_date.month == month
                    ]
                    
                    # Process in batches
                    month_stats = await self._process_papers_in_batches(
                        month_papers, 
                        priority=9,  # High priority
                        batch_delay=10  # Fast processing for recent papers
                    )
                    
                    # Update stats
                    for key in stats:
                        stats[key] += month_stats.get(key, 0)
                    
                    logger.info(f"✅ {year}-{month:02d}: {month_stats['created']} papers created")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process {year}-{month:02d}: {e}")
                    stats["failed"] += 1
        
        return stats
    
    async def backfill_foundational_papers(self) -> Dict[str, int]:
        """Phase 2: Backfill foundational high-citation papers"""
        stats = {"total": 0, "created": 0, "skipped": 0, "failed": 0}
        
        # Search for foundational terms that indicate high-impact papers
        foundational_queries = [
            "transformer neural network",
            "deep learning",
            "convolutional neural network",
            "generative adversarial network",
            "reinforcement learning",
            "attention mechanism",
            "BERT language model",
            "computer vision",
            "natural language processing",
            "machine learning theory",
            "autonomous robotics",
            "robot learning",
            "robotic manipulation"
        ]
        
        for query in foundational_queries:
            try:
                logger.info(f"Searching foundational papers for: {query}")
                
                # Fetch papers for this query
                papers = await arxiv_ingestion_service.fetch_papers_by_query(
                    query=f"{query} AND cat:cs.AI OR cat:cs.LG OR cat:cs.CV OR cat:cs.CL",
                    max_results=500
                )
                
                # Filter to 2020-2022 (foundational recent papers)
                foundational_papers = [
                    paper for paper in papers
                    if 2020 <= paper.published_date.year <= 2022
                ]
                
                # Process in batches
                query_stats = await self._process_papers_in_batches(
                    foundational_papers,
                    priority=8,  # High priority
                    batch_delay=20
                )
                
                # Update stats
                for key in stats:
                    stats[key] += query_stats.get(key, 0)
                
                logger.info(f"✅ Query '{query}': {query_stats['created']} papers created")
                
            except Exception as e:
                logger.error(f"❌ Failed query '{query}': {e}")
                stats["failed"] += 1
        
        return stats
    
    async def backfill_historical_papers(self) -> Dict[str, int]:
        """Phase 3: Complete historical backfill (2015-2019)"""
        stats = {"total": 0, "created": 0, "skipped": 0, "failed": 0}
        
        categories = ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.NE", "stat.ML", "cs.RO", "cs.IR"]
        
        # Process by year (2015-2019)
        for year in range(2015, 2020):
            try:
                logger.info(f"Processing historical year: {year}")
                
                # Fetch papers for entire year
                papers = await arxiv_ingestion_service.fetch_papers_by_categories(
                    categories=categories,
                    days=0,  # No recent filter
                    max_results=5000
                )
                
                # Filter by year
                year_papers = [
                    paper for paper in papers
                    if paper.published_date.year == year
                ]
                
                # Process in batches with longer delays
                year_stats = await self._process_papers_in_batches(
                    year_papers,
                    priority=3,  # Lower priority
                    batch_delay=60  # Slower processing
                )
                
                # Update stats
                for key in stats:
                    stats[key] += year_stats.get(key, 0)
                
                logger.info(f"✅ Year {year}: {year_stats['created']} papers created")
                
                # Long delay between years to avoid overloading
                await asyncio.sleep(300)  # 5 minutes between years
                
            except Exception as e:
                logger.error(f"❌ Failed year {year}: {e}")
                stats["failed"] += 1
        
        return stats
    
    async def _process_papers_in_batches(
        self, 
        papers: List, 
        priority: int = 5,
        batch_delay: int = 30
    ) -> Dict[str, int]:
        """Process papers in batches with rate limiting"""
        stats = {"total": len(papers), "created": 0, "skipped": 0, "failed": 0}
        
        # Process in batches
        for i in range(0, len(papers), self.batch_size):
            batch = papers[i:i + self.batch_size]
            
            try:
                # Ingest batch
                batch_stats = await arxiv_ingestion_service.ingest_and_process_papers(batch)
                
                # Update priority for analysis queue
                for paper in batch:
                    if batch_stats.get("created", 0) > 0:
                        await supabase_service.add_to_processing_queue(
                            paper_id=paper.id,
                            task_type="analysis",
                            priority=priority
                        )
                
                # Update stats
                for key in ["created", "skipped", "failed"]:
                    stats[key] += batch_stats.get(key, 0)
                
                logger.info(f"Batch {i//self.batch_size + 1}: {batch_stats['created']} created, {batch_stats['skipped']} skipped")
                
                # Rate limiting delay
                if i + self.batch_size < len(papers):
                    await asyncio.sleep(batch_delay)
                
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                stats["failed"] += len(batch)
        
        return stats
    
    async def _save_backfill_progress(self, phase: str, stats: Dict[str, Any]):
        """Save backfill progress to Redis"""
        try:
            progress_key = f"backfill_progress:{phase}"
            await self.redis.setex(
                progress_key, 
                86400 * 7,  # Keep for 7 days
                json.dumps(stats)
            )
            logger.info(f"💾 Saved progress for phase: {phase}")
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    async def get_backfill_status(self) -> Dict[str, Any]:
        """Get current backfill status"""
        try:
            # Check for saved progress
            phases = ["phase1_complete", "phase2_complete", "complete"]
            
            status = {
                "is_running": False,
                "current_phase": None,
                "progress": {},
                "estimated_completion": None
            }
            
            for phase in phases:
                progress_key = f"backfill_progress:{phase}"
                progress_data = await self.redis.get(progress_key)
                
                if progress_data:
                    status["progress"][phase] = json.loads(progress_data)
                    if phase == "complete":
                        status["current_phase"] = "completed"
                    elif not status["current_phase"]:
                        status["current_phase"] = phase
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get backfill status: {e}")
            return {"error": str(e)}
    
    async def estimate_backfill_cost(self) -> Dict[str, Any]:
        """Estimate cost and time for complete backfill"""
        
        # Rough estimates based on arXiv data
        estimates = {
            "phase1_recent": {
                "papers": 50000,
                "cost_usd": 1500,
                "time_days": 14,
                "description": "Recent high-impact papers (2023-2024)"
            },
            "phase2_foundational": {
                "papers": 25000,
                "cost_usd": 750,
                "time_days": 7,
                "description": "Foundational papers (2020-2022)"
            },
            "phase3_historical": {
                "papers": 75000,
                "cost_usd": 2250,
                "time_days": 30,
                "description": "Historical coverage (2015-2019)"
            },
            "total": {
                "papers": 150000,
                "cost_usd": 4500,
                "time_days": 51,
                "description": "Complete historical backfill"
            }
        }
        
        return estimates

# Global historical backfill service
historical_backfill_service = HistoricalBackfillService()