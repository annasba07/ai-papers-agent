"use client";

import React, { useState, useEffect, useRef, useCallback, useMemo } from "react";

interface LineageNode {
  paper_id: string;
  title: string;
  relationship: string;
  description: string | null;
  depth: number;
  published_date: string | null;
  citation_count: number | null;
}

interface LineageData {
  paper_id: string;
  ancestors: LineageNode[];
  descendants: LineageNode[];
}

interface GraphNode extends LineageNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
  fx?: number | null;
  fy?: number | null;
  isCenter: boolean;
  direction: 'ancestor' | 'descendant' | 'center';
}

interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
  description: string | null;
}

type PaperLineageGraphProps = {
  paperId: string;
  paperTitle?: string;
  apiBaseUrl?: string;
  width?: number;
  height?: number;
  maxDepth?: number;
};

const RELATIONSHIP_COLORS: Record<string, string> = {
  'builds_on': '#4f46e5',
  'extends': '#059669',
  'improves': '#f59e0b',
  'applies': '#0ea5e9',
  'compares_to': '#ec4899',
  'alternative_to': '#7c3aed',
  'cites': '#94a3b8',
  'default': '#64748b',
};

const COLORS = {
  center: '#0f172a',
  ancestor: '#059669',
  descendant: '#f59e0b',
  edge: '#94a3b8',
  edgeHighlight: '#4f46e5',
  text: '#0f172a',
  background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
};

const getRelationshipColor = (relationship: string): string => {
  return RELATIONSHIP_COLORS[relationship] || RELATIONSHIP_COLORS.default;
};

const getRelationshipLabel = (relationship: string): string => {
  const labels: Record<string, string> = {
    'builds_on': 'Builds on',
    'extends': 'Extends',
    'improves': 'Improves',
    'applies': 'Applies',
    'compares_to': 'Compares to',
    'alternative_to': 'Alternative to',
    'cites': 'Cites',
  };
  return labels[relationship] || relationship;
};

const PaperLineageGraph: React.FC<PaperLineageGraphProps> = ({
  paperId,
  paperTitle = 'Current Paper',
  apiBaseUrl = 'http://localhost:8000/api/v1',
  width = 800,
  height = 600,
  maxDepth = 3,
}) => {
  const [lineageData, setLineageData] = useState<LineageData | null>(null);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [draggedNode, setDraggedNode] = useState<string | null>(null);

  const svgRef = useRef<SVGSVGElement>(null);
  const animationRef = useRef<number | undefined>(undefined);
  const simulationRunning = useRef(false);

  // Fetch lineage data
  useEffect(() => {
    const fetchLineage = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `${apiBaseUrl}/data-moat/lineage/${paperId}?max_depth=${maxDepth}`
        );

        if (!response.ok) {
          if (response.status === 404) {
            setLineageData({ paper_id: paperId, ancestors: [], descendants: [] });
          } else {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        } else {
          const data: LineageData = await response.json();
          setLineageData(data);
        }
      } catch (err) {
        console.error('Error fetching lineage:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch lineage');
      } finally {
        setLoading(false);
      }
    };

    fetchLineage();
  }, [paperId, apiBaseUrl, maxDepth]);

  // Initialize nodes with positions when lineage data changes
  useEffect(() => {
    if (!lineageData) return;

    const centerX = width / 2;
    const centerY = height / 2;

    // Create center node
    const centerNode: GraphNode = {
      paper_id: paperId,
      title: paperTitle,
      relationship: 'center',
      description: null,
      depth: 0,
      published_date: null,
      citation_count: null,
      x: centerX,
      y: centerY,
      vx: 0,
      vy: 0,
      isCenter: true,
      direction: 'center',
    };

    const graphNodes: GraphNode[] = [centerNode];
    const graphEdges: GraphEdge[] = [];

    // Add ancestors (above center)
    const ancestorsByDepth: Record<number, LineageNode[]> = {};
    lineageData.ancestors.forEach((a) => {
      if (!ancestorsByDepth[a.depth]) ancestorsByDepth[a.depth] = [];
      ancestorsByDepth[a.depth].push(a);
    });

    Object.entries(ancestorsByDepth).forEach(([depthStr, ancestors]) => {
      const depth = parseInt(depthStr);
      const yOffset = -120 - (depth - 1) * 100;
      const spacing = width / (ancestors.length + 1);

      ancestors.forEach((ancestor, i) => {
        graphNodes.push({
          ...ancestor,
          x: spacing * (i + 1) + (Math.random() - 0.5) * 30,
          y: centerY + yOffset + (Math.random() - 0.5) * 20,
          vx: 0,
          vy: 0,
          isCenter: false,
          direction: 'ancestor',
        });

        // Find parent to connect to (or center if depth 1)
        const targetId = depth === 1 ? paperId : lineageData.ancestors.find(
          (a) => a.depth === depth - 1 && Math.random() > 0.5
        )?.paper_id || paperId;

        graphEdges.push({
          source: ancestor.paper_id,
          target: targetId,
          relationship: ancestor.relationship,
          description: ancestor.description,
        });
      });
    });

    // Add descendants (below center)
    const descendantsByDepth: Record<number, LineageNode[]> = {};
    lineageData.descendants.forEach((d) => {
      if (!descendantsByDepth[d.depth]) descendantsByDepth[d.depth] = [];
      descendantsByDepth[d.depth].push(d);
    });

    Object.entries(descendantsByDepth).forEach(([depthStr, descendants]) => {
      const depth = parseInt(depthStr);
      const yOffset = 120 + (depth - 1) * 100;
      const spacing = width / (descendants.length + 1);

      descendants.forEach((descendant, i) => {
        graphNodes.push({
          ...descendant,
          x: spacing * (i + 1) + (Math.random() - 0.5) * 30,
          y: centerY + yOffset + (Math.random() - 0.5) * 20,
          vx: 0,
          vy: 0,
          isCenter: false,
          direction: 'descendant',
        });

        graphEdges.push({
          source: paperId,
          target: descendant.paper_id,
          relationship: descendant.relationship,
          description: descendant.description,
        });
      });
    });

    setNodes(graphNodes);
    setEdges(graphEdges);
    simulationRunning.current = graphNodes.length > 1;
  }, [lineageData, paperId, paperTitle, width, height]);

  // Force simulation
  const simulate = useCallback(() => {
    if (!simulationRunning.current || nodes.length === 0) return;

    setNodes((prevNodes) => {
      const newNodes = prevNodes.map((node) => ({ ...node }));
      const centerX = width / 2;
      const centerY = height / 2;

      const repulsionStrength = 3000;
      const attractionStrength = 0.02;
      const verticalBias = 0.1;
      const dampening = 0.85;

      // Reset velocities for fixed nodes
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

      // Repulsion between nodes at same level
      for (let i = 0; i < newNodes.length; i++) {
        for (let j = i + 1; j < newNodes.length; j++) {
          const nodeA = newNodes[i];
          const nodeB = newNodes[j];

          if (nodeA.direction === nodeB.direction) {
            const dx = nodeB.x - nodeA.x;
            const dy = nodeB.y - nodeA.y;
            const distance = Math.sqrt(dx * dx + dy * dy) || 1;

            if (distance < 200) {
              const force = repulsionStrength / (distance * distance);
              const fx = (dx / distance) * force;

              if (nodeA.fx === undefined || nodeA.fx === null) {
                nodeA.vx -= fx;
              }
              if (nodeB.fx === undefined || nodeB.fx === null) {
                nodeB.vx += fx;
              }
            }
          }
        }
      }

      // Attraction along edges
      edges.forEach((edge) => {
        const sourceNode = newNodes.find((n) => n.paper_id === edge.source);
        const targetNode = newNodes.find((n) => n.paper_id === edge.target);

        if (sourceNode && targetNode) {
          const dx = targetNode.x - sourceNode.x;
          const dy = targetNode.y - sourceNode.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;

          const idealDistance = 150;
          const force = (distance - idealDistance) * attractionStrength;
          const fx = (dx / distance) * force;

          if (!sourceNode.isCenter && (sourceNode.fx === undefined || sourceNode.fx === null)) {
            sourceNode.vx += fx * 0.5;
          }
          if (!targetNode.isCenter && (targetNode.fx === undefined || targetNode.fx === null)) {
            targetNode.vx -= fx * 0.5;
          }
        }
      });

      // Vertical separation bias (ancestors up, descendants down)
      newNodes.forEach((node) => {
        if (node.isCenter) return;

        const targetY = node.direction === 'ancestor'
          ? centerY - 120 - (node.depth - 1) * 100
          : centerY + 120 + (node.depth - 1) * 100;

        if (node.fy === undefined || node.fy === null) {
          node.vy += (targetY - node.y) * verticalBias;
        }

        // Horizontal centering
        if (node.fx === undefined || node.fx === null) {
          node.vx += (centerX - node.x) * 0.005;
        }
      });

      // Apply velocities with dampening
      let totalMovement = 0;
      newNodes.forEach((node) => {
        if (node.fx === undefined || node.fx === null) {
          node.vx *= dampening;
          node.x += node.vx;
          node.x = Math.max(60, Math.min(width - 60, node.x));
          totalMovement += Math.abs(node.vx);
        }
        if (node.fy === undefined || node.fy === null) {
          node.vy *= dampening;
          node.y += node.vy;
          node.y = Math.max(60, Math.min(height - 60, node.y));
          totalMovement += Math.abs(node.vy);
        }
      });

      if (totalMovement < 0.3) {
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

  // Handle node drag
  const handleMouseDown = (nodeId: string, e: React.MouseEvent) => {
    e.preventDefault();
    setDraggedNode(nodeId);
    setSelectedNode(nodeId);

    setNodes((prev) =>
      prev.map((n) =>
        n.paper_id === nodeId ? { ...n, fx: n.x, fy: n.y } : n
      )
    );
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!draggedNode || !svgRef.current) return;

    const svg = svgRef.current;
    const rect = svg.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setNodes((prev) =>
      prev.map((n) =>
        n.paper_id === draggedNode ? { ...n, x, y, fx: x, fy: y } : n
      )
    );
  };

  const handleMouseUp = () => {
    if (draggedNode) {
      setNodes((prev) =>
        prev.map((n) =>
          n.paper_id === draggedNode ? { ...n, fx: null, fy: null } : n
        )
      );
      setDraggedNode(null);
      simulationRunning.current = true;
      animationRef.current = requestAnimationFrame(simulate);
    }
  };

  // Get connected edges for highlighting
  const connectedEdges = useMemo(() => {
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

  // Get node radius
  const getNodeRadius = (node: GraphNode): number => {
    if (node.isCenter) return 28;
    const citations = node.citation_count || 0;
    return 14 + Math.min(10, Math.log(citations + 1) * 2);
  };

  // Get node color
  const getNodeColor = (node: GraphNode): string => {
    if (node.isCenter) return COLORS.center;
    return node.direction === 'ancestor' ? COLORS.ancestor : COLORS.descendant;
  };

  const selectedNodeData = selectedNode
    ? nodes.find((n) => n.paper_id === selectedNode)
    : null;

  if (loading) {
    return (
      <div className="lineage-graph lineage-graph--loading">
        <div className="lineage-graph__spinner" />
        <p>Tracing paper lineage...</p>
        <style jsx>{`
          .lineage-graph--loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 300px;
            gap: 16px;
            color: var(--secondary-text, #64748b);
          }
          .lineage-graph__spinner {
            width: 32px;
            height: 32px;
            border: 3px solid rgba(79, 70, 229, 0.2);
            border-top-color: var(--accent-indigo, #4f46e5);
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lineage-graph lineage-graph--error">
        <p>Failed to load lineage: {error}</p>
        <style jsx>{`
          .lineage-graph--error {
            padding: 24px;
            text-align: center;
            color: #dc2626;
            background: rgba(220, 38, 38, 0.1);
            border-radius: 12px;
          }
        `}</style>
      </div>
    );
  }

  const hasData = lineageData && (lineageData.ancestors.length > 0 || lineageData.descendants.length > 0);

  if (!hasData) {
    return (
      <div className="lineage-graph lineage-graph--empty">
        <span style={{ fontSize: '2rem', marginBottom: '8px' }}>🔗</span>
        <p>No semantic relationships found yet</p>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          Relationships are extracted from paper analysis
        </p>
        <style jsx>{`
          .lineage-graph--empty {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 200px;
            color: var(--secondary-text, #64748b);
            text-align: center;
            padding: 24px;
          }
          .lineage-graph--empty p {
            margin: 4px 0;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="lineage-graph">
      <div className="lineage-graph__header">
        <h4>Paper Lineage</h4>
        <div className="lineage-graph__legend">
          <span className="legend-item">
            <span className="legend-dot" style={{ background: COLORS.ancestor }} />
            Builds On ({lineageData?.ancestors.length || 0})
          </span>
          <span className="legend-item">
            <span className="legend-dot" style={{ background: COLORS.descendant }} />
            Built Upon By ({lineageData?.descendants.length || 0})
          </span>
        </div>
      </div>

      <div className="lineage-graph__container">
        <svg
          ref={svgRef}
          width={width}
          height={height}
          className="lineage-graph__svg"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <defs>
            <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f8fafc" />
              <stop offset="100%" stopColor="#f1f5f9" />
            </linearGradient>
            <marker
              id="lineage-arrow"
              markerWidth="8"
              markerHeight="6"
              refX="8"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill={COLORS.edge} fillOpacity={0.6} />
            </marker>
          </defs>

          <rect width={width} height={height} fill="url(#bgGradient)" />

          {/* Direction labels */}
          <text
            x={width / 2}
            y={30}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="12"
            fontFamily="Commissioner, sans-serif"
          >
            FOUNDATIONAL PAPERS
          </text>
          <text
            x={width / 2}
            y={height - 15}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="12"
            fontFamily="Commissioner, sans-serif"
          >
            DERIVATIVE WORKS
          </text>

          {/* Edges */}
          <g className="lineage-graph__edges">
            {edges.map((edge) => {
              const source = nodes.find((n) => n.paper_id === edge.source);
              const target = nodes.find((n) => n.paper_id === edge.target);
              if (!source || !target) return null;

              const edgeKey = `${edge.source}-${edge.target}`;
              const isHighlighted = connectedEdges.has(edgeKey);
              const edgeColor = getRelationshipColor(edge.relationship);

              // Calculate control point for curved edge
              const midX = (source.x + target.x) / 2;
              const midY = (source.y + target.y) / 2;
              const dx = target.x - source.x;
              const curveOffset = Math.abs(dx) * 0.2;

              return (
                <g key={edgeKey}>
                  <path
                    d={`M ${source.x} ${source.y} Q ${midX + curveOffset} ${midY} ${target.x} ${target.y}`}
                    fill="none"
                    stroke={isHighlighted ? edgeColor : COLORS.edge}
                    strokeWidth={isHighlighted ? 2.5 : 1.5}
                    strokeOpacity={isHighlighted ? 0.9 : 0.4}
                    markerEnd="url(#lineage-arrow)"
                  />
                  {/* Relationship label on hover */}
                  {isHighlighted && (
                    <text
                      x={midX}
                      y={midY - 8}
                      textAnchor="middle"
                      fill={edgeColor}
                      fontSize="10"
                      fontWeight="600"
                      fontFamily="Commissioner, sans-serif"
                    >
                      {getRelationshipLabel(edge.relationship)}
                    </text>
                  )}
                </g>
              );
            })}
          </g>

          {/* Nodes */}
          <g className="lineage-graph__nodes">
            {nodes.map((node) => {
              const radius = getNodeRadius(node);
              const color = getNodeColor(node);
              const isHovered = hoveredNode === node.paper_id;
              const isSelected = selectedNode === node.paper_id;

              return (
                <g
                  key={node.paper_id}
                  transform={`translate(${node.x}, ${node.y})`}
                  onMouseEnter={() => setHoveredNode(node.paper_id)}
                  onMouseLeave={() => setHoveredNode(null)}
                  onMouseDown={(e) => handleMouseDown(node.paper_id, e)}
                  style={{ cursor: draggedNode ? 'grabbing' : 'grab' }}
                >
                  {/* Glow effect */}
                  {(isHovered || isSelected) && (
                    <circle
                      r={radius + 6}
                      fill={color}
                      fillOpacity={0.2}
                    />
                  )}

                  {/* Node circle */}
                  <circle
                    r={radius}
                    fill={color}
                    stroke={isSelected ? '#0f172a' : isHovered ? '#fff' : 'rgba(255,255,255,0.5)'}
                    strokeWidth={isSelected ? 3 : isHovered ? 2 : 1}
                  />

                  {/* Icon or label */}
                  <text
                    dy="0.35em"
                    textAnchor="middle"
                    fill="#fff"
                    fontSize={node.isCenter ? '14' : '10'}
                    fontWeight="600"
                    style={{ pointerEvents: 'none' }}
                  >
                    {node.isCenter ? '★' : node.depth}
                  </text>

                  {/* Title tooltip */}
                  {(isHovered || isSelected) && (
                    <g transform={`translate(0, ${radius + 20})`}>
                      <rect
                        x={-120}
                        y={-12}
                        width={240}
                        height={24}
                        fill="rgba(15, 23, 42, 0.95)"
                        rx={6}
                      />
                      <text
                        textAnchor="middle"
                        fill="#fff"
                        fontSize="11"
                        fontFamily="Commissioner, sans-serif"
                        style={{ pointerEvents: 'none' }}
                      >
                        {node.title.length > 40
                          ? `${node.title.slice(0, 40)}...`
                          : node.title}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* Info panel */}
        {selectedNodeData && !selectedNodeData.isCenter && (
          <div className="lineage-graph__info">
            <button
              className="info-close"
              onClick={() => setSelectedNode(null)}
            >
              x
            </button>
            <h5>{selectedNodeData.title}</h5>
            <div className="info-meta">
              <span
                className="relationship-badge"
                style={{ background: getRelationshipColor(selectedNodeData.relationship) }}
              >
                {getRelationshipLabel(selectedNodeData.relationship)}
              </span>
              {selectedNodeData.citation_count !== null && (
                <span>{selectedNodeData.citation_count} citations</span>
              )}
              {selectedNodeData.published_date && (
                <span>{new Date(selectedNodeData.published_date).getFullYear()}</span>
              )}
            </div>
            {selectedNodeData.description && (
              <p className="info-description">{selectedNodeData.description}</p>
            )}
            <a
              href={`https://arxiv.org/abs/${selectedNodeData.paper_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="info-link"
            >
              View Paper
            </a>
          </div>
        )}
      </div>

      <style jsx>{`
        .lineage-graph {
          background: white;
          border-radius: 16px;
          overflow: hidden;
          border: 1px solid rgba(148, 163, 184, 0.2);
        }

        .lineage-graph__header {
          padding: 16px 20px;
          border-bottom: 1px solid rgba(148, 163, 184, 0.15);
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 12px;
        }

        .lineage-graph__header h4 {
          margin: 0;
          font-size: 1rem;
          font-weight: 600;
          color: var(--primary-text, #0f172a);
        }

        .lineage-graph__legend {
          display: flex;
          gap: 16px;
          font-size: 0.8rem;
          color: var(--secondary-text, #64748b);
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .legend-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }

        .lineage-graph__container {
          position: relative;
        }

        .lineage-graph__svg {
          display: block;
        }

        .lineage-graph__info {
          position: absolute;
          bottom: 16px;
          left: 16px;
          right: 16px;
          background: white;
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
          border: 1px solid rgba(148, 163, 184, 0.2);
        }

        .info-close {
          position: absolute;
          top: 8px;
          right: 12px;
          background: none;
          border: none;
          font-size: 1.2rem;
          color: var(--secondary-text, #64748b);
          cursor: pointer;
          padding: 4px 8px;
        }

        .info-close:hover {
          color: var(--primary-text, #0f172a);
        }

        .lineage-graph__info h5 {
          margin: 0 0 8px 0;
          font-size: 0.95rem;
          font-weight: 600;
          color: var(--primary-text, #0f172a);
          padding-right: 24px;
        }

        .info-meta {
          display: flex;
          gap: 10px;
          align-items: center;
          flex-wrap: wrap;
          margin-bottom: 8px;
          font-size: 0.8rem;
          color: var(--secondary-text, #64748b);
        }

        .relationship-badge {
          padding: 2px 8px;
          border-radius: 12px;
          color: white;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .info-description {
          font-size: 0.85rem;
          color: var(--secondary-text, #475569);
          margin: 8px 0;
          line-height: 1.5;
        }

        .info-link {
          display: inline-block;
          font-size: 0.85rem;
          color: var(--accent-indigo, #4f46e5);
          text-decoration: none;
          font-weight: 500;
        }

        .info-link:hover {
          text-decoration: underline;
        }
      `}</style>
    </div>
  );
};

export default PaperLineageGraph;
