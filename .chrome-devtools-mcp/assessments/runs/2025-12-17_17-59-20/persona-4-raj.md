# UX Assessment Report: Dr. Raj Patel - Senior ML Engineer

**Persona**: Dr. Raj Patel, Senior ML Engineer at FAANG
**Focus**: Production ML Optimization, Model Compression
**Date**: December 17, 2025
**Session Duration**: ~3.5 minutes (17:59:43 - 18:03:18 PST)
**Chrome Instance**: chrome-4

---

## Executive Summary

As a production ML engineer, I need tools that filter for **deployable** techniques with real-world metrics. AI Paper Atlas has good semantic search via the Research Advisor, but critically missing: production metrics (latency/memory/throughput), code quality indicators (GitHub stars, maintainability), and hardware-specific benchmarks. The "Has Code" filter is table stakes—I need "Has Production-Ready Code" or "Tested on Real Hardware". **Verdict: Not ready to replace Papers with Code for production work.**

---

## Session Timeline

| Time | Step | Action | Outcome | Emotion (1-5) |
|------|------|--------|---------|---------------|
| 17:59:43 | 0 | Navigate to landing page | Clean interface, immediate "Has Code" filter visible | 3 |
| 17:59:50 | 1 | First impression | Search box prominent, filters sidebar | 3 |
| 18:00:05 | 2 | Explore navigation | Found Generate tab (code generation), not relevant for my task | 3 |
| 18:00:15 | 3 | Search "model quantization production" | 30 results, none relevant (CV papers, not quantization) | 2 |
| 18:00:30 | 3.5 | Click "Ask Advisor" button | Research Advisor panel opened, 6 quantization papers found in 8s | 4 |
| 18:01:00 | 3.5 | Submit detailed production query | Advisor returned CodeBERT compression (not production models) | 2 |
| 18:01:15 | 4 | Expand SingleQuant paper | Abstract visible, tabs for Summary/Related/Benchmarks, no latency metrics | 3 |
| 18:01:30 | 5 | Apply "Has Code" filter | Filter applied, still 6 papers, no GitHub stars or production metrics shown | 2 |
| 18:03:18 | 12 | End session | Limited value for production evaluation | 2 |

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

**Screenshot**: `01-landing-first-impression.png`

**Observations**:
- Clean, uncluttered interface—good first impression
- Search box with placeholder text: "Describe what you're researching"
- **"Has Code" filter prominently visible in sidebar** ✓
- 30 papers shown by default
- No performance metrics visible on landing

**Emotional State**: 3/5 (Neutral - looks professional but unproven)

**Task Success**: Value proposition unclear. Is this for production engineers or academics?

---

### Step 2: Initial Exploration

**Screenshots**: `02a-nav-generate.png`

**Navigation Discovery**:
- Two main tabs: **Explore** (search) and **Generate** (code generation)
- Generate tab: "Turn Papers into Working Code" with 5-agent system
  - Not relevant for finding papers, but interesting for later validation
- Filters sidebar: Quick filters (Has Code, High Impact), Categories, Difficulty, Trending Topics

**Emotional State**: 3/5 (Neutral - clear navigation but Generate seems tangential)

**Confusion Points**:
- Why is code generation mixed with paper search?
- No clear path to "production-ready" papers vs research prototypes

---

### Step 3: Task-Based Search - Finding Quantization Papers

**Screenshots**: `03a-search-query-entered.png`

**Query**: "model quantization production"
**Results**: 30 papers returned
**Response Time**: Instant (client-side filtering?)

**Critical Issue**: Results were NOT relevant to quantization:
- "StereoSpace: Depth-Free Synthesis of Stereo Geometry" (CV paper)
- "WorldLens: Full-Spectrum Evaluations of Driving World Models" (autonomous driving)
- "Omni-Attribute: Open-vocabulary Attribute Encoder" (vision)

**Root Cause**: Keyword search, not semantic. The word "production" matched "video production", "image production", etc.

**Emotional State**: 2/5 (Frustrated - wasted time on irrelevant results)

**Time to Relevant Result**: N/A - gave up after scrolling, switched to Advisor

---

### Step 3.5: Research Advisor (AI-Powered Search)

**Screenshots**: `03b-advisor-loading.png`, `03c-advisor-query-typed.png`, `03d-advisor-response.png`

**Initial Search**: Click "Ask Advisor" button
**Result**: Advisor immediately re-ranked to 6 quantization papers in 8 seconds
**Response Time**: 8004ms (8 seconds)

**Papers Returned**:
1. SingleQuant: Efficient Quantization of LLMs in a Single Pass ✓
2. R2Q: Towards Robust 2-Bit LLMs ✓
3. Quantization Blindspots (security-focused, less relevant)
4. SVD-Based Weight Preservation for Mixed-Precision ✓
5. MeshMosaic (mesh generation, not relevant ✗)
6. AutoChemSchematic (chemical manufacturing, not relevant ✗)

**Success Rate**: 4/6 papers relevant (67%)

**Follow-Up Query**: "I need to speed up a production model using quantization or pruning. Looking for techniques with production-ready code that report latency and memory metrics, not just accuracy."

**Advisor Response**:
- "Contextual synthesis temporarily unavailable" (feature broken?)
- Returned different papers:
  - "On the Compression of Language Models for Code: An Empirical Study on CodeBERT" (code models, not my use case ✗)
  - "QStore: Quantization-Aware Compressed Model Storage" (storage, not inference ✗)
  - "Reasoning Efficiently Through Adaptive Chain-of-Thought Compression" (CoT, not quantization ✗)

**Critical Insight**: Advisor is much better than keyword search, but doesn't understand "production-ready" or "hardware metrics" constraints. It's finding compression papers, not deployment papers.

**Emotional State**: Fluctuated from 4/5 (hopeful when first 6 papers appeared) to 2/5 (disappointed when detailed query returned irrelevant papers)

**Delights**:
- Semantic search works! Much better than keyword
- Follow-up action buttons: "Find papers that cite these works", "Show me implementation code"

**Frustrations**:
- "Contextual synthesis temporarily unavailable" - core feature broken
- Doesn't filter for production constraints (latency, memory, real hardware)
- Mixes research papers with completely unrelated domains (mesh generation, chemical manufacturing)

---

### Step 4: Deep Dive - Examining Paper Analysis

**Screenshots**: `04-paper-detail.png`, `04b-paper-expanded.png`

**Paper**: SingleQuant: Efficient Quantization of LLMs in a Single Pass

**Expanded View**:
- Full abstract displayed
- Tabs: Summary | Related Papers | Benchmarks
- Buttons: "Read on arXiv", "Generate Code"

**Critical Missing**:
- **No production metrics**: Claims "1,400× quantization speedup" but no wall-clock time, memory usage, or throughput
- **No hardware details**: Tested on what GPU? CPU? Mobile?
- **No code quality indicators**: Is there a GitHub repo? How many stars? Is it maintained?
- **Abstract only reports accuracy**: "+0.57% average task performance" - I need latency

**Tabs Tested**:
- **Summary tab**: Didn't load or change view (screenshots 06, 07 show same content)
- **Related Papers tab**: Didn't load
- **Benchmarks tab**: Didn't load

**Emotional State**: 3/5 (Neutral - paper is relevant but missing critical production info)

**What Papers with Code Shows That This Doesn't**:
- GitHub stars, forks, last commit date
- Links to official implementations
- Hardware: GPU model, batch size, precision
- Latency benchmarks (ms/token, throughput)
- Memory footprint (GB)

---

### Step 5: Code Availability Check

**Screenshots**: `05-has-code-filter.png`

**Action**: Applied "Has Code" filter from sidebar

**Result**:
- Filter applied successfully (shown as active chip)
- Still 6 papers (same count)
- **No visual indicators of code availability on paper cards**
- **No GitHub links visible**
- **No code quality metrics** (stars, forks, recency)

**Critical Gap**: "Has Code" is binary, but code quality varies 1000x:
- Research prototype that runs once on author's machine
- Maintained library with 10K+ GitHub stars, CI/CD, documentation
- Production-grade with TensorRT/ONNX export, benchmarks on multiple GPUs

**Papers with Code Advantage**:
- Shows GitHub stars prominently
- Links to official vs unofficial implementations
- Community rankings by stars/usage
- Can filter by "Minimum 100 stars" (proxy for quality)

**Emotional State**: 2/5 (Frustrated - "Has Code" doesn't mean "Has Usable Code")

---

## Pain Points Assessment

**Did AI Paper Atlas solve my production ML pain points?**

| Pain Point | Solved? | Evidence |
|-----------|---------|----------|
| **1. Academic Hype Filter** | ⚠️ Partial | Advisor found relevant papers, but no production metrics to validate claims |
| **2. Production Constraints** | ❌ No | No latency, memory, or throughput metrics. Abstract only shows accuracy |
| **3. Code Quality** | ❌ No | "Has Code" filter exists but no quality indicators (stars, maintenance, real tests) |
| **4. Time to Value** | ⚠️ Partial | Advisor saved time vs keyword search, but still need to read papers to assess deployability |
| **5. Reproducibility** | ❌ No | No hardware details, no benchmark transparency, no deployment guides |

**Overall**: 1/5 pain points fully solved. Advisor is better than keyword search, but production engineers need deployment-focused filters and metrics.

---

## Production Utility Assessment

**For a production ML engineer evaluating model compression, I need**:

### CRITICAL (Must-Have):
1. **✗ Hardware-specific benchmarks**: Latency on T4 vs A100 vs CPU
2. **✗ Memory footprint**: Model size (GB), peak RAM during inference
3. **✗ Throughput metrics**: Tokens/sec, QPS, batch size effects
4. **✗ Code maturity**: GitHub stars, last commit, issue count, CI status
5. **✗ Deployment readiness**: ONNX export, TensorRT support, quantization format (INT8, FP16)

### IMPORTANT (Should-Have):
6. **✗ Trade-off clarity**: Latency vs accuracy plots, Pareto frontiers
7. **✗ Industry validation**: Used by what companies? What scale?
8. **✗ Integration guides**: Works with HuggingFace? PyTorch? TensorFlow?
9. **⚠️ Related work**: Advisor shows related papers (partial credit)
10. **✗ Failure modes**: What scenarios break? Known limitations?

### Score: 0.5/10 for production utility
- Advisor finds relevant papers (better than arXiv search)
- But missing ALL production-critical metadata
- Can't replace Papers with Code for deployment decisions

---

## Code Quality Evaluation

**"Has Code" filter exists, but lacks depth**:

**What I Need to Assess Code**:
1. **Repository health**:
   - GitHub stars (proxy for community trust)
   - Last commit date (is it maintained?)
   - Open issues vs closed (is it supported?)
   - Contributors (one-person project vs team?)

2. **Code quality indicators**:
   - CI/CD badges (tests passing?)
   - Documentation quality (quickstart, API reference)
   - Example scripts (can I run it in 5 minutes?)
   - Benchmark reproduction (scripts to verify paper claims)

3. **Production readiness**:
   - Export formats (ONNX, TensorRT, CoreML)
   - Platform support (Linux, Windows, mobile)
   - Dependencies (lightweight vs bloated)
   - License (can I use commercially?)

**Current State**: Binary "Has Code" checkbox with no quality signals

**Papers with Code Does This Well**:
- Shows GitHub stars next to each implementation
- Links to official vs community implementations
- Ranks by popularity (stars)
- Shows framework (PyTorch, TensorFlow, JAX)

**Emotional State**: 2/5 (Frustrated - Can't evaluate if code is production-ready without leaving the site)

---

## Time-to-Value for Practitioners

**From landing page to actionable decision**: Too long, incomplete

**Steps Taken**:
1. Keyword search → failed (30 irrelevant papers)
2. Advisor search → partial success (4/6 relevant papers)
3. Detailed advisor query → failed (returned code models, not inference optimization)
4. Click through to paper → no production metrics visible
5. Need to: Read abstract → Find GitHub → Clone → Test → Benchmark
6. **Estimated time to deployment decision**: 2-4 hours per paper

**Papers with Code Comparison**:
1. Search "quantization" → immediate results
2. Sort by GitHub stars → see most-used implementations
3. Click top result → see benchmarks, hardware, code link
4. **Estimated time to deployment decision**: 15 minutes per paper

**Verdict**: AI Paper Atlas adds research context (related papers, advisor chat) but doesn't reduce evaluation time for production deployment.

**Emotional State**: 2/5 (Frustrated - Tool optimized for researchers, not engineers)

---

## Comparison to Papers with Code

**Why I still need Papers with Code**:

| Feature | Papers with Code | AI Paper Atlas | Winner |
|---------|-----------------|----------------|--------|
| **Search relevance** | Keyword + tags | Semantic (Advisor) | **Atlas** (when Advisor works) |
| **Code discovery** | GitHub stars, official badge | Binary "Has Code" | **PwC** |
| **Benchmarks** | Standardized leaderboards | Abstract mentions only | **PwC** |
| **Hardware details** | GPU model, batch size | Not shown | **PwC** |
| **Production metrics** | Latency, memory, FLOPs | Accuracy only | **PwC** |
| **Code quality** | Stars, forks, recency | Not shown | **PwC** |
| **Reproducibility** | Dataset links, repro scripts | Not shown | **PwC** |
| **Related work** | Manual exploration | Advisor + tabs | **Atlas** (if tabs worked) |
| **Learning curve** | Flat | Good (clean UI) | **Atlas** |
| **Community trust** | High (10K+ stars for top papers) | Unknown (no signals) | **PwC** |

**Overall**: Papers with Code wins 7/10 categories for production work

**When AI Paper Atlas is Better**:
- Semantic search (Advisor understands intent)
- Exploring related work (if tabs worked)
- Natural language queries ("what are alternatives?")

**When Papers with Code is Better**:
- Evaluating code quality (stars, maintenance)
- Finding production-ready implementations
- Comparing quantitative benchmarks
- Hardware-specific performance

**Emotional State**: 2/5 (Disappointed - Expected "AI-powered" to mean smarter filters for production constraints)

---

## Delights

1. **Research Advisor semantic search**: 8-second query found 4/6 relevant papers, much better than keyword search
2. **Follow-up actions**: "Find papers that cite these works", "What are alternative approaches?" - great for exploration
3. **Clean UI**: Not overwhelming, easy to scan results
4. **"Generate Code" feature**: Didn't test, but interesting concept for prototyping

---

## Frustrations

1. **No production metrics**: Latency, memory, throughput completely absent. Only accuracy reported.
2. **"Has Code" too shallow**: Binary flag, no quality indicators (GitHub stars, maintenance, tests)
3. **Advisor inconsistency**: First query found quantization papers, second query (more detailed) returned unrelated compression papers
4. **Broken features**: "Contextual synthesis temporarily unavailable" on second advisor query
5. **Tabs don't work**: Summary, Related Papers, Benchmarks tabs showed same content (or didn't load)
6. **No hardware filters**: Can't filter by "Benchmarked on T4 GPU" or "Mobile-optimized"
7. **Missing deployment signals**: No ONNX/TensorRT tags, no inference framework tags
8. **Can't assess reproducibility**: No links to datasets, benchmark scripts, or hardware specs

---

## Performance Metrics

**Page Load Time**: Not measured (navigation was instant, assumed SSR/cached)
**Search Response Time**:
- Keyword search: Instant (<100ms)
- Advisor first query: 8004ms (8 seconds)
- Advisor second query: Not measured (waited ~10s)

**Perceived Performance**: Fast for keyword search, slow for Advisor (8s feels long when Papers with Code is instant)

**Bottleneck**: Advisor likely doing semantic search + re-ranking on backend. Need streaming responses or progress indicator.

---

## Priority Improvements (Impact/Effort)

### 🔴 CRITICAL (High Impact, Medium-High Effort)

1. **Add production metric extraction** [Impact: 10/10, Effort: 8/10]
   - Parse abstracts/methods for latency, memory, throughput
   - Surface as badges: "🚀 15ms latency on T4", "💾 2.1GB model"
   - Allow filtering: "Show only papers with GPU benchmarks"

2. **Code quality indicators** [Impact: 10/10, Effort: 6/10]
   - Fetch GitHub stars, last commit, issues from GitHub API
   - Show maintainability score: "⭐ 5.2K stars, updated 2 days ago"
   - Filter: "Minimum 500 stars" (proxy for battle-tested)

3. **Hardware-specific filters** [Impact: 9/10, Effort: 7/10]
   - Tags: "T4", "A100", "V100", "CPU", "Mobile", "Edge"
   - Allows: "Show quantization papers benchmarked on T4 GPU"

### 🟡 IMPORTANT (High Impact, Low-Medium Effort)

4. **Fix Advisor consistency** [Impact: 8/10, Effort: 5/10]
   - Second query with more details returned worse results
   - Should: More specific query → More filtered results
   - Currently: More specific query → Different random papers

5. **Production readiness tags** [Impact: 8/10, Effort: 4/10]
   - Tags: "ONNX Export", "TensorRT Ready", "HuggingFace Integration"
   - Source from README badges, code analysis, or manual curation

6. **Benchmark standardization** [Impact: 9/10, Effort: 9/10]
   - Leaderboards like Papers with Code
   - Standardized metrics: Latency (p50, p99), Memory (peak, average), Throughput
   - Apples-to-apples comparison (same hardware, batch size, precision)

### 🟢 NICE-TO-HAVE (Medium Impact, Low Effort)

7. **Code preview** [Impact: 6/10, Effort: 3/10]
   - Embed README snippet or quickstart from GitHub
   - Show: "Can I run this in 5 minutes?"

8. **Deployment checklist** [Impact: 7/10, Effort: 6/10]
   - For each paper, surface: ✓ Code, ✓ Benchmarks, ✓ Hardware details, ✗ Mobile support
   - Traffic light: 🟢 Production-ready, 🟡 Needs work, 🔴 Research-only

9. **Fix tabs UI** [Impact: 5/10, Effort: 2/10]
   - Summary, Related Papers, Benchmarks tabs didn't change content
   - Likely JavaScript bug

10. **Industry validation tags** [Impact: 6/10, Effort: 8/10]
    - Tags: "Used at: Meta", "Deployed in: WhatsApp", "Scale: 1B+ users"
    - Source from blog posts, talks, or manual curation

---

## Screenshots Index

| # | Filename | Description | Key Observations |
|---|----------|-------------|------------------|
| 01 | `01-landing-first-impression.png` | Landing page | Clean UI, "Has Code" filter visible, 30 papers |
| 02 | `02a-nav-generate.png` | Generate tab | Code generation feature, not relevant for search |
| 03a | `03a-search-query-entered.png` | Keyword search: "model quantization production" | 30 results, all irrelevant (CV papers) |
| 03b | `03b-advisor-loading.png` | Research Advisor opened | 6 quantization papers found in 8s |
| 03c | `03c-advisor-query-typed.png` | Detailed production query entered | Long query about latency/memory metrics |
| 03d | `03d-advisor-response.png` | Advisor response | Returned CodeBERT paper (unrelated), "Contextual synthesis unavailable" |
| 04 | `04-paper-detail.png` | Advisor panel with papers | Follow-up action buttons visible |
| 04b | `04b-paper-expanded.png` | SingleQuant paper expanded | Abstract visible, tabs present but not functional |
| 05 | `05-has-code-filter.png` | "Has Code" filter applied | No GitHub stars or quality indicators shown |
| 06 | `06-related-papers-tab.png` | Attempted to click Related Papers tab | Tab didn't change view |
| 07 | `07-benchmarks-tab.png` | Attempted to click Benchmarks tab | Tab didn't change view |
| 08 | `08-filter-cleared.png` | Filter state | Same view, filter still active |
| 09 | `09-second-search-pruning.png` | Attempted second search | Same view, no change |
| 10 | `10-paper-collapsed.png` | Paper collapsed | Back to list view |
| 11 | `11-trending-hot-topics.png` | Trending Hot Topics tab | No data available |
| 12 | `12-trending-rising.png` | Trending Rising tab | No data available |
| 13 | `13-final-state.png` | Final state | End of session |

---

## Final Verdict

**Would I use this instead of Papers with Code?** **No**, not for production work.

**Why Not?**
1. **Missing production metrics**: Can't evaluate if technique will work at scale without latency/memory data
2. **No code quality signals**: "Has Code" doesn't mean "Has Production-Ready Code"
3. **No hardware filters**: Can't find T4-optimized vs A100-optimized techniques
4. **Advisor unreliable**: Second query returned unrelated papers, core synthesis feature broken

**Would I recommend to my team?** **Not yet**, but I'm watching.

**What Would Change My Mind?**
- Add GitHub stars/maintenance to each paper
- Extract and display production metrics (latency, memory) from abstracts
- Fix Advisor consistency (more specific query should = better results)
- Add hardware-specific filters ("Show T4 benchmarks only")

**Current Use Case**:
- Good for: Exploring research landscape, finding related work, semantic search
- Bad for: Production deployment decisions, code quality assessment, hardware-specific optimization

**Realistic Workflow**:
1. Use AI Paper Atlas Advisor to find candidate papers (better than arXiv search)
2. Switch to Papers with Code to evaluate code quality and benchmarks
3. Read top 3 papers' GitHub repos to assess production readiness
4. Benchmark top 1-2 on our hardware to validate claims

**Time Saved**: Minimal. Advisor saves 10 minutes on discovery, but I still need Papers with Code for evaluation.

**Rating**: 2.5/5 for production ML engineers
- 4/5 for research exploration (Advisor is good)
- 1/5 for deployment evaluation (missing all critical signals)

**Bottom Line**: Tool is built for researchers, not practitioners. The "AI-powered" search is clever, but production engineers need data-driven filters (metrics, hardware, code quality), not just semantic matching.

---

## Technical Notes

**Browser**: Chrome (instance 4)
**Viewport**: 1440x900
**Network**: No throttling
**Performance**: Advisor queries took 8+ seconds (may need optimization)
**Bugs Encountered**:
- Tabs (Summary, Related, Benchmarks) didn't change content when clicked
- "Contextual synthesis temporarily unavailable" on second Advisor query
- Trending tabs showed "No trending data available"

**Accessibility**: Not tested (focused on functionality for production use case)

---

**End of Report**
