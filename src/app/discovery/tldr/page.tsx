'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface TLDRPaper {
  id: string;
  title: string;
  published: string | null;
  category: string;
  executive_summary: string | null;
  problem_statement: string | null;
  proposed_solution: string | null;
  key_contribution: string | null;
  reading_time_minutes: number | null;
}

interface TLDRResponse {
  papers: TLDRPaper[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// Reading time badge component
function ReadingTimeBadge({ minutes }: { minutes: number | null }) {
  if (!minutes) return null;

  const getColor = () => {
    if (minutes <= 10) return '#22c55e'; // green - quick read
    if (minutes <= 20) return '#3b82f6'; // blue - moderate
    if (minutes <= 30) return '#f59e0b'; // yellow - longer
    return '#ef4444'; // red - lengthy
  };

  const getLabel = () => {
    if (minutes <= 10) return 'Quick';
    if (minutes <= 20) return 'Moderate';
    if (minutes <= 30) return 'Longer';
    return 'In-depth';
  };

  return (
    <span className="reading-badge" style={{ borderColor: getColor(), color: getColor() }}>
      {minutes} min {getLabel()}
      <style jsx>{`
        .reading-badge {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 2px 8px;
          border: 1px solid;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 500;
        }
      `}</style>
    </span>
  );
}

// Paper card component for TL;DR display
function TLDRCard({ paper }: { paper: TLDRPaper }) {
  const [expanded, setExpanded] = useState(false);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'cs.LG': '#3b82f6',
      'cs.CL': '#8b5cf6',
      'cs.CV': '#10b981',
      'cs.AI': '#f59e0b',
      'stat.ML': '#ec4899',
      'cs.NE': '#6366f1',
    };
    return colors[category] || '#6b7280';
  };

  return (
    <div className="tldr-card">
      <div className="card-header">
        <div className="meta-row">
          <span className="category" style={{ backgroundColor: getCategoryColor(paper.category) }}>
            {paper.category}
          </span>
          {paper.published && (
            <span className="date">{formatDate(paper.published)}</span>
          )}
          <ReadingTimeBadge minutes={paper.reading_time_minutes} />
        </div>
        <Link href={`/papers/${paper.id}`} className="paper-title">
          {paper.title}
        </Link>
      </div>

      {paper.executive_summary && (
        <div className="summary-section">
          <h4>TL;DR</h4>
          <p>{paper.executive_summary}</p>
        </div>
      )}

      {(paper.problem_statement || paper.proposed_solution || paper.key_contribution) && (
        <button
          className="expand-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'Show less' : 'Show details'}
          <span className={`arrow ${expanded ? 'up' : 'down'}`}>
            {expanded ? '\u25B2' : '\u25BC'}
          </span>
        </button>
      )}

      {expanded && (
        <div className="details-section">
          {paper.problem_statement && (
            <div className="detail-block">
              <h5>Problem</h5>
              <p>{paper.problem_statement}</p>
            </div>
          )}
          {paper.proposed_solution && (
            <div className="detail-block">
              <h5>Solution</h5>
              <p>{paper.proposed_solution}</p>
            </div>
          )}
          {paper.key_contribution && (
            <div className="detail-block">
              <h5>Key Contribution</h5>
              <p>{paper.key_contribution}</p>
            </div>
          )}
        </div>
      )}

      <div className="card-actions">
        <Link href={`/papers/${paper.id}`} className="action-link">
          Full Details
        </Link>
        <a
          href={`https://arxiv.org/abs/${paper.id.replace('v', '').replace(/v\d+$/, '')}`}
          target="_blank"
          rel="noopener noreferrer"
          className="action-link secondary"
        >
          arXiv
        </a>
      </div>

      <style jsx>{`
        .tldr-card {
          background: #1a1a2e;
          border: 1px solid #2d2d44;
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 16px;
          transition: border-color 0.2s;
        }
        .tldr-card:hover {
          border-color: #3b82f6;
        }
        .card-header {
          margin-bottom: 16px;
        }
        .meta-row {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 10px;
          flex-wrap: wrap;
        }
        .category {
          padding: 2px 10px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
          color: white;
        }
        .date {
          color: #9ca3af;
          font-size: 13px;
        }
        .paper-title {
          font-size: 17px;
          font-weight: 600;
          color: #e5e7eb;
          text-decoration: none;
          line-height: 1.4;
          display: block;
        }
        .paper-title:hover {
          color: #3b82f6;
        }
        .summary-section {
          background: #0d0d1a;
          border-radius: 8px;
          padding: 14px;
          margin-bottom: 12px;
        }
        .summary-section h4 {
          color: #3b82f6;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 8px;
        }
        .summary-section p {
          color: #d1d5db;
          font-size: 14px;
          line-height: 1.6;
          margin: 0;
        }
        .expand-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          background: none;
          border: none;
          color: #9ca3af;
          font-size: 13px;
          cursor: pointer;
          padding: 8px 0;
          transition: color 0.2s;
        }
        .expand-btn:hover {
          color: #3b82f6;
        }
        .arrow {
          font-size: 10px;
        }
        .details-section {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #2d2d44;
        }
        .detail-block {
          margin-bottom: 14px;
        }
        .detail-block:last-child {
          margin-bottom: 0;
        }
        .detail-block h5 {
          color: #9ca3af;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 6px;
        }
        .detail-block p {
          color: #d1d5db;
          font-size: 14px;
          line-height: 1.5;
          margin: 0;
        }
        .card-actions {
          display: flex;
          gap: 12px;
          margin-top: 16px;
          padding-top: 12px;
          border-top: 1px solid #2d2d44;
        }
        .action-link {
          color: #3b82f6;
          font-size: 13px;
          font-weight: 500;
          text-decoration: none;
        }
        .action-link:hover {
          text-decoration: underline;
        }
        .action-link.secondary {
          color: #9ca3af;
        }
        .action-link.secondary:hover {
          color: #d1d5db;
        }
      `}</style>
    </div>
  );
}

export default function TLDRPage() {
  const [papers, setPapers] = useState<TLDRPaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  // Filters
  const [days, setDays] = useState<number>(30);
  const [minImpact, setMinImpact] = useState<number | ''>('');
  const [category, setCategory] = useState<string>('all');

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'cs.LG', label: 'Machine Learning' },
    { value: 'cs.CL', label: 'Computation & Language' },
    { value: 'cs.CV', label: 'Computer Vision' },
    { value: 'cs.AI', label: 'Artificial Intelligence' },
    { value: 'stat.ML', label: 'Statistics ML' },
    { value: 'cs.NE', label: 'Neural & Evolutionary' },
  ];

  const dayOptions = [
    { value: 7, label: 'Last 7 days' },
    { value: 14, label: 'Last 14 days' },
    { value: 30, label: 'Last 30 days' },
    { value: 60, label: 'Last 60 days' },
    { value: 90, label: 'Last 90 days' },
  ];

  const fetchPapers = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        days: days.toString(),
        limit: '50',
      });
      if (minImpact !== '') params.set('min_impact', minImpact.toString());
      if (category !== 'all') params.set('category', category);

      const response = await fetch(`/api/discovery/tldr?${params.toString()}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data: TLDRResponse = await response.json();
      setPapers(data.papers || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch papers');
    } finally {
      setLoading(false);
    }
  }, [days, minImpact, category]);

  useEffect(() => {
    fetchPapers();
  }, [fetchPapers]);

  // Stats for papers with summaries
  const papersWithSummary = papers.filter(p => p.executive_summary).length;
  const avgReadingTime = papers.length > 0
    ? Math.round(papers.reduce((acc, p) => acc + (p.reading_time_minutes || 0), 0) / papers.length)
    : 0;

  return (
    <div className="tldr-page">
      <header className="page-header">
        <div className="header-content">
          <Link href="/discovery" className="back-link">
            &larr; Discovery
          </Link>
          <h1>TL;DR Feed</h1>
          <p className="subtitle">
            Quick summaries to stay up-to-date with the latest research
          </p>
        </div>
      </header>

      <div className="filters-section">
        <div className="filter-group">
          <label>Time Range</label>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          >
            {dayOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Min Impact</label>
          <select
            value={minImpact}
            onChange={(e) => setMinImpact(e.target.value === '' ? '' : Number(e.target.value))}
          >
            <option value="">Any</option>
            <option value="5">5+ (Moderate)</option>
            <option value="7">7+ (High)</option>
            <option value="8">8+ (Very High)</option>
            <option value="9">9+ (Transformative)</option>
          </select>
        </div>
      </div>

      <div className="stats-bar">
        <div className="stat">
          <span className="stat-value">{total}</span>
          <span className="stat-label">papers found</span>
        </div>
        <div className="stat">
          <span className="stat-value">{papersWithSummary}</span>
          <span className="stat-label">with summaries</span>
        </div>
        <div className="stat">
          <span className="stat-value">{avgReadingTime} min</span>
          <span className="stat-label">avg reading time</span>
        </div>
      </div>

      <main className="papers-section">
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <span>Loading papers...</span>
          </div>
        )}

        {error && (
          <div className="error">
            <span>Error: {error}</span>
            <button onClick={fetchPapers}>Retry</button>
          </div>
        )}

        {!loading && !error && papers.length === 0 && (
          <div className="empty">
            <h3>No papers found</h3>
            <p>Try adjusting your filters or expanding the time range.</p>
          </div>
        )}

        {!loading && !error && papers.length > 0 && (
          <div className="papers-list">
            {papers.map(paper => (
              <TLDRCard key={paper.id} paper={paper} />
            ))}
          </div>
        )}
      </main>

      <style jsx>{`
        .tldr-page {
          min-height: 100vh;
          background: #0a0a14;
          color: #e5e7eb;
        }
        .page-header {
          background: linear-gradient(135deg, #1a1a2e 0%, #0d0d1a 100%);
          padding: 24px;
          border-bottom: 1px solid #2d2d44;
        }
        .header-content {
          max-width: 900px;
          margin: 0 auto;
        }
        .back-link {
          color: #9ca3af;
          text-decoration: none;
          font-size: 14px;
          display: inline-block;
          margin-bottom: 12px;
        }
        .back-link:hover {
          color: #3b82f6;
        }
        .page-header h1 {
          font-size: 28px;
          font-weight: 700;
          margin: 0 0 8px 0;
          background: linear-gradient(135deg, #3b82f6, #8b5cf6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .subtitle {
          color: #9ca3af;
          font-size: 15px;
          margin: 0;
        }
        .filters-section {
          max-width: 900px;
          margin: 0 auto;
          padding: 20px 24px;
          display: flex;
          gap: 16px;
          flex-wrap: wrap;
        }
        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .filter-group label {
          color: #9ca3af;
          font-size: 12px;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .filter-group select {
          background: #1a1a2e;
          border: 1px solid #2d2d44;
          border-radius: 8px;
          color: #e5e7eb;
          padding: 8px 12px;
          font-size: 14px;
          cursor: pointer;
          min-width: 150px;
        }
        .filter-group select:hover {
          border-color: #3b82f6;
        }
        .stats-bar {
          max-width: 900px;
          margin: 0 auto;
          padding: 0 24px 20px;
          display: flex;
          gap: 32px;
        }
        .stat {
          display: flex;
          flex-direction: column;
        }
        .stat-value {
          font-size: 20px;
          font-weight: 700;
          color: #3b82f6;
        }
        .stat-label {
          font-size: 12px;
          color: #6b7280;
        }
        .papers-section {
          max-width: 900px;
          margin: 0 auto;
          padding: 0 24px 40px;
        }
        .loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          padding: 60px 0;
          color: #9ca3af;
        }
        .spinner {
          width: 32px;
          height: 32px;
          border: 3px solid #2d2d44;
          border-top-color: #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .error {
          background: #1a1a2e;
          border: 1px solid #ef4444;
          border-radius: 12px;
          padding: 20px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          color: #ef4444;
        }
        .error button {
          background: #ef4444;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 6px;
          cursor: pointer;
        }
        .empty {
          text-align: center;
          padding: 60px 0;
        }
        .empty h3 {
          color: #e5e7eb;
          margin-bottom: 8px;
        }
        .empty p {
          color: #6b7280;
        }
        .papers-list {
          display: flex;
          flex-direction: column;
        }
      `}</style>
    </div>
  );
}
