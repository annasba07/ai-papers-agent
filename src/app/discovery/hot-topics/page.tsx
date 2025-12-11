'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

// Types matching the backend API response
interface TopPaper {
  id: string;
  title: string;
  citation_velocity: number;
  citation_count: number;
}

interface HotTopic {
  name: string;
  paper_count: number;
  total_citations: number;
  avg_citation_velocity: number;
  max_velocity: number;
  velocity_tier: string;
  trend_direction: string;
  trend_pct: number;
  categories: string[];
  top_papers: TopPaper[];
}

interface HotTopicsResponse {
  topics: HotTopic[];
  params: {
    days: number;
    min_papers: number;
    min_citations: number;
    limit: number;
    category: string | null;
    velocity_tier: string | null;
  };
}

// Velocity tier badge colors
const TIER_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  viral: { bg: '#fef3c7', text: '#92400e', border: '#f59e0b' },
  hot: { bg: '#fee2e2', text: '#991b1b', border: '#ef4444' },
  rising: { bg: '#dbeafe', text: '#1e40af', border: '#3b82f6' },
  growing: { bg: '#d1fae5', text: '#065f46', border: '#10b981' },
  emerging: { bg: '#e5e7eb', text: '#374151', border: '#6b7280' },
};

// Trend direction icons
const TrendIcon = ({ direction, pct }: { direction: string; pct: number }) => {
  if (direction === 'up') {
    return (
      <span className="trend-up" style={{ color: '#10b981' }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M7 17l5-5 5 5M7 7l5-5 5 5" />
        </svg>
        +{Math.abs(pct).toFixed(0)}%
      </span>
    );
  } else if (direction === 'down') {
    return (
      <span className="trend-down" style={{ color: '#ef4444' }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M7 7l5 5 5-5M7 17l5 5 5-5" />
        </svg>
        {pct.toFixed(0)}%
      </span>
    );
  }
  return <span className="trend-stable" style={{ color: '#6b7280' }}>--</span>;
};

// Topic card component
const TopicCard = ({ topic }: { topic: HotTopic }) => {
  const tierStyle = TIER_COLORS[topic.velocity_tier] || TIER_COLORS.emerging;

  return (
    <article className="topic-card">
      <header className="topic-card__header">
        <div className="topic-card__title-row">
          <h3 className="topic-card__name">{topic.name}</h3>
          <span
            className="topic-card__tier"
            style={{
              backgroundColor: tierStyle.bg,
              color: tierStyle.text,
              border: `1px solid ${tierStyle.border}`,
            }}
          >
            {topic.velocity_tier}
          </span>
        </div>
        <div className="topic-card__trend">
          <TrendIcon direction={topic.trend_direction} pct={topic.trend_pct} />
        </div>
      </header>

      <div className="topic-card__stats">
        <div className="stat">
          <span className="stat__value">{topic.paper_count}</span>
          <span className="stat__label">Papers</span>
        </div>
        <div className="stat">
          <span className="stat__value">{topic.total_citations}</span>
          <span className="stat__label">Citations</span>
        </div>
        <div className="stat">
          <span className="stat__value">{topic.avg_citation_velocity.toFixed(1)}</span>
          <span className="stat__label">Avg Vel</span>
        </div>
        <div className="stat stat--highlight">
          <span className="stat__value">{topic.max_velocity.toFixed(1)}</span>
          <span className="stat__label">Max Vel</span>
        </div>
      </div>

      <div className="topic-card__categories">
        {topic.categories.slice(0, 4).map((cat) => (
          <span key={cat} className="topic-card__category">{cat}</span>
        ))}
        {topic.categories.length > 4 && (
          <span className="topic-card__category-more">+{topic.categories.length - 4}</span>
        )}
      </div>

      <div className="topic-card__papers">
        <h4>Top Papers</h4>
        <ul>
          {topic.top_papers.slice(0, 3).map((paper) => (
            <li key={paper.id}>
              <Link
                href={`https://arxiv.org/abs/${paper.id.split('v')[0]}`}
                target="_blank"
                rel="noopener"
                className="topic-card__paper-link"
              >
                <span className="paper-title">{paper.title.slice(0, 60)}{paper.title.length > 60 ? '...' : ''}</span>
                <span className="paper-velocity">{paper.citation_velocity.toFixed(1)}/mo</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </article>
  );
};

// Main page component
export default function HotTopicsPage() {
  const [topics, setTopics] = useState<HotTopic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [days, setDays] = useState(90);
  const [velocityTier, setVelocityTier] = useState<string>('');
  const [minPapers, setMinPapers] = useState(3);

  useEffect(() => {
    const fetchTopics = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams({
          limit: '30',
          days: days.toString(),
          min_papers: minPapers.toString(),
          min_citations: '3',
        });
        if (velocityTier) params.set('velocity_tier', velocityTier);

        const response = await fetch(`/api/discovery/hot-topics?${params.toString()}`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data: HotTopicsResponse = await response.json();
        setTopics(data.topics || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load hot topics');
      } finally {
        setLoading(false);
      }
    };

    fetchTopics();
  }, [days, velocityTier, minPapers]);

  // Group topics by tier for display
  const tierOrder = ['viral', 'hot', 'rising', 'growing', 'emerging'];
  const topicsByTier = tierOrder.reduce((acc, tier) => {
    acc[tier] = topics.filter((t) => t.velocity_tier === tier);
    return acc;
  }, {} as Record<string, HotTopic[]>);

  return (
    <div className="hot-topics-page">
      <style jsx global>{`
        .hot-topics-page {
          min-height: 100vh;
          background: linear-gradient(to bottom, #0f172a, #1e293b);
          color: #e2e8f0;
          padding: 2rem;
        }

        .hot-topics-hero {
          text-align: center;
          margin-bottom: 3rem;
        }

        .hot-topics-hero h1 {
          font-size: 2.5rem;
          font-weight: 700;
          background: linear-gradient(135deg, #f59e0b, #ef4444, #8b5cf6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 0.5rem;
        }

        .hot-topics-hero p {
          color: #94a3b8;
          font-size: 1.1rem;
          max-width: 600px;
          margin: 0 auto;
        }

        .hot-topics-filters {
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

        .hot-topics-loading {
          text-align: center;
          padding: 4rem;
        }

        .hot-topics-loading__spinner {
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

        .hot-topics-error {
          text-align: center;
          padding: 3rem;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 12px;
          color: #fca5a5;
        }

        .topics-grid {
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
          text-transform: capitalize;
        }

        .tier-section__count {
          background: rgba(148, 163, 184, 0.1);
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          color: #94a3b8;
        }

        .topic-card {
          background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 12px;
          padding: 1.25rem;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .topic-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
          border-color: rgba(148, 163, 184, 0.2);
        }

        .topic-card__header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .topic-card__title-row {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex-wrap: wrap;
        }

        .topic-card__name {
          font-size: 1.1rem;
          font-weight: 600;
          color: #f1f5f9;
          margin: 0;
        }

        .topic-card__tier {
          font-size: 0.625rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .topic-card__trend {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .trend-up, .trend-down, .trend-stable {
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }

        .topic-card__stats {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 0.5rem;
          margin-bottom: 1rem;
          padding: 0.75rem;
          background: rgba(15, 23, 42, 0.5);
          border-radius: 8px;
        }

        .stat {
          text-align: center;
        }

        .stat__value {
          display: block;
          font-size: 1.125rem;
          font-weight: 600;
          color: #f1f5f9;
        }

        .stat__label {
          display: block;
          font-size: 0.625rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #64748b;
        }

        .stat--highlight .stat__value {
          color: #f59e0b;
        }

        .topic-card__categories {
          display: flex;
          flex-wrap: wrap;
          gap: 0.375rem;
          margin-bottom: 1rem;
        }

        .topic-card__category {
          font-size: 0.625rem;
          padding: 0.125rem 0.5rem;
          background: rgba(59, 130, 246, 0.1);
          color: #93c5fd;
          border-radius: 4px;
        }

        .topic-card__category-more {
          font-size: 0.625rem;
          padding: 0.125rem 0.5rem;
          background: rgba(148, 163, 184, 0.1);
          color: #94a3b8;
          border-radius: 4px;
        }

        .topic-card__papers {
          border-top: 1px solid rgba(148, 163, 184, 0.1);
          padding-top: 1rem;
        }

        .topic-card__papers h4 {
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #64748b;
          margin: 0 0 0.75rem 0;
        }

        .topic-card__papers ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .topic-card__papers li {
          margin-bottom: 0.5rem;
        }

        .topic-card__paper-link {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 0.5rem;
          padding: 0.5rem;
          background: rgba(15, 23, 42, 0.5);
          border-radius: 6px;
          text-decoration: none;
          transition: background 0.15s;
        }

        .topic-card__paper-link:hover {
          background: rgba(59, 130, 246, 0.1);
        }

        .paper-title {
          font-size: 0.8rem;
          color: #cbd5e1;
          line-height: 1.4;
        }

        .paper-velocity {
          font-size: 0.7rem;
          color: #f59e0b;
          white-space: nowrap;
          font-weight: 500;
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

      <header className="hot-topics-hero">
        <h1>Hot Topics Dashboard</h1>
        <p>
          Research areas gaining momentum based on citation velocity.
          Topics are clustered by concept and ranked by how fast papers are accumulating citations.
        </p>
      </header>

      <section className="hot-topics-filters">
        <div className="filter-group">
          <label>Time Window</label>
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
            <option value={30}>Last 30 days</option>
            <option value={60}>Last 60 days</option>
            <option value={90}>Last 90 days</option>
            <option value={180}>Last 6 months</option>
            <option value={365}>Last year</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Min Papers per Topic</label>
          <select value={minPapers} onChange={(e) => setMinPapers(Number(e.target.value))}>
            <option value={2}>2+ papers</option>
            <option value={3}>3+ papers</option>
            <option value={5}>5+ papers</option>
            <option value={10}>10+ papers</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Velocity Tier</label>
          <div className="tier-chips">
            <button
              className={`tier-chip ${!velocityTier ? 'tier-chip--active' : ''}`}
              style={{
                backgroundColor: !velocityTier ? '#1e40af' : '#1e293b',
                color: !velocityTier ? '#fff' : '#94a3b8',
                borderColor: !velocityTier ? '#3b82f6' : '#334155',
              }}
              onClick={() => setVelocityTier('')}
            >
              All
            </button>
            {tierOrder.map((tier) => {
              const style = TIER_COLORS[tier];
              const isActive = velocityTier === tier;
              return (
                <button
                  key={tier}
                  className={`tier-chip ${isActive ? 'tier-chip--active' : ''}`}
                  style={{
                    backgroundColor: style.bg,
                    color: style.text,
                    borderColor: style.border,
                  }}
                  onClick={() => setVelocityTier(tier)}
                >
                  {tier}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {loading ? (
        <div className="hot-topics-loading">
          <div className="hot-topics-loading__spinner" />
          <span>Analyzing research momentum...</span>
        </div>
      ) : error ? (
        <div className="hot-topics-error">
          <h3>Failed to load hot topics</h3>
          <p>{error}</p>
        </div>
      ) : topics.length === 0 ? (
        <div className="empty-state">
          <h3>No hot topics found</h3>
          <p>Try adjusting the filters to see more results.</p>
        </div>
      ) : velocityTier ? (
        // Show flat grid when filtering by tier
        <div className="topics-grid">
          {topics.map((topic) => (
            <TopicCard key={topic.name} topic={topic} />
          ))}
        </div>
      ) : (
        // Show grouped by tier when no filter
        tierOrder.map((tier) => {
          const tierTopics = topicsByTier[tier];
          if (!tierTopics || tierTopics.length === 0) return null;

          return (
            <section key={tier} className="tier-section">
              <header className="tier-section__header">
                <h2
                  className="tier-section__title"
                  style={{ color: TIER_COLORS[tier]?.text || '#94a3b8' }}
                >
                  {tier} Topics
                </h2>
                <span className="tier-section__count">{tierTopics.length} topics</span>
              </header>
              <div className="topics-grid">
                {tierTopics.map((topic) => (
                  <TopicCard key={topic.name} topic={topic} />
                ))}
              </div>
            </section>
          );
        })
      )}
    </div>
  );
}
