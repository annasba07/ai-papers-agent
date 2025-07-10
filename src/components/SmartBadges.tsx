import React from 'react';

interface SmartBadgesProps {
  impactScore: number;
  difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
  readingTime: number;
  hasCode: boolean;
  implementationComplexity: 'low' | 'medium' | 'high';
  practicalApplicability: 'low' | 'medium' | 'high';
  researchSignificance?: 'incremental' | 'significant' | 'breakthrough';
  reproductionDifficulty?: 'low' | 'medium' | 'high';
  size?: 'sm' | 'md';
}

const SmartBadges: React.FC<SmartBadgesProps> = ({
  impactScore,
  difficultyLevel,
  readingTime,
  hasCode,
  implementationComplexity,
  practicalApplicability,
  researchSignificance = 'incremental',
  reproductionDifficulty = 'medium',
  size = 'md'
}) => {
  const getImpactColor = (score: number) => {
    if (score >= 4.5) return 'var(--accent-pink)';
    if (score >= 4.0) return 'var(--accent-orange)';
    if (score >= 3.5) return 'var(--accent-blue)';
    if (score >= 3.0) return 'var(--accent-purple)';
    return 'var(--secondary-text)';
  };

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'beginner': return 'var(--accent-blue)';
      case 'intermediate': return 'var(--accent-orange)';
      case 'advanced': return 'var(--accent-pink)';
      default: return 'var(--secondary-text)';
    }
  };


  const getApplicabilityColor = (applicability: string) => {
    switch (applicability) {
      case 'high': return 'var(--accent-blue)';
      case 'medium': return 'var(--accent-orange)';
      case 'low': return 'var(--accent-pink)';
      default: return 'var(--secondary-text)';
    }
  };

  const getSignificanceColor = (significance: string) => {
    switch (significance) {
      case 'breakthrough': return 'var(--accent-pink)';
      case 'significant': return 'var(--accent-orange)';
      case 'incremental': return 'var(--accent-blue)';
      default: return 'var(--secondary-text)';
    }
  };

  const getSignificanceIcon = (significance: string) => {
    switch (significance) {
      case 'breakthrough': return '🚀';
      case 'significant': return '⭐';
      case 'incremental': return '📈';
      default: return '📊';
    }
  };

  const renderStars = (score: number) => {
    const stars = [];
    const fullStars = Math.floor(score);
    const hasHalfStar = score % 1 >= 0.5;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="star full">★</span>);
    }
    
    if (hasHalfStar) {
      stars.push(<span key="half" className="star half">★</span>);
    }
    
    const emptyStars = 5 - Math.ceil(score);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="star empty">☆</span>);
    }
    
    return stars;
  };

  const badgeClass = size === 'sm' ? 'smart-badge-sm' : 'smart-badge';

  return (
    <div className="smart-badges">
      {/* Impact Score */}
      <div className={`${badgeClass} impact-badge`}>
        <div className="badge-content">
          <div className="stars" style={{ color: getImpactColor(impactScore) }}>
            {renderStars(impactScore)}
          </div>
          {size === 'md' && <span className="badge-label">Impact</span>}
        </div>
      </div>

      {/* Reading Time */}
      <div className={`${badgeClass} time-badge`}>
        <div className="badge-content">
          <span className="badge-icon">⏱️</span>
          <span className="badge-text">{readingTime}m</span>
        </div>
      </div>

      {/* Difficulty Level */}
      <div className={`${badgeClass} difficulty-badge`} style={{ borderColor: getDifficultyColor(difficultyLevel) }}>
        <div className="badge-content">
          <span className="difficulty-dot" style={{ backgroundColor: getDifficultyColor(difficultyLevel) }}></span>
          <span className="badge-text">{difficultyLevel}</span>
        </div>
      </div>

      {/* Research Significance */}
      <div className={`${badgeClass} significance-badge`} style={{ borderColor: getSignificanceColor(researchSignificance) }}>
        <div className="badge-content">
          <span className="badge-icon">{getSignificanceIcon(researchSignificance)}</span>
          {size === 'md' && <span className="badge-text">{researchSignificance}</span>}
        </div>
      </div>

      {/* Code Availability */}
      {hasCode && (
        <div className={`${badgeClass} code-badge`}>
          <div className="badge-content">
            <span className="badge-icon">🔧</span>
            {size === 'md' && <span className="badge-text">Code</span>}
          </div>
        </div>
      )}

      {/* Implementation Complexity (only show in md size) */}
      {size === 'md' && (
        <div className={`${badgeClass} complexity-badge`}>
          <div className="badge-content">
            <span className="complexity-bars">
              <span className={`bar ${implementationComplexity === 'low' || implementationComplexity === 'medium' || implementationComplexity === 'high' ? 'active' : ''}`}></span>
              <span className={`bar ${implementationComplexity === 'medium' || implementationComplexity === 'high' ? 'active' : ''}`}></span>
              <span className={`bar ${implementationComplexity === 'high' ? 'active' : ''}`}></span>
            </span>
            <span className="badge-text">Complexity</span>
          </div>
        </div>
      )}

      {/* Practical Applicability (only show in md size) */}
      {size === 'md' && (
        <div className={`${badgeClass} applicability-badge`}>
          <div className="badge-content">
            <span className="applicability-indicator" style={{ color: getApplicabilityColor(practicalApplicability) }}>
              {practicalApplicability === 'high' ? '🚀' : practicalApplicability === 'medium' ? '⚡' : '🔬'}
            </span>
            <span className="badge-text">Practical</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartBadges;