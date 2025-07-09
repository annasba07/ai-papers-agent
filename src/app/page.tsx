'use client';
import ContextualSearch from '@/components/ContextualSearch';
import PaperList from '@/components/PaperList';
import { Paper } from '@/types/Paper';
import { useState, useEffect } from 'react';

export default function Home() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterDays] = useState('7');
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchPapers = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          days: filterDays,
          category: filterCategory,
          query: searchQuery,
        });
        const response = await fetch(`${API_BASE_URL}/papers?${params.toString()}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: Paper[] = await response.json();
        setPapers(data);
      } catch (error) {
        console.error("Failed to fetch papers:", error);
        setPapers([]);
      } finally {
        setLoading(false);
      }
    };

    const handler = setTimeout(() => {
      fetchPapers();
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [filterDays, filterCategory, searchQuery, API_BASE_URL]);

  return (
    <main className="container">
      <header style={{ textAlign: 'center', margin: '48px 0' }}>
        <h1>AI Paper Digest</h1>
        <p style={{ fontSize: '20px', color: 'var(--secondary-text)' }}>Your intelligent guide to the latest in AI research.</p>
      </header>

      <div className="card" style={{ marginBottom: '32px' }}>
        <ContextualSearch />
      </div>

      <section>
        <h2>Discover Papers</h2>
        <div style={{ display: 'flex', gap: '16px', marginBottom: '32px' }}>
          <input
            type="text"
            placeholder="Filter by keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="form-control"
            style={{ flexGrow: 1 }}
          />
          <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)} className="form-control">
            <option value="all">All Categories</option>
            <option value="cs.AI">Artificial Intelligence</option>
            <option value="cs.LG">Machine Learning</option>
            <option value="cs.CV">Computer Vision</option>
            <option value="cs.CL">Computation and Language</option>
          </select>
        </div>

        {loading ? (
          <p style={{ textAlign: 'center' }}>Loading papers...</p>
        ) : papers.length > 0 ? (
          <PaperList papers={papers} />
        ) : (
          <p style={{ textAlign: 'center' }}>No papers found for the selected criteria.</p>
        )}
      </section>
    </main>
  );
}
