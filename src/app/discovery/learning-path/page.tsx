'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface LearningPaper {
  id: string;
  title: string;
  difficulty_level: string | null;
  prerequisites: string[] | null;
  reading_time_minutes: number | null;
  key_sections: string[] | null;
  summary: string | null;
}

interface LearningLevel {
  level: string;
  description: string;
  papers: LearningPaper[];
}

interface LearningPathResponse {
  topic: string | null;
  category: string | null;
  path: LearningLevel[];
}

function DifficultyBadge({ level }: { level: string | null }) {
  if (!level) return null;

  const getColor = (l: string) => {
    const lower = l.toLowerCase();
    if (lower === 'beginner' || lower === 'introductory') return { bg: '#dcfce7', text: '#166534', border: '#86efac' };
    if (lower === 'intermediate') return { bg: '#fef3c7', text: '#92400e', border: '#fcd34d' };
    if (lower === 'advanced' || lower === 'expert') return { bg: '#fee2e2', text: '#991b1b', border: '#fca5a5' };
    return { bg: '#f3f4f6', text: '#6b7280', border: '#d1d5db' };
  };

  const colors = getColor(level);

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 10px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 600,
        backgroundColor: colors.bg,
        color: colors.text,
        border: `1px solid ${colors.border}`,
        textTransform: 'capitalize',
      }}
    >
      {level}
    </span>
  );
}

function ReadingTimeBadge({ minutes }: { minutes: number | null }) {
  if (minutes === null) return null;

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
        backgroundColor: '#e0e7ff',
        color: '#3730a3',
        border: '1px solid #a5b4fc',
      }}
    >
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 6v6l4 2" />
      </svg>
      {minutes} min read
    </span>
  );
}

function LearningPaperCard({ paper }: { paper: LearningPaper }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: '10px',
        padding: '16px',
        marginBottom: '12px',
        backgroundColor: '#ffffff',
        transition: 'box-shadow 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
        <Link
          href={`/paper/${paper.id}`}
          style={{
            fontSize: '15px',
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
        <div style={{ display: 'flex', gap: '6px', flexShrink: 0 }}>
          <DifficultyBadge level={paper.difficulty_level} />
          <ReadingTimeBadge minutes={paper.reading_time_minutes} />
        </div>
      </div>

      {paper.summary && (
        <p style={{ fontSize: '13px', color: '#4b5563', lineHeight: 1.6, margin: '0 0 12px 0' }}>
          {expanded ? paper.summary : paper.summary.slice(0, 200) + (paper.summary.length > 200 ? '...' : '')}
        </p>
      )}

      {paper.prerequisites && paper.prerequisites.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#6b7280', marginBottom: '6px', textTransform: 'uppercase' }}>
            Prerequisites
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {paper.prerequisites.slice(0, expanded ? undefined : 3).map((prereq, idx) => (
              <span
                key={idx}
                style={{
                  display: 'inline-block',
                  padding: '3px 8px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  backgroundColor: '#f3f4f6',
                  color: '#4b5563',
                  border: '1px solid #e5e7eb',
                }}
              >
                {prereq}
              </span>
            ))}
            {!expanded && paper.prerequisites.length > 3 && (
              <span style={{ fontSize: '11px', color: '#6b7280', padding: '3px' }}>
                +{paper.prerequisites.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {expanded && paper.key_sections && paper.key_sections.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#6b7280', marginBottom: '6px', textTransform: 'uppercase' }}>
            Key Sections to Read
          </div>
          <ul style={{ margin: 0, paddingLeft: '18px' }}>
            {paper.key_sections.map((section, idx) => (
              <li
                key={idx}
                style={{
                  fontSize: '12px',
                  color: '#4b5563',
                  lineHeight: 1.5,
                  marginBottom: '2px',
                }}
              >
                {section}
              </li>
            ))}
          </ul>
        </div>
      )}

      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          padding: '4px 10px',
          borderRadius: '4px',
          border: '1px solid #e5e7eb',
          backgroundColor: '#ffffff',
          color: '#6b7280',
          fontSize: '11px',
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
        {expanded ? 'Less' : 'More'}
      </button>
    </div>
  );
}

function LevelSection({ level }: { level: LearningLevel }) {
  const getLevelStyle = (lvl: string) => {
    const lower = lvl.toLowerCase();
    if (lower === 'beginner' || lower === 'introductory') {
      return { borderColor: '#86efac', iconBg: '#dcfce7', iconColor: '#166534' };
    }
    if (lower === 'intermediate') {
      return { borderColor: '#fcd34d', iconBg: '#fef3c7', iconColor: '#92400e' };
    }
    if (lower === 'advanced' || lower === 'expert') {
      return { borderColor: '#fca5a5', iconBg: '#fee2e2', iconColor: '#991b1b' };
    }
    return { borderColor: '#d1d5db', iconBg: '#f3f4f6', iconColor: '#6b7280' };
  };

  const style = getLevelStyle(level.level);

  return (
    <div
      style={{
        marginBottom: '32px',
        borderLeft: `4px solid ${style.borderColor}`,
        paddingLeft: '20px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <div
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            backgroundColor: style.iconBg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={style.iconColor} strokeWidth="2">
            <path d="M12 14l9-5-9-5-9 5 9 5z" />
            <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
          </svg>
        </div>
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#111827', textTransform: 'capitalize' }}>
            {level.level}
          </h3>
          <p style={{ margin: 0, fontSize: '13px', color: '#6b7280' }}>
            {level.description}
          </p>
        </div>
        <span style={{ marginLeft: 'auto', fontSize: '13px', color: '#9ca3af' }}>
          {level.papers.length} papers
        </span>
      </div>

      {level.papers.map(paper => (
        <LearningPaperCard key={paper.id} paper={paper} />
      ))}
    </div>
  );
}

export default function LearningPathDashboard() {
  const [pathData, setPathData] = useState<LearningLevel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [topic, setTopic] = useState('');
  const [category, setCategory] = useState('all');
  const [difficultyLevel, setDifficultyLevel] = useState('all');

  const fetchLearningPath = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ limit: '30' });
      if (topic) params.set('topic', topic);
      if (category !== 'all') params.set('category', category);
      if (difficultyLevel !== 'all') params.set('difficulty_level', difficultyLevel);

      const response = await fetch(`/api/discovery/learning-path?${params.toString()}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data: LearningPathResponse = await response.json();
      setPathData(data.path || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load learning path');
    } finally {
      setLoading(false);
    }
  }, [topic, category, difficultyLevel]);

  useEffect(() => {
    fetchLearningPath();
  }, [fetchLearningPath]);

  const totalPapers = pathData.reduce((sum, level) => sum + level.papers.length, 0);

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
            Learning Paths
          </h1>
          <p style={{ fontSize: '16px', color: '#6b7280', margin: 0 }}>
            Structured reading paths organized by difficulty level with prerequisites and estimated reading times
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
              Topic (optional)
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., transformers, reinforcement learning"
              style={{
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                backgroundColor: '#ffffff',
                fontSize: '14px',
                color: '#374151',
                minWidth: '250px',
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '4px' }}>
              Difficulty
            </label>
            <select
              value={difficultyLevel}
              onChange={(e) => setDifficultyLevel(e.target.value)}
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
              <option value="all">All Levels</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
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
              <strong style={{ color: '#111827' }}>{totalPapers}</strong> papers in {pathData.length} levels
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
            Building your learning path...
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

        {/* Learning Path */}
        {!loading && !error && pathData.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px', color: '#6b7280' }}>
            No learning path found with the selected filters
          </div>
        )}

        {!loading && !error && pathData.map((level, idx) => (
          <LevelSection key={idx} level={level} />
        ))}
      </div>
    </div>
  );
}
