'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface PracticalPaper {
  id: string;
  title: string;
  category: string | null;
  industry_relevance: string | null;
  impact_score: number | null;
  use_cases: string[] | null;
  scalability: string | null;
  deployment_considerations: string | null;
  limitations: string[] | null;
  ai_practical_score: string | null;
}

interface PracticalResponse {
  papers: PracticalPaper[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
  industry_relevance_filter: string | null;
}

function IndustryRelevanceBadge({ relevance }: { relevance: string | null }) {
  if (!relevance) return null;

  const getColor = (r: string) => {
    const lower = r.toLowerCase();
    if (lower === 'high') return { bg: '#dcfce7', text: '#166534', border: '#86efac' };
    if (lower === 'medium') return { bg: '#fef3c7', text: '#92400e', border: '#fcd34d' };
    return { bg: '#f3f4f6', text: '#6b7280', border: '#d1d5db' };
  };

  const colors = getColor(relevance);

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 10px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 600,
        backgroundColor: colors.bg,
        color: colors.text,
        border: `1px solid ${colors.border}`,
        textTransform: 'capitalize',
      }}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
      {relevance} Relevance
    </span>
  );
}

function ImpactScoreBadge({ score }: { score: number | null }) {
  if (score === null) return null;

  const getColor = (s: number) => {
    if (s >= 9) return { bg: '#dbeafe', text: '#1e40af', border: '#93c5fd' };
    if (s >= 7) return { bg: '#e0e7ff', text: '#3730a3', border: '#a5b4fc' };
    return { bg: '#f3f4f6', text: '#6b7280', border: '#d1d5db' };
  };

  const colors = getColor(score);

  return (
    <span
      style={{
        display: 'inline-block',
        padding: '4px 10px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 500,
        backgroundColor: colors.bg,
        color: colors.text,
        border: `1px solid ${colors.border}`,
      }}
    >
      Impact: {score}/10
    </span>
  );
}

function PracticalCard({ paper }: { paper: PracticalPaper }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '16px',
        backgroundColor: '#ffffff',
        transition: 'box-shadow 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <Link
          href={`/paper/${paper.id}`}
          style={{
            fontSize: '16px',
            fontWeight: 600,
            color: '#1f2937',
            textDecoration: 'none',
            flex: 1,
            marginRight: '12px',
            lineHeight: 1.4,
          }}
          onMouseEnter={(e) => { e.currentTarget.style.color = '#2563eb'; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = '#1f2937'; }}
        >
          {paper.title}
        </Link>
        <IndustryRelevanceBadge relevance={paper.industry_relevance} />
      </div>

      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
        {paper.category && (
          <span
            style={{
              display: 'inline-block',
              padding: '4px 10px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 500,
              backgroundColor: '#f3f4f6',
              color: '#374151',
              border: '1px solid #e5e7eb',
            }}
          >
            {paper.category}
          </span>
        )}
        <ImpactScoreBadge score={paper.impact_score} />
        {paper.ai_practical_score && (
          <span
            style={{
              display: 'inline-block',
              padding: '4px 10px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 500,
              backgroundColor: '#f3e8ff',
              color: '#6b21a8',
              border: '1px solid #d8b4fe',
              textTransform: 'capitalize',
            }}
          >
            Practical: {paper.ai_practical_score}
          </span>
        )}
      </div>

      {paper.use_cases && paper.use_cases.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '8px', textTransform: 'uppercase' }}>
            Use Cases
          </div>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {paper.use_cases.slice(0, expanded ? undefined : 3).map((useCase, idx) => (
              <li
                key={idx}
                style={{
                  fontSize: '13px',
                  color: '#4b5563',
                  lineHeight: 1.6,
                  marginBottom: '4px',
                }}
              >
                {useCase}
              </li>
            ))}
          </ul>
          {!expanded && paper.use_cases.length > 3 && (
            <span style={{ fontSize: '12px', color: '#6b7280', marginLeft: '20px' }}>
              +{paper.use_cases.length - 3} more use cases
            </span>
          )}
        </div>
      )}

      {expanded && paper.scalability && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>
            Scalability
          </div>
          <p style={{ fontSize: '14px', color: '#4b5563', lineHeight: 1.6, margin: 0, backgroundColor: '#f0fdf4', padding: '12px', borderRadius: '8px' }}>
            {paper.scalability}
          </p>
        </div>
      )}

      {expanded && paper.deployment_considerations && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>
            Deployment Considerations
          </div>
          <p style={{ fontSize: '14px', color: '#4b5563', lineHeight: 1.6, margin: 0, backgroundColor: '#eff6ff', padding: '12px', borderRadius: '8px' }}>
            {paper.deployment_considerations}
          </p>
        </div>
      )}

      {expanded && paper.limitations && paper.limitations.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '8px', textTransform: 'uppercase' }}>
            Limitations
          </div>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {paper.limitations.map((limitation, idx) => (
              <li
                key={idx}
                style={{
                  fontSize: '13px',
                  color: '#9ca3af',
                  lineHeight: 1.6,
                  marginBottom: '4px',
                }}
              >
                {limitation}
              </li>
            ))}
          </ul>
        </div>
      )}

      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          marginTop: '8px',
          padding: '6px 12px',
          borderRadius: '6px',
          border: '1px solid #e5e7eb',
          backgroundColor: '#ffffff',
          color: '#6b7280',
          fontSize: '12px',
          cursor: 'pointer',
          transition: 'all 0.2s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#f3f4f6';
          e.currentTarget.style.color = '#374151';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = '#ffffff';
          e.currentTarget.style.color = '#6b7280';
        }}
      >
        {expanded ? 'Show Less' : 'Show More Details'}
      </button>
    </div>
  );
}

export default function PracticalDashboard() {
  const [papers, setPapers] = useState<PracticalPaper[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [industryRelevance, setIndustryRelevance] = useState('high');
  const [minImpact, setMinImpact] = useState('');
  const [category, setCategory] = useState('all');

  const fetchPapers = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ limit: '20' });
      if (industryRelevance !== 'all') params.set('industry_relevance', industryRelevance);
      if (minImpact) params.set('min_impact', minImpact);
      if (category !== 'all') params.set('category', category);

      const response = await fetch(`/api/discovery/practical?${params.toString()}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data: PracticalResponse = await response.json();
      setPapers(data.papers || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load papers');
    } finally {
      setLoading(false);
    }
  }, [industryRelevance, minImpact, category]);

  useEffect(() => {
    fetchPapers();
  }, [fetchPapers]);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '32px 24px' }}>
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <Link
            href="/discovery"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              color: '#6b7280',
              fontSize: '14px',
              textDecoration: 'none',
              marginBottom: '16px',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = '#2563eb'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = '#6b7280'; }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '4px' }}>
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            Back to Discovery
          </Link>
          <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#111827', margin: '0 0 8px 0' }}>
            Practical Papers
          </h1>
          <p style={{ fontSize: '16px', color: '#6b7280', margin: 0 }}>
            Industry-relevant research with real-world use cases, scalability analysis, and deployment guidance
          </p>
        </div>

        {/* Filters */}
        <div style={{
          display: 'flex',
          gap: '16px',
          marginBottom: '24px',
          flexWrap: 'wrap',
          alignItems: 'center',
        }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px' }}>
              Industry Relevance
            </label>
            <select
              value={industryRelevance}
              onChange={(e) => setIndustryRelevance(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                backgroundColor: '#ffffff',
                fontSize: '14px',
                color: '#374151',
                cursor: 'pointer',
                minWidth: '130px',
              }}
            >
              <option value="all">Any</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px' }}>
              Min Impact Score
            </label>
            <select
              value={minImpact}
              onChange={(e) => setMinImpact(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                backgroundColor: '#ffffff',
                fontSize: '14px',
                color: '#374151',
                cursor: 'pointer',
                minWidth: '130px',
              }}
            >
              <option value="">Any Score</option>
              <option value="9">9+ (Excellent)</option>
              <option value="8">8+ (Very Good)</option>
              <option value="7">7+ (Good)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px' }}>
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                backgroundColor: '#ffffff',
                fontSize: '14px',
                color: '#374151',
                cursor: 'pointer',
                minWidth: '150px',
              }}
            >
              <option value="all">All Categories</option>
              <option value="cs.LG">Machine Learning</option>
              <option value="cs.CL">NLP</option>
              <option value="cs.CV">Computer Vision</option>
              <option value="cs.AI">Artificial Intelligence</option>
              <option value="stat.ML">Statistics ML</option>
            </select>
          </div>

          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'flex-end' }}>
            <span style={{ fontSize: '14px', color: '#6b7280' }}>
              <strong style={{ color: '#111827' }}>{total.toLocaleString()}</strong> practical papers
            </span>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '48px', color: '#6b7280' }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '3px solid #e5e7eb',
              borderTopColor: '#3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 16px',
            }} />
            Loading practical papers...
            <style>{`
              @keyframes spin {
                to { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            padding: '16px',
            backgroundColor: '#fef2f2',
            borderRadius: '8px',
            color: '#dc2626',
            marginBottom: '24px',
          }}>
            Error: {error}
          </div>
        )}

        {/* Papers */}
        {!loading && !error && papers.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px', color: '#6b7280' }}>
            No papers found with the selected filters
          </div>
        )}

        {!loading && !error && papers.map(paper => (
          <PracticalCard key={paper.id} paper={paper} />
        ))}
      </div>
    </div>
  );
}
