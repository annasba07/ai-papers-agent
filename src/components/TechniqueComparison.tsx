"use client";

import { useState, type CSSProperties } from "react";
import type { TechniqueComparison } from "@/types/Trends";

type TechniqueComparisonProps = {
  apiBaseUrl?: string;
};

const SUGGESTED_TECHNIQUES = [
  "Transformer",
  "LoRA",
  "Diffusion",
  "Flash Attention",
  "RLHF",
  "DPO",
  "Contrastive",
  "Distillation",
  "MoE",
  "SSM",
];

const TechniqueComparisonComponent = ({ apiBaseUrl = "" }: TechniqueComparisonProps) => {
  const [techniqueA, setTechniqueA] = useState("");
  const [techniqueB, setTechniqueB] = useState("");
  const [comparison, setComparison] = useState<TechniqueComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    if (!techniqueA.trim() || !techniqueB.trim()) {
      setError("Please enter both techniques to compare");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        technique_a: techniqueA.trim(),
        technique_b: techniqueB.trim(),
        window_days: "90",
      });

      const endpoint = apiBaseUrl
        ? `${apiBaseUrl}/trends/compare-techniques?${params.toString()}`
        : `/api/v1/trends/compare-techniques?${params.toString()}`;

      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setComparison(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to compare techniques");
    } finally {
      setLoading(false);
    }
  };

  const selectSuggestion = (technique: string, target: "a" | "b") => {
    if (target === "a") {
      setTechniqueA(technique);
    } else {
      setTechniqueB(technique);
    }
  };

  const swapTechniques = () => {
    setTechniqueA(techniqueB);
    setTechniqueB(techniqueA);
  };

  return (
    <section className="technique-comparison">
      <header className="technique-comparison__header">
        <span className="eyebrow">Technique Analysis</span>
        <h2>Compare Techniques</h2>
        <p className="section-subtitle">
          Compare adoption rates, research domains, and representative papers between two techniques.
        </p>
      </header>

      {/* Input Form */}
      <div className="technique-comparison__form">
        <div className="technique-comparison__input-group">
          <label htmlFor="technique-a">Technique A</label>
          <input
            id="technique-a"
            type="text"
            value={techniqueA}
            onChange={(e) => setTechniqueA(e.target.value)}
            placeholder="e.g., Transformer"
            className="technique-comparison__input"
          />
          <div className="technique-comparison__suggestions">
            {SUGGESTED_TECHNIQUES.slice(0, 5).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => selectSuggestion(t, "a")}
                className="technique-comparison__suggestion"
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <button
          type="button"
          onClick={swapTechniques}
          className="technique-comparison__swap"
          title="Swap techniques"
        >
          <span>Swap</span>
        </button>

        <div className="technique-comparison__input-group">
          <label htmlFor="technique-b">Technique B</label>
          <input
            id="technique-b"
            type="text"
            value={techniqueB}
            onChange={(e) => setTechniqueB(e.target.value)}
            placeholder="e.g., Diffusion"
            className="technique-comparison__input"
          />
          <div className="technique-comparison__suggestions">
            {SUGGESTED_TECHNIQUES.slice(5).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => selectSuggestion(t, "b")}
                className="technique-comparison__suggestion"
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <button
          type="button"
          onClick={handleCompare}
          disabled={loading || !techniqueA.trim() || !techniqueB.trim()}
          className="technique-comparison__submit"
        >
          {loading ? "Comparing..." : "Compare"}
        </button>
      </div>

      {error && <div className="alert alert--error">{error}</div>}

      {/* Comparison Results */}
      {comparison && (
        <div className="technique-comparison__results">
          <div className="technique-comparison__versus">
            <div className="technique-comparison__side technique-comparison__side--a">
              <h3 className="technique-comparison__side-name">{comparison.technique_a.name}</h3>
              <div className="technique-comparison__side-count">
                <span className="technique-comparison__count-value">
                  {comparison.technique_a.paper_count}
                </span>
                <span className="technique-comparison__count-label">papers</span>
              </div>
            </div>

            <div className="technique-comparison__vs">
              <span>VS</span>
            </div>

            <div className="technique-comparison__side technique-comparison__side--b">
              <h3 className="technique-comparison__side-name">{comparison.technique_b.name}</h3>
              <div className="technique-comparison__side-count">
                <span className="technique-comparison__count-value">
                  {comparison.technique_b.paper_count}
                </span>
                <span className="technique-comparison__count-label">papers</span>
              </div>
            </div>
          </div>

          {/* Paper Count Bar */}
          <div className="technique-comparison__bar-container">
            <ComparisonBar
              countA={comparison.technique_a.paper_count}
              countB={comparison.technique_b.paper_count}
              nameA={comparison.technique_a.name}
              nameB={comparison.technique_b.name}
            />
          </div>

          {/* Domains Comparison */}
          <div className="technique-comparison__domains">
            <div className="technique-comparison__domain-column">
              <h4>Top Domains - {comparison.technique_a.name}</h4>
              <ul className="technique-comparison__domain-list">
                {comparison.technique_a.top_domains.map(([domain, count]) => (
                  <li key={domain}>
                    <span className="technique-comparison__domain-name">{domain}</span>
                    <span className="technique-comparison__domain-count">{count}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="technique-comparison__domain-column">
              <h4>Top Domains - {comparison.technique_b.name}</h4>
              <ul className="technique-comparison__domain-list">
                {comparison.technique_b.top_domains.map(([domain, count]) => (
                  <li key={domain}>
                    <span className="technique-comparison__domain-name">{domain}</span>
                    <span className="technique-comparison__domain-count">{count}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Common Domains */}
          {comparison.comparison.common_domains.length > 0 && (
            <div className="technique-comparison__common">
              <h4>Common Research Domains</h4>
              <div className="technique-comparison__common-pills">
                {comparison.comparison.common_domains.map((domain) => (
                  <span key={domain} className="technique-comparison__common-pill">
                    {domain}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Representative Papers */}
          <div className="technique-comparison__papers">
            <div className="technique-comparison__papers-column">
              <h4>Recent Papers - {comparison.technique_a.name}</h4>
              <ul className="technique-comparison__papers-list">
                {comparison.technique_a.representative_papers.map((paper) => (
                  <li key={paper.id}>
                    <a
                      href={`https://arxiv.org/abs/${paper.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {paper.title.length > 80 ? `${paper.title.slice(0, 80)}...` : paper.title}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div className="technique-comparison__papers-column">
              <h4>Recent Papers - {comparison.technique_b.name}</h4>
              <ul className="technique-comparison__papers-list">
                {comparison.technique_b.representative_papers.map((paper) => (
                  <li key={paper.id}>
                    <a
                      href={`https://arxiv.org/abs/${paper.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {paper.title.length > 80 ? `${paper.title.slice(0, 80)}...` : paper.title}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <footer className="technique-comparison__footer">
            <span>Analysis window: {comparison.comparison.window_days} days</span>
            <span>
              Ratio: {comparison.comparison.count_ratio.toFixed(2)}:1
            </span>
          </footer>
        </div>
      )}
    </section>
  );
};

const ComparisonBar = ({
  countA,
  countB,
  nameA,
  nameB,
}: {
  countA: number;
  countB: number;
  nameA: string;
  nameB: string;
}) => {
  const total = countA + countB;
  const percentA = total > 0 ? (countA / total) * 100 : 50;
  const percentB = total > 0 ? (countB / total) * 100 : 50;

  return (
    <div className="technique-comparison__bar">
      <div
        className="technique-comparison__bar-segment technique-comparison__bar-segment--a"
        style={{ width: `${percentA}%` } as CSSProperties}
        title={`${nameA}: ${countA} papers (${percentA.toFixed(1)}%)`}
      >
        {percentA > 20 && <span>{percentA.toFixed(0)}%</span>}
      </div>
      <div
        className="technique-comparison__bar-segment technique-comparison__bar-segment--b"
        style={{ width: `${percentB}%` } as CSSProperties}
        title={`${nameB}: ${countB} papers (${percentB.toFixed(1)}%)`}
      >
        {percentB > 20 && <span>{percentB.toFixed(0)}%</span>}
      </div>
    </div>
  );
};

export default TechniqueComparisonComponent;
