"use client";

import { useState, useEffect } from "react";
import type { CitationData } from "@/types/Paper";

type CitationBadgeProps = {
  paperId: string;
  citations?: CitationData;
  apiBaseUrl?: string;
  compact?: boolean;
};

const CitationBadge = ({
  paperId,
  citations: initialCitations,
  apiBaseUrl = "",
  compact = false,
}: CitationBadgeProps) => {
  const [citations, setCitations] = useState<CitationData | null>(initialCitations || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    // If we already have citation data, don't fetch
    if (initialCitations || citations) return;

    const fetchCitations = async () => {
      setLoading(true);
      setError(false);

      try {
        // Clean the paper ID (remove version suffix)
        const cleanId = paperId.split("v")[0];
        const endpoint = apiBaseUrl
          ? `${apiBaseUrl}/enrichment/papers/${cleanId}/citations`
          : `/api/v1/enrichment/papers/${cleanId}/citations`;

        const response = await fetch(endpoint);
        if (!response.ok) {
          if (response.status === 404) {
            // No citation data available is not an error
            setCitations(null);
            return;
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setCitations(data);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    // Fetch after a small delay to prevent too many concurrent requests
    const timer = setTimeout(fetchCitations, 100);
    return () => clearTimeout(timer);
  }, [paperId, initialCitations, citations, apiBaseUrl]);

  if (loading) {
    return (
      <span className="citation-badge citation-badge--loading">
        <span className="citation-badge__spinner" />
      </span>
    );
  }

  if (error || !citations) {
    return null; // Don't show anything if no data
  }

  if (compact) {
    return (
      <span className="citation-badge citation-badge--compact" title="Citation count from OpenAlex">
        <span className="citation-badge__icon">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18M3 12h18M3 18h18" />
          </svg>
        </span>
        <span className="citation-badge__count">{citations.cited_by_count}</span>
      </span>
    );
  }

  return (
    <div className="citation-badge">
      <div className="citation-badge__header" onClick={() => setExpanded(!expanded)}>
        <div className="citation-badge__stats">
          <div className="citation-badge__stat">
            <span className="citation-badge__value">{citations.cited_by_count}</span>
            <span className="citation-badge__label">Citations</span>
          </div>
          <div className="citation-badge__stat">
            <span className="citation-badge__value">{citations.references_count}</span>
            <span className="citation-badge__label">References</span>
          </div>
        </div>
        {citations.concepts && citations.concepts.length > 0 && (
          <button className="citation-badge__expand" title={expanded ? "Hide concepts" : "Show concepts"}>
            {expanded ? "−" : "+"}
          </button>
        )}
      </div>

      {expanded && citations.concepts && citations.concepts.length > 0 && (
        <div className="citation-badge__concepts">
          <span className="citation-badge__concepts-label">Research Concepts:</span>
          <div className="citation-badge__concepts-list">
            {citations.concepts.slice(0, 5).map((concept, idx) => (
              <span
                key={idx}
                className="citation-badge__concept"
                style={{
                  opacity: Math.max(0.5, concept.score),
                }}
              >
                {concept.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {citations.openalex_id && (
        <a
          href={`https://openalex.org/${citations.openalex_id}`}
          target="_blank"
          rel="noopener noreferrer"
          className="citation-badge__link"
        >
          View on OpenAlex →
        </a>
      )}
    </div>
  );
};

export default CitationBadge;
