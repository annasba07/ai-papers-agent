import { useState } from 'react';

// Define the structure of the results once, to be reused
interface SearchResult {
  analysis: string;
  papers: {
    id: string;
    title: string;
    summary: string; // Assuming the API returns this
  }[];
}

const ContextualSearch = () => {
  const [description, setDescription] = useState('');
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!description) return;
    setLoading(true);
    setResults(null); // Clear previous results
    try {
      const response = await fetch('http://localhost:8000/papers/contextual-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Failed to fetch contextual search results:", error);
      // Optionally, set an error state here to show in the UI
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>Contextual Project Analysis</h2>
      <p style={{ color: 'var(--secondary-text)', marginBottom: '16px' }}>
        Describe what you're building. The AI will find relevant papers and suggest cutting-edge techniques.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="e.g., 'I am building a mobile app that identifies plant species from a photo taken by the user. I need to know the best models for high-accuracy, on-device image classification...'"
          rows={5}
          className="form-control"
        />
        <button onClick={handleSearch} disabled={loading} className="btn btn-primary" style={{ alignSelf: 'flex-start' }}>
          {loading ? 'Analyzing...' : 'Analyze Project'}
        </button>
      </div>

      {loading && <p style={{ marginTop: '24px', textAlign: 'center' }}>Analyzing your project and fetching papers...</p>}

      {results && (
        <div style={{ marginTop: '32px' }}>
          <h3 style={{ marginBottom: '16px' }}>Analysis Report</h3>
          <div className="card" style={{ whiteSpace: 'pre-wrap', lineHeight: '1.7' }}>
            {results.analysis}
          </div>

          <h3 style={{ marginTop: '32px', marginBottom: '16px' }}>Relevant Papers</h3>
          <div style={{ display: 'grid', gap: '16px' }}>
            {results.papers.map((paper) => (
              <a key={paper.id} href={paper.id} target="_blank" rel="noopener noreferrer" className="card">
                <h3 style={{ marginBottom: '8px' }}>{paper.title}</h3>
                <p style={{ color: 'var(--secondary-text)', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                  {paper.summary}
                </p>
              </a>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};

export default ContextualSearch;
