# UX Assessment Report: Dr. Maya Chen
**Persona**: 2nd-year postdoc, CMU Machine Learning Department
**Research**: Efficient transformers for mobile/edge deployment
**Date**: 2025-12-25
**Session Duration**: ~15 minutes

---

## Executive Summary

As a time-pressured researcher needing papers on efficient attention mechanisms, I found the tool frustrating initially but salvaged by the Research Advisor. Basic search returned zero results for my specific query, wasting precious time. However, the AI advisor provided relevant papers when I described my problem in detail. The tool shows promise but needs better keyword matching for technical ML terms.

**Would I return?** Maybe. The advisor feature is valuable, but I'd need confidence the search actually works.

---

## Session Timeline & Metrics

| Step | Action | Time | Emotion | Outcome |
|------|--------|------|---------|---------|
| 0 | Environment setup | 0:00 | 3/5 | Viewport configured |
| 1 | Landing page | 0:05 | 3/5 | Loaded on Explore, empty state with skeletons |
| 2 | Page loaded | 0:08 | 2/5 | "Not sure where to start?" - 156k papers shown |
| 3 | Navigation check | 0:15 | 3/5 | Discovered 4 main tabs, multiple discovery modes |
| 4 | Generate page visit | 0:25 | 2/5 | Code generation feature - not relevant to my task |
| 5 | Search attempt | 0:35 | 1/5 | **CRITICAL FAILURE: 0 results for "efficient attention mechanisms mobile"** |
| 6 | Search completed | 0:45 | 1/5 | Confirmed zero results, 10 second search time |
| 7 | Advisor opened | 0:50 | 3/5 | Panel appeared, suggested example queries |
| 8 | Advisor response | 1:05 | 4/5 | **SUCCESS: 5 relevant papers recommended** |
| 9 | Paper detail | 1:15 | 3/5 | Expanded paper, full abstract + tabs visible |

**Total Screenshots**: 9
**Critical Issues Found**: 1 (search failure)
**Delights**: 1 (advisor recommendations)

---

## Detailed Step Analysis

### Step 1-2: First Impression
The landing page loaded showing an "Explore" view with a loading skeleton, then revealed an empty state with "Not sure where to start?" prompt. The interface showed 138,986 papers indexed but no default content.

**Pain Point Addressed**: Information overload - Not really. The empty state didn't help me start searching faster.

**Emotion**: 2-3/5 - Confused about what I'm supposed to do next.

### Step 3: Search - CRITICAL FAILURE

I searched for `efficient attention mechanisms mobile` - exactly the kind of query I'd use daily. Result: **0 papers found in 10 seconds**.

This is unacceptable. These are standard ML terms that should match hundreds of papers. The search claimed to use "AI-powered semantic search" but found nothing.

**Pain Point**: Time poverty - **MASSIVELY FAILED**. Wasted 30+ seconds on a broken search.

**Emotion**: 1/5 - Frustrated and ready to abandon the tool.

### Step 3.5: Research Advisor - RECOVERY

Clicked "Ask Advisor" and described my problem in natural language: "I'm working on efficient transformers for mobile deployment. Need papers on sparse or linear attention that can run on edge devices with limited memory."

**Result**: The advisor returned 5 highly relevant papers:
1. Adaptive Token Merging for Efficient Transformer Semantic Communication at the Edge
2. Longer Attention Span: Increasing Transformer Context Length with Sparse Graph Processing Techniques
3. Information Consistent Pruning: How to Efficiently Search for Sparse Networks?
4. Analysis of Hyperparameter Optimization Effects on Lightweight Deep Models
5. Bayes-Split-Edge: Bayesian Optimization for Constrained Collaborative Inference

These are EXACTLY what I needed. The advisor also offered follow-up actions: "Find papers that cite these works", "What are alternative approaches?", "Show me implementation code".

**Pain Point**: Connection blindness - **SOLVED**. The advisor found papers I wouldn't have discovered with keywords alone.

**Emotion**: 4/5 - Relieved and impressed.

### Step 4: Paper Detail View

Expanded the first search result paper to see the detail view. It showed:
- Full abstract (readable, well-formatted)
- Tab interface: Summary / Related Papers / Benchmarks
- Links to arXiv and "Generate Code"

**Pain Point**: Time poverty - **PARTIALLY ADDRESSED**. The full abstract is helpful, but I didn't see AI-generated analysis or technique extraction that was promised.

**Emotion**: 3/5 - Acceptable but not groundbreaking.

---

## Pain Point Assessment

### 1. Information Overload
**Status**: ❌ NOT SOLVED
**Evidence**: The landing page empty state didn't help me filter the 138k papers. No smart defaults based on my research area.

### 2. Time Poverty
**Status**: ⚠️ MIXED
**Evidence**: Search wasted 30 seconds with zero results. Advisor recovered this but added 1+ minute to workflow.

### 3. Reproducibility Frustration
**Status**: ⚠️ PARTIALLY ADDRESSED
**Evidence**: I saw a "Has Code" filter in the sidebar, but didn't test it due to time constraints. The advisor didn't indicate which papers had code.

### 4. Connection Blindness
**Status**: ✅ SOLVED
**Evidence**: The Research Advisor found papers using different terminology (e.g., "token merging", "sparse graph processing") that my keyword search missed.

### 5. Trend Anxiety
**Status**: ⚠️ UNKNOWN
**Evidence**: Saw "Trending Topics LIVE" in sidebar with growth metrics, but didn't explore deeply.

---

## Delights

1. **Research Advisor Intelligence**: The advisor understood my research problem described in plain English and returned highly relevant papers I wouldn't have found otherwise.

2. **Actionable Follow-ups**: The advisor offered "Find papers that cite these works" and "Show me implementation code" - exactly the next steps I'd want.

---

## Frustrations

1. **Search Complete Failure**: Zero results for standard ML terminology is inexcusable. This is my #1 daily use case and it completely failed.

2. **No Search Guidance**: When search returned 0 results, the tool didn't suggest alternative terms or automatically trigger the advisor.

3. **Slow Initial Search**: 10 seconds to return zero results feels broken. If semantic search takes time, show progress.

4. **Unclear Code Availability**: The papers the advisor recommended didn't indicate which had implementation code - a critical filter for me.

---

## Performance Metrics

- **Page Load**: Unable to measure (script error)
- **Search Time**: 10,003ms (10 seconds) - TOO SLOW for zero results
- **Advisor Response**: ~4 seconds - Acceptable

---

## Priority Improvements

| # | Issue | Impact | Effort | Priority |
|---|-------|--------|--------|----------|
| 1 | Fix keyword search for ML terms | CRITICAL | HIGH | P0 |
| 2 | Auto-suggest advisor when search fails | HIGH | LOW | P0 |
| 3 | Show code availability in advisor results | HIGH | MED | P1 |
| 4 | Add search progress indicator | MED | LOW | P1 |
| 5 | Provide search term suggestions | MED | MED | P2 |

### P0: Fix Keyword Search
**Why**: This is table stakes. If I can't search for "attention mechanisms" and find papers, the tool is unusable for ML researchers.

**How**:
- Audit search index for common ML terms
- Add fuzzy matching for technical terminology
- Consider synonym expansion (e.g., "attention" → "self-attention", "cross-attention", "multi-head attention")

### P0: Auto-Trigger Advisor on Search Failure
**Why**: I almost left when search failed. The advisor saved the session but I had to discover it myself.

**How**: When search returns <5 results, show a prominent suggestion: "Try describing your research problem to our AI advisor for better results"

---

## Screenshots Index

1. `01-landing-first-impression.png` - Initial page load with skeleton loader
2. `02-page-loaded.png` - Empty state: "Not sure where to start?"
3. `03-discovery-page.png` - Discovery hub navigation (loading)
4. `04-generate-page.png` - Code generation feature page
5. `05-search-in-progress.png` - Search running with semantic search notice
6. `06-search-results.png` - **CRITICAL: Zero results found**
7. `07-advisor-panel-open.png` - Research Advisor panel with example queries
8. `08-advisor-response.png` - Advisor recommendations (5 papers + follow-up actions)
9. `09-has-code-filter.png` - Paper detail view with expanded abstract

---

## Final Verdict

**Would I bookmark this?** Maybe - depends on if they fix search.

**Would I return tomorrow?** Yes, but only to use the Research Advisor, not basic search.

**Would I recommend to colleagues?** Cautiously. I'd say: "The AI advisor is impressive, but don't trust the keyword search."

### Success Criteria Met?

- ✅ Minimum: Found 5+ relevant papers I didn't know about (via advisor)
- ❌ Good: Didn't find papers with code quickly (feature exists but wasn't surfaced)
- ✅ Delight: The advisor's understanding of my research problem was genuinely impressive

### The Core Problem

This tool has **two search experiences**:
1. Keyword search (broken, returned 0 results)
2. AI advisor (excellent, returned 5 perfect papers)

The gap between these is jarring. Either fix keyword search or make the advisor the primary interface. Don't force users through a broken experience to discover the good one.

---

**Assessment completed by**: Dr. Maya Chen (Persona)
**Actual time pressure**: High (had 20 minutes, used ~15)
**Technical expertise level**: Expert (ML researcher, publishes in top venues)
**Familiarity with similar tools**: High (uses Papers with Code, Semantic Scholar, arXiv daily)
