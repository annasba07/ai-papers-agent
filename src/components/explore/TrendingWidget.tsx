"use client";

import { useState, useEffect } from "react";

interface TrendingTopic {
  name: string;
  count: number;
  acceleration?: number;
  category?: string;
}

interface TrendsSummaryRaw {
  hot_topics: TrendingTopic[];
  rising_techniques: TrendingTopic[];
  // Backend returns strings for emerging_areas, not full objects
  emerging_areas: string[] | TrendingTopic[];
}

interface TrendsSummary {
  hot_topics: TrendingTopic[];
  rising_techniques: TrendingTopic[];
  emerging_areas: TrendingTopic[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export default function TrendingWidget() {
  const [trends, setTrends] = useState<TrendsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<"hot" | "rising" | "emerging">("hot");

  useEffect(() => {
    async function fetchTrends() {
      try {
        const endpoint = API_BASE
          ? `${API_BASE}/api/v1/trends/summary`
          : "/api/v1/trends/summary";

        const response = await fetch(endpoint);
        if (response.ok) {
          const rawData: TrendsSummaryRaw = await response.json();

          // Transform emerging_areas from string[] to TrendingTopic[]
          const transformedData: TrendsSummary = {
            hot_topics: rawData.hot_topics || [],
            rising_techniques: rawData.rising_techniques || [],
            emerging_areas: (rawData.emerging_areas || []).map((area) => {
              // Handle both string and object formats for backwards compatibility
              if (typeof area === "string") {
                return { name: area, count: 0 };
              }
              return area;
            }),
          };

          setTrends(transformedData);
        }
      } catch {
        // Silently fail - widget is non-critical
      } finally {
        setLoading(false);
      }
    }

    fetchTrends();
  }, []);

  const getCurrentTopics = (): TrendingTopic[] => {
    if (!trends) return [];
    switch (activeSection) {
      case "hot":
        return trends.hot_topics || [];
      case "rising":
        return trends.rising_techniques || [];
      case "emerging":
        return trends.emerging_areas || [];
      default:
        return [];
    }
  };

  const topics = getCurrentTopics();

  return (
    <div className="widget widget--trending">
      <div className="widget__header">
        <h3 className="widget__title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
            <polyline points="17 6 23 6 23 12" />
          </svg>
          Trending Now
        </h3>
      </div>

      {/* Section Tabs */}
      <div className="widget__tabs">
        <button
          className={`widget__tab ${activeSection === "hot" ? "widget__tab--active" : ""}`}
          onClick={() => setActiveSection("hot")}
        >
          Hot Topics
        </button>
        <button
          className={`widget__tab ${activeSection === "rising" ? "widget__tab--active" : ""}`}
          onClick={() => setActiveSection("rising")}
        >
          Rising
        </button>
        <button
          className={`widget__tab ${activeSection === "emerging" ? "widget__tab--active" : ""}`}
          onClick={() => setActiveSection("emerging")}
        >
          Emerging
        </button>
      </div>

      <div className="widget__content">
        {loading ? (
          <div className="widget__loading">
            <div className="spinner" style={{ width: 20, height: 20 }} />
          </div>
        ) : topics.length > 0 ? (
          <ul className="trending-list">
            {topics.slice(0, 6).map((topic, i) => (
              <li key={topic.name || i} className="trending-item">
                <span className="trending-item__rank">{i + 1}</span>
                <div className="trending-item__info">
                  <span className="trending-item__name">{topic.name}</span>
                  <span className="trending-item__count">
                    {topic.count} papers
                    {topic.acceleration && topic.acceleration > 1 && (
                      <span className="trending-item__acceleration">
                        +{Math.round((topic.acceleration - 1) * 100)}%
                      </span>
                    )}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="widget__empty">No trending data available</p>
        )}
      </div>
    </div>
  );
}
