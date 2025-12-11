'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

// Types matching the backend API response
interface ImpactPaper {
  id: string;
  title: string;
  published: string | null;
  category: string;
  impact_score: number;
  citation_potential: string | null;
  industry_relevance: string | null;
  research_significance: string | null;
  executive_summary: string | null;
  novelty_type: string | null;
}

interface ImpactResponse {
  papers: ImpactPaper[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
  score_distribution: Record<string, number>;
  score_rubric: Record<string, string>;
}

// Score tier badge colors
const SCORE_COLORS: Record<number, { bg: string; text: string; border: string; label: string }> = {
  10: { bg: '#fef3c7', text: '#92400e', border: '#f59e0b', label: 'Transformative' },
  9: { bg: '#fef3c7', text: '#92400e', border: '#f59e0b', label: 'Transformative' },
  8: { bg: '#fee2e2', text: '#991b1b', border: '#ef4444', label: 'High Impact' },
  7: { bg: '#fee2e2', text: '#991b1b', border: '#ef4444', label: 'High Impact' },
  6: { bg: '#dbeafe', text: '#1e40af', border: '#3b82f6', label: 'Moderate' },
  5: { bg: '#dbeafe', text: '#1e40af', border: '#3b82f6', label: 'Moderate' },
  4: { bg: '#e5e7eb', text: '#374151', border: '#6b7280', label: 'Low' },
  3: { bg: '#e5e7eb', text: '#374151', border: '#6b7280', label: 'Low' },
  2: { bg: '#f3f4f6', text: '#6b7280', border: '#9ca3af', label: 'Minimal' },
  1: { bg: '#f3f4f6', text: '#6b7280', border: '#9ca3af', label: 'Minimal' },
};

// Relevance badge colors
const RELEVANCE_COLORS: Record<string, { bg: string; text: string }> = {
  high: { bg: '#dcfce7', text: '#166534' },
  medium: { bg: '#fef9c3', text: '#854d0e' },
  low: { bg: '#f3f4f6', text: '#374151' },
};

// Impact meter visualization
const ImpactMeter = ({ score }: { score: number }) => {
  const size = 48;
  const strokeWidth = 4;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 10) * circumference;

  const getColor = (s: number) => {
    if (s >= 9) return '#f59e0b'; // Gold
    if (s >= 7) return '#ef4444'; // Red
    if (s >= 5) return '#3b82f6'; // Blue
    return '#6b7280'; // Gray
  };

  return (
    <div className="impact-meter">
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor(score)}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          strokeLinecap="round"
          style={{
            transform: 'rotate(-90deg)',
            transformOrigin: 'center',
            transition: 'stroke-dashoffset 0.8s ease-out',
          }}
        />
      </svg>
      <span className="impact-meter__value">{score}</span>
    </div>
  );
};

// Score distribution chart
const ScoreDistribution = ({ distribution }: { distribution: Record<string, number> }) => {
  const scores = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1];
  const maxCount = Math.max(...Object.values(distribution), 1);

  return (
    <div className="score-distribution">
      <h3>Score Distribution</h3>
      <div className="score-bars">
        {scores.map((score) => {
          const count = distribution[score] || 0;
          const height = (count / maxCount) * 100;
          const color = SCORE_COLORS[score];
          return (
            <div key={score} className="score-bar-wrapper">
              <div className="score-bar-container">
                <div
                  className="score-bar"
                  style={{
                    height: `${Math.max(height, 2)}%`,
                    backgroundColor: color?.border || '#6b7280',
                  }}
                />
              </div>
              <span className="score-bar-label">{score}</span>
              <span className="score-bar-count">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Paper card component
const PaperCard = ({ paper }: { paper: ImpactPaper }) => {
  const plainId = paper.id.split('v')[0];
  const scoreStyle = SCORE_COLORS[paper.impact_score] || SCORE_COLORS[5];
  const relevanceStyle = paper.industry_relevance
    ? RELEVANCE_COLORS[paper.industry_relevance] || RELEVANCE_COLORS.medium
    : null;

  return (
    <article className="paper-card">
      <header className="paper-card__header">
        <ImpactMeter score={paper.impact_score} />
        <div className="paper-card__badges">
          <span
            className="paper-card__score-badge"
            style={{
              backgroundColor: scoreStyle.bg,
              color: scoreStyle.text,
              border: `1px solid ${scoreStyle.border}`,
            }}
          >
            {scoreStyle.label}
          </span>
          {relevanceStyle && (
            <span
              className="paper-card__relevance-badge"
              style={{
                backgroundColor: relevanceStyle.bg,
                color: relevanceStyle.text,
              }}
            >
              {paper.industry_relevance} industry
            </span>
          )}
        </div>
      </header>

      <h3 className="paper-card__title">
        <Link
          href={`https://arxiv.org/abs/${plainId}`}
          target="_blank"
          rel="noopener"
        >
          {paper.title}
        </Link>
      </h3>

      {paper.executive_summary && (
        <p className="paper-card__summary">{paper.executive_summary}</p>
      )}

      {paper.research_significance && (
        <p className="paper-card__significance">
          <strong>Significance:</strong> {paper.research_significance}
        </p>
      )}

      <footer className="paper-card__footer">
        <div className="paper-card__meta">
          <span className="paper-card__category">{paper.category}</span>
          {paper.novelty_type && (
            <span className="paper-card__novelty">{paper.novelty_type}</span>
          )}
        </div>
        <div className="paper-card__details">
          {paper.citation_potential && (
            <span className="paper-card__citation">
              Citation: {paper.citation_potential}
            </span>
          )}
          {paper.published && (
            <time className="paper-card__date">
              {new Date(paper.published).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </time>
          )}
        </div>
      </footer>
    </article>
  );
};

// Main page component
export default function ImpactDashboardPage() {
  const [papers, setPapers] = useState<ImpactPaper[]>([]);
  const [distribution, setDistribution] = useState<Record<string, number>>({});
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [minScore, setMinScore] = useState(7);
  const [industryRelevance, setIndustryRelevance] = useState<string>('');
  const [citationPotential, setCitationPotential] = useState<string>('');
  const [days, setDays] = useState<number | ''>('');

  useEffect(() => {
    const fetchPapers = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams({
          limit: '30',
          min_score: minScore.toString(),
        });
        if (industryRelevance) params.set('industry_relevance', industryRelevance);
        if (citationPotential) params.set('citation_potential', citationPotential);
        if (days) params.set('days', days.toString());

        const response = await fetch(`/api/discovery/impact?${params.toString()}`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data: ImpactResponse = await response.json();
        setPapers(data.papers || []);
        setDistribution(data.score_distribution || {});
        setTotal(data.total || 0);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load impact papers');
      } finally {
        setLoading(false);
      }
    };

    fetchPapers();
  }, [minScore, industryRelevance, citationPotential, days]);

  // Group papers by score tier for display
  const papersByTier = {
    transformative: papers.filter((p) => p.impact_score >= 9),
    high: papers.filter((p) => p.impact_score >= 7 && p.impact_score < 9),
    moderate: papers.filter((p) => p.impact_score >= 5 && p.impact_score < 7),
    low: papers.filter((p) => p.impact_score < 5),
  };

  return (
    <div className="impact-page">
      <style jsx global>{`
        .impact-page {
          min-height: 100vh;
          background: linear-gradient(to bottom, #0f172a, #1e293b);
          color: #e2e8f0;
          padding: 2rem;
        }

        .impact-hero {
          text-align: center;
          margin-bottom: 3rem;
        }

        .impact-hero h1 {
          font-size: 2.5rem;
          font-weight: 700;
          background: linear-gradient(135deg, #f59e0b, #ef4444, #8b5cf6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 0.5rem;
        }

        .impact-hero p {
          color: #94a3b8;
          font-size: 1.1rem;
          max-width: 700px;
          margin: 0 auto;
        }

        .impact-stats {
          display: flex;
          justify-content: center;
          gap: 2rem;
          margin-top: 1.5rem;
        }

        .impact-stat {
          text-align: center;
        }

        .impact-stat__value {
          display: block;
          font-size: 2rem;
          font-weight: 700;
          color: #f59e0b;
        }

        .impact-stat__label {
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #64748b;
        }

        .impact-filters {
          display: flex;
          flex-wrap: wrap;
          gap: 1.5rem;
          justify-content: center;
          margin-bottom: 3rem;
          padding: 1.5rem;
          background: rgba(30, 41, 59, 0.5);
          border-radius: 12px;
          border: 1px solid rgba(148, 163, 184, 0.1);
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .filter-group label {
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #64748b;
        }

        .filter-group select,
        .filter-group input {
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 6px;
          padding: 0.5rem 1rem;
          color: #e2e8f0;
          font-size: 0.875rem;
          min-width: 140px;
        }

        .filter-group select:focus,
        .filter-group input:focus {
          outline: none;
          border-color: #f59e0b;
        }

        .score-chips {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .score-chip {
          padding: 0.375rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
          cursor: pointer;
          border: 1px solid;
          transition: all 0.15s;
        }

        .score-chip--active {
          transform: scale(1.05);
          box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.5);
        }

        .score-distribution {
          background: rgba(30, 41, 59, 0.5);
          border-radius: 12px;
          padding: 1.5rem;
          margin-bottom: 3rem;
          border: 1px solid rgba(148, 163, 184, 0.1);
        }

        .score-distribution h3 {
          font-size: 0.875rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #94a3b8;
          margin: 0 0 1rem 0;
          text-align: center;
        }

        .score-bars {
          display: flex;
          justify-content: center;
          gap: 0.75rem;
          height: 120px;
          align-items: flex-end;
        }

        .score-bar-wrapper {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
        }

        .score-bar-container {
          width: 24px;
          height: 80px;
          background: rgba(15, 23, 42, 0.5);
          border-radius: 4px;
          display: flex;
          flex-direction: column;
          justify-content: flex-end;
          overflow: hidden;
        }

        .score-bar {
          width: 100%;
          border-radius: 4px 4px 0 0;
          transition: height 0.5s ease-out;
        }

        .score-bar-label {
          font-size: 0.75rem;
          font-weight: 600;
          color: #e2e8f0;
        }

        .score-bar-count {
          font-size: 0.625rem;
          color: #64748b;
        }

        .impact-loading {
          text-align: center;
          padding: 4rem;
        }

        .impact-loading__spinner {
          width: 40px;
          height: 40px;
          border: 3px solid #334155;
          border-top-color: #f59e0b;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .impact-error {
          text-align: center;
          padding: 3rem;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 12px;
          color: #fca5a5;
        }

        .papers-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
          gap: 1.5rem;
          max-width: 1400px;
          margin: 0 auto;
        }

        .tier-section {
          margin-bottom: 3rem;
        }

        .tier-section__header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1.5rem;
          padding-bottom: 0.75rem;
          border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }

        .tier-section__title {
          font-size: 1.25rem;
          font-weight: 600;
        }

        .tier-section__count {
          background: rgba(148, 163, 184, 0.1);
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          color: #94a3b8;
        }

        .paper-card {
          background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 12px;
          padding: 1.25rem;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .paper-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
          border-color: rgba(148, 163, 184, 0.2);
        }

        .paper-card__header {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .impact-meter {
          position: relative;
          width: 48px;
          height: 48px;
          flex-shrink: 0;
        }

        .impact-meter__value {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 1rem;
          font-weight: 700;
          color: #f1f5f9;
        }

        .paper-card__badges {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .paper-card__score-badge {
          font-size: 0.625rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .paper-card__relevance-badge {
          font-size: 0.625rem;
          font-weight: 500;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          text-transform: capitalize;
        }

        .paper-card__title {
          font-size: 1rem;
          font-weight: 600;
          line-height: 1.4;
          margin: 0 0 0.75rem 0;
        }

        .paper-card__title a {
          color: #f1f5f9;
          text-decoration: none;
          transition: color 0.15s;
        }

        .paper-card__title a:hover {
          color: #f59e0b;
        }

        .paper-card__summary {
          font-size: 0.875rem;
          color: #94a3b8;
          line-height: 1.5;
          margin: 0 0 0.75rem 0;
        }

        .paper-card__significance {
          font-size: 0.8rem;
          color: #cbd5e1;
          line-height: 1.5;
          margin: 0 0 1rem 0;
          padding: 0.75rem;
          background: rgba(15, 23, 42, 0.5);
          border-radius: 8px;
        }

        .paper-card__significance strong {
          color: #f59e0b;
        }

        .paper-card__footer {
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
          flex-wrap: wrap;
          gap: 0.5rem;
          padding-top: 0.75rem;
          border-top: 1px solid rgba(148, 163, 184, 0.1);
        }

        .paper-card__meta {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .paper-card__category {
          font-size: 0.625rem;
          padding: 0.125rem 0.5rem;
          background: rgba(59, 130, 246, 0.1);
          color: #93c5fd;
          border-radius: 4px;
        }

        .paper-card__novelty {
          font-size: 0.625rem;
          padding: 0.125rem 0.5rem;
          background: rgba(139, 92, 246, 0.1);
          color: #c4b5fd;
          border-radius: 4px;
        }

        .paper-card__details {
          display: flex;
          gap: 0.75rem;
          align-items: center;
        }

        .paper-card__citation {
          font-size: 0.7rem;
          color: #64748b;
          text-transform: capitalize;
        }

        .paper-card__date {
          font-size: 0.7rem;
          color: #64748b;
        }

        .back-link {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          color: #94a3b8;
          text-decoration: none;
          font-size: 0.875rem;
          margin-bottom: 2rem;
          transition: color 0.15s;
        }

        .back-link:hover {
          color: #e2e8f0;
        }

        .empty-state {
          text-align: center;
          padding: 4rem 2rem;
          color: #64748b;
        }

        .empty-state h3 {
          color: #94a3b8;
          margin-bottom: 0.5rem;
        }

        .rubric {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-top: 1.5rem;
          padding: 1rem;
          background: rgba(15, 23, 42, 0.3);
          border-radius: 8px;
        }

        .rubric__item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.75rem;
        }

        .rubric__score {
          font-weight: 600;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          min-width: 40px;
          text-align: center;
        }

        .rubric__description {
          color: #94a3b8;
        }
      `}</style>

      <Link href="/discovery" className="back-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        Back to Discovery
      </Link>

      <header className="impact-hero">
        <h1>Impact Dashboard</h1>
        <p>
          Discover research papers ranked by their potential to shape the field.
          Impact scores are calibrated based on novelty, methodology, and practical significance.
        </p>
        <div className="impact-stats">
          <div className="impact-stat">
            <span className="impact-stat__value">{total.toLocaleString()}</span>
            <span className="impact-stat__label">Matching Papers</span>
          </div>
          <div className="impact-stat">
            <span className="impact-stat__value">
              {papersByTier.transformative.length}
            </span>
            <span className="impact-stat__label">Transformative</span>
          </div>
          <div className="impact-stat">
            <span className="impact-stat__value">
              {papersByTier.high.length}
            </span>
            <span className="impact-stat__label">High Impact</span>
          </div>
        </div>

        <div className="rubric">
          <div className="rubric__item">
            <span className="rubric__score" style={{ backgroundColor: '#fef3c7', color: '#92400e' }}>9-10</span>
            <span className="rubric__description">Transformative (paradigm shifting)</span>
          </div>
          <div className="rubric__item">
            <span className="rubric__score" style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}>7-8</span>
            <span className="rubric__description">High impact (field advancement)</span>
          </div>
          <div className="rubric__item">
            <span className="rubric__score" style={{ backgroundColor: '#dbeafe', color: '#1e40af' }}>5-6</span>
            <span className="rubric__description">Moderate (solid incremental work)</span>
          </div>
          <div className="rubric__item">
            <span className="rubric__score" style={{ backgroundColor: '#e5e7eb', color: '#374151' }}>1-4</span>
            <span className="rubric__description">Low to minimal contribution</span>
          </div>
        </div>
      </header>

      <section className="impact-filters">
        <div className="filter-group">
          <label>Minimum Score</label>
          <div className="score-chips">
            {[9, 8, 7, 6, 5].map((score) => {
              const style = SCORE_COLORS[score];
              const isActive = minScore === score;
              return (
                <button
                  key={score}
                  className={`score-chip ${isActive ? 'score-chip--active' : ''}`}
                  style={{
                    backgroundColor: style.bg,
                    color: style.text,
                    borderColor: style.border,
                  }}
                  onClick={() => setMinScore(score)}
                >
                  {score}+
                </button>
              );
            })}
          </div>
        </div>

        <div className="filter-group">
          <label>Industry Relevance</label>
          <select
            value={industryRelevance}
            onChange={(e) => setIndustryRelevance(e.target.value)}
          >
            <option value="">All</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Citation Potential</label>
          <select
            value={citationPotential}
            onChange={(e) => setCitationPotential(e.target.value)}
          >
            <option value="">All</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Time Period</label>
          <select
            value={days}
            onChange={(e) => setDays(e.target.value ? Number(e.target.value) : '')}
          >
            <option value="">All Time</option>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="180">Last 6 months</option>
            <option value="365">Last year</option>
          </select>
        </div>
      </section>

      {Object.keys(distribution).length > 0 && (
        <ScoreDistribution distribution={distribution} />
      )}

      {loading ? (
        <div className="impact-loading">
          <div className="impact-loading__spinner" />
          <span>Analyzing research impact...</span>
        </div>
      ) : error ? (
        <div className="impact-error">
          <h3>Failed to load impact papers</h3>
          <p>{error}</p>
        </div>
      ) : papers.length === 0 ? (
        <div className="empty-state">
          <h3>No papers found</h3>
          <p>Try adjusting the filters to see more results.</p>
        </div>
      ) : minScore >= 9 ? (
        // Show flat grid when filtering for top scores
        <div className="papers-grid">
          {papers.map((paper) => (
            <PaperCard key={paper.id} paper={paper} />
          ))}
        </div>
      ) : (
        // Show grouped by tier
        <>
          {papersByTier.transformative.length > 0 && (
            <section className="tier-section">
              <header className="tier-section__header">
                <h2 className="tier-section__title" style={{ color: '#f59e0b' }}>
                  Transformative Papers
                </h2>
                <span className="tier-section__count">
                  {papersByTier.transformative.length} papers
                </span>
              </header>
              <div className="papers-grid">
                {papersByTier.transformative.map((paper) => (
                  <PaperCard key={paper.id} paper={paper} />
                ))}
              </div>
            </section>
          )}

          {papersByTier.high.length > 0 && (
            <section className="tier-section">
              <header className="tier-section__header">
                <h2 className="tier-section__title" style={{ color: '#ef4444' }}>
                  High Impact Papers
                </h2>
                <span className="tier-section__count">
                  {papersByTier.high.length} papers
                </span>
              </header>
              <div className="papers-grid">
                {papersByTier.high.map((paper) => (
                  <PaperCard key={paper.id} paper={paper} />
                ))}
              </div>
            </section>
          )}

          {papersByTier.moderate.length > 0 && minScore <= 6 && (
            <section className="tier-section">
              <header className="tier-section__header">
                <h2 className="tier-section__title" style={{ color: '#3b82f6' }}>
                  Moderate Impact Papers
                </h2>
                <span className="tier-section__count">
                  {papersByTier.moderate.length} papers
                </span>
              </header>
              <div className="papers-grid">
                {papersByTier.moderate.map((paper) => (
                  <PaperCard key={paper.id} paper={paper} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
