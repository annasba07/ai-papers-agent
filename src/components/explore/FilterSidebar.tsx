"use client";

import type { ExploreFilters } from "@/types/Explore";

interface FilterSidebarProps {
  filters: ExploreFilters;
  onFilterChange: (key: keyof ExploreFilters, value: unknown) => void;
  totalPapers: number;
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

export default function FilterSidebar({
  filters,
  onFilterChange,
  totalPapers,
}: FilterSidebarProps) {
  return (
    <aside className="explore-sidebar">
      <div className="sidebar-header" style={{ marginBottom: "1.5rem" }}>
        <h2 className="text-lg font-semibold" style={{ marginBottom: "0.25rem" }}>
          Filters
        </h2>
        <span className="text-sm text-muted">
          {totalPapers.toLocaleString()} papers
        </span>
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
              className="text-xs text-accent"
              onClick={() => onFilterChange("category", null)}
              style={{ background: "none", border: "none", cursor: "pointer" }}
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
              className="text-xs text-accent"
              onClick={() => onFilterChange("difficulty", null)}
              style={{ background: "none", border: "none", cursor: "pointer" }}
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

      {/* Trending Section */}
      <div className="filter-section">
        <h3 className="filter-section__title">Trending Topics</h3>
        <div className="filter-chips">
          <span className="chip">LLM Agents</span>
          <span className="chip">Mixture of Experts</span>
          <span className="chip">RLHF</span>
          <span className="chip">Diffusion</span>
          <span className="chip">RAG</span>
        </div>
      </div>

      {/* Stats Footer */}
      <div className="sidebar-footer" style={{ marginTop: "auto", paddingTop: "1.5rem", borderTop: "1px solid var(--color-border)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
          <span className="text-xs text-muted">Papers indexed</span>
          <span className="text-xs font-medium">{totalPapers.toLocaleString()}</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span className="text-xs text-muted">Updated</span>
          <span className="text-xs font-medium">Just now</span>
        </div>
      </div>
    </aside>
  );
}
