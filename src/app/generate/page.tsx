"use client";

import { useState, useEffect, useMemo } from "react";

interface Paper {
  id: string;
  title: string;
  authors: string[];
  published: string;
  abstract?: string;
}

interface GenerationResult {
  success: boolean;
  generation_time_seconds: number;
  code?: {
    main_code: string;
    test_code: string;
    example_code: string;
    config_code: string;
    dependencies: string[];
  };
  tests?: {
    total_tests: number;
  };
  test_results?: {
    tests_passed: number;
    tests_total: number;
  };
  readme?: string;
  system_reflection?: string;
  debug_iterations: number;
}

type GenerationStatus = "idle" | "searching" | "generating" | "success" | "error";

export default function GeneratePage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [status, setStatus] = useState<GenerationStatus>("idle");
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"code" | "tests" | "readme">("code");

  const apiBaseUrl = useMemo(() => process.env.NEXT_PUBLIC_API_BASE_URL ?? "", []);

  // Search for papers
  const searchPapers = async () => {
    if (!searchQuery.trim()) return;

    setStatus("searching");
    setError(null);

    try {
      const endpoint = apiBaseUrl
        ? `${apiBaseUrl}/papers?query=${encodeURIComponent(searchQuery)}&limit=10`
        : `/api/atlas/papers?query=${encodeURIComponent(searchQuery)}&limit=10`;

      const response = await fetch(endpoint);
      if (!response.ok) throw new Error("Failed to search papers");

      const data = await response.json();
      const paperList = Array.isArray(data) ? data : data.papers || [];
      setPapers(paperList);
      setStatus("idle");
    } catch (err) {
      setError("Failed to search papers. Please try again.");
      setStatus("idle");
    }
  };

  // Generate code from selected paper
  const generateCode = async () => {
    if (!selectedPaper) return;

    setStatus("generating");
    setError(null);
    setResult(null);

    try {
      const endpoint = apiBaseUrl
        ? `${apiBaseUrl}/papers/${selectedPaper.id}/generate-code`
        : `/api/v1/papers/${selectedPaper.id}/generate-code`;

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Code generation failed");
      }

      const data = await response.json();
      setResult(data);
      setStatus("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Code generation failed");
      setStatus("error");
    }
  };

  return (
    <main className="generate-page">
      <section className="generate-hero">
        <div className="generate-hero__content">
          <span className="eyebrow">Multi-Agent Code Generation</span>
          <h1>Turn Papers into Working Code</h1>
          <p className="generate-hero__subtitle">
            Select a research paper and let our 5-agent system analyze, design tests,
            generate code, and debug until it works.
          </p>
        </div>
      </section>

      <section className="generate-workflow">
        {/* Step 1: Search */}
        <div className="generate-step">
          <div className="generate-step__header">
            <span className="generate-step__number">1</span>
            <h2>Find a Paper</h2>
          </div>
          <div className="generate-step__content">
            <div className="generate-search">
              <input
                type="text"
                placeholder="Search for papers (e.g., 'attention mechanism', 'diffusion model')"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && searchPapers()}
                className="form-control generate-search__input"
              />
              <button
                onClick={searchPapers}
                disabled={status === "searching" || !searchQuery.trim()}
                className="btn btn-primary"
              >
                {status === "searching" ? "Searching..." : "Search"}
              </button>
            </div>

            {papers.length > 0 && (
              <div className="generate-papers">
                {papers.map((paper) => (
                  <div
                    key={paper.id}
                    className={`generate-paper-card ${selectedPaper?.id === paper.id ? "generate-paper-card--selected" : ""}`}
                    onClick={() => setSelectedPaper(paper)}
                  >
                    <h3 className="generate-paper-card__title">{paper.title}</h3>
                    <p className="generate-paper-card__meta">
                      {paper.authors?.slice(0, 3).join(", ")}
                      {paper.authors?.length > 3 && ` +${paper.authors.length - 3} more`}
                      {paper.published && ` · ${new Date(paper.published).toLocaleDateString()}`}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Step 2: Generate */}
        <div className={`generate-step ${!selectedPaper ? "generate-step--disabled" : ""}`}>
          <div className="generate-step__header">
            <span className="generate-step__number">2</span>
            <h2>Generate Code</h2>
          </div>
          <div className="generate-step__content">
            {selectedPaper ? (
              <div className="generate-selected">
                <div className="generate-selected__paper">
                  <h3>{selectedPaper.title}</h3>
                  <p>{selectedPaper.authors?.slice(0, 3).join(", ")}</p>
                </div>
                <button
                  onClick={generateCode}
                  disabled={status === "generating"}
                  className="btn btn-primary btn-lg"
                >
                  {status === "generating" ? (
                    <>
                      <span className="generate-spinner" />
                      Generating...
                    </>
                  ) : (
                    "Generate Working Code"
                  )}
                </button>
              </div>
            ) : (
              <p className="generate-placeholder">Select a paper above to generate code</p>
            )}

            {status === "generating" && (
              <div className="generate-progress">
                <div className="generate-progress__stages">
                  <Stage label="Analyzing paper" status="active" />
                  <Stage label="Designing tests" status="pending" />
                  <Stage label="Generating code" status="pending" />
                  <Stage label="Running tests" status="pending" />
                  <Stage label="Debugging" status="pending" />
                </div>
                <p className="generate-progress__note">
                  This typically takes 60-120 seconds depending on paper complexity.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Step 3: Results */}
        {(status === "success" || status === "error") && (
          <div className="generate-step">
            <div className="generate-step__header">
              <span className="generate-step__number">3</span>
              <h2>Results</h2>
            </div>
            <div className="generate-step__content">
              {error && (
                <div className="generate-error">
                  <p>{error}</p>
                  <button onClick={generateCode} className="btn btn-secondary">
                    Try Again
                  </button>
                </div>
              )}

              {result && (
                <div className="generate-result">
                  <div className="generate-result__header">
                    <div className="generate-result__status">
                      {result.success ? (
                        <span className="generate-result__badge generate-result__badge--success">
                          Success
                        </span>
                      ) : (
                        <span className="generate-result__badge generate-result__badge--partial">
                          Partial
                        </span>
                      )}
                      <span className="generate-result__time">
                        Generated in {result.generation_time_seconds.toFixed(1)}s
                      </span>
                    </div>
                    <div className="generate-result__stats">
                      <span>
                        Tests: {result.test_results?.tests_passed}/{result.test_results?.tests_total}
                      </span>
                      <span>Debug iterations: {result.debug_iterations}</span>
                    </div>
                  </div>

                  <div className="generate-result__tabs">
                    <button
                      className={`generate-result__tab ${activeTab === "code" ? "generate-result__tab--active" : ""}`}
                      onClick={() => setActiveTab("code")}
                    >
                      Code
                    </button>
                    <button
                      className={`generate-result__tab ${activeTab === "tests" ? "generate-result__tab--active" : ""}`}
                      onClick={() => setActiveTab("tests")}
                    >
                      Tests
                    </button>
                    <button
                      className={`generate-result__tab ${activeTab === "readme" ? "generate-result__tab--active" : ""}`}
                      onClick={() => setActiveTab("readme")}
                    >
                      README
                    </button>
                  </div>

                  <div className="generate-result__content">
                    {activeTab === "code" && result.code && (
                      <div className="generate-code-block">
                        <div className="generate-code-block__header">
                          <span>main.py</span>
                          <button
                            onClick={() => navigator.clipboard.writeText(result.code?.main_code || "")}
                            className="btn btn-sm"
                          >
                            Copy
                          </button>
                        </div>
                        <pre className="generate-code-block__code">
                          <code>{result.code.main_code}</code>
                        </pre>
                      </div>
                    )}

                    {activeTab === "tests" && result.code && (
                      <div className="generate-code-block">
                        <div className="generate-code-block__header">
                          <span>test_model.py</span>
                          <button
                            onClick={() => navigator.clipboard.writeText(result.code?.test_code || "")}
                            className="btn btn-sm"
                          >
                            Copy
                          </button>
                        </div>
                        <pre className="generate-code-block__code">
                          <code>{result.code.test_code}</code>
                        </pre>
                      </div>
                    )}

                    {activeTab === "readme" && result.readme && (
                      <div className="generate-readme">
                        <pre>{result.readme}</pre>
                      </div>
                    )}
                  </div>

                  {result.system_reflection && (
                    <div className="generate-result__reflection">
                      <h4>System Reflection</h4>
                      <p>{result.system_reflection}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </section>

      {/* Info Section */}
      <section className="generate-info">
        <h2>How It Works</h2>
        <div className="generate-info__grid">
          <div className="generate-info__card">
            <div className="generate-info__icon">1</div>
            <h3>Paper Analyzer</h3>
            <p>Extracts core algorithms, dependencies, and implementation requirements from the paper.</p>
          </div>
          <div className="generate-info__card">
            <div className="generate-info__icon">2</div>
            <h3>Test Designer</h3>
            <p>Creates comprehensive test suites before any code is written (test-driven development).</p>
          </div>
          <div className="generate-info__card">
            <div className="generate-info__icon">3</div>
            <h3>Code Generator</h3>
            <p>Generates implementation code designed to pass the test suite.</p>
          </div>
          <div className="generate-info__card">
            <div className="generate-info__icon">4</div>
            <h3>Test Executor</h3>
            <p>Runs the tests in a sandboxed environment and reports results.</p>
          </div>
          <div className="generate-info__card">
            <div className="generate-info__icon">5</div>
            <h3>Debugger</h3>
            <p>Analyzes failures, generates fixes, and iterates until tests pass.</p>
          </div>
        </div>
      </section>
    </main>
  );
}

type StageProps = {
  label: string;
  status: "pending" | "active" | "complete";
};

const Stage = ({ label, status }: StageProps) => (
  <div className={`generate-stage generate-stage--${status}`}>
    <span className="generate-stage__indicator" />
    <span className="generate-stage__label">{label}</span>
  </div>
);
