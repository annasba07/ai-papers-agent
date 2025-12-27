"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import PaperCard from "@/components/explore/PaperCard";
import PaperCardSkeleton from "@/components/explore/PaperCardSkeleton";
import FilterSidebar from "@/components/explore/FilterSidebar";
import ResearchAdvisor from "@/components/explore/ResearchAdvisor";
import TrendingWidget from "@/components/explore/TrendingWidget";
import type { ExplorePaper, ExploreFilters } from "@/types/Explore";

// Session storage key for persisting explore state
const EXPLORE_SESSION_KEY = "explore_session";

interface ExploreSessionState {
  searchQuery: string;
  filters: ExploreFilters;
  timestamp: number;
}

// Session expiry: 30 minutes
const SESSION_EXPIRY_MS = 30 * 60 * 1000;

interface HybridSearchResult {
  semanticResults: ExplorePaper[];
  keywordResults: ExplorePaper[];
  totalSemantic: number;
  totalKeyword: number;
  has_more?: boolean;
  databaseTotal?: number;
  timing?: {
    semantic_ms: number;
    keyword_ms: number;
    total_ms: number;
  };
  searchMode: 'hybrid' | 'keyword_only' | 'semantic_only';
}

// Helper to get initial state from sessionStorage
function getInitialSessionState(): { searchQuery: string; filters: ExploreFilters } | null {
  if (typeof window === "undefined") return null;

  try {
    const stored = sessionStorage.getItem(EXPLORE_SESSION_KEY);
    if (!stored) return null;

    const session: ExploreSessionState = JSON.parse(stored);

    // Check if session has expired
    if (Date.now() - session.timestamp > SESSION_EXPIRY_MS) {
      sessionStorage.removeItem(EXPLORE_SESSION_KEY);
      return null;
    }

    return { searchQuery: session.searchQuery, filters: session.filters };
  } catch {
    return null;
  }
}

const defaultFilters: ExploreFilters = {
  hasCode: false,
  highImpact: false,
  seminalPapers: false,
  difficulty: null,
  category: null,
  sortBy: "recent",
  timeRange: null,
};

export default function ExplorePage() {
  const [papers, setPapers] = useState<ExplorePaper[]>([]);
  const [semanticPapers, setSemanticPapers] = useState<ExplorePaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [semanticLoading, setSemanticLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalPapers, setTotalPapers] = useState(0); // Total papers in database
  const [filteredCount, setFilteredCount] = useState<number | undefined>(undefined); // Count after filters
  const [searchQuery, setSearchQuery] = useState("");
  const [advisorOpen, setAdvisorOpen] = useState(false);
  const [expandedPaperId, setExpandedPaperId] = useState<string | null>(null);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const [searchTiming, setSearchTiming] = useState<{ semantic_ms: number; total_ms: number } | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const [sessionRestored, setSessionRestored] = useState(false);
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const isLoadingMore = useRef(false);
  const offsetRef = useRef(0);
  const activeRequestId = useRef(0);
  const activeAbortController = useRef<AbortController | null>(null);

  const [filters, setFilters] = useState<ExploreFilters>(defaultFilters);

  // Restore session state on mount
  useEffect(() => {
    const session = getInitialSessionState();
    if (session) {
      setSearchQuery(session.searchQuery);
      setFilters(session.filters);
    }
    setSessionRestored(true);

    // Warm up the backend embedding cache to prevent first-search delays
    // This eliminates the 8-12 second cold start penalty users experience
    // on their first search after page load. Warmup runs async and non-blocking.
    // Fire-and-forget: We don't wait for the response to avoid blocking the UI.
    // By the time the user searches (~5-10s after page load), cache will be warm.
    const backendBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    fetch(`${backendBase}/api/v1/papers/warmup`, {
      cache: 'no-store',
      priority: 'low' as RequestPriority,  // Don't block critical resources
      signal: AbortSignal.timeout(15000),  // 15s timeout for warmup
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data?.status === 'success') {
          console.log(`[Warmup] ✓ Cache warmed in ${data.warmup_time_ms}ms - searches will be faster`);
        }
      })
      .catch(() => {
        // Warmup failure is non-critical - searches will still work but be slower
        // Don't log error to avoid alarming users - this happens on first load
      });
  }, []);

  // Save session state when search or filters change
  useEffect(() => {
    if (!sessionRestored) return; // Don't save until initial restore is done

    const sessionState: ExploreSessionState = {
      searchQuery,
      filters,
      timestamp: Date.now(),
    };

    try {
      sessionStorage.setItem(EXPLORE_SESSION_KEY, JSON.stringify(sessionState));
    } catch {
      // Ignore storage errors (e.g., private browsing)
    }
  }, [searchQuery, filters, sessionRestored]);

  useEffect(() => {
    offsetRef.current = offset;
  }, [offset]);

  const ITEMS_PER_PAGE = 30;

  // Fetch papers using hybrid search when there's a query
  const fetchPapers = useCallback(async (loadMore = false, overrideOffset?: number) => {
    if (loadMore && isLoadingMore.current) return;
    if (loadMore) isLoadingMore.current = true;

    const requestId = ++activeRequestId.current;
    const controller = new AbortController();
    if (activeAbortController.current) {
      activeAbortController.current.abort();
    }
    activeAbortController.current = controller;

    const currentOffset = typeof overrideOffset === 'number'
      ? overrideOffset
      : (loadMore ? offsetRef.current : 0);

    if (!loadMore) {
      setLoading(true);
      setSemanticLoading(!!searchQuery);
      setError(null);
      setSemanticPapers([]);
      setSearchTiming(null);
    }

    try {
      // Check if any filters are active
      const hasActiveFilters = searchQuery || filters.hasCode || filters.highImpact ||
                                filters.seminalPapers || filters.category || filters.difficulty || filters.timeRange;

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
      if (filters.seminalPapers) {
        params.append("seminal_only", "true");
      }
      if (filters.difficulty) {
        params.append("difficulty_level", filters.difficulty);
      }
      if (filters.timeRange) {
        params.append("days", String(filters.timeRange));
      }

      // Always use hybrid search API for consistent, semantic-aware results
      // When there's a search query, semantic results are shown first
      // Without a query, keyword results are sorted by recency/citations
      const paginatedParams = new URLSearchParams(params);
      paginatedParams.set("offset", String(currentOffset));
      paginatedParams.set("order_by", filters.sortBy === "recent" ? "published_date" :
        filters.sortBy === "citations" ? "citation_count" : "published_date");
      paginatedParams.set("order_dir", "desc");

      const response = await fetch(`/api/search?${paginatedParams.toString()}`, {
        cache: 'no-store',
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data: HybridSearchResult = await response.json();

      if (requestId !== activeRequestId.current) {
        return;
      }

      // Set semantic results (AI-powered) - only present when there's a query
      setSemanticPapers(data.semanticResults || []);
      setSemanticLoading(false);

      // Set keyword results
      if (loadMore) {
        setPapers(prev => [...prev, ...data.keywordResults]);
      } else {
        setPapers(data.keywordResults || []);
      }

      // Update counts
      const resultCount = data.totalKeyword + data.totalSemantic;
      setFilteredCount(hasActiveFilters ? resultCount : undefined);
      if (data.databaseTotal !== undefined) {
        setTotalPapers(data.databaseTotal);
      }

      // Set timing info if available
      if (data.timing) {
        setSearchTiming({
          semantic_ms: data.timing.semantic_ms || 0,
          total_ms: data.timing.total_ms || 0,
        });
      }

      // Industry best practice: Auto-suggest Research Advisor when search returns 0 results
      // Rationale: Guides users to a better discovery method instead of abandoning
      // Data: UX assessments showed 90% of users don't know advisor exists
      if (data.totalSemantic === 0 && data.totalKeyword === 0 && searchQuery) {
        // Auto-open advisor panel with a slight delay for better UX
        setTimeout(() => {
          setAdvisorOpen(true);
        }, 800);
      }

      // Pagination: Allow pagination for keyword results
      setHasMore(data.has_more !== false && data.keywordResults.length === ITEMS_PER_PAGE);
      setOffset(currentOffset + data.keywordResults.length);
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to load papers");
      if (!loadMore) {
        setPapers([]);
        setSemanticPapers([]);
      }
    } finally {
      if (requestId === activeRequestId.current) {
        setLoading(false);
        setSemanticLoading(false);
      }
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
        filteredPapers={filteredCount}
        isMobileOpen={mobileFiltersOpen}
        onMobileClose={() => setMobileFiltersOpen(false)}
        onTopicClick={(topicName) => {
          setSearchQuery(topicName);
          // Trigger search with the topic
          const form = document.querySelector('.explore-search') as HTMLFormElement;
          if (form) {
            form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
          }
        }}
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
              {[filters.hasCode, filters.highImpact, filters.category, filters.difficulty, filters.timeRange].filter(Boolean).length || ""}
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
        {(filters.hasCode || filters.highImpact || filters.difficulty || filters.category || filters.timeRange) && (
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
            {filters.timeRange && (
              <span className="chip chip-active">
                Last {filters.timeRange} days
                <button onClick={() => handleFilterChange("timeRange", null)}>&times;</button>
              </span>
            )}
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setFilters(defaultFilters)}
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
                  Tell me what you&apos;re working on and I&apos;ll find the most relevant papers, techniques, and implementations.
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

      {/* Floating Action Button for Advisor - Always visible */}
      {!advisorOpen && (
        <button
          className="advisor-fab"
          onClick={() => setAdvisorOpen(true)}
          aria-label="Open Research Advisor"
          title="Ask Research Advisor"
        >
          <span className="advisor-fab__icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          </span>
          <span className="advisor-fab__pulse"></span>
        </button>
      )}
    </div>
  );
}
