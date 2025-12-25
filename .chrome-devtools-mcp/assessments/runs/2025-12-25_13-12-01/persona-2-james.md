# UX Assessment Report: Prof. James Williams
**Date:** December 25, 2025
**Duration:** ~15 minutes
**Persona:** Senior MIT Faculty, NLP Research
**Task:** Prepare graduate seminar reading list on efficient language models

---

## Executive Summary

**Verdict: Cannot recommend.** The system is fundamentally broken. Search returned zero results for "efficient language models" - a core NLP topic with thousands of papers. The Research Advisor timed out after 10+ seconds. Every Discovery tab (High Impact, TL;DR, Reproducible, Rising, Techniques, Learning Path) failed to load, hanging indefinitely. This is not a tool I can use, let alone recommend to students.

**Emotional Journey:** 3/5 → 1/5 (rapid deterioration as each feature failed)

---

## Session Timeline

| Time | Step | Action | Result | Emotion |
|------|------|--------|--------|---------|
| 0:00 | 1 | Landing | Redirected to Explore page, professional UI, filters visible | 3/5 |
| 0:30 | 2 | Navigation | Discovery, Generate tabs discovered | 4/5 |
| 2:00 | 3 | Search "efficient language models" | **0 results** for major NLP topic | 1/5 |
| 3:00 | 3.5 | Research Advisor query | Timed out after 10s, then error | 2/5 |
| 4:00 | 4 | Discovery/High Impact | Loading indefinitely, no content | 1/5 |
| 5:00 | 5 | Discovery/Reproducible | Loading indefinitely | 1/5 |
| 6:00 | 6 | Discovery/Learning Path | "Building..." without input submitted | 1/5 |
| 7:00 | 7-9 | TL;DR, Techniques, Rising | All loading indefinitely | 1/5 |
| 8:00 | 10 | Return to Explore | Still searching for original query | 1/5 |
| 9:00 | 12 | Exit | Complete system failure | 1/5 |

---

## Detailed Step Analysis

### Step 1: First Impression ✓
**Screenshot:** `01-landing-first-impression.png`

Landed directly on `/explore` (not a traditional landing page). Professional design, clear filter sidebar, 138,986 papers indexed. "Ask Advisor" button prominent. Initial impression: competent tool.

**Observations:**
- Clean, academic aesthetic
- Filters well-organized (Quick Filters, Category, Difficulty, Time Range)
- "Seminal Papers" filter visible - exactly what I need for teaching
- No obvious value proposition statement

**Emotion:** 3/5 (neutral-positive, cautiously optimistic)

---

### Step 2: Navigation Discovery ✓
**Screenshots:** `02a-nav-discovery.png`, `02b-nav-generate.png`

Explored Discovery and Generate sections. Discovery hub showed metrics (138,986 total, 26,666 deep-analyzed, 6,105 with code). Generate page promised code generation from papers - intriguing for reproducibility.

**Observations:**
- Navigation clear: Explore, Discovery, Reading List, Generate
- Discovery tabs: Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path
- Promising features for faculty (High Impact = seminal work, Learning Path = student progression)

**Emotion:** 4/5 (interested, features align with faculty needs)

---

### Step 3: Task-Based Search ✗ **CRITICAL FAILURE**
**Screenshots:** `03-search-results.png`, `03b-search-loading.png`

Searched for "efficient language models" - a foundational NLP topic. System showed "Smart Results AI-POWERED" indicator, then returned **0 results** after 10+ seconds.

**Observations:**
- Query: "efficient language models"
- Expected: Hundreds of papers (BERT distillation, DistilBERT, MobileBERT, efficient transformers, etc.)
- Actual: "No papers found" with suggestion to "Try different keywords"
- This is a **core failure** - the topic has enormous literature

**This alone disqualifies the tool for academic use.**

**Emotion:** 1/5 (frustrated, questioning database completeness)

---

### Step 3.5: Research Advisor ✗ **TIMEOUT + ERROR**
**Screenshots:** `03c-advisor-panel.png`, `03d-advisor-searching.png`, `03e-advisor-timeout.png`

Clicked "Ask Advisor" as fallback. Entered detailed query: "I need to find papers on efficient transformers and model compression for my graduate seminar on efficient language models. Looking for both foundational work and recent advances."

**Observations:**
- Advisor panel opened with example queries
- Submitted query → "Searching papers..." state
- Waited 10+ seconds → still searching
- Final state: "Sorry, I encountered an error while searching. Please try again."
- **Both primary search mechanisms failed**

**Emotion:** 2/5 (deeply concerned, time pressure mounting)

---

### Step 4: Paper Detail Analysis ✗ **LOADING TIMEOUT**
**Screenshot:** `04-high-impact-loading.png`, `04b-high-impact-timeout.png`

Attempted to browse High Impact papers (seminal works for student reading). Tab loaded indefinitely without content.

**Observations:**
- Clicked "High Impact" tab in Discovery
- "Loading high impact papers..." message
- Waited 5+ seconds → no content appeared
- This should be pre-computed data (top papers by citations)

**Cannot evaluate paper detail views because no papers loaded.**

**Emotion:** 1/5 (system reliability crisis evident)

---

### Step 5: Code Availability ✗ **LOADING TIMEOUT**
**Screenshot:** `05-reproducible-loading.png`

Tried Reproducible tab (papers with code) - critical for setting lab standards.

**Observations:**
- "Finding reproducible papers..." - never completed
- This feature directly addresses my Pain Point #3 (reproducibility standards)
- **Feature exists but is non-functional**

**Emotion:** 1/5 (key faculty need unmet)

---

### Step 6: Learning Path ✗ **BROKEN UI STATE**
**Screenshot:** `06-learning-path.png`

Learning Path tab showed "Building your learning path..." **before** I entered any topic. Broken state management.

**Observations:**
- Tab has input field: "Enter a topic (e.g., transformers, diffusion models)..."
- System displayed "Building your learning path..." without user action
- This would be valuable for Pain Point #2 (student guidance) if it worked

**Emotion:** 1/5 (UI consistency failures)

---

### Step 7-9: TL;DR, Techniques, Rising ✗ **ALL FAILED**
**Screenshots:** `07-tldr-loading.png`, `08-techniques-loading.png`, `09-rising-loading.png`

Rapidly tested remaining Discovery tabs. **All failed to load.**

**Observations:**
- TL;DR: "Loading summaries..." (indefinite)
- Techniques: "Loading techniques..." (indefinite)
- Rising: "Finding rising papers..." (indefinite)
- **7/8 Discovery features are non-functional** (only Overview showed metrics)

**This is a systemic backend failure, not isolated bugs.**

**Emotion:** 1/5 (complete loss of confidence)

---

### Step 10-11: Return to Explore ✗ **STILL BROKEN**
**Screenshot:** `10-explore-timeout.png`

Returned to Explore page. Original search for "efficient language models" still showed "AI-powered semantic search in progress" - **the query never completed.**

**Observations:**
- Backend appears hung on the original query
- Page navigation timing out (10s timeout exceeded)
- System in unrecoverable state

**Emotion:** 1/5 (unusable)

---

### Step 12: Exit Reflection
**Screenshot:** `12-final-state.png`

Final state: Explore page showing search in progress, no papers loaded anywhere in the system.

**Would I use this tomorrow?** No.
**Would I recommend to students?** Absolutely not - I'd be wasting their time.
**Would I recommend to colleagues?** No - would damage my credibility.

**Emotion:** 1/5 (disappointed, frustrated, time wasted)

---

## Pain Point Assessment

### 1. Curation Burden (Reading List Maintenance)
**Status:** ❌ **NOT SOLVED**
**Why:** Cannot find papers on basic topics. High Impact tab doesn't load. No reading list generated.

### 2. Student Guidance
**Status:** ❌ **NOT SOLVED**
**Why:** Learning Path feature broken. Cannot identify foundational vs. advanced papers. Search failure means I have nothing to recommend.

### 3. Reproducibility Standards
**Status:** ❌ **NOT SOLVED**
**Why:** Reproducible tab infinite loading. Code availability filters exist but results don't load. Generate feature untested due to search failures.

### 4. Field Breadth (Multimodal/Cross-domain)
**Status:** ❓ **UNTESTABLE**
**Why:** Cannot search NLP papers, let alone explore cross-domain connections.

### 5. Historical Context (Foundational Work)
**Status:** ❌ **NOT SOLVED**
**Why:** "Seminal Papers" filter exists but produces no results when combined with any search.

---

## Teaching Utility Assessment

**Can I use this for my seminar?** No.

**Specific failures for teaching:**
1. **Cannot identify seminal papers** - High Impact, Seminal Papers filter both failed
2. **Cannot create progression** - Learning Path broken, cannot order beginner → expert
3. **Cannot verify reproducibility** - Reproducible tab doesn't load
4. **Cannot find domain papers** - Search returns 0 results for core topics
5. **No export/share** - Even if it worked, unclear how to share reading lists with students

**What I need vs. what I got:**
- Need: 10-15 papers from foundational (Attention Is All You Need) to recent (efficient transformers)
- Got: Zero papers, infinite loading states, error messages

---

## Student Recommendation Potential

**Would I recommend this to PhD students?** No.

**Reasoning:**
- Students will waste time on a broken tool
- Teaches bad research habits (relying on tools that don't work)
- Better to teach them Semantic Scholar, Google Scholar, arXiv search - these actually work
- The "AI-powered" features failed universally - worse than keyword search

**If the system worked, I would value:**
- Code availability filtering (addresses reproducibility crisis)
- Difficulty progression (helps first-years vs. advanced students)
- Technique extraction (cross-pollination between subfields)
- Reading list generation (saves faculty curation time)

**But none of these features functioned during testing.**

---

## Delights

**None.** Every feature attempted resulted in loading failures or errors.

**Potential delights (if system worked):**
- Seminal Papers filter - directly addresses teaching needs
- Learning Path generation - automates student guidance
- Code generation from papers - supports reproducibility
- Difficulty labeling - helps match papers to student level

---

## Frustrations

### Critical (Blocking)
1. **Search returns 0 results for major topics** - "efficient language models" is not obscure
2. **Research Advisor timeout + error** - AI feature completely broken
3. **All Discovery tabs infinite loading** - 7/8 features non-functional
4. **No error recovery** - system hung, required reload (untested due to time)

### High (Severely Impairs Use)
5. **No loading time indicators** - unclear if system is working or broken
6. **Performance degradation** - each action slower than previous
7. **Broken UI states** - "Building learning path" before topic entered
8. **No fallback mechanisms** - when AI fails, no basic search available

### Medium (Annoying)
9. **No citation counts visible** - cannot assess paper impact without loading details
10. **No paper preview** - must expand each paper to see anything beyond title
11. **No export functionality** - cannot share findings even if search worked
12. **Unclear data freshness** - "138,986 papers" but which papers? From when?

---

## Performance Metrics

| Operation | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Page Load (Explore) | <2s | ~2s | ✓ |
| Search "efficient language models" | <3s | 10s+ timeout | ✗ |
| Research Advisor query | <5s | 10s+ timeout, then error | ✗ |
| Discovery/High Impact load | <3s | Never completed | ✗ |
| Discovery/Reproducible load | <3s | Never completed | ✗ |
| Discovery/Learning Path load | <3s | Broken state, never initiated | ✗ |
| Discovery/TL;DR load | <3s | Never completed | ✗ |
| Discovery/Techniques load | <3s | Never completed | ✗ |
| Discovery/Rising load | <3s | Never completed | ✗ |

**Performance verdict:** System is non-functional, not slow. 9/10 attempted operations failed.

---

## Priority Improvements

### P0 (Critical - System Unusable Without)
1. **Fix search backend** - returns 0 results for valid queries
   *Impact:* Critical | *Effort:* High | *ROI:* Infinite (unusable → usable)

2. **Fix Discovery tab data loading** - all tabs timeout
   *Impact:* Critical | *Effort:* High | *ROI:* Infinite (7 features broken → working)

3. **Fix Research Advisor backend** - timeout and errors
   *Impact:* Critical | *Effort:* High | *ROI:* Infinite (flagship feature broken)

### P1 (High - Major Faculty Needs)
4. **Add loading timeouts with error messages** - user knows when to give up
   *Impact:* High | *Effort:* Low | *ROI:* High (reduces frustration)

5. **Implement graceful degradation** - if AI fails, fall back to keyword search
   *Impact:* High | *Effort:* Medium | *ROI:* High (system remains usable)

6. **Add citation counts to paper cards** - faculty assess impact at glance
   *Impact:* High | *Effort:* Low | *ROI:* Medium (faster triage)

### P2 (Medium - Teaching Features)
7. **Export reading lists** - share with students
   *Impact:* Medium | *Effort:* Medium | *ROI:* Medium (enables core use case)

8. **Show paper publication dates prominently** - distinguish foundational vs. recent
   *Impact:* Medium | *Effort:* Low | *ROI:* Medium (teaching context)

9. **Add "Copy citation" button** - faculty workflow efficiency
   *Impact:* Low | *Effort:* Low | *ROI:* Low (convenience)

---

## Screenshots Index

1. `01-landing-first-impression.png` - Explore page initial load, filters visible
2. `02a-nav-discovery.png` - Discovery hub with tabs and metrics
3. `02b-nav-generate.png` - Generate page (code from papers)
4. `03-search-results.png` - Search loading state for "efficient language models"
5. `03b-search-loading.png` - Search returned 0 results (critical failure)
6. `03c-advisor-panel.png` - Research Advisor panel opened
7. `03d-advisor-searching.png` - Advisor "Searching papers..." state (not viewed)
8. `03e-advisor-timeout.png` - Advisor still searching after 10s, eventually errored
9. `04-high-impact-loading.png` - High Impact tab loading (not viewed)
10. `04b-high-impact-timeout.png` - High Impact still loading after 5s
11. `05-reproducible-loading.png` - Reproducible tab loading indefinitely
12. `06-learning-path.png` - Learning Path in broken state ("Building..." without input)
13. `07-tldr-loading.png` - TL;DR tab loading (saved but not viewed individually)
14. `08-techniques-loading.png` - Techniques tab loading (saved but not viewed)
15. `09-rising-loading.png` - Rising tab loading (saved but not viewed)
16. `10-explore-timeout.png` - Return to Explore, search still in progress
17. `12-final-state.png` - Final system state, completely non-functional

---

## Final Verdict

### Would I use this for my seminar?
**No.** The system cannot find papers on "efficient language models" - the exact topic of my seminar. This is not a tool limitation, it's a tool failure.

### Would I recommend to students?
**Absolutely not.** I would be wasting their time and teaching them to rely on broken tools. My students deserve better.

### Root Cause Analysis (Faculty Perspective)

This feels like a system that was:
1. **Designed with the right features** - I can see what the developers intended (learning paths, code availability, impact metrics)
2. **Never tested with real queries** - "efficient language models" is not edge case; it's mainstream NLP
3. **Suffering from backend infrastructure collapse** - universal timeouts suggest database/API issues, not UI bugs
4. **Released prematurely** - no production system should have 9/10 operations fail

### What Would Make Me Reconsider?

If the developers fix the P0 issues and I hear from a colleague it works:

1. **Demonstrate working search** - show me you can find BERT, DistilBERT, MobileBERT
2. **Prove Discovery tabs load** - I need High Impact and Reproducible for teaching
3. **Show reading list export** - must be able to share with students
4. **Provide uptime/status page** - faculty won't waste time on unreliable tools

### Academic Standards

As a researcher who reviews systems for publication, this system would not pass peer review. The failure modes are too severe, the coverage too incomplete, the reliability too low. It needs months of engineering work before it's ready for faculty use.

**Status:** Not recommended for academic use.

---

**Assessment Completed:** 2025-12-25
**Assessor:** Prof. James Williams (Persona)
**Total Time:** ~15 minutes
**Screenshots:** 17
**Verdict:** System non-functional, cannot recommend
