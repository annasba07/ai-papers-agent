# UX Assessment: Dr. Maya Chen - AI Paper Atlas
**Date**: December 25, 2025
**Duration**: ~20 minutes
**Persona**: 2nd-year postdoc, CMU Machine Learning Dept
**Research Focus**: Efficient transformers for mobile deployment

---

## Executive Summary

As a time-pressured researcher looking for efficient attention mechanisms, AI Paper Atlas failed to deliver basic functionality. Search returned zero results for my core research topic, multiple discovery tabs showed errors instead of content, and the Research Advisor feature—while conceptually promising—took 15+ seconds to return papers that weren't directly relevant to my query. **I would not return to this tool.** The core value proposition (finding papers quickly) was not met.

---

## Session Timeline

| Time | Step | Action | Outcome | Emotion (1-5) |
|------|------|--------|---------|---------------|
| 0:00 | Setup | Navigate to localhost:3000 | Landed on Explore page, papers loading | 3 |
| 0:15 | Landing | Page loaded with CV papers visible | Clean interface, search box prominent | 3 |
| 0:45 | Navigation | Clicked Discovery tab | Saw tabs for different discovery modes | 3 |
| 1:00 | Reproducible | Clicked Reproducible tab | Loading hung for 5s, then showed error | 2 |
| 1:30 | Generate | Viewed Generate page | Code generation feature noted | 3 |
| 2:00 | **Search** | Typed "efficient attention mechanisms" | Auto-search triggered, showed "Searching..." | 3 |
| 2:15 | Search Wait | Waited for results | **Returned 0 results** after 10s | 2 |
| 2:30 | **Advisor** | Clicked "Ask Advisor" button | Advisor panel opened with suggestions | 3 |
| 2:45 | Advisor Query | Entered "efficient attention mechanisms for mobile deployment" | Query submitted, "Searching papers..." shown | 3 |
| 3:00 | Advisor Wait | Waited 15+ seconds | Still loading... | 2 |
| 3:15 | Advisor Result | **Got response** | 5 papers shown but NOT FlashAttention/relevant work | 3 |
| 3:30 | Paper Detail | Expanded first paper (StereoSpace) | Full abstract shown, "Generate Code" link visible | 3 |
| 3:45 | **Code Filter** | Clicked "Has Code" filter | Filter badge appeared but **results didn't change** | 3 |
| 4:00 | Discovery Retry | Went back to Discovery tab | Error: "Failed to fetch impact papers" | 2 |
| 4:15 | Techniques | Clicked Techniques tab | Error: "Failed to fetch technique papers" | 2 |
| 4:30 | TL;DR | Clicked TL;DR tab | Error + "No recent papers with executive summaries" | 2 |
| 4:45 | Clear Filter | Removed "Has Code" filter | Search re-triggered | 2 |
| 5:00 | **Final State** | Search completed | **Still 0 results** for "efficient attention mechanisms" | 1 |

**Total Screenshots Captured**: 10
**Critical Errors Encountered**: 5 (search failure, 3 discovery tab errors, Reproducible timeout)

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

**Visual Observations** (Screenshots 01, 01b):
- Clean, professional design with Paper Atlas branding
- Large search box with placeholder: "Describe what you're researching..."
- "Ask Advisor" button prominently placed (orange/red accent)
- Sidebar with filters: Has Code, High Impact, Seminal Papers, Categories, Difficulty, Time Range
- Trending Topics sidebar showing live growth percentages
- Papers loaded showing recent CS.CV papers with TL;DR summaries

**Initial Reaction**:
The interface looks polished and the value proposition is clear: search for AI papers with filtering and AI-powered assistance. The "Ask Advisor" button suggests intelligent search beyond keywords. However, I immediately noticed the default papers shown were all Computer Vision—not my field (efficient transformers). This made me wonder about relevance.

**Performance**: Page loaded quickly, papers appeared within ~2 seconds.

**Emotion**: 3/5 (Neutral, cautiously optimistic)

---

### Step 2: Navigation Discovery

**Screenshots**: 02a-nav-discovery.png, 02b-reproducible-loading.png, 02c-reproducible-timeout.png, 02d-nav-generate.png

**What I Explored**:
1. **Discovery Hub** - Found tabs for: Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path
2. **Reproducible Tab** - Clicked this first (critical for my work)
   - Showed "Finding reproducible papers..." loading state
   - **Hung for 5+ seconds**
   - **Error: "Failed to fetch impact papers"**
3. **Generate Page** - "Turn Papers into Working Code" feature
   - Interesting concept but not my immediate need

**Navigation Assessment**:
- Tab labels are clear and intuitive
- Good categorization of discovery modes
- **BUT: Multiple tabs failed to load**, raising concerns about reliability

**Emotion**: 2-3/5 (Concerned about errors, but interface is understandable)

---

### Step 3: Task-Based Search - Finding Relevant Papers

**Screenshots**: 03a-search-typed.png, 03b-search-timeout.png

**My Query**: "efficient attention mechanisms"
**Expected**: Papers on FlashAttention, Linformer, Performer, sparse attention, linear attention
**Actual Result**: **0 papers found** after 10 seconds

**Search Behavior**:
- Auto-search triggered as I typed (good UX)
- Showed "AI-powered semantic search in progress..." (promising)
- Search time: **10,004ms** (10 seconds—too slow)
- Result: "No papers found. Try different keywords or describe your research goal in more detail."

**Critical Failure**:
This is a fundamental failure. "Efficient attention mechanisms" is a well-established research area with hundreds of papers. Major works include:
- FlashAttention (Dao et al., 2022)
- Linformer (Wang et al., 2020)
- Performer (Choromanski et al., 2021)
- Sparse Transformers (Child et al., 2019)

The tool claims to have "138,986 papers indexed" but couldn't find ANY papers on a core ML topic.

**Emotion**: 2/5 (Frustrated, starting to lose confidence)

---

### Step 3.5: Research Advisor - AI-Powered Search

**Screenshots**: 03c-advisor-opened.png, 03d-advisor-searching.png, 03e-advisor-timeout.png, 03f-advisor-response.png

**Fallback Strategy**: Since basic search failed, I tried the "Ask Advisor" feature.

**My Query**: "efficient attention mechanisms for mobile deployment"

**Advisor Experience**:
1. Panel opened quickly with example questions (good)
2. Submitted my query
3. **Waited 15+ seconds** with "Searching papers..." spinner
4. Finally got a response:
   - "Contextual synthesis temporarily unavailable"
   - Listed 5 papers:
     - Adaptive Attention-Based Model for 5G Radio-based Outdoor Localization
     - DeltaLLM: A Training-Free Framework Exploiting Temporal Sparsity for Efficient Edge LLM Inference
     - Taming the Titans: A Survey of Efficient LLM Inference Serving
     - An Efficient GNNs-to-KANs Distillation...
     - Dynamic Graph Communication for Decentralised Multi-Agent RL

**Assessment**:
- **Response time: 15+ seconds** (unacceptable for a 20-minute research session)
- **Results were tangentially related** but not what I needed:
  - "DeltaLLM" is about LLM inference, not attention mechanisms
  - "5G Radio localization" is completely unrelated
  - No FlashAttention, no seminal attention papers
- The "temporarily unavailable" message suggests the feature is broken
- Follow-up buttons ("Find papers that cite these works", "Show me implementation code") were interesting but I didn't trust them given the poor initial results

**Emotion**: 3/5 (Relieved to get *something*, but disappointed by relevance)

---

### Step 4: Deep Dive - Paper Detail

**Screenshot**: 04-paper-expanded.png

I expanded the first paper (StereoSpace) to see what detail view offers:

**What I Saw**:
- Full abstract displayed
- Tabs: Summary, Related Papers, Benchmarks
- "Read on arXiv" link
- "Generate Code" link

**Assessment**:
- The detail view is clean and informative
- Tabs suggest rich analysis (Related Papers, Benchmarks)
- **However**, I didn't explore further because this paper wasn't relevant to my research

**Emotion**: 3/5 (Neutral—feature looks good but not useful for irrelevant papers)

---

### Step 5: Code Availability Check

**Screenshot**: 05-code-filter-applied.png

**Action**: Clicked "Has Code" filter to find reproducible papers

**Result**:
- Filter badge appeared in the search bar: "Has Code ×"
- **Results remained at 0 papers**
- No change in search outcome

**Assessment**:
- Filter UI works (badge appeared)
- **But filtering 0 results = still 0 results**
- Can't evaluate the code filtering feature because search is broken

**Pain Point Addressed?** NO—my "Reproducibility Frustration" pain point requires finding papers FIRST, then filtering for code. Since search found nothing, this feature is useless.

**Emotion**: 3/5 (Filter UX is fine, but doesn't help with core problem)

---

### Step 6-8: Discovery Tab Errors

**Screenshots**: 06-discovery-error.png, 07-techniques-error.png, 08-tldr-error.png

Attempted to use Discovery features as alternative to broken search:

| Tab | Result | Error Message |
|-----|--------|---------------|
| **Reproducible** | Failed | "Failed to fetch impact papers" |
| **Techniques** | Failed | "Failed to fetch technique papers" |
| **TL;DR** | Failed | "Failed to fetch TL;DR papers" + "No recent papers with executive summaries found from the last 7 days" |

**Pattern**: All discovery tabs failed to load. This suggests backend API issues or database problems.

**Emotion**: 2/5 (Multiple failures erode trust)

---

### Step 9-11: Trending & Retry

**Screenshots**: 09-back-to-explore.png, 10-final-state.png

**Trending Topics**: Sidebar showed topics like "Dropout", "SSM", "PEFT", "RLHF", "Distillation", "Diffusion" with growth percentages. These worked and were visible throughout.

**Second Search Attempt**: Removed "Has Code" filter and searched again
- **Result: Still 0 papers** for "efficient attention mechanisms"
- **Emotion**: 1/5 (Completely frustrated)

---

## Problem Assessment: Did It Solve My Pain Points?

### Pain Point 1: Information Overload
**Status**: ❌ NOT ADDRESSED
**Reason**: Tool couldn't find papers in the first place. Can't reduce overload if there's nothing to filter.

### Pain Point 2: Time Poverty
**Status**: ❌ MADE WORSE
**Reason**:
- Wasted **10+ seconds on failed search**
- Wasted **15+ seconds on Research Advisor** that returned poor results
- Wasted time clicking through broken Discovery tabs
- **Total time wasted: ~5 minutes** with zero papers found

### Pain Point 3: Reproducibility Frustration
**Status**: ❌ NOT ADDRESSABLE
**Reason**: "Has Code" filter exists but is useless when search returns 0 results. The Reproducible discovery tab was broken.

### Pain Point 4: Connection Blindness
**Status**: ❌ NOT ADDRESSABLE
**Reason**: "Related Papers" feature exists in paper detail view, but I couldn't test it because search didn't find relevant papers to start from.

### Pain Point 5: Trend Anxiety
**Status**: ⚠️ PARTIALLY ADDRESSED
**Reason**: Trending Topics sidebar (Dropout +29900%, SSM +12841%, etc.) DID work and was interesting. However, these are technique names, not papers. I couldn't click through to see which attention papers are trending.

---

## Delights and Frustrations

### Delights ✨
1. **Clean, professional interface** - Visually polished, modern design
2. **Trending Topics sidebar** - Live growth percentages were engaging
3. **"Ask Advisor" concept** - AI-powered research assistant is promising
4. **Auto-search** - Search triggered as I typed (no button click needed)
5. **Filter UI** - Clear badges for active filters

### Frustrations 😤
1. **Search returned 0 results** for a major research area ⚠️ CRITICAL
2. **Research Advisor took 15+ seconds** and gave poor results ⚠️ CRITICAL
3. **Multiple Discovery tabs failed to load** (Reproducible, Techniques, TL;DR) ⚠️ CRITICAL
4. **10-second search time** is too slow for iterative exploration
5. **No error recovery guidance** - "Try different keywords" isn't helpful when the problem is the index, not my query
6. **No example queries** that actually work - If search is broken, show me what DOES work
7. **Misleading stats** - "138,986 papers indexed" but can't find basic topics?

---

## Performance Metrics

| Metric | Value | Target | Assessment |
|--------|-------|--------|------------|
| **Landing Page Load** | ~2s | <3s | ✅ Good |
| **Search Response Time** | 10,004ms | <3s | ❌ Too Slow |
| **Research Advisor Response** | 15+ seconds | <5s | ❌ Way Too Slow |
| **Discovery Tab Loads** | Failed | N/A | ❌ Broken |
| **Relevant Results (Search)** | 0 / 0 | 5+ | ❌ Total Failure |
| **Relevant Results (Advisor)** | 1-2 / 5 | 3+ | ⚠️ Poor |

**Core Web Vitals**: Not measured (page functionality failed before performance became relevant)

---

## Priority Improvements

### P0: CRITICAL - Fix Core Search
**Impact**: 🔴 **HIGHEST** | **Effort**: Unknown (likely backend/index issue)

**Issue**: Search returns 0 results for "efficient attention mechanisms" despite 138K papers indexed.

**Recommendation**:
1. **Investigate search index** - Is it actually populated? Check database queries.
2. **Test with known queries** - "attention is all you need", "BERT", "GPT", "ResNet"
3. **Add fallback search** - If semantic search fails, fall back to keyword matching
4. **Show debug info** - In dev mode, show which search method was used and why it failed

**Why P0**: Without working search, the entire product is unusable.

---

### P0: CRITICAL - Fix Discovery Tab Backend
**Impact**: 🔴 **HIGHEST** | **Effort**: Medium-High

**Issue**: Reproducible, Techniques, and TL;DR tabs all show "Failed to fetch" errors.

**Recommendation**:
1. **Check API endpoints** - Are `/api/discovery/reproducible`, `/api/discovery/techniques`, `/api/discovery/tldr` returning errors?
2. **Add error boundaries** - Show user-friendly messages with retry buttons
3. **Test data population** - Ensure database has required data for these views

**Why P0**: Discovery features are advertised in navigation but completely broken.

---

### P1: HIGH - Improve Research Advisor Performance
**Impact**: 🟠 **HIGH** | **Effort**: High

**Issue**: 15+ second response time, poor relevance, "temporarily unavailable" error message

**Recommendation**:
1. **Optimize LLM/retrieval pipeline** - 15s is unacceptable; target <5s
2. **Add streaming responses** - Show papers as they're found, not all at once
3. **Improve relevance** - "efficient attention mechanisms for mobile deployment" should return FlashAttention, MobileBERT, TinyBERT, etc.
4. **Remove "temporarily unavailable" message** - Either fix it or hide the feature

**Why P1**: This is the fallback when search fails. If both search AND advisor fail, users have no path forward.

---

### P1: HIGH - Add Example Queries & Onboarding
**Impact**: 🟠 **HIGH** | **Effort**: Low

**Issue**: When search fails, users don't know what queries actually work.

**Recommendation**:
1. **Add "Example Searches"** below search box:
   - "Papers on transformer architectures"
   - "Recent work in computer vision"
   - "Reinforcement learning for robotics"
2. **Test these examples** - Ensure they actually return results
3. **Add tooltip** - "Describe your research problem in natural language"
4. **Empty state improvement** - Instead of "Try different keywords", show:
   - "Tip: Describe your research problem (e.g., 'attention mechanisms for mobile devices')"
   - "Or try one of these: [Example 1] [Example 2] [Example 3]"

**Why P1**: Helps users discover working functionality even when their queries fail.

---

### P2: MEDIUM - Improve Search Performance
**Impact**: 🟡 **MEDIUM** | **Effort**: Medium

**Issue**: 10-second search time is too slow for iterative exploration.

**Recommendation**:
1. **Add caching** - Cache common queries and semantic embeddings
2. **Optimize database queries** - Add indexes for common filters
3. **Show incremental results** - Display results as they arrive, don't wait for full query
4. **Add cancel button** - Let users cancel long-running searches

**Target**: <3 seconds for typical queries, <1s for cached queries

---

### P2: MEDIUM - Filter Feedback Improvements
**Impact**: 🟡 **MEDIUM** | **Effort**: Low

**Issue**: "Has Code" filter applied but results didn't change (hard to tell if filter worked)

**Recommendation**:
1. **Show filter counts** - "Has Code (1,234)" before clicking
2. **Show result diff** - "Filtered from 5,000 to 1,234 papers"
3. **Disable unavailable filters** - If no papers have code, gray out "Has Code" filter
4. **Add filter preview** - Hover over filter to see count before applying

---

## Screenshots Index

| # | Filename | Description | Emotion |
|---|----------|-------------|---------|
| 01 | `01-landing-first-impression.png` | Initial landing, loading state | 3/5 |
| 01b | `01b-landing-loaded.png` | Papers loaded, CV papers visible | 3/5 |
| 02a | `02a-nav-discovery.png` | Discovery hub with tabs | 3/5 |
| 02b | `02b-reproducible-loading.png` | Reproducible tab loading | 3/5 |
| 02c | `02c-reproducible-timeout.png` | Reproducible error after timeout | 2/5 |
| 02d | `02d-nav-generate.png` | Generate page view | 3/5 |
| 03a | `03a-search-typed.png` | Search query typed, auto-searching | 3/5 |
| 03b | `03b-search-timeout.png` | **Search returned 0 results** | 2/5 |
| 03c | `03c-advisor-opened.png` | Research Advisor panel opened | 3/5 |
| 03d | `03d-advisor-searching.png` | Advisor searching for papers | 3/5 |
| 03e | `03e-advisor-timeout.png` | Advisor still loading after 15s | 2/5 |
| 03f | `03f-advisor-response.png` | Advisor returned 5 papers | 3/5 |
| 04 | `04-paper-expanded.png` | Paper detail view with abstract | 3/5 |
| 05 | `05-code-filter-applied.png` | "Has Code" filter badge shown | 3/5 |
| 06 | `06-discovery-error.png` | Discovery tab error | 2/5 |
| 07 | `07-techniques-error.png` | Techniques tab error | 2/5 |
| 08 | `08-tldr-error.png` | TL;DR tab error | 2/5 |
| 09 | `09-back-to-explore.png` | Removed filter, searching again | 2/5 |
| 10 | `10-final-state.png` | **Still 0 results after retry** | 1/5 |

**Total**: 10 screenshots captured
**Average Emotion**: 2.6/5 (Disappointed)

---

## Final Verdict

### Would I bookmark this tool?
**NO.** The core functionality (search) is completely broken.

### Would I return tomorrow?
**NO.** I wasted 20 minutes and found zero papers relevant to my research. I'll stick with Google Scholar, Semantic Scholar, and arXiv.

### Would I recommend it to colleagues?
**NO.** I would warn them that it's not ready for use. The errors and failed searches would waste their time.

### What frustrated me most?
**Search returning 0 results for "efficient attention mechanisms"** while claiming to have 138,986 papers indexed. This is a fundamental failure that makes all other features irrelevant.

### What delighted me most?
**The interface design and the concept.** If the backend worked, this could be a valuable tool. The Research Advisor feature, Trending Topics, and discovery modes show promise. But promise doesn't find papers.

---

## Summary for Developers

**Critical Path Failure**: Search → Research Advisor → Discovery Tabs all failed. User has NO working path to find papers.

**Fix These First**:
1. Search index (0 results for major topics)
2. Discovery API endpoints (all returning errors)
3. Research Advisor performance & relevance

**Then Improve**:
4. Search speed (<3s target)
5. Example queries & onboarding
6. Filter feedback

**Don't Work On** (until core is fixed):
- Visual refinements
- New features
- Performance optimizations

**As a researcher**: I need a tool that finds papers FAST and ACCURATELY. AI Paper Atlas failed on both counts. Fix search first, everything else second.

---

**Assessment completed**: 2025-12-25, ~20 minutes
**Recommendation**: **NOT READY FOR PRODUCTION USE**
**Return likelihood**: 5% (only if core search is completely rebuilt)
