'use client';
import ContextualSearch from '@/components/ContextualSearch';
import PaperList from '@/components/PaperList';
import AtlasOverview from '@/components/AtlasOverview';
import { Paper } from '@/types/Paper';
import { useState, useEffect, useMemo } from 'react';

export default function Home() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterDays] = useState('7');
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const apiBaseUrl = useMemo(() => process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000', []);

  useEffect(() => {
    const fetchPapers = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          days: filterDays,
          category: filterCategory,
          query: searchQuery,
        });
        const response = await fetch(`${apiBaseUrl}/papers?${params.toString()}`);
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
  }, [filterDays, filterCategory, searchQuery, apiBaseUrl]);

  return (
    <main className="container" style={{ paddingTop: '64px', paddingBottom: '64px' }}>
      <header style={{ textAlign: 'center', margin: '0 0 56px 0' }}>
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          padding: '8px 16px',
          borderRadius: '999px',
          background: 'rgba(99, 102, 241, 0.12)',
          color: 'var(--accent-indigo)',
          fontWeight: 600,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          marginBottom: '18px'
        }}>
          Living Research Atlas
        </span>
        <h1 style={{ fontSize: '42px', fontWeight: 700, marginBottom: '16px', color: '#f8fafc' }}>
          See where AI research is moving—and act on it fast.
        </h1>
        <p style={{ fontSize: '20px', color: 'var(--secondary-text)', maxWidth: '760px', margin: '0 auto 32px' }}>
          Discover breakout areas, analyse the leading papers, and bootstrap implementation plans with a single toolkit designed for research teams.
        </p>
        <div style={{ display: 'inline-flex', gap: '14px' }}>
          <a href="#roadmap" className="btn btn-primary">Explore Atlas</a>
          <a href="#contextual-search" className="btn btn-secondary">Ask the Assistant</a>
        </div>
      </header>

      <section id="roadmap" style={{ display: 'grid', gap: '24px', marginBottom: '48px' }}>
        <div className="card" style={{ display: 'grid', gap: '16px' }}>
          <h2 style={{ marginBottom: '8px' }}>Your Research Playbook</h2>
          <div style={{ display: 'grid', gap: '18px', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
            <StepCard
              step="1"
              title="Explore the landscape"
              description="Track where research velocity is accelerating across categories, benchmarks, and authors."
            />
            <StepCard
              step="2"
              title="Find the right papers"
              description="Drill into the topics with the most momentum. Inspect abstracts, code links, or trends in a click."
            />
            <StepCard
              step="3"
              title="Activate code generation"
              description="Select a key paper and hand off to the multi-agent builder to create specs, tests, and runnable projects."
            />
          </div>
        </div>
      </section>

      <div id="contextual-search" className="card" style={{ marginBottom: '32px' }}>
        <ContextualSearch />
      </div>

      <AtlasOverview paperLimit={8} />

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

const StepCard = ({ step, title, description }: { step: string; title: string; description: string }) => (
  <div style={{
    padding: '18px',
    borderRadius: '16px',
    background: 'rgba(17, 24, 39, 0.55)',
    border: '1px solid rgba(148, 163, 184, 0.15)'
  }}>
    <div style={{
      width: '36px',
      height: '36px',
      borderRadius: '999px',
      background: 'rgba(99, 102, 241, 0.2)',
      color: 'var(--accent-indigo)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontWeight: 600,
      marginBottom: '12px'
    }}>
      {step}
    </div>
    <h3 style={{ fontSize: '18px', marginBottom: '8px' }}>{title}</h3>
    <p style={{ color: 'var(--secondary-text)', fontSize: '14px', lineHeight: 1.6 }}>{description}</p>
  </div>
);
