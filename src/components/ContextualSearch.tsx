import { useEffect, useState } from 'react';
import ProgressIndicator from './ProgressIndicator';

interface EmbeddingCache {
  label: string;
  paper_count: number;
  active: boolean;
}

interface SearchPaper {
  id: string;
  title: string;
  summary: string;
  relevance_score?: number;
}

interface SearchResult {
  analysis: string;
  papers: SearchPaper[];
  timing?: {
    total_ms: number;
    retrieval_ms: number;
    rerank_ms: number;
    synthesis_ms: number;
    mode: string;
  };
}

const quickSearchSteps = [
  'Searching papers...',
  'Ranking results...',
];

const deepSearchSteps = [
  'Analyzing your project description...',
  'Searching relevant papers...',
  'Generating AI insights...',
  'Finalizing recommendations...',
];

const ContextualSearch = () => {
  const [description, setDescription] = useState('');
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendReady, setBackendReady] = useState<boolean | null>(null);
  const [embeddingOptions, setEmbeddingOptions] = useState<EmbeddingCache[]>([]);
  const [embeddingLabel, setEmbeddingLabel] = useState<string>('');
  const [searchMode, setSearchMode] = useState<'quick' | 'deep'>('quick');
  const searchSteps = searchMode === 'quick' ? quickSearchSteps : deepSearchSteps;

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('/api/contextual-search');
        if (!response.ok) {
          throw new Error('CONFIG');
        }
        const data = (await response.json()) as { enabled: boolean };
        setBackendReady(data.enabled);
      } catch {
        setBackendReady(false);
      }
    };

    checkBackend();
  }, []);

  useEffect(() => {
    const fetchCaches = async () => {
      try {
        const response = await fetch('/api/atlas/embedding-caches');
        if (!response.ok) {
          throw new Error('Failed to fetch caches');
        }
        const caches = (await response.json()) as EmbeddingCache[];
        setEmbeddingOptions(caches);
        const active = caches.find((cache) => cache.active);
        if (active) {
          setEmbeddingLabel(active.label);
        } else if (caches.length > 0 && !embeddingLabel) {
          setEmbeddingLabel(caches[0].label);
        }
      } catch (error) {
        console.error('Failed to load embedding caches', error);
        setEmbeddingOptions([]);
      }
    };

    fetchCaches();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = async () => {
    if (!description.trim()) {
      return;
    }
    if (backendReady === false) {
      setError('Contextual analysis backend is not available. Start the FastAPI server or set RESEARCH_API_BASE_URL.');
      return;
    }

    setLoading(true);
    setResults(null);
    setCurrentStep(0);
    setIsComplete(false);
    setError(null);

    try {
      // Step 0: Start search
      setCurrentStep(0);

      // Build payload with mode-specific flags
      const payload: Record<string, unknown> = { description };
      if (embeddingLabel) {
        payload.embedding_label = embeddingLabel;
      }

      // Quick mode: skip expensive operations for fast results
      // Deep mode: full AI analysis with reranking and synthesis
      if (searchMode === 'quick') {
        payload.skip_reranking = true;
        payload.skip_synthesis = true;
      }

      // Step 1: Ranking (Quick) or Processing (Deep)
      setCurrentStep(1);

      const response = await fetch('/api/contextual-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // For deep mode, show additional steps as response processes
      if (searchMode === 'deep') {
        setCurrentStep(2);
      }

      const data = (await response.json()) as SearchResult;

      if (searchMode === 'deep') {
        setCurrentStep(3);
      }

      setResults(data);
      setIsComplete(true);
    } catch (err) {
      console.error('Failed to fetch contextual search results:', err);
      setError(
        'Contextual analysis is currently unavailable. Start the backend API (`uvicorn app.main:app --reload`) or configure RESEARCH_API_BASE_URL.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="contextual-search">
      <header className="contextual-search__header">
        <h2>Contextual Project Analysis</h2>
        <p className="section-subtitle contextual-search__subtitle">
          Describe what you&apos;re building. The AI will find relevant papers and suggest cutting-edge techniques.
        </p>
      </header>

      {error && <div className="alert alert--error contextual-search__alert">{error}</div>}

      <div className="contextual-search__form">
        {embeddingOptions.length > 0 && (
          <div className="contextual-search__selector">
            <label htmlFor="embedding-label">Embedding Model</label>
            <select
              id="embedding-label"
              className="form-control contextual-search__select"
              value={embeddingLabel}
              onChange={(event) => setEmbeddingLabel(event.target.value)}
            >
              {embeddingOptions.map((option) => (
                <option key={option.label} value={option.label}>
                  {option.label.replaceAll('_', ' ')} ({option.paper_count} papers)
                </option>
              ))}
            </select>
          </div>
        )}
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="e.g., “I am building a mobile app that identifies plant species from a photo. I need the best on-device vision models…”"
          rows={5}
          className="form-control contextual-search__textarea"
        />
        <div className="contextual-search__actions">
          <div className="contextual-search__mode-toggle">
            <label className="contextual-search__mode-label">
              <input
                type="radio"
                name="searchMode"
                value="quick"
                checked={searchMode === 'quick'}
                onChange={() => setSearchMode('quick')}
                disabled={loading}
              />
              <span className="contextual-search__mode-option">
                <strong>Quick</strong>
                <small>~1-2s, fast semantic search</small>
              </span>
            </label>
            <label className="contextual-search__mode-label">
              <input
                type="radio"
                name="searchMode"
                value="deep"
                checked={searchMode === 'deep'}
                onChange={() => setSearchMode('deep')}
                disabled={loading}
              />
              <span className="contextual-search__mode-option">
                <strong>Deep</strong>
                <small>~3-8s, AI-powered analysis</small>
              </span>
            </label>
          </div>
          <button
            onClick={handleSearch}
            disabled={loading || backendReady === false || backendReady === null}
            className="btn btn-primary contextual-search__submit"
            type="button"
          >
            {loading ? 'Analyzing…' : searchMode === 'quick' ? 'Quick Search' : 'Deep Analysis'}
          </button>
        </div>
      </div>

      {backendReady === false && (
        <p className="contextual-search__tip">
          Tip: run <code>uvicorn app.main:app --reload</code> in <code>backend/</code> and set{' '}
          <code>RESEARCH_API_BASE_URL</code> (or <code>NEXT_PUBLIC_API_BASE_URL</code>) in <code>.env.local</code> so the proxy can reach it.
        </p>
      )}

      {loading && (
        <div className="contextual-search__progress">
          <ProgressIndicator steps={searchSteps} currentStep={currentStep} isComplete={isComplete} />
        </div>
      )}

      {results && (
        <div className="contextual-search__results">
          {results.timing && (
            <div className="contextual-search__timing">
              <span className="contextual-search__timing-badge">
                Completed in {(results.timing.total_ms / 1000).toFixed(1)}s
              </span>
              {results.timing.mode && (
                <span className="contextual-search__timing-mode">
                  {results.timing.mode === 'fast' ? 'Quick mode' : 'Deep analysis'}
                </span>
              )}
            </div>
          )}
          <div>
            <h3 className="contextual-search__heading section-title">Analysis Report</h3>
            <article className="card contextual-search__analysis">{results.analysis}</article>
          </div>

          <div>
            <h3 className="contextual-search__heading section-title">Relevant Papers ({results.papers.length})</h3>
            <div className="contextual-search-results">
              {results.papers.map((paper, index) => (
                <a
                  key={`${paper.id}-${index}`}
                  href={paper.id}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="contextual-paper-card"
                >
                  <div className="paper-rank">#{index + 1}</div>
                  <div className="paper-content">
                    <h4 className="contextual-paper-title">{paper.title}</h4>
                    <p className="contextual-paper-summary">{paper.summary}</p>
                    {paper.relevance_score !== undefined && (
                      <div className="contextual-paper-relevance" title="Relevance: 85% semantic similarity + 15% keyword match">
                        <span className="contextual-paper-relevance__bar">
                          <span
                            className="contextual-paper-relevance__fill"
                            style={{ width: `${Math.min(paper.relevance_score * 100, 100)}%` }}
                          />
                        </span>
                        <span className="contextual-paper-relevance__score">
                          {(paper.relevance_score * 100).toFixed(0)}% match
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="paper-arrow">→</div>
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default ContextualSearch;
