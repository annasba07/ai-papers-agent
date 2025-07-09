import React, { useEffect, useRef } from 'react';
import { Paper } from '../types/Paper';
import SmartBadges from './SmartBadges';

interface PaperDetailModalProps {
  paper: Paper;
  isOpen: boolean;
  onClose: () => void;
}

const PaperDetailModal: React.FC<PaperDetailModalProps> = ({ paper, isOpen, onClose }) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.addEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const extractKeyTerms = (text: string): string[] => {
    const terms = text.match(/\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b/g) || [];
    return [...new Set(terms)].slice(0, 8);
  };

  const conceptTerms = extractKeyTerms(paper.aiSummary.keyContribution + ' ' + paper.aiSummary.novelty);
  const estimatedReadingTime = Math.ceil(paper.summary.split(' ').length / 200);

  return (
    <div className="modal-overlay">
      <div className="modal-content" ref={modalRef}>
        <div className="modal-header">
          <button className="modal-close" onClick={onClose} aria-label="Close modal">×</button>
        </div>

        <div className="modal-body">
          <div className="paper-header">
            <h1 className="paper-title">{paper.title}</h1>
            <div className="paper-meta">
              <span className="authors">{paper.authors.join(', ')}</span>
              <span className="publication-date">{new Date(paper.published).toLocaleDateString()}</span>
            </div>
            <div style={{ marginTop: '16px' }}>
              <SmartBadges
                impactScore={paper.aiSummary.impactScore || 3.0}
                difficultyLevel={paper.aiSummary.difficultyLevel || 'intermediate'}
                readingTime={paper.aiSummary.readingTime || estimatedReadingTime}
                hasCode={paper.aiSummary.hasCode || false}
                implementationComplexity={paper.aiSummary.implementationComplexity || 'medium'}
                practicalApplicability={paper.aiSummary.practicalApplicability || 'medium'}
                size="md"
              />
            </div>
          </div>

          <div className="concept-cloud">
            <h3>Key Concepts</h3>
            <div className="concepts">
              {conceptTerms.map((term, index) => (
                <span key={index} className="concept-tag" style={{ animationDelay: `${index * 0.1}s` }}>
                  {term}
                </span>
              ))}
            </div>
          </div>

          <div className="content-sections">
            <section className="insight-section">
              <h3>Key Contribution</h3>
              <div className="insight-card contribution">
                <p>{paper.aiSummary.keyContribution}</p>
              </div>
            </section>

            <section className="insight-section">
              <h3>What&apos;s Novel</h3>
              <div className="insight-card novelty">
                <p>{paper.aiSummary.novelty}</p>
              </div>
            </section>

            <section className="insight-section">
              <h3>AI Summary</h3>
              <div className="insight-card summary">
                <p>{paper.aiSummary.summary}</p>
              </div>
            </section>

            <section className="insight-section">
              <h3>Original Abstract</h3>
              <div className="insight-card abstract">
                <p>{paper.summary}</p>
              </div>
            </section>
          </div>

          <div className="modal-actions">
            <a 
              href={paper.link} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="btn btn-primary"
            >
              Read Full Paper
            </a>
            <button className="btn btn-secondary" onClick={onClose}>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaperDetailModal;