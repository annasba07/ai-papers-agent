'use client';
import ContextualSearch from '@/components/ContextualSearch';
import PaperList from '@/components/PaperList';
import AtlasOverview from '@/components/AtlasOverview';
import { Paper } from '@/types/Paper';
import type { AtlasPaper, AtlasSummary } from '@/types/Atlas';
import { useState, useEffect, useMemo } from 'react';

const mapAtlasPaperToPaper = (paper: AtlasPaper): Paper => {
  const abstract = paper.abstract ?? '';
  const wordCount = abstract ? abstract.split(/\s+/).filter(Boolean).length : 0;
  const readingTime = Math.max(4, Math.round((wordCount / 200) * 5));
  const plainId = paper.id?.split('v')[0] ?? paper.id;

  return {
    id: paper.id,
    title: paper.title ?? 'Untitled Paper',
    authors: paper.authors ?? [],
    published: paper.published ?? '',
    summary: abstract,
    link: paper.link ?? (plainId ? `https://arxiv.org/abs/${plainId}` : '#'),
    aiSummary: {
      summary: abstract || 'Summary not available yet.',
      keyContribution: 'Detailed AI analysis not generated yet.',
      novelty: 'Awaiting AI analysis.',
      technicalInnovation: 'Awaiting AI analysis.',
      methodologyBreakdown: 'Awaiting AI analysis.',
      performanceHighlights: 'Awaiting AI analysis.',
      implementationInsights: 'Awaiting AI analysis.',
      researchContext: 'Awaiting AI analysis.',
      futureImplications: 'Awaiting AI analysis.',
      limitations: 'Awaiting AI analysis.',
      impactScore: 5,
      difficultyLevel: 'intermediate',
      readingTime,
      hasCode: false,
      implementationComplexity: 'medium',
      practicalApplicability: 'medium',
      researchSignificance: 'incremental',
      reproductionDifficulty: 'medium',
    },
  };
};

const SectionNav = () => (
  <nav className="section-nav" aria-label="Page sections">
    <ul className="section-nav__list">
      <li><a href="#top">Overview</a></li>
      <li><a href="#roadmap">Playbook</a></li>
      <li><a href="#contextual-search">Assistant</a></li>
      <li><a href="#atlas-feed">Feed</a></li>
    </ul>
  </nav>
);

export default function Home() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterDays] = useState('7');
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [apiError, setApiError] = useState<string | null>(null);
  const [atlasSummary, setAtlasSummary] = useState<AtlasSummary | null>(null);
  const [atlasSummaryLoading, setAtlasSummaryLoading] = useState<boolean>(true);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [atlasHighlights, setAtlasHighlights] = useState<AtlasPaper[]>([]);
  const [atlasHighlightsLoading, setAtlasHighlightsLoading] = useState<boolean>(true);
  const [highlightsError, setHighlightsError] = useState<string | null>(null);

  const apiBaseUrl = useMemo(() => process.env.NEXT_PUBLIC_API_BASE_URL ?? '', []);

  useEffect(() => {
    const fetchPapers = async () => {
      setLoading(true);
      try {
        setApiError(null);
        const params = new URLSearchParams({
          days: filterDays,
          category: filterCategory,
          query: searchQuery,
        });
        const endpoint = apiBaseUrl
          ? `${apiBaseUrl}/papers?${params.toString()}`
          : `/api/atlas/papers?${params.toString()}`;

        const response = await fetch(endpoint);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (Array.isArray(data)) {
          setPapers(data as Paper[]);
        } else if (Array.isArray(data.papers)) {
          setPapers((data.papers as AtlasPaper[]).map(mapAtlasPaperToPaper));
        } else {
          setPapers([]);
        }
      } catch (error) {
        console.error("Failed to fetch papers:", error);
        setPapers([]);
        if (apiBaseUrl) {
          setApiError(
            'Unable to reach the research API. Start the backend server (`uvicorn app.main:app --reload`) or update NEXT_PUBLIC_API_BASE_URL.'
          );
        } else {
          setApiError('Failed to load atlas dataset. Ensure derived files exist in `data/derived`.');
        }
      } finally {
        setLoading(false);
      }
    };

    const handler = setTimeout(() => {
      fetchPapers();
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [filterDays, filterCategory, searchQuery, apiBaseUrl]);

  useEffect(() => {
    let isMounted = true;

    const fetchSummary = async () => {
      setAtlasSummaryLoading(true);
      setSummaryError(null);
      try {
        const response = await fetch('/api/atlas/summary');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = (await response.json()) as AtlasSummary;
        if (isMounted) {
          setAtlasSummary(data);
        }
      } catch (error) {
        console.error('Failed to load atlas summary:', error);
        if (isMounted) {
          setSummaryError('Failed to load atlas summary');
          setAtlasSummary(null);
        }
      } finally {
        if (isMounted) {
          setAtlasSummaryLoading(false);
        }
      }
    };

    const fetchHighlights = async () => {
      setAtlasHighlightsLoading(true);
      setHighlightsError(null);
      try {
        const response = await fetch('/api/atlas/papers?limit=8');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = (await response.json()) as { papers: AtlasPaper[] };
        if (isMounted) {
          setAtlasHighlights(data.papers);
        }
      } catch (error) {
        console.error('Failed to load atlas highlight papers:', error);
        if (isMounted) {
          setHighlightsError('Failed to load atlas highlight papers');
          setAtlasHighlights([]);
        }
      } finally {
        if (isMounted) {
          setAtlasHighlightsLoading(false);
        }
      }
    };

    fetchSummary();
    fetchHighlights();

    return () => {
      isMounted = false;
    };
  }, []);

  const atlasError = summaryError ?? highlightsError;

  const latestHighlightDate = useMemo(() => {
    let latest: Date | null = null;
    atlasHighlights.forEach((paper) => {
      if (!paper.published) {
        return;
      }
      const candidate = new Date(paper.published);
      if (Number.isNaN(candidate.getTime())) {
        return;
      }
      if (!latest || candidate > latest) {
        latest = candidate;
      }
    });
    return latest;
  }, [atlasHighlights]);

  const latestHighlightLag = useMemo(() => {
    if (!latestHighlightDate) {
      return '—';
    }
    const diffMs = Date.now() - latestHighlightDate.getTime();
    if (diffMs <= 0) {
      return '<1h';
    }
    const diffHours = Math.round(diffMs / (1000 * 60 * 60));
    if (diffHours >= 72) {
      const diffDays = Math.max(1, Math.round(diffHours / 24));
      return `${diffDays}d`;
    }
    return `${Math.max(1, diffHours)}h`;
  }, [latestHighlightDate]);

  const heroSparklineCopy = useMemo(() => {
    if (!atlasSummary) {
      return 'A living atlas that learns from every new release—highlighting velocity, breakthroughs, and the builders behind them.';
    }
    const categories = atlasSummary.stats.categories.length;
    const paperCount = atlasSummary.stats.unique_papers.toLocaleString();
    const freshness =
      latestHighlightLag === '—'
        ? 'staying current as new work lands.'
        : `refreshing within ${latestHighlightLag} of new releases.`;
    return `Tracking ${paperCount} papers across ${categories} active areas, ${freshness}`;
  }, [atlasSummary, latestHighlightLag]);

  return (
    <>
      <SectionNav />
      <main className="page-shell">
        <section id="top" className="hero">
        <div className="hero__content">
          <span className="hero__chip">Living Research Atlas</span>
          <h1>See where AI research is moving—and act on it fast.</h1>
          <p className="hero__subtitle">
            Discover breakout areas, analyse the leading papers, and bootstrap implementation plans with a toolkit
            purpose-built for research teams that need traction today.
          </p>
          <div className="hero__actions">
            <a href="#roadmap" className="btn btn-primary">
              Explore Atlas
            </a>
            <a href="#contextual-search" className="btn btn-secondary">
              Ask the Assistant
            </a>
          </div>
        </div>
        <aside className="hero__meta">
          <span className="hero__meta-title">Inside the atlas</span>
          <ul className="hero__fact-list">
            <li className="hero__fact">
              <span className="hero__fact-value">
                {atlasSummary ? atlasSummary.stats.unique_papers.toLocaleString() : '—'}
              </span>
              <span className="hero__fact-label">Indexed papers</span>
            </li>
            <li className="hero__fact">
              <span className="hero__fact-value">
                {atlasSummary ? atlasSummary.stats.categories.length : '—'}
              </span>
              <span className="hero__fact-label">Active research areas</span>
            </li>
            <li className="hero__fact">
              <span className="hero__fact-value">{latestHighlightLag}</span>
              <span className="hero__fact-label">Last highlight added</span>
            </li>
          </ul>
          <p className="hero__sparkline">{heroSparklineCopy}</p>
        </aside>
      </section>

      <section id="roadmap" className="step-track-section">
        <div className="step-track-section__header">
          <span className="eyebrow">Research playbook</span>
          <h2>Your Research Playbook</h2>
          <p className="section-subtitle">
            Follow the momentum from scouting breakthrough ideas to spinning up agents that can prototype the work.
          </p>
        </div>
        <div className="step-track">
          <StepCard
            step="01"
            title="Explore the landscape"
            description="Track where research velocity is accelerating across categories, benchmarks, and authors."
          />
          <StepCard
            step="02"
            title="Find the right papers"
            description="Drill into the topics with the most momentum. Inspect abstracts, code links, or trends in a click."
          />
          <StepCard
            step="03"
            title="Activate code generation"
            description="Select a key paper and hand off to the multi-agent builder to create specs, tests, and runnable projects."
          />
        </div>
      </section>

      <section id="contextual-search" className="contextual-section" aria-label="Contextual research console">
        <div className="contextual-shell">
          <ContextualSearch />
        </div>
      </section>

      <section aria-label="Atlas snapshot" className="atlas-section">
        <AtlasOverview
          summary={atlasSummary}
          papers={atlasHighlights}
          loadingSummary={atlasSummaryLoading}
          loadingPapers={atlasHighlightsLoading}
          error={atlasError}
        />
      </section>

      <section id="atlas-feed" className="paper-discovery" aria-labelledby="discover-heading">
        <header>
          <span className="eyebrow">Atlas feed</span>
          <h2 id="discover-heading" className="section-title">
            Discover Papers
          </h2>
          <p className="section-subtitle">
            Tune the filters to surface the freshest research signals from the last {filterDays} days.
          </p>
        </header>

        {apiError && <div className="alert alert--error">{apiError}</div>}

        <div className="paper-discovery__controls">
          <input
            type="text"
            placeholder="Filter by keywords…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="form-control"
            aria-label="Filter papers by keyword"
          />
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="form-control"
            aria-label="Filter papers by category"
          >
            <option value="all">All Categories</option>
            <option value="cs.AI">Artificial Intelligence</option>
            <option value="cs.LG">Machine Learning</option>
            <option value="cs.CV">Computer Vision</option>
            <option value="cs.CL">Computation and Language</option>
          </select>
        </div>

        {loading ? (
          <p className="atlas-empty">Loading papers…</p>
        ) : papers.length > 0 ? (
          <PaperList papers={papers} />
        ) : (
          <p className="atlas-empty">No papers found for the selected criteria.</p>
        )}
      </section>
    </main>
    </>
  );
}

type StepCardProps = {
  step: string;
  title: string;
  description: string;
};

const StepCard = ({ step, title, description }: StepCardProps) => (
  <article className="step-card">
    <span className="step-card__step">{step}</span>
    <h3 className="step-card__title">{title}</h3>
    <p className="step-card__copy">{description}</p>
  </article>
);
