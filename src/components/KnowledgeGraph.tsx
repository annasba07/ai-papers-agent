"use client";

import { useState, useEffect, useRef, useCallback, useMemo } from "react";

interface GraphNode {
  id: string;
  title: string;
  cited_by_count: number;
  level: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  fx?: number | null;
  fy?: number | null;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

interface CitationGraphData {
  center: string;
  nodes: Array<{
    id: string;
    title: string;
    cited_by_count: number;
    level: number;
  }>;
  edges: GraphEdge[];
  node_count: number;
  edge_count: number;
}

type KnowledgeGraphProps = {
  paperId: string;
  apiBaseUrl?: string;
  width?: number;
  height?: number;
  depth?: number;
  maxPapers?: number;
};

const COLORS = {
  center: "#4f46e5",
  level1: "#059669",
  level2: "#f59e0b",
  level3: "#ec4899",
  edge: "#94a3b8",
  edgeHighlight: "#4f46e5",
  text: "#0f172a",
  background: "#f8fafc",
};

const KnowledgeGraph = ({
  paperId,
  apiBaseUrl = "",
  width = 800,
  height = 600,
  depth = 1,
  maxPapers = 20,
}: KnowledgeGraphProps) => {
  const [graphData, setGraphData] = useState<CitationGraphData | null>(null);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [draggedNode, setDraggedNode] = useState<string | null>(null);

  const svgRef = useRef<SVGSVGElement>(null);
  const animationRef = useRef<number>();
  const simulationRunning = useRef(false);

  // Fetch graph data
  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      setError(null);

      try {
        const cleanId = paperId.split("v")[0];
        const params = new URLSearchParams({
          depth: depth.toString(),
          max_papers: maxPapers.toString(),
        });

        const endpoint = apiBaseUrl
          ? `${apiBaseUrl}/enrichment/papers/${cleanId}/citation-graph?${params}`
          : `/api/v1/enrichment/papers/${cleanId}/citation-graph?${params}`;

        const response = await fetch(endpoint);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: CitationGraphData = await response.json();
        setGraphData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch graph");
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [paperId, apiBaseUrl, depth, maxPapers]);

  // Initialize nodes with positions when graph data changes
  useEffect(() => {
    if (!graphData || graphData.nodes.length === 0) return;

    const centerX = width / 2;
    const centerY = height / 2;

    const initialNodes: GraphNode[] = graphData.nodes.map((node, i) => {
      // Position nodes in circles based on level
      const angle = (2 * Math.PI * i) / graphData.nodes.length;
      const radius = node.level === 0 ? 0 : 100 + node.level * 80;

      return {
        ...node,
        x: centerX + radius * Math.cos(angle) + (Math.random() - 0.5) * 20,
        y: centerY + radius * Math.sin(angle) + (Math.random() - 0.5) * 20,
        vx: 0,
        vy: 0,
      };
    });

    setNodes(initialNodes);
    setEdges(graphData.edges);
    simulationRunning.current = true;
  }, [graphData, width, height]);

  // Force simulation
  const simulate = useCallback(() => {
    if (!simulationRunning.current || nodes.length === 0) return;

    setNodes((prevNodes) => {
      const newNodes = prevNodes.map((node) => ({ ...node }));
      const centerX = width / 2;
      const centerY = height / 2;

      // Parameters
      const repulsionStrength = 5000;
      const attractionStrength = 0.01;
      const centeringStrength = 0.005;
      const dampening = 0.85;
      const minDistance = 60;

      // Reset velocities
      newNodes.forEach((node) => {
        if (node.fx !== undefined && node.fx !== null) {
          node.x = node.fx;
          node.vx = 0;
        }
        if (node.fy !== undefined && node.fy !== null) {
          node.y = node.fy;
          node.vy = 0;
        }
      });

      // Repulsion between all nodes
      for (let i = 0; i < newNodes.length; i++) {
        for (let j = i + 1; j < newNodes.length; j++) {
          const nodeA = newNodes[i];
          const nodeB = newNodes[j];

          const dx = nodeB.x - nodeA.x;
          const dy = nodeB.y - nodeA.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;

          if (distance < minDistance * 3) {
            const force = repulsionStrength / (distance * distance);
            const fx = (dx / distance) * force;
            const fy = (dy / distance) * force;

            if (nodeA.fx === undefined || nodeA.fx === null) {
              nodeA.vx -= fx;
              nodeA.vy -= fy;
            }
            if (nodeB.fx === undefined || nodeB.fx === null) {
              nodeB.vx += fx;
              nodeB.vy += fy;
            }
          }
        }
      }

      // Attraction along edges
      edges.forEach((edge) => {
        const sourceNode = newNodes.find((n) => n.id === edge.source);
        const targetNode = newNodes.find((n) => n.id === edge.target);

        if (sourceNode && targetNode) {
          const dx = targetNode.x - sourceNode.x;
          const dy = targetNode.y - sourceNode.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;

          const idealDistance = 120;
          const force = (distance - idealDistance) * attractionStrength;
          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;

          if (sourceNode.fx === undefined || sourceNode.fx === null) {
            sourceNode.vx += fx;
            sourceNode.vy += fy;
          }
          if (targetNode.fx === undefined || targetNode.fx === null) {
            targetNode.vx -= fx;
            targetNode.vy -= fy;
          }
        }
      });

      // Centering force
      newNodes.forEach((node) => {
        if (node.fx === undefined || node.fx === null) {
          node.vx += (centerX - node.x) * centeringStrength;
        }
        if (node.fy === undefined || node.fy === null) {
          node.vy += (centerY - node.y) * centeringStrength;
        }
      });

      // Apply velocities with dampening
      let totalMovement = 0;
      newNodes.forEach((node) => {
        if (node.fx === undefined || node.fx === null) {
          node.vx *= dampening;
          node.x += node.vx;
          node.x = Math.max(50, Math.min(width - 50, node.x));
          totalMovement += Math.abs(node.vx);
        }
        if (node.fy === undefined || node.fy === null) {
          node.vy *= dampening;
          node.y += node.vy;
          node.y = Math.max(50, Math.min(height - 50, node.y));
          totalMovement += Math.abs(node.vy);
        }
      });

      // Stop simulation when stable
      if (totalMovement < 0.5) {
        simulationRunning.current = false;
      }

      return newNodes;
    });

    animationRef.current = requestAnimationFrame(simulate);
  }, [nodes.length, edges, width, height]);

  // Run simulation
  useEffect(() => {
    if (simulationRunning.current) {
      animationRef.current = requestAnimationFrame(simulate);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [simulate]);

  // Node color based on level
  const getNodeColor = (level: number) => {
    switch (level) {
      case 0:
        return COLORS.center;
      case 1:
        return COLORS.level1;
      case 2:
        return COLORS.level2;
      default:
        return COLORS.level3;
    }
  };

  // Node radius based on citation count
  const getNodeRadius = (citedByCount: number, level: number) => {
    if (level === 0) return 25;
    const base = 12;
    const scaled = Math.min(20, Math.log(citedByCount + 1) * 3);
    return base + scaled;
  };

  // Handle node drag
  const handleMouseDown = (nodeId: string, e: React.MouseEvent) => {
    e.preventDefault();
    setDraggedNode(nodeId);
    setSelectedNode(nodeId);

    const node = nodes.find((n) => n.id === nodeId);
    if (node) {
      setNodes((prev) =>
        prev.map((n) =>
          n.id === nodeId ? { ...n, fx: n.x, fy: n.y } : n
        )
      );
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!draggedNode || !svgRef.current) return;

    const svg = svgRef.current;
    const rect = svg.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setNodes((prev) =>
      prev.map((n) =>
        n.id === draggedNode ? { ...n, x, y, fx: x, fy: y } : n
      )
    );
  };

  const handleMouseUp = () => {
    if (draggedNode) {
      setNodes((prev) =>
        prev.map((n) =>
          n.id === draggedNode ? { ...n, fx: null, fy: null } : n
        )
      );
      setDraggedNode(null);
      simulationRunning.current = true;
      animationRef.current = requestAnimationFrame(simulate);
    }
  };

  // Get connected edges for highlighting
  const getConnectedEdges = useMemo(() => {
    if (!hoveredNode && !selectedNode) return new Set<string>();
    const nodeId = hoveredNode || selectedNode;
    const connected = new Set<string>();
    edges.forEach((edge) => {
      if (edge.source === nodeId || edge.target === nodeId) {
        connected.add(`${edge.source}-${edge.target}`);
      }
    });
    return connected;
  }, [hoveredNode, selectedNode, edges]);

  // Get connected nodes for highlighting
  const getConnectedNodes = useMemo(() => {
    if (!hoveredNode && !selectedNode) return new Set<string>();
    const nodeId = hoveredNode || selectedNode;
    const connected = new Set<string>([nodeId!]);
    edges.forEach((edge) => {
      if (edge.source === nodeId) connected.add(edge.target);
      if (edge.target === nodeId) connected.add(edge.source);
    });
    return connected;
  }, [hoveredNode, selectedNode, edges]);

  if (loading) {
    return (
      <div className="knowledge-graph knowledge-graph--loading">
        <div className="knowledge-graph__spinner" />
        <p>Building citation network...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="knowledge-graph knowledge-graph--error">
        <p>Failed to load citation graph: {error}</p>
      </div>
    );
  }

  if (!graphData || nodes.length === 0) {
    return (
      <div className="knowledge-graph knowledge-graph--empty">
        <p>No citation data available for this paper.</p>
      </div>
    );
  }

  const selectedNodeData = selectedNode
    ? nodes.find((n) => n.id === selectedNode)
    : null;

  return (
    <div className="knowledge-graph">
      <div className="knowledge-graph__header">
        <h3>Citation Network</h3>
        <div className="knowledge-graph__legend">
          <span className="knowledge-graph__legend-item">
            <span style={{ background: COLORS.center }} />
            Center Paper
          </span>
          <span className="knowledge-graph__legend-item">
            <span style={{ background: COLORS.level1 }} />
            Direct Citations
          </span>
          {depth > 1 && (
            <span className="knowledge-graph__legend-item">
              <span style={{ background: COLORS.level2 }} />
              2nd Degree
            </span>
          )}
        </div>
      </div>

      <div className="knowledge-graph__container">
        <svg
          ref={svgRef}
          width={width}
          height={height}
          className="knowledge-graph__svg"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          {/* Background */}
          <rect width={width} height={height} fill={COLORS.background} />

          {/* Edges */}
          <g className="knowledge-graph__edges">
            {edges.map((edge) => {
              const source = nodes.find((n) => n.id === edge.source);
              const target = nodes.find((n) => n.id === edge.target);
              if (!source || !target) return null;

              const edgeKey = `${edge.source}-${edge.target}`;
              const isHighlighted = getConnectedEdges.has(edgeKey);

              return (
                <line
                  key={edgeKey}
                  x1={source.x}
                  y1={source.y}
                  x2={target.x}
                  y2={target.y}
                  stroke={isHighlighted ? COLORS.edgeHighlight : COLORS.edge}
                  strokeWidth={isHighlighted ? 2 : 1}
                  strokeOpacity={isHighlighted ? 0.8 : 0.3}
                  markerEnd="url(#arrowhead)"
                />
              );
            })}
          </g>

          {/* Arrow marker definition */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3.5, 0 7"
                fill={COLORS.edge}
                fillOpacity={0.5}
              />
            </marker>
          </defs>

          {/* Nodes */}
          <g className="knowledge-graph__nodes">
            {nodes.map((node) => {
              const radius = getNodeRadius(node.cited_by_count, node.level);
              const color = getNodeColor(node.level);
              const isConnected =
                getConnectedNodes.size === 0 || getConnectedNodes.has(node.id);
              const isHovered = hoveredNode === node.id;
              const isSelected = selectedNode === node.id;

              return (
                <g
                  key={node.id}
                  className="knowledge-graph__node"
                  transform={`translate(${node.x}, ${node.y})`}
                  onMouseEnter={() => setHoveredNode(node.id)}
                  onMouseLeave={() => setHoveredNode(null)}
                  onMouseDown={(e) => handleMouseDown(node.id, e)}
                  style={{ cursor: draggedNode ? "grabbing" : "grab" }}
                >
                  {/* Node circle */}
                  <circle
                    r={radius}
                    fill={color}
                    fillOpacity={isConnected ? 1 : 0.3}
                    stroke={isSelected ? "#0f172a" : isHovered ? "#fff" : "none"}
                    strokeWidth={isSelected ? 3 : isHovered ? 2 : 0}
                  />

                  {/* Citation count label */}
                  {node.cited_by_count > 0 && (
                    <text
                      dy="0.35em"
                      textAnchor="middle"
                      fill="#fff"
                      fontSize={radius > 15 ? "10" : "8"}
                      fontFamily="JetBrains Mono, monospace"
                      fontWeight="600"
                      style={{ pointerEvents: "none" }}
                    >
                      {node.cited_by_count > 999
                        ? `${(node.cited_by_count / 1000).toFixed(1)}k`
                        : node.cited_by_count}
                    </text>
                  )}

                  {/* Title label on hover */}
                  {(isHovered || isSelected) && (
                    <g transform={`translate(0, ${radius + 15})`}>
                      <rect
                        x={-100}
                        y={-10}
                        width={200}
                        height={20}
                        fill="rgba(15, 23, 42, 0.9)"
                        rx={4}
                      />
                      <text
                        textAnchor="middle"
                        fill="#fff"
                        fontSize="11"
                        fontFamily="Commissioner, sans-serif"
                        style={{ pointerEvents: "none" }}
                      >
                        {node.title.length > 35
                          ? `${node.title.slice(0, 35)}...`
                          : node.title}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* Info panel for selected node */}
        {selectedNodeData && (
          <div className="knowledge-graph__info">
            <button
              className="knowledge-graph__info-close"
              onClick={() => setSelectedNode(null)}
            >
              x
            </button>
            <h4>{selectedNodeData.title}</h4>
            <div className="knowledge-graph__info-stats">
              <span>
                <strong>{selectedNodeData.cited_by_count}</strong> citations
              </span>
              <span>Level {selectedNodeData.level}</span>
            </div>
            <a
              href={`https://arxiv.org/abs/${selectedNodeData.id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="knowledge-graph__info-link"
            >
              View on arXiv
            </a>
          </div>
        )}
      </div>

      <div className="knowledge-graph__stats">
        <span>{graphData.node_count} papers</span>
        <span>{graphData.edge_count} citations</span>
      </div>
    </div>
  );
};

export default KnowledgeGraph;
