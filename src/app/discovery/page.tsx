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

interface LearningPathLevel {
  level: string;
  description: string;
  papers: {
    id: string;
    title: string;
    difficulty_level: string;
    prerequisites: string[];
    reading_time_minutes: number;
    key_sections: string[];
    summary?: string;
  }[];
}

interface LearningPathResponse {
  topic: string | null;
  category: string | null;
  path: LearningPathLevel[];
}

interface TechniquePaper {
  id: string;
  title: string;
  novelty_type: string | null;
  novelty_description: string | null;
  methodology_approach: string | null;
  key_components: string[];
  architecture: string | null;
}

interface TechniqueResponse {
  papers: TechniquePaper[];
  total: number;
  novelty_type_distribution?: Record<string, number>;
}

interface ReproduciblePaper {
  id: string;
  title: string;
  reproducibility_score: number;
  code_availability: string | null;
  implementation_detail: string | null;
  github_urls: string[];
  datasets_mentioned: string[];
  has_code: boolean;
}

interface PracticalPaper {
  id: string;
  title: string;
  category: string;
  industry_relevance: string;
  impact_score: number;
  use_cases: string[];
  scalability: string | null;
  deployment_considerations: string | null;
  limitations: string[];
  ai_practical_score: string | null;
}

// Animated number counter
const AnimatedNumber = ({ value, duration = 1200 }: { value: number; duration?: number }) => {
  const [displayValue, setDisplayValue] = useState(0);
  const startTime = useRef<number | null>(null);
  const animationFrame = useRef<number | undefined>(undefined);

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
  const [techniques, setTechniques] = useState<TechniquePaper[]>([]);
  const [techniqueDistribution, setTechniqueDistribution] = useState<Record<string, number>>({});
  const [reproducible, setReproducible] = useState<ReproduciblePaper[]>([]);
  const [practical, setPractical] = useState<PracticalPaper[]>([]);
  const [activeTab, setActiveTab] = useState<'impact' | 'tldr' | 'learning' | 'techniques' | 'reproducibility' | 'practical'>('impact');
  const [loading, setLoading] = useState(true);
  const [minImpact, setMinImpact] = useState(7);
  const [selectedNoveltyType, setSelectedNoveltyType] = useState<string | null>(null);
  const [minReproducibility, setMinReproducibility] = useState(7);
  const [industryRelevance, setIndustryRelevance] = useState<'high' | 'medium' | 'low'>('high');

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const techniqueUrl = selectedNoveltyType
          ? `${API_BASE}/discovery/techniques?novelty_type=${selectedNoveltyType}&limit=12`
          : `${API_BASE}/discovery/techniques?limit=12`;

        const [statsRes, impactRes, tldrRes, learningRes, techniquesRes, reproducibleRes, practicalRes] = await Promise.all([
          fetch(`${API_BASE}/discovery/stats`),
          fetch(`${API_BASE}/discovery/impact?min_score=${minImpact}&limit=12`),
          fetch(`${API_BASE}/discovery/tldr?limit=8`),
          fetch(`${API_BASE}/discovery/learning-path?limit_per_level=4`),
          fetch(techniqueUrl),
          fetch(`${API_BASE}/discovery/reproducible?min_reproducibility=${minReproducibility}&limit=12`),
          fetch(`${API_BASE}/discovery/practical?industry_relevance=${industryRelevance}&limit=12`),
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
        if (techniquesRes.ok) {
          const data: TechniqueResponse = await techniquesRes.json();
          setTechniques(data.papers);
          setTechniqueDistribution(data.novelty_type_distribution || {});
        }
        if (reproducibleRes.ok) {
          const data = await reproducibleRes.json();
          setReproducible(data.papers);
        }
        if (practicalRes.ok) {
          const data = await practicalRes.json();
          setPractical(data.papers);
        }
      } catch (err) {
        console.error('Failed to fetch discovery data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, [API_BASE, minImpact, selectedNoveltyType, minReproducibility, industryRelevance]);

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
          <button
            role="tab"
            aria-selected={activeTab === 'techniques'}
            className={`discovery-tab ${activeTab === 'techniques' ? 'discovery-tab--active' : ''}`}
            onClick={() => setActiveTab('techniques')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
              <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Techniques
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'reproducibility'}
            className={`discovery-tab ${activeTab === 'reproducibility' ? 'discovery-tab--active' : ''}`}
            onClick={() => setActiveTab('reproducibility')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" />
            </svg>
            Reproducibility
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'practical'}
            className={`discovery-tab ${activeTab === 'practical' ? 'discovery-tab--active' : ''}`}
            onClick={() => setActiveTab('practical')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z" />
            </svg>
            Practical
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
                    {learningPath.path.map((levelData, idx) => {
                      if (levelData.papers.length === 0) return null;

                      return (
                        <div key={levelData.level} className="learning-rung" style={{ '--delay': `${idx * 100}ms` } as React.CSSProperties}>
                          <div className="learning-rung__header">
                            <DifficultyBadge level={levelData.level} />
                            <span className="learning-rung__count">{levelData.description}</span>
                          </div>
                          <div className="learning-rung__papers">
                            {levelData.papers.map((paper) => (
                              <article key={paper.id} className="learning-paper">
                                <h4>
                                  <Link href={`https://arxiv.org/abs/${paper.id.split('v')[0]}`} target="_blank">
                                    {paper.title}
                                  </Link>
                                </h4>
                                {paper.reading_time_minutes && (
                                  <span className="learning-paper__time">{paper.reading_time_minutes} min read</span>
                                )}
                              </article>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>
              )}

              {/* Techniques tab */}
              {activeTab === 'techniques' && (
                <section className="tab-panel" aria-label="Technique explorer">
                  <header className="tab-panel__header">
                    <h2>Technique Explorer</h2>
                    <span className="tab-panel__count">Papers by methodology type</span>
                  </header>

                  {/* Novelty type filter chips */}
                  <div className="technique-filters">
                    <button
                      className={`technique-chip ${!selectedNoveltyType ? 'technique-chip--active' : ''}`}
                      onClick={() => setSelectedNoveltyType(null)}
                    >
                      All Types
                    </button>
                    {Object.entries(techniqueDistribution)
                      .sort((a, b) => b[1] - a[1])
                      .slice(0, 6)
                      .map(([type, count]) => (
                        <button
                          key={type}
                          className={`technique-chip ${selectedNoveltyType === type ? 'technique-chip--active' : ''}`}
                          onClick={() => setSelectedNoveltyType(type)}
                        >
                          {type} <span className="technique-chip__count">{count}</span>
                        </button>
                      ))}
                  </div>

                  <div className="technique-grid">
                    {techniques.map((paper) => (
                      <article key={paper.id} className="technique-card">
                        <header className="technique-card__header">
                          {paper.novelty_type && (
                            <span className="technique-card__type">{paper.novelty_type}</span>
                          )}
                        </header>

                        <h3 className="technique-card__title">
                          <Link href={`https://arxiv.org/abs/${paper.id.split('v')[0]}`} target="_blank">
                            {paper.title}
                          </Link>
                        </h3>

                        {paper.methodology_approach && (
                          <p className="technique-card__methodology">
                            {paper.methodology_approach.slice(0, 200)}
                            {paper.methodology_approach.length > 200 ? '...' : ''}
                          </p>
                        )}

                        {paper.key_components && paper.key_components.length > 0 && (
                          <div className="technique-card__components">
                            <span className="technique-card__label">Key Components:</span>
                            <ul>
                              {paper.key_components.slice(0, 3).map((comp, i) => (
                                <li key={i}>{comp}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </article>
                    ))}
                  </div>
                </section>
              )}

              {/* Reproducibility tab */}
              {activeTab === 'reproducibility' && (
                <section className="tab-panel" aria-label="Reproducibility index">
                  <header className="tab-panel__header">
                    <h2>Reproducibility Index</h2>
                    <span className="tab-panel__count">Papers with code and data availability</span>
                  </header>

                  {/* Reproducibility score filter */}
                  <div className="repro-filter">
                    <span className="repro-filter__label">Minimum Score:</span>
                    <div className="repro-filter__buttons">
                      {[5, 6, 7, 8, 9].map((score) => (
                        <button
                          key={score}
                          className={`repro-score-btn ${minReproducibility === score ? 'repro-score-btn--active' : ''}`}
                          onClick={() => setMinReproducibility(score)}
                        >
                          {score}+
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="repro-grid">
                    {reproducible.map((paper) => (
                      <article key={paper.id} className="repro-card">
                        <header className="repro-card__header">
                          <div className="repro-card__score">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>{paper.reproducibility_score}/10</span>
                          </div>
                          <div className="repro-card__badges">
                            {paper.has_code && (
                              <span className="repro-badge repro-badge--code">Code</span>
                            )}
                            {paper.code_availability === 'yes' && (
                              <span className="repro-badge repro-badge--available">Available</span>
                            )}
                            {paper.implementation_detail === 'high' && (
                              <span className="repro-badge repro-badge--detailed">Detailed</span>
                            )}
                          </div>
                        </header>

                        <h3 className="repro-card__title">
                          <Link href={`https://arxiv.org/abs/${paper.id.split('v')[0]}`} target="_blank">
                            {paper.title}
                          </Link>
                        </h3>

                        {paper.github_urls && paper.github_urls.length > 0 && (
                          <div className="repro-card__links">
                            <span className="repro-card__label">Repositories:</span>
                            <div className="repro-card__repos">
                              {paper.github_urls.slice(0, 2).map((url, i) => (
                                <a
                                  key={i}
                                  href={url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="repro-card__repo"
                                >
                                  <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                                  </svg>
                                  {url.includes('github.com') ? url.split('github.com/')[1]?.split('/').slice(0, 2).join('/') : 'View Code'}
                                </a>
                              ))}
                            </div>
                          </div>
                        )}

                        {paper.datasets_mentioned && paper.datasets_mentioned.length > 0 && (
                          <div className="repro-card__datasets">
                            <span className="repro-card__label">Datasets:</span>
                            <div className="repro-card__dataset-list">
                              {paper.datasets_mentioned.slice(0, 3).map((ds, i) => (
                                <span key={i} className="repro-card__dataset">{ds}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </article>
                    ))}
                  </div>
                </section>
              )}

              {/* Practical tab */}
              {activeTab === 'practical' && (
                <section className="tab-panel" aria-label="Practical applications">
                  <header className="tab-panel__header">
                    <h2>Practical Applications</h2>
                    <span className="tab-panel__count">Papers ready for real-world deployment</span>
                  </header>

                  {/* Industry relevance filter */}
                  <div className="practical-filter">
                    <span className="practical-filter__label">Industry Relevance:</span>
                    <div className="practical-filter__buttons">
                      {(['high', 'medium', 'low'] as const).map((level) => (
                        <button
                          key={level}
                          className={`practical-level-btn ${industryRelevance === level ? 'practical-level-btn--active' : ''}`}
                          onClick={() => setIndustryRelevance(level)}
                        >
                          {level.charAt(0).toUpperCase() + level.slice(1)}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="practical-grid">
                    {practical.map((paper) => (
                      <article key={paper.id} className="practical-card">
                        <header className="practical-card__header">
                          <div className="practical-card__score">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z" />
                            </svg>
                            <span>{paper.impact_score}/10</span>
                          </div>
                          <div className="practical-card__badges">
                            <span className={`practical-badge practical-badge--${paper.industry_relevance}`}>
                              {paper.industry_relevance} relevance
                            </span>
                            {paper.ai_practical_score && (
                              <span className="practical-badge practical-badge--score">
                                {paper.ai_practical_score}
                              </span>
                            )}
                          </div>
                        </header>

                        <h3 className="practical-card__title">
                          <Link href={`https://arxiv.org/abs/${paper.id.split('v')[0]}`} target="_blank">
                            {paper.title}
                          </Link>
                        </h3>

                        {paper.use_cases && paper.use_cases.length > 0 && (
                          <div className="practical-card__usecases">
                            <span className="practical-card__label">Use Cases:</span>
                            <ul>
                              {paper.use_cases.slice(0, 3).map((useCase, i) => (
                                <li key={i}>{useCase}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {paper.scalability && (
                          <div className="practical-card__scalability">
                            <span className="practical-card__label">Scalability:</span>
                            <p>{paper.scalability.slice(0, 150)}{paper.scalability.length > 150 ? '...' : ''}</p>
                          </div>
                        )}

                        {paper.deployment_considerations && (
                          <div className="practical-card__deployment">
                            <span className="practical-card__label">Deployment:</span>
                            <p>{paper.deployment_considerations.slice(0, 150)}{paper.deployment_considerations.length > 150 ? '...' : ''}</p>
                          </div>
                        )}

                        {paper.limitations && paper.limitations.length > 0 && (
                          <div className="practical-card__limitations">
                            <span className="practical-card__label">Limitations:</span>
                            <div className="practical-card__limitation-list">
                              {paper.limitations.slice(0, 2).map((lim, i) => (
                                <span key={i} className="practical-card__limitation">{lim}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </article>
                    ))}
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
