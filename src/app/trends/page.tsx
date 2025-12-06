'use client';

import { useMemo } from 'react';
import TrendsDashboard from '@/components/TrendsDashboard';
import TechniqueComparisonComponent from '@/components/TechniqueComparison';

export default function TrendsPage() {
  const apiBaseUrl = useMemo(() => process.env.NEXT_PUBLIC_API_BASE_URL ?? '', []);

  return (
    <main className="page-shell">
      <section className="hero hero--compact">
        <span className="eyebrow">Research Intelligence</span>
        <h1>AI Research Trends</h1>
        <p className="hero__subtitle">
          Real-time analysis of technique adoption, rising methods, and active researchers.
          Powered by citation data and technique extraction.
        </p>
      </section>

      <div className="page-content">
        <TrendsDashboard apiBaseUrl={apiBaseUrl} />

        <TechniqueComparisonComponent apiBaseUrl={apiBaseUrl} />

        <section className="trends-info">
          <h3 className="section-title">About Trend Detection</h3>
          <div className="trends-info__grid">
            <div className="trends-info__card">
              <h4>Hot Topics</h4>
              <p>
                Identifies techniques with accelerating paper counts by comparing
                the last 30 days to the previous 30 days. Higher acceleration
                indicates rapidly growing interest.
              </p>
            </div>
            <div className="trends-info__card">
              <h4>Rising Techniques</h4>
              <p>
                Tracks techniques showing consistent growth over three periods.
                These are methods gaining steady traction rather than sudden spikes.
              </p>
            </div>
            <div className="trends-info__card">
              <h4>Active Authors</h4>
              <p>
                Highlights researchers with the most publications in recent weeks,
                along with their primary research areas and topic expertise.
              </p>
            </div>
            <div className="trends-info__card">
              <h4>Emerging Areas</h4>
              <p>
                Detects task domains and research areas with accelerating activity,
                helping you spot new frontiers before they become mainstream.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
