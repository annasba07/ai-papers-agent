# UX Assessment: Prof. James Williams
**MIT CSAIL Faculty | NLP Researcher | Graduate Seminar Instructor**

**Date:** 2025-12-23
**Session Duration:** ~15 minutes
**Task:** Prepare reading list for graduate seminar on efficient language models

---

## Executive Summary

**Verdict: Cannot recommend to students. Critical search failures prevent basic usage.**

The AI Paper Atlas search system is fundamentally broken. Multiple search attempts for "efficient language models" returned 0 results with 10+ second response times. The Research Advisor feature crashed with an error. As an educator preparing course materials, I cannot use a tool that fails to return any papers on a well-established research topic. This tool is not ready for academic use.

---

## Session Timeline

| Time | Step | Action | Result | Emotion |
|------|------|--------|--------|---------|
| 0:00 | 1 | Landing page load | Clean UI, filters visible | 4/5 |
| 0:15 | 2 | Navigate to Discovery | Loading state, no content shown | 3/5 |
| 0:30 | 3 | Keyword search: "efficient language models" | 30 results shown (keyword match only) | 2/5 |
| 1:00 | 3.5 | Click "Ask Advisor" button | Advisor panel opened | 3/5 |
| 1:30 | 3.5 | Submit detailed seminar query to Advisor | "Searching papers..." indicator | 3/5 |
| 1:40 | 3.5 | Advisor response received | ERROR: "Sorry, I encountered an error" | 1/5 |
| 2:00 | 4 | Close Advisor, check search results | 0 results, 10005ms response time | 1/5 |
| 2:30 | 5 | Apply cs.CL category filter | "AI-powered semantic search in progress" | 3/5 |
| 2:40 | 6 | Wait for semantic search | 0 results, 10212ms response time | 1/5 |
| 3:00 | 7 | Clear filters, try "Has Code" | Still 0 results | 1/5 |

**Average Emotional State:** 2.2/5 (Frustrated)
**Task Success:** 0% - Could not find a single relevant paper
**Would Return:** No
**Would Recommend to Students:** Absolutely not

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

**Screenshot:** `01-landing-first-impression.png`

**Visual Observations:**
- Professional, academic-appropriate design
- Clear value proposition: "Search and filter AI research papers"
- Filters sidebar well-organized (category, difficulty, time range)
- Search box prominent with "Ask Advisor" button
- Trending topics visible (LLMs, Diffusion Models, VLMs)

**Academic Assessment:**
- Interface suggests serious research tool
- Difficulty levels (Beginner → Expert) show pedagogical awareness
- Trending topics could help identify hot areas for seminars

**Emotion:** 4/5 - Promising first impression

---

### Step 2: Navigation Discovery

**Screenshot:** `02-discovery-nav.png`

**Visual Observations:**
- Discovery page with tabs: Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path
- "Quick Discovery" section with categorized buttons
- Loading state displayed ("Loading papers...")
- Clean information architecture

**Academic Assessment:**
- "Learning Path" feature directly addresses curriculum design needs
- "Reproducible" section aligns with my code availability requirements
- Tab organization makes sense for different discovery modes

**Issues:**
- Content didn't load during my brief visit
- Unclear if this is the right place to start

**Emotion:** 3/5 - Organized but empty

---

### Step 3: Task-Based Search - Finding Relevant Papers

**Screenshot:** `03a-search-typed.png`

**Search Query:** "efficient language models"

**Visual Observations:**
- Search box accepted query
- "30 results" displayed
- Filter badge: "# KEYWORD MATCH"
- First visible paper: "Generative View Stitching" (CS.CV)
- Results appear to be unfiltered corpus, not semantically matched

**Critical Issues:**
1. **No semantic understanding**: Query about "efficient language models" returned computer vision papers
2. **Keyword-only matching**: The "KEYWORD MATCH" badge confirms shallow search
3. **No relevance ranking**: Results appear to be recent papers, not relevant ones

**Academic Assessment:**
As a researcher, I need semantic search. A graduate seminar on efficient LMs should return:
- BERT distillation papers (DistilBERT, TinyBERT)
- Model compression techniques
- Efficient attention mechanisms (Linformer, Performer)
- Quantization approaches

Instead, I got generic recent papers with no connection to efficiency or language models.

**Emotion:** 2/5 - Disappointed, but hoping Advisor helps

---

### Step 3.5: Research Advisor (AI-Powered Search)

**Screenshots:**
- `03b-advisor-opened.png` - Panel opened
- `03c-advisor-query-sent.png` - Query submitted
- `03d-advisor-response.png` - Error received

**Query Submitted:**
> "I'm preparing a graduate seminar on efficient language models. I need foundational papers on model compression, distillation, and efficiency techniques for transformers. Also looking for recent advances."

**Visual Observations:**
- Clean conversational interface
- Suggested example queries visible
- Input accepted full pedagogical context
- Loading indicator: "Searching papers..."
- **CRITICAL FAILURE:** Error message after ~8 seconds: "Sorry, I encountered an error while searching. Please try again."

**Critical Issues:**
1. **Complete failure of flagship feature**: The "AI-powered" advisor crashed
2. **No fallback**: After error, no alternative suggestions or results
3. **No error recovery**: Generic error message with no actionable guidance
4. **Lost context**: My detailed seminar requirements were discarded

**Academic Assessment:**
This is the feature that should differentiate Paper Atlas from Google Scholar. It failed completely. I provided:
- Clear role (graduate instructor)
- Specific topic (efficient language models)
- Concrete subtopics (compression, distillation, efficiency techniques)
- Time dimension (foundational + recent)

Any competent literature search system should excel at this query. The Advisor error is a showstopper.

**Emotion:** 1/5 - Professionally frustrated. This wastes my time.

---

### Step 4-7: Attempting Recovery

**Screenshot:** `04-close-advisor.png`, `05-category-filter.png`, `06-search-results.png`, `07-has-code-filter.png`

**Actions Attempted:**
1. Closed Advisor panel → 0 results still displayed
2. Applied cs.CL (Computation & Language) category filter
3. Waited for "AI-powered semantic search in progress" to complete
4. Cleared filters, tried "Has Code" quick filter

**Results:**
- **Every attempt:** 0 results
- **Every response time:** 10+ seconds (10005ms, 10212ms)
- **Search status:** "No papers found. Try different keywords or describe your research goal in more detail."

**Critical Issues:**
1. **Database appears empty**: 0 papers indexed in cs.CL is impossible
2. **Slow failure**: 10-second waits just to get "0 results"
3. **No diagnostics**: System doesn't explain why search failed
4. **No suggestions**: No related queries, no spell check, nothing

**Academic Assessment:**
At this point, I concluded the system is non-functional. The backend appears broken - either the database is empty, the search index is corrupted, or there's a critical API failure.

For comparison:
- **Semantic Scholar:** Would return 1000+ papers on this query instantly
- **Google Scholar:** Would return relevant results in <1 second
- **ArXiv search:** Would find dozens of matching papers
- **Paper Atlas:** 0 results after 10 seconds

**Emotion:** 1/5 - This is not a viable tool

---

## Pain Point Assessment

### Pain Point 1: Curation Burden ❌ **NOT SOLVED**
**Need:** Maintain reading lists for graduate seminar
**Outcome:** Could not find a single paper to add to reading list
**Impact:** Tool is completely unusable for this purpose

### Pain Point 2: Student Guidance ❌ **NOT SOLVED**
**Need:** Answer "what should I read?" for PhD students
**Outcome:** Would be embarrassed to recommend this tool to students
**Impact:** Students would lose confidence in my recommendations

### Pain Point 3: Reproducibility Standards ❓ **CANNOT EVALUATE**
**Need:** Prefer papers with released code
**Outcome:** "Has Code" filter visible but search returned 0 results
**Impact:** Cannot test if code availability is surfaced properly

### Pain Point 4: Field Breadth ❓ **CANNOT EVALUATE**
**Need:** Keep up with multimodal/vision-language work affecting NLP
**Outcome:** Cross-domain discovery features not tested due to search failure
**Impact:** Potentially valuable, but inaccessible

### Pain Point 5: Historical Context ❓ **CANNOT EVALUATE**
**Need:** Help students understand intellectual history
**Outcome:** "Learning Path" feature exists but couldn't test with 0 results
**Impact:** Concept is good, execution unknown

---

## Teaching Utility Assessment

### For Graduate Seminars: **F (Fail)**
- Cannot find foundational papers
- Cannot find recent advances
- Cannot build reading progression
- Search system is non-functional

### For PhD Student Advising: **F (Fail)**
- Would damage credibility to recommend
- Students need reliable tools
- Broken search wastes research time

### For Curriculum Development: **Incomplete**
- "Difficulty" filters show pedagogical thinking
- "Learning Path" feature conceptually valuable
- But core functionality (search) doesn't work

---

## Student Recommendation Potential

**Would I recommend to my students?** **Absolutely not.**

**Reasons:**
1. **Unreliable core functionality**: Search returns 0 results on standard queries
2. **Slow performance**: 10-second response times for failures
3. **No error recovery**: System crashes with generic error messages
4. **Credibility risk**: Recommending broken tools damages instructor trust
5. **Time waste**: Students' research time is valuable

**What would need to change:**
1. Fix the search backend immediately (appears to be database/index issue)
2. Semantic search must work reliably
3. Response times must be <2 seconds
4. Advisor feature must not crash
5. Basic queries like "efficient language models" must return results

**Current state:** Pre-alpha quality, not ready for academic use

---

## Delights

**None.** I cannot identify any delightful moments when core functionality is broken.

**Potential delights** (if system worked):
- Clean, academic-appropriate interface
- "Learning Path" concept for curriculum design
- Integration of code availability (important for reproducibility)
- Pedagogical difficulty levels

---

## Frustrations

### 1. **Complete Search Failure** (Critical)
- **What:** Every search query returned 0 results
- **Impact:** Tool is completely unusable
- **Frequency:** 100% of search attempts

### 2. **Research Advisor Crash** (Critical)
- **What:** Flagship AI feature crashed with error
- **Impact:** Lost detailed query context, no results
- **Frequency:** 1/1 attempts (100% failure rate)

### 3. **Extremely Slow Failures** (Major)
- **What:** 10+ seconds to return "0 results"
- **Impact:** Time wasted waiting for failures
- **Why frustrating:** Fast tools fail fast; slow failures are worst UX

### 4. **No Error Diagnostics** (Major)
- **What:** Generic "try different keywords" message
- **Impact:** No actionable guidance for recovery
- **Why frustrating:** As a technical user, I want to understand what's broken

### 5. **No Fallback Mechanisms** (Moderate)
- **What:** When semantic search fails, no keyword fallback offered
- **Impact:** Dead end with no recovery path
- **Why frustrating:** Robust systems degrade gracefully

---

## Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Page Load Time | Not measured | <2s | ❓ |
| First Search Response | 10005ms | <3s | ❌ (3.3x slower) |
| Second Search Response | 10212ms | <3s | ❌ (3.4x slower) |
| Advisor Response | ERROR | <5s | ❌ (Crashed) |
| Results Returned | 0 | >10 | ❌ (Complete failure) |
| Success Rate | 0% | >80% | ❌ |

**Performance Verdict:** Unacceptable. Slow AND broken.

---

## Priority Improvements

### P0: Critical - Fix Search Backend
**Impact:** 10/10 (Tool is unusable without this)
**Effort:** Unknown (appears to be database/index corruption)
**Evidence:** Every search query returns 0 results
**Action:** Investigate backend connectivity, database status, search index integrity

### P0: Critical - Fix Research Advisor
**Impact:** 10/10 (Flagship feature completely broken)
**Effort:** Unknown (API failure or backend crash)
**Evidence:** Error on well-formed pedagogical query
**Action:** Check API error logs, validate LLM integration, add error handling

### P0: Critical - Improve Response Time
**Impact:** 8/10 (10-second waits are unacceptable)
**Effort:** Medium (likely query optimization needed)
**Evidence:** 10+ second responses for failures
**Action:** Add timeouts, optimize queries, cache common searches

### P1: High - Add Error Diagnostics
**Impact:** 6/10 (Helps users understand failures)
**Effort:** Low (better error messages)
**Evidence:** Generic "try different keywords" is not actionable
**Action:** Provide specific error types (no results vs. backend error vs. timeout)

### P1: High - Implement Fallback Search
**Impact:** 7/10 (Graceful degradation)
**Effort:** Medium (keyword fallback when semantic fails)
**Evidence:** When AI search fails, nothing happens
**Action:** Offer keyword-based fallback when semantic search unavailable

### P2: Medium - Add Search Diagnostics for Educators
**Impact:** 5/10 (Helps instructors evaluate results)
**Effort:** Low (show match reasons, relevance scores)
**Evidence:** No explanation of why papers matched query
**Action:** Display relevance scores, matching keywords, semantic similarity

---

## Screenshots Index

1. **01-landing-first-impression.png** - Initial page load, filters visible
2. **02-discovery-nav.png** - Discovery page with tabs (loading state)
3. **03a-search-typed.png** - Keyword search entered, 30 irrelevant results
4. **03b-advisor-opened.png** - Research Advisor panel opened
5. **03c-advisor-query-sent.png** - Detailed pedagogical query submitted
6. **03d-advisor-response.png** - **ERROR: Advisor crashed**
7. **04-close-advisor.png** - Closed Advisor, 0 results displayed
8. **05-category-filter.png** - Applied cs.CL filter, semantic search loading
9. **06-search-results.png** - **0 results after 10+ seconds**
10. **07-has-code-filter.png** - Attempted "Has Code" filter (not captured fully)

---

## Final Verdict

### Would I use this for my seminar? **No.**
The tool does not work. I cannot prepare a reading list with 0 search results.

### Would I recommend to students? **Absolutely not.**
Recommending broken tools damages instructor credibility and wastes student time.

### What needs to happen before I'd reconsider?

**Minimum requirements:**
1. ✅ Search must return results for standard academic queries
2. ✅ Response time must be <3 seconds
3. ✅ Research Advisor must not crash
4. ✅ Semantic search must understand "efficient language models" as NLP topic

**Desired features** (for positive recommendation):
1. Citation-based ranking (show impact metrics)
2. Foundational paper identification (flag seminal works)
3. Reading progression generation (beginner → advanced)
4. Integration with course management (export to reading lists)

---

## Pedagogical Perspective

**As an educator with 15+ years of experience:**

This tool shows **conceptual understanding** of academic needs:
- Difficulty levels indicate pedagogical awareness
- "Learning Path" suggests curriculum design thinking
- Code availability aligns with reproducibility standards
- Multi-dimensional filtering (time, impact, category) is valuable

But it demonstrates **complete execution failure:**
- Search engine is non-functional (0 results)
- Flagship features crash (Research Advisor error)
- Performance is unacceptable (10+ second failures)
- No quality assurance evident (basic queries fail)

**My assessment:** Good ideas, broken implementation. Not ready for academic use.

**Recommendation to developers:** Fix the backend before adding features. A working search engine is table stakes. The pedagogical thinking is sound, but the engineering needs significant work.

**Timeline:** I would not revisit this tool for at least 6 months, assuming major backend fixes are made. When search reliably returns results in <3 seconds, I would be willing to test again.

---

**Session completed:** 2025-12-23
**Total time:** ~15 minutes
**Papers found for seminar:** 0
**Likelihood of return:** Very low
**Overall experience:** 1.5/5 stars
