'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';

type GraphNode = {
  id: string;
  title: string;
  authors: string[];
  category: string;
  published?: string;
  depth: number;
  is_center: boolean;
};

type GraphEdge = {
  source: string;
  target: string;
  similarity: number;
  edge_type: string;
};

type GraphData = {
  center: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    total_nodes: number;
    total_edges: number;
    depth_0: number;
    depth_1: number;
    depth_2: number;
  };
};

type D3Node = d3.SimulationNodeDatum & GraphNode & {
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
};

type D3Link = d3.SimulationLinkDatum<D3Node> & {
  source: D3Node | string;
  target: D3Node | string;
  similarity: number;
};

type CitationGraphProps = {
  paperId: string;
  maxDepth?: number;
  neighborsPerNode?: number;
  minSimilarity?: number;
  onNodeClick?: (nodeId: string, title: string) => void;
};

const categoryColors: Record<string, string> = {
  'cs.AI': '#3b82f6',
  'cs.CV': '#10b981',
  'cs.CL': '#f59e0b',
  'cs.LG': '#8b5cf6',
  'cs.NE': '#ec4899',
  'stat.ML': '#06b6d4',
  'eess.SP': '#f97316',
  'eess.IV': '#84cc16',
  default: '#6b7280',
};

export default function CitationGraph({
  paperId,
  maxDepth = 2,
  neighborsPerNode = 5,
  minSimilarity = 0.5,
  onNodeClick,
}: CitationGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width } = containerRef.current.getBoundingClientRect();
        setDimensions({ width: Math.max(400, width), height: 500 });
      }
    };
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!paperId) return;

    const fetchGraph = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams({
          max_depth: String(maxDepth),
          neighbors_per_node: String(neighborsPerNode),
          min_similarity: String(minSimilarity),
        });
        const res = await fetch(`/api/atlas/graph/${paperId}?${params}`);
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Failed to fetch graph');
        }
        const data = await res.json();
        setGraphData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load graph');
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [paperId, maxDepth, neighborsPerNode, minSimilarity]);

  const renderGraph = useCallback(() => {
    if (!graphData || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const { width, height } = dimensions;

    const nodes: D3Node[] = graphData.nodes.map((n) => ({ ...n }));
    const links: D3Link[] = graphData.edges.map((e) => ({
      source: e.source,
      target: e.target,
      similarity: e.similarity,
    }));

    const simulation = d3
      .forceSimulation<D3Node>(nodes)
      .force(
        'link',
        d3
          .forceLink<D3Node, D3Link>(links)
          .id((d) => d.id)
          .distance((d) => 100 * (1 - d.similarity + 0.3))
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    const g = svg.append('g');

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    const link = g
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#4b5563')
      .attr('stroke-opacity', (d) => 0.3 + d.similarity * 0.5)
      .attr('stroke-width', (d) => 1 + d.similarity * 2);

    const node = g
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGGElement, D3Node>('g')
      .data(nodes)
      .join('g')
      .attr('class', 'node')
      .style('cursor', 'pointer')
      .call(
        d3
          .drag<SVGGElement, D3Node>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    node
      .append('circle')
      .attr('r', (d) => (d.is_center ? 20 : 12 - d.depth * 2))
      .attr('fill', (d) => categoryColors[d.category] || categoryColors.default)
      .attr('stroke', (d) => (d.is_center ? '#fff' : 'none'))
      .attr('stroke-width', (d) => (d.is_center ? 3 : 0));

    node
      .append('text')
      .attr('dy', (d) => (d.is_center ? 35 : 25))
      .attr('text-anchor', 'middle')
      .attr('fill', '#e5e7eb')
      .attr('font-size', (d) => (d.is_center ? '12px' : '10px'))
      .attr('font-weight', (d) => (d.is_center ? 'bold' : 'normal'))
      .text((d) => {
        const maxLen = d.is_center ? 30 : 20;
        return d.title.length > maxLen ? d.title.slice(0, maxLen) + '...' : d.title;
      });

    node.on('click', (event, d) => {
      event.stopPropagation();
      setSelectedNode(d);
      if (onNodeClick) onNodeClick(d.id, d.title);
    });

    node
      .on('mouseenter', function () {
        d3.select(this).select('circle').attr('stroke', '#fff').attr('stroke-width', 2);
      })
      .on('mouseleave', function (event, d) {
        d3.select(this)
          .select('circle')
          .attr('stroke', d.is_center ? '#fff' : 'none')
          .attr('stroke-width', d.is_center ? 3 : 0);
      });

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as D3Node).x!)
        .attr('y1', (d) => (d.source as D3Node).y!)
        .attr('x2', (d) => (d.target as D3Node).x!)
        .attr('y2', (d) => (d.target as D3Node).y!);

      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });

    const centerNode = nodes.find((n) => n.is_center);
    if (centerNode) {
      centerNode.fx = width / 2;
      centerNode.fy = height / 2;
      setTimeout(() => {
        if (centerNode) {
          centerNode.fx = null;
          centerNode.fy = null;
        }
      }, 1500);
    }

    return () => simulation.stop();
  }, [graphData, dimensions, onNodeClick]);

  useEffect(() => {
    renderGraph();
  }, [renderGraph]);

  const getCategoryColor = (cat: string) => categoryColors[cat] || categoryColors.default;

  if (loading) {
    return (
      <div className="citation-graph citation-graph--loading">
        <div className="citation-graph__spinner" />
        <p>Loading similarity graph...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="citation-graph citation-graph--error">
        <p>{error}</p>
      </div>
    );
  }

  if (!graphData) {
    return (
      <div className="citation-graph citation-graph--empty">
        <p>Select a paper to view its similarity graph</p>
      </div>
    );
  }

  return (
    <div className="citation-graph" ref={containerRef}>
      <div className="citation-graph__header">
        <div className="citation-graph__stats">
          <span>{graphData.stats.total_nodes} papers</span>
          <span>{graphData.stats.total_edges} connections</span>
        </div>
        <div className="citation-graph__legend">
          {Object.entries(categoryColors)
            .filter(([k]) => k !== 'default')
            .slice(0, 5)
            .map(([cat, color]) => (
              <span key={cat} className="citation-graph__legend-item">
                <span className="citation-graph__legend-dot" style={{ backgroundColor: color }} />
                {cat}
              </span>
            ))}
        </div>
      </div>
      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        className="citation-graph__svg"
      />
      {selectedNode && (
        <div className="citation-graph__tooltip">
          <div className="citation-graph__tooltip-header">
            <span
              className="citation-graph__tooltip-cat"
              style={{ backgroundColor: getCategoryColor(selectedNode.category) }}
            >
              {selectedNode.category}
            </span>
            <button
              className="citation-graph__tooltip-close"
              onClick={() => setSelectedNode(null)}
            >
              &times;
            </button>
          </div>
          <h4>{selectedNode.title}</h4>
          <p className="citation-graph__tooltip-authors">
            {selectedNode.authors?.slice(0, 3).join(', ')}
            {selectedNode.authors?.length > 3 && ` +${selectedNode.authors.length - 3}`}
          </p>
          {selectedNode.published && (
            <p className="citation-graph__tooltip-date">
              {new Date(selectedNode.published).toLocaleDateString()}
            </p>
          )}
          <a
            href={`https://arxiv.org/abs/${selectedNode.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="citation-graph__tooltip-link"
          >
            View on arXiv
          </a>
        </div>
      )}
    </div>
  );
}
