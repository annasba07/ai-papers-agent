# UX Assessment Report: Dr. Emily Zhang
## AI Paper Atlas - Interdisciplinary Researcher Perspective

**Assessment Date:** December 23, 2025
**Session Duration:** ~8.5 minutes (19:57:04 - 20:05:39)
**Persona:** Dr. Emily Zhang - Climate Science Researcher using ML
**Research Goal:** Find transformer architectures for weather prediction and time series forecasting

---

## Executive Summary

As an atmospheric scientist exploring ML for climate modeling, I found AI Paper Atlas **completely non-functional** during this session. Search returned 0 results for multiple queries ("transformers time series", "neural network"), the Research Advisor threw an error when I described my cross-domain research problem, and I was unable to evaluate any of the features designed to help interdisciplinary researchers like myself. The database appeared empty throughout the entire session.

**Verdict:** Cannot recommend. The tool would be unusable in its current state.

---

## Session Timeline

| Time | Step | Action | Outcome | Emotion |
|------|------|--------|---------|---------|
| 19:57:04 | 0 | Environment setup | Viewport set to 1440x900 | 3/5 |
| 19:57:15 | 1 | First impression - landing page | Redirected to /explore, ML-focused examples visible | 3/5 |
| 19:57:28 | 2 | Navigation exploration | Clicked Discovery (loaded but showing 0 papers) | 3/5 |
| 19:58:05 | 3 | Search: "transformers time series" | 0 results in 10546ms | 2/5 |
| 19:58:42 | 3.5 | Research Advisor attempt | Opened panel, described climate modeling problem | 3/5 |
| 19:59:18 | 3.5 | Research Advisor response | Error: "Sorry, I encountered an error while searching" | 2/5 |
| 20:00:05 | 3 | Search: "neural network" | 0 results (10001ms) | 2/5 |
| 20:01:12 | - | Navigate to Generate page | Code generation feature visible but needs papers | 2/5 |
| 20:05:39 | 12 | Final reflection | Unable to test core features, database appears empty | 2/5 |

**Average Emotional State:** 2.4/5 (Frustrated)

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

**Screenshot:** `01-landing-first-impression.png`

**What I Saw:**
- Clean, professional interface
- Automatically redirected to /explore page
- Search bar with placeholder text about "efficient attention for mobile deployment"
- Sidebar with filters (Categories, Difficulty, Time Range, Trending Topics)
- Example prompts: "How to make AI explain its decisions", "Speed up neural network training", etc.
- Showing "30 papers" initially

**Observations:**
- The example prompts are all ML/AI-focused (chatbots, neural networks, medical imaging)
- No examples related to physical sciences, climate, weather, or scientific computing
- The language assumes ML expertise ("attention", "neural networks", "RLHF")
- Categories listed: "Artificial Intelligence", "Machine Learning", "Computer Vision", etc. - no "Scientific ML" or "Applications"

**Pain Point Match:**
- ❌ **Terminology Gap:** The interface speaks pure ML jargon from the start
- ❌ **Cross-Domain Discovery:** No indication that the tool understands scientific applications
- ⚠️ **Limited ML Background:** Assumes familiarity with ML concepts

**Emotion:** 3/5 - Curious but already feeling like an outsider

---

### Step 2: Initial Exploration (Navigation Discovery)

**Screenshot:** `02-navigation-explore.png`

**What I Saw:**
- Clicked "Discovery" link - page loaded showing discovery features
- Navigation tabs: Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path
- "Quick Discovery" cards visible
- Page showed "Loading papers..." but eventually displayed empty state

**Observations:**
- Discovery page has many features that could be useful (Learning Path, Techniques)
- The page structure looks well-organized
- But immediately hit the core issue: 0 papers available

**Pain Point Match:**
- ⚠️ **Cross-Domain Discovery:** Couldn't test discovery features due to empty database

**Emotion:** 3/5 - Interested in the features but concerned about lack of content

---

### Step 3: Task-Based Search - "transformers time series"

**Screenshot:** `03-search-transformers-timeseries.png`

**What I Saw:**
- Entered my natural search term: "transformers time series"
- Search took 10546ms (~10.5 seconds)
- Result: "0 results"
- Message: "No papers found - Try different keywords or describe your research goal in more detail"
- Sidebar showed "0 papers"

**Observations:**
- This is exactly the query I would use as a climate scientist
- Search was slow (>10 seconds) for 0 results
- No suggestions for alternative terms
- No indication of *why* there are no results (database empty? bad query? wrong terminology?)
- The "Ask Research Advisor" button appeared as a fallback option

**Pain Point Match:**
- ❌ **Terminology Gap:** My domain-specific terms ("time series" for temporal climate data) found nothing
- ❌ **Cross-Domain Discovery:** No cross-domain search working
- ❌ **Adaptation Complexity:** Can't find techniques that might transfer to my domain

**Emotion:** 2/5 - Frustrated. This is exactly what I feared - my language doesn't match the tool's language.

---

### Step 3.5: Research Advisor Attempt

**Screenshots:**
- `04-advisor-panel-opened.png` - Panel opened with example prompts
- `05-advisor-searching.png` - My query submitted, "Searching papers..." state
- `06-advisor-error.png` - Error message received

**What I Saw:**
- Clicked "Ask Research Advisor" button
- Panel opened on the right side with friendly intro text
- Example prompts shown (same ML-focused ones from landing page)
- Entered detailed description: "I'm working on using ML for weather prediction and climate modeling. I want to understand which transformer architectures work well for long-range time series forecasting with physical science data."
- Query submitted, showed "Searching papers..." with loading indicator
- After ~5 seconds: "Sorry, I encountered an error while searching. Please try again."

**Observations:**
- The Research Advisor interface is clean and inviting
- Natural language input worked well
- But the feature completely failed with an error
- No error details, no guidance on what went wrong
- This was my last hope for cross-domain discovery - describing my problem in plain language

**Pain Point Match:**
- ❌ **Terminology Gap:** Natural language query should have helped, but feature broke
- ❌ **Cross-Domain Discovery:** Couldn't test semantic understanding due to error
- ❌ **Limited ML Background:** Feature designed for this use case, but non-functional

**Emotion:** 2/5 - Very frustrated. The one feature that seemed designed for researchers like me didn't work.

---

### Step 4: Second Search Attempt - "neural network"

**Screenshot:** `07-search-neural-network-failed.png`

**What I Saw:**
- Tried a simpler, more generic ML term: "neural network"
- Search took 10001ms (~10 seconds)
- Result: "0 results"
- Same empty state as before

**Observations:**
- Even basic ML terminology returns nothing
- Confirms the database is empty or severely broken
- Search performance is poor (10+ seconds for 0 results)

**Pain Point Match:**
- ❌ All pain points - can't evaluate anything without papers

**Emotion:** 2/5 - Giving up on search functionality

---

### Step 5: Generate Page Exploration

**Screenshots:**
- `08-generate-page.png` - Code generation feature
- `09-final-state.png` - Final state at session end

**What I Saw:**
- Navigated to "Generate" page
- Feature: "Turn Papers into Working Code"
- 5-agent system described: Paper Analyzer → Test Designer → Code Generator → Test Executor → Debugger
- Step 1: "Find a Paper" - search box disabled until papers available
- Step 2: "Generate Code" - grayed out

**Observations:**
- This feature could be valuable for implementation (Pain Point: Adaptation Complexity)
- Well-explained workflow
- But completely inaccessible without papers in the database

**Pain Point Match:**
- ⚠️ **Adaptation Complexity:** Could help translate papers to working code, but can't test

**Emotion:** 2/5 - Interesting feature I can't use

---

## Pain Point Assessment

### Did AI Paper Atlas solve my research pain points?

| Pain Point | Status | Notes |
|------------|--------|-------|
| **1. Terminology Gap** | ❌ Failed | Search didn't understand "transformers time series". No terminology bridging observed. |
| **2. Cross-Domain Discovery** | ❌ Failed | Couldn't test - database empty and Research Advisor errored. |
| **3. Adaptation Complexity** | ❌ Failed | Code generation feature exists but inaccessible without papers. |
| **4. Limited ML Background** | ❌ Failed | No foundational guidance available, Learning Path feature untested. |
| **5. Justification to Peers** | ❌ Failed | Couldn't find any papers to justify, let alone techniques. |

**Overall:** 0/5 pain points addressed. Complete failure for interdisciplinary use case.

---

## Cross-Domain Discovery Assessment

**Goal:** Find techniques from NLP/vision that transfer to climate/weather data.

**Result:** Unable to assess. The core functionality required for cross-domain discovery:
1. **Semantic search** across multiple domains - 0 results for all queries
2. **Research Advisor** natural language understanding - threw error
3. **Technique browsing** by methodology - couldn't access
4. **Related paper discovery** - no base papers to start from

**Expected Workflow:**
1. Describe problem in domain language → Get ML techniques
2. Browse papers by technique (e.g., "attention mechanisms") → See climate applications
3. Ask "what works for long-range forecasting?" → Get relevant recommendations

**Actual Experience:**
1. Describe problem → Error
2. Search by technique → 0 results
3. Ask question → Can't even attempt

---

## Accessibility for Non-ML Experts

**Language Analysis:**
- Landing page: Pure ML jargon ("attention", "neural networks", "diffusion models", "RLHF")
- No glossary or explanations
- Example prompts assume ML knowledge
- Category filters all ML subfields, no application domains

**Onboarding:**
- No tutorial or guidance for interdisciplinary users
- Assumes users know how to search for ML papers
- No "start here" for domain scientists

**Learning Resources:**
- Learning Path feature exists but couldn't test (0 papers)
- No visible documentation or help for cross-domain researchers

**Verdict:** Interface designed for ML researchers, not domain scientists exploring ML.

---

## Transfer Potential Evaluation

**Could I find techniques applicable to climate modeling?**

**Unable to assess** due to complete lack of functionality. However, based on interface design:

**Potential (if working):**
- ✅ Research Advisor could understand "weather prediction" and map to relevant techniques
- ✅ Technique taxonomy could show what's transferable
- ✅ Code generation could help prototype implementations
- ⚠️ Would need climate-specific examples or cross-domain tagging

**Missing (even if working):**
- No "application domain" filter (climate, physics, biology, etc.)
- No indication of whether papers discuss scientific data
- No "similar applications" discovery (e.g., "other time series in physical sciences")

---

## Delights and Frustrations

### Delights
1. **Research Advisor concept** - The idea of describing my problem in natural language is exactly what I need
2. **Code generation** - Could save enormous time adapting papers to climate data
3. **Clean interface** - Professional, not overwhelming
4. **Learning Path feature** - Would help me build foundational knowledge systematically

### Frustrations
1. **Complete non-functionality** - Nothing worked. 0 papers, advisor error, broken search (🔥 Critical)
2. **No error explanations** - "Error while searching" tells me nothing (🔥 Critical)
3. **Poor search performance** - 10+ seconds for 0 results (High)
4. **ML-only language** - Feels exclusionary to domain scientists (High)
5. **No fallback guidance** - When search fails, no suggestions or help (Medium)
6. **No status indicators** - Is the database loading? Indexing? Down? (Medium)

---

## Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Initial page load | Unknown (eval error) | <2s | ❓ |
| Search response time | 10001-10546ms | <3s | ❌ Failed (3-4x too slow) |
| Research Advisor response | Error after ~5s | <5s | ❌ Failed (error) |
| Papers indexed | 0 | >1000 | ❌ Critical failure |
| Successful interactions | 0/4 | 100% | ❌ 0% success rate |

---

## Priority Improvements

### Critical (Blocking)
1. **Fix database/indexing** (Impact: 🔥🔥🔥🔥🔥, Effort: Unknown)
   - Papers showing "30 papers" initially but searches return 0
   - Without papers, entire product is non-functional

2. **Fix Research Advisor errors** (Impact: 🔥🔥🔥🔥, Effort: Medium)
   - Core feature for interdisciplinary users
   - Natural language query is the terminology bridge we need

3. **Improve search performance** (Impact: 🔥🔥🔥, Effort: Medium)
   - 10+ seconds for 0 results is unacceptable
   - Should be <1s for empty results

### High Priority
4. **Add domain/application filters** (Impact: 🔥🔥🔥🔥, Effort: Medium)
   - "Climate", "Physics", "Biology", "Chemistry", etc.
   - Enable cross-domain discovery by application

5. **Better error messaging** (Impact: 🔥🔥🔥, Effort: Low)
   - "Database currently indexing - check back in X minutes"
   - "No papers found for 'X'. Try: [suggestions]"
   - "Advisor error: [specific issue]. Try [alternative]"

6. **Add non-ML example prompts** (Impact: 🔥🔥🔥, Effort: Low)
   - "Find ML for climate prediction"
   - "Techniques for scientific time series"
   - "Neural networks for physics simulations"

### Medium Priority
7. **Terminology glossary** (Impact: 🔥🔥, Effort: Medium)
   - Explain ML terms for domain scientists
   - Link terms to application examples

8. **Cross-domain tagging** (Impact: 🔥🔥, Effort: High)
   - Tag papers with application domains
   - Show "also applied to [domain]" connections

9. **Empty state guidance** (Impact: 🔥🔥, Effort: Low)
   - When 0 results, suggest alternatives
   - Offer to contact support or check system status

---

## Screenshots Index

1. `01-landing-first-impression.png` - Initial page load, ML-focused examples visible
2. `02-navigation-explore.png` - Discovery page navigation, 0 papers shown
3. `03-search-transformers-timeseries.png` - First search attempt, 0 results
4. `04-advisor-panel-opened.png` - Research Advisor interface opened
5. `05-advisor-searching.png` - Advisor processing my climate modeling query
6. `06-advisor-error.png` - Advisor error message received
7. `07-search-neural-network-failed.png` - Second search attempt, still 0 results
8. `08-generate-page.png` - Code generation feature page
9. `09-final-state.png` - Final session state, Generate page with no papers

---

## Final Verdict

**Would I use this tool for my climate modeling research?**
**No.** Not in its current state.

**Would I recommend it to other domain scientists?**
**No.** The tool is completely non-functional - 0 papers indexed, search broken, Research Advisor throwing errors.

**What would change my mind:**
1. Fix the database (must have papers to search)
2. Fix the Research Advisor (critical for cross-domain users)
3. Add application domain filters (climate, physics, etc.)
4. Show examples of cross-domain applications
5. Improve error handling and user guidance

**Potential if Fixed:**
If the core functionality worked, this could be transformative for interdisciplinary ML research. The Research Advisor concept is exactly what domain scientists need - a bridge between our language and ML terminology. But in its current state, it's unusable.

**Key Insight for Product Team:**
You have features designed for interdisciplinary researchers (Research Advisor, natural language search), but the implementation assumes users speak ML fluently. The interface needs to meet domain scientists where we are - in our terminology, with our use cases, showing us how ML techniques apply to *our* data problems. Right now, it feels like a tool built by ML researchers, for ML researchers.

---

**Assessment completed:** 2025-12-23 20:05:39
**Total screenshots:** 9
**Session success rate:** 0% (0 of 4 attempted features worked)
