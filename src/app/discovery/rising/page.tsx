'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

// Types matching the backend API response
interface RisingPaper {
  id: string;
  title: string;
  published: string | null;
  category: string;
  citation_count: number;
  influential_citation_count: number;
  months_since_publication: number;
  citation_velocity: number;
  link: string;
}

interface RisingResponse {
  papers: RisingPaper[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
  velocity_distribution: Record<string, number>;
  filters: {
    min_citations: number;
    min_months: number;
    max_months: number | null;
    category: string | null;
  };
  velocity_tiers: Record<string, string>;
}

// Velocity tier badge colors (matching velocity distribution keys)
const TIER_COLORS: Record<string, { bg: string; text: string; border: string; label: string }> = {
  'viral (20+/mo)': { bg: '#fef3c7', text: '#92400e', border: '#f59e0b', label: 'Viral' },
  'hot (10-20/mo)': { bg: '#fee2e2', text: '#991b1b', border: '#ef4444', label: 'Hot' },
  'rising (5-10/mo)': { bg: '#dbeafe', text: '#1e40af', border: '#3b82f6', label: 'Rising' },
  'growing (2-5/mo)': { bg: '#d1fae5', text: '#065f46', border: '#10b981', label: 'Growing' },
  'steady (<2/mo)': { bg: '#e5e7eb', text: '#374151', border: '#6b7280', label: 'Steady' },
};

// Helper to get tier from velocity
const getVelocityTier = (velocity: number): string => {
  if (velocity >= 20) return 'viral (20+/mo)';
  if (velocity >= 10) return 'hot (10-20/mo)';
  if (velocity >= 5) return 'rising (5-10/mo)';
  if (velocity >= 2) return 'growing (2-5/mo)';
  return 'steady (<2/mo)';
};

// Format date
const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return 'Unknown';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
};

// Paper card component
const PaperCard = ({ paper }: { paper: RisingPaper }) => {
  const tier = getVelocityTier(paper.citation_velocity);
  const tierStyle = TIER_COLORS[tier] || TIER_COLORS['steady (<2/mo)'];

  return (
    <article className="paper-card">
      <header className="paper-card__header">
        <div className="paper-card__meta">
          <span className="paper-card__category">{paper.category || 'cs.AI'}</span>
          <span
            className="paper-card__tier"
            style={{
              backgroundColor: tierStyle.bg,
              color: tierStyle.text,
              border: `1px solid ${tierStyle.border}`,
            }}
          >
            {tierStyle.label}
          </span>
        </div>
        <div className="paper-card__velocity">
          <span className="velocity-value">{paper.citation_velocity.toFixed(1)}</span>
          <span className="velocity-label">cit/mo</span>
        </div>
      </header>

      <h3 className="paper-card__title">
        <Link href={paper.link} target="_blank" rel="noopener">
          {paper.title}
        </Link>
      </h3>

      <div className="paper-card__stats">
        <div className="stat">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 8v4l3 3" />
            <circle cx="12" cy="12" r="10" />
          </svg>
          <span>{formatDate(paper.published)}</span>
        </div>
        <div className="stat">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span>{paper.months_since_publication.toFixed(1)} months old</span>
        </div>
      </div>

      <div className="paper-card__citations">
        <div className="citation-stat">
          <span className="citation-value">{paper.citation_count}</span>
          <span className="citation-label">Total Citations</span>
        </div>
        <div className="citation-stat citation-stat--highlight">
          <span className="citation-value">{paper.influential_citation_count}</span>
          <span className="citation-label">Influential</span>
        </div>
      </div>

      <footer className="paper-card__footer">
        <Link href={paper.link} target="_blank" rel="noopener" className="paper-card__link">
          View on arXiv
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" />
          </svg>
        </Link>
      </footer>
    </article>
  );
};

// Velocity Distribution Chart
const VelocityDistribution = ({ distribution }: { distribution: Record<string, number> }) => {
  const tierOrder = ['viral (20+/mo)', 'hot (10-20/mo)', 'rising (5-10/mo)', 'growing (2-5/mo)', 'steady (<2/mo)'];
  const total = Object.values(distribution).reduce((a, b) => a + b, 0);

  if (total === 0) return null;

  return (
    <div className="velocity-distribution">
      <h3>Velocity Distribution</h3>
      <div className="distribution-bars">
        {tierOrder.map((tier) => {
          const count = distribution[tier] || 0;
          const pct = total > 0 ? (count / total) * 100 : 0;
          const style = TIER_COLORS[tier] || TIER_COLORS['steady (<2/mo)'];

          return (
            <div key={tier} className="distribution-bar">
              <div className="bar-label">
                <span style={{ color: style.text }}>{style.label}</span>
                <span className="bar-count">{count}</span>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    width: `${Math.max(pct, 2)}%`,
                    backgroundColor: style.border,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Main page component
export default function RisingPapersPage() {
  const [papers, setPapers] = useState<RisingPaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [distribution, setDistribution] = useState<Record<string, number>>({});

  // Filters
  const [minCitations, setMinCitations] = useState(5);
  const [maxMonths, setMaxMonths] = useState(24);
  const [velocityFilter, setVelocityFilter] = useState<string>('');

  useEffect(() => {
    const fetchPapers = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams({
          limit: '50',
          min_citations: minCitations.toString(),
          max_months: maxMonths.toString(),
        });
        if (velocityFilter) params.set('velocity_tier', velocityFilter);

        const response = await fetch(`/api/discovery/rising?${params.toString()}`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data: RisingResponse = await response.json();

        // Filter by velocity tier if set (since backend may not support this filter)
        let filteredPapers = data.papers || [];
        if (velocityFilter) {
          filteredPapers = filteredPapers.filter((p) => getVelocityTier(p.citation_velocity) === velocityFilter);
        }

        setPapers(filteredPapers);
        setTotal(data.total || 0);
        setDistribution(data.velocity_distribution || {});
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load rising papers');
      } finally {
        setLoading(false);
      }
    };

    fetchPapers();
  }, [minCitations, maxMonths, velocityFilter]);

  // Group papers by tier for display
  const tierOrder = ['viral (20+/mo)', 'hot (10-20/mo)', 'rising (5-10/mo)', 'growing (2-5/mo)', 'steady (<2/mo)'];
  const papersByTier = tierOrder.reduce((acc, tier) => {
    acc[tier] = papers.filter((p) => getVelocityTier(p.citation_velocity) === tier);
    return acc;
  }, {} as Record<string, RisingPaper[]>);

  return (
    <div className="rising-papers-page">
      <style jsx global>{`
        .rising-papers-page {
          min-height: 100vh;
          background: linear-gradient(to bottom, #0f172a, #1e293b);
          color: #e2e8f0;
          padding: 2rem;
        }

        .rising-papers-hero {
          text-align: center;
          margin-bottom: 3rem;
        }

        .rising-papers-hero h1 {
          font-size: 2.5rem;
          font-weight: 700;
          background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 0.5rem;
        }

        .rising-papers-hero p {
          color: #94a3b8;
          font-size: 1.1rem;
          max-width: 600px;
          margin: 0 auto;
        }

        .rising-papers-filters {
          display: flex;
          flex-wrap: wrap;
          gap: 1.5rem;
          justify-content: center;
          margin-bottom: 2rem;
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
          border-color: #3b82f6;
        }

        .tier-chips {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .tier-chip {
          padding: 0.375rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
          cursor: pointer;
          border: 1px solid;
          transition: all 0.15s;
        }

        .tier-chip--active {
          transform: scale(1.05);
          box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
        }

        .velocity-distribution {
          max-width: 400px;
          margin: 0 auto 2rem;
          padding: 1.5rem;
          background: rgba(30, 41, 59, 0.5);
          border-radius: 12px;
          border: 1px solid rgba(148, 163, 184, 0.1);
        }

        .velocity-distribution h3 {
          font-size: 0.875rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #64748b;
          margin: 0 0 1rem 0;
          text-align: center;
        }

        .distribution-bars {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .distribution-bar {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .bar-label {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
        }

        .bar-count {
          color: #94a3b8;
        }

        .bar-track {
          height: 8px;
          background: rgba(15, 23, 42, 0.5);
          border-radius: 4px;
          overflow: hidden;
        }

        .bar-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.3s ease;
        }

        .rising-papers-loading {
          text-align: center;
          padding: 4rem;
        }

        .rising-papers-loading__spinner {
          width: 40px;
          height: 40px;
          border: 3px solid #334155;
          border-top-color: #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .rising-papers-error {
          text-align: center;
          padding: 3rem;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 12px;
          color: #fca5a5;
        }

        .papers-summary {
          text-align: center;
          margin-bottom: 2rem;
          color: #94a3b8;
          font-size: 0.875rem;
        }

        .papers-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
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
          display: flex;
          flex-direction: column;
        }

        .paper-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
          border-color: rgba(148, 163, 184, 0.2);
        }

        .paper-card__header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 0.75rem;
        }

        .paper-card__meta {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }

        .paper-card__category {
          font-size: 0.625rem;
          padding: 0.125rem 0.5rem;
          background: rgba(59, 130, 246, 0.1);
          color: #93c5fd;
          border-radius: 4px;
        }

        .paper-card__tier {
          font-size: 0.625rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          padding: 0.125rem 0.5rem;
          border-radius: 4px;
        }

        .paper-card__velocity {
          text-align: right;
        }

        .velocity-value {
          display: block;
          font-size: 1.5rem;
          font-weight: 700;
          color: #f59e0b;
          line-height: 1;
        }

        .velocity-label {
          font-size: 0.625rem;
          color: #64748b;
          text-transform: uppercase;
        }

        .paper-card__title {
          font-size: 1rem;
          font-weight: 600;
          line-height: 1.4;
          margin: 0 0 0.75rem 0;
          flex-grow: 1;
        }

        .paper-card__title a {
          color: #f1f5f9;
          text-decoration: none;
          transition: color 0.15s;
        }

        .paper-card__title a:hover {
          color: #3b82f6;
        }

        .paper-card__stats {
          display: flex;
          gap: 1rem;
          margin-bottom: 0.75rem;
          flex-wrap: wrap;
        }

        .paper-card__stats .stat {
          display: flex;
          align-items: center;
          gap: 0.375rem;
          font-size: 0.75rem;
          color: #94a3b8;
        }

        .paper-card__stats .stat svg {
          opacity: 0.7;
        }

        .paper-card__citations {
          display: flex;
          gap: 1rem;
          padding: 0.75rem;
          background: rgba(15, 23, 42, 0.5);
          border-radius: 8px;
          margin-bottom: 0.75rem;
        }

        .citation-stat {
          flex: 1;
          text-align: center;
        }

        .citation-value {
          display: block;
          font-size: 1.25rem;
          font-weight: 600;
          color: #f1f5f9;
        }

        .citation-stat--highlight .citation-value {
          color: #8b5cf6;
        }

        .citation-label {
          font-size: 0.625rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #64748b;
        }

        .paper-card__footer {
          margin-top: auto;
          padding-top: 0.75rem;
          border-top: 1px solid rgba(148, 163, 184, 0.1);
        }

        .paper-card__link {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.75rem;
          color: #3b82f6;
          text-decoration: none;
          transition: color 0.15s;
        }

        .paper-card__link:hover {
          color: #60a5fa;
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
      `}</style>

      <Link href="/discovery" className="back-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        Back to Discovery
      </Link>

      <header className="rising-papers-hero">
        <h1>Rising Papers</h1>
        <p>
          Discover papers gaining traction faster than average.
          Citation velocity measures how quickly papers are accumulating citations per month.
        </p>
      </header>

      <section className="rising-papers-filters">
        <div className="filter-group">
          <label>Min Citations</label>
          <select value={minCitations} onChange={(e) => setMinCitations(Number(e.target.value))}>
            <option value={3}>3+ citations</option>
            <option value={5}>5+ citations</option>
            <option value={10}>10+ citations</option>
            <option value={20}>20+ citations</option>
            <option value={50}>50+ citations</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Publication Age</label>
          <select value={maxMonths} onChange={(e) => setMaxMonths(Number(e.target.value))}>
            <option value={6}>Last 6 months</option>
            <option value={12}>Last 12 months</option>
            <option value={24}>Last 24 months</option>
            <option value={36}>Last 3 years</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Velocity Tier</label>
          <div className="tier-chips">
            <button
              className={`tier-chip ${!velocityFilter ? 'tier-chip--active' : ''}`}
              style={{
                backgroundColor: !velocityFilter ? '#1e40af' : '#1e293b',
                color: !velocityFilter ? '#fff' : '#94a3b8',
                borderColor: !velocityFilter ? '#3b82f6' : '#334155',
              }}
              onClick={() => setVelocityFilter('')}
            >
              All
            </button>
            {tierOrder.map((tier) => {
              const style = TIER_COLORS[tier];
              const isActive = velocityFilter === tier;
              return (
                <button
                  key={tier}
                  className={`tier-chip ${isActive ? 'tier-chip--active' : ''}`}
                  style={{
                    backgroundColor: style.bg,
                    color: style.text,
                    borderColor: style.border,
                  }}
                  onClick={() => setVelocityFilter(tier)}
                >
                  {style.label}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {!loading && !error && Object.keys(distribution).length > 0 && (
        <VelocityDistribution distribution={distribution} />
      )}

      {loading ? (
        <div className="rising-papers-loading">
          <div className="rising-papers-loading__spinner" />
          <span>Discovering rising papers...</span>
        </div>
      ) : error ? (
        <div className="rising-papers-error">
          <h3>Failed to load rising papers</h3>
          <p>{error}</p>
        </div>
      ) : papers.length === 0 ? (
        <div className="empty-state">
          <h3>No rising papers found</h3>
          <p>Try adjusting the filters to see more results.</p>
        </div>
      ) : velocityFilter ? (
        // Show flat grid when filtering by tier
        <>
          <p className="papers-summary">
            Showing {papers.length} papers with {TIER_COLORS[velocityFilter]?.label.toLowerCase()} velocity
          </p>
          <div className="papers-grid">
            {papers.map((paper) => (
              <PaperCard key={paper.id} paper={paper} />
            ))}
          </div>
        </>
      ) : (
        // Show grouped by tier when no filter
        <>
          <p className="papers-summary">
            Found {total} papers with citation velocity data
          </p>
          {tierOrder.map((tier) => {
            const tierPapers = papersByTier[tier];
            if (!tierPapers || tierPapers.length === 0) return null;

            const style = TIER_COLORS[tier];
            return (
              <section key={tier} className="tier-section">
                <header className="tier-section__header">
                  <h2
                    className="tier-section__title"
                    style={{ color: style.text }}
                  >
                    {style.label} Papers
                  </h2>
                  <span className="tier-section__count">{tierPapers.length} papers</span>
                </header>
                <div className="papers-grid">
                  {tierPapers.map((paper) => (
                    <PaperCard key={paper.id} paper={paper} />
                  ))}
                </div>
              </section>
            );
          })}
        </>
      )}
    </div>
  );
}
