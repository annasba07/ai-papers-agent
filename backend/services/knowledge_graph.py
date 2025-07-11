"""
Knowledge Graph Service for Neo4j AuraDB
Manages the graph database schema and operations for research intelligence
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from neo4j import Session, Result
from .database_manager import get_neo4j

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    """Service for managing the research knowledge graph"""
    
    def __init__(self):
        self.driver = get_neo4j()
    
    async def initialize_schema(self):
        """Initialize Neo4j schema with constraints and indexes"""
        schema_queries = [
            # Node constraints
            "CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT author_name IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE", 
            "CREATE CONSTRAINT institution_name IF NOT EXISTS FOR (i:Institution) REQUIRE i.name IS UNIQUE",
            "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
            "CREATE CONSTRAINT technique_name IF NOT EXISTS FOR (tech:Technique) REQUIRE tech.name IS UNIQUE",
            
            # Indexes for performance
            "CREATE INDEX paper_published_date IF NOT EXISTS FOR (p:Paper) ON (p.published_date)",
            "CREATE INDEX paper_impact_score IF NOT EXISTS FOR (p:Paper) ON (p.impact_score)",
            "CREATE INDEX technique_maturity IF NOT EXISTS FOR (tech:Technique) ON (tech.maturity_level)",
            "CREATE INDEX author_citation_count IF NOT EXISTS FOR (a:Author) ON (a.total_citations)",
            
            # Full-text search indexes
            "CREATE FULLTEXT INDEX paper_text_search IF NOT EXISTS FOR (p:Paper) ON EACH [p.title, p.abstract]",
            "CREATE FULLTEXT INDEX technique_search IF NOT EXISTS FOR (tech:Technique) ON EACH [tech.name, tech.description]"
        ]
        
        with self.driver.session() as session:
            for query in schema_queries:
                try:
                    session.run(query)
                    logger.info(f"✅ Schema query executed: {query[:50]}...")
                except Exception as e:
                    logger.warning(f"⚠️ Schema query failed (may already exist): {e}")
    
    async def create_paper_node(self, paper_data: Dict[str, Any]) -> bool:
        """Create or update a paper node in the knowledge graph"""
        query = """
        MERGE (p:Paper {id: $paper_id})
        SET p.title = $title,
            p.abstract = $abstract,
            p.published_date = datetime($published_date),
            p.arxiv_url = $arxiv_url,
            p.categories = $categories,
            p.impact_score = $impact_score,
            p.research_significance = $research_significance,
            p.practical_applicability = $practical_applicability,
            p.updated_at = datetime()
        RETURN p.id as id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, 
                    paper_id=paper_data["id"],
                    title=paper_data["title"],
                    abstract=paper_data["abstract"],
                    published_date=paper_data["published_date"].isoformat(),
                    arxiv_url=paper_data["arxiv_url"],
                    categories=paper_data["categories"],
                    impact_score=paper_data.get("impact_score", 3.0),
                    research_significance=paper_data.get("research_significance", "incremental"),
                    practical_applicability=paper_data.get("practical_applicability", "medium")
                )
                return result.single() is not None
        except Exception as e:
            logger.error(f"Failed to create paper node: {e}")
            return False
    
    async def create_author_relationships(self, paper_id: str, authors: List[Dict[str, Any]]) -> bool:
        """Create author nodes and relationships"""
        query = """
        MATCH (p:Paper {id: $paper_id})
        UNWIND $authors as author_data
        MERGE (a:Author {name: author_data.name})
        SET a.affiliation = author_data.affiliation,
            a.total_papers = coalesce(a.total_papers, 0) + 1,
            a.updated_at = datetime()
        MERGE (p)-[:AUTHORED_BY {position: author_data.position}]->(a)
        """
        
        try:
            with self.driver.session() as session:
                # Add position information to authors
                authors_with_position = [
                    {**author, "position": i} 
                    for i, author in enumerate(authors)
                ]
                
                session.run(query, paper_id=paper_id, authors=authors_with_position)
                return True
        except Exception as e:
            logger.error(f"Failed to create author relationships: {e}")
            return False
    
    async def create_citation_relationships(self, citing_paper_id: str, cited_paper_ids: List[str]) -> bool:
        """Create citation relationships between papers"""
        query = """
        MATCH (citing:Paper {id: $citing_paper_id})
        UNWIND $cited_paper_ids as cited_id
        MATCH (cited:Paper {id: cited_id})
        MERGE (citing)-[r:CITES]->(cited)
        SET r.created_at = datetime()
        """
        
        try:
            with self.driver.session() as session:
                session.run(query, 
                    citing_paper_id=citing_paper_id,
                    cited_paper_ids=cited_paper_ids
                )
                return True
        except Exception as e:
            logger.error(f"Failed to create citation relationships: {e}")
            return False
    
    async def create_technique_relationships(self, paper_id: str, techniques: List[Dict[str, Any]]) -> bool:
        """Create technique nodes and relationships"""
        query = """
        MATCH (p:Paper {id: $paper_id})
        UNWIND $techniques as tech_data
        MERGE (t:Technique {name: tech_data.name})
        SET t.description = tech_data.description,
            t.maturity_level = tech_data.maturity_level,
            t.domain = tech_data.domain,
            t.paper_count = coalesce(t.paper_count, 0) + 1,
            t.updated_at = datetime()
        MERGE (p)-[r:USES_TECHNIQUE]->(t)
        SET r.confidence = tech_data.confidence,
            r.is_primary = tech_data.is_primary,
            r.created_at = datetime()
        """
        
        try:
            with self.driver.session() as session:
                session.run(query, paper_id=paper_id, techniques=techniques)
                return True
        except Exception as e:
            logger.error(f"Failed to create technique relationships: {e}")
            return False
    
    async def find_competitive_approaches(self, research_components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find competing research approaches using graph traversal"""
        query = """
        // Find papers that solve similar problems but use different techniques
        MATCH (target_tech:Technique) 
        WHERE target_tech.name IN $target_techniques
        
        MATCH (competing_paper:Paper)-[:USES_TECHNIQUE]->(competing_tech:Technique)
        WHERE competing_tech.domain = target_tech.domain 
        AND NOT competing_tech.name IN $target_techniques
        AND competing_paper.published_date > datetime() - duration({months: 12})
        
        RETURN competing_paper.id as paper_id,
               competing_paper.title as title,
               competing_paper.impact_score as impact_score,
               competing_paper.published_date as published_date,
               collect(competing_tech.name) as competing_techniques,
               avg(competing_paper.impact_score) as threat_level
        ORDER BY threat_level DESC, competing_paper.published_date DESC
        LIMIT 10
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, 
                    target_techniques=research_components.get("techniques", [])
                )
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Failed to find competitive approaches: {e}")
            return []
    
    async def find_research_opportunities(self, research_components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find unexplored research opportunities"""
        query = """
        // Find technique combinations that haven't been explored
        MATCH (tech1:Technique), (tech2:Technique)
        WHERE tech1.name IN $target_techniques
        AND tech2.domain = tech1.domain
        AND tech1 <> tech2
        AND NOT EXISTS {
            MATCH (p:Paper)-[:USES_TECHNIQUE]->(tech1)
            MATCH (p)-[:USES_TECHNIQUE]->(tech2)
        }
        
        RETURN tech1.name as technique1,
               tech2.name as technique2,
               tech1.maturity_level as maturity1,
               tech2.maturity_level as maturity2,
               (tech1.paper_count + tech2.paper_count) as combined_popularity
        ORDER BY combined_popularity DESC
        LIMIT 5
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query,
                    target_techniques=research_components.get("techniques", [])
                )
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Failed to find research opportunities: {e}")
            return []
    
    async def get_topic_evolution(self, topic_name: str, timeframe_months: int = 12) -> Dict[str, Any]:
        """Get topic evolution over time"""
        query = """
        MATCH (p:Paper)-[:BELONGS_TO]->(t:Topic {name: $topic_name})
        WHERE p.published_date > datetime() - duration({months: $timeframe_months})
        
        // Get techniques used over time
        MATCH (p)-[:USES_TECHNIQUE]->(tech:Technique)
        
        WITH p, tech, 
             duration.between(datetime() - duration({months: $timeframe_months}), p.published_date).months as months_ago
        
        RETURN tech.name as technique,
               count(p) as paper_count,
               avg(p.impact_score) as avg_impact,
               collect(months_ago) as time_distribution,
               max(p.published_date) as latest_usage
        ORDER BY paper_count DESC, avg_impact DESC
        LIMIT 20
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query,
                    topic_name=topic_name,
                    timeframe_months=timeframe_months
                )
                techniques = [record.data() for record in result]
                
                return {
                    "topic": topic_name,
                    "timeframe_months": timeframe_months,
                    "technique_evolution": techniques,
                    "total_techniques": len(techniques)
                }
        except Exception as e:
            logger.error(f"Failed to get topic evolution: {e}")
            return {}
    
    async def find_collaboration_patterns(self, author_name: str) -> Dict[str, Any]:
        """Find collaboration patterns and potential collaborators"""
        query = """
        MATCH (target:Author {name: $author_name})<-[:AUTHORED_BY]-(p:Paper)
        
        // Find co-authors
        MATCH (p)-[:AUTHORED_BY]->(coauthor:Author)
        WHERE coauthor <> target
        
        // Find their research areas
        MATCH (p)-[:USES_TECHNIQUE]->(tech:Technique)
        
        RETURN coauthor.name as collaborator,
               count(DISTINCT p) as joint_papers,
               collect(DISTINCT tech.name) as shared_techniques,
               max(p.published_date) as latest_collaboration
        ORDER BY joint_papers DESC, latest_collaboration DESC
        LIMIT 10
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, author_name=author_name)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Failed to find collaboration patterns: {e}")
            return []

# Global knowledge graph service instance
knowledge_graph = KnowledgeGraphService()