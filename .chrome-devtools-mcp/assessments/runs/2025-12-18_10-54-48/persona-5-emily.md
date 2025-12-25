# UX Assessment Report: Dr. Emily Zhang
## Interdisciplinary Climate Science Researcher

**Date:** 2025-12-18
**Session Duration:** 10:55:13 - 10:59:54 (~5 minutes)
**Persona:** Dr. Emily Zhang - Climate & Energy Sciences Researcher at National Lab
**Research Focus:** Applying ML to climate modeling and weather prediction

---

## Executive Summary

As an atmospheric scientist learning ML, I found AI Paper Atlas helpful for discovering transformer architectures applicable to climate data. The semantic search successfully bridged my domain terminology (weather, climate, physical systems) with ML papers. However, the Research Advisor feature failed completely, and the interface assumes ML expertise I don't have. The tool shows promise for cross-domain discovery but needs better accessibility for domain scientists.

**Would I use it again?** Yes, cautiously - the search works well enough to find relevant papers, but I'd need to learn ML jargon first.

---

## Session Timeline & Metrics

| Time | Step | Action | Outcome | Emotion |
|------|------|--------|---------|---------|
| 10:55:13 | 0 | Environment setup | Viewport 1440x900 | 3/5 |
| 10:55:20 | 1 | Landing page load | Clean but ML-jargon heavy | 3/5 |
| 10:55:48 | 2 | Explored Generate page | Code generation - interesting but not immediate need | 3/5 |
| 10:56:00 | 3 | First search: "transformers time series weather prediction" | Found 30 relevant papers in 3732ms, PFformer looks perfect! | 4/5 |
| 10:56:24 | 3.5 | Tried Research Advisor | **FAILED** - Error message. Feature broken. | 2/5 |
| 10:57:30 | 4 | Expanded PFformer paper | Full abstract helpful, mentions weather explicitly | 4/5 |
| 10:57:45 | 5 | Clicked "Related Papers" | Loading... feature appears to work | 3/5 |
| 10:58:00 | 6 | Applied "Has Code" filter | Fast re-search (759ms), same 6 papers | 3/5 |
| 10:58:30 | 7 | Cross-domain search: "neural networks physical systems climate" | Found physics-ML bridge papers! Granger Causality, thermodynamics | 4/5 |
| 10:59:54 | 12 | Final reflection | Overall positive despite Advisor failure | 3.5/5 |

**Average Emotion Score:** 3.4/5 (Cautiously optimistic)

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

**Screenshot:** `01-landing-first-impression.png`

**What I Saw:**
- Clean, minimalist interface with large search box
- Sidebar filters: "Has Code", "High Impact", Category filters, Difficulty levels
- Suggested queries displayed: "Latest advances in LLM reasoning", "Techniques for reducing hallucinations"
- 138,986 papers indexed (impressive!)

**Immediate Reactions:**
- **Positive:** Search box is prominent and inviting. The sheer number of papers is reassuring.
- **Concern:** All example queries use ML jargon I barely understand ("LLM reasoning"? "hallucinations"?). These don't speak to my domain at all. Where are examples like "weather prediction" or "time series for climate data"?
- **Terminology gap:** The "Difficulty" filter assumes I know what "Beginner" means in ML context. Beginner for whom? An ML PhD student?

**Verdict:** The interface looks professional, but it's clearly built by ML people for ML people. I'm not sure if it will understand my climate science vocabulary.

**Emotion:** 3/5 - Neutral with slight trepidation

---

### Step 2: Navigation Discovery

**Screenshot:** `02-generate-page.png`

**What I Explored:**
- Clicked "Generate" tab out of curiosity
- Found "Multi-Agent Code Generation" feature that turns papers into working code
- 5-agent system: Paper Analyzer → Test Designer → Code Generator → Test Executor → Debugger

**Reactions:**
- **Interesting conceptually:** If I could turn a weather prediction paper into runnable Python code, that would save weeks of work.
- **Skepticism:** Can this really work for climate modeling papers? Those often require domain-specific data formats, physical constants, boundary conditions...
- **Not my immediate need:** I need to *find* the right papers first before worrying about implementation.

**Verdict:** Cool feature but premature for my workflow. Would revisit after finding relevant papers.

**Emotion:** 3/5 - Curious but not convinced

---

### Step 3: Task-Based Search - Finding Transformer Papers

**Screenshot:** `03-search-typed.png`

**Search Query:** "transformers time series weather prediction"

**What Happened:**
- Search returned **30 results** in **3732ms** (~3.7 seconds - fast!)
- Results labeled "Smart Results ✦ AI-POWERED"
- **Top result: "PFformer: A Position-Free Transformer Variant for Extreme-Adaptive Multivariate Time Series Forecasting"**
  - TL;DR mentions: "Multivariate time series (MTS) forecasting is vital in fields like weather, energy, and finance..."
  - This is EXACTLY what I need!

**Other Relevant Results:**
- "Leveraging Time Series Categorization and Temporal Fusion Transformers" (cryptocurrency - less relevant but shows technique transfer)
- "BEAT: Balanced Frequency Adaptive Tuning for Long-Term Time-Series Forecasting" (weather prediction mentioned)
- "UNet with Axial Transformer: A Neural Weather Model for Precipitation Nowcasting" (**Perfect match!**)

**Reactions:**
- **Delight:** The semantic search understood my domain terminology! It didn't just match keywords - it found papers that bridge transformers with weather/climate applications.
- **Confidence boost:** Maybe this tool *can* understand cross-domain queries.
- **TL;DR summaries are helpful:** I can quickly scan which papers are worth reading without diving into abstracts.

**Verdict:** This is the core value - finding ML techniques applicable to my domain. Search quality exceeded expectations.

**Emotion:** 4/5 - Excited and hopeful

**Performance Note:** 3.7 seconds feels acceptable for semantic search over 138k papers. Not instant, but reasonable.

---

### Step 3.5: Research Advisor Failure

**Screenshots:** `04-advisor-opened.png`, `05-advisor-query-typed.png`, `06-advisor-error.png`

**What I Tried:**
- Clicked "Ask Advisor" button next to search
- Panel opened with friendly greeting: "Hi! I'm your Research Advisor..."
- Typed natural language query: *"I'm applying ML to climate modeling for long-range weather prediction. What transformer architectures work well for physical time series data with spatial-temporal dependencies?"*
- Clicked submit

**Result:** **ERROR MESSAGE** - "Sorry, I encountered an error while searching. Please try again."

**Reactions:**
- **Frustration:** This was the feature I was most excited about! Natural language queries are how domain scientists think.
- **Disappointment:** The example queries shown (LLM reasoning, hallucinations, fine-tuning) are all ML-centric. My climate-focused query broke it.
- **Lost opportunity:** This could have been the killer feature for interdisciplinary researchers. Instead, it's broken.
- **Trust erosion:** If the "AI-powered" advisor doesn't work, what else is broken?

**Verdict:** Critical feature failure. This undermines the product's promise for domain scientists.

**Emotion:** 2/5 - Frustrated and disappointed

**Error Analysis:** The error message is generic ("encountered an error"). No indication if:
- My query was too long?
- The backend timed out?
- The system can't handle cross-domain queries?
Better error handling would help.

---

### Step 4: Deep Dive - PFformer Paper Analysis

**Screenshot:** `07-paper-expanded.png`

**What I Did:**
- Clicked "Expand" on the PFformer paper
- Viewed full abstract

**Full Abstract Key Points:**
- ✅ "Multivariate time series (MTS) forecasting is vital in fields like **weather**, energy, and finance"
- ✅ Handles "rare or extreme events" (important for climate!)
- ✅ "position-free Transformer" - novel architecture I hadn't heard of
- ✅ Tested on "long sequence prediction for 3 days ahead" and "rolling predictions every four hours" (realistic timescales)
- ✅ "20% to 60% improvement" over state-of-the-art

**Available Actions:**
- "Read on arXiv" link (opens paper)
- "Generate Code" link (interesting!)
- Tabs: Summary | Related Papers | Benchmarks

**Reactions:**
- **High relevance:** This paper explicitly addresses weather forecasting, my exact use case.
- **Technical accessibility:** The abstract is readable! It explains the problem before diving into technical details.
- **Actionable:** Links to full paper and code generation give clear next steps.
- **Missing:** No indication if code is available. Is there a GitHub repo? This matters for reproducibility.

**Verdict:** The paper detail view provides enough information to decide if it's worth reading the full paper.

**Emotion:** 4/5 - Satisfied with depth of information

**Missing Feature:** A "Has Code" badge directly on the paper card (visible without expanding) would be helpful.

---

### Step 5: Code Availability Check

**Screenshot:** `09-has-code-filter-searching.png`

**What I Did:**
- Clicked "Has Code" filter in sidebar
- System re-searched with filter applied

**Results:**
- **Same 6 papers** returned
- Search completed in **759ms** (very fast!)
- All 6 papers apparently have code

**Reactions:**
- **Unclear:** Do all these papers actually have GitHub repos? Or is "Has Code" inferred from paper content?
- **Speed appreciated:** Sub-second filter application is excellent.
- **Desire for visibility:** I want to see GitHub stars, language (Python? Julia?), and last commit date. Helps assess code quality and maintenance.

**Verdict:** Filter works quickly but lacks transparency about what "Has Code" means.

**Emotion:** 3/5 - Functional but incomplete

**Improvement Needed:** Show code metadata directly (language, stars, activity) without requiring navigation to GitHub.

---

### Step 7: Cross-Domain Discovery Test

**Screenshot:** `10-cross-domain-search.png`

**Search Query:** "neural networks physical systems climate"

**Results:**
- **6 papers** in **2590ms**
- **Top result: "Granger Causality Detection with Kolmogorov-Arnold Networks"**
  - TL;DR: "Discovering causal relationships in time series data is central in many scientific areas, ranging from economics to **climate science**."
  - This bridges ML techniques (Granger causality, KANs) with climate applications!
- **Second result: "An introduction to Neural Networks for Physicists"**
  - Educational paper explaining ML concepts in physics terms
  - Exactly what I need to onboard my team!

**Other Papers Found:**
- Hopfield networks for biology
- Thermodynamic bounds on DNNs
- Physical learning systems

**Reactions:**
- **Delight:** The search found papers at the ML-physics interface, not just pure ML or pure climate.
- **Educational value:** Papers like "Neural Networks for Physicists" are gold for interdisciplinary teams.
- **Terminology translation:** The tool successfully mapped my domain language ("physical systems", "climate") to relevant ML work.

**Verdict:** This is where the tool shines - discovering cross-domain connections that Google Scholar would miss.

**Emotion:** 4/5 - Genuinely impressed

**Key Insight:** The semantic search understands domain context, not just keywords. This is critical for interdisciplinary research.

---

### Screenshot Evidence (Additional Captures)

**Screenshot:** `08-related-papers-loading.png`
- Related Papers feature showed "Finding similar papers..." spinner
- Feature appears to work but didn't complete during my session
- Would be useful to explore paper networks

**Screenshot:** `11-physics-ml-papers.png`
- Bottom of cross-domain search results
- Shows diverse physics-ML connections (biology, thermodynamics, physical systems)
- Demonstrates breadth of interdisciplinary coverage

---

## Pain Point Assessment

**Original Pain Points vs. Outcomes:**

### 1. Terminology Gap ❌ PARTIALLY SOLVED
**Problem:** ML papers use different terminology than climate science.

**Outcome:**
- ✅ Search successfully mapped my domain terms to ML papers
- ✅ Found papers explicitly mentioning weather/climate applications
- ❌ Interface still uses ML jargon ("LLM", "hallucinations", "fine-tuning")
- ❌ No glossary or term explanations for domain scientists

**Improvement Needed:** Add a "Learning Mode" that explains ML concepts in domain-neutral language.

---

### 2. Cross-Domain Discovery ✅ SOLVED
**Problem:** Techniques from NLP/vision might apply to climate but published in venues I don't follow.

**Outcome:**
- ✅ Search found transformer papers from computer vision applied to time series
- ✅ Discovered "Neural Networks for Physicists" educational paper
- ✅ Granger Causality paper explicitly bridges economics, climate, and ML

**Why it worked:** Semantic search understands conceptual similarity beyond keyword matching.

---

### 3. Adaptation Complexity ⚠️ PARTIALLY ADDRESSED
**Problem:** Hard to know which ML methods will transfer to physical science data.

**Outcome:**
- ✅ Papers like PFformer explicitly tested on weather/energy/finance data
- ✅ Abstracts often mention "multivariate time series" (my domain)
- ❌ No explicit "transfer potential" assessment
- ❌ Can't filter by "applied to physical sciences" as a category

**Improvement Needed:** Tag papers by application domain. Add filter: "Applied to: [Climate | Physics | Biology | ...]"

---

### 4. Limited ML Background ❌ NOT ADDRESSED
**Problem:** Haven't read "foundational" ML papers. Miss context ML researchers assume.

**Outcome:**
- ❌ No learning path or prerequisite suggestions
- ❌ "Difficulty" filter unclear (beginner for whom?)
- ❌ No explanations of assumed ML knowledge

**Critical Gap:** The tool assumes ML literacy. Domain scientists need scaffolding.

**Improvement Needed:**
- Add "Prerequisites" section to papers
- Suggest foundational papers to read first
- Explain concepts like "attention mechanism" in hover-tooltips

---

### 5. Justification to Peers ⚠️ PARTIALLY SUPPORTED
**Problem:** Need to justify ML approaches to skeptical climate scientists.

**Outcome:**
- ✅ Papers showing quantitative improvements (e.g., "20-60% better than state-of-the-art")
- ✅ Applications to real-world climate data would help credibility
- ❌ No section on interpretability or explainability
- ❌ Can't filter for "interpretable methods"

**Improvement Needed:** Add interpretability metadata. Climate scientists distrust black boxes.

---

## Delights & Frustrations

### 😊 Delights

1. **Semantic search quality** (4/5)
   - Found domain-relevant papers despite using climate science terminology
   - PFformer paper was a perfect match - exactly what I needed
   - Cross-domain connections discovered (physics, climate, ML)

2. **Search speed** (4/5)
   - Initial search: 3732ms (~3.7s)
   - Filtered search: 759ms (<1s)
   - Fast enough to iterate on queries

3. **TL;DR summaries** (4/5)
   - Quickly scan 20+ papers without reading full abstracts
   - Identify relevant papers in seconds
   - Saves significant time vs. arXiv browsing

4. **Cross-domain bridge papers** (5/5)
   - "Neural Networks for Physicists" - perfect onboarding resource
   - Granger Causality linking climate + ML - wouldn't find this on Google Scholar
   - Educational value for my team

---

### 😞 Frustrations

1. **Research Advisor completely broken** (1/5 - Critical failure)
   - This was the most promising feature for natural language queries
   - Error message gave no actionable feedback
   - Lost opportunity for domain scientists who think in questions, not keywords

2. **ML jargon everywhere** (2/5)
   - Example queries assume ML expertise ("LLM reasoning", "hallucinations")
   - No definitions or explanations
   - Feels like tool wasn't tested with domain scientists

3. **Code availability unclear** (2/5)
   - "Has Code" filter doesn't show: GitHub link, stars, language, last update
   - Can't assess code quality without clicking through
   - Reproducibility is critical in climate science

4. **No learning path** (2/5)
   - No guidance on prerequisite knowledge
   - "Difficulty" filter meaningless without context
   - Would help to know "Read papers A, B, C before this one"

5. **Missing interpretability metadata** (3/5)
   - Can't filter for explainable methods
   - No tags for "physics-informed", "interpretable", "causal"
   - Climate scientists need to justify black boxes to peers

---

## Performance Metrics

### Load Times
- Landing page: Not measured (instant)
- First search (30 results): **3732ms** (3.7s)
- Filtered search (6 results): **759ms** (<1s)
- Cross-domain search (6 results): **2590ms** (2.6s)

**Assessment:** Search times acceptable for semantic search over 138k papers. Under 4 seconds feels responsive.

---

### Research Advisor
- **Status:** FAILED
- **Time to error:** ~3-5 seconds
- **User impact:** Critical feature unusable

---

### Paper Detail View
- Expansion: Instant (client-side)
- "Related Papers" tab: Loading... (didn't complete during session)

---

## Accessibility for Non-ML Experts

**Current State:** 2/5 - Poor

### What Works:
- ✅ Search accepts domain terminology (not just ML keywords)
- ✅ Paper abstracts often readable by domain scientists
- ✅ Some papers explicitly bridge domains ("for Physicists")

### What Doesn't Work:
- ❌ Interface assumes ML vocabulary knowledge
- ❌ No explanations of ML concepts
- ❌ Example queries alienate domain scientists
- ❌ "Difficulty" rating unclear without ML context
- ❌ No onboarding for interdisciplinary users

### Recommendations:
1. **Add "Domain Scientist Mode"**
   - Show ML concept definitions on hover
   - Provide example queries from different domains (climate, bio, physics)
   - Filter by "Accessibility: [Beginner | Domain Expert | ML Expert]"

2. **Create bridging content**
   - "ML Concepts for Climate Scientists" guide
   - Glossary of ML terms with domain examples
   - "Start here" reading paths

3. **Improve terminology**
   - Replace "Difficulty" with "Assumed Background: [Minimal | Some ML | Advanced ML]"
   - Add domain tags: [Climate | Physics | Biology | General ML]

---

## Transfer Potential Evaluation

**Question:** Does the tool surface ML techniques that will actually work on climate data?

**Assessment:** 3.5/5 - Good but could be better

### What the Tool Did Well:
- ✅ PFformer paper tested on weather data (direct applicability)
- ✅ Papers mention "multivariate time series" (my data type)
- ✅ Some papers discuss extreme events, rare occurrences (climate relevant)
- ✅ Cross-domain papers show successful transfers (NLP → time series)

### What's Missing:
- ❌ No explicit "Transfer Potential" score or assessment
- ❌ Can't filter by "Tested on physical science data"
- ❌ No indication if method requires large datasets (climate data often limited)
- ❌ No discussion of data requirements (temporal resolution, spatial coverage)

### Improvement Ideas:
1. **Add metadata tags:**
   - "Tested on: [Climate | Biology | Finance | Synthetic]"
   - "Data requirements: [Small | Medium | Large]"
   - "Domain assumptions: [General | Physics-informed | Domain-agnostic]"

2. **Show applicability score:**
   - "Transfer potential to climate: 8/10" (based on paper content analysis)
   - Explain: "High - tested on weather data with similar characteristics"

3. **Surface limitations:**
   - "Requires: 100k+ training examples" (may not work for rare climate events)
   - "Assumes: IID data" (climate has spatial autocorrelation)

---

## Priority Improvements

### Critical (Fix Before Next User)

| # | Issue | Impact | Effort | Improvement |
|---|-------|--------|--------|-------------|
| 1 | Research Advisor broken | **HIGH** | **MEDIUM** | Fix error handling, test cross-domain queries, provide better error messages |
| 2 | ML jargon alienates domain scientists | **HIGH** | **LOW** | Update example queries to show domain science examples (weather, biology, physics) |
| 3 | Code availability unclear | **MEDIUM** | **LOW** | Show GitHub link, stars, language directly on paper cards |

---

### Important (Enhance Core Value)

| # | Issue | Impact | Effort | Improvement |
|---|-------|--------|--------|-------------|
| 4 | No learning path for prerequisites | **MEDIUM** | **MEDIUM** | Add "Prerequisites" section suggesting foundational papers to read first |
| 5 | "Difficulty" rating unclear | **MEDIUM** | **LOW** | Replace with "Assumed Background" and explain what each level means |
| 6 | Missing interpretability filters | **MEDIUM** | **MEDIUM** | Add tags for "Interpretable", "Physics-informed", "Explainable" methods |

---

### Nice-to-Have (Polish)

| # | Issue | Impact | Effort | Improvement |
|---|-------|--------|--------|-------------|
| 7 | No domain tags on papers | **LOW** | **MEDIUM** | Tag papers by application domain (Climate, Physics, Biology, etc.) |
| 8 | Related Papers slow/incomplete | **LOW** | **MEDIUM** | Optimize related papers lookup for faster response |
| 9 | No hover-tooltips for ML terms | **LOW** | **HIGH** | Add glossary tooltips for common ML jargon |

---

## Screenshots Index

1. **01-landing-first-impression.png** - Clean interface but ML jargon heavy ("LLM reasoning", "hallucinations"). Search looks approachable.

2. **02-generate-page.png** - Code generation page. Interesting for reproducibility but not my immediate need.

3. **03-search-typed.png** - Smart search found 30+ relevant time series papers! "PFformer" looks perfect for my work.

4. **04-advisor-opened.png** - Advisor panel clean and inviting. Example queries are ML-focused, not domain science.

5. **05-advisor-query-typed.png** - Natural language query entered about climate ML needs. Hopeful.

6. **06-advisor-error.png** - Advisor failed with error message. Feature broken. Very disappointing.

7. **07-paper-expanded.png** - PFformer paper details helpful. Abstract mentions weather explicitly!

8. **08-related-papers-loading.png** - Related papers feature loading. Appears to work but slow.

9. **09-has-code-filter-searching.png** - Code filter applied, still showing 6 papers. Fast search (759ms).

10. **10-cross-domain-search.png** - Cross-domain search found climate science papers! "Granger Causality" paper bridges domains.

11. **11-physics-ml-papers.png** - Physics-ML papers like biology networks and thermodynamics. Domain bridging works!

---

## Final Verdict

### Would I Bookmark This Tool?
**Yes** - The search quality alone makes it valuable.

### Would I Return Tomorrow?
**Maybe** - Only if I'm actively looking for papers. Not a daily-use tool.

### Would I Recommend to Colleagues?
**Yes, with caveats** - "It works well but assumes you know ML jargon. Don't rely on the Research Advisor."

---

## Summary for Product Team

**What's Working:**
- Semantic search successfully bridges domain terminology gaps
- Cross-domain discovery is excellent - finds physics-ML connections I wouldn't find elsewhere
- Search speed acceptable (< 4 seconds for complex queries)
- TL;DR summaries save time

**What's Broken:**
- Research Advisor completely fails on cross-domain queries (critical bug)
- Interface assumes ML expertise throughout
- No onboarding or learning path for domain scientists

**Biggest Opportunity:**
The tool has the potential to become THE platform for interdisciplinary ML research, but only if it stops assuming everyone speaks ML fluently. Add domain science affordances, fix the Advisor, and this becomes indispensable for researchers like me.

**For Emily Zhang (Climate Scientist):**
I'd cautiously use this tool to find transformer architectures for climate modeling. The search quality exceeded expectations - finding PFformer and the UNet weather paper alone justified the 5-minute session. However, the broken Research Advisor and ML-centric interface mean I'll need to learn more ML terminology before feeling fully comfortable. The tool *works* but doesn't feel like it was built for me.

**Emotional Arc:** Started neutral (3/5) → Excited by search quality (4/5) → Frustrated by Advisor failure (2/5) → Pleased by cross-domain results (4/5) → Ending cautiously optimistic (3.5/5)

**Bottom Line:** The tool bridges domains better than Google Scholar, but assumes too much ML literacy. Fix the Advisor, add domain scientist affordances, and this becomes a killer app for interdisciplinary research.

---

**Assessment completed by:** Dr. Emily Zhang (simulated persona)
**Total screenshots:** 11
**Total search queries:** 3
**Papers discovered:** 30+ relevant to climate modeling
**Broken features encountered:** 1 (Research Advisor)
**Would use again:** Yes, for paper discovery - with lowered expectations for AI features
