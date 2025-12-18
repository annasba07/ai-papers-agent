"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import type { ExplorePaper } from "@/types/Explore";

interface SimilarPaper {
  id: string;
  title: string;
  abstract: string;
  published_date: string;
  category: string;
  citation_count: number;
  similarity: number;
}

interface PaperCardProps {
  paper: ExplorePaper;
  isExpanded: boolean;
  onToggleExpand: () => void;
  variant?: "default" | "semantic";
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export default function PaperCard({ paper, isExpanded, onToggleExpand, variant = "default" }: PaperCardProps) {
  const [activeTab, setActiveTab] = useState<"summary" | "related" | "benchmarks">("summary");
  const [relatedPapers, setRelatedPapers] = useState<SimilarPaper[]>([]);
  const [relatedLoading, setRelatedLoading] = useState(false);
  const [relatedError, setRelatedError] = useState<string | null>(null);
  const [hasFetchedRelated, setHasFetchedRelated] = useState(false);

  // Fetch related papers when tab is activated
  useEffect(() => {
    if (isExpanded && activeTab === "related" && !hasFetchedRelated && !relatedLoading) {
      const fetchRelatedPapers = async () => {
        setRelatedLoading(true);
        setRelatedError(null);
        try {
          const endpoint = API_BASE
            ? `${API_BASE}/knowledge-graph/papers/${paper.id}/similar`
            : `/api/related-papers/${paper.id}`;

          const response = await fetch(endpoint);
          if (!response.ok) {
            throw new Error("Failed to fetch related papers");
          }
          const data = await response.json();
          setRelatedPapers(data.similar_papers || data || []);
          setHasFetchedRelated(true);
        } catch (err) {
          setRelatedError(err instanceof Error ? err.message : "Failed to load related papers");
        } finally {
          setRelatedLoading(false);
        }
      };
      fetchRelatedPapers();
    }
  }, [isExpanded, activeTab, hasFetchedRelated, relatedLoading, paper.id]);

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

  const getTldr = () => {
    // Priority: ai_analysis.summary > keyContribution > truncated abstract
    if (paper.ai_analysis?.summary) {
      return paper.ai_analysis.summary;
    }
    if (paper.ai_analysis?.keyContribution) {
      return paper.ai_analysis.keyContribution;
    }
    // Generate a quick TL;DR from the abstract (first 2 sentences or ~150 chars)
    const abstract = paper.abstract || "";
    const sentences = abstract.split(/(?<=[.!?])\s+/);
    if (sentences.length >= 2) {
      const twoSentences = sentences.slice(0, 2).join(" ");
      if (twoSentences.length <= 250) {
        return twoSentences;
      }
    }
    // Fallback to first 150 chars with ellipsis
    if (abstract.length > 150) {
      return abstract.substring(0, 150).trim() + "...";
    }
    return abstract;
  };

  const getDifficulty = () => {
    return paper.deep_analysis?.reader_guidance?.difficulty_level ||
           paper.ai_analysis?.difficultyLevel || null;
  };

  const hasCode = () => {
    return paper.code_repos && paper.code_repos.length > 0;
  };

  const getGitHubStats = () => {
    return paper.external_signals?.github || null;
  };

  const formatStars = (stars: number): string => {
    if (stars >= 1000) {
      return `${(stars / 1000).toFixed(1)}k`;
    }
    return stars.toString();
  };

  const formatRelativeTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "today";
    if (diffDays === 1) return "yesterday";
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo ago`;
    return `${Math.floor(diffDays / 365)}y ago`;
  };

  const isRecentlyUpdated = (dateStr: string): boolean => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24);
    return diffDays < 90; // Updated within last 3 months
  };

  const impactScore = getImpactScore();
  const difficulty = getDifficulty();
  const githubStats = getGitHubStats();

  return (
    <article className={`paper-card ${isExpanded ? "paper-card--expanded" : ""} ${variant === "semantic" ? "paper-card--semantic" : ""}`}>
      <div className="paper-card__header">
        <div className="paper-card__content">
          {/* Badges */}
          <div className="paper-card__badges">
            {impactScore && impactScore >= 7 && (
              <span className="badge badge-highlight">High Impact</span>
            )}
            {githubStats && githubStats.total_stars >= 100 && (
              <span className="badge badge-github">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 .587l3.668 7.568 8.332 1.151-6.064 5.828 1.48 8.279-7.416-3.967-7.417 3.967 1.481-8.279-6.064-5.828 8.332-1.151z"/>
                </svg>
                {formatStars(githubStats.total_stars)}
              </span>
            )}
            {hasCode() && (
              <a
                href={githubStats?.repos?.[0]?.url || paper.code_repos?.[0]}
                target="_blank"
                rel="noopener noreferrer"
                className="badge badge-success badge-link"
                onClick={(e) => e.stopPropagation()}
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
                View Code
              </a>
            )}
            {githubStats?.repos?.[0]?.pushed_at && isRecentlyUpdated(githubStats.repos[0].pushed_at) && (
              <span className="badge badge-active">Active</span>
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

          {/* TL;DR - Quick summary for scanning */}
          {!isExpanded && (
            <div className="paper-card__tldr">
              <span className="paper-card__tldr-label">TL;DR</span>
              <p className="paper-card__tldr-text">{getTldr()}</p>
            </div>
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

        {/* GitHub Stats Inline */}
        {githubStats && githubStats.repos && githubStats.repos.length > 0 && (
          <span className="paper-card__github-stats">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="paper-card__github-icon">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            <span className="paper-card__github-stat">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 .587l3.668 7.568 8.332 1.151-6.064 5.828 1.48 8.279-7.416-3.967-7.417 3.967 1.481-8.279-6.064-5.828 8.332-1.151z"/>
              </svg>
              {formatStars(githubStats.total_stars)}
            </span>
            {githubStats.repos[0].forks > 0 && (
              <span className="paper-card__github-stat">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="18" r="3" />
                  <circle cx="6" cy="6" r="3" />
                  <circle cx="18" cy="6" r="3" />
                  <path d="M18 9v1a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V9" />
                  <line x1="12" y1="12" x2="12" y2="15" />
                </svg>
                {formatStars(githubStats.repos[0].forks)}
              </span>
            )}
            {githubStats.repos[0].language && (
              <span className="paper-card__github-lang">{githubStats.repos[0].language}</span>
            )}
            {githubStats.repos[0].pushed_at && (
              <span className="paper-card__github-updated">
                {formatRelativeTime(githubStats.repos[0].pushed_at)}
              </span>
            )}
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
              className={`paper-card__expand-icon ${isExpanded ? "paper-card__expand-icon--rotated" : ""}`}
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
                <h4 className="text-sm font-semibold text-secondary paper-detail__heading">
                  Full Abstract
                </h4>
                <p className="text-sm paper-detail__text">
                  {paper.abstract}
                </p>

                {paper.ai_analysis?.keyContribution && (
                  <>
                    <h4 className="text-sm font-semibold text-secondary paper-detail__heading--spaced">
                      Key Contribution
                    </h4>
                    <p className="text-sm paper-detail__text">
                      {paper.ai_analysis.keyContribution}
                    </p>
                  </>
                )}

                {/* Enhanced GitHub Repository Section */}
                {githubStats && githubStats.repos && githubStats.repos.length > 0 ? (
                  <div className="paper-detail__section paper-detail__github">
                    <h4 className="text-sm font-semibold text-secondary paper-detail__heading">
                      Code Repositories
                    </h4>
                    <div className="github-repos">
                      {githubStats.repos.map((repo, i) => (
                        <div key={i} className="github-repo-card">
                          <div className="github-repo-card__header">
                            <a
                              href={repo.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="github-repo-card__name"
                            >
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                              </svg>
                              {repo.owner}/{repo.repo}
                            </a>
                            {repo.is_archived && (
                              <span className="github-repo-card__archived">Archived</span>
                            )}
                            {repo.pushed_at && isRecentlyUpdated(repo.pushed_at) && (
                              <span className="github-repo-card__active">Active</span>
                            )}
                          </div>
                          <div className="github-repo-card__stats">
                            <span className="github-repo-card__stat" title="Stars">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 .587l3.668 7.568 8.332 1.151-6.064 5.828 1.48 8.279-7.416-3.967-7.417 3.967 1.481-8.279-6.064-5.828 8.332-1.151z"/>
                              </svg>
                              {formatStars(repo.stars)}
                            </span>
                            <span className="github-repo-card__stat" title="Forks">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="18" r="3" />
                                <circle cx="6" cy="6" r="3" />
                                <circle cx="18" cy="6" r="3" />
                                <path d="M18 9v1a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V9" />
                                <line x1="12" y1="12" x2="12" y2="15" />
                              </svg>
                              {formatStars(repo.forks)}
                            </span>
                            {repo.language && (
                              <span className="github-repo-card__lang">{repo.language}</span>
                            )}
                            {repo.license && (
                              <span className="github-repo-card__license" title={`License: ${repo.license}`}>{repo.license}</span>
                            )}
                          </div>
                          {repo.pushed_at && (
                            <div className="github-repo-card__meta">
                              Last updated: {formatRelativeTime(repo.pushed_at)}
                              {repo.contributors && repo.contributors > 0 && (
                                <span> • {repo.contributors} contributors</span>
                              )}
                            </div>
                          )}
                          {repo.topics && repo.topics.length > 0 && (
                            <div className="github-repo-card__topics">
                              {repo.topics.slice(0, 5).map((topic) => (
                                <span key={topic} className="github-repo-card__topic">{topic}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : hasCode() && (
                  <div className="paper-detail__section">
                    <h4 className="text-sm font-semibold text-secondary paper-detail__heading">
                      Code Repository
                    </h4>
                    {paper.code_repos?.map((repo, i) => (
                      <a
                        key={i}
                        href={repo}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-secondary btn-sm paper-detail__repo-link"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                        </svg>
                        View Code
                      </a>
                    ))}
                  </div>
                )}

                <div className="paper-detail__actions">
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
                {relatedLoading && (
                  <div className="paper-detail__loading">
                    <div className="spinner spinner--sm" />
                    <span>Finding similar papers...</span>
                  </div>
                )}

                {relatedError && (
                  <div className="paper-detail__error">
                    <p>{relatedError}</p>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => {
                        setHasFetchedRelated(false);
                        setRelatedError(null);
                      }}
                    >
                      Retry
                    </button>
                  </div>
                )}

                {!relatedLoading && !relatedError && relatedPapers.length === 0 && hasFetchedRelated && (
                  <div className="paper-detail__placeholder">
                    <span className="paper-detail__placeholder-icon">
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <circle cx="12" cy="12" r="3" />
                        <circle cx="19" cy="5" r="2" />
                        <circle cx="5" cy="19" r="2" />
                        <circle cx="19" cy="19" r="2" />
                        <path d="M14.5 10.5L17 7" />
                        <path d="M9.5 13.5L7 17" />
                        <path d="M14.5 13.5L17 17" />
                      </svg>
                    </span>
                    <p className="paper-detail__placeholder-text">
                      No similar papers found in the database yet
                    </p>
                  </div>
                )}

                {!relatedLoading && relatedPapers.length > 0 && (
                  <div className="related-papers-list">
                    {relatedPapers.map((related) => (
                      <div key={related.id} className="related-paper-card">
                        <div className="related-paper-card__header">
                          <span className="related-paper-card__similarity">
                            {Math.round(related.similarity * 100)}% match
                          </span>
                          {related.category && (
                            <span className="badge badge-accent">{related.category}</span>
                          )}
                        </div>
                        <h4 className="related-paper-card__title">
                          <a
                            href={`https://arxiv.org/abs/${related.id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {related.title}
                          </a>
                        </h4>
                        <p className="related-paper-card__abstract">
                          {related.abstract.length > 200
                            ? `${related.abstract.substring(0, 200)}...`
                            : related.abstract}
                        </p>
                        <div className="related-paper-card__meta">
                          <span>{formatDate(related.published_date)}</span>
                          {related.citation_count > 0 && (
                            <span>{related.citation_count.toLocaleString()} citations</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === "benchmarks" && (
              <div className="paper-detail__placeholder">
                <span className="paper-detail__placeholder-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M18 20V10" />
                    <path d="M12 20V4" />
                    <path d="M6 20v-6" />
                  </svg>
                </span>
                <p className="paper-detail__placeholder-text">
                  View benchmark results and state-of-the-art comparisons
                </p>
                <button className="btn btn-secondary btn-sm">
                  Load Benchmarks
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </article>
  );
}
