import { useState } from 'react';
import ProgressIndicator from './ProgressIndicator';

interface SearchResult {
  analysis: string;
  papers: {
    id: string;
    title: string;
    summary: string;
  }[];
}

const searchSteps = [
  'Analyzing your project description...',
  'Searching relevant papers...',
  'Generating insights...',
  'Finalizing recommendations...',
];

const ContextualSearch = () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
  const [description, setDescription] = useState('');
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!description.trim()) {
      return;
    }
    if (!API_BASE_URL) {
      setError('Configure NEXT_PUBLIC_API_BASE_URL to use contextual analysis or start the FastAPI backend.');
      return;
    }

    setLoading(true);
    setResults(null);
    setCurrentStep(0);
    setIsComplete(false);
    setError(null);

    try {
      const progressIntervals = [800, 1200, 1500, 2000];

      setCurrentStep(0);
      await new Promise((resolve) => setTimeout(resolve, progressIntervals[0]));

      setCurrentStep(1);
      await new Promise((resolve) => setTimeout(resolve, progressIntervals[1]));

      setCurrentStep(2);
      const response = await fetch(`${API_BASE_URL}/papers/contextual-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setCurrentStep(3);
      await new Promise((resolve) => setTimeout(resolve, progressIntervals[3]));

      const data = (await response.json()) as SearchResult;
      setResults(data);
      setIsComplete(true);
    } catch (err) {
      console.error('Failed to fetch contextual search results:', err);
      setError(
        'Contextual analysis is currently unavailable. Start the backend API (`uvicorn app.main:app --reload`) or set NEXT_PUBLIC_API_BASE_URL to a running instance.'
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
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="e.g., “I am building a mobile app that identifies plant species from a photo. I need the best on-device vision models…”"
          rows={5}
          className="form-control contextual-search__textarea"
        />
        <div className="contextual-search__actions">
          <button
            onClick={handleSearch}
            disabled={loading || !API_BASE_URL}
            className="btn btn-primary contextual-search__submit"
            type="button"
          >
            {loading ? 'Analyzing…' : 'Analyze Project'}
          </button>
        </div>
      </div>

      {!API_BASE_URL && (
        <p className="contextual-search__tip">
          Tip: run <code>uvicorn app.main:app --reload</code> in <code>backend/</code> and set{' '}
          <code>NEXT_PUBLIC_API_BASE_URL</code> to enable contextual insights.
        </p>
      )}

      {loading && (
        <div className="contextual-search__progress">
          <ProgressIndicator steps={searchSteps} currentStep={currentStep} isComplete={isComplete} />
        </div>
      )}

      {results && (
        <div className="contextual-search__results">
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
