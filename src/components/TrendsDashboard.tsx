"use client";

import { useState, useEffect, type CSSProperties } from "react";
import type { TrendSummary, TrendingTopic, RisingTechnique, ActiveAuthor } from "@/types/Trends";

type TrendsDashboardProps = {
  apiBaseUrl?: string;
};

const pillVariants = ["indigo", "emerald", "amber", "pink", "sky", "rose"] as const;

const TrendsDashboard = ({ apiBaseUrl = "" }: TrendsDashboardProps) => {
  const [summary, setSummary] = useState<TrendSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"hot" | "rising" | "authors">("hot");

  useEffect(() => {
    const fetchTrends = async () => {
      setLoading(true);
      setError(null);

      try {
        const endpoint = apiBaseUrl
          ? `${apiBaseUrl}/trends/summary`
          : "/api/v1/trends/summary";

        const response = await fetch(endpoint);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSummary(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch trends");
      } finally {
        setLoading(false);
      }
    };

    fetchTrends();
  }, [apiBaseUrl]);

  const formatAcceleration = (acceleration: number) => {
    const sign = acceleration >= 0 ? "+" : "";
    return `${sign}${acceleration.toFixed(0)}%`;
  };

  if (loading) {
    return (
      <section className="trends-dashboard">
        <header className="trends-dashboard__header">
          <span className="eyebrow">Research Trends</span>
          <h2>What&apos;s Trending in AI Research</h2>
        </header>
        <div className="trends-dashboard__loading">
          <div className="trends-dashboard__spinner" />
          <p>Analyzing research trends...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="trends-dashboard">
        <header className="trends-dashboard__header">
          <span className="eyebrow">Research Trends</span>
          <h2>What&apos;s Trending in AI Research</h2>
        </header>
        <div className="alert alert--error">{error}</div>
      </section>
    );
  }

  if (!summary) {
    return (
      <section className="trends-dashboard">
        <header className="trends-dashboard__header">
          <span className="eyebrow">Research Trends</span>
          <h2>What&apos;s Trending in AI Research</h2>
        </header>
        <p className="trends-dashboard__empty">No trend data available.</p>
      </section>
    );
  }

  return (
    <section className="trends-dashboard">
      <header className="trends-dashboard__header">
        <span className="eyebrow">Research Trends</span>
        <h2>What&apos;s Trending in AI Research</h2>
        <p className="section-subtitle">
          Real-time analysis of technique adoption, research velocity, and emerging areas.
        </p>
      </header>

      {/* Tab Navigation */}
      <nav className="trends-dashboard__tabs">
        <button
          className={`trends-dashboard__tab ${activeTab === "hot" ? "trends-dashboard__tab--active" : ""}`}
          onClick={() => setActiveTab("hot")}
        >
          Hot Topics
          <span className="trends-dashboard__tab-count">{summary.hot_topics.length}</span>
        </button>
        <button
          className={`trends-dashboard__tab ${activeTab === "rising" ? "trends-dashboard__tab--active" : ""}`}
          onClick={() => setActiveTab("rising")}
        >
          Rising Techniques
          <span className="trends-dashboard__tab-count">{summary.rising_techniques.length}</span>
        </button>
        <button
          className={`trends-dashboard__tab ${activeTab === "authors" ? "trends-dashboard__tab--active" : ""}`}
          onClick={() => setActiveTab("authors")}
        >
          Active Authors
          <span className="trends-dashboard__tab-count">{summary.active_authors.length}</span>
        </button>
      </nav>

      {/* Tab Content */}
      <div className="trends-dashboard__content">
        {activeTab === "hot" && (
          <div className="trends-dashboard__panel">
            <div className="trends-topic-grid">
              {summary.hot_topics.map((topic, index) => (
                <HotTopicCard
                  key={topic.normalized_name}
                  topic={topic}
                  rank={index + 1}
                  variant={pillVariants[index % pillVariants.length]}
                />
              ))}
            </div>
          </div>
        )}

        {activeTab === "rising" && (
          <div className="trends-dashboard__panel">
            <div className="trends-technique-grid">
              {summary.rising_techniques.map((technique, index) => (
                <RisingTechniqueCard
                  key={technique.normalized_name}
                  technique={technique}
                  rank={index + 1}
                  variant={pillVariants[index % pillVariants.length]}
                  formatAcceleration={formatAcceleration}
                />
              ))}
            </div>
          </div>
        )}

        {activeTab === "authors" && (
          <div className="trends-dashboard__panel">
            <div className="trends-author-grid">
              {summary.active_authors.map((author, index) => (
                <ActiveAuthorCard
                  key={author.name}
                  author={author}
                  rank={index + 1}
                  variant={pillVariants[index % pillVariants.length]}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Emerging Areas */}
      {summary.emerging_areas.length > 0 && (
        <div className="trends-dashboard__emerging">
          <h3 className="section-title">Emerging Research Areas</h3>
          <div className="trends-emerging-pills">
            {summary.emerging_areas.map((area, index) => (
              <span
                key={area}
                className={`trends-emerging-pill trends-emerging-pill--${pillVariants[index % pillVariants.length]}`}
              >
                {area}
              </span>
            ))}
          </div>
        </div>
      )}

      <footer className="trends-dashboard__footer">
        <span className="trends-dashboard__timestamp">
          Last updated: {new Date(summary.generated_at).toLocaleString()}
        </span>
      </footer>
    </section>
  );
};

const HotTopicCard = ({
  topic,
  rank,
  variant,
}: {
  topic: TrendingTopic;
  rank: number;
  variant: string;
}) => {
  const maxCount = Math.max(topic.current_count, topic.previous_count, 1);
  const currentShare = (topic.current_count / maxCount) * 100;
  const previousShare = (topic.previous_count / maxCount) * 100;

  return (
    <article className={`trends-topic-card trends-topic-card--${variant}`}>
      <div className="trends-topic-card__header">
        <span className="trends-topic-card__rank">#{rank}</span>
        <span className="trends-topic-card__name">{topic.name}</span>
        <span
          className={`trends-topic-card__acceleration ${
            topic.acceleration >= 0 ? "trends-topic-card__acceleration--up" : "trends-topic-card__acceleration--down"
          }`}
        >
          {topic.acceleration >= 0 ? "+" : ""}
          {topic.acceleration.toFixed(0)}%
        </span>
      </div>

      <div className="trends-topic-card__stats">
        <div className="trends-topic-card__stat">
          <span className="trends-topic-card__stat-label">Current</span>
          <span className="trends-topic-card__stat-value">{topic.current_count}</span>
        </div>
        <div className="trends-topic-card__stat">
          <span className="trends-topic-card__stat-label">Previous</span>
          <span className="trends-topic-card__stat-value">{topic.previous_count}</span>
        </div>
      </div>

      <div className="trends-topic-card__bars">
        <div className="trends-topic-card__bar trends-topic-card__bar--current">
          <span style={{ width: `${currentShare}%` } as CSSProperties} />
        </div>
        <div className="trends-topic-card__bar trends-topic-card__bar--previous">
          <span style={{ width: `${previousShare}%` } as CSSProperties} />
        </div>
      </div>

      {topic.representative_papers.length > 0 && (
        <div className="trends-topic-card__papers">
          <span className="trends-topic-card__papers-label">Recent papers:</span>
          <ul>
            {topic.representative_papers.slice(0, 2).map((paper) => (
              <li key={paper.id}>
                <a
                  href={`https://arxiv.org/abs/${paper.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={paper.title}
                >
                  {paper.title.length > 60 ? `${paper.title.slice(0, 60)}...` : paper.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {topic.related_topics.length > 0 && (
        <div className="trends-topic-card__related">
          <span>Related:</span>
          {topic.related_topics.map((t) => (
            <span key={t} className="trends-topic-card__related-tag">
              {t}
            </span>
          ))}
        </div>
      )}
    </article>
  );
};

const RisingTechniqueCard = ({
  technique,
  rank,
  variant,
  formatAcceleration,
}: {
  technique: RisingTechnique;
  rank: number;
  variant: string;
  formatAcceleration: (n: number) => string;
}) => (
  <article className={`trends-technique-card trends-technique-card--${variant}`}>
    <div className="trends-technique-card__header">
      <span className="trends-technique-card__rank">#{rank}</span>
      <span className="trends-technique-card__name">{technique.name}</span>
    </div>

    <div className="trends-technique-card__growth">
      <span className="trends-technique-card__growth-value">
        {formatAcceleration(technique.acceleration)}
      </span>
      <span className="trends-technique-card__growth-label">growth</span>
    </div>

    <div className="trends-technique-card__category">
      <span className="trends-technique-card__category-badge">{technique.category}</span>
    </div>

    <div className="trends-technique-card__counts">
      <span>{technique.previous_count} papers</span>
      <span className="trends-technique-card__arrow">→</span>
      <span className="trends-technique-card__current">{technique.current_count} papers</span>
    </div>
  </article>
);

const ActiveAuthorCard = ({
  author,
  rank,
  variant,
}: {
  author: ActiveAuthor;
  rank: number;
  variant: string;
}) => (
  <article className={`trends-author-card trends-author-card--${variant}`}>
    <div className="trends-author-card__header">
      <span className="trends-author-card__rank">#{rank}</span>
      <span className="trends-author-card__name">{author.name}</span>
    </div>

    <div className="trends-author-card__stats">
      <div className="trends-author-card__stat">
        <span className="trends-author-card__stat-value">{author.recent_papers}</span>
        <span className="trends-author-card__stat-label">Recent</span>
      </div>
      <div className="trends-author-card__stat">
        <span className="trends-author-card__stat-value">{author.paper_count}</span>
        <span className="trends-author-card__stat-label">Total</span>
      </div>
    </div>

    {author.top_topics.length > 0 && (
      <div className="trends-author-card__topics">
        {author.top_topics.map((topic) => (
          <span key={topic} className="trends-author-card__topic-tag">
            {topic}
          </span>
        ))}
      </div>
    )}
  </article>
);

export default TrendsDashboard;
