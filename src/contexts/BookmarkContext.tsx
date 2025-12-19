"use client";

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";

const STORAGE_KEY = "paper-atlas-bookmarks";

interface BookmarkContextType {
  bookmarkedIds: Set<string>;
  isBookmarked: (paperId: string) => boolean;
  toggleBookmark: (paperId: string) => void;
  bookmarkCount: number;
}

const BookmarkContext = createContext<BookmarkContextType | undefined>(undefined);

export function BookmarkProvider({ children }: { children: ReactNode }) {
  const [bookmarkedIds, setBookmarkedIds] = useState<Set<string>>(new Set());
  const [isInitialized, setIsInitialized] = useState(false);

  // Load bookmarks from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const ids = JSON.parse(stored) as string[];
        setBookmarkedIds(new Set(ids));
      }
    } catch {
      // Silently fail if localStorage is unavailable
    }
    setIsInitialized(true);
  }, []);

  // Save bookmarks to localStorage whenever they change
  useEffect(() => {
    if (isInitialized) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(bookmarkedIds)));
      } catch {
        // Silently fail if localStorage is unavailable
      }
    }
  }, [bookmarkedIds, isInitialized]);

  const isBookmarked = useCallback(
    (paperId: string) => bookmarkedIds.has(paperId),
    [bookmarkedIds]
  );

  const toggleBookmark = useCallback((paperId: string) => {
    setBookmarkedIds((prev) => {
      const next = new Set(prev);
      if (next.has(paperId)) {
        next.delete(paperId);
      } else {
        next.add(paperId);
      }
      return next;
    });
  }, []);

  return (
    <BookmarkContext.Provider
      value={{
        bookmarkedIds,
        isBookmarked,
        toggleBookmark,
        bookmarkCount: bookmarkedIds.size,
      }}
    >
      {children}
    </BookmarkContext.Provider>
  );
}

export function useBookmarks() {
  const context = useContext(BookmarkContext);
  if (context === undefined) {
    throw new Error("useBookmarks must be used within a BookmarkProvider");
  }
  return context;
}
