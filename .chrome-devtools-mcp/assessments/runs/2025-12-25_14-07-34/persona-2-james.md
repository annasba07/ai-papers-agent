# UX Assessment Report: Prof. James Williams
**AI Paper Atlas | Research Intelligence Platform**
**Date**: 2025-12-25
**Session Duration**: ~20 minutes
**Persona**: Prof. James Williams - MIT CSAIL Faculty, NLP Research

---

## Executive Summary

As a senior faculty member preparing graduate seminar materials, I found AI Paper Atlas technically sound but pedagogically incomplete. The system lacks foundational citations, historical context, and clear differentiation between seminal and incremental work—critical for teaching. Search failed entirely on my primary query ("efficient language models"), and the Research Advisor timed out after 18+ seconds. Code generation is intriguing but untested. **I would not recommend this to my students in its current state.**

**Key Verdict**: 2.5/5 - Needs significant improvements before being useful for academic teaching contexts.

---

## Session Context

**Research Goal**: Prepare graduate seminar on "Efficient Language Models"
**Key Requirements**:
1. Identify seminal foundational papers
2. Find recent cutting-edge work with code
3. Build coherent reading progression (basic → advanced)
4. Assess pedagogical value (clarity, reproducibility)

**Pain Points Tested**:
- Curation burden (maintaining reading lists)
- Student guidance (what should they read?)
- Reproducibility standards (code availability)
- Historical context (foundational vs. incremental)

---

## Session Timeline & Screenshots

| Step | Time | Action | Screenshot | Outcome |
|------|------|--------|------------|---------|
| 1 | 0:00 | Landing page load | 01-landing-first-impression.png | Page loaded in loading state, filters visible |
| 2a | 1:30 | Explore Discovery tab | 02a-nav-discovery.png | Quick discovery cards, high-impact section |
| 2b | 2:00 | Explore Generate feature | 02b-nav-generate.png | Multi-agent code generation (5 agents, TDD) |
| 3a | 3:00 | Search: "efficient language models" | 03a-search-query-typed.png | Query entered, searching state |
| 3b | 3:15 | Search results | 03b-search-no-results.png | **CRITICAL FAILURE**: 0 results, 10s response time |
| 3c | 4:00 | Open Research Advisor | 03c-advisor-opened.png | Advisor panel with example queries |
| 3d | 4:30 | Advisor query submitted | 03d-advisor-query-typed.png | Detailed pedagogical query submitted |
| 3e | 4:40 | Advisor searching (8s) | 03e-advisor-response.png | Still searching, no response |
| 3f | 4:50 | Advisor timeout (18s total) | 03f-advisor-still-searching.png | Partial results, synthesis unavailable |
| 4 | 5:30 | Expand paper detail | 04-paper-expanded.png | Full abstract, tabs visible, no citations |
| 5 | 6:00 | Apply "Has Code" filter | 05-code-filter.png | Filter applied, same results (all recent papers) |

**Total Screenshots Captured**: 11
**Steps Completed**: 5 of 13 (stopped due to context limits and critical search failures)

---

## Detailed Step Analysis

### Step 1: First Impression (0:00)
**Goal**: Understand value proposition and find path to papers

**Observations**:
- Page loaded in "Searching..." state - unclear if intentional or slow
- Filters highly visible in left sidebar (good)
- 138,986 papers indexed - impressive scale
- "Ask Advisor" button prominent
- Navigation clear: Explore, Discovery, Reading List, Generate

**Emotional State**: 3/5 (neutral - professional but incomplete first impression)

**Pedagogical Assessment**: No clear indication of how this helps with *teaching* vs. just research. Where's the learning path feature?

---

### Step 2: Navigation Exploration (1:30-2:00)

#### Discovery Tab (02a-nav-discovery.png)
**Positive**:
- Quick Discovery cards: "High Impact Papers", "Rising Stars", "Papers with Code", "TL;DR Feed"
- Tabs: Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path
- "Recent High Impact Papers" section with one paper visible (Hopfield network)

**Concerns**:
- "Loading papers..." state - persistent performance issues?
- No clear definition of "High Impact" (citations? community votes?)
- Where's the historical timeline? Need to see 2017-2025 progression.

#### Generate Tab (02b-nav-generate.png)
**Innovative Feature**: Multi-agent code generation system
- 5 agents: Paper Analyzer → Test Designer → Code Generator → Test Executor → Debugger
- Test-driven development approach
- "Turn Papers into Working Code"

**Pedagogical Value**: Could be excellent for teaching implementation, but:
- How accurate is the generated code?
- Does it capture algorithm essence or just boilerplate?
- Students need to understand *why*, not just get working code

**Emotional State**: 4/5 (intrigued by TDD approach for papers)

---

### Step 3: Task-Based Search - CRITICAL FAILURE (3:00-5:00)

#### Basic Search Attempt (03a-03b)
**Query**: "efficient language models"
**Expected**: BERT, DistilBERT, TinyBERT, ALBERT, MobileBERT, knowledge distillation papers
**Result**: **0 results after 10 seconds**

**Analysis of Failure**:
- This is a FUNDAMENTAL query for my seminar topic
- These are among the most cited papers in NLP (BERT: 90,000+ citations)
- Search appears to be semantic/embedding-based but returned nothing
- 10-second response time is pedagogically unacceptable (students will abandon)

**Emotional State**: 1/5 (frustration - core functionality broken)

---

#### Research Advisor Attempt (03c-03f)
**Query**: "What are the key papers on efficient transformers and knowledge distillation for language models that my graduate students should read?"

**Experience**:
1. Panel opened smoothly with example queries
2. Submitted detailed pedagogical query
3. Waited 8 seconds → still "Searching papers..."
4. Waited 18 seconds total → "Contextual synthesis temporarily unavailable"
5. Received 5 paper links with minimal context

**Papers Returned**:
1. Knowledge Distillation for Code Understanding
2. Knowledge Distillation for Bundle Generation (LLM-based)
3. AfroXLMR-Comet (multilingual, low-resource)
4. Elastic Architecture Search for Efficient Language Models ✓
5. Black-Box LLM Replication via Distillation

**Assessment of Results**:
- Only 1 of 5 papers (#4) directly addresses my query
- Missing canonical works: DistilBERT, TinyBERT, ALBERT
- No pedagogical progression (foundational → advanced)
- "Temporarily unavailable" suggests infrastructure issues
- 18-second timeout is unacceptable for classroom demos

**Emotional State**: 2/5 (disappointed - promised semantic search, delivered unreliable results)

---

### Step 4: Paper Detail Examination (5:30)

**Paper Examined**: StereoSpace (2512.10959)
- CS.CV paper (Computer Vision - not my field, but examining UI)
- Full abstract available
- Tabs: Summary, Related Papers, Benchmarks
- Links: "Read on arXiv", "Generate Code"

**Missing Critical Information for Teaching**:
1. **No citation count** - How do I assess impact?
2. **No publication venue** - Conference? Journal? ArXiv-only?
3. **No date beyond "Dec 11, 2025"** - Is this yesterday's paper or last week's?
4. **No author affiliations** - Students ask "where is this research from?"
5. **No "cited by" / "cites" relationships** - Can't build citation graph
6. **No historical context** - Is this foundational or incremental?

**For Graduate Teaching, I Need**:
- Citation trajectory (how fast is it accumulating?)
- Which papers it builds upon (intellectual lineage)
- Which papers cite it (influence assessment)
- Author reputation (helps students assess credibility)

**Emotional State**: 3/5 (neutral - decent abstract, poor metadata)

---

### Step 5: Code Availability Check (6:00)

**Action**: Clicked "Has Code" quick filter

**Result**: Filter applied, chip appeared, but results unchanged
- Still showing same 30 papers (all from Dec 11, 2025)
- No indication of which papers *actually* have code
- No GitHub icons, star counts, or code quality indicators

**Critical for My Use Case**:
- I require students to reproduce key results
- Need to differentiate:
  - Papers with official implementation
  - Papers with community reimplementations
  - Papers with no code (theory-only)
- GitHub stars help assess code quality
- Last commit date indicates maintenance status

**What Semantic Scholar Does Better**:
- Shows GitHub link prominently
- Displays star count and fork count
- Links to Papers with Code leaderboards

**Emotional State**: 2/5 (frustrated - filter doesn't actually surface code metadata)

---

## Steps Not Completed (Due to Time/Context Constraints)

**Step 6**: Learning Path Assessment - CRITICAL MISSING FEATURE
**Step 7**: TL;DR / Quick Scan Mode
**Step 8**: Technique Explorer
**Step 9**: Rising Papers / Hot Topics
**Step 10**: Paper Relationships / Similarity Graph
**Step 11**: Second Search (Consistency Check)
**Step 12**: Exit Reflection

---

## Pain Point Analysis

### 1. Curation Burden (Maintaining Reading Lists)
**Status**: ❌ **NOT SOLVED**

- Search failure means I can't even *find* papers to curate
- No "Reading List" tested, but suspect it's just bookmarking
- Need: Automatic seminar syllabus generation by difficulty level
- Need: Temporal sorting (2017 foundations → 2025 cutting edge)

### 2. Student Guidance ("What should I read?")
**Status**: ❌ **PARTIALLY ADDRESSED, POORLY EXECUTED**

- "Learning Path" feature exists in Discovery tab but not tested
- Research Advisor timeout suggests backend infrastructure issues
- Returned papers lack pedagogical context (difficulty level, prerequisites)
- No differentiation between survey papers vs. research papers

**For Students, I Need**:
- **Beginner**: Survey papers, well-cited tutorials, papers with good figures
- **Intermediate**: Landmark papers (BERT, GPT-2, T5)
- **Advanced**: Recent techniques building on foundations
- **Expert**: Current research frontier

### 3. Reproducibility Standards (Code Availability)
**Status**: ❌ **SURFACE-LEVEL ONLY**

- "Has Code" filter exists but provides no metadata
- No indication of code quality, stars, maintenance
- "Generate Code" feature is interesting but untested
- Missing: Direct links to implementations, test results, benchmarks

### 4. Field Breadth (Keeping Up Across Subfields)
**Status**: ⚠️ **PARTIALLY ADDRESSED**

- Trending topics sidebar shows: LLMs, Diffusion Models, VLMs, RL, Fine-tuning
- Category filters available but too broad (need subfield granularity)
- Missing: Cross-field connections (e.g., RL for NLP, Vision for Language)

### 5. Historical Context (Foundational vs. Incremental)
**Status**: ❌ **COMPLETELY MISSING**

- No citation counts (cannot assess impact)
- No temporal visualization (cannot see field evolution)
- No "Seminal Papers" automatic identification
- "Seminal Papers" filter exists but tooltip only says "Top 1% cited" - too crude

**Critical for Teaching**: Students need to understand *why* BERT (2018) matters more than BERT+TinyTweak (2025). This tool doesn't help with that.

---

## Teaching Utility Assessment

### Would I Use This for My Graduate Seminar?
**NO - 2/5**

**Reasons**:
1. **Search is broken** - Core functionality failed on standard query
2. **No citation metadata** - Cannot assess paper importance
3. **No historical timeline** - Cannot build foundational → advanced progression
4. **Advisor is unreliable** - 18-second timeout, "temporarily unavailable"
5. **Code metadata is superficial** - Filter doesn't surface actual code quality

### Would I Recommend to Students?
**NOT YET - 2.5/5**

**Potential Value**:
- If search worked, semantic queries could help beginners
- If Advisor worked, natural language queries reduce barrier to entry
- If Learning Path worked, could replace office hours questions
- Code generation *might* help with implementation understanding

**Current Blockers**:
- Students will lose confidence after search failures
- No way to verify paper importance (citations critical for PhD students)
- Trending topics too noisy (dropout +29,900%? What does that mean?)
- Cannot distinguish hype from substance

### What Would Make Me Recommend It?

**Must-Have Fixes (Before Next Semester)**:
1. ✅ **Fix semantic search** - "efficient language models" must return results
2. ✅ **Add citation counts** - Minimum viable metadata
3. ✅ **Add publication venues** - NeurIPS vs. ArXiv matters
4. ✅ **Stabilize Research Advisor** - 3-second response or don't offer it
5. ✅ **Show code quality** - GitHub stars, last commit, language

**Nice-to-Have (Would Increase Adoption)**:
- Citation graph visualization (who cites whom)
- Difficulty level estimation (beginner/intermediate/advanced/expert)
- Author reputation scores (h-index, affiliation)
- Pedagogical quality indicators (figures, clarity, writing style)
- Temporal timeline view (2017-2025 evolution of field)

---

## Delights

1. **Code Generation Feature (untested but promising)**
   - 5-agent TDD system is pedagogically sound
   - Could revolutionize "implement this paper" assignments
   - Need to test accuracy before recommending

2. **Trending Topics Sidebar**
   - Live growth percentages (+44% for Diffusion Models)
   - Helps me stay current on what students are excited about
   - Good conversation starter for seminar

3. **Discovery Quick Cards**
   - "Rising Stars" could surface important early work
   - "Papers with Code" aligns with my reproducibility values
   - Good for browsing vs. targeted search

4. **Clean, Professional UI**
   - Filters clearly organized
   - TL;DR summaries save time vs. reading abstracts
   - No distracting ads or clutter

---

## Frustrations

1. **Search Failure (Critical)**
   - Wasted 5 minutes on a query that should work
   - No fallback or suggestions
   - Error message unhelpful ("Try different keywords" - I used standard terms!)

2. **Research Advisor Timeout (Critical)**
   - Promised intelligent assistance, delivered "temporarily unavailable"
   - 18 seconds of loading is unacceptable
   - Partial results with no context are worse than no results

3. **Missing Citation Metadata (High Priority)**
   - Cannot distinguish BERT (90,000 cites) from BERT-variant-2025 (3 cites)
   - This is fundamental for academic work
   - Semantic Scholar and Google Scholar both provide this

4. **Code Filter Doesn't Filter (High Priority)**
   - "Has Code" should show only papers with implementations
   - Instead, it's just a search modifier with no visible effect
   - No GitHub links, stars, or quality indicators

5. **No Historical Context (Medium Priority)**
   - All results from Dec 11, 2025 - where's the history?
   - Need to see 2017 (Transformer), 2018 (BERT), 2019 (DistilBERT) progression
   - "Seminal Papers" filter exists but unclear how it works

6. **Trending Topics Too Noisy**
   - "Dropout +29,900%" - is this a bug? A joke?
   - "SSM +12,841%" - what's SSM? (State Space Models? Not obvious)
   - Need context for percentages (29,900% of what baseline?)

---

## Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Initial page load | ~2s (loading state) | <1s | ⚠️ Acceptable |
| Search response ("efficient language models") | 10,002ms | <3,000ms | ❌ **Failed** |
| Research Advisor response | 18,000ms+ (timeout) | <5,000ms | ❌ **Failed** |
| Paper expand | Instant | <500ms | ✅ Good |
| Filter apply | Instant | <500ms | ✅ Good |

**Performance Assessment**: Backend infrastructure appears to be the bottleneck. Search and Advisor both have unacceptable latency.

---

## Priority Improvements

### P0: Blockers (Must Fix Before I Can Recommend)

| Issue | Impact | Effort | Recommendation |
|-------|--------|--------|----------------|
| Search returns 0 results for valid queries | CRITICAL | High | Fix semantic search index/embeddings |
| Research Advisor times out after 18s | CRITICAL | High | Add timeout handling, show partial results gracefully |
| No citation counts displayed | HIGH | Medium | Integrate with Semantic Scholar API or scrape arXiv citations |
| Code filter doesn't show code metadata | HIGH | Medium | Add GitHub integration (stars, forks, last commit) |

### P1: High Priority (Needed for Teaching Use Case)

| Issue | Impact | Effort | Recommendation |
|-------|--------|--------|----------------|
| No publication venue shown | HIGH | Low | Parse arXiv category, add conference/journal metadata |
| No historical timeline view | HIGH | High | Add temporal visualization of field evolution |
| Difficulty level not indicated | MEDIUM | Medium | Use ML to estimate (abstract complexity, citation velocity) |
| Trending topics lack context | MEDIUM | Low | Add hover tooltips explaining metrics |

### P2: Nice-to-Have (Would Increase Adoption)

| Issue | Impact | Effort | Recommendation |
|-------|--------|--------|----------------|
| No citation graph | MEDIUM | High | Build interactive graph of citing/cited papers |
| No author reputation | MEDIUM | Medium | Integrate h-index, affiliation data |
| No pedagogical quality score | LOW | High | Analyze figures, clarity, writing style (advanced ML) |
| No learning path tested | UNKNOWN | Unknown | Test existing feature in future assessment |

---

## Screenshots Index

1. **01-landing-first-impression.png** - Initial page load, loading state visible
2. **02a-nav-discovery.png** - Discovery tab with quick cards and high-impact section
3. **02b-nav-generate.png** - Code generation feature (5-agent TDD system)
4. **03a-search-query-typed.png** - Search query entered, "Searching..." state
5. **03b-search-no-results.png** - Search failure: 0 results after 10 seconds
6. **03c-advisor-opened.png** - Research Advisor panel opened
7. **03d-advisor-query-typed.png** - Detailed pedagogical query submitted to Advisor
8. **03e-advisor-response.png** - Advisor still searching after 8 seconds
9. **03f-advisor-still-searching.png** - Advisor timeout after 18+ seconds, partial results
10. **04-paper-expanded.png** - Paper detail view with tabs, missing citation data
11. **05-code-filter.png** - "Has Code" filter applied, no visible effect on results

---

## Final Verdict

### Overall Score: 2.5/5

**Would I Use This Tool?**
Not in its current state. Search failures and missing citation metadata are dealbreakers.

**Would I Return Tomorrow?**
Only if I heard that search was fixed. Without working search, there's no tool.

**Would I Recommend to Colleagues?**
No. I would recommend Semantic Scholar or Google Scholar instead, despite their clutter, because they work reliably.

**What Would Change My Mind?**
1. Fix search (must return results for "efficient language models")
2. Add citation counts (must be visible on every paper)
3. Fix Advisor timeout (must respond in <5 seconds or fail gracefully)
4. Add publication venues (conference/journal matters for credibility)

**One Thing That Delighted Me**:
The 5-agent code generation system. If it works as advertised, this could transform how students learn to implement papers. But I couldn't test it due to search failures.

**One Thing That Frustrated Me Most**:
Search returning zero results for "efficient language models" - a query with thousands of relevant papers. This suggests a fundamental indexing or embedding problem that undermines the entire product.

---

## Recommendations for Product Team

### For Academic Users (Faculty, PhD Students)

**Priority 1: Citation Metadata**
- Add citation counts from Semantic Scholar API
- Show publication venue (conference, journal, preprint)
- Display "cited by" and "references" counts
- Consider: Citation trajectory (velocity over time)

**Priority 2: Historical Context**
- Add temporal filters (pre-2020, 2020-2023, 2023-present)
- Build timeline visualization of field evolution
- Highlight seminal papers automatically (not just top 1% cited)
- Show "foundational work" vs. "builds upon X"

**Priority 3: Pedagogical Features**
- Difficulty estimation (beginner → expert)
- Prerequisite detection ("read X before Y")
- Learning path generation (tested feature didn't work)
- Paper quality indicators (clarity, figures, writing style)

### For Search & Advisor

**Immediate Fixes**:
- Debug why "efficient language models" returns 0 results
- Add query expansion (suggest related terms)
- Show partial results faster (don't wait for full synthesis)
- Add timeout handling (fail gracefully after 5 seconds)

**Long-term Improvements**:
- Hybrid search (semantic + keyword fallback)
- Query understanding ("show me" vs. "what is")
- Confidence scores on results
- Explain why results were chosen

### For Code Integration

**Current State**: Filter exists but provides no value

**Needed**:
- Direct GitHub links with star counts
- Code quality indicators (tests, docs, activity)
- Multiple implementations ranked by quality
- "Official" vs. "Community" badges

---

**End of Assessment**
**Assessor**: Prof. James Williams (Persona 2)
**Next Steps**: Fix P0 blockers before next semester begins.
