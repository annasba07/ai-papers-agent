"""
Citation Graph Service

Builds citation-like graphs based on paper similarity.
Uses embedding similarity as a proxy for "related papers" relationships.
Returns visualization-ready nodes and edges for graph rendering.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import numpy as np

from app.services.local_atlas_service import local_atlas_service
from app.utils.logger import LoggerMixin


@dataclass
class GraphNode:
    """A node in the citation graph."""
    id: str
    title: str
    authors: List[str]
    category: str
    published: Optional[str]
    depth: int  # 0 = center, 1 = first-level, 2 = second-level
    is_center: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "category": self.category,
            "published": self.published,
            "depth": self.depth,
            "is_center": self.is_center,
        }


@dataclass
class GraphEdge:
    """An edge connecting two papers in the graph."""
    source: str
    target: str
    similarity: float
    edge_type: str = "similar"  # "similar", "cited_by", "cites"

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "target": self.target,
            "similarity": round(self.similarity, 4),
            "edge_type": self.edge_type,
        }


@dataclass
class CitationGraph:
    """Complete graph structure for visualization."""
    center_paper_id: str
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "center": self.center_paper_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "depth_0": sum(1 for n in self.nodes if n.depth == 0),
                "depth_1": sum(1 for n in self.nodes if n.depth == 1),
                "depth_2": sum(1 for n in self.nodes if n.depth == 2),
            }
        }


class CitationGraphService(LoggerMixin):
    """
    Service for building citation/similarity graphs from the local atlas.

    Uses embedding similarity as a proxy for "related papers" relationships,
    creating visualization-ready graphs.
    """

    def __init__(self) -> None:
        self._atlas = local_atlas_service
        self.log_info("Citation graph service initialized")

    @property
    def enabled(self) -> bool:
        return self._atlas.enabled and self._atlas._embeddings is not None

    def build_similarity_graph(
        self,
        paper_id: str,
        *,
        max_depth: int = 2,
        neighbors_per_node: int = 5,
        min_similarity: float = 0.5,
        category: Optional[str] = None,
    ) -> Optional[CitationGraph]:
        """
        Build a similarity-based graph around a central paper.

        Args:
            paper_id: The central paper ID
            max_depth: Maximum depth (1 = direct neighbors, 2 = neighbors of neighbors)
            neighbors_per_node: How many similar papers to include per node
            min_similarity: Minimum similarity threshold for edges
            category: Optional category filter

        Returns:
            CitationGraph object or None if paper not found
        """
        if not self.enabled:
            self.log_warning("Citation graph service not enabled (no embeddings)")
            return None

        # Normalize paper_id
        base_id = paper_id.split("v")[0] if "v" in paper_id else paper_id

        # Find center paper
        center_paper = self._atlas.get_paper_by_id(paper_id)
        if not center_paper:
            self.log_warning(f"Paper not found: {paper_id}")
            return None

        # Initialize graph
        graph = CitationGraph(center_paper_id=paper_id)
        visited: Set[str] = set()

        # Add center node
        center_node = GraphNode(
            id=center_paper["id"],
            title=center_paper["title"],
            authors=center_paper.get("authors", []),
            category=center_paper.get("category", ""),
            published=center_paper.get("published"),
            depth=0,
            is_center=True,
        )
        graph.nodes.append(center_node)
        visited.add(self._normalize_id(center_paper["id"]))

        # BFS to build the graph
        current_level_ids = [paper_id]

        for depth in range(1, max_depth + 1):
            next_level_ids = []

            for source_id in current_level_ids:
                # Find similar papers for this node
                similar = self._atlas.find_similar(
                    source_id,
                    top_k=neighbors_per_node * 2,  # Get more to account for filtering
                    category=category,
                )

                for sim_paper in similar:
                    sim_id = self._normalize_id(sim_paper["id"])
                    similarity = sim_paper.get("similarity_score", 0)

                    if similarity < min_similarity:
                        continue

                    # Add edge
                    edge = GraphEdge(
                        source=source_id,
                        target=sim_paper["id"],
                        similarity=similarity,
                        edge_type="similar",
                    )
                    graph.edges.append(edge)

                    # Add node if not visited
                    if sim_id not in visited:
                        node = GraphNode(
                            id=sim_paper["id"],
                            title=sim_paper["title"],
                            authors=sim_paper.get("authors", []),
                            category=sim_paper.get("category", ""),
                            published=sim_paper.get("published"),
                            depth=depth,
                        )
                        graph.nodes.append(node)
                        visited.add(sim_id)

                        # Queue for next level
                        if len(next_level_ids) < neighbors_per_node * len(current_level_ids):
                            next_level_ids.append(sim_paper["id"])

            current_level_ids = next_level_ids[:neighbors_per_node * 3]  # Limit growth

        self.log_info(
            f"Built similarity graph",
            center=paper_id,
            nodes=len(graph.nodes),
            edges=len(graph.edges),
        )

        return graph

    def build_cluster_graph(
        self,
        paper_ids: List[str],
        *,
        min_similarity: float = 0.6,
    ) -> CitationGraph:
        """
        Build a graph showing relationships between a set of papers.

        Args:
            paper_ids: List of paper IDs to include
            min_similarity: Minimum similarity for edges

        Returns:
            CitationGraph with inter-paper relationships
        """
        if not self.enabled:
            return CitationGraph(center_paper_id="cluster")

        graph = CitationGraph(center_paper_id="cluster")

        # Get paper details and indices
        papers = []
        indices = []
        for pid in paper_ids:
            paper = self._atlas.get_paper_by_id(pid)
            if paper:
                papers.append(paper)
                idx = self._get_paper_index(pid)
                if idx is not None:
                    indices.append((pid, idx))

        if not papers:
            return graph

        # Add all papers as nodes
        for paper in papers:
            node = GraphNode(
                id=paper["id"],
                title=paper["title"],
                authors=paper.get("authors", []),
                category=paper.get("category", ""),
                published=paper.get("published"),
                depth=0,
            )
            graph.nodes.append(node)

        # Compute pairwise similarities
        if len(indices) >= 2 and self._atlas._embeddings is not None:
            for i, (pid_a, idx_a) in enumerate(indices):
                for pid_b, idx_b in indices[i + 1:]:
                    emb_a = self._atlas._embeddings[idx_a]
                    emb_b = self._atlas._embeddings[idx_b]
                    similarity = float(np.dot(emb_a, emb_b))

                    if similarity >= min_similarity:
                        edge = GraphEdge(
                            source=pid_a,
                            target=pid_b,
                            similarity=similarity,
                        )
                        graph.edges.append(edge)

        return graph

    def get_paper_neighborhood(
        self,
        paper_id: str,
        *,
        top_k: int = 10,
    ) -> Dict:
        """
        Get immediate neighborhood for a paper (simpler than full graph).

        Returns papers grouped by similarity tiers.
        """
        if not self.enabled:
            return {"error": "Service not enabled"}

        similar = self._atlas.find_similar(paper_id, top_k=top_k)

        # Group by similarity tiers
        tiers = {
            "highly_similar": [],  # > 0.85
            "similar": [],  # 0.7-0.85
            "related": [],  # 0.5-0.7
        }

        for paper in similar:
            score = paper.get("similarity_score", 0)
            if score > 0.85:
                tiers["highly_similar"].append(paper)
            elif score > 0.7:
                tiers["similar"].append(paper)
            else:
                tiers["related"].append(paper)

        return {
            "paper_id": paper_id,
            "tiers": tiers,
            "total": len(similar),
        }

    def _normalize_id(self, paper_id: str) -> str:
        """Normalize paper ID by removing version suffix."""
        return paper_id.split("v")[0] if "v" in paper_id else paper_id

    def _get_paper_index(self, paper_id: str) -> Optional[int]:
        """Get the index of a paper in the atlas records."""
        base_id = self._normalize_id(paper_id)
        for idx, record_id in enumerate(self._atlas._record_ids):
            record_base = self._normalize_id(record_id) if record_id else None
            if record_base == base_id:
                return idx
        return None


# Module-level singleton
_citation_graph_service: Optional[CitationGraphService] = None


def get_citation_graph_service() -> CitationGraphService:
    """Get or create the citation graph service singleton."""
    global _citation_graph_service
    if _citation_graph_service is None:
        _citation_graph_service = CitationGraphService()
    return _citation_graph_service
