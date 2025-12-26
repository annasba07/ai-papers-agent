"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useBookmarks } from "@/contexts/BookmarkContext";
import PaperCard from "@/components/explore/PaperCard";
import PaperCardSkeleton from "@/components/explore/PaperCardSkeleton";
import type { ExplorePaper } from "@/types/Explore";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export default function ReadingListPage() {
  const { bookmarkedIds, bookmarkCount } = useBookmarks();
  const [papers, setPapers] = useState<ExplorePaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedPaperId, setExpandedPaperId] = useState<string | null>(null);

  const fetchBookmarkedPapers = useCallback(async () => {
    if (bookmarkedIds.size === 0) {
      setPapers([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Fetch papers individually (could be optimized with batch endpoint)
      const paperPromises = Array.from(bookmarkedIds).map(async (paperId) => {
        try {
          const endpoint = API_BASE
            ? `${API_BASE}/atlas-db/papers/${paperId}`
            : `/api/atlas/papers/${paperId}`;

          const response = await fetch(endpoint, { cache: 'no-store' });
          if (!response.ok) {
            console.warn(`Failed to fetch paper ${paperId}`);
            return null;
          }
          return await response.json();
        } catch {
          console.warn(`Error fetching paper ${paperId}`);
          return null;
        }
      });

      const results = await Promise.all(paperPromises);
      const validPapers = results.filter((p): p is ExplorePaper => p !== null);
      setPapers(validPapers);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load papers");
    } finally {
      setLoading(false);
    }
  }, [bookmarkedIds]);

  useEffect(() => {
    fetchBookmarkedPapers();
  }, [fetchBookmarkedPapers]);

  const togglePaperExpand = (paperId: string) => {
    setExpandedPaperId((prev) => (prev === paperId ? null : paperId));
  };

  return (
    <div className="reading-list-page">
      <main className="reading-list-main">
        {/* Page Header */}
        <header className="reading-list-header">
          <h1 className="reading-list-header__title">Reading List</h1>
          <p className="reading-list-header__subtitle">
            Papers you've saved for later. Your reading list is stored locally in your browser.
          </p>
          {bookmarkCount > 0 && (
            <span className="reading-list-header__count">
              {bookmarkCount} {bookmarkCount === 1 ? "paper" : "papers"} saved
            </span>
          )}
        </header>

        {/* Paper List */}
        <div className="reading-list-feed">
          {loading ? (
            <>
              {[...Array(Math.min(bookmarkCount || 3, 6))].map((_, i) => (
                <PaperCardSkeleton key={i} />
              ))}
            </>
          ) : error ? (
            <div className="empty-state">
              <div className="empty-state__icon">!</div>
              <h3 className="empty-state__title">Something went wrong</h3>
              <p className="empty-state__description">{error}</p>
              <button
                className="btn btn-primary"
                onClick={() => fetchBookmarkedPapers()}
              >
                Try again
              </button>
            </div>
          ) : papers.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state__icon">
                <svg
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <h3 className="empty-state__title">No papers saved yet</h3>
              <p className="empty-state__description">
                Bookmark papers from the Explore page to build your reading list. Click the bookmark icon on any paper card to save it for later.
              </p>
              <Link href="/explore" className="btn btn-primary">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  style={{ marginRight: "8px" }}
                >
                  <circle cx="12" cy="12" r="10" />
                  <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
                </svg>
                Explore Papers
              </Link>
            </div>
          ) : (
            <>
              {papers.map((paper) => (
                <PaperCard
                  key={paper.id}
                  paper={paper}
                  isExpanded={expandedPaperId === paper.id}
                  onToggleExpand={() => togglePaperExpand(paper.id)}
                />
              ))}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
