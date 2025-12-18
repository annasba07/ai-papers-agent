# UX Assessment Report: AI Paper Atlas
**Persona**: Dr. Maya Chen (CMU Postdoc - Efficient Transformers)
**Date**: 2025-12-17
**Session Duration**: ~18 minutes
**Task**: Find recent papers on efficient attention mechanisms for mobile deployment

---

## Executive Summary

As a time-pressed postdoc researching efficient transformers, I tested AI Paper Atlas to solve my daily paper discovery problem. The **Research Advisor semantic search was a game-changer** - it found relevant papers that keyword search missed entirely. However, **critical reproducibility features are broken** (no visible code indicators, "Has Code" filter ineffective), and **all advanced discovery routes (TL;DR, techniques, trending) return 404 errors**. The tool shows promise for semantic discovery but feels incomplete - like an MVP with missing features that were advertised but not built.

**Verdict**: 3/5 - Would bookmark cautiously, but current gaps make it unreliable for my daily workflow.

---

## Session Timeline & Metrics

| Step | Action | Time | Emotion | Success |
|------|--------|------|---------|---------|
| 0 | Environment setup | 0s | 3/5 neutral | ✓ |
| 1 | Landing page first impression | ~3s load | 3/5 cautious | ✓ |
| 2 | Navigation exploration (Generate tab) | ~2s | 3/5 neutral | ✓ |
| 3 | Keyword search "efficient attention..." | ~1s | 2/5 frustrated | ✗ |
| 3.5 | Research Advisor AI search | 2.6s | 4/5 hopeful | ✓ |
| 4 | Paper detail examination | ~1s | 3/5 concerned | ≈ |
| 5 | Code filter test | ~1s | 2/5 frustrated | ✗ |
| 6-9 | Discovery routes (404 errors) | ~4s total | 2/5 disappointed | ✗ |
| 11 | Second search "linear attention" | 3.8s | 4/5 pleased | ✓ |
| 12 | Final reflection | - | 3/5 mixed | - |

**Total Papers Found**: 6 relevant (via Advisor) vs 0 (via keyword search)
**Critical Blocker**: No way to identify which papers have code implementations

---

## Detailed Step Analysis

### Step 1: Landing Page - First Impression
**Screenshot**: `01-landing-first-impression.png`

**What I Saw**: Clean interface, prominent search bar, but immediately confused by default content showing Computer Vision papers when I need ML/efficiency research.

**Observations**:
- ✓ Search box is front and center with helpful placeholder
- ✓ "Ask Advisor" button suggests AI capabilities
- ✗ Default papers (StereoSpace, WorldLens) are CS.CV - irrelevant to my work
- ✗ No clear explanation of what makes this different from arXiv or Papers with Code
- ≈ Filters sidebar visible but not immediately clear if they're active

**Load Performance**: Page loaded quickly, no performance issues detected.

**Emotional State**: 3/5 - Cautiously neutral. Professional design, but wondering if this tool understands my domain.

---

### Step 2: Navigation Discovery
**Screenshot**: `02a-nav-generate.png`

**What I Saw**: Two main tabs - Explore and Generate. Generate page shows "Turn Papers into Working Code" with 5-agent system.

**Observations**:
- ✓ Simple, clear navigation structure
- ✓ Code generation feature is intriguing for reproducibility
- ≈ "Generate" feels orthogonal to my current task (discovery)
- ✗ No obvious link to trending papers, learning paths, or topic exploration

**Emotional State**: 3/5 - Interesting feature but not addressing my immediate need.

---

### Step 3: Keyword Search - The Frustration
**Screenshot**: `03-search-query-entered.png` (not captured due to immediate transition)

**What I Did**: Typed "efficient attention mechanisms for mobile deployment" and pressed Enter (or search executed automatically).

**What Happened**: Got 30 results - **ALL Computer Vision papers**. Same StereoSpace, WorldLens, Omni-Attribute papers. Zero relevant to efficient attention.

**Observations**:
- ✗ Keyword search appears to be broken or ignoring my query
- ✗ Results don't change based on search input
- ✗ No indication of whether search is semantic or keyword-based
- ✗ Wasting my precious 20 minutes on irrelevant results

**Pain Point Hit**: **Information Overload** - This is exactly the problem I face on arXiv. Drowning in irrelevant papers.

**Emotional State**: 2/5 - Frustrated. This isn't better than arXiv's basic search.

---

### Step 3.5: Research Advisor - The Turnaround
**Screenshot**: `03b-research-advisor.png`

**What I Did**: Clicked "Ask Advisor" button in frustration.

**What Happened**: Modal opened, I clicked "Ask Advisor" with my existing query. Got **6 highly relevant results in 2.6 seconds**:
- "An Efficient GNNs-to-KANs Distillation... for Consumer Electronics **Edge Deployment**" ← Perfect match!
- "LSNet: See Large, Focus Small" ← Vision efficiency
- "Adaptive Attention-Based Model for 5G..." ← Attention + mobile
- "EdgeMLBalancer... on Resource-Constrained **Edge Devices**" ← Exactly my domain!

**Observations**:
- ✓✓ **HUGE WIN**: Semantic search actually understands "mobile deployment" = edge/resource-constrained
- ✓ Response time (2.6s) feels acceptable for this quality
- ✓ "Smart Results" label with AI-POWERED badge sets expectations
- ✓ Papers are actually from my domain (efficiency, edge, mobile)
- ✗ Confusing UX: Why have two search modes? Why not make semantic the default?

**Pain Point Solved**: **Connection Blindness** - Found papers using different terminology ("edge deployment", "consumer electronics") that I would've missed.

**Emotional State**: 4/5 - **Hopeful!** This is what I needed. Finally finding relevant work.

---

### Step 4: Paper Detail Examination
**Screenshot**: `04-paper-expanded.png`

**What I Saw**: Clicked "Expand" on GNNs-to-KANs paper. Got full abstract, tabs for Summary/Related Papers/Benchmarks, buttons for "Read on arXiv" and "Generate Code".

**Observations**:
- ✓ Full abstract saves me from leaving the site
- ✓ Three tabs suggest deeper analysis available
- ✓ "Generate Code" integration is smart
- ✗ **CRITICAL MISSING**: No GitHub link visible anywhere
- ✗ **CRITICAL MISSING**: No indication if code is available
- ✗ Abstract is wall of text - hard to scan quickly
- ≈ Tabs not explored due to time pressure

**Pain Point NOT Solved**: **Reproducibility Frustration** - I still can't tell if this paper has code! This is my #1 filter criterion.

**Emotional State**: 3/5 - Good information, but missing the most critical piece.

---

### Step 5: Code Filter Test - Major Disappointment
**Screenshot**: `05-code-filter.png`

**What I Did**: Clicked "Has Code" filter in sidebar to find reproducible papers.

**What Happened**: Filter appears to activate (shows "Has Code" pill and "Clear all" button), but **still shows same 6 results**. No GitHub icons, no stars/forks, no visual indicators of code availability.

**Observations**:
- ✗ **BROKEN FEATURE**: Filter doesn't reduce results or highlight code availability
- ✗ No visual indicators (GitHub icon, badge) on papers with code
- ✗ Can't tell if all 6 papers have code, or if filter is non-functional
- ✗ This is a deal-breaker for my workflow

**Pain Point AMPLIFIED**: **Reproducibility Frustration** - I waste hours finding papers with code. This was supposed to solve that. It doesn't work.

**Emotional State**: 2/5 - Very frustrated. This is my #1 need and it's broken.

---

### Steps 6-9: Discovery Routes - All 404s
**Screenshots**: `06-reproducible-404.png`, `07-tldr-404.png`, `08-techniques-404.png`, `09-rising-404.png`

**What I Tried**:
- `/discovery/reproducible` → 404
- `/discovery/tldr` → 404
- `/discovery/techniques` → 404
- `/discovery/rising` → 404

**Observations**:
- ✗ **MAJOR GAP**: None of the advanced discovery features exist
- ✗ No "TL;DR scan" mode to quickly triage papers
- ✗ No technique taxonomy to find specific methods
- ✗ No trending/rising papers to catch emerging work
- ✗ Sidebar showed "Trending Topics" but clicking leads nowhere

**Pain Points NOT Addressed**:
- **Time Poverty**: Can't quickly scan 10-20 papers with TL;DRs
- **Trend Anxiety**: No way to see what's "hot" or gaining momentum
- **Connection Blindness**: No technique-based discovery

**Emotional State**: 2/5 - Disappointed. These features would differentiate this tool, but they don't exist.

---

### Step 11: Second Search - Consistency Check
**Screenshot**: `11-second-search-results.png`

**What I Did**: Searched "linear attention" via Research Advisor to test consistency.

**What Happened**: Got **36 relevant results in 3.8 seconds**:
- "InfiniteVL: Synergizing **Linear** and Sparse Attention..." ← Highly relevant!
- "LUNA: **Linear** Universal Neural Attention..." ← Exactly what I searched!
- Papers on efficiency, mobile deployment, linear time complexity

**Observations**:
- ✓ Consistently good semantic search quality
- ✓ Response time similar (~3-4s range)
- ✓ Results clearly relevant to "linear attention"
- ✓ Shows recency ("Dec 9, 2025", "Dec 8, 2025")
- ✗ Still no code indicators despite this being a common need

**Pain Point Solved**: **Connection Blindness** - Finding papers across different months, different terminology, unified by semantic understanding.

**Emotional State**: 4/5 - Pleased with consistency and relevance.

---

### Step 12: Final Reflection
**Screenshot**: `12-final-state.png`

**Overall Experience**: Mixed. The Research Advisor is legitimately impressive - it found papers I wouldn't have discovered through keyword search. But the missing reproducibility features and 404 discovery routes make this feel like an incomplete product.

**Time Spent**: ~18 minutes. Found 2-3 papers I'll actually read (GNNs-to-KANs, InfiniteVL, LUNA).

**Emotional State**: 3/5 - Cautiously optimistic but wary of broken features.

---

## Problem Assessment: Did It Solve My Pain Points?

| Pain Point | Status | Evidence |
|------------|--------|----------|
| **Information Overload** | ✓ SOLVED | Research Advisor filtered 197 papers → 6/36 highly relevant |
| **Time Poverty** | ≈ PARTIAL | Fast semantic search (2-4s) but no TL;DR scan mode |
| **Reproducibility Frustration** | ✗ FAILED | Code filter broken, no GitHub links visible |
| **Connection Blindness** | ✓ SOLVED | Found papers using "edge deployment" when I said "mobile" |
| **Trend Anxiety** | ✗ FAILED | No trending/rising pages, "Trending Now" shows "No data" |

**Score**: 2/5 pain points fully solved, 1/5 partial, 2/5 failed.

---

## Delights 🎉

1. **Research Advisor Semantic Search** ⭐⭐⭐
   - Game-changer for finding relevant papers across terminology variations
   - Found "edge deployment" papers when I searched "mobile deployment"
   - Actually understands research context, not just keywords

2. **Response Time** ⭐⭐
   - 2-4 seconds for semantic search feels fast enough
   - No frustrating loading states

3. **Clean, Professional UI** ⭐
   - Not overwhelming like some research tools
   - Clear hierarchy, easy to scan

---

## Frustrations 😤

1. **Broken Code Filter** ⭐⭐⭐ (CRITICAL)
   - "Has Code" filter does nothing
   - No GitHub links visible anywhere
   - No stars/forks shown
   - **This is a deal-breaker** for reproducibility-focused researchers

2. **All Discovery Routes 404** ⭐⭐⭐ (CRITICAL)
   - Promised features don't exist: TL;DR, techniques, trending, learning paths
   - Feels like vaporware - advertised but not built
   - Sidebar shows "Trending Topics" but clicking leads nowhere

3. **Confusing Dual Search UX** ⭐⭐
   - Why have keyword search AND Ask Advisor?
   - Keyword search seems broken (returns same results regardless of query)
   - Should just make semantic search the default

4. **No Paper Relationship Graphs** ⭐
   - Can't visualize citations or similar papers
   - "Related Papers" tab exists but not explored

5. **"Invalid Date" on Many Papers** ⭐
   - Metadata quality issues undermine trust

---

## Performance Metrics

- **Page Load Time**: ~3s (acceptable)
- **Search Response Times**:
  - First semantic search: 2.6s
  - Second semantic search: 3.8s
- **No performance issues** during session

---

## Priority Improvements

| Improvement | Impact | Effort | Priority | Reasoning |
|-------------|--------|--------|----------|-----------|
| **Fix "Has Code" filter** | HIGH | MED | P0 | Broken core feature. Non-negotiable for reproducibility researchers. |
| **Show GitHub links/badges** | HIGH | LOW | P0 | Critical metadata. Easy win - just display what you have. |
| **Build discovery routes OR remove links** | HIGH | HIGH | P0 | Having 404s damages trust. Either build or remove. |
| **Make semantic search default** | MED | LOW | P1 | Why force users to discover the better search? Just use it. |
| **Add TL;DR quick scan mode** | HIGH | HIGH | P1 | Huge time-saver for busy researchers. Differentiator. |
| **Fix paper dates ("Invalid Date")** | MED | MED | P2 | Metadata quality undermines trust. |
| **Add GitHub stars/forks counts** | MED | LOW | P2 | Helps assess code quality/adoption. |
| **Show trending papers** | MED | HIGH | P2 | Currently shows "No data" - finish this feature. |
| **Paper similarity graph viz** | LOW | HIGH | P3 | Nice-to-have but not critical for my workflow. |

---

## Screenshot Index

1. **01-landing-first-impression.png**: Initial page load showing CV papers
2. **02a-nav-generate.png**: Generate tab with code generation feature
3. **03b-research-advisor.png**: Advisor modal with relevant results
4. **04-paper-expanded.png**: Expanded paper view with full abstract
5. **05-code-filter.png**: "Has Code" filter applied (but ineffective)
6. **06-reproducible-404.png**: 404 error on /discovery/reproducible
7. **07-tldr-404.png**: 404 error on /discovery/tldr
8. **08-techniques-404.png**: 404 error on /discovery/techniques
9. **09-rising-404.png**: 404 error on /discovery/rising
10. **11-second-search-results.png**: "Linear attention" search results
11. **12-final-state.png**: Final state showing search results

---

## Final Verdict

**Would I bookmark this tool?** Yes, cautiously. The Research Advisor is genuinely useful for semantic discovery.

**Would I return tomorrow?** Maybe. Depends on if the code filter gets fixed. Without reproducibility features, it's not better than Papers with Code.

**Would I recommend to colleagues?** Not yet. Too many broken features. I'd wait for:
1. Code filter to work
2. Discovery routes to be built or removed
3. GitHub links to be visible

**Overall Rating**: **3/5** - Promising core technology (semantic search), but feels like an incomplete MVP. Fix the broken features and this could be a daily driver.

---

## Researcher's Bottom Line

As a postdoc with 20 minutes to find papers before my advisor meeting, I **did find 2-3 papers I didn't know about** (GNNs-to-KANs, InfiniteVL, LUNA). That's a win. But I **couldn't tell which have code**, so I'll still need to visit GitHub separately. The tool saved me discovery time but didn't solve my reproducibility pain.

**Best Use Case**: Exploratory semantic search when you're not sure what terminology to use.

**Don't Use For**: Finding papers with code (broken), trending research (doesn't exist), quick TL;DR scanning (doesn't exist).

**Competitive Position**: Better semantic search than arXiv, worse reproducibility features than Papers with Code. Needs to decide what problem it's solving.
