import React from 'react';

interface ProgressIndicatorProps {
  steps: string[];
  currentStep: number;
  isComplete?: boolean;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  steps,
  currentStep,
  isComplete = false
}) => {
  return (
    <div className="progress-indicator">
      <div className="progress-steps">
        {steps.map((step, index) => (
          <div
            key={index}
            className={`progress-step ${
              index < currentStep ? 'completed' : 
              index === currentStep ? 'active' : 'pending'
            }`}
          >
            <div className="step-icon">
              {index < currentStep ? (
                <span className="step-check">✓</span>
              ) : index === currentStep ? (
                <div className="step-spinner">
                  <div className="spinner"></div>
                </div>
              ) : (
                <span className="step-number">{index + 1}</span>
              )}
            </div>
            <span className="step-label">{step}</span>
          </div>
        ))}
      </div>
      
      {isComplete && (
        <div className="progress-complete">
          <div className="complete-icon">🎉</div>
          <span className="complete-text">Analysis Complete!</span>
        </div>
      )}
    </div>
  );
};

export default ProgressIndicator;