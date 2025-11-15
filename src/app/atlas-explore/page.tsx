'use client';

import { useEffect, useMemo, useState } from 'react';

type AtlasPaper = {
  id?: string;
  title?: string;
  abstract?: string;
  link?: string;
  category?: string;
  published?: string;
};

type AtlasSummary = {
  stats?: { unique_papers: number; categories: string[]; input_files: number };
  topCategories?: Array<{ category: string; total: number }>;
  topAuthors?: Array<{ author: string; paper_count: number }>;
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

const recencyOptions = [
  { label: 'Last 30 days', value: 30 },
  { label: 'Last 90 days', value: 90 },
  { label: 'Last 6 months', value: 180 },
  { label: 'Last year', value: 365 },
  { label: 'All time', value: 0 },
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
    const loadPapers = async () => {
      setPapersLoading(true);
      try {
        const params = new URLSearchParams();
        params.set('limit', '50');
        params.set('category', category);
        params.set('days', String(days));
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
  }, [category, days, query]);

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
          <h3>Highlights</h3>
          {papersLoading ? (
            <div className="muted">Loading papers…</div>
          ) : (
            <div className="paper-grid">
              {papers.slice(0, 9).map((paper, idx) => (
                <a
                  key={`${paper.id}-${idx}`}
                  className="highlight-card"
                  href={paper.link || `http://arxiv.org/abs/${paper.id || ''}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  <div className="badge">{paper.category}</div>
                  <h4>{paper.title}</h4>
                  <p>{paper.abstract?.slice(0, 160)}{paper.abstract && paper.abstract.length > 160 ? '…' : ''}</p>
                </a>
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
