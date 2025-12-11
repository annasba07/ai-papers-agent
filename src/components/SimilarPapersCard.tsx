"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

interface SimilarPaper {
  id: string;
  title: string;
  authors: string[];
  published: string;
  category?: string;
  similarity_score: number;
}

interface SimilarPapersCardProps {
  paperId: string;
  apiBaseUrl?: string;
  onPaperClick?: (paperId: string) => void;
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
};

const SimilarPapersCard: React.FC<SimilarPapersCardProps> = ({
  paperId,
  apiBaseUrl = 'http://localhost:8000/api/v1',
  onPaperClick,
}) => {
  const [papers, setPapers] = useState<SimilarPaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const fetchSimilarPapers = async () => {
      setLoading(true);
      setError(null);

      try {
        const res = await fetch(`${apiBaseUrl}/papers/similar/${paperId}?top_k=8`);
        if (res.ok) {
          const data = await res.json();
          setPapers(data.similar_papers || []);
        } else if (res.status === 503) {
          setError('Similar papers unavailable');
        } else if (res.status === 404) {
          setError('Paper not in atlas');
        } else {
          setError('Failed to load');
        }
      } catch (err) {
        console.error('Error fetching similar papers:', err);
        setError('Connection error');
      } finally {
        setLoading(false);
      }
    };

    if (paperId) {
      fetchSimilarPapers();
    }
  }, [paperId, apiBaseUrl]);

  // Don't render if no data and not loading
  if (!loading && papers.length === 0 && !error) {
    return null;
  }

  const displayedPapers = expanded ? papers : papers.slice(0, 4);

  return (
    <div className="similar-papers-card">
      <h3
        className="similar-papers-header"
        onClick={() => papers.length > 0 && setExpanded(!expanded)}
        style={{ cursor: papers.length > 4 ? 'pointer' : 'default' }}
      >
        <span style={{ marginRight: '8px' }}>🔗</span>
        Similar Papers
        {papers.length > 4 && (
          <span className="expand-toggle">
            {expanded ? '▼' : `+${papers.length - 4} more`}
          </span>
        )}
      </h3>

      {loading ? (
        <div className="similar-loading">
          <div className="loading-dot" />
          <div className="loading-dot" />
          <div className="loading-dot" />
        </div>
      ) : error ? (
        <div className="similar-error">{error}</div>
      ) : (
        <div className="similar-list">
          {displayedPapers.map((paper, idx) => (
            <div key={paper.id} className="similar-item" style={{ animationDelay: `${idx * 0.05}s` }}>
              <div className="similar-item__score">
                <span className="score-value">{Math.round(paper.similarity_score * 100)}%</span>
              </div>
              <div className="similar-item__content">
                {onPaperClick ? (
                  <button
                    className="similar-item__title"
                    onClick={() => onPaperClick(paper.id)}
                  >
                    {paper.title}
                  </button>
                ) : (
                  <Link
                    href={`https://arxiv.org/abs/${paper.id.split('v')[0]}`}
                    target="_blank"
                    className="similar-item__title"
                  >
                    {paper.title}
                  </Link>
                )}
                <div className="similar-item__meta">
                  <span className="similar-item__authors">
                    {paper.authors.slice(0, 2).join(', ')}
                    {paper.authors.length > 2 && ' et al.'}
                  </span>
                  <span className="similar-item__date">{formatDate(paper.published)}</span>
                  {paper.category && (
                    <span className="similar-item__category">{paper.category}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        .similar-papers-card {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.03) 0%, rgba(6, 182, 212, 0.03) 100%);
          border: 1px solid rgba(16, 185, 129, 0.12);
          border-radius: 16px;
          padding: 20px;
          margin: 24px 0;
        }

        .similar-papers-header {
          font-size: 1rem;
          font-weight: 600;
          color: var(--primary-text, #0f172a);
          margin-bottom: 16px;
          display: flex;
          align-items: center;
        }

        .expand-toggle {
          margin-left: auto;
          font-size: 0.8rem;
          font-weight: 500;
          color: var(--accent-emerald, #10b981);
          padding: 4px 10px;
          background: rgba(16, 185, 129, 0.1);
          border-radius: 12px;
        }

        .similar-loading {
          display: flex;
          gap: 6px;
          padding: 20px;
          justify-content: center;
        }

        .loading-dot {
          width: 8px;
          height: 8px;
          background: var(--accent-emerald, #10b981);
          border-radius: 50%;
          animation: bounce 1.4s infinite ease-in-out both;
        }

        .loading-dot:nth-child(1) { animation-delay: -0.32s; }
        .loading-dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }

        .similar-error {
          color: #64748b;
          font-size: 0.9rem;
          text-align: center;
          padding: 16px;
        }

        .similar-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .similar-item {
          display: flex;
          gap: 12px;
          padding: 12px;
          background: white;
          border-radius: 10px;
          border: 1px solid rgba(148, 163, 184, 0.15);
          animation: fadeIn 0.3s ease-out both;
          transition: border-color 0.2s, box-shadow 0.2s;
        }

        .similar-item:hover {
          border-color: rgba(16, 185, 129, 0.3);
          box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1);
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .similar-item__score {
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 48px;
          padding: 4px 8px;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
          border-radius: 8px;
        }

        .score-value {
          font-family: var(--font-tech, 'JetBrains Mono', monospace);
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--accent-emerald, #10b981);
        }

        .similar-item__content {
          flex: 1;
          min-width: 0;
        }

        .similar-item__title {
          display: block;
          font-size: 0.9rem;
          font-weight: 500;
          color: var(--primary-text, #0f172a);
          text-decoration: none;
          line-height: 1.4;
          margin-bottom: 6px;
          background: none;
          border: none;
          padding: 0;
          text-align: left;
          cursor: pointer;
        }

        .similar-item__title:hover {
          color: var(--accent-emerald, #10b981);
        }

        .similar-item__meta {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          font-size: 0.75rem;
          color: var(--secondary-text, #64748b);
        }

        .similar-item__authors {
          max-width: 200px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .similar-item__date {
          color: #94a3b8;
        }

        .similar-item__category {
          padding: 1px 6px;
          background: rgba(99, 102, 241, 0.1);
          color: var(--accent-indigo, #6366f1);
          border-radius: 4px;
          font-size: 0.7rem;
        }
      `}</style>
    </div>
  );
};

export default SimilarPapersCard;
