"use client";

import React, { useEffect, useState } from 'react';

interface GitHubRepo {
  url: string;
  owner: string;
  repo: string;
  stars: number;
  forks: number;
  open_issues: number;
  language: string | null;
  license: string | null;
  pushed_at: string | null;
  is_archived: boolean;
  contributors: number | null;
  topics: string[];
}

interface ExternalSignals {
  paper_id: string;
  github: {
    repos: GitHubRepo[];
    total_stars: number;
    updated_at: string | null;
  } | null;
  huggingface: {
    total_downloads: number;
    models: Array<{ name: string; downloads: number }>;
  } | null;
  social: {
    twitter_mentions_30d: number;
    reddit_threads: number;
  } | null;
}

interface TrendData {
  paper_id: string;
  citation_trend: string;
  citation_velocity_current: number | null;
  citation_velocity_change: number | null;
  github_trend: string | null;
  buzz_trend: string | null;
}

interface ExternalSignalsCardProps {
  paperId: string;
  apiBaseUrl?: string;
}

const formatNumber = (num: number): string => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
};

const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return 'Unknown';
  const date = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
};

const TrendIcon: React.FC<{ trend: string | null }> = ({ trend }) => {
  if (!trend) return null;

  switch (trend) {
    case 'rising':
      return <span style={{ color: '#059669', fontSize: '1rem' }}>↑</span>;
    case 'falling':
      return <span style={{ color: '#dc2626', fontSize: '1rem' }}>↓</span>;
    default:
      return <span style={{ color: '#6b7280', fontSize: '1rem' }}>→</span>;
  }
};

const ExternalSignalsCard: React.FC<ExternalSignalsCardProps> = ({
  paperId,
  apiBaseUrl = 'http://localhost:8000/api/v1'
}) => {
  const [signals, setSignals] = useState<ExternalSignals | null>(null);
  const [trend, setTrend] = useState<TrendData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch external signals and trends in parallel
        const [signalsRes, trendRes] = await Promise.all([
          fetch(`${apiBaseUrl}/data-moat/signals/${paperId}`),
          fetch(`${apiBaseUrl}/data-moat/metrics/trend/${paperId}`).catch(() => null)
        ]);

        if (signalsRes.ok) {
          const signalsData = await signalsRes.json();
          setSignals(signalsData);
        }

        if (trendRes && trendRes.ok) {
          const trendData = await trendRes.json();
          setTrend(trendData);
        }
      } catch (err) {
        console.error('Error fetching external signals:', err);
        setError('Failed to load external signals');
      } finally {
        setLoading(false);
      }
    };

    if (paperId) {
      fetchData();
    }
  }, [paperId, apiBaseUrl]);

  // Don't render if no data and not loading
  if (!loading && !signals?.github?.repos?.length && !signals?.huggingface && !trend) {
    return null;
  }

  const hasGitHub = signals?.github?.repos && signals.github.repos.length > 0;
  const hasHuggingFace = signals?.huggingface && signals.huggingface.total_downloads > 0;
  const hasTrend = trend && trend.citation_trend;

  return (
    <div className="external-signals-card">
      <h3>
        <span style={{ marginRight: '8px' }}>📊</span>
        External Signals
      </h3>

      {loading ? (
        <div className="signals-loading">
          <div className="loading-spinner" />
          <span>Loading signals...</span>
        </div>
      ) : error ? (
        <div className="signals-error">{error}</div>
      ) : (
        <div className="signals-grid">
          {/* GitHub Section */}
          {hasGitHub && (
            <div className="signal-section github-section">
              <div className="signal-header">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                <span>GitHub</span>
                <TrendIcon trend={trend?.github_trend || null} />
              </div>

              <div className="signal-stats">
                <div className="stat-item">
                  <span className="stat-value">{formatNumber(signals!.github!.total_stars)}</span>
                  <span className="stat-label">Stars</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">
                    {formatNumber(signals!.github!.repos.reduce((sum, r) => sum + r.forks, 0))}
                  </span>
                  <span className="stat-label">Forks</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{signals!.github!.repos.length}</span>
                  <span className="stat-label">Repos</span>
                </div>
              </div>

              {/* Show top repo */}
              {signals!.github!.repos[0] && (
                <div className="repo-preview">
                  <a
                    href={signals!.github!.repos[0].url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="repo-link"
                  >
                    <span className="repo-name">
                      {signals!.github!.repos[0].owner}/{signals!.github!.repos[0].repo}
                    </span>
                    {signals!.github!.repos[0].language && (
                      <span className="repo-language">{signals!.github!.repos[0].language}</span>
                    )}
                  </a>
                  <div className="repo-meta">
                    <span>Last push: {formatDate(signals!.github!.repos[0].pushed_at)}</span>
                    {signals!.github!.repos[0].is_archived && (
                      <span className="archived-badge">Archived</span>
                    )}
                  </div>
                  {signals!.github!.repos[0].topics.length > 0 && (
                    <div className="repo-topics">
                      {signals!.github!.repos[0].topics.slice(0, 4).map((topic, i) => (
                        <span key={i} className="topic-tag">{topic}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* HuggingFace Section */}
          {hasHuggingFace && (
            <div className="signal-section huggingface-section">
              <div className="signal-header">
                <span style={{ fontSize: '1.2rem' }}>🤗</span>
                <span>Hugging Face</span>
              </div>

              <div className="signal-stats">
                <div className="stat-item">
                  <span className="stat-value">{formatNumber(signals!.huggingface!.total_downloads)}</span>
                  <span className="stat-label">Downloads</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{signals!.huggingface!.models?.length || 0}</span>
                  <span className="stat-label">Models</span>
                </div>
              </div>
            </div>
          )}

          {/* Trend Section */}
          {hasTrend && (
            <div className="signal-section trend-section">
              <div className="signal-header">
                <span style={{ fontSize: '1.2rem' }}>📈</span>
                <span>Momentum</span>
              </div>

              <div className="signal-stats">
                <div className="stat-item">
                  <span className={`stat-value trend-${trend!.citation_trend}`}>
                    {trend!.citation_trend === 'rising' ? '🔥 Rising' :
                     trend!.citation_trend === 'falling' ? '📉 Falling' : '➡️ Stable'}
                  </span>
                  <span className="stat-label">Citation Trend</span>
                </div>
                {trend!.citation_velocity_current !== null && (
                  <div className="stat-item">
                    <span className="stat-value">{trend!.citation_velocity_current.toFixed(1)}</span>
                    <span className="stat-label">Cites/Month</span>
                  </div>
                )}
                {trend!.buzz_trend && (
                  <div className="stat-item">
                    <span className={`stat-value trend-${trend!.buzz_trend}`}>
                      <TrendIcon trend={trend!.buzz_trend} />
                    </span>
                    <span className="stat-label">Buzz</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Empty state */}
          {!hasGitHub && !hasHuggingFace && !hasTrend && (
            <div className="signals-empty">
              <span style={{ fontSize: '1.5rem', marginBottom: '8px' }}>🔍</span>
              <p>No external signals available yet</p>
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        .external-signals-card {
          background: linear-gradient(135deg, rgba(79, 70, 229, 0.03) 0%, rgba(14, 165, 233, 0.03) 100%);
          border: 1px solid rgba(79, 70, 229, 0.12);
          border-radius: 16px;
          padding: 20px;
          margin: 24px 0;
        }

        .external-signals-card h3 {
          font-size: 1rem;
          font-weight: 600;
          color: var(--primary-text, #0f172a);
          margin-bottom: 16px;
          display: flex;
          align-items: center;
        }

        .signals-loading {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 20px;
          color: var(--secondary-text, #64748b);
        }

        .loading-spinner {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(79, 70, 229, 0.2);
          border-top-color: var(--accent-indigo, #4f46e5);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .signals-error {
          color: #dc2626;
          padding: 12px;
          background: rgba(220, 38, 38, 0.1);
          border-radius: 8px;
        }

        .signals-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
        }

        .signal-section {
          background: white;
          border-radius: 12px;
          padding: 16px;
          border: 1px solid rgba(148, 163, 184, 0.2);
        }

        .signal-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
          font-weight: 600;
          color: var(--primary-text, #0f172a);
        }

        .signal-header svg {
          color: var(--secondary-text, #64748b);
        }

        .signal-stats {
          display: flex;
          gap: 16px;
          flex-wrap: wrap;
        }

        .stat-item {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .stat-value {
          font-family: var(--font-tech, 'JetBrains Mono', monospace);
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--primary-text, #0f172a);
        }

        .stat-value.trend-rising {
          color: #059669;
        }

        .stat-value.trend-falling {
          color: #dc2626;
        }

        .stat-value.trend-stable {
          color: #6b7280;
        }

        .stat-label {
          font-size: 0.75rem;
          color: var(--secondary-text, #64748b);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .repo-preview {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid rgba(148, 163, 184, 0.15);
        }

        .repo-link {
          display: flex;
          align-items: center;
          gap: 8px;
          color: var(--accent-indigo, #4f46e5);
          font-weight: 500;
          text-decoration: none;
        }

        .repo-link:hover {
          text-decoration: underline;
        }

        .repo-name {
          font-family: var(--font-tech, 'JetBrains Mono', monospace);
          font-size: 0.9rem;
        }

        .repo-language {
          font-size: 0.7rem;
          padding: 2px 6px;
          background: rgba(79, 70, 229, 0.1);
          color: var(--accent-indigo, #4f46e5);
          border-radius: 4px;
        }

        .repo-meta {
          margin-top: 6px;
          font-size: 0.8rem;
          color: var(--secondary-text, #64748b);
          display: flex;
          gap: 8px;
          align-items: center;
        }

        .archived-badge {
          font-size: 0.7rem;
          padding: 2px 6px;
          background: rgba(251, 146, 60, 0.15);
          color: #ea580c;
          border-radius: 4px;
        }

        .repo-topics {
          margin-top: 8px;
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
        }

        .topic-tag {
          font-size: 0.7rem;
          padding: 2px 8px;
          background: rgba(14, 165, 233, 0.1);
          color: var(--accent-sky, #0ea5e9);
          border-radius: 12px;
        }

        .signals-empty {
          grid-column: 1 / -1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 32px;
          color: var(--secondary-text, #64748b);
          text-align: center;
        }

        .signals-empty p {
          margin: 0;
          font-size: 0.9rem;
        }
      `}</style>
    </div>
  );
};

export default ExternalSignalsCard;
