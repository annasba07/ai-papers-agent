'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface ReproduciblePaper {
  id: string;
  title: string;
  reproducibility_score: number | null;
  code_availability: string | null;
  implementation_detail: string | null;
  github_urls: string[] | null;
  datasets_mentioned: string[] | null;
  has_code: boolean;
}

interface ReproducibleResponse {
  papers: ReproduciblePaper[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

function ReproducibilityBadge({ score }: { score: number | null }) {
  if (score === null) return null;

  const getColor = (s: number) => {
    if (s >= 9) return { bg: '#dcfce7', text: '#166534', border: '#86efac' };
    if (s >= 7) return { bg: '#dbeafe', text: '#1e40af', border: '#93c5fd' };
    if (s >= 5) return { bg: '#fef3c7', text: '#92400e', border: '#fcd34d' };
    return { bg: '#fee2e2', text: '#991b1b', border: '#fca5a5' };
  };

  const colors = getColor(score);

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
      }}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      {score}/10
    </span>
  );
}

function CodeAvailabilityBadge({ available, hasCode }: { available: string | null; hasCode: boolean }) {
  const isAvailable = available === 'yes' || hasCode;

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 10px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 500,
        backgroundColor: isAvailable ? '#dcfce7' : '#f3f4f6',
        color: isAvailable ? '#166534' : '#6b7280',
        border: `1px solid ${isAvailable ? '#86efac' : '#d1d5db'}`,
      }}
    >
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
      {isAvailable ? 'Code Available' : 'No Code'}
    </span>
  );
}

function ReproducibleCard({ paper }: { paper: ReproduciblePaper }) {
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
        <ReproducibilityBadge score={paper.reproducibility_score} />
      </div>

      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
        <CodeAvailabilityBadge available={paper.code_availability} hasCode={paper.has_code} />
        {paper.implementation_detail && (
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
            {paper.implementation_detail} Detail
          </span>
        )}
      </div>

      {paper.github_urls && paper.github_urls.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '6px', textTransform: 'uppercase' }}>
            Code Links
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {paper.github_urls.slice(0, expanded ? undefined : 2).map((url, idx) => (
              <a
                key={idx}
                href={url.startsWith('http') ? url : `https://${url}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '13px',
                  color: '#2563eb',
                  textDecoration: 'none',
                  padding: '6px 10px',
                  backgroundColor: '#eff6ff',
                  borderRadius: '6px',
                  maxWidth: '100%',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#dbeafe'; }}
                onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#eff6ff'; }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
                {url.length > 50 ? url.substring(0, 50) + '...' : url}
              </a>
            ))}
            {!expanded && paper.github_urls.length > 2 && (
              <span style={{ fontSize: '12px', color: '#6b7280', padding: '4px' }}>
                +{paper.github_urls.length - 2} more links
              </span>
            )}
          </div>
        </div>
      )}

      {expanded && paper.datasets_mentioned && paper.datasets_mentioned.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '8px', textTransform: 'uppercase' }}>
            Datasets Mentioned
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {paper.datasets_mentioned.map((dataset, idx) => (
              <span
                key={idx}
                style={{
                  display: 'inline-block',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontSize: '12px',
                  backgroundColor: '#fef3c7',
                  color: '#92400e',
                  border: '1px solid #fcd34d',
                }}
              >
                {dataset}
              </span>
            ))}
          </div>
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

export default function ReproducibleDashboard() {
  const [papers, setPapers] = useState<ReproduciblePaper[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [minReproducibility, setMinReproducibility] = useState('');
  const [codeAvailability, setCodeAvailability] = useState('all');
  const [category, setCategory] = useState('all');

  const fetchPapers = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ limit: '20' });
      if (minReproducibility) params.set('min_reproducibility', minReproducibility);
      if (codeAvailability !== 'all') params.set('code_availability', codeAvailability);
      if (category !== 'all') params.set('category', category);

      const response = await fetch(`/api/discovery/reproducible?${params.toString()}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data: ReproducibleResponse = await response.json();
      setPapers(data.papers || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load papers');
    } finally {
      setLoading(false);
    }
  }, [minReproducibility, codeAvailability, category]);

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
            Reproducible Papers
          </h1>
          <p style={{ fontSize: '16px', color: '#6b7280', margin: 0 }}>
            Papers with code, datasets, and high reproducibility scores for hands-on implementation
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
              Min Reproducibility
            </label>
            <select
              value={minReproducibility}
              onChange={(e) => setMinReproducibility(e.target.value)}
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
              <option value="5">5+ (Moderate)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px' }}>
              Code Availability
            </label>
            <select
              value={codeAvailability}
              onChange={(e) => setCodeAvailability(e.target.value)}
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
              <option value="yes">Code Available</option>
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
              <strong style={{ color: '#111827' }}>{total.toLocaleString()}</strong> reproducible papers
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
            Loading reproducible papers...
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
          <ReproducibleCard key={paper.id} paper={paper} />
        ))}
      </div>
    </div>
  );
}
