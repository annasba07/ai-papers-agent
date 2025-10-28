# 🚀 AI Papers Agent — Research Atlas Roadmap

**North Star:** Help AI teams move from idea → production-grade implementation in hours by giving them a living map of the AI research universe and the tools to execute on it.

**Guiding Principles**
- Treat research as a graph, not a list. Everything connects: papers ↔ techniques ↔ datasets ↔ benchmarks ↔ institutions ↔ people.
- Capture signals continuously (publications, citations, repos, benchmarks) and reason over their trajectories.
- Wrap insights in opinionated workflows that answer, “What should I do next and why?”
- Keep implementation acceleration (code generation, testing, debugging) as the compounding force on top of intelligence.

---

## 📚 Pillars

1. **Living Research Graph**
   - Unified ontology for papers, techniques, tasks, datasets, benchmarks, institutions, and authors.
   - Semantic embeddings + citation/affiliation edges + co-usage relationships.
   - APIs and graph-query layer for flexible traversal.

2. **Deep Paper Intelligence**
   - Gemini-driven analysis + PDF table parsing.
   - Extraction of techniques, metrics, compute requirements, novelty signals, and reproducibility cues.
   - Benchmark deltas and SOTA tracking backed by structured storage.

3. **Exploratory Atlas UI**
   - Multi-scale visualizations: global topic map, technique timelines, benchmark leaderboards.
   - Guided exploration flows for “solve my problem,” “compare methods,” and “find what’s trending.”
   - Project planning canvases that turn insights into actionable plans.

4. **Implementation Acceleration**
   - Multi-agent code generation orchestrator with testing and debugging loops.
   - Asset packs (code, configs, eval scripts) tailored to the chosen technique.
   - Feedback loops that learn from execution outcomes and user edits.

---

## ✅ Current Foundation

- Async FastAPI backend with service boundaries (arXiv, AI analysis, embeddings, ingestion, similarity, agents).
- Next.js 15 frontend with contextual search, paper browsing, and detailed AI-generated insight views.
- Gemini-based analysis pipeline producing structured summaries, significance scores, and applicability metadata.
- Code detection service (GitHub search + heuristics) feeding UI badges.
- Knowledge graph groundwork via Supabase/Postgres schema and ingestion jobs.

---

## 🛠️ Phase Plan

### Phase 1 — Graph & Signals (Weeks 1-4)
**Goal:** Evolve from paper list → connected research graph enriched with high-value signals.

1. **Graph Schema & Normalization**
   - Finalize ontology (paper, technique, task, dataset, benchmark, organization, author).
   - Implement normalization pipeline (alias resolution, concept canonicalization).
   - Store in Postgres + vector DB; expose via Hasura/GraphQL or custom resolvers.
2. **Citation & Similarity Enrichment**
   - Integrate OpenAlex/Semantic Scholar for citation data.
   - Compute similarity embeddings (paper-to-paper, technique-to-technique).
   - Add co-author, co-citation, shared-dataset edges.
3. **Signal Ingestion Jobs**
   - Extend ingestion to capture GitHub stats, benchmark metrics (Papers With Code), conference acceptances.
   - Build incremental ETL jobs (dbt/Spark) for momentum metrics (velocity, acceleration, novelty).

**Milestone:** API can answer graph questions like “what techniques are rising for real-time control?” with supporting metrics.

### Phase 2 — Insight Surfaces (Weeks 5-8)
**Goal:** Let users explore the map and understand frontier movement at a glance.

1. **Atlas Visualizations**
   - Force-directed/global map of research topics (react-force-graph or deck.gl).
   - Timeline views for techniques/datasets showing key papers and metric jumps.
   - Benchmark dashboards with historical SOTA, methodology notes, compute costs.
2. **Exploration Workflows**
   - Guided problem decomposition: user describes goal → system surfaces subproblems, candidate techniques, evaluation checklists.
   - Comparison mode: side-by-side diff of two techniques (benchmark performance, complexity, maturity, code availability).
   - Trend trackers: weekly “hot topics” digest with underlying metrics.
3. **Contextual Reasoning API**
   - Natural-language graph query layer (LLM translating to Cypher/SQL).
   - Narrative summaries (e.g., “Diffusion models in robotics: 3 emerging approaches, top paper summaries, code links, open risks.”)

**Milestone:** Researchers can visually explore, compare, and plan from the web UI without raw data dives.

### Phase 3 — Implementation Engine (Weeks 9-12)
**Goal:** Turn insights into runnable, high-quality code bundles.

1. **Agent Orchestration Hardening**
   - Formalize multi-agent roles (analyzer, designer, coder, tester, debugger).
   - Persist agent memory/outcome metrics for continual improvement.
   - Add guardrails: spec validation, hallucination detection, policy checks.
2. **Technique Playbooks**
   - Pre-build playbooks for top 20 techniques (LoRA, diffusion, ViT, MoE, etc.).
   - Each playbook = architecture summary, config template, dataset prep, evaluation harness.
3. **Execution Loop**
   - Integrate with containerized sandbox for running generated code & tests.
   - Support iterative refinement (capture failures, update prompts, re-run).
   - Surface success/failure analytics back into graph (implementation maturity score).

**Milestone:** User selects technique → receives runnable repo with tests + docs, validated by automated execution.

---

## 📈 Supporting Workstreams

- **Data Quality & Observability**
  - Monitoring dashboards for ingestion freshness, API latency, and agent success rates.
  - Manual review interface for concept/metric extraction accuracy.
- **Developer Experience**
  - Tooling to replay analyses, trace agent decisions, and patch prompts safely.
  - CLI for power users to query graph and trigger ingestion runs.
- **Partnership & Integrations**
  - Hook into institutional repositories, ArXiv overlays, benchmark communities.
  - Optional user-driven curation (stars, notes, replication results) to enrich graph.

---

## 🪜 Implementation Sequencing Cheat Sheet

| Week | Focus | Key Deliverables |
|------|-------|------------------|
| 1 | Ontology + Graph schema | ERD, migration set, initial loaders |
| 2 | Concept normalization | Alias resolver, embedding-based clustering |
| 3 | Citation + similarity edges | OpenAlex ingestion, similarity jobs |
| 4 | Signal metrics | Benchmark ETL, momentum calculations |
| 5 | Atlas prototype | Topic map with drill-down |
| 6 | Trend pipeline | Hot topics service + API |
| 7 | Comparison workflows | Technique diff endpoint + UI |
| 8 | Problem-to-plan UX | Guided flow MVP |
| 9 | Agent orchestration v2 | Role definitions, evaluation harness |
|10 | Playbook library | 10 core technique templates |
|11 | Execution sandbox | Containerized run + logging |
|12 | Launch alpha | End-to-end “idea → code bundle” demo |

---

By layering these capabilities on the foundation already in place, AI Paper Digest becomes the go-to companion for discovering where the cutting edge is, understanding how it got there, and building what comes next.***
