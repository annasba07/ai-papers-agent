import { useState } from 'react';
import { Paper } from '../types/Paper';
import PaperDetailModal from './PaperDetailModal';
import SmartBadges from './SmartBadges';

interface PaperListProps {
  papers: Paper[];
}

const PaperList: React.FC<PaperListProps> = ({ papers }) => {
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openPaperDetail = (paper: Paper) => {
    setSelectedPaper(paper);
    setIsModalOpen(true);
  };

  const closePaperDetail = () => {
    setIsModalOpen(false);
    setSelectedPaper(null);
  };

  return (
    <>
      <div style={{ display: 'grid', gap: '24px' }}>
        {papers.map((paper) => (
          <div key={paper.id} className="card paper-card" onClick={() => openPaperDetail(paper)}>
            <div className="paper-card-header">
              <h3 className="paper-card-title">
                {paper.title}
              </h3>
              <div className="paper-card-meta">
                <SmartBadges
                  impactScore={paper.aiSummary.impactScore || 3.0}
                  difficultyLevel={paper.aiSummary.difficultyLevel || 'intermediate'}
                  readingTime={paper.aiSummary.readingTime || Math.ceil(paper.summary.split(' ').length / 200)}
                  hasCode={paper.aiSummary.hasCode || false}
                  implementationComplexity={paper.aiSummary.implementationComplexity || 'medium'}
                  practicalApplicability={paper.aiSummary.practicalApplicability || 'medium'}
                  size="sm"
                />
              </div>
            </div>
          <p className="paper-authors">
            {paper.authors.join(', ')} · {new Date(paper.published).toLocaleDateString()}
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
    
    {selectedPaper && (
      <PaperDetailModal
        paper={selectedPaper}
        isOpen={isModalOpen}
        onClose={closePaperDetail}
      />
    )}
  </>
  );
};

export default PaperList;
