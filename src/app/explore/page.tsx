"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import PaperCard from "@/components/explore/PaperCard";
import PaperCardSkeleton from "@/components/explore/PaperCardSkeleton";
import FilterSidebar from "@/components/explore/FilterSidebar";
import ResearchAdvisor from "@/components/explore/ResearchAdvisor";
import TrendingWidget from "@/components/explore/TrendingWidget";
import type { ExplorePaper, ExploreFilters } from "@/types/Explore";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

interface HybridSearchResult {
  semanticResults: ExplorePaper[];
  keywordResults: ExplorePaper[];
  totalSemantic: number;
  totalKeyword: number;
  timing: {
    semantic_ms: number;
    keyword_ms: number;
    total_ms: number;
  };
  searchMode: 'hybrid' | 'keyword_only' | 'semantic_only';
}

export default function ExplorePage() {
  const [papers, setPapers] = useState<ExplorePaper[]>([]);
  const [semanticPapers, setSemanticPapers] = useState<ExplorePaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [semanticLoading, setSemanticLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalPapers, setTotalPapers] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [advisorOpen, setAdvisorOpen] = useState(false);
  const [expandedPaperId, setExpandedPaperId] = useState<string | null>(null);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const [searchTiming, setSearchTiming] = useState<{ semantic_ms: number; total_ms: number } | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const isLoadingMore = useRef(false);

  const [filters, setFilters] = useState<ExploreFilters>({
    hasCode: false,
    highImpact: false,
    difficulty: null,
    category: null,
    sortBy: "recent",
  });

  const ITEMS_PER_PAGE = 30;

  // Fetch papers using hybrid search when there's a query
  const fetchPapers = useCallback(async (loadMore = false, overrideOffset?: number) => {
    if (loadMore && isLoadingMore.current) return;
    if (loadMore) isLoadingMore.current = true;

    const currentOffset = typeof overrideOffset === 'number' ? overrideOffset : (loadMore ? offset : 0);

    if (!loadMore) {
      setLoading(true);
      setSemanticLoading(!!searchQuery);
      setError(null);
      setSemanticPapers([]);
      setSearchTiming(null);
    }

    try {
      // Build params
      const params = new URLSearchParams({
        limit: String(ITEMS_PER_PAGE),
      });

      if (searchQuery) {
        params.append("query", searchQuery);
      }
      if (filters.category) {
        params.append("category", filters.category);
      }
      if (filters.hasCode) {
        params.append("has_code", "true");
      }
      if (filters.highImpact) {
        params.append("has_deep_analysis", "true");
        params.append("min_impact_score", "7");
      }
      if (filters.difficulty) {
        params.append("difficulty_level", filters.difficulty);
      }

      // Use hybrid search API when there's a query, otherwise use keyword-only
      if (searchQuery) {
        const response = await fetch(`/api/search/hybrid?${params.toString()}`);

        if (!response.ok) {
          throw new Error(`Search failed: ${response.status}`);
        }

        const data: HybridSearchResult = await response.json();

        // Set semantic results (AI-powered)
        setSemanticPapers(data.semanticResults || []);
        setSemanticLoading(false);

        // Set keyword results
        if (loadMore) {
          setPapers(prev => [...prev, ...data.keywordResults]);
        } else {
          setPapers(data.keywordResults || []);
        }

        setTotalPapers(data.totalKeyword + data.totalSemantic);
        setSearchTiming({
          semantic_ms: data.timing.semantic_ms,
          total_ms: data.timing.total_ms,
        });

        // For hybrid search, we don't paginate (semantic has limited results)
        setHasMore(false);
      } else {
        // No query - use standard keyword search with pagination
        const paginatedParams = new URLSearchParams(params);
        paginatedParams.set("offset", String(currentOffset));
        paginatedParams.set("order_by", filters.sortBy === "recent" ? "published_date" :
          filters.sortBy === "citations" ? "citation_count" : "published_date");
        paginatedParams.set("order_dir", "desc");

        const endpoint = API_BASE
          ? `${API_BASE}/atlas-db/papers?${paginatedParams.toString()}`
          : `/api/atlas/papers?${paginatedParams.toString()}`;

        const response = await fetch(endpoint);

        if (!response.ok) {
          throw new Error(`Failed to fetch papers: ${response.status}`);
        }

        const data = await response.json();
        const paperList = Array.isArray(data) ? data : data.papers || [];

        if (loadMore) {
          setPapers(prev => [...prev, ...paperList]);
        } else {
          setPapers(paperList);
        }

        setTotalPapers(data.total || paperList.length);
        setHasMore(data.has_more !== false && paperList.length === ITEMS_PER_PAGE);
        setOffset(currentOffset + paperList.length);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load papers");
      if (!loadMore) {
        setPapers([]);
        setSemanticPapers([]);
      }
    } finally {
      setLoading(false);
      setSemanticLoading(false);
      isLoadingMore.current = false;
    }
  }, [searchQuery, filters]);

  // Reset and fetch when search/filters change
  useEffect(() => {
    setOffset(0);
    setHasMore(true);
    const debounce = setTimeout(() => fetchPapers(false, 0), 300);
    return () => clearTimeout(debounce);
  }, [searchQuery, filters, fetchPapers]);

  // Infinite scroll observer
  useEffect(() => {
    if (!loadMoreRef.current || !hasMore || loading || searchQuery) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading && !isLoadingMore.current) {
          fetchPapers(true);
        }
      },
      { threshold: 0.1 }
    );

    observer.observe(loadMoreRef.current);
    return () => observer.disconnect();
  }, [hasMore, loading, searchQuery, fetchPapers]);

  const handleFilterChange = (key: keyof ExploreFilters, value: unknown) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
  };

  const togglePaperExpand = (paperId: string) => {
    setExpandedPaperId(prev => prev === paperId ? null : paperId);
  };

  const hasSemanticResults = semanticPapers.length > 0;
  const hasKeywordResults = papers.length > 0;
  const totalResults = semanticPapers.length + papers.length;

  // Starter prompts for inline advisor intro - diverse, accessible examples
  const STARTER_PROMPTS = [
    "How to make AI explain its decisions",
    "Speed up neural network training",
    "AI for medical image diagnosis",
    "Build more accurate chatbots",
  ];

  const handleStarterPromptClick = (prompt: string) => {
    setSearchQuery(prompt);
    setAdvisorOpen(true);
  };

  return (
    <div className="explore-page">
      <FilterSidebar
        filters={filters}
        onFilterChange={handleFilterChange}
        totalPapers={totalPapers}
        isMobileOpen={mobileFiltersOpen}
        onMobileClose={() => setMobileFiltersOpen(false)}
      />

      <main className="explore-main">
        {/* Page Header */}
        <header className="explore-header">
          <h1 className="explore-header__title">Explore</h1>
          <p className="explore-header__subtitle">
            Search and filter AI research papers by topic, code availability, and impact
          </p>
        </header>

        {/* Search Bar */}
        <form className="explore-search" onSubmit={handleSearch}>
          {/* Mobile Filter Toggle */}
          <button
            type="button"
            className="mobile-filter-toggle"
            onClick={() => setMobileFiltersOpen(true)}
            aria-label="Open filters"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
            </svg>
            <span className="mobile-filter-toggle__count">
              {[filters.hasCode, filters.highImpact, filters.category, filters.difficulty].filter(Boolean).length || ""}
            </span>
          </button>

          <input
            type="text"
            className="input explore-search__input"
            placeholder="Describe what you're researching (e.g., 'efficient attention for mobile deployment')..."
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
            {loading ? "Searching..." : (
              searchQuery
                ? (
                  <>
                    <span className="results-breakdown">
                      <strong>{totalResults} results</strong>
                      {hasSemanticResults && hasKeywordResults && (
                        <span className="results-breakdown__detail">
                          ({semanticPapers.length} AI-matched + {papers.length} keyword)
                        </span>
                      )}
                      {searchTiming && (
                        <span className="results-breakdown__timing">
                          {Math.round(searchTiming.total_ms)}ms
                        </span>
                      )}
                    </span>
                  </>
                )
                : `${totalPapers.toLocaleString()} papers`
            )}
          </span>
          {!searchQuery && (
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
          )}
        </div>

        {/* Research Advisor Hero - Show when no search query */}
        {!searchQuery && !loading && (
          <div className="advisor-hero">
            <div className="advisor-hero__content">
              <div className="advisor-hero__icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </div>
              <div className="advisor-hero__text">
                <h2 className="advisor-hero__title">
                  Not sure where to start?
                </h2>
                <p className="advisor-hero__description">
                  Tell me what you're working on and I'll find the most relevant papers, techniques, and implementations.
                </p>
              </div>
              <button
                className="advisor-hero__cta"
                onClick={() => setAdvisorOpen(true)}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                Ask Research Advisor
              </button>
            </div>
            <div className="advisor-hero__prompts">
              <span className="advisor-hero__prompts-label">Try asking:</span>
              <div className="advisor-hero__prompt-chips">
                {STARTER_PROMPTS.map((prompt, i) => (
                  <button
                    key={i}
                    className="advisor-hero__prompt-chip"
                    onClick={() => handleStarterPromptClick(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Paper Feed */}
        <div className="explore-feed">
          {loading && papers.length === 0 && semanticPapers.length === 0 ? (
            <>
              {searchQuery && (
                <div className="search-mode-indicator">
                  <div className="search-mode-indicator__icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <path d="M12 6v6l4 2" />
                    </svg>
                  </div>
                  <span>AI-powered semantic search in progress...</span>
                </div>
              )}
              {[...Array(6)].map((_, i) => (
                <PaperCardSkeleton key={i} />
              ))}
            </>
          ) : error ? (
            <div className="empty-state">
              <div className="empty-state__icon">!</div>
              <h3 className="empty-state__title">Something went wrong</h3>
              <p className="empty-state__description">{error}</p>
              <button className="btn btn-primary" onClick={() => fetchPapers(false)}>
                Try again
              </button>
            </div>
          ) : totalResults === 0 ? (
            <div className="empty-state">
              <div className="empty-state__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.35-4.35" />
                </svg>
              </div>
              <h3 className="empty-state__title">No papers found</h3>
              <p className="empty-state__description">
                {searchQuery
                  ? "Try different keywords or describe your research goal in more detail."
                  : "Try adjusting your filters."
                }
              </p>
              {searchQuery && (
                <button
                  className="btn btn-primary"
                  onClick={() => setAdvisorOpen(true)}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '8px' }}>
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                  Ask Research Advisor
                </button>
              )}
            </div>
          ) : (
            <>
              {/* Smart Results Section (Semantic) */}
              {searchQuery && (semanticLoading || hasSemanticResults) && (
                <div className="smart-results-section">
                  <div className="section-header">
                    <div className="section-header__title">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5z" />
                        <path d="M2 17l10 5 10-5" />
                        <path d="M2 12l10 5 10-5" />
                      </svg>
                      <span>Smart Results</span>
                      <span className="badge badge-ai">AI-Powered</span>
                    </div>
                    {searchTiming && (
                      <span className="section-header__timing">
                        {Math.round(searchTiming.semantic_ms)}ms
                      </span>
                    )}
                  </div>

                  {semanticLoading ? (
                    <div className="smart-results-loading">
                      <PaperCardSkeleton />
                      <PaperCardSkeleton />
                    </div>
                  ) : hasSemanticResults ? (
                    <div className="smart-results-grid">
                      {semanticPapers.map((paper) => (
                        <PaperCard
                          key={`semantic-${paper.id}`}
                          paper={paper}
                          isExpanded={expandedPaperId === paper.id}
                          onToggleExpand={() => togglePaperExpand(paper.id)}
                          variant="semantic"
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="smart-results-empty">
                      <p>No semantic matches found. Try the Research Advisor for better results.</p>
                    </div>
                  )}
                </div>
              )}

              {/* Keyword Results Section */}
              {hasKeywordResults && (
                <div className="keyword-results-section">
                  {searchQuery && (
                    <div className="section-header section-header--keyword">
                      <div className="section-header__title">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="11" cy="11" r="8" />
                          <path d="m21 21-4.35-4.35" />
                        </svg>
                        <span>{hasSemanticResults ? "More Results" : "All Results"}</span>
                        <span className="badge badge-keyword">Keyword Match</span>
                        <span className="section-header__count">{papers.length} papers</span>
                      </div>
                      {searchTiming && (
                        <span className="section-header__timing">
                          {Math.round(searchTiming.keyword_ms || 0)}ms
                        </span>
                      )}
                    </div>
                  )}

                  {papers.map((paper) => (
                    <PaperCard
                      key={paper.id}
                      paper={paper}
                      isExpanded={expandedPaperId === paper.id}
                      onToggleExpand={() => togglePaperExpand(paper.id)}
                    />
                  ))}

                  {/* Load More trigger for infinite scroll */}
                  {!searchQuery && hasMore && (
                    <div ref={loadMoreRef} className="load-more-trigger">
                      {isLoadingMore.current && (
                        <div className="load-more-spinner">
                          <PaperCardSkeleton />
                          <PaperCardSkeleton />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </>
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
