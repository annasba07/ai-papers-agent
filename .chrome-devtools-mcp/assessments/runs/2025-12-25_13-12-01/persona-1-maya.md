# UX Assessment Report: Dr. Maya Chen
**AI Paper Atlas - Research Intelligence Platform**
**Assessment Date:** December 25, 2025
**Session Duration:** ~15 minutes
**Persona:** Dr. Maya Chen, CMU Postdoc, Efficient Transformers Research

---

## Executive Summary

**CRITICAL FAILURE: System completely non-functional.** The platform returned zero results for all searches, hung indefinitely on all discovery features, and provided no access to the claimed 138,986 papers. As a time-pressured researcher with 20 minutes before my next meeting, this tool wasted 100% of my available time and delivered 0% value. I would not return, would not recommend, and am deeply frustrated by the gap between promising UI and broken functionality.

**Verdict:** 1/5 - Unusable in current state

---

## Session Timeline & Metrics

### Timeline Summary
- **00:00** - Landing page loaded (redirected to /explore)
- **01:30** - Explored Discovery navigation tabs
- **03:00** - Attempted search: "efficient attention mechanisms"
- **03:10** - Search returned 0 results in 10,004ms ❌
- **04:00** - Opened Research Advisor panel
- **04:30** - Submitted advisor query with detailed research problem
- **04:43** - Advisor failed with error after 13+ seconds ❌
- **06:00** - Applied "Has Code" filter - still 0 results ❌
- **07:30** - Navigated to Discovery/TL;DR tab
- **07:32** - TL;DR stuck on "Loading summaries..." ❌
- **09:00** - Tried Techniques tab
- **09:03** - Techniques stuck on "Loading techniques..." ❌
- **10:30** - Tried Rising Papers tab
- **10:33** - Rising stuck on "Finding rising papers..." ❌
- **15:00** - Gave up, wrote this report

### Performance Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Search response time | 10,004ms | 🔴 Unacceptable (target: <3s) |
| Search results returned | 0 papers | 🔴 Critical failure |
| Advisor response time | 13,000ms+ | 🔴 Failed with error |
| TL;DR load time | ∞ (never loaded) | 🔴 Critical failure |
| Techniques load time | ∞ (never loaded) | 🔴 Critical failure |
| Rising papers load time | ∞ (never loaded) | 🔴 Critical failure |
| Papers indexed (displayed) | 0 | 🔴 System error |
| Successful interactions | 0% | 🔴 Complete failure |

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)
**Screenshot:** `01-landing-first-impression.png`
**Timestamp:** 00:00
**Emotional State:** 3/5 (Cautious)

**Observations:**
- Redirected to `/explore` instead of dedicated landing page
- Clean, modern interface with prominent search box - good first impression
- Showed "138,986 papers" in sidebar - seemed promising
- DEFAULT showed Computer Vision papers (not my area) - irrelevant
- No immediate clarity on what makes this different from arXiv or Semantic Scholar

**First Thoughts as Maya:**
"Okay, looks professional. Search box is prominent. But why am I seeing random CV papers when I just arrived? I need to search for my topic immediately."

---

### Step 2: Initial Exploration (Navigation Discovery)
**Screenshots:** `02a-nav-discovery.png`, `02b-nav-reproducible.png`
**Timestamp:** 01:30
**Emotional State:** 3/5 (Neutral, exploring)

**Observations:**
- Clicked "Discovery" nav - found multiple tabs (Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path)
- **Positive:** "Reproducible" tab with code filtering is EXACTLY what I need
- Discovery page showed stats: 138,986 papers, 26,666 papers indexed, 6,105 with code
- Loading state appeared briefly
- Reproducible tab showed category filters (cs.CV, cs.LG, etc.) - good granularity

**First Thoughts as Maya:**
"This is promising! A dedicated 'Reproducible' section addresses my #1 pain point. Let me go search for my specific topic now."

---

### Step 3: Task-Based Search - Finding Efficient Attention Papers
**Screenshot:** `03-search-zero-results.png`
**Timestamp:** 03:00 - 03:10
**Emotional State:** 1/5 (Frustrated)

**Query:** "efficient attention mechanisms"
**Results:** **0 papers in 10,004ms**

**CRITICAL FAILURE:**
- Searched for a common, well-researched topic in my exact field
- System took 10+ seconds and returned ZERO results
- Error message: "No papers found - Try different keywords or describe your research goal in more detail"
- Sidebar showed "0 papers" - contradicting the earlier "138,986 papers indexed"

**First Thoughts as Maya:**
"What?! This is a fundamental topic with hundreds of papers. Flash Attention, Linear Attention, Sparse Transformers - there should be DOZENS of results. Is the database broken? I've already wasted 3 minutes of my 20-minute window."

**Pain Point Addressed:** ❌ FAILED - Information Overload → Zero Information
- Expected: Filtered, relevant papers on efficient attention
- Got: Complete absence of any papers

---

### Step 3.5: Research Advisor (AI-Powered Search)
**Screenshots:** `04-advisor-opened.png`, `05-advisor-searching.png`
**Timestamp:** 04:00 - 04:43
**Emotional State:** 1/5 (Very frustrated)

**Query:** "I need papers on efficient attention mechanisms for mobile deployment with working code implementations"

**Observations:**
- Clicked "Ask Advisor" button - panel opened quickly (good UX)
- Interface looked polished with example prompts
- Submitted detailed, natural language query describing my exact research need
- Advisor showed "Searching papers..." status
- After 13+ seconds: **"Sorry, I encountered an error while searching. Please try again."**

**CRITICAL FAILURE #2:**
- The AI advisor, supposed to be smarter than keyword search, completely failed
- No partial results, no suggestions, no fallback
- Error message was generic with no troubleshooting guidance

**First Thoughts as Maya:**
"Both search methods are broken. I've now wasted 5 minutes and found ZERO papers. The basic search failed, the AI search failed. Why would I use this over just going to arXiv? At least arXiv has papers."

**Pain Point Addressed:** ❌ FAILED - Connection Blindness → Complete Blindness
- Expected: Semantic understanding to find related work under different terminology
- Got: Error message and wasted time

---

### Step 4: Deep Dive - Paper Analysis
**Status:** SKIPPED - No papers available to examine
**Emotional State:** N/A

Could not test paper detail views, AI analysis, or relationship graphs because zero papers were accessible.

---

### Step 5: Code Availability Check
**Screenshot:** `06-has-code-filter-applied.png`
**Timestamp:** 06:00
**Emotional State:** 1/5 (Desperate)

**Observations:**
- Clicked "Has Code" filter in sidebar
- Filter badge appeared showing it was active
- Still showed "0 results"
- System appeared to re-search with old query ("efficient attention mechanisms")
- "AI-powered semantic search in progress..." message appeared but never completed

**CRITICAL FAILURE #3:**
- Even the basic filtering mechanism is broken
- Cannot browse papers with code (my most critical need)
- The Reproducible tab that initially looked promising is completely inaccessible

**First Thoughts as Maya:**
"This addresses my #1 pain point - reproducibility frustration - but it doesn't work AT ALL. I can't even browse what papers have code. This is worse than useless."

**Pain Point Addressed:** ❌ FAILED - Reproducibility Frustration → Amplified Frustration
- Expected: Quick filter to papers with working implementations
- Got: Broken filter returning zero results

---

### Step 6: Learning Path Assessment
**Status:** SKIPPED - Feature inaccessible due to system failure
**Emotional State:** N/A

---

### Step 7: TL;DR / Quick Scan Mode
**Screenshot:** `07-tldr-page.png`
**Timestamp:** 07:30 - 09:00
**Emotional State:** 1/5 (Giving up hope)

**Observations:**
- Navigated to `/discovery/tldr`
- Page showed "Quick summaries for fast scanning" description
- Status: **"Loading summaries..." - NEVER COMPLETED**
- Waited 90+ seconds - infinite loading state
- No timeout, no error, no papers

**CRITICAL FAILURE #4:**
- Promised feature completely non-functional
- No feedback on why it's not working
- Wastes user time with false promise of content

**First Thoughts as Maya:**
"I have 10 minutes left before my meeting. This tool has shown me NOTHING. Every feature I try just hangs forever. I should have just gone to arXiv."

**Pain Point Addressed:** ❌ FAILED - Time Poverty → Time Wasted
- Expected: Quick scan of recent papers in 30 seconds each
- Got: Infinite loading, zero papers, wasted 90+ seconds

---

### Step 8: Technique Explorer
**Screenshot:** `08-techniques-loading.png`
**Timestamp:** 09:00 - 09:30
**Emotional State:** 1/5 (Resigned)

**Observations:**
- Clicked "Techniques" tab
- Page showed "Browse by methodology type" with "Novelty: All" filter
- Status: **"Loading techniques..." - NEVER COMPLETED**
- Another infinite loading state
- No content ever appeared

**CRITICAL FAILURE #5:**
- Yet another core feature completely broken
- Would have been useful to browse by methodology (e.g., "sparse attention", "linear complexity")
- Instead: nothing

**Pain Point Addressed:** ❌ FAILED - Connection Blindness → Total Darkness
- Expected: Discover papers organized by technique taxonomy
- Got: Eternal loading spinner

---

### Step 9: Rising Papers / Hot Topics
**Screenshot:** `09-rising-loading.png`
**Timestamp:** 10:30 - 11:00
**Emotional State:** 1/5 (Completely frustrated)

**Observations:**
- Clicked "Rising" tab
- Description: "Papers gaining citation momentum"
- Status: **"Finding rising papers..." - NEVER COMPLETED**
- Third consecutive infinite loading state
- Pattern is clear: backend is completely broken

**CRITICAL FAILURE #6:**
- Addresses my "Trend Anxiety" pain point in theory
- In practice: completely non-functional
- No papers, no trends, no value

**First Thoughts as Maya:**
"Every. Single. Feature. Is. Broken. I have 5 minutes left and I've found ZERO papers. This is the worst research tool I've ever tried."

**Pain Point Addressed:** ❌ FAILED - Trend Anxiety → Panic
- Expected: Early detection of important emerging work
- Got: No detection of anything

---

### Step 10: Paper Relationships / Similarity Graph
**Status:** SKIPPED - No papers available to examine relationships
**Emotional State:** N/A

---

### Step 11: Second Search (Consistency Check)
**Status:** SKIPPED - First search never worked, no point testing consistency
**Emotional State:** N/A

---

### Step 12: Exit Reflection
**Screenshot:** `10-final-state.png`
**Timestamp:** 15:00
**Emotional State:** 1/5 (Deeply frustrated and disappointed)

**Final State:**
- Back on Explore page
- Search still showing "0 results 10004ms"
- Sidebar still showing "0 papers"
- No data loaded throughout entire session

**Overall Experience:**
This is one of the most frustrating research tools I've encountered. The UI is polished and promises exactly what I need - code-focused search, AI recommendations, trend detection - but delivers absolutely nothing. Every feature is broken. I wasted my entire 20-minute window and found zero papers.

---

## Pain Point Assessment

### Did AI Paper Atlas solve Dr. Maya Chen's pain points?

| Pain Point | Addressed? | Details |
|-----------|-----------|---------|
| **1. Information Overload** | ❌ NO | Zero papers shown. Can't filter the firehose because there's no firehose - the system is empty/broken. |
| **2. Time Poverty** | ❌ WORSE | Wasted 100% of my 20-minute window with infinite loading states and failed searches. Would have been faster to manually browse arXiv. |
| **3. Reproducibility Frustration** | ❌ NO | "Has Code" filter exists but returns 0 results. Reproducible tab never loads. Cannot identify papers with implementations. |
| **4. Connection Blindness** | ❌ NO | No papers means no connections. Research Advisor failed. Techniques taxonomy never loaded. |
| **5. Trend Anxiety** | ❌ NO | Rising Papers tab infinite load. Hot Topics unavailable. Cannot detect emerging work. |

**Summary:** 0 out of 5 pain points addressed. The tool made every problem worse by wasting time.

---

## Delights

**None.**

The only positive moment was the initial UI impression before I realized nothing works.

---

## Frustrations (Ranked by Severity)

### 🔴 CRITICAL (Session-Ending Issues)

1. **Zero Papers Accessible (10/10 severity)**
   - System claims 138,986 papers but displays 0
   - Database appears completely empty or disconnected
   - Makes entire tool useless

2. **Search Completely Broken (10/10 severity)**
   - Both keyword search and AI advisor fail
   - 10+ second latency followed by zero results
   - No fallback or suggestions

3. **Infinite Loading States (9/10 severity)**
   - TL;DR, Techniques, Rising tabs never load
   - No timeout, no error messages
   - Wastes user time with false promise

4. **Research Advisor Error (8/10 severity)**
   - Flagship AI feature completely fails
   - Generic error message with no guidance
   - Destroys trust in the platform

### 🟡 HIGH (Usability Problems)

5. **No Error Recovery (7/10 severity)**
   - System never explains WHY it's broken
   - No troubleshooting steps
   - No "try again" functionality that works

6. **Misleading Paper Count (7/10 severity)**
   - Sidebar shows "138,986 papers" but displays 0
   - Sets false expectations
   - Suggests system is broken, not just empty

7. **No Offline/Degraded Mode (6/10 severity)**
   - When backend fails, entire UI becomes useless
   - Should show cached data or at least explain status

---

## Priority Improvements

### P0 - CRITICAL (Must Fix Before Any User Testing)

| Issue | Impact | Effort | Recommendation |
|-------|--------|--------|----------------|
| **Fix database connection** | 🔴 Critical | High | Database appears disconnected. Fix backend API/connection. BLOCKER for all functionality. |
| **Fix search functionality** | 🔴 Critical | High | Keyword and semantic search both broken. Check vector DB, indexing pipeline. BLOCKER. |
| **Fix infinite loading states** | 🔴 Critical | Medium | Add timeouts (30s max), error boundaries, fallback UI. Currently wastes user time. |
| **Add error diagnostics** | 🔴 Critical | Low | Show actual error messages (API down, DB empty, etc.) instead of generic loading. |

### P1 - HIGH (Fix Before Public Launch)

| Issue | Impact | Effort | Recommendation |
|-------|--------|--------|----------------|
| **Research Advisor reliability** | 🟡 High | High | Fix error handling, add retry logic, show partial results on failure. |
| **Has Code filter** | 🟡 High | Medium | Ensure filter works when DB is populated. Critical differentiator. |
| **Discovery tab loading** | 🟡 High | Medium | Fix TL;DR, Techniques, Rising tabs. Core value props currently inaccessible. |
| **System health indicator** | 🟡 High | Low | Show status: "X papers indexed, last updated Y ago" to diagnose issues. |

### P2 - MEDIUM (Post-Launch Improvements)

| Issue | Impact | Effort | Recommendation |
|-------|--------|--------|----------------|
| **Search latency** | 🟢 Medium | Medium | 10s for 0 results is unacceptable even if it worked. Target: <3s. |
| **Default landing experience** | 🟢 Medium | Low | Don't show random CV papers on first load. Show onboarding or ask for interests. |

---

## Screenshots Index

| # | Filename | Description | Emotion |
|---|----------|-------------|---------|
| 01 | `01-landing-first-impression.png` | Initial Explore page with CV papers, search box, filters | 3/5 Cautious |
| 02a | `02a-nav-discovery.png` | Discovery hub with multiple tabs, overview stats | 3/5 Neutral |
| 02b | `02b-nav-reproducible.png` | Reproducible tab with category filters, loading state | 4/5 Hopeful |
| 03 | `03-search-zero-results.png` | Search "efficient attention" returned 0 results in 10s | 1/5 Frustrated |
| 04 | `04-advisor-opened.png` | Research Advisor panel with example prompts | 3/5 Trying again |
| 05 | `05-advisor-searching.png` | Advisor error: "Sorry, I encountered an error while searching" | 1/5 Very frustrated |
| 06 | `06-has-code-filter-applied.png` | Has Code filter active, still 0 results, semantic search stuck | 1/5 Desperate |
| 07 | `07-tldr-page.png` | TL;DR tab infinite loading: "Loading summaries..." | 1/5 Giving up |
| 08 | `08-techniques-loading.png` | Techniques tab infinite loading: "Loading techniques..." | 1/5 Resigned |
| 09 | `09-rising-loading.png` | Rising tab infinite loading: "Finding rising papers..." | 1/5 Completely frustrated |
| 10 | `10-final-state.png` | Back to Explore, search still showing 0 results, system broken | 1/5 Done |

---

## Final Verdict

### Would I bookmark this tool?
**No.** It doesn't work.

### Would I return tomorrow?
**Absolutely not.** Zero value delivered, 100% time wasted.

### Would I recommend it to colleagues?
**Never.** It would damage my credibility to recommend a completely broken tool.

### What frustrated me most?
The gap between promise and reality. The UI looks professional and offers exactly what I need (code filtering, trend detection, AI recommendations), but nothing works. This is worse than a bad tool - it's a deceptive tool that wastes my extremely limited time.

### What would make me return?
1. **Proof that it works:** Show me it can return >0 papers for a common query
2. **Code filtering:** Demonstrate the "Has Code" filter actually works
3. **Speed:** <3s search response time
4. **Reliability:** No infinite loading states or AI errors

Until then, I'll stick with arXiv's email alerts and Papers with Code - they're not fancy, but they work.

---

## Recommendations for Team

### Immediate Actions (Before Next Test)
1. **Verify database connection** - System shows 0 papers despite claiming 138,986 indexed
2. **Test basic search** - "transformer", "attention", "CNN" should all return results
3. **Fix infinite loading** - Add 30s timeouts to ALL data fetching operations
4. **Add health check UI** - Show "DB status: Connected, Papers indexed: X, Last updated: Y"

### Architectural Concerns
The fact that EVERY feature failed suggests a systemic backend issue:
- Database connection severed?
- API gateway misconfigured?
- Vector index not built?
- Environment variables missing?

This isn't a UX problem - this is an infrastructure failure that makes UX assessment impossible.

### For Next UX Test
**Do NOT conduct user testing until basic functionality is verified.** This session wasted my time and yours. Fix the backend first, then test UX.

---

**Assessment completed at 15:00**
**Total papers found: 0**
**Total value delivered: 0**
**Time wasted: 100%**

**- Dr. Maya Chen**
