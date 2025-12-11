'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import './benchmarks.css';

interface Benchmark {
  id: string;
  name: string;
  slug: string;
  task_category: string;
  modality: string;
  primary_metric: string;
  higher_is_better: boolean;
  description: string | null;
}

interface SOTAEntry {
  benchmark_id: string;
  benchmark_name: string;
  paper_id: string;
  paper_title: string;
  value: number;
  achieved_date: string;
  model_name: string | null;
  model_size: string | null;
  details: Record<string, unknown> | null;
}

interface LeaderboardEntry {
  rank: number;
  paper_id: string;
  paper_title: string;
  value: number;
  model_name: string | null;
  model_size: string | null;
  achieved_date: string | null;
  is_current_sota: boolean;
}

const modalityIcons: Record<string, string> = {
  vision: '👁️',
  language: '📝',
  code: '💻',
  multimodal: '🔀',
  general: '⚡',
};

const modalityColors: Record<string, string> = {
  vision: '#10b981',
  language: '#6366f1',
  code: '#f59e0b',
  multimodal: '#ec4899',
  general: '#8b5cf6',
};

export default function BenchmarksPage() {
  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
  const [selectedBenchmark, setSelectedBenchmark] = useState<Benchmark | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [currentSOTA, setCurrentSOTA] = useState<SOTAEntry | null>(null);
  const [sotaHistory, setSOTAHistory] = useState<SOTAEntry[]>([]);
  const [activeModality, setActiveModality] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

  // Fetch all benchmarks
  useEffect(() => {
    const fetchBenchmarks = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/data-moat/benchmarks`);
        if (res.ok) {
          const data = await res.json();
          setBenchmarks(data.benchmarks || []);
        }
      } catch (err) {
        console.error('Failed to fetch benchmarks:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchBenchmarks();
  }, [API_BASE]);

  // Fetch benchmark details when selected
  useEffect(() => {
    if (!selectedBenchmark) {
      setLeaderboard([]);
      setCurrentSOTA(null);
      setSOTAHistory([]);
      return;
    }

    const fetchDetails = async () => {
      setDetailLoading(true);
      try {
        const [leaderboardRes, sotaRes, historyRes] = await Promise.all([
          fetch(`${API_BASE}/data-moat/benchmarks/${selectedBenchmark.slug}/leaderboard`),
          fetch(`${API_BASE}/data-moat/benchmarks/${selectedBenchmark.slug}/sota`),
          fetch(`${API_BASE}/data-moat/benchmarks/${selectedBenchmark.slug}/history`).catch(() => null),
        ]);

        if (leaderboardRes.ok) {
          const data = await leaderboardRes.json();
          setLeaderboard(data.leaderboard || []);
        }

        if (sotaRes.ok) {
          const data = await sotaRes.json();
          if (data.paper_id) {
            setCurrentSOTA(data);
          }
        } else {
          setCurrentSOTA(null);
        }

        if (historyRes && historyRes.ok) {
          const data = await historyRes.json();
          setSOTAHistory(data.history || []);
        }
      } catch (err) {
        console.error('Failed to fetch benchmark details:', err);
      } finally {
        setDetailLoading(false);
      }
    };

    fetchDetails();
  }, [selectedBenchmark, API_BASE]);

  // Group benchmarks by modality
  const modalities = Array.from(new Set(benchmarks.map(b => b.modality)));
  const benchmarksByModality = modalities.reduce((acc, modality) => {
    acc[modality] = benchmarks.filter(b => b.modality === modality);
    return acc;
  }, {} as Record<string, Benchmark[]>);

  const filteredModalities = activeModality
    ? [activeModality]
    : modalities;

  return (
    <div className="benchmarks-page">
      {/* Background */}
      <div className="benchmarks-bg">
        <div className="benchmarks-bg__grid" />
        <div className="benchmarks-bg__glow" />
      </div>

      <main className="benchmarks-main">
        {/* Hero */}
        <header className="benchmarks-hero">
          <div className="benchmarks-hero__badge">
            <span className="pulse" />
            SOTA Tracker
          </div>
          <h1>Benchmark Leaderboards</h1>
          <p className="benchmarks-hero__subtitle">
            Track state-of-the-art results across {benchmarks.length} ML benchmarks.
            See which papers are pushing the boundaries.
          </p>
        </header>

        {/* Modality filters */}
        <nav className="modality-filters">
          <button
            className={`modality-chip ${!activeModality ? 'modality-chip--active' : ''}`}
            onClick={() => setActiveModality(null)}
          >
            All Modalities
          </button>
          {modalities.map(modality => (
            <button
              key={modality}
              className={`modality-chip ${activeModality === modality ? 'modality-chip--active' : ''}`}
              onClick={() => setActiveModality(modality)}
              style={{ '--modality-color': modalityColors[modality] || '#6b7280' } as React.CSSProperties}
            >
              <span className="modality-chip__icon">{modalityIcons[modality] || '📊'}</span>
              {modality}
              <span className="modality-chip__count">{benchmarksByModality[modality]?.length || 0}</span>
            </button>
          ))}
        </nav>

        {loading ? (
          <div className="benchmarks-loading">
            <div className="benchmarks-loading__spinner" />
            <span>Loading benchmarks...</span>
          </div>
        ) : (
          <div className="benchmarks-layout">
            {/* Benchmark list */}
            <aside className="benchmarks-sidebar">
              {filteredModalities.map(modality => (
                <section key={modality} className="modality-section">
                  <h2 className="modality-section__title">
                    <span className="modality-section__icon">{modalityIcons[modality] || '📊'}</span>
                    {modality.charAt(0).toUpperCase() + modality.slice(1)}
                  </h2>
                  <div className="benchmark-list">
                    {benchmarksByModality[modality]?.map(benchmark => (
                      <button
                        key={benchmark.id}
                        className={`benchmark-item ${selectedBenchmark?.id === benchmark.id ? 'benchmark-item--active' : ''}`}
                        onClick={() => setSelectedBenchmark(benchmark)}
                      >
                        <span className="benchmark-item__name">{benchmark.name}</span>
                        <span className="benchmark-item__metric">{benchmark.primary_metric}</span>
                      </button>
                    ))}
                  </div>
                </section>
              ))}
            </aside>

            {/* Detail panel */}
            <div className="benchmarks-detail">
              {!selectedBenchmark ? (
                <div className="benchmarks-detail__empty">
                  <div className="benchmarks-detail__empty-icon">🏆</div>
                  <h3>Select a Benchmark</h3>
                  <p>Choose a benchmark from the list to view its leaderboard and SOTA progression</p>
                </div>
              ) : (
                <>
                  {/* Benchmark header */}
                  <header className="benchmark-header">
                    <div className="benchmark-header__info">
                      <span
                        className="benchmark-header__modality"
                        style={{ '--modality-color': modalityColors[selectedBenchmark.modality] || '#6b7280' } as React.CSSProperties}
                      >
                        {modalityIcons[selectedBenchmark.modality]} {selectedBenchmark.modality}
                      </span>
                      <h2 className="benchmark-header__name">{selectedBenchmark.name}</h2>
                      <p className="benchmark-header__desc">
                        {selectedBenchmark.description || `${selectedBenchmark.task_category} benchmark`}
                      </p>
                    </div>
                    <div className="benchmark-header__meta">
                      <div className="benchmark-meta-item">
                        <span className="benchmark-meta-item__label">Primary Metric</span>
                        <span className="benchmark-meta-item__value">{selectedBenchmark.primary_metric}</span>
                      </div>
                      <div className="benchmark-meta-item">
                        <span className="benchmark-meta-item__label">Direction</span>
                        <span className="benchmark-meta-item__value">
                          {selectedBenchmark.higher_is_better ? '↑ Higher is better' : '↓ Lower is better'}
                        </span>
                      </div>
                    </div>
                  </header>

                  {detailLoading ? (
                    <div className="benchmarks-loading benchmarks-loading--small">
                      <div className="benchmarks-loading__spinner" />
                      <span>Loading leaderboard...</span>
                    </div>
                  ) : (
                    <>
                      {/* Current SOTA */}
                      {currentSOTA && (
                        <section className="sota-current">
                          <h3 className="section-title">
                            <span className="section-title__icon">🥇</span>
                            Current State-of-the-Art
                          </h3>
                          <div className="sota-card">
                            <div className="sota-card__value">
                              <span className="sota-card__number">{currentSOTA.value.toFixed(2)}</span>
                              <span className="sota-card__metric">{selectedBenchmark.primary_metric}</span>
                            </div>
                            <div className="sota-card__info">
                              <h4 className="sota-card__paper">
                                <Link
                                  href={`https://arxiv.org/abs/${currentSOTA.paper_id.split('v')[0]}`}
                                  target="_blank"
                                >
                                  {currentSOTA.paper_title}
                                </Link>
                              </h4>
                              {currentSOTA.model_name && (
                                <span className="sota-card__model">{currentSOTA.model_name}</span>
                              )}
                              <span className="sota-card__date">
                                Achieved: {new Date(currentSOTA.achieved_date).toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                        </section>
                      )}

                      {/* Leaderboard */}
                      <section className="leaderboard-section">
                        <h3 className="section-title">
                          <span className="section-title__icon">📊</span>
                          Leaderboard
                        </h3>

                        {leaderboard.length === 0 ? (
                          <div className="leaderboard-empty">
                            <p>No leaderboard entries yet.</p>
                            <p className="leaderboard-empty__hint">
                              SOTA data is extracted from papers during deep analysis.
                              Run enrichment scripts to populate benchmark results.
                            </p>
                          </div>
                        ) : (
                          <div className="leaderboard-table">
                            <div className="leaderboard-row leaderboard-row--header">
                              <span className="leaderboard-cell leaderboard-cell--rank">Rank</span>
                              <span className="leaderboard-cell leaderboard-cell--paper">Paper / Model</span>
                              <span className="leaderboard-cell leaderboard-cell--value">Score</span>
                              <span className="leaderboard-cell leaderboard-cell--date">Date</span>
                            </div>
                            {leaderboard.map(entry => (
                              <div
                                key={`${entry.paper_id}-${entry.rank}`}
                                className={`leaderboard-row ${entry.is_current_sota ? 'leaderboard-row--sota' : ''}`}
                              >
                                <span className="leaderboard-cell leaderboard-cell--rank">
                                  {entry.rank === 1 && <span className="rank-medal">🥇</span>}
                                  {entry.rank === 2 && <span className="rank-medal">🥈</span>}
                                  {entry.rank === 3 && <span className="rank-medal">🥉</span>}
                                  {entry.rank > 3 && <span className="rank-number">#{entry.rank}</span>}
                                </span>
                                <span className="leaderboard-cell leaderboard-cell--paper">
                                  <Link
                                    href={`https://arxiv.org/abs/${entry.paper_id.split('v')[0]}`}
                                    target="_blank"
                                    className="leaderboard-paper-link"
                                  >
                                    {entry.paper_title}
                                  </Link>
                                  {entry.model_name && (
                                    <span className="leaderboard-model">{entry.model_name}</span>
                                  )}
                                </span>
                                <span className="leaderboard-cell leaderboard-cell--value">
                                  {entry.value.toFixed(2)}
                                </span>
                                <span className="leaderboard-cell leaderboard-cell--date">
                                  {entry.achieved_date
                                    ? new Date(entry.achieved_date).toLocaleDateString('en-US', {
                                        month: 'short',
                                        year: 'numeric'
                                      })
                                    : '-'
                                  }
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </section>

                      {/* SOTA History Timeline */}
                      {sotaHistory.length > 0 && (
                        <section className="sota-history">
                          <h3 className="section-title">
                            <span className="section-title__icon">📈</span>
                            SOTA Progression
                          </h3>
                          <div className="sota-timeline">
                            {sotaHistory.map((entry, idx) => (
                              <div key={`${entry.paper_id}-${idx}`} className="sota-timeline__entry">
                                <div className="sota-timeline__marker" />
                                <div className="sota-timeline__content">
                                  <span className="sota-timeline__value">{entry.value.toFixed(2)}</span>
                                  <span className="sota-timeline__paper">{entry.paper_title}</span>
                                  <span className="sota-timeline__date">
                                    {new Date(entry.achieved_date).toLocaleDateString()}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </section>
                      )}
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
