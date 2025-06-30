interface Paper {
  id: string;
  title: string;
  authors: string[];
  published: string;
  summary: string;
  aiSummary: {
    summary: string;
    keyContribution: string;
    novelty: string;
  };
  link: string;
}

interface PaperListProps {
  papers: Paper[];
}

const PaperList: React.FC<PaperListProps> = ({ papers }) => {
  return (
    <div style={{ display: 'grid', gap: '24px' }}>
      {papers.map((paper) => (
        <div key={paper.id} className="card">
          <h3 style={{ fontSize: '20px', color: 'var(--primary-text)', marginBottom: '8px' }}>{paper.title}</h3>
          <p style={{ color: 'var(--secondary-text)', fontSize: '14px', marginBottom: '16px' }}>
            {paper.authors.join(', ')} - {new Date(paper.published).toLocaleDateString()}
          </p>

          <div style={{ marginBottom: '16px' }}>
            <h4 style={{ fontSize: '16px', color: 'var(--accent-blue)', marginBottom: '4px' }}>Key Contribution</h4>
            <p style={{ color: 'var(--secondary-text)' }}>{paper.aiSummary.keyContribution}</p>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <h4 style={{ fontSize: '16px', color: 'var(--accent-blue)', marginBottom: '4px' }}>Novelty</h4>
            <p style={{ color: 'var(--secondary-text)' }}>{paper.aiSummary.novelty}</p>
          </div>

          <details style={{ marginBottom: '24px' }}>
            <summary style={{ cursor: 'pointer', color: 'var(--accent-blue)', fontSize: '14px' }}>View AI Summary & Original Abstract</summary>
            <div style={{ marginTop: '16px' }}>
              <h4 style={{ fontSize: '16px', color: 'var(--accent-blue)', marginBottom: '4px' }}>AI Summary</h4>
              <p style={{ color: 'var(--secondary-text)' }}>{paper.aiSummary.summary}</p>
              <h4 style={{ fontSize: '16px', color: 'var(--accent-blue)', marginTop: '16px', marginBottom: '4px' }}>Original Abstract</h4>
              <p style={{ color: 'var(--secondary-text)' }}>{paper.summary}</p>
            </div>
          </details>

          <a href={paper.link} target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ alignSelf: 'flex-start' }}>
            Read on arXiv
          </a>
        </div>
      ))}
    </div>
  );
};

export default PaperList;
