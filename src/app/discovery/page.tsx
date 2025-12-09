'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import './discovery.css';

// Types
interface DiscoveryStats {
  coverage: {
    total_papers: number;
    ai_analyzed: number;
    ai_coverage_pct: number;
    deep_analyzed: number;
    deep_coverage_pct: number;
    with_code: number;
  };
  distributions: {
    impact_scores: Record<string, number>;
    difficulty_levels: Record<string, number>;
    novelty_types: Record<string, number>;
  };
}

interface DiscoveryPaper {
  id: string;
  title: string;
  published: string;
  category: string;
  impact_score?: number;
  impact_rationale?: string;
  executive_summary?: string;
  difficulty_level?: string;
  novelty_type?: string;
  reproducibility_score?: number;
  methodology?: string[];
  use_cases?: string[];
  industry_relevance?: string;
}

interface ImpactResponse {
  papers: DiscoveryPaper[];
  total: number;
  score_distribution: Record<string, number>;
}

interface TldrResponse {
  papers: DiscoveryPaper[];
  total: number;
}

interface LearningPathResponse {
  beginner: DiscoveryPaper[];
  intermediate: DiscoveryPaper[];
  advanced: DiscoveryPaper[];
  expert: DiscoveryPaper[];
  suggested_path: string[];
  total_by_level: Record<string, number>;
}

// Animated number counter
const AnimatedNumber = ({ value, duration = 1200 }: { value: number; duration?: number }) => {
  const [displayValue, setDisplayValue] = useState(0);
  const startTime = useRef<number | null>(null);
  const animationFrame = useRef<number>();

  useEffect(() => {
    const animate = (timestamp: number) => {
      if (!startTime.current) startTime.current = timestamp;
      const progress = Math.min((timestamp - startTime.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // Cubic ease-out
      setDisplayValue(Math.floor(eased * value));

      if (progress < 1) {
        animationFrame.current = requestAnimationFrame(animate);
      }
    };

    animationFrame.current = requestAnimationFrame(animate);
    return () => {
      if (animationFrame.current) cancelAnimationFrame(animationFrame.current);
    };
  }, [value, duration]);

  return <span>{displayValue.toLocaleString()}</span>;
};

// Impact meter visualization
const ImpactMeter = ({ score, size = 'md' }: { score: number; size?: 'sm' | 'md' | 'lg' }) => {
  const sizes = { sm: 32, md: 48, lg: 64 };
  const dim = sizes[size];
  const strokeWidth = size === 'sm' ? 3 : 4;
  const radius = (dim - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 10) * circumference;

  const getColor = (s: number) => {
    if (s >= 9) return '#f59e0b'; // Gold
    if (s >= 7) return '#c87533'; // Copper
    if (s >= 5) return '#6b7280'; // Gray
    return '#374151';
  };

  return (
    <div className="impact-meter" style={{ width: dim, height: dim }}>
      <svg viewBox={`0 0 ${dim} ${dim}`}>
        <circle
          cx={dim / 2}
          cy={dim / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={dim / 2}
          cy={dim / 2}
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

// Difficulty badge
const DifficultyBadge = ({ level }: { level: string }) => {
  const colors: Record<string, string> = {
    beginner: '#10b981',
    intermediate: '#f59e0b',
    advanced: '#ef4444',
    expert: '#8b5cf6',
  };
  return (
    <span
      className="difficulty-badge"
      style={{ '--badge-color': colors[level] || '#6b7280' } as React.CSSProperties}
    >
      {level}
    </span>
  );
};

// Paper card for discovery
const DiscoveryCard = ({ paper, showImpact = true }: { paper: DiscoveryPaper; showImpact?: boolean }) => {
  const plainId = paper.id.split('v')[0];

  return (
    <article className="discovery-card">
      <header className="discovery-card__header">
        {showImpact && paper.impact_score && (
          <ImpactMeter score={paper.impact_score} size="sm" />
        )}
        <div className="discovery-card__meta">
          <span className="discovery-card__category">{paper.category}</span>
          {paper.difficulty_level && (
            <DifficultyBadge level={paper.difficulty_level} />
          )}
        </div>
      </header>

      <h3 className="discovery-card__title">
        <Link href={`https://arxiv.org/abs/${plainId}`} target="_blank" rel="noopener">
          {paper.title}
        </Link>
      </h3>

      {paper.executive_summary && (
        <p className="discovery-card__summary">{paper.executive_summary}</p>
      )}

      {paper.impact_rationale && (
        <p className="discovery-card__rationale">
          <strong>Why it matters:</strong> {paper.impact_rationale}
        </p>
      )}

      <footer className="discovery-card__footer">
        <time className="discovery-card__date">
          {new Date(paper.published).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          })}
        </time>
        {paper.novelty_type && (
          <span className="discovery-card__novelty">{paper.novelty_type}</span>
        )}
      </footer>
    </article>
  );
};

// Main Discovery Page
export default function DiscoveryPage() {
  const [stats, setStats] = useState<DiscoveryStats | null>(null);
  const [impactPapers, setImpactPapers] = useState<DiscoveryPaper[]>([]);
  const [tldrPapers, setTldrPapers] = useState<DiscoveryPaper[]>([]);
  const [learningPath, setLearningPath] = useState<LearningPathResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'impact' | 'tldr' | 'learning'>('impact');
  const [loading, setLoading] = useState(true);
  const [minImpact, setMinImpact] = useState(7);

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [statsRes, impactRes, tldrRes, learningRes] = await Promise.all([
          fetch(`${API_BASE}/api/v1/discovery/stats`),
          fetch(`${API_BASE}/api/v1/discovery/impact?min_score=${minImpact}&limit=12`),
          fetch(`${API_BASE}/api/v1/discovery/tldr?limit=8`),
          fetch(`${API_BASE}/api/v1/discovery/learning-path?papers_per_level=4`),
        ]);

        if (statsRes.ok) {
          const data = await statsRes.json();
          setStats(data);
        }
        if (impactRes.ok) {
          const data: ImpactResponse = await impactRes.json();
          setImpactPapers(data.papers);
        }
        if (tldrRes.ok) {
          const data: TldrResponse = await tldrRes.json();
          setTldrPapers(data.papers);
        }
        if (learningRes.ok) {
          const data: LearningPathResponse = await learningRes.json();
          setLearningPath(data);
        }
      } catch (err) {
        console.error('Failed to fetch discovery data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, [API_BASE, minImpact]);

  // Calculate impact distribution for visualization
  const impactDistribution = stats?.distributions.impact_scores || {};
  const maxImpactCount = Math.max(...Object.values(impactDistribution), 1);

  return (
    <div className="discovery-page">
      {/* Animated background */}
      <div className="discovery-bg">
        <div className="discovery-bg__grid" />
        <div className="discovery-bg__glow" />
      </div>

      <main className="discovery-main">
        {/* Hero section */}
        <header className="discovery-hero">
          <div className="discovery-hero__badge">
            <span className="pulse" />
            Research Command Center
          </div>
          <h1>Discover What Matters</h1>
          <p className="discovery-hero__subtitle">
            Navigate 27,000+ papers through the lens of impact, reproducibility, and practical application.
            Updated continuously as new research lands.
          </p>
        </header>

        {/* Stats overview */}
        {stats && (
          <section className="discovery-stats" aria-label="Coverage statistics">
            <div className="stat-card stat-card--primary">
              <div className="stat-card__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                </svg>
              </div>
              <div className="stat-card__content">
                <span className="stat-card__value">
                  <AnimatedNumber value={stats.coverage.total_papers} />
                </span>
                <span className="stat-card__label">Total Papers</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card__ring">
                <svg viewBox="0 0 36 36">
                  <circle cx="18" cy="18" r="16" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
                  <circle
                    cx="18" cy="18" r="16" fill="none"
                    stroke="#c87533" strokeWidth="2"
                    strokeDasharray={`${stats.coverage.deep_coverage_pct} 100`}
                    strokeLinecap="round"
                    style={{ transform: 'rotate(-90deg)', transformOrigin: 'center' }}
                  />
                </svg>
                <span className="stat-card__ring-value">{Math.round(stats.coverage.deep_coverage_pct)}%</span>
              </div>
              <div className="stat-card__content">
                <span className="stat-card__value">
                  <AnimatedNumber value={stats.coverage.deep_analyzed} />
                </span>
                <span className="stat-card__label">Deep Analyzed</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card__icon stat-card__icon--code">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
                </svg>
              </div>
              <div className="stat-card__content">
                <span className="stat-card__value">
                  <AnimatedNumber value={stats.coverage.with_code} />
                </span>
                <span className="stat-card__label">With Code</span>
              </div>
            </div>
          </section>
        )}

        {/* Impact distribution visualization */}
        {stats && (
          <section className="impact-viz" aria-label="Impact score distribution">
            <h2 className="section-heading">Impact Distribution</h2>
            <p className="section-desc">
              Papers scored by potential influence on the field. Calibrated against breakthrough work like
              Attention Is All You Need (10) and BERT (9).
            </p>
            <div className="impact-bars">
              {[4, 5, 6, 7, 8, 9, 10].map((score) => {
                const count = impactDistribution[score.toString()] || 0;
                const height = (count / maxImpactCount) * 100;
                const isHighImpact = score >= 8;
                return (
                  <button
                    key={score}
                    className={`impact-bar ${isHighImpact ? 'impact-bar--high' : ''} ${minImpact === score ? 'impact-bar--active' : ''}`}
                    onClick={() => setMinImpact(score)}
                    title={`${count.toLocaleString()} papers with impact score ${score}`}
                  >
                    <div className="impact-bar__fill" style={{ height: `${Math.max(height, 4)}%` }} />
                    <span className="impact-bar__score">{score}</span>
                    <span className="impact-bar__count">{count.toLocaleString()}</span>
                  </button>
                );
              })}
            </div>
            <p className="impact-viz__hint">Click a bar to filter papers by minimum impact score</p>
          </section>
        )}

        {/* Tab navigation */}
        <nav className="discovery-tabs" role="tablist">
          <button
            role="tab"
            aria-selected={activeTab === 'impact'}
            className={`discovery-tab ${activeTab === 'impact' ? 'discovery-tab--active' : ''}`}
            onClick={() => setActiveTab('impact')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
            High Impact
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'tldr'}
            className={`discovery-tab ${activeTab === 'tldr' ? 'discovery-tab--active' : ''}`}
            onClick={() => setActiveTab('tldr')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" />
            </svg>
            TL;DR Feed
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'learning'}
            className={`discovery-tab ${activeTab === 'learning' ? 'discovery-tab--active' : ''}`}
            onClick={() => setActiveTab('learning')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
            </svg>
            Learning Paths
          </button>
        </nav>

        {/* Tab content */}
        <div className="discovery-content">
          {loading ? (
            <div className="discovery-loading">
              <div className="discovery-loading__spinner" />
              <span>Scanning the research landscape...</span>
            </div>
          ) : (
            <>
              {/* Impact tab */}
              {activeTab === 'impact' && (
                <section className="tab-panel" aria-label="High impact papers">
                  <header className="tab-panel__header">
                    <h2>Papers with Impact Score {minImpact}+</h2>
                    <span className="tab-panel__count">{impactPapers.length} papers</span>
                  </header>
                  <div className="discovery-grid">
                    {impactPapers.map((paper) => (
                      <DiscoveryCard key={paper.id} paper={paper} />
                    ))}
                  </div>
                </section>
              )}

              {/* TL;DR tab */}
              {activeTab === 'tldr' && (
                <section className="tab-panel" aria-label="Executive summaries">
                  <header className="tab-panel__header">
                    <h2>Executive Summaries</h2>
                    <span className="tab-panel__count">Latest papers, distilled</span>
                  </header>
                  <div className="tldr-list">
                    {tldrPapers.map((paper) => (
                      <article key={paper.id} className="tldr-card">
                        <div className="tldr-card__header">
                          <span className="tldr-card__category">{paper.category}</span>
                          <time className="tldr-card__date">
                            {new Date(paper.published).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric'
                            })}
                          </time>
                        </div>
                        <h3 className="tldr-card__title">
                          <Link href={`https://arxiv.org/abs/${paper.id.split('v')[0]}`} target="_blank">
                            {paper.title}
                          </Link>
                        </h3>
                        {paper.executive_summary && (
                          <p className="tldr-card__summary">{paper.executive_summary}</p>
                        )}
                      </article>
                    ))}
                  </div>
                </section>
              )}

              {/* Learning paths tab */}
              {activeTab === 'learning' && learningPath && (
                <section className="tab-panel" aria-label="Learning paths">
                  <header className="tab-panel__header">
                    <h2>Structured Learning Paths</h2>
                    <span className="tab-panel__count">Papers organized by difficulty</span>
                  </header>

                  <div className="learning-ladder">
                    {(['beginner', 'intermediate', 'advanced', 'expert'] as const).map((level, idx) => {
                      const papers = learningPath[level] || [];
                      const total = learningPath.total_by_level[level] || 0;
                      if (papers.length === 0) return null;

                      return (
                        <div key={level} className="learning-rung" style={{ '--delay': `${idx * 100}ms` } as React.CSSProperties}>
                          <div className="learning-rung__header">
                            <DifficultyBadge level={level} />
                            <span className="learning-rung__count">{total.toLocaleString()} papers</span>
                          </div>
                          <div className="learning-rung__papers">
                            {papers.map((paper) => (
                              <article key={paper.id} className="learning-paper">
                                <h4>
                                  <Link href={`https://arxiv.org/abs/${paper.id.split('v')[0]}`} target="_blank">
                                    {paper.title}
                                  </Link>
                                </h4>
                                <span className="learning-paper__category">{paper.category}</span>
                              </article>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
