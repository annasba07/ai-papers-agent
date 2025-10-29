"use client";

import { useEffect, useState } from "react";
import type { AtlasSummary, AtlasPaper } from "@/types/Atlas";

interface AtlasOverviewProps {
  paperLimit?: number;
}

export const AtlasOverview: React.FC<AtlasOverviewProps> = ({ paperLimit = 8 }) => {
  const [summary, setSummary] = useState<AtlasSummary | null>(null);
  const [papers, setPapers] = useState<AtlasPaper[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await fetch("/api/atlas/summary");
        if (!res.ok) {
          throw new Error(await res.text());
        }
        const json = (await res.json()) as AtlasSummary;
        setSummary(json);
      } catch (err) {
        setError("Failed to load atlas summary");
        console.error(err);
      }
    };

    const fetchPapers = async () => {
      try {
        const res = await fetch(`/api/atlas/papers?limit=${paperLimit}`);
        if (!res.ok) {
          throw new Error(await res.text());
        }
        const json = (await res.json()) as { papers: AtlasPaper[] };
        setPapers(json.papers);
      } catch (err) {
        setError("Failed to load atlas papers");
        console.error(err);
      }
    };

    fetchSummary();
    fetchPapers();
  }, [paperLimit]);

  if (error) {
    return (
      <div className="card" style={{ marginBottom: "32px" }}>
        <h2>Atlas Snapshot</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="card" style={{ marginBottom: "32px" }}>
      <h2>Living Research Atlas Snapshot</h2>
      {!summary ? (
        <p>Loading atlas data…</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "16px" }}>
            <StatBlock label="Papers" value={summary.stats.unique_papers.toLocaleString()} />
            <StatBlock label="Input Windows" value={summary.stats.input_files} />
            <StatBlock label="Active Categories" value={summary.stats.categories.length} />
          </div>

          <div>
            <h3 style={{ marginBottom: "12px" }}>Top Research Areas (last 3 years)</h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "12px" }}>
              {summary.topCategories.slice(0, 8).map((cat) => (
                <span
                  key={cat.category}
                  className="badge"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "8px 14px",
                    borderRadius: "999px",
                    backgroundColor: "rgba(59, 130, 246, 0.12)",
                    color: "var(--accent-blue)",
                    fontWeight: 600,
                  }}
                >
                  {cat.category}
                  <span style={{ fontSize: "12px", color: "var(--secondary-text)" }}>
                    {cat.total.toLocaleString()} papers
                  </span>
                </span>
              ))}
            </div>
          </div>

          <div>
            <h3 style={{ marginBottom: "12px" }}>Most Prolific Authors</h3>
            <ol style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "8px", paddingLeft: "18px" }}>
              {summary.topAuthors.slice(0, 12).map((author) => (
                <li key={author.author} style={{ color: "var(--secondary-text)" }}>
                  <strong style={{ color: "var(--primary-text)" }}>{author.author}</strong>
                  <span style={{ marginLeft: "6px", fontSize: "12px" }}>({author.paper_count})</span>
                </li>
              ))}
            </ol>
          </div>

          <div>
            <h3 style={{ marginBottom: "12px" }}>Recent Highlights</h3>
            {!papers.length ? (
              <p>Loading papers…</p>
            ) : (
              <div style={{ display: "grid", gap: "16px" }}>
                {papers.map((paper) => (
                  <article key={paper.id} className="paper-card" style={{ padding: "16px", borderRadius: "12px", backgroundColor: "var(--component-bg-light)", border: "1px solid var(--borders)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: "12px" }}>
                      <h4 style={{ margin: 0, fontSize: "18px" }}>{paper.title}</h4>
                      <span style={{ fontSize: "12px", color: "var(--secondary-text)" }}>{paper.category}</span>
                    </div>
                    <p style={{ fontSize: "13px", color: "var(--secondary-text)", marginBottom: "8px" }}>
                      {paper.authors.slice(0, 4).join(", ")}
                      {paper.authors.length > 4 ? " et al." : ""}
                      {paper.published ? ` • ${new Date(paper.published).toLocaleDateString()}` : ""}
                    </p>
                    <p style={{ fontSize: "14px", color: "var(--primary-text)", lineHeight: 1.5 }}>
                      {paper.abstract.slice(0, 260)}{paper.abstract.length > 260 ? "…" : ""}
                    </p>
                    {paper.link && (
                      <a href={paper.link} target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ marginTop: "8px" }}>
                        View on arXiv
                      </a>
                    )}
                  </article>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const StatBlock = ({ label, value }: { label: string; value: string | number }) => (
  <div style={{ padding: "16px", borderRadius: "12px", backgroundColor: "rgba(17, 25, 40, 0.04)" }}>
    <div style={{ fontSize: "14px", color: "var(--secondary-text)", marginBottom: "6px" }}>{label}</div>
    <div style={{ fontSize: "26px", fontWeight: 700 }}>{value}</div>
  </div>
);

export default AtlasOverview;
