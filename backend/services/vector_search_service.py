"""
Vector Search Service using Pinecone
Handles paper embeddings and similarity search for research intelligence
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime

import google.generativeai as genai
from pinecone import Pinecone, PodSpec

from ..core.config import settings
from ..models.paper import Paper
from .database_manager import get_pinecone

logger = logging.getLogger(__name__)

class VectorSearchService:
    """Service for vector embeddings and similarity search"""
    
    def __init__(self):
        self.pinecone_client = get_pinecone()
        self.index_name = settings.PINECONE_INDEX_NAME
        self.embedding_dimension = 768  # Gemini text embedding dimension
        
        # Configure Gemini for embeddings
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
    async def initialize_index(self):
        """Initialize Pinecone index if it doesn't exist"""
        try:
            # Check if index exists
            existing_indexes = self.pinecone_client.list_indexes()
            index_names = [idx.name for idx in existing_indexes.indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                
                # Create index with appropriate spec
                self.pinecone_client.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric="cosine",
                    spec=PodSpec(
                        environment=settings.PINECONE_ENVIRONMENT,
                        pod_type="s1.x1",  # Starter pod type
                        pods=1,
                        replicas=1
                    )
                )
                
                # Wait for index to be ready
                await asyncio.sleep(10)
                logger.info(f"✅ Created Pinecone index: {self.index_name}")
            else:
                logger.info(f"✅ Pinecone index already exists: {self.index_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {e}")
            raise
    
    def get_index(self):
        """Get Pinecone index instance"""
        return self.pinecone_client.Index(self.index_name)
    
    async def generate_text_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Gemini
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            # Clean and truncate text if needed
            cleaned_text = text.strip()[:8000]  # Gemini has input limits
            
            # Generate embedding using Gemini
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=cleaned_text,
                task_type="semantic_similarity"
            )
            
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension
    
    async def create_paper_embedding(self, paper: Dict[str, Any]) -> Optional[str]:
        """
        Create and store embedding for a paper
        
        Args:
            paper: Paper data dictionary
            
        Returns:
            Vector ID if successful, None if failed
        """
        try:
            # Combine title and abstract for embedding
            content = f"{paper['title']} {paper['abstract']}"
            
            # Generate embedding
            embedding = await self.generate_text_embedding(content)
            
            if not embedding or all(v == 0.0 for v in embedding):
                logger.warning(f"Failed to generate valid embedding for paper {paper['id']}")
                return None
            
            # Prepare metadata
            metadata = {
                "paper_id": paper["id"],
                "title": paper["title"][:500],  # Pinecone metadata size limits
                "published_date": paper["published_date"].isoformat() if isinstance(paper["published_date"], datetime) else str(paper["published_date"]),
                "categories": paper.get("categories", [])[:10],  # Limit array size
                "author_count": len(paper.get("authors", [])),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Pinecone
            index = self.get_index()
            vector_id = f"paper_{paper['id']}"
            
            index.upsert(vectors=[(vector_id, embedding, metadata)])
            
            logger.info(f"✅ Created embedding for paper {paper['id']}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Failed to create embedding for paper {paper['id']}: {e}")
            return None
    
    async def search_similar_papers(
        self, 
        query_text: str, 
        top_k: int = 10,
        category_filter: Optional[List[str]] = None,
        date_filter: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for papers similar to query text
        
        Args:
            query_text: Search query
            top_k: Number of results to return
            category_filter: Optional list of categories to filter by
            date_filter: Optional date range filter
            
        Returns:
            List of similar papers with scores
        """
        try:
            # Generate query embedding
            query_embedding = await self.generate_text_embedding(query_text)
            
            if not query_embedding or all(v == 0.0 for v in query_embedding):
                logger.warning("Failed to generate query embedding")
                return []
            
            # Build filter conditions
            filter_conditions = {}
            
            if category_filter:
                filter_conditions["categories"] = {"$in": category_filter}
            
            if date_filter:
                if "start_date" in date_filter:
                    filter_conditions["published_date"] = {"$gte": date_filter["start_date"]}
                if "end_date" in date_filter:
                    if "published_date" not in filter_conditions:
                        filter_conditions["published_date"] = {}
                    filter_conditions["published_date"]["$lte"] = date_filter["end_date"]
            
            # Search in Pinecone
            index = self.get_index()
            
            search_kwargs = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True,
                "include_values": False
            }
            
            if filter_conditions:
                search_kwargs["filter"] = filter_conditions
            
            results = index.query(**search_kwargs)
            
            # Format results
            similar_papers = []
            for match in results.matches:
                similar_papers.append({
                    "paper_id": match.metadata["paper_id"],
                    "title": match.metadata["title"],
                    "similarity_score": float(match.score),
                    "published_date": match.metadata["published_date"],
                    "categories": match.metadata["categories"],
                    "author_count": match.metadata.get("author_count", 0)
                })
            
            logger.info(f"Found {len(similar_papers)} similar papers for query: {query_text[:50]}...")
            return similar_papers
            
        except Exception as e:
            logger.error(f"Failed to search similar papers: {e}")
            return []
    
    async def search_papers_by_embedding(
        self, 
        paper_id: str, 
        top_k: int = 10,
        exclude_self: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find papers similar to a specific paper using its embedding
        
        Args:
            paper_id: ID of the reference paper
            top_k: Number of results to return
            exclude_self: Whether to exclude the reference paper from results
            
        Returns:
            List of similar papers
        """
        try:
            # Get the paper's vector from Pinecone
            index = self.get_index()
            vector_id = f"paper_{paper_id}"
            
            # Fetch the vector
            fetch_result = index.fetch(ids=[vector_id])
            
            if vector_id not in fetch_result.vectors:
                logger.warning(f"No embedding found for paper {paper_id}")
                return []
            
            # Get the embedding
            paper_vector = fetch_result.vectors[vector_id].values
            
            # Search for similar papers
            search_results = index.query(
                vector=paper_vector,
                top_k=top_k + (1 if exclude_self else 0),  # Get extra if excluding self
                include_metadata=True,
                include_values=False
            )
            
            # Format results and optionally exclude self
            similar_papers = []
            for match in search_results.matches:
                if exclude_self and match.metadata["paper_id"] == paper_id:
                    continue
                
                similar_papers.append({
                    "paper_id": match.metadata["paper_id"],
                    "title": match.metadata["title"],
                    "similarity_score": float(match.score),
                    "published_date": match.metadata["published_date"],
                    "categories": match.metadata["categories"]
                })
            
            # Limit to requested top_k
            return similar_papers[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to search by paper embedding {paper_id}: {e}")
            return []
    
    async def get_topic_clusters(
        self, 
        category: str, 
        cluster_size: int = 50,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find clusters of related papers in a category
        
        Args:
            category: arXiv category to analyze
            cluster_size: Maximum papers per cluster
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of paper clusters
        """
        try:
            # This is a simplified clustering approach
            # In production, you'd want more sophisticated clustering
            
            # Get all papers in category (sample approach)
            index = self.get_index()
            
            # Query with a broad filter to get papers in category
            dummy_vector = [0.0] * self.embedding_dimension
            
            results = index.query(
                vector=dummy_vector,
                top_k=1000,  # Adjust based on your needs
                filter={"categories": {"$in": [category]}},
                include_metadata=True
            )
            
            # Simple clustering by similarity ranges
            clusters = []
            processed_papers = set()
            
            for i, match in enumerate(results.matches):
                if match.metadata["paper_id"] in processed_papers:
                    continue
                
                # Start new cluster with this paper
                cluster = {
                    "cluster_id": i,
                    "papers": [match.metadata],
                    "representative_paper": match.metadata["paper_id"],
                    "avg_similarity": 1.0
                }
                
                processed_papers.add(match.metadata["paper_id"])
                
                # Find similar papers for this cluster
                similar_papers = await self.search_papers_by_embedding(
                    match.metadata["paper_id"],
                    top_k=cluster_size
                )
                
                # Add papers above similarity threshold
                cluster_similarities = []
                for similar_paper in similar_papers:
                    if (similar_paper["similarity_score"] >= min_similarity and 
                        similar_paper["paper_id"] not in processed_papers):
                        
                        cluster["papers"].append({
                            "paper_id": similar_paper["paper_id"],
                            "title": similar_paper["title"],
                            "similarity_score": similar_paper["similarity_score"]
                        })
                        
                        cluster_similarities.append(similar_paper["similarity_score"])
                        processed_papers.add(similar_paper["paper_id"])
                
                # Calculate average similarity
                if cluster_similarities:
                    cluster["avg_similarity"] = sum(cluster_similarities) / len(cluster_similarities)
                
                clusters.append(cluster)
                
                # Stop if we've processed enough clusters
                if len(clusters) >= 10:
                    break
            
            return clusters
            
        except Exception as e:
            logger.error(f"Failed to get topic clusters for {category}: {e}")
            return []
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index"""
        try:
            index = self.get_index()
            stats = index.describe_index_stats()
            
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {"error": str(e)}
    
    async def delete_paper_embedding(self, paper_id: str) -> bool:
        """Delete a paper's embedding from the index"""
        try:
            index = self.get_index()
            vector_id = f"paper_{paper_id}"
            
            index.delete(ids=[vector_id])
            
            logger.info(f"✅ Deleted embedding for paper {paper_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete embedding for paper {paper_id}: {e}")
            return False

# Global vector search service instance
vector_search_service = VectorSearchService()