'use client';

import { useEffect, useMemo, useState } from 'react';
import CitationGraph from '@/components/CitationGraph';
import './atlas-explore.css';

type AtlasPaper = {
  id?: string;
  title?: string;
  abstract?: string;
  link?: string;
  category?: string;
  published?: string;
  citation_count?: number;
  influential_citation_count?: number;
};

type AtlasSummary = {
  stats?: { unique_papers: number; categories: string[]; input_files: number };
  topCategories?: Array<{ category: string; total: number }>;
  topAuthors?: Array<{ author: string; paper_count: number }>;
  timeline?: Record<string, Array<{ month: string; count: number }>>;
};

type EmbeddingCache = {
  label: string;
  paper_count: number;
  active: boolean;
};

type ContextualResult = {
  analysis: string;
  papers: { id: string; title: string; summary: string }[];
};

type RisingPaper = {
  id: string;
  title: string;
  published: string;
  category: string;
  citation_count: number;
  influential_citation_count: number;
  months_since_publication: number;
  citation_velocity: number;
  link: string;
};

const recencyOptions = [
  { label: 'Last 30 days', value: 30 },
  { label: 'Last 90 days', value: 90 },
  { label: 'Last 6 months', value: 180 },
  { label: 'Last year', value: 365 },
  { label: 'All time', value: 0 },
];

const sortOptions = [
  { label: 'Newest', value: 'published_date' },
  { label: 'Most Cited', value: 'citation_count' },
  { label: 'Title A-Z', value: 'title' },
];

export default function AtlasExplorePage() {
  const [summary, setSummary] = useState<AtlasSummary | null>(null);
  const [papers, setPapers] = useState<AtlasPaper[]>([]);
  const [papersLoading, setPapersLoading] = useState(false);
  const [contextDescription, setContextDescription] = useState('');
  const [contextResult, setContextResult] = useState<ContextualResult | null>(null);
  const [contextLoading, setContextLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [caches, setCaches] = useState<EmbeddingCache[]>([]);
  const [selectedCache, setSelectedCache] = useState<string>('');
  const [category, setCategory] = useState<string>('all');
  const [days, setDays] = useState<number>(90);
  const [query, setQuery] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('published_date');
  const [selectedTimelineCat, setSelectedTimelineCat] = useState<string>('');
  const [graphPaperId, setGraphPaperId] = useState<string>('');
  const [graphPaperTitle, setGraphPaperTitle] = useState<string>('');
  const [risingPapers, setRisingPapers] = useState<RisingPaper[]>([]);
  const [risingLoading, setRisingLoading] = useState(false);

  const availableCategories = useMemo(() => {
    if (summary?.topCategories?.length) {
      return ['all', ...summary.topCategories.map((c) => c.category)];
    }
    return ['all'];
  }, [summary]);

  useEffect(() => {
    fetch('/api/atlas/summary')
      .then((res) => res.json())
      .then((data: AtlasSummary) => setSummary(data))
      .catch(() => setSummary(null));
  }, []);

  useEffect(() => {
    fetch('/api/atlas/embedding-caches')
      .then((res) => res.json())
      .then((data: EmbeddingCache[]) => {
        setCaches(data);
        const active = data.find((c) => c.active);
        if (active) {
          setSelectedCache(active.label);
        } else if (data.length > 0) {
          setSelectedCache(data[0].label);
        }
      })
      .catch(() => setCaches([]));
  }, []);

  useEffect(() => {
    if (!selectedTimelineCat && summary?.topCategories?.length) {
      setSelectedTimelineCat(summary.topCategories[0].category);
    }
  }, [selectedTimelineCat, summary]);

  useEffect(() => {
    const loadPapers = async () => {
      setPapersLoading(true);
      try {
        const params = new URLSearchParams();
        params.set('limit', '50');
        params.set('category', category);
        params.set('days', String(days));
        params.set('order_by', sortBy);
        params.set('order_dir', sortBy === 'title' ? 'asc' : 'desc');
        if (query.trim()) params.set('query', query.trim());
        const res = await fetch(`/api/atlas/papers?${params.toString()}`);
        const data = await res.json();
        setPapers(data.papers || []);
      } catch (err) {
        console.error('Failed to load papers', err);
        setPapers([]);
      } finally {
        setPapersLoading(false);
      }
    };
    loadPapers();
  }, [category, days, query, sortBy]);

  // Fetch rising papers (high citation velocity)
  useEffect(() => {
    const loadRisingPapers = async () => {
      setRisingLoading(true);
      try {
        const params = new URLSearchParams();
        params.set('limit', '12');
        params.set('min_citations', '5');
        params.set('max_months', '24');
        if (category && category !== 'all') {
          params.set('category', category);
        }
        const res = await fetch(`/api/discovery/rising?${params.toString()}`);
        if (res.ok) {
          const data = await res.json();
          setRisingPapers(data.papers || []);
        }
      } catch (err) {
        console.error('Failed to load rising papers', err);
        setRisingPapers([]);
      } finally {
        setRisingLoading(false);
      }
    };
    loadRisingPapers();
  }, [category]);

  const latestTechniques = useMemo(() => {
    return papers.slice(0, 12).map((p) => {
      const summary = p.abstract || '';
      const firstSentence = summary.split('. ').slice(0, 2).join('. ').trim();
      return {
        id: p.id || '',
        title: p.title || '',
        summary: firstSentence || summary.slice(0, 160),
        link: p.link || `http://arxiv.org/abs/${p.id || ''}`,
        category: p.category || '',
        published: p.published,
      };
    });
  }, [papers]);

  const timelineSeries = useMemo(() => {
    if (!summary?.timeline) return [];
    const key = selectedTimelineCat || (summary.topCategories && summary.topCategories[0]?.category) || '';
    if (!key || !summary.timeline[key]) return [];
    return summary.timeline[key].slice(-12); // last 12 months
  }, [summary, selectedTimelineCat]);

  const handleSelectPaperForGraph = (paper: AtlasPaper) => {
    if (paper.id) {
      setGraphPaperId(paper.id);
      setGraphPaperTitle(paper.title || 'Unknown');
    }
  };

  const handleGraphNodeClick = (nodeId: string, title: string) => {
    setGraphPaperId(nodeId);
    setGraphPaperTitle(title);
  };

  const handleContextualSearch = async () => {
    if (!contextDescription.trim()) return;
    setContextLoading(true);
    setContextResult(null);
    setError(null);
    try {
      const body: Record<string, unknown> = { description: contextDescription.trim() };
      if (selectedCache) body.embedding_label = selectedCache;
      const res = await fetch('/api/contextual-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = (await res.json()) as ContextualResult;
      setContextResult(data);
    } catch (err) {
      console.error(err);
      setError('Contextual analysis failed. Ensure the backend is running.');
    } finally {
      setContextLoading(false);
    }
  };

  return (
    <main className="explore-shell">
      <section className="explore-hero card">
        <div>
          <p className="eyebrow">Living Research Atlas</p>
          <h1>Describe your goal. Get the freshest papers and what to do next.</h1>
          <p className="muted">
            Powered by the 12-month atlas and semantic embeddings. Swap models to compare Specter2 vs Voyage.
          </p>
          <div className="hero-actions">
            {caches.length > 0 && (
              <label className="select-inline">
                <span>Embedding</span>
                <select value={selectedCache} onChange={(e) => setSelectedCache(e.target.value)}>
                  {caches.map((c) => (
                    <option key={c.label} value={c.label}>
                      {c.label.replaceAll('_', ' ')} ({c.paper_count})
                    </option>
                  ))}
                </select>
              </label>
            )}
            <div className="filters-row">
              {recencyOptions.map((opt) => (
                <button
                  key={opt.value}
                  className={`pill ${days === opt.value ? 'pill--active' : ''}`}
                  onClick={() => setDays(opt.value)}
                  type="button"
                >
                  {opt.label}
                </button>
              ))}
            </div>
            <div className="filters-row scrollable">
              {availableCategories.map((cat) => (
                <button
                  key={cat}
                  className={`pill ${category === cat ? 'pill--active' : ''}`}
                  onClick={() => setCategory(cat)}
                  type="button"
                >
                  {cat === 'all' ? 'All categories' : cat}
                </button>
              ))}
            </div>
            <label className="select-inline">
              <span>Sort by</span>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                {sortOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
      </section>

      <section className="card explore-grid">
        <div className="panel">
          <h2>Contextual Project Analysis</h2>
          <p className="muted">Describe what you’re building. We’ll fetch the best-matching papers and a plan.</p>
          <textarea
            value={contextDescription}
            onChange={(e) => setContextDescription(e.target.value)}
            placeholder="e.g., On-device vision model for plant ID; need high-accuracy mobile-friendly architectures."
            rows={6}
          />
          <div className="actions-row">
            <button className="btn btn-primary" onClick={handleContextualSearch} disabled={contextLoading}>
              {contextLoading ? 'Analyzing…' : 'Analyze'}
            </button>
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Optional: quick keyword boost (e.g., diffusion, retrieval)"
            />
          </div>
          {error && <div className="alert alert--error">{error}</div>}
          {contextResult && (
            <div className="result-card">
              <h3>Analysis</h3>
              <p className="analysis-text">{contextResult.analysis}</p>
              <h4>Papers</h4>
              <div className="result-list">
                {contextResult.papers.map((p, idx) => (
                  <a key={p.id + idx} href={p.id} target="_blank" rel="noreferrer" className="paper-chip">
                    <span className="rank">#{idx + 1}</span>
                    <div>
                      <div className="paper-title">{p.title}</div>
                      <div className="paper-summary">{p.summary}</div>
                    </div>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="panel">
          <h2>Atlas Snapshot</h2>
          <div className="summary-cards">
            <div className="summary-card">
              <div className="label">Papers</div>
              <div className="value">{summary?.stats?.unique_papers?.toLocaleString() || '–'}</div>
            </div>
            <div className="summary-card">
              <div className="label">Categories</div>
              <div className="value">{summary?.stats?.categories?.length || '–'}</div>
            </div>
            <div className="summary-card">
              <div className="label">Top Authors</div>
              <div className="value">{summary?.topAuthors?.length || '–'}</div>
            </div>
          </div>
          <div className="top-cats">
            {(summary?.topCategories || []).slice(0, 8).map((cat) => (
              <div key={cat.category} className="pill pill--ghost">
                {cat.category} · {cat.total}
              </div>
            ))}
          </div>
          <div className="timeline-block">
            <div className="timeline-header">
              <h4>Trend</h4>
              <select
                value={selectedTimelineCat}
                onChange={(e) => setSelectedTimelineCat(e.target.value)}
                className="timeline-select"
              >
                {(summary?.topCategories || []).map((cat) => (
                  <option key={cat.category} value={cat.category}>
                    {cat.category}
                  </option>
                ))}
              </select>
            </div>
            {timelineSeries.length > 0 ? (
              <div className="sparkline">
                {timelineSeries.map((point) => (
                  <div key={point.month} className="spark-bar" style={{ height: `${Math.min(point.count, 80)}px` }}>
                    <span className="spark-label">{point.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No timeline available.</p>
            )}
          </div>
          <h3>Highlights</h3>
          {papersLoading ? (
            <div className="muted">Loading papers…</div>
          ) : (
            <div className="paper-grid">
              {papers.slice(0, 9).map((paper, idx) => (
                <div key={`${paper.id}-${idx}`} className="highlight-card">
                  <div className="highlight-card__header">
                    <div className="badge">{paper.category}</div>
                    {typeof paper.citation_count === 'number' && paper.citation_count > 0 && (
                      <div className="citation-badge" title="Citation count from Semantic Scholar">
                        {paper.citation_count.toLocaleString()} citations
                      </div>
                    )}
                  </div>
                  <h4>{paper.title}</h4>
                  <p>{paper.abstract?.slice(0, 160)}{paper.abstract && paper.abstract.length > 160 ? '…' : ''}</p>
                  <div className="highlight-card__actions">
                    <a
                      href={paper.link || `http://arxiv.org/abs/${paper.id || ''}`}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-sm"
                    >
                      View Paper
                    </a>
                    <button
                      type="button"
                      className="btn btn-sm btn-ghost"
                      onClick={() => handleSelectPaperForGraph(paper)}
                    >
                      View Graph
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          <h3>Latest Techniques</h3>
          <div className="paper-grid">
            {latestTechniques.map((paper, idx) => (
              <a
                key={`${paper.id}-${idx}`}
                className="highlight-card"
                href={paper.link}
                target="_blank"
                rel="noreferrer"
              >
                <div className="badge">{paper.category || 'AI'}</div>
                <h4>{paper.title}</h4>
                <p>{paper.summary}{paper.summary && !paper.summary.endsWith('…') ? '…' : ''}</p>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* Rising Papers Section */}
      <section className="card rising-section">
        <div className="rising-section__header">
          <h2>Rising Papers</h2>
          <p className="muted">Papers gaining citations faster than their peers. Citation velocity = citations / months since publication.</p>
        </div>
        {risingLoading ? (
          <div className="muted">Loading rising papers…</div>
        ) : risingPapers.length === 0 ? (
          <div className="muted">No rising papers found for this category. Try selecting &quot;All categories&quot;.</div>
        ) : (
          <div className="rising-grid">
            {risingPapers.map((paper, idx) => {
              const velocityTier = paper.citation_velocity >= 20 ? 'viral' :
                paper.citation_velocity >= 10 ? 'hot' :
                paper.citation_velocity >= 5 ? 'rising' :
                paper.citation_velocity >= 2 ? 'growing' : 'steady';
              return (
                <div key={`${paper.id}-${idx}`} className={`rising-card rising-card--${velocityTier}`}>
                  <div className="rising-card__header">
                    <span className={`velocity-badge velocity-badge--${velocityTier}`}>
                      {paper.citation_velocity.toFixed(1)}/mo
                    </span>
                    <span className="badge">{paper.category}</span>
                  </div>
                  <h4>{paper.title}</h4>
                  <div className="rising-card__stats">
                    <span title="Total citations">{paper.citation_count} citations</span>
                    <span title="Age in months">{paper.months_since_publication.toFixed(1)} months old</span>
                    {paper.influential_citation_count > 0 && (
                      <span title="Influential citations">{paper.influential_citation_count} influential</span>
                    )}
                  </div>
                  <div className="rising-card__actions">
                    <a
                      href={paper.link}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-sm"
                    >
                      View Paper
                    </a>
                    <button
                      type="button"
                      className="btn btn-sm btn-ghost"
                      onClick={() => {
                        setGraphPaperId(paper.id);
                        setGraphPaperTitle(paper.title);
                      }}
                    >
                      View Graph
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Similarity Graph Section */}
      <section className="card graph-section">
        <div className="graph-section__header">
          <h2>Paper Similarity Graph</h2>
          <p className="muted">Explore related papers through embedding similarity. Click a paper above or enter an ID.</p>
        </div>
        <div className="graph-section__controls">
          <input
            type="text"
            className="graph-section__input"
            placeholder="Enter paper ID (e.g., 2501.12345)"
            value={graphPaperId}
            onChange={(e) => {
              setGraphPaperId(e.target.value);
              setGraphPaperTitle('');
            }}
          />
          {graphPaperTitle && (
            <span className="graph-section__selected">
              Viewing: <strong>{graphPaperTitle}</strong>
            </span>
          )}
        </div>
        <CitationGraph
          paperId={graphPaperId}
          onNodeClick={handleGraphNodeClick}
        />
      </section>
    </main>
  );
}
