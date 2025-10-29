import { useState } from 'react';
import ProgressIndicator from './ProgressIndicator';

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
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  const [description, setDescription] = useState('');
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const searchSteps = [
    'Analyzing your project description...',
    'Searching relevant papers...',
    'Generating insights...',
    'Finalizing recommendations...'
  ];

  const handleSearch = async () => {
    if (!description) return;
    setLoading(true);
    setResults(null); // Clear previous results
    setCurrentStep(0);
    setIsComplete(false);
    setError(null);
    
    try {
      // Simulate progressive steps for better UX
      const progressIntervals = [800, 1200, 1500, 2000];
      
      // Step 1: Analyzing description
      setCurrentStep(0);
      await new Promise(resolve => setTimeout(resolve, progressIntervals[0]));
      
      // Step 2: Searching papers
      setCurrentStep(1);
      await new Promise(resolve => setTimeout(resolve, progressIntervals[1]));
      
      // Step 3: Generating insights (actual API call)
      setCurrentStep(2);
      const response = await fetch(`${API_BASE_URL}/papers/contextual-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Step 4: Finalizing
      setCurrentStep(3);
      await new Promise(resolve => setTimeout(resolve, progressIntervals[3]));
      
      const data = await response.json();
      setResults(data);
      setIsComplete(true);
      
    } catch (error) {
      console.error("Failed to fetch contextual search results:", error);
      setError(
        "Contextual analysis is currently unavailable. Start the backend API (`uvicorn app.main:app --reload`) or set NEXT_PUBLIC_API_BASE_URL to a running instance."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>Contextual Project Analysis</h2>
      <p style={{ color: 'var(--secondary-text)', marginBottom: '16px' }}>
        Describe what you&apos;re building. The AI will find relevant papers and suggest cutting-edge techniques.
      </p>
      {error && (
        <div style={{
          marginBottom: '16px',
          padding: '16px',
          borderRadius: '12px',
          border: '1px solid rgba(239, 68, 68, 0.35)',
          background: 'rgba(239, 68, 68, 0.08)',
          color: '#fecaca'
        }}>
          {error}
        </div>
      )}
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

      {loading && (
        <div style={{ marginTop: '24px' }}>
          <ProgressIndicator
            steps={searchSteps}
            currentStep={currentStep}
            isComplete={isComplete}
          />
        </div>
      )}

      {results && (
        <div style={{ marginTop: '32px' }}>
          <h3 style={{ marginBottom: '16px' }}>Analysis Report</h3>
          <div className="card" style={{ whiteSpace: 'pre-wrap', lineHeight: '1.7' }}>
            {results.analysis}
          </div>

          <h3 style={{ marginTop: '32px', marginBottom: '16px' }}>Relevant Papers ({results.papers.length})</h3>
          <div className="contextual-search-results">
            {results.papers.map((paper, index) => (
              <a 
                key={paper.id} 
                href={paper.id} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="contextual-paper-card"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="paper-rank">#{index + 1}</div>
                <div className="paper-content">
                  <h4 className="contextual-paper-title">{paper.title}</h4>
                  <p className="contextual-paper-summary">
                    {paper.summary}
                  </p>
                </div>
                <div className="paper-arrow">→</div>
              </a>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};

export default ContextualSearch;
