# UX Assessment Report: AI Paper Atlas
**Persona:** Prof. James Williams (MIT CSAIL, preparing graduate seminar on efficient language models)
**Date:** 2025-12-19
**Session Duration:** ~25 minutes
**Assessment Type:** 13-Step Structured UX Evaluation

---

## Executive Summary

As a senior faculty member preparing a graduate seminar, I need tools that save time, not waste it. AI Paper Atlas shows potential with 138,986 indexed papers and interesting discovery features, but critical functionality is broken. The Research Advisor errors out, TL;DR summaries never load, Learning Paths generate irrelevant papers, and Related Papers remain stuck loading. Basic search works, but the value proposition—AI-powered assistance beyond keyword matching—falls short. **I would not bookmark this tool in its current state.** Verdict: 2/5 overall.

---

## Session Timeline

| Step | Feature | Time | Emotion | Task Success |
|------|---------|------|---------|--------------|
| 0 | Environment setup | 0:00 | 3/5 | ✓ |
| 1 | Landing page first impression | 0:01 | 3/5 | ✓ |
| 2 | Navigation discovery | 0:03 | 3/5 | ✓ |
| 3 | Task-based search (efficient language models) | 0:05 | 3/5 | ✓ |
| 3.5 | Research Advisor test | 0:07 | 1/5 | ✗ Error |
| 4 | Paper detail examination | 0:09 | 3/5 | ✓ |
| 5 | Code availability check | 0:11 | 2/5 | Partial |
| 6 | Learning Path (efficient transformers) | 0:13 | 1/5 | ✗ Irrelevant |
| 7 | TL;DR scan mode | 0:15 | 1/5 | ✗ Never loads |
| 8 | Technique explorer | 0:17 | 4/5 | ✓ |
| 9 | Rising papers/trending | 0:19 | 4/5 | ✓ |
| 10 | Paper relationships | 0:21 | 2/5 | ✗ Stuck loading |
| 11 | Second search (neural architecture search) | 0:23 | 3/5 | ✓ |
| 12 | Exit reflection | 0:25 | 2/5 | ✓ |

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)
**Screenshot:** `01-landing-first-impression.png`
**Observation:** Clean interface, 138,986 papers indexed, search bar prominent
**Emotion:** 3/5 (Neutral - professional but not compelling)

The landing page is clean and professional. The search bar is immediately visible with placeholder text suggesting semantic queries ("efficient attention for mobile deployment"). The large paper count (138k+) signals comprehensive coverage. However, there's no immediate clarity on what makes this different from arXiv or Google Scholar. The value proposition is implied, not stated.

**What worked:**
- Clean, uncluttered design
- Obvious search entry point
- Professional appearance builds initial trust

**What didn't:**
- No clear differentiation from existing tools
- No immediate evidence of AI assistance value
- Missing quick-start guidance for new users

---

### Step 2: Initial Exploration (Navigation Discovery)
**Screenshots:** `02a-discovery-page.png`, `02b-tldr-loading.png`
**Observation:** Four main sections: Explore, Discovery, Reading List, Generate
**Emotion:** 3/5 (Intrigued but cautious)

Navigation is straightforward with four top-level tabs. The Discovery section promises specialized views (TL;DR, Learning Path, Techniques, Rising, Reproducible). However, clicking TL;DR immediately revealed the first broken feature—infinite "Loading summaries..." state. This early failure undermined confidence.

**What worked:**
- Clear navigation structure
- Descriptive section labels
- Multiple specialized views available

**What didn't:**
- TL;DR feature broken (infinite loading)
- No explanation of what each discovery mode offers
- Early broken feature damages trust

---

### Step 3: Task-Based Search (Efficient Language Models)
**Screenshot:** `03-search-results.png`
**Observation:** 31 results (6 AI-matched + 25 keyword), fast response
**Emotion:** 3/5 (Functional but unremarkable)

Searched for "efficient language models" and got 31 relevant results quickly. The system splits results into "AI-matched" (6 papers) and "Keyword match" (25 papers), which is interesting but unclear. What makes the AI-matched papers special? Results appear relevant based on titles. Response time felt fast (<2 seconds).

**What worked:**
- Fast search response
- Results appear relevant to query
- Clear result count and categorization

**What didn't:**
- Unclear what "AI-matched" vs "Keyword" means
- No explanation of ranking methodology
- Results look similar to standard keyword search

---

### Step 3.5: Research Advisor (AI-Powered Search)
**Screenshots:** `03b-advisor-panel-open.png`, `03c-advisor-query-sent.png`
**Observation:** Advisor modal opened but returned error on query
**Emotion:** 1/5 (Frustrated - flagship feature broken)

Clicked "Ask Advisor" button, which opened a modal with suggested queries. This appeared to be the flagship AI-powered feature. Sent query: "What are the latest techniques for reducing transformer inference latency?" The system returned: **"Sorry, I encountered an error while searching. Please try again."** Second critical feature failure. This is supposed to be the differentiator, and it doesn't work.

**What worked:**
- Modal design is clean
- Suggested example queries helpful
- Clear input field

**What didn't:**
- **CRITICAL: Feature completely non-functional**
- Error message unhelpful (no guidance on what to do)
- No fallback or alternative suggestions
- Core value proposition fails immediately

---

### Step 4: Deep Dive (Paper Detail)
**Screenshot:** `04-paper-detail-expanded.png`
**Observation:** Paper expands with Summary/Related Papers/Benchmarks tabs
**Emotion:** 3/5 (Adequate - basic functionality works)

Expanded a paper to see detail view. Three tabs available: Summary, Related Papers, Benchmarks. The Summary tab showed paper metadata, TL;DR summary, and basic information. This works as expected and provides useful quick context. However, the AI analysis is minimal—just a TL;DR, not deep technique extraction or methodology analysis as suggested by the landing page.

**What worked:**
- Expandable paper details without page navigation
- Three-tab organization logical
- TL;DR summaries helpful for quick triage

**What didn't:**
- Limited depth of AI analysis
- No visible technique extraction or methodology breakdown
- Unclear if AI summary is better than abstract

---

### Step 5: Code Availability Check
**Screenshot:** `05-code-filter-applied.png`
**Observation:** "Has Code" filter applied but still shows all 31 results
**Emotion:** 2/5 (Confused - filter appears broken)

As a researcher preparing a practical seminar, code availability is critical. Clicked "Has Code" quick filter expecting results to narrow. The filter button highlighted as active, but results count stayed at 31 papers. Either all 31 papers have code (unlikely), or the filter isn't working. No GitHub indicators visible in result list to confirm code availability.

**What worked:**
- Filter button easy to find
- Quick filter concept good for common use cases

**What didn't:**
- **LIKELY BUG: Filter doesn't appear to reduce results**
- No visual indicators (GitHub icon) on papers with code
- Can't verify which papers actually have code repositories
- Critical feature for reproducibility research

---

### Step 6: Learning Path Assessment
**Screenshot:** `06-learning-path.png`
**Observation:** Generated learning path for "efficient transformers" returns completely unrelated papers
**Emotion:** 1/5 (Baffled - results make no sense)

Navigated to Discovery → Learning Path and requested a learning path for "efficient transformers". Expected: foundational papers on attention mechanisms → transformer efficiency techniques → recent advances. Got: papers on cryo-electron tomography, multi-agent pathfinding, and other completely unrelated topics. **This is catastrophically broken.** A learning path with wrong papers is worse than no learning path—it actively misleads students.

**What worked:**
- Learning path interface exists
- Concept of progressive difficulty is valuable

**What didn't:**
- **CRITICAL: Results completely unrelated to query**
- Would actively harm students if used
- No apparent semantic understanding of the query
- Feature unusable in current state

---

### Step 7: TL;DR / Quick Scan Mode
**Screenshot:** `07-tldr-still-loading.png`
**Observation:** Feature stuck in infinite "Loading summaries..." state
**Emotion:** 1/5 (Resigned - another broken feature)

Returned to TL;DR tab to attempt quick scanning of recent papers. The page shows "Loading summaries..." indefinitely. Waited 30+ seconds with no change. This is the third major feature failure. For a tool promising AI-powered paper analysis, having the summary view broken is unacceptable.

**What worked:**
- (Nothing—feature non-functional)

**What didn't:**
- **CRITICAL: Infinite loading state, no summaries ever appear**
- No error message or timeout
- No fallback to basic paper list
- Core value proposition (AI summaries) fails

---

### Step 8: Technique Explorer
**Screenshot:** `08-techniques-loading.png`
**Observation:** Technique tags loaded successfully, browsable by methodology
**Emotion:** 4/5 (Pleased - finally something works well)

Navigated to Discovery → Techniques. This feature actually works! Shows a large collection of technique tags organized by categories (Architectures, Training Methods, etc.). Can browse papers by specific techniques. This is useful for curriculum planning—I can find papers by specific methods (e.g., "Flash Attention", "LoRA", "Mixture of Experts"). First feature that delivers on the AI-powered promise.

**What worked:**
- **Feature actually functional**
- Comprehensive technique taxonomy
- Useful for finding papers by methodology
- Good for curriculum planning

**What didn't:**
- Could benefit from technique descriptions/definitions
- Unclear how techniques are extracted (manual tags? AI?)

---

### Step 9: Rising Papers / Hot Topics
**Screenshot:** `09-rising-loading.png`
**Observation:** Rising papers loaded with citation velocity metrics (300.6 cites/mo, 81.4 cites/mo)
**Emotion:** 4/5 (Impressed - useful metric)

Navigated to Discovery → Rising. Shows papers with high citation velocity (citations per month). This is genuinely useful—better than raw citation counts for identifying emerging important work. Metrics like "300.6 cites/mo" help identify papers gaining rapid traction. Would be valuable for keeping seminar current with trending research.

**What worked:**
- **Feature functional and useful**
- Citation velocity is smart metric
- Helps identify emerging important work
- Better than static "most cited" lists

**What didn't:**
- Limited to recent papers (by design)
- Could benefit from trending topics/themes

---

### Step 10: Paper Relationships / Similarity Graph
**Screenshot:** `10-related-papers.png`
**Observation:** Related Papers tab stuck in "Finding similar papers..." loading state
**Emotion:** 2/5 (Disappointed - pattern continues)

Searched for "attention mechanisms" (36 results), expanded a paper, clicked "Related Papers" tab. Tab shows "Finding similar papers..." loading message indefinitely. Fourth major feature failure. The ability to explore paper relationships is valuable for comprehensive literature reviews, but it doesn't work.

**What worked:**
- Related Papers tab concept is sound
- Would be valuable for literature mapping

**What didn't:**
- **CRITICAL: Infinite loading, no results**
- No timeout or error handling
- Can't explore paper relationships
- Important feature for comprehensive research

---

### Step 11: Second Search (Consistency Check)
**Screenshot:** `11-second-search.png`
**Observation:** Searched "neural architecture search", got 30 results, consistent experience
**Emotion:** 3/5 (Neutral - at least search is consistent)

Performed second search to check consistency. Query "neural architecture search" returned 30 results quickly. Search experience consistent with first attempt—fast response, categorized results (keyword matches). At least basic search functionality is reliable, even if advanced features fail.

**What worked:**
- Consistent search experience
- Fast response time maintained
- Results appear relevant

**What didn't:**
- Still no differentiation from basic keyword search
- Advanced AI features still broken on retry
- Reliability only at baseline level

---

### Step 12: Exit Reflection
**Screenshot:** `12-final-state.png`
**Emotion:** 2/5 (Would not return)

After 25 minutes of testing, my verdict as a senior faculty member preparing a graduate seminar:

**Would I bookmark this tool?** No.
**Would I return tomorrow?** No.
**Would I recommend to colleagues?** No—too many broken features to risk professional reputation.

**What frustrated me most:**
Multiple flagship features completely broken (Research Advisor, TL;DR, Learning Path, Related Papers). These are the differentiators—if they don't work, this is just a worse version of arXiv search.

**What delighted me most:**
Techniques explorer and Rising papers actually work and provide value. Citation velocity is a smart metric.

---

## Problem Assessment: Did It Solve My Pain Points?

As a professor preparing a graduate seminar on efficient language models, I need:

| Pain Point | Tool Solution | Verdict |
|------------|---------------|---------|
| **Finding foundational → advanced progression** | Learning Path feature | ✗ BROKEN - Irrelevant papers |
| **Identifying code-available papers** | "Has Code" filter | ✗ BROKEN - Doesn't filter |
| **Quick triage of new papers** | TL;DR summaries | ✗ BROKEN - Never loads |
| **Semantic search beyond keywords** | Research Advisor | ✗ BROKEN - Returns errors |
| **Finding papers by technique** | Techniques explorer | ✓ WORKS - Actually useful |
| **Identifying important emerging work** | Rising papers (citation velocity) | ✓ WORKS - Smart metric |
| **Exploring related work** | Related Papers | ✗ BROKEN - Stuck loading |

**Score: 2/7 major use cases functional (29%)**

---

## Delights and Frustrations

### Delights (What Worked)
1. **Techniques Explorer** - Finally, a way to find papers by specific methods (Flash Attention, LoRA, etc.). Useful for curriculum design.
2. **Citation Velocity Metric** - Smarter than raw citation counts for identifying emerging important work.
3. **Fast Basic Search** - Keyword search is fast and reliable.
4. **Clean Interface** - Professional design, not cluttered.

### Frustrations (What Didn't Work)
1. **Research Advisor Completely Broken** - Core differentiator returns errors. Unacceptable.
2. **Learning Path Generates Gibberish** - Asked for "efficient transformers", got cryo-electron tomography. Actively harmful.
3. **TL;DR Infinite Loading** - Promising feature, never works. Waited 60+ seconds.
4. **Related Papers Never Load** - Another infinite loading state. Pattern suggests infrastructure issues.
5. **Code Filter Ineffective** - Applied "Has Code" filter, results didn't change. Bug or misleading UI?
6. **No Error Recovery** - When features fail, no guidance or alternatives offered.

---

## Performance Metrics

**Load Times:**
- Landing page: ~1-2 seconds (acceptable)
- Search response: <2 seconds (good)
- TL;DR summaries: ∞ (broken)
- Related Papers: ∞ (broken)
- Research Advisor: Immediate error (broken)

**Reliability:**
- Basic search: 100% (2/2 attempts)
- Advanced AI features: 0% (0/4 functional)
  - Research Advisor: Failed
  - TL;DR: Failed
  - Learning Path: Failed (worse—returns wrong results)
  - Related Papers: Failed

**Overall Uptime of Advertised Features: ~43% (3/7 major features functional)**

---

## Priority Improvements

Listed by Impact/Effort ratio for maximum value:

### Critical (Fix Immediately - Tool Unusable Without These)

| Priority | Issue | Impact | Effort | Recommendation |
|----------|-------|--------|--------|----------------|
| **P0** | Research Advisor errors out | Flagship feature broken | Medium | Debug API errors, add fallback, comprehensive error handling |
| **P0** | TL;DR infinite loading | Core value prop broken | Medium | Fix async loading, add timeout, show partial results |
| **P0** | Learning Path irrelevant results | Actively harmful | High | Retrain/fix semantic matching, validate output relevance |
| **P0** | Related Papers stuck loading | Blocks literature discovery | Medium | Fix similarity computation timeout, add loading progress |

### High (Functional but Broken)

| Priority | Issue | Impact | Effort | Recommendation |
|----------|-------|--------|--------|----------------|
| **P1** | "Has Code" filter doesn't work | Critical for reproducibility research | Low | Fix filter logic, add GitHub indicators to UI |
| **P1** | No error recovery guidance | Users stuck when features fail | Low | Add helpful error messages, suggest alternatives |

### Medium (Enhancements)

| Priority | Issue | Impact | Effort | Recommendation |
|----------|-------|--------|--------|----------------|
| **P2** | No value prop clarity on landing | Users don't understand differentiation | Low | Add "Why AI Paper Atlas?" section, example queries |
| **P2** | Unclear AI-matched vs Keyword | Confusing categorization | Low | Add explanatory tooltips, document methodology |

### Low (Nice to Have)

| Priority | Issue | Impact | Effort | Recommendation |
|----------|-------|--------|--------|----------------|
| **P3** | Technique definitions missing | Useful for students | Medium | Add hover tooltips with technique descriptions |
| **P3** | No trending topics view | Minor enhancement | Medium | Aggregate rising papers into topic clusters |

---

## Screenshots Index

1. `01-landing-first-impression.png` - Landing page, 138k papers indexed
2. `02a-discovery-page.png` - Discovery navigation tabs
3. `02b-tldr-loading.png` - TL;DR infinite loading (broken)
4. `03-search-results.png` - Search for "efficient language models" (31 results)
5. `03b-advisor-panel-open.png` - Research Advisor modal (before error)
6. `03c-advisor-query-sent.png` - Research Advisor error message
7. `04-paper-detail-expanded.png` - Paper detail with Summary/Related/Benchmarks tabs
8. `05-code-filter-applied.png` - "Has Code" filter applied (no effect)
9. `06-learning-path.png` - Learning Path with irrelevant papers (broken)
10. `07-tldr-still-loading.png` - TL;DR still loading after 60+ seconds
11. `08-techniques-loading.png` - Techniques explorer (functional)
12. `09-rising-loading.png` - Rising papers with citation velocity (functional)
13. `10-related-papers.png` - Related Papers infinite loading (broken)
14. `11-second-search.png` - Second search "neural architecture search" (30 results)
15. `12-final-state.png` - Final state at exit

---

## Final Verdict

**Overall Score: 2/5**

**Recommendation:** Do not use in current state. Fix critical bugs (P0) before launching to faculty/researchers.

**Would I use this for my graduate seminar preparation?** No. The broken AI features mean I can't trust the tool for high-stakes academic work. Basic search works, but arXiv + Google Scholar are more reliable. The two functional features (Techniques explorer, Rising papers) don't compensate for four major failures.

**Path to Adoption:**
Fix the P0 bugs (Research Advisor, TL;DR, Learning Path, Related Papers), and I would reconsider. The underlying ideas are sound—AI-powered literature discovery, technique-based search, citation velocity—but execution fails at critical points. In academia, reliability matters more than features. A tool that works 43% of the time is worse than no tool at all.

---

**Assessment Completed:** 2025-12-19
**Total Time:** 25 minutes
**Persona:** Prof. James Williams, MIT CSAIL
