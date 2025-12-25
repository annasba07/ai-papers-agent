# UX Assessment: Dr. Maya Chen - AI Paper Atlas

**Persona**: Dr. Maya Chen, 2nd-year Postdoc, CMU ML Department
**Date**: 2025-12-25
**Session Duration**: ~10 minutes
**Assessment Run**: 2025-12-25_11-35-32

---

## Executive Summary

As a time-pressed ML researcher, I found AI Paper Atlas underwhelming for my core needs. The Research Advisor returned results but with an error message, the "Has Code" filter appeared broken (badge showed but results unchanged), and I saw no code indicators on papers. For someone who wastes hours hunting reproducible work, this was disappointing. The basic UI is clean, but critical functionality didn't work as expected.

**Verdict**: Would not return. Need to see code availability and working filters before reconsidering.

---

## Session Timeline

| Time | Action | Outcome | Emotion (1-5) |
|------|--------|---------|---------------|
| 0:00 | Landing page load | Redirected to /explore, Advisor popup appeared | 3 - Neutral |
| 0:15 | Opened Research Advisor | Panel opened cleanly | 3 - Neutral |
| 0:30 | Entered query: "efficient attention mechanisms for mobile deployment" | Query accepted | 3 - Cautious |
| 0:45 | Submitted query | Searching state appeared | 3 - Waiting |
| 1:00 | Received response | Papers shown but "Contextual synthesis temporarily unavailable" warning | 2 - Skeptical |
| 1:30 | Closed advisor, clicked "Has Code" filter | Filter badge appeared | 2 - Hopeful |
| 2:00 | Observed results | Papers unchanged, still showing CV papers from Dec 11 | 2 - Frustrated |
| 2:30 | Expanded paper detail | Full abstract shown, "Generate Code" button visible | 2 - Curious |
| 3:00 | Visited Discovery page | Stats shown, Quick Discovery options | 3 - Exploring |
| 3:30 | Checked Techniques tab | Loaded techniques page | 3 - Neutral |

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)
**Screenshot**: `01-landing-first-impression.png`

**Observations**:
- Immediately redirected to `/explore` page
- Research Advisor popup appeared front and center
- Clean layout with left sidebar filters, main content area
- Default content showed Computer Vision papers from Dec 11, 2025
- Not immediately clear what makes this different from arXiv

**Load Performance**: Could not measure (script error)

**Emotional State**: 3/5 - Neutral. Professional appearance but not yet convinced of value.

**What worked**: Clean visual design, clear navigation.

**What didn't**: Auto-popup felt pushy. No immediate value proposition visible.

---

### Step 2: Research Advisor Interaction
**Screenshots**: `02-advisor-panel-opened.png`, `03-query-entered.png`, `04-advisor-response.png`

**Actions**:
1. Clicked "Ask Research Advisor" button
2. Entered my actual research query: "efficient attention mechanisms for mobile deployment"
3. Submitted query and waited

**Response Quality**:
- Received 5 paper recommendations
- **WARNING MESSAGE**: "Contextual synthesis temporarily unavailable"
- Papers included:
  - "Adaptive Attention-Based Model for 5G Radio-based Outdoor Localization" (not relevant - 5G localization, not mobile ML)
  - "DeltaLLM: A Training-Free Framework..." (marginally relevant - LLM inference)
  - "Taming the Titans: A Survey of Efficient LLM Inference Serving" (survey, possibly useful)
  - GNN distillation paper (not attention mechanisms)
  - Multi-agent RL paper (totally irrelevant)

**Relevance Assessment**: 2/10 - Only 1-2 papers were remotely related to my query about attention mechanisms for mobile deployment.

**Emotional State**: 2/5 - Disappointed. The advisor seemed to misunderstand my query or lack relevant papers in the index.

**What worked**: Fast response, links to papers provided.

**What didn't**: Poor relevance, error message destroyed confidence, no explanation of *why* these papers were chosen.

---

### Step 3: Code Availability Check (Critical Pain Point)
**Screenshots**: `06-back-to-main.png`, `07-code-filter-applied.png`

**This is where the tool failed me most.**

**Actions**:
1. Closed Research Advisor
2. Clicked "Has Code" quick filter
3. Observed results

**What I Expected**:
- Results to filter down to only papers with GitHub repos
- Code badges/icons on remaining papers
- Significantly fewer results (maybe 10-20% of total)

**What Actually Happened**:
- "Has Code" badge appeared in filter area
- Paper count remained "138,986 papers" (unchanged)
- Same papers visible (StereoSpace, WorldLens, etc.)
- **NO CODE INDICATORS** visible on any paper cards

**Emotional State**: 2/5 - Frustrated. This is my #1 pain point and the filter appears broken.

**Critical Issue**: I cannot tell if:
- The filter isn't working
- These papers actually have code but it's not shown
- The database lacks code metadata

**Time Wasted**: ~1 minute clicking and waiting for something to happen.

---

### Step 4: Paper Detail Exploration
**Screenshots**: `08-paper-expanded.png`

**Clicked**: "StereoSpace: Depth-Free Synthesis..." paper to expand

**Detail View Showed**:
- Full abstract (useful)
- Three tabs: Summary, Related Papers, Benchmarks
- "Read on arXiv" button
- **"Generate Code" button** (interesting but unclear what it does)

**What I Looked For (Code Indicators)**:
- GitHub link/icon - **NOT FOUND**
- Star count - **NOT FOUND**
- "Has Implementation" badge - **NOT FOUND**
- Code snippet preview - **NOT FOUND**

**Emotional State**: 2/5 - The "Generate Code" button is intriguing but doesn't solve my problem. I need *existing, tested* implementations, not AI-generated code.

**What worked**: Clean expansion, tabbed interface makes sense.

**What didn't**: Still no code availability information despite "Has Code" filter being active.

---

### Step 5: Discovery Page Exploration
**Screenshots**: `09-discovery-page.png`, `10-techniques-page.png`

**Quick scan of Discovery features**:
- Overview tab with stats: 138,986 papers, 26,666 "With Analysis"
- Quick Discovery: High impact papers, Rising citations, etc.
- Tabs: High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path

**Techniques Tab**:
- Loaded successfully
- Appeared to show technique categorization (insufficient time to explore fully)

**Emotional State**: 3/5 - Some interesting features here, but didn't have time to dig deep.

**Note**: Under time pressure, didn't prioritize these discovery features over core search/filter needs.

---

## Problem Assessment: Did It Solve My Pain Points?

| Pain Point | Addressed? | Evidence |
|------------|-----------|----------|
| **1. Information Overload** | Partially | Research Advisor attempted semantic search, but poor relevance made it worse |
| **2. Time Poverty** | No | Wasted time on broken filter, unclear features. No time savings observed. |
| **3. Reproducibility Frustration** | **No** | **CRITICAL FAILURE**: "Has Code" filter appeared broken, no code indicators visible |
| **4. Connection Blindness** | Maybe | "Related Papers" tab exists but didn't test thoroughly |
| **5. Trend Anxiety** | Unclear | Saw "Rising" and "Hot Topics" options but no time to validate quality |

---

## Delights and Frustrations

### Delights (What Impressed Me)
1. **Clean, professional UI** - Not cluttered, decent typography
2. **Research Advisor exists** - Shows ambition to go beyond keyword search
3. **Generate Code button** - Novel idea, though unclear if useful
4. **Discovery features breadth** - Many options (TL;DR, Techniques, Learning Paths)

### Frustrations (What Wasted My Time)
1. **"Has Code" filter appears broken** ⚠️ CRITICAL
2. **No code indicators on papers** - Can't tell which have implementations
3. **Research Advisor poor relevance** - 2/5 papers matched my query
4. **"Contextual synthesis temporarily unavailable"** - Error message on first use
5. **Paper count didn't change with filter** - Unclear if anything happened
6. **Auto-popup advisor** - Felt pushy on landing
7. **All papers from Dec 11, 2025** - Seems like limited/old index?

---

## Performance Metrics

**Load Times**: Unable to measure (evaluate_script error with performance API)

**Interaction Response**:
- Research Advisor query: ~5 seconds
- Filter application: Instant (but no visual change in results)
- Page navigation: Fast (<1 second)

**Subjective Speed**: Acceptable. No obvious slowness.

---

## Priority Improvements

Ranked by Impact/Effort for my persona:

| Priority | Improvement | Impact | Effort | Rationale |
|----------|-------------|--------|--------|-----------|
| 🔴 P0 | **Fix "Has Code" filter** | High | Medium | Critical for reproducibility-focused researchers. Currently appears broken. |
| 🔴 P0 | **Add GitHub badges to paper cards** | High | Low | Show GitHub icon + stars on cards. Essential metadata. |
| 🔴 P0 | **Update paper index** | High | High | All visible papers from Dec 11. Seems stale. |
| 🟡 P1 | **Improve Research Advisor relevance** | High | High | 2/5 relevant results is unacceptable. Needs better understanding of queries. |
| 🟡 P1 | **Remove error messages on advisor** | Medium | Low | "Contextual synthesis temporarily unavailable" destroys confidence. |
| 🟡 P1 | **Show filter result counts** | Medium | Low | "138,986 papers" should change to "3,421 papers" when filtering. |
| 🟢 P2 | **Clarify "Generate Code" feature** | Low | Low | Tooltip or explanation needed. Is this AI code generation? |
| 🟢 P2 | **Make advisor popup optional** | Low | Low | Auto-popup on landing is pushy. Let users discover it. |

---

## Screenshots Index

1. `01-landing-first-impression.png` - Initial page load (redirected to /explore)
2. `02-advisor-panel-opened.png` - Research Advisor panel open
3. `03-query-entered.png` - Query typed into advisor
4. `04-advisor-response.png` - Advisor results with error message
5. `05-advisor-closed.png` - Back to main explore view
6. `06-back-to-main.png` - Explore page, advisor still visible
7. `07-code-filter-applied.png` - "Has Code" filter badge visible
8. `08-paper-expanded.png` - Paper detail view expanded
9. `09-discovery-page.png` - Discovery page overview
10. `10-techniques-page.png` - Techniques tab on Discovery

**Total Screenshots**: 10

---

## Final Verdict

**Would I bookmark this tool?** No.

**Would I return tomorrow?** No - not until code availability works.

**Would I recommend to colleagues?** No - would embarrass me if they tried the "Has Code" filter.

**What would change my mind?**
1. Seeing actual GitHub badges on papers with star counts
2. "Has Code" filter reducing results from 138k to ~10k papers
3. Research Advisor returning relevant results without error messages
4. Evidence the paper index is current (not Dec 11 papers in late December)

**Raw Emotional Assessment**: 2/5 - Disappointed. The tool showed potential but failed on my most critical need (code availability). As someone who wastes hours hunting for reproducible papers, a broken "Has Code" filter is a dealbreaker.

**Time Saved vs. Time Wasted**: Net negative. Wasted 2-3 minutes on broken filter, got poor advisor results. Would have been faster to search Papers with Code directly.

---

## Researcher Notes

**What I was hoping for**:
- Instant filtering to papers with GitHub implementations
- Star counts and repo links visible on cards
- Semantic search that understands "efficient attention for mobile" means transformer optimization, not 5G localization

**What I got**:
- A broken-looking filter
- Generic papers unrelated to my query
- No code indicators anywhere

**The gap between expectation and reality was too large for me to invest more time.**

---

**End of Assessment**
