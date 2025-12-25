"use client";

import { useEffect, useState } from "react";
import type { ExploreFilters } from "@/types/Explore";

interface TrendingConcept {
  id: number;
  name: string;
  category: string;
  total_papers: number;
  recent_papers: number;
  growth_percentage: number;
}

interface FilterSidebarProps {
  filters: ExploreFilters;
  onFilterChange: (key: keyof ExploreFilters, value: unknown) => void;
  totalPapers: number;
  filteredPapers?: number; // Optional: count after filters applied
  isMobileOpen?: boolean;
  onMobileClose?: () => void;
  onTopicClick?: (topicName: string) => void;
}

const categories = [
  { value: "cs.AI", label: "Artificial Intelligence" },
  { value: "cs.LG", label: "Machine Learning" },
  { value: "cs.CL", label: "Computation & Language" },
  { value: "cs.CV", label: "Computer Vision" },
  { value: "cs.NE", label: "Neural & Evolutionary" },
  { value: "cs.RO", label: "Robotics" },
  { value: "stat.ML", label: "Statistics ML" },
];

const difficulties = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
  { value: "expert", label: "Expert" },
];

const timeRanges = [
  { value: 7, label: "Last 7 days" },
  { value: 30, label: "Last 30 days" },
  { value: 90, label: "Last 90 days" },
  { value: 365, label: "Last year" },
];

// Fallback topics when API is unavailable
const fallbackTopics = ["LLM Agents", "Mixture of Experts", "RLHF", "Diffusion", "RAG"];

export default function FilterSidebar({
  filters,
  onFilterChange,
  totalPapers,
  filteredPapers,
  isMobileOpen = false,
  onMobileClose,
  onTopicClick,
}: FilterSidebarProps) {
  const [trendingTopics, setTrendingTopics] = useState<TrendingConcept[]>([]);
  const [isLoadingTopics, setIsLoadingTopics] = useState(true);

  // Fetch trending topics from API
  useEffect(() => {
    const fetchTrendingTopics = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/knowledge-graph/concepts/trending?limit=5`
        );
        if (response.ok) {
          const data = await response.json();
          setTrendingTopics(data);
        }
      } catch {
        // Silently fail, will use fallback topics
      } finally {
        setIsLoadingTopics(false);
      }
    };

    fetchTrendingTopics();
  }, []);

  // Handle escape key for mobile
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isMobileOpen && onMobileClose) {
        onMobileClose();
      }
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isMobileOpen, onMobileClose]);

  // Prevent body scroll when mobile drawer is open
  useEffect(() => {
    if (isMobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isMobileOpen]);

  return (
    <>
      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="filter-drawer-overlay"
          onClick={onMobileClose}
          aria-hidden="true"
        />
      )}

      <aside className={`explore-sidebar ${isMobileOpen ? "explore-sidebar--mobile-open" : ""}`}>
        {/* Mobile Header with Close */}
        <div className="sidebar-header">
          <div>
            <h2 className="text-lg font-semibold sidebar-header__title">
              Filters
            </h2>
            <span className="text-sm text-muted">
              {filteredPapers !== undefined && filteredPapers !== totalPapers ? (
                <>
                  <strong>{filteredPapers.toLocaleString()}</strong> of {totalPapers.toLocaleString()} papers
                </>
              ) : (
                <>{totalPapers.toLocaleString()} papers</>
              )}
            </span>
          </div>
          {onMobileClose && (
            <button
              className="sidebar-close"
              onClick={onMobileClose}
              aria-label="Close filters"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          )}
        </div>

      {/* Quick Filters */}
      <div className="filter-section">
        <h3 className="filter-section__title">Quick Filters</h3>
        <div className="filter-list">
          <button
            className={`filter-item ${filters.hasCode ? "filter-item--active" : ""}`}
            onClick={() => onFilterChange("hasCode", !filters.hasCode)}
          >
            <span className="filter-item__checkbox">
              {filters.hasCode && (
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              )}
            </span>
            <span>Has Code</span>
          </button>

          <button
            className={`filter-item ${filters.highImpact ? "filter-item--active" : ""}`}
            onClick={() => onFilterChange("highImpact", !filters.highImpact)}
          >
            <span className="filter-item__checkbox">
              {filters.highImpact && (
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              )}
            </span>
            <span>High Impact (7+)</span>
          </button>
        </div>
      </div>

      {/* Category Filter */}
      <div className="filter-section">
        <h3 className="filter-section__title">
          Category
          {filters.category && (
            <button
              className="filter-section__clear"
              onClick={() => onFilterChange("category", null)}
            >
              Clear
            </button>
          )}
        </h3>
        <div className="filter-list">
          {categories.map((cat) => (
            <button
              key={cat.value}
              className={`filter-item ${filters.category === cat.value ? "filter-item--active" : ""}`}
              onClick={() => onFilterChange("category", filters.category === cat.value ? null : cat.value)}
            >
              <span className="filter-item__checkbox">
                {filters.category === cat.value && (
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                )}
              </span>
              <span>{cat.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Difficulty Filter */}
      <div className="filter-section">
        <h3 className="filter-section__title">
          Difficulty
          {filters.difficulty && (
            <button
              className="filter-section__clear"
              onClick={() => onFilterChange("difficulty", null)}
            >
              Clear
            </button>
          )}
        </h3>
        <div className="filter-chips">
          {difficulties.map((diff) => (
            <button
              key={diff.value}
              className={`chip ${filters.difficulty === diff.value ? "chip-active" : ""}`}
              onClick={() => onFilterChange("difficulty", filters.difficulty === diff.value ? null : diff.value)}
            >
              {diff.label}
            </button>
          ))}
        </div>
      </div>

      {/* Time Range Filter */}
      <div className="filter-section">
        <h3 className="filter-section__title">
          Time Range
          {filters.timeRange && (
            <button
              className="filter-section__clear"
              onClick={() => onFilterChange("timeRange", null)}
            >
              Clear
            </button>
          )}
        </h3>
        <div className="filter-chips">
          {timeRanges.map((range) => (
            <button
              key={range.value}
              className={`chip ${filters.timeRange === range.value ? "chip-active" : ""}`}
              onClick={() => onFilterChange("timeRange", filters.timeRange === range.value ? null : range.value)}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Trending Section */}
      <div className="filter-section">
        <h3 className="filter-section__title">
          Trending Topics
          {!isLoadingTopics && trendingTopics.length > 0 && (
            <span className="filter-section__badge">Live</span>
          )}
        </h3>
        <div className="filter-chips">
          {isLoadingTopics ? (
            // Loading skeleton
            <>
              <span className="chip chip-skeleton" />
              <span className="chip chip-skeleton" />
              <span className="chip chip-skeleton" />
            </>
          ) : trendingTopics.length > 0 ? (
            // Dynamic topics from API
            trendingTopics.map((topic) => (
              <button
                key={topic.id}
                className="chip chip-clickable"
                onClick={() => onTopicClick?.(topic.name)}
                title={`${topic.recent_papers} recent papers • ${topic.growth_percentage > 0 ? '+' : ''}${topic.growth_percentage.toFixed(0)}% growth`}
              >
                {topic.name}
                {topic.growth_percentage > 20 && (
                  <span className="chip-trend">↑</span>
                )}
              </button>
            ))
          ) : (
            // Fallback static topics
            fallbackTopics.map((topic) => (
              <button
                key={topic}
                className="chip chip-clickable"
                onClick={() => onTopicClick?.(topic)}
              >
                {topic}
              </button>
            ))
          )}
        </div>
      </div>

        {/* Stats Footer */}
        <div className="sidebar-footer">
          {filteredPapers !== undefined && filteredPapers !== totalPapers ? (
            <>
              <div className="sidebar-footer__row">
                <span className="text-xs text-muted">Showing</span>
                <span className="text-xs font-medium">{filteredPapers.toLocaleString()}</span>
              </div>
              <div className="sidebar-footer__row">
                <span className="text-xs text-muted">Total indexed</span>
                <span className="text-xs font-medium">{totalPapers.toLocaleString()}</span>
              </div>
            </>
          ) : (
            <>
              <div className="sidebar-footer__row">
                <span className="text-xs text-muted">Papers indexed</span>
                <span className="text-xs font-medium">{totalPapers.toLocaleString()}</span>
              </div>
              <div className="sidebar-footer__row">
                <span className="text-xs text-muted">Updated</span>
                <span className="text-xs font-medium">Just now</span>
              </div>
            </>
          )}
        </div>
      </aside>
    </>
  );
}
