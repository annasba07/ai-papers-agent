# UX Assessment Report: AI Paper Atlas
**Persona:** Dr. Maya Chen - CMU Postdoc, Efficient Transformers Research
**Date:** 2025-12-23
**Session Duration:** 19:56:11 - 20:08:25 (~12 minutes)
**Assessment Status:** CRITICAL FAILURE - Core functionality broken

---

## Executive Summary

**Verdict: Would not return. Would not recommend.**

The tool completely failed to deliver its core value proposition. Despite multiple attempts across different search methods (keyword search, Research Advisor, filters), **every single query returned 0 results**. The "AI-powered semantic search" that took 10+ seconds consistently failed. Discovery features timed out. This is not a usability problem - it's a catastrophic technical failure that renders the entire product unusable.

---

## Session Timeline & Metrics

| Step | Time | Action | Result | Emotion (1-5) | Screenshot |
|------|------|--------|--------|---------------|------------|
| 0 | 19:56:11 | Environment setup | Viewport 1440x900 | 3 | - |
| 1 | 19:56:11 | Landing page load | Redirected to /explore, saw 30 papers (CV papers) | 3 | 01-landing-first-impression.png |
| 2 | 19:56:11 | Navigation discovery | Clicked Discovery tab, saw High Impact papers | 4 | 02a-nav-discovery.png, 02b-nav-generate.png |
| 3 | 19:56:11 | Search: "efficient attention mechanisms for mobile deployment" | **0 results in 10007ms** | 1 | 03a-search-query-entered.png, 03b-search-no-results.png |
| 3.5 | 19:59:33 | Research Advisor with same query | **ERROR after 30s timeout** | 1 | 03c-advisor-opened.png, 03d-advisor-query-entered.png, 03e-advisor-timeout.png |
| 5 | - | Applied "Has Code" filter | Still 0 results | 1 | 05-code-filter-applied.png |
| 5b | - | Tried "Reproducible" tab | Stuck on "Finding reproducible papers..." | 2 | 05b-reproducible-tab.png |
| 6 | 20:03:13 | Learning Path: "efficient attention" | **Timeout after 20s**, stuck on "Building your learning path..." | 1 | 06-learning-path.png, 06b-learning-path-timeout.png |
| 7 | - | TL;DR tab | Stuck on "Loading summaries..." indefinitely | 1 | 07-tldr-page.png, 07b-tldr-still-loading.png |
| 8 | - | Techniques tab navigation | **Navigation timeout** | 1 | 08-techniques-timeout.png |
| 11 | 20:07:55 | Second search: "transformers" | **0 results in 10003ms** | 1 | 11-back-to-explore.png, 11b-second-search-transformers.png |
| 12 | 20:08:25 | Exit reflection | Complete failure | 1 | 12-final-state.png |

**Total screenshots captured:** 15

---

## Detailed Step Analysis

### Step 1: First Impression - Confusing Start (Emotion: 3/5)

**What I saw:** Clean interface, but immediately landed on `/explore` showing 30 papers - all Computer Vision papers about generative video and diffusion models. Not what I expected on a "landing page."

**Visual observations (01-landing-first-impression.png):**
- Search box prominent with good placeholder: "Describe what you're researching..."
- "Ask Advisor" button in orange - stands out
- Left sidebar with filters (Has Code, High Impact, categories)
- Trending topics visible in sidebar
- Papers displayed with TL;DR summaries

**Confusion points:**
- Why am I seeing CV papers by default? No obvious reason.
- Is this the home page? Feels like I skipped something.
- "30 papers" - is that all that's in the system?

**Time to value:** Still looking for it.

---

### Step 2: Navigation Discovery - Some Promise (Emotion: 4/5)

**What I saw:** Clicked "Discovery" tab and found a well-organized hub with multiple tabs: Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path.

**Visual observations (02a-nav-discovery.png):**
- Clean tab navigation
- "Papers with Code" explicitly called out - exactly what I need!
- High Impact papers showing with Impact scores (10/10, 9/10)
- Quick Discovery cards with clear labels

**Positive:** Navigation structure makes sense. Having "Reproducible" as a top-level feature shows understanding of researcher needs.

**Concern:** Will these features actually work?

---

### Step 3: Search - CRITICAL FAILURE (Emotion: 1/5)

**Query:** "efficient attention mechanisms for mobile deployment"

**Expected:** Relevant papers on FlashAttention, linear attention, sparse transformers, mobile deployment techniques.

**Actual:** **0 results** after 10007ms (10+ seconds)

**Visual evidence (03b-search-no-results.png):**
- Large "No papers found" heading
- Suggestion: "Try different keywords or describe your research goal in more detail"
- Search took over 10 seconds to fail

**Critical issues:**
1. **Search doesn't work** - This is THE core feature. Complete failure.
2. **10+ second response time** - Unacceptable even if it worked
3. **No helpful error** - "Try different keywords" is not actionable when the problem is clearly technical
4. **No data?** - The sidebar shows "0 papers" but earlier showed "30 papers". Data loading issue?

**This is a showstopper.** My 20 minutes before the meeting just became wasted time.

---

### Step 3.5: Research Advisor - SECOND FAILURE (Emotion: 1/5)

**Attempt:** Clicked "Ask Advisor" button, entered detailed query: "I need papers on efficient attention mechanisms for mobile and edge device deployment, preferably with code implementations"

**Expected:** AI-powered recommendations, understanding of semantic intent, paper suggestions with rationale.

**Actual:** After 30+ seconds, received error: **"Sorry, I encountered an error while searching. Please try again."**

**Visual evidence (03e-advisor-timeout.png):**
- Generic error message
- No explanation of what went wrong
- Input field re-enabled but no point trying again

**Impact:** The "fallback" to basic search failure is also broken. Two strikes.

---

### Step 5: Code Availability Check - THIRD FAILURE (Emotion: 1/5)

**Attempt:** Applied "Has Code" filter to see if that would surface any results.

**Actual:** Filter badge appeared, but **still 0 results**.

**Visual evidence (05-code-filter-applied.png):**
- "Has Code" badge shows in active filters
- Search counter still shows "0 papers"
- Sidebar shows "0 papers indexed"

**Also tried:** "Reproducible" discovery tab - stuck on "Finding reproducible papers..." with no results.

**Critical insight:** The problem is not the search algorithm - **there appears to be no data loaded at all**. The sidebar consistently shows "0 papers indexed" once you interact with filters/search.

---

### Step 6: Learning Path - TIMEOUT (Emotion: 1/5)

**Attempt:** Navigate to "Learning Path" tab, enter "efficient attention" to generate a learning path.

**Actual:** Clicked "Generate Path" button, got "Building your learning path..." message, **timed out after 20+ seconds** with no result.

**Visual evidence (06b-learning-path-timeout.png):**
- Loading message persisted indefinitely
- No progress indicator
- No timeout handling
- Page became unresponsive

**Pattern emerging:** Not just search - ALL dynamic features are broken.

---

### Step 7: TL;DR Scan - STUCK LOADING (Emotion: 1/5)

**Attempt:** Navigate to "TL;DR" tab for quick paper scanning.

**Actual:** Page shows "Loading summaries..." indefinitely. Never loaded.

**Visual evidence (07b-tldr-still-loading.png):**
- Perpetual loading state
- No data appeared
- No error message
- No timeout

**This would be a key feature for my workflow** (scanning 50-100 papers quickly), but it's completely non-functional.

---

### Step 8: Techniques Explorer - NAVIGATION TIMEOUT (Emotion: 1/5)

**Attempt:** Navigate to "Techniques" tab to browse by technique name.

**Actual:** **Navigation timeout** - page failed to load entirely.

**Visual evidence (08-techniques-timeout.png):**
- Browser timeout during navigation
- Blank state
- Had to navigate back to Explore

**Every discovery feature is broken.**

---

### Step 11: Second Search - CONSISTENCY IN FAILURE (Emotion: 1/5)

**Attempt:** Tried simpler query "transformers" to rule out query complexity.

**Actual:** **0 results** in 10003ms.

**Visual evidence (11b-second-search-transformers.png):**
- Same "No papers found" message
- Same 10+ second delay
- Exactly the same failure mode

**Conclusion:** Search is systematically broken. Not a data relevance issue - it's a data availability issue.

---

## Pain Points Assessment: Did AI Paper Atlas Solve Them?

### 1. Information Overload ❌ MADE IT WORSE
- **Pain:** Drowning in daily arXiv flood, missing important papers
- **Expected:** AI-powered filtering, relevance ranking, personalized recommendations
- **Actual:** Can't find ANY papers. Literally worse than manually browsing arXiv.
- **Verdict:** Critical failure

### 2. Time Poverty ❌ WASTED MY TIME
- **Pain:** Only 20-30 minutes per day for paper discovery
- **Expected:** Fast, efficient search and triage
- **Actual:** Spent 12 minutes getting 0 results. Every query took 10+ seconds to fail.
- **Verdict:** Actively harmful to my workflow

### 3. Reproducibility Frustration ❌ CAN'T EVEN CHECK
- **Pain:** Papers without code waste hours of reimplementation time
- **Expected:** "Has Code" filter, GitHub links, Papers with Code integration
- **Actual:** Filter exists but returns 0 results. Can't evaluate the feature.
- **Verdict:** Unknown - feature unusable

### 4. Connection Blindness ❌ NO DATA TO CONNECT
- **Pain:** Hard to see paper relationships across subfields
- **Expected:** Related papers, citation networks, technique connections
- **Actual:** Can't examine any paper relationships because can't load any papers.
- **Verdict:** Unable to test

### 5. Trend Anxiety ❌ NO TRENDS VISIBLE
- **Pain:** Missing "next big thing" in efficient ML
- **Expected:** "Rising" papers, "Hot Topics", trend indicators
- **Actual:** "No trending data available" in all trending sections
- **Verdict:** Feature exists but completely empty

---

## Delights & Frustrations

### Delights: NONE
I wanted to be delighted. The UI looked promising. The feature set addresses real pain points. But **I never got past the front door**. Can't be delighted by features that don't work.

### Frustrations: EVERYTHING

1. **Search returns 0 results on every query**
   - Impact: 10/10 - This is the core feature
   - "efficient attention mechanisms for mobile deployment" → 0 results
   - "transformers" → 0 results
   - This is not a relevance problem - it's a data loading problem

2. **Research Advisor errors immediately**
   - Impact: 9/10 - Marketed as key differentiator
   - Timeout after 30 seconds
   - Generic error message with no troubleshooting help

3. **Discovery features stuck in perpetual loading**
   - Impact: 8/10 - TL;DR, Learning Path, Techniques all broken
   - No timeout handling
   - No error states
   - Page becomes unresponsive

4. **Every interaction takes 10+ seconds**
   - Impact: 7/10 - Even failures are slow
   - Makes debugging painful
   - Feels like backend is down or severely misconfigured

5. **Data inconsistency: "30 papers" → "0 papers"**
   - Impact: 6/10 - Suggests database/indexing issue
   - Landing showed 30 papers
   - After any filter/search: 0 papers
   - Trending topics sidebar: "0 papers indexed"

6. **No helpful error messages**
   - Impact: 5/10 - Can't self-troubleshoot
   - "Try different keywords" when problem is clearly technical
   - No indication of what's broken (API down? DB empty? Auth issue?)

---

## Performance Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Search response time | <3s | 10+ seconds | ❌ FAIL |
| Page load time | <2s | Variable, many timeouts | ❌ FAIL |
| Feature availability | 100% | 0% (all features broken) | ❌ FAIL |
| Error recovery | Graceful | Generic errors, no recovery | ❌ FAIL |
| Data consistency | Stable | Inconsistent (30 → 0 papers) | ❌ FAIL |

---

## Priority Improvements

### P0: CRITICAL - FIX DATA LOADING (Impact: 10, Effort: ?)
**Problem:** No papers returned by any search, all features showing "0 papers indexed"
**Evidence:** Screenshots 03b, 05, 11b
**Why P0:** Product is completely unusable without data
**Fix:**
- Check if database is populated
- Verify search indexing is running
- Check API connectivity between frontend and backend
- Add health check endpoint to expose system status

### P0: CRITICAL - FIX RESEARCH ADVISOR (Impact: 9, Effort: ?)
**Problem:** Advisor errors after 30s timeout on every query
**Evidence:** Screenshot 03e
**Why P0:** This is the marketed differentiator vs Papers with Code
**Fix:**
- Debug why advisor API is timing out
- Add proper error handling with actionable messages
- Set reasonable timeout (5-10s max)
- Show progress indicator during processing

### P0: CRITICAL - FIX DISCOVERY FEATURE LOADING (Impact: 8, Effort: ?)
**Problem:** TL;DR, Learning Path, Techniques all timeout or stuck loading
**Evidence:** Screenshots 06b, 07b, 08
**Why P0:** These are core value propositions
**Fix:**
- Implement timeout handling (10s max)
- Show skeleton loaders during load
- Handle empty states gracefully
- Add error states with retry buttons

### P1: HIGH - PERFORMANCE OPTIMIZATION (Impact: 7, Effort: Medium)
**Problem:** Every operation takes 10+ seconds, even to return 0 results
**Evidence:** All search screenshots show 10000+ ms
**Why P1:** Speed is critical for researchers with time poverty
**Fix:**
- Add caching layer
- Optimize database queries
- Implement search result streaming
- Target <3s for initial results

### P1: HIGH - BETTER ERROR MESSAGES (Impact: 6, Effort: Low)
**Problem:** Generic "try different keywords" when problem is clearly technical
**Evidence:** Screenshots 03b, 03e
**Why P1:** Helps users AND developers debug issues
**Fix:**
- Differentiate between "no matches" vs "system error"
- Add status page link in error states
- Show specific error codes for debugging
- Provide actionable troubleshooting steps

### P2: MEDIUM - DATA CONSISTENCY (Impact: 6, Effort: ?)
**Problem:** Landing shows "30 papers", then drops to "0 papers" after interaction
**Evidence:** Screenshots 01 vs 03b
**Why P2:** Indicates underlying data integrity issue
**Fix:**
- Debug why initial load shows data but subsequent queries don't
- Ensure consistent data source across all views
- Add data validation/monitoring

---

## Screenshots Index

1. **01-landing-first-impression.png** - Initial page load, shows 30 CV papers
2. **02a-nav-discovery.png** - Discovery hub with tab navigation
3. **02b-nav-generate.png** - Generate tab view
4. **03a-search-query-entered.png** - Search box with query entered
5. **03b-search-no-results.png** - Search failure: 0 results in 10007ms
6. **03c-advisor-opened.png** - Research Advisor panel opened
7. **03d-advisor-query-entered.png** - Advisor query entered, "Searching papers..."
8. **03e-advisor-timeout.png** - Advisor error after 30s timeout
9. **05-code-filter-applied.png** - "Has Code" filter applied, still 0 results
10. **05b-reproducible-tab.png** - Reproducible tab stuck loading
11. **06-learning-path.png** - Learning Path input form
12. **06b-learning-path-timeout.png** - Learning Path timeout after 20s
13. **07-tldr-page.png** - TL;DR tab initial load
14. **07b-tldr-still-loading.png** - TL;DR stuck on "Loading summaries..."
15. **08-techniques-timeout.png** - Techniques navigation timeout
16. **11-back-to-explore.png** - Return to explore page
17. **11b-second-search-transformers.png** - Second search also failed
18. **12-final-state.png** - Final state, still showing 0 results

---

## Final Verdict

### Would I bookmark this tool? ❌ NO
There's nothing to bookmark. It doesn't work.

### Would I return tomorrow? ❌ NO
Not until I see evidence that core search functionality is operational. I'd check a status page or changelog first.

### Would I recommend to colleagues? ❌ ABSOLUTELY NOT
Would actively warn them away. Recommending a broken tool damages my credibility.

### What frustrated me most?
**The complete failure to deliver basic functionality.** This isn't about missing features or poor UX - the product literally doesn't work. Search returns nothing, AI advisor errors, discovery features timeout. It feels like I'm testing a broken staging environment, not a production tool.

### What would delight me?
At this point, **just working search** would be delightful. I came in skeptical but hopeful. The feature set looks great on paper. The UI is clean. But none of that matters if I can't find a single paper.

### Time to value achieved: NEVER
I invested 12 minutes and got zero value. Worse than zero - I wasted time I could have spent actually finding papers on arXiv.

---

## Researcher Perspective: The Bigger Picture

As a postdoc with limited time and high research pressure, **tool adoption is a calculated risk**. I need to see ROI quickly or I abandon the tool. AI Paper Atlas had ~3 minutes to prove value before my skepticism would win.

**Timeline of trust:**
- 0:00 - Cautiously optimistic (clean UI, good features)
- 1:00 - First search failure → concerned
- 2:00 - Advisor timeout → skeptical
- 5:00 - Everything timing out → convinced it's broken
- 12:00 - Done. Will not return.

**The opportunity cost:** In the 12 minutes I spent on AI Paper Atlas, I could have:
- Scanned 20-30 arXiv abstracts manually
- Found 2-3 relevant papers
- Checked if they have code on GitHub
- Made progress on my actual research

**The trust damage:** I'm now *less* likely to try similar tools in the future. This experience reinforced my prior that "AI-powered research tools" are overhyped and underdelivered.

---

## System Health Concerns

Based on observed behavior, I suspect:

1. **Database is empty or not connected** - Explains "0 papers indexed"
2. **Search API is misconfigured or down** - Explains timeouts and 0 results
3. **Backend services not running** - Explains universal failures across features
4. **No health checks or monitoring** - Explains lack of user-facing status info

**Recommendation:** Before any UX improvements, ensure the system is actually operational. Add health check endpoints, monitoring, and a status page.

---

## Conclusion

**AI Paper Atlas is not ready for users.** The technical infrastructure appears fundamentally broken. Every core feature failed during this assessment. As a researcher who desperately needs tools like this, I'm disappointed but not surprised - this matches my prior experience with academic software launches.

**What would make me reconsider:**
1. Evidence that search actually works (demo video with real queries)
2. Explanation of what broke and how it was fixed
3. Status page showing system health
4. Beta tester testimonials from real researchers

**Until then:** I'll stick with my current workflow (arXiv + Papers with Code + Google Scholar), even though it's painful. At least those tools work.

---

**Assessment completed:** 2025-12-23 20:08:25
**Total time invested:** 12 minutes, 14 seconds
**Value received:** None
**Likelihood to return:** 0%
