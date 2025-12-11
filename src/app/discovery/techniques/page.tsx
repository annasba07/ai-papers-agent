'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface TechniquePaper {
  id: string;
  title: string;
  novelty_type: string | null;
  novelty_description: string | null;
  methodology_approach: string | null;
  key_components: string[] | null;
  architecture: string | null;
}

interface TechniquesResponse {
  papers: TechniquePaper[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
  novelty_type_distribution: Record<string, number>;
}

// Main novelty types to filter by
const NOVELTY_TYPES = [
  { value: 'all', label: 'All Types' },
  { value: 'algorithmic', label: 'Algorithmic' },
  { value: 'architectural', label: 'Architectural' },
  { value: 'theoretical', label: 'Theoretical' },
  { value: 'empirical', label: 'Empirical' },
  { value: 'application', label: 'Application' },
  { value: 'dataset', label: 'Dataset' },
];

function NoveltyBadge({ type }: { type: string | null }) {
  if (!type) return null;

  const getColor = (t: string) => {
    const lower = t.toLowerCase();
    if (lower.includes('algorithmic')) return { bg: '#dbeafe', text: '#1e40af', border: '#93c5fd' };
    if (lower.includes('architectural')) return { bg: '#fce7f3', text: '#9d174d', border: '#f9a8d4' };
    if (lower.includes('theoretical')) return { bg: '#f3e8ff', text: '#6b21a8', border: '#d8b4fe' };
    if (lower.includes('empirical')) return { bg: '#dcfce7', text: '#166534', border: '#86efac' };
    if (lower.includes('application')) return { bg: '#fef3c7', text: '#92400e', border: '#fcd34d' };
    if (lower.includes('dataset')) return { bg: '#e0e7ff', text: '#3730a3', border: '#a5b4fc' };
    return { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
  };

  const colors = getColor(type);

  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 500,
        backgroundColor: colors.bg,
        color: colors.text,
        border: `1px solid ${colors.border}`,
        textTransform: 'capitalize',
      }}
    >
      {type}
    </span>
  );
}

function TechniqueCard({ paper }: { paper: TechniquePaper }) {
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
        <NoveltyBadge type={paper.novelty_type} />
      </div>

      {paper.methodology_approach && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>
            Methodology
          </div>
          <p style={{ fontSize: '14px', color: '#4b5563', lineHeight: 1.6, margin: 0 }}>
            {expanded ? paper.methodology_approach : paper.methodology_approach.slice(0, 250) + (paper.methodology_approach.length > 250 ? '...' : '')}
          </p>
        </div>
      )}

      {paper.key_components && paper.key_components.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '8px', textTransform: 'uppercase' }}>
            Key Components
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {paper.key_components.slice(0, expanded ? undefined : 5).map((component, idx) => (
              <span
                key={idx}
                style={{
                  display: 'inline-block',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontSize: '12px',
                  backgroundColor: '#f3f4f6',
                  color: '#374151',
                  border: '1px solid #e5e7eb',
                }}
              >
                {component}
              </span>
            ))}
            {!expanded && paper.key_components.length > 5 && (
              <span style={{ fontSize: '12px', color: '#6b7280', padding: '4px' }}>
                +{paper.key_components.length - 5} more
              </span>
            )}
          </div>
        </div>
      )}

      {expanded && paper.architecture && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>
            Architecture
          </div>
          <p style={{ fontSize: '14px', color: '#4b5563', lineHeight: 1.6, margin: 0, backgroundColor: '#f9fafb', padding: '12px', borderRadius: '8px' }}>
            {paper.architecture}
          </p>
        </div>
      )}

      {expanded && paper.novelty_description && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>
            Novelty Description
          </div>
          <p style={{ fontSize: '14px', color: '#4b5563', lineHeight: 1.6, margin: 0 }}>
            {paper.novelty_description}
          </p>
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

function DistributionChart({ distribution }: { distribution: Record<string, number> }) {
  // Get top 8 types by count
  const sorted = Object.entries(distribution)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8);

  const maxCount = Math.max(...sorted.map(([, count]) => count));

  return (
    <div style={{ marginBottom: '24px' }}>
      <div style={{ fontSize: '14px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
        Novelty Type Distribution
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {sorted.map(([type, count]) => (
          <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '120px', fontSize: '12px', color: '#6b7280', textTransform: 'capitalize', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {type}
            </div>
            <div style={{ flex: 1, height: '20px', backgroundColor: '#f3f4f6', borderRadius: '4px', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${(count / maxCount) * 100}%`,
                  height: '100%',
                  backgroundColor: '#3b82f6',
                  borderRadius: '4px',
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
            <div style={{ width: '60px', fontSize: '12px', color: '#374151', textAlign: 'right' }}>
              {count.toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function TechniquesDashboard() {
  const [papers, setPapers] = useState<TechniquePaper[]>([]);
  const [total, setTotal] = useState(0);
  const [distribution, setDistribution] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [noveltyType, setNoveltyType] = useState('all');
  const [category, setCategory] = useState('all');

  const fetchTechniques = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ limit: '20' });
      if (noveltyType !== 'all') params.set('novelty_type', noveltyType);
      if (category !== 'all') params.set('category', category);

      const response = await fetch(`/api/discovery/techniques?${params.toString()}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data: TechniquesResponse = await response.json();
      setPapers(data.papers || []);
      setTotal(data.total || 0);
      setDistribution(data.novelty_type_distribution || {});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load techniques');
    } finally {
      setLoading(false);
    }
  }, [noveltyType, category]);

  useEffect(() => {
    fetchTechniques();
  }, [fetchTechniques]);

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
            Techniques & Methods
          </h1>
          <p style={{ fontSize: '16px', color: '#6b7280', margin: 0 }}>
            Explore novel methodologies, architectures, and algorithmic innovations from research papers
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
              Novelty Type
            </label>
            <select
              value={noveltyType}
              onChange={(e) => setNoveltyType(e.target.value)}
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
              {NOVELTY_TYPES.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
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
              <strong style={{ color: '#111827' }}>{total.toLocaleString()}</strong> papers with techniques
            </span>
          </div>
        </div>

        {/* Distribution Chart */}
        {!loading && Object.keys(distribution).length > 0 && (
          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            border: '1px solid #e5e7eb',
            padding: '20px',
            marginBottom: '24px',
          }}>
            <DistributionChart distribution={distribution} />
          </div>
        )}

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
            Loading techniques...
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
          <TechniqueCard key={paper.id} paper={paper} />
        ))}
      </div>
    </div>
  );
}
