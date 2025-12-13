"use client";

import { useState, useEffect, useCallback } from "react";
import PaperCard from "@/components/explore/PaperCard";
import FilterSidebar from "@/components/explore/FilterSidebar";
import ResearchAdvisor from "@/components/explore/ResearchAdvisor";
import TrendingWidget from "@/components/explore/TrendingWidget";
import type { ExplorePaper, ExploreFilters } from "@/types/Explore";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export default function ExplorePage() {
  const [papers, setPapers] = useState<ExplorePaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalPapers, setTotalPapers] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [advisorOpen, setAdvisorOpen] = useState(false);
  const [expandedPaperId, setExpandedPaperId] = useState<string | null>(null);

  const [filters, setFilters] = useState<ExploreFilters>({
    hasCode: false,
    highImpact: false,
    difficulty: null,
    category: null,
    sortBy: "recent",
  });

  const fetchPapers = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        limit: "30",
        order_by: filters.sortBy === "recent" ? "published_date" :
                  filters.sortBy === "citations" ? "citation_count" : "published_date",
        order_dir: "desc",
      });

      if (searchQuery) {
        params.append("query", searchQuery);
      }
      if (filters.category) {
        params.append("category", filters.category);
      }
      if (filters.hasCode) {
        params.append("has_deep_analysis", "true");
        params.append("min_reproducibility", "6");
      }
      if (filters.highImpact) {
        params.append("has_deep_analysis", "true");
        params.append("min_impact_score", "7");
      }
      if (filters.difficulty) {
        params.append("difficulty_level", filters.difficulty);
      }

      const endpoint = API_BASE
        ? `${API_BASE}/atlas-db/papers?${params.toString()}`
        : `/api/atlas/papers?${params.toString()}`;

      const response = await fetch(endpoint);

      if (!response.ok) {
        throw new Error(`Failed to fetch papers: ${response.status}`);
      }

      const data = await response.json();

      // Handle both response formats
      const paperList = Array.isArray(data) ? data : data.papers || [];
      setPapers(paperList);
      setTotalPapers(data.total || paperList.length);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load papers");
      setPapers([]);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, filters]);

  useEffect(() => {
    const debounce = setTimeout(fetchPapers, 300);
    return () => clearTimeout(debounce);
  }, [fetchPapers]);

  const handleFilterChange = (key: keyof ExploreFilters, value: unknown) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
  };

  const togglePaperExpand = (paperId: string) => {
    setExpandedPaperId(prev => prev === paperId ? null : paperId);
  };

  return (
    <div className="explore-page">
      <FilterSidebar
        filters={filters}
        onFilterChange={handleFilterChange}
        totalPapers={totalPapers}
      />

      <main className="explore-main">
        {/* Search Bar */}
        <form className="explore-search" onSubmit={handleSearch}>
          <input
            type="text"
            className="input explore-search__input"
            placeholder="Search papers by title, abstract, or concept..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button
            type="button"
            className="advisor-trigger"
            onClick={() => setAdvisorOpen(true)}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            Ask Advisor
          </button>
        </form>

        {/* Active Filters */}
        {(filters.hasCode || filters.highImpact || filters.difficulty || filters.category) && (
          <div className="explore-active-filters">
            {filters.hasCode && (
              <span className="chip chip-active">
                Has Code
                <button onClick={() => handleFilterChange("hasCode", false)}>&times;</button>
              </span>
            )}
            {filters.highImpact && (
              <span className="chip chip-active">
                High Impact
                <button onClick={() => handleFilterChange("highImpact", false)}>&times;</button>
              </span>
            )}
            {filters.difficulty && (
              <span className="chip chip-active">
                {filters.difficulty}
                <button onClick={() => handleFilterChange("difficulty", null)}>&times;</button>
              </span>
            )}
            {filters.category && (
              <span className="chip chip-active">
                {filters.category}
                <button onClick={() => handleFilterChange("category", null)}>&times;</button>
              </span>
            )}
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setFilters({
                hasCode: false,
                highImpact: false,
                difficulty: null,
                category: null,
                sortBy: "recent",
              })}
            >
              Clear all
            </button>
          </div>
        )}

        {/* Results Info */}
        <div className="explore-results-info">
          <span className="text-secondary text-sm">
            {loading ? "Loading..." : `${totalPapers.toLocaleString()} papers`}
          </span>
          <select
            className="input select"
            style={{ width: "auto" }}
            value={filters.sortBy}
            onChange={(e) => handleFilterChange("sortBy", e.target.value)}
          >
            <option value="recent">Most Recent</option>
            <option value="citations">Most Cited</option>
            <option value="impact">Highest Impact</option>
          </select>
        </div>

        {/* Paper Feed */}
        <div className="explore-feed">
          {loading && papers.length === 0 ? (
            <div className="loading-state">
              <div className="spinner" />
              <span className="loading-state__text">Loading papers...</span>
            </div>
          ) : error ? (
            <div className="empty-state">
              <div className="empty-state__icon">!</div>
              <h3 className="empty-state__title">Something went wrong</h3>
              <p className="empty-state__description">{error}</p>
              <button className="btn btn-primary" onClick={fetchPapers}>
                Try again
              </button>
            </div>
          ) : papers.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state__icon">🔍</div>
              <h3 className="empty-state__title">No papers found</h3>
              <p className="empty-state__description">
                Try adjusting your filters or search query
              </p>
            </div>
          ) : (
            papers.map((paper) => (
              <PaperCard
                key={paper.id}
                paper={paper}
                isExpanded={expandedPaperId === paper.id}
                onToggleExpand={() => togglePaperExpand(paper.id)}
              />
            ))
          )}
        </div>

        {/* Bottom Widgets */}
        <div className="widget-grid">
          <TrendingWidget />
        </div>
      </main>

      {/* Research Advisor Overlay */}
      <ResearchAdvisor
        isOpen={advisorOpen}
        onClose={() => setAdvisorOpen(false)}
      />
    </div>
  );
}
