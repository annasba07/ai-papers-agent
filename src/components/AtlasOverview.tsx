"use client";

import type { CSSProperties } from "react";
import type { AtlasSummary, AtlasPaper } from "@/types/Atlas";

type AtlasOverviewProps = {
  summary: AtlasSummary | null;
  papers: AtlasPaper[];
  loadingSummary?: boolean;
  loadingPapers?: boolean;
  error?: string | null;
};

const pillVariants = ["indigo", "emerald", "amber", "pink", "sky", "slate"] as const;

const AtlasOverview = ({
  summary,
  papers,
  loadingSummary = false,
  loadingPapers = false,
  error = null,
}: AtlasOverviewProps) => {
  const totalPapers = summary?.stats.unique_papers ?? 0;
  const showSummaryPlaceholder = loadingSummary && !summary && !error;
  const summaryUnavailable = !loadingSummary && !summary && !error;
  const pillDenominator = totalPapers > 0 ? totalPapers : 1;

  return (
    <section className="atlas-overview">
      <header className="atlas-overview__header">
        <span className="eyebrow">Atlas snapshot</span>
        <h2>Living Research Atlas Snapshot</h2>
        <p className="section-subtitle">
          A live view of where research momentum is building so you can target the teams, categories, and papers that matter.
        </p>
      </header>

      {error && <div className="alert alert--error">{error}</div>}
      {showSummaryPlaceholder && <p className="atlas-empty">Loading atlas data…</p>}
      {summaryUnavailable && <p className="atlas-empty">Atlas summary unavailable right now.</p>}

      {summary && (
        <div className="atlas-overview__grid">
          <div className="atlas-statboard">
            <StatTile
              label="Indexed papers"
              value={summary.stats.unique_papers.toLocaleString()}
              hint="Aggregated from arXiv & partner feeds"
            />
            <StatTile
              label="Context windows processed"
              value={summary.stats.input_files.toLocaleString()}
              hint="Documents ingested for contextual grounding"
            />
            <StatTile
              label="Active research areas"
              value={summary.stats.categories.length}
              hint="Categories with activity in the last 90 days"
            />
          </div>

          <div className="atlas-field">
            <h3 className="section-title">Top Research Areas</h3>
            <p className="section-subtitle">Where publication velocity is peaking across the last three years.</p>
            <div className="atlas-pillboard">
              {summary.topCategories.slice(0, 8).map((cat, index) => {
                const share = Math.max(0, Math.min(1, cat.total / pillDenominator));
                const variant = pillVariants[index % pillVariants.length];

                return (
                  <div
                    key={cat.category}
                    className={`atlas-pill atlas-pill--${variant}`}
                    style={{ "--pill-share": `${Math.round(share * 100)}%` } as CSSProperties}
                  >
                    <div className="atlas-pill__name">{cat.category}</div>
                    <div className="atlas-pill__value">{cat.total.toLocaleString()} papers</div>
                    <span className="atlas-pill__bar" />
                  </div>
                );
              })}
            </div>
          </div>

          <div className="atlas-field">
            <h3 className="section-title">Most Prolific Authors</h3>
            <p className="section-subtitle">Researchers pushing the frontier with the highest output.</p>
            <ol className="atlas-author-list">
              {summary.topAuthors.slice(0, 10).map((author, index) => (
                <li key={author.author}>
                  <span className="atlas-author-rank">#{index + 1}</span>
                  <span className="atlas-author-name">{author.author}</span>
                  <span className="atlas-author-count">{author.paper_count} papers</span>
                </li>
              ))}
            </ol>
          </div>

          <div className="atlas-field atlas-highlights">
            <h3 className="section-title">Recent Highlights</h3>
            <p className="section-subtitle">Signal-rich releases from the latest atlas entries.</p>
            {loadingPapers ? (
              <p className="atlas-empty">Loading highlight papers…</p>
            ) : papers.length ? (
              <div className="highlight-grid">
                {papers.map((paper, index) => {
                  const variant = pillVariants[index % pillVariants.length];
                  return (
                    <article key={paper.id} className={`highlight-card highlight-card--${variant}`}>
                      <span className="highlight-card__category">{paper.category ?? "Uncategorised"}</span>
                      <h4 className="highlight-card__title">{paper.title}</h4>
                      <p className="highlight-card__meta">
                        {paper.authors.slice(0, 3).join(", ")}
                        {paper.authors.length > 3 ? " et al." : ""}
                        {paper.published ? ` • ${new Date(paper.published).toLocaleDateString()}` : ""}
                      </p>
                      <p className="highlight-card__excerpt">
                        {paper.abstract.length > 240 ? `${paper.abstract.slice(0, 240)}…` : paper.abstract}
                      </p>
                      {paper.link && (
                        <a href={paper.link} target="_blank" rel="noopener noreferrer" className="highlight-card__cta">
                          View paper →
                        </a>
                      )}
                    </article>
                  );
                })}
              </div>
            ) : (
              <p className="atlas-empty">No highlight papers available yet.</p>
            )}
          </div>
        </div>
      )}
    </section>
  );
};

const StatTile = ({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint: string;
}) => (
  <div className="atlas-statboard__tile">
    <span className="atlas-statboard__label">{label}</span>
    <span className="atlas-statboard__value">{value}</span>
    <span className="atlas-statboard__hint">{hint}</span>
  </div>
);

export default AtlasOverview;
