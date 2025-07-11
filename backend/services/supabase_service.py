"""
Supabase Service for structured data operations
Manages paper storage, analysis results, and metadata in PostgreSQL
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase import Client as SupabaseClient

from ..models.paper import Paper, PaperCreate, PaperUpdate, AIAnalysis, ProcessingQueue, Topic
from .database_manager import get_supabase

logger = logging.getLogger(__name__)

class SupabaseService:
    """Service for managing Supabase operations"""
    
    def __init__(self):
        self.client: SupabaseClient = get_supabase()
    
    async def create_paper(self, paper_data: PaperCreate) -> Optional[str]:
        """Create a new paper record"""
        try:
            # Convert Pydantic model to dict
            paper_dict = paper_data.model_dump()
            
            # Handle datetime serialization
            if isinstance(paper_dict["published_date"], datetime):
                paper_dict["published_date"] = paper_dict["published_date"].isoformat()
            
            # Insert paper
            result = self.client.table("papers").insert(paper_dict).execute()
            
            if result.data:
                logger.info(f"✅ Created paper: {paper_data.id}")
                return paper_data.id
            else:
                logger.error(f"❌ Failed to create paper: {paper_data.id}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating paper {paper_data.id}: {e}")
            return None
    
    async def update_paper(self, paper_id: str, update_data: PaperUpdate) -> bool:
        """Update an existing paper record"""
        try:
            # Convert Pydantic model to dict, excluding None values
            update_dict = update_data.model_dump(exclude_none=True)
            
            # Handle datetime serialization
            for key, value in update_dict.items():
                if isinstance(value, datetime):
                    update_dict[key] = value.isoformat()
            
            # Add updated_at timestamp
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.client.table("papers").update(update_dict).eq("id", paper_id).execute()
            
            if result.data:
                logger.info(f"✅ Updated paper: {paper_id}")
                return True
            else:
                logger.error(f"❌ Failed to update paper: {paper_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating paper {paper_id}: {e}")
            return False
    
    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        """Get a paper by ID"""
        try:
            result = self.client.table("papers").select("*").eq("id", paper_id).execute()
            
            if result.data:
                paper_data = result.data[0]
                return Paper(**paper_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting paper {paper_id}: {e}")
            return None
    
    async def get_papers_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 50,
        offset: int = 0
    ) -> List[Paper]:
        """Get papers within a date range"""
        try:
            result = (
                self.client.table("papers")
                .select("*")
                .gte("published_date", start_date.isoformat())
                .lte("published_date", end_date.isoformat())
                .order("published_date", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            if result.data:
                return [Paper(**paper_data) for paper_data in result.data]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting papers by date range: {e}")
            return []
    
    async def get_papers_by_categories(
        self, 
        categories: List[str],
        limit: int = 50,
        offset: int = 0
    ) -> List[Paper]:
        """Get papers by categories"""
        try:
            # Build category filter for JSONB array
            category_filter = f"[{','.join(f'\"{cat}\"' for cat in categories)}]"
            
            result = (
                self.client.table("papers")
                .select("*")
                .overlaps("categories", categories)
                .order("published_date", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            if result.data:
                return [Paper(**paper_data) for paper_data in result.data]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting papers by categories: {e}")
            return []
    
    async def search_papers(
        self, 
        query: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Paper]:
        """Search papers by title and abstract"""
        try:
            # Use PostgreSQL full-text search
            result = (
                self.client.table("papers")
                .select("*")
                .text_search("title", query)
                .order("published_date", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            # If no results in title, search abstract
            if not result.data:
                result = (
                    self.client.table("papers")
                    .select("*")
                    .text_search("abstract", query)
                    .order("published_date", desc=True)
                    .range(offset, offset + limit - 1)
                    .execute()
                )
            
            if result.data:
                return [Paper(**paper_data) for paper_data in result.data]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error searching papers: {e}")
            return []
    
    async def get_papers_needing_analysis(self, limit: int = 10) -> List[Paper]:
        """Get papers that need AI analysis"""
        try:
            result = (
                self.client.table("papers")
                .select("*")
                .is_("ai_analysis", "null")
                .order("published_date", desc=True)
                .limit(limit)
                .execute()
            )
            
            if result.data:
                return [Paper(**paper_data) for paper_data in result.data]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting papers needing analysis: {e}")
            return []
    
    async def add_to_processing_queue(
        self, 
        paper_id: str, 
        task_type: str,
        priority: int = 5
    ) -> bool:
        """Add a paper to the processing queue"""
        try:
            queue_item = ProcessingQueue(
                paper_id=paper_id,
                task_type=task_type,
                priority=priority
            )
            
            result = (
                self.client.table("processing_queue")
                .insert(queue_item.model_dump())
                .execute()
            )
            
            if result.data:
                logger.info(f"✅ Added to queue: {paper_id} -> {task_type}")
                return True
            else:
                logger.error(f"❌ Failed to add to queue: {paper_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding to processing queue: {e}")
            return False
    
    async def get_next_queue_item(self, task_type: Optional[str] = None) -> Optional[ProcessingQueue]:
        """Get the next item from the processing queue"""
        try:
            query = (
                self.client.table("processing_queue")
                .select("*")
                .eq("status", "pending")
            )
            
            if task_type:
                query = query.eq("task_type", task_type)
            
            result = (
                query
                .order("priority", desc=True)
                .order("created_at", desc=False)
                .limit(1)
                .execute()
            )
            
            if result.data:
                return ProcessingQueue(**result.data[0])
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting next queue item: {e}")
            return None
    
    async def update_queue_status(
        self, 
        queue_id: int, 
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update processing queue item status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if error_message:
                update_data["error_message"] = error_message
            
            if status == "processing":
                # Increment attempts
                result = (
                    self.client.table("processing_queue")
                    .select("attempts")
                    .eq("id", queue_id)
                    .execute()
                )
                
                if result.data:
                    current_attempts = result.data[0]["attempts"]
                    update_data["attempts"] = current_attempts + 1
            
            result = (
                self.client.table("processing_queue")
                .update(update_data)
                .eq("id", queue_id)
                .execute()
            )
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating queue status: {e}")
            return False
    
    async def get_topic_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics about topics and categories"""
        try:
            # Get category distribution
            result = (
                self.client.rpc("get_category_stats")
                .execute()
            )
            
            if result.data:
                return result.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting topic statistics: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check if Supabase connection is healthy"""
        try:
            result = self.client.table("papers").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False

# Global Supabase service instance
supabase_service = SupabaseService()