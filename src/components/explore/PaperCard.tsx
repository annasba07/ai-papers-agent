"use client";

import { useState } from "react";
import Link from "next/link";
import type { ExplorePaper } from "@/types/Explore";

interface PaperCardProps {
  paper: ExplorePaper;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

export default function PaperCard({ paper, isExpanded, onToggleExpand }: PaperCardProps) {
  const [activeTab, setActiveTab] = useState<"summary" | "related" | "benchmarks">("summary");

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatAuthors = (authors: string[]) => {
    if (authors.length <= 3) {
      return authors.join(", ");
    }
    return `${authors.slice(0, 3).join(", ")} +${authors.length - 3} more`;
  };

  const getImpactScore = () => {
    return paper.deep_analysis?.impact_assessment?.impact_score ||
           paper.ai_analysis?.impactScore || null;
  };

  const getDifficulty = () => {
    return paper.deep_analysis?.reader_guidance?.difficulty_level ||
           paper.ai_analysis?.difficultyLevel || null;
  };

  const hasCode = () => {
    return paper.code_repos && paper.code_repos.length > 0;
  };

  const impactScore = getImpactScore();
  const difficulty = getDifficulty();

  return (
    <article className={`paper-card ${isExpanded ? "paper-card--expanded" : ""}`}>
      <div className="paper-card__header">
        <div className="paper-card__content">
          {/* Badges */}
          <div className="paper-card__badges">
            {impactScore && impactScore >= 7 && (
              <span className="badge badge-highlight">High Impact</span>
            )}
            {hasCode() && (
              <span className="badge badge-success">Has Code</span>
            )}
            {difficulty && (
              <span className="badge badge-muted">{difficulty}</span>
            )}
            {paper.category && (
              <span className="badge badge-accent">{paper.category}</span>
            )}
          </div>

          {/* Title */}
          <h3 className="paper-card__title">
            <a href={paper.link} target="_blank" rel="noopener noreferrer">
              {paper.title}
            </a>
          </h3>

          {/* Authors */}
          <p className="paper-card__authors">
            {formatAuthors(paper.authors)}
          </p>

          {/* Abstract */}
          {!isExpanded && (
            <p className="paper-card__abstract line-clamp-3">
              {paper.abstract}
            </p>
          )}
        </div>
      </div>

      {/* Meta Info */}
      <div className="paper-card__meta">
        <span className="paper-card__meta-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
          {formatDate(paper.published)}
        </span>

        {paper.citation_count > 0 && (
          <span className="paper-card__meta-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            {paper.citation_count.toLocaleString()} citations
          </span>
        )}

        {impactScore && (
          <span className="paper-card__meta-item">
            Impact: {impactScore}/10
          </span>
        )}

        <div className="paper-card__actions">
          <button className="paper-card__expand" onClick={onToggleExpand}>
            {isExpanded ? "Collapse" : "Expand"}
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              style={{ transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.2s" }}
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="paper-card__details">
          {/* Tabs */}
          <div className="paper-card__tabs">
            <button
              className={`paper-card__tab ${activeTab === "summary" ? "paper-card__tab--active" : ""}`}
              onClick={() => setActiveTab("summary")}
            >
              Summary
            </button>
            <button
              className={`paper-card__tab ${activeTab === "related" ? "paper-card__tab--active" : ""}`}
              onClick={() => setActiveTab("related")}
            >
              Related Papers
            </button>
            <button
              className={`paper-card__tab ${activeTab === "benchmarks" ? "paper-card__tab--active" : ""}`}
              onClick={() => setActiveTab("benchmarks")}
            >
              Benchmarks
            </button>
          </div>

          {/* Tab Content */}
          <div className="paper-card__tab-content">
            {activeTab === "summary" && (
              <div className="paper-detail-summary">
                <h4 className="text-sm font-semibold text-secondary" style={{ marginBottom: "0.5rem" }}>
                  Full Abstract
                </h4>
                <p className="text-sm" style={{ lineHeight: 1.7 }}>
                  {paper.abstract}
                </p>

                {paper.ai_analysis?.keyContribution && (
                  <>
                    <h4 className="text-sm font-semibold text-secondary" style={{ marginTop: "1rem", marginBottom: "0.5rem" }}>
                      Key Contribution
                    </h4>
                    <p className="text-sm" style={{ lineHeight: 1.7 }}>
                      {paper.ai_analysis.keyContribution}
                    </p>
                  </>
                )}

                {hasCode() && (
                  <div style={{ marginTop: "1rem" }}>
                    <h4 className="text-sm font-semibold text-secondary" style={{ marginBottom: "0.5rem" }}>
                      Code Repository
                    </h4>
                    {paper.code_repos?.map((repo, i) => (
                      <a
                        key={i}
                        href={repo}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-secondary btn-sm"
                        style={{ marginRight: "0.5rem" }}
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                        </svg>
                        View Code
                      </a>
                    ))}
                  </div>
                )}

                <div style={{ marginTop: "1.5rem", display: "flex", gap: "0.75rem" }}>
                  <a
                    href={paper.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary"
                  >
                    Read on arXiv
                  </a>
                  <Link
                    href={`/generate?paper=${paper.id}`}
                    className="btn btn-primary"
                  >
                    Generate Code
                  </Link>
                </div>
              </div>
            )}

            {activeTab === "related" && (
              <div className="paper-detail-related">
                <p className="text-secondary text-sm">
                  Related papers will be loaded based on semantic similarity and shared concepts.
                </p>
                {/* This would fetch from /papers/similar/{id} */}
              </div>
            )}

            {activeTab === "benchmarks" && (
              <div className="paper-detail-benchmarks">
                <p className="text-secondary text-sm">
                  Benchmark results and SOTA comparisons for this paper.
                </p>
                {/* This would fetch from /leaderboards/paper/{id} */}
              </div>
            )}
          </div>
        </div>
      )}
    </article>
  );
}
