import React from 'react';

interface CodeRepository {
  url: string;
  stars: number;
  forks: number;
  lastUpdated: string;
  description: string;
  isOfficial: boolean;
  language: string;
  qualityScore: number;
}

interface CodeAvailability {
  hasCode: boolean;
  officialRepo: CodeRepository | null;
  communityRepos: CodeRepository[];
  totalRepos: number;
}

interface CodeRepositoriesProps {
  codeAvailability: CodeAvailability;
}

const CodeRepositories: React.FC<CodeRepositoriesProps> = ({ codeAvailability }) => {
  if (!codeAvailability || !codeAvailability.hasCode) {
    return (
      <div style={{ padding: '12px', backgroundColor: 'var(--card-bg)', borderRadius: '8px', marginTop: '16px' }}>
        <h4 style={{ fontSize: '14px', color: 'var(--secondary-text)', margin: 0 }}>
          ❌ No code implementations found
        </h4>
      </div>
    );
  }

  const { officialRepo, communityRepos, totalRepos } = codeAvailability;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 30) return `${diffDays} days ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  };

  const getQualityColor = (score: number) => {
    if (score >= 8) return '#10b981'; // green
    if (score >= 6) return '#f59e0b'; // yellow
    return '#6b7280'; // gray
  };

  const renderRepo = (repo: CodeRepository, isOfficial: boolean = false) => (
    <a
      href={repo.url}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        display: 'block',
        padding: '12px',
        backgroundColor: 'var(--card-bg)',
        borderRadius: '8px',
        marginBottom: '8px',
        border: isOfficial ? '2px solid var(--accent-blue)' : '1px solid rgba(255,255,255,0.1)',
        textDecoration: 'none',
        color: 'inherit',
        transition: 'all 0.2s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            {isOfficial && (
              <span style={{
                fontSize: '11px',
                backgroundColor: 'var(--accent-blue)',
                color: 'white',
                padding: '2px 8px',
                borderRadius: '4px',
                fontWeight: '600'
              }}>
                ✅ OFFICIAL
              </span>
            )}
            <span style={{ fontSize: '12px', color: 'var(--secondary-text)' }}>
              {repo.language}
            </span>
          </div>
          <h5 style={{
            margin: 0,
            fontSize: '14px',
            fontWeight: '600',
            color: 'var(--accent-blue)'
          }}>
            {repo.url.split('/').slice(-2).join('/')}
          </h5>
        </div>
        <div style={{
          fontSize: '18px',
          fontWeight: '700',
          color: getQualityColor(repo.qualityScore)
        }}>
          {repo.qualityScore.toFixed(1)}
        </div>
      </div>

      {repo.description && (
        <p style={{
          margin: '0 0 8px 0',
          fontSize: '12px',
          color: 'var(--secondary-text)',
          lineHeight: '1.4'
        }}>
          {repo.description.length > 150
            ? repo.description.substring(0, 150) + '...'
            : repo.description}
        </p>
      )}

      <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: 'var(--secondary-text)' }}>
        <span>⭐ {repo.stars.toLocaleString()}</span>
        <span>🔱 {repo.forks.toLocaleString()}</span>
        <span>📅 Updated {formatDate(repo.lastUpdated)}</span>
      </div>
    </a>
  );

  return (
    <div style={{ marginTop: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <h4 style={{ margin: 0, fontSize: '16px', color: 'var(--accent-blue)' }}>
          💻 Code Implementations
        </h4>
        <span style={{
          fontSize: '11px',
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          color: 'var(--accent-blue)',
          padding: '2px 8px',
          borderRadius: '12px',
          fontWeight: '600'
        }}>
          {totalRepos} {totalRepos === 1 ? 'repo' : 'repos'} found
        </span>
      </div>

      {officialRepo && (
        <div style={{ marginBottom: '16px' }}>
          <p style={{ fontSize: '12px', color: 'var(--secondary-text)', margin: '0 0 8px 0' }}>
            Official Implementation
          </p>
          {renderRepo(officialRepo, true)}
        </div>
      )}

      {communityRepos.length > 0 && (
        <div>
          <p style={{ fontSize: '12px', color: 'var(--secondary-text)', margin: '0 0 8px 0' }}>
            Community Implementations {communityRepos.length > 3 && `(Top ${Math.min(3, communityRepos.length)})`}
          </p>
          {communityRepos.slice(0, 3).map((repo, index) => (
            <div key={index}>
              {renderRepo(repo)}
            </div>
          ))}
          {communityRepos.length > 3 && (
            <p style={{
              fontSize: '12px',
              color: 'var(--secondary-text)',
              textAlign: 'center',
              margin: '8px 0 0 0'
            }}>
              + {communityRepos.length - 3} more implementations
            </p>
          )}
        </div>
      )}

      <div style={{
        marginTop: '12px',
        padding: '8px',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderRadius: '6px',
        fontSize: '11px',
        color: 'var(--secondary-text)',
        lineHeight: '1.4'
      }}>
        💡 <strong>Quality Score</strong> considers stars, recency, official status, and activity. Higher is better.
      </div>
    </div>
  );
};

export default CodeRepositories;
