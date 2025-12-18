# UX Assessment Report: AI Paper Atlas
**Persona**: Prof. James Williams (MIT NLP Faculty)
**Use Case**: Graduate Seminar Preparation - Efficient Language Models
**Date**: 2025-12-17
**Session Duration**: ~25 minutes

---

## Executive Summary

As a professor preparing a graduate seminar on efficient language models, I need to quickly find papers progressing from foundational work (DistilBERT) to cutting-edge quantization and pruning techniques. AI Paper Atlas delivered relevant search results consistently (2.8-7.7s response times), but critical gaps emerged: missing citation counts prevent impact assessment, the Research Advisor feature proved too slow (15+ seconds) with synthesis unavailable, and "Invalid Date" errors undermine credibility. The tool shows promise for discovery but needs metadata completeness and performance optimization before I'd recommend it to students.

---

## Session Timeline

| Step | Task | Time | Load Time | Emotional State | Success |
|------|------|------|-----------|-----------------|---------|
| 0 | Environment setup | 11:56 | - | 3/5 | ✓ |
| 1 | Landing page first impression | 11:57 | N/A | 3/5 | ✓ |
| 2 | Navigation discovery | 11:58 | - | 3/5 | Partial |
| 3 | Search "efficient language models" | 11:59 | 7752ms | 4/5 | ✓ |
| 3.5 | Research Advisor query | 12:01 | 15000ms+ | 2/5 | ✗ |
| 5 | Code availability filter | 12:04 | ~1000ms | 3/5 | ✓ |
| 11 | Second search "knowledge distillation" | 12:06 | 2867ms | 4/5 | ✓ |
| 12 | Exit reflection | 12:07 | - | 3/5 | ✓ |

**Average Search Response**: 5.3 seconds
**Overall Session Emotion**: 3.3/5 (Neutral with frustration moments)

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

**Screenshot**: `01-landing-first-impression.png`

**Observation**: Clean, professional layout immediately visible. Search bar prominent with "Ask Advisor" button suggesting AI assistance. Filters sidebar shows 1,036 papers indexed - gives confidence in coverage.

**Issues Identified**:
- No value proposition or "what is this tool" statement visible
- Landing redirected to `/explore` immediately - unclear if this is intended behavior
- Missing citation counts on preview cards (critical for academic assessment)

**Emotion**: 3/5 (Neutral) - Professional appearance but unclear positioning.

---

### Step 2: Initial Exploration (Navigation Discovery)

**Screenshot**: `02a-nav-generate.png`

**Observation**: Clicked "Generate" tab out of curiosity. Found multi-agent code generation feature - interesting but irrelevant to my seminar prep task.

**Issues Identified**:
- Only 2 navigation items (Explore, Generate) - limited discoverability
- No "About", "How it works", or "Browse by category" sections
- Generate feature feels disconnected from paper research workflow

**Emotion**: 3/5 (Neutral) - Navigation too minimal, returned to Explore quickly.

---

### Step 3: Task-Based Search - Finding Relevant Papers

**Screenshot**: `03-search-results.png`

**Query**: "efficient language models"
**Results**: 31 papers in 7752ms (~7.7 seconds)
**Relevance**: Excellent - top results covered distillation, pruning, quantization, finetuning

**Positive Observations**:
- AI-powered "Smart Results" badge suggests semantic ranking
- TL;DR summaries enable quick scanning
- Top 6 papers highly relevant to seminar curriculum

**Issues Identified**:
- **CRITICAL**: "Invalid Date" appears on all papers in top section - data quality issue
- No citation counts visible (need this to prioritize impactful papers for students)
- 7.7s load time feels slow for a keyword search
- No indication of which papers have been cited together (citation network)

**Emotion**: 4/5 (Satisfied with relevance, concerned about missing metadata)

---

### Step 3.5: Research Advisor (AI-Powered Search)

**Screenshot**: `03b-research-advisor.png`

**Query**: "I'm preparing a graduate seminar on efficient language models. I need papers that progress from foundational work like DistilBERT to recent quantization and pruning techniques. Priority on papers with clear pedagogical value and available implementations."

**Result**: FAILURE
**Load Time**: 15+ seconds (timed out waiting for response)
**Final State**: "Contextual synthesis temporarily unavailable" with 5 generic paper recommendations

**Critical Issues**:
- **Performance**: 15+ second wait is unacceptable in an academic workflow
- **Synthesis unavailable**: The advertised "contextual" feature was non-functional
- **Generic recommendations**: Papers recommended didn't reflect my detailed pedagogical requirements
- **No error messaging**: Stuck on "Searching papers..." with no progress indicator

**Teaching Context**: If I recommend this tool to students and they encounter this, they'll abandon it immediately. Graduate students expect sub-3-second interactions.

**Emotion**: 2/5 (Frustrated) - This feature needs major performance work before being production-ready.

---

### Step 5: Code Availability Check

**Screenshot**: `05-code-filter.png`

**Observation**: Clicked "Has Code" quick filter. Results reduced from 31 to 9 papers immediately (~1s filter application).

**Positive Observations**:
- Filter worked correctly (31 → 9 papers)
- Clear visual feedback with "Has Code ×" dismissible tag
- Papers remaining likely have GitHub implementations

**Issues Identified**:
- No GitHub stars/forks count shown on paper cards
- No "View Code" direct link visible in results
- Cannot tell if code is official implementation vs. third-party

**Pedagogical Value**: Code availability is CRITICAL for a hands-on seminar. This filter helps but needs more metadata (implementation quality, maintenance status).

**Emotion**: 3/5 (Neutral) - Feature works but lacks depth.

---

### Step 11: Second Search (Consistency Check)

**Screenshot**: `11-second-search.png`

**Query**: "knowledge distillation"
**Results**: 31 papers in 2867ms (~2.9 seconds)
**Relevance**: Excellent - methodology papers on distillation techniques

**Observations**:
- **Faster than first search** (2.9s vs 7.7s) - suggests caching or index warming
- Different result set (predictive distribution, error correction approaches)
- Top papers now methodology-focused vs. application-focused in first search
- Consistent interface experience

**Emotion**: 4/5 (Satisfied) - Search quality consistent, performance improved.

---

### Step 12: Exit Reflection

**Screenshot**: `12-final-state.png`

**Final Verdict Questions**:

**Would you bookmark this tool?**
Maybe. The search quality is good enough for initial discovery, but missing citation counts and date errors make me hesitant to rely on it.

**Would you return tomorrow?**
Yes, if I'm doing exploratory research. No, if I need comprehensive metadata for citation analysis or seminar reading list creation.

**Would you recommend it to colleagues?**
Not yet. I'd need to see:
1. Citation counts on all papers
2. Working date fields (no "Invalid Date" errors)
3. Research Advisor performance <5 seconds
4. Learning path feature for seminar curriculum design

**What frustrated you most?**
1. Research Advisor timeout (15+ seconds) with synthesis unavailable
2. "Invalid Date" on recent papers - looks unprofessional
3. No citation counts - can't assess paper impact for student reading lists

**What delighted you most?**
1. Search relevance - both queries returned appropriate paper sets
2. TL;DR summaries - saved time scanning abstracts
3. "Has Code" filter - reduced 31 papers to 9 with implementations

**Overall Emotion**: 3/5 (Neutral leaning skeptical)

---

## Problem Assessment: Did It Solve My Pain Points?

### My Core Needs (Prof. Williams Perspective):

1. **Find progression of papers from foundational → cutting-edge** ✓ SOLVED
   - Search returned appropriate mix from DistilBERT-era to 2025 quantization work

2. **Assess paper impact for student reading lists** ✗ NOT SOLVED
   - No citation counts visible
   - Cannot identify seminal papers vs. recent exploratory work

3. **Verify code availability for hands-on labs** ⚠️ PARTIALLY SOLVED
   - Filter works (31 → 9 papers) but no implementation quality metadata

4. **Build learning path from basics to advanced** ⚠️ NOT TESTED
   - Skipped Step 6 (Learning Path) due to time constraints

5. **Quick scan of recent developments** ✓ SOLVED
   - TL;DR summaries effective for triage

### Pedagogical Value (1-5): **2.5/5**

The tool helps with discovery but lacks the metadata richness needed for curriculum design. I need to cross-reference with Google Scholar for citation counts and check GitHub manually for code quality.

---

## Teaching Utility

### Would I Use This for Seminar Prep?

**Current State**: Supplementary tool only
**Required for Primary Use**: Fix date errors, add citation metrics, improve Advisor performance

### Student Recommendation Potential

**Would I tell my graduate students to use this?**

**Pros**:
- Fast discovery of recent papers (2.9-7.7s)
- TL;DR summaries save time
- Code filter useful for implementation projects

**Cons**:
- "Invalid Date" errors damage credibility with critical students
- No citation metrics → students can't distinguish impactful work
- Research Advisor too slow and unreliable for real-time research

**Decision**: I'd mention it as "experimental" but emphasize Google Scholar + arXiv as primary sources until metadata issues are fixed.

---

## Performance Metrics

### Page Load Times
- Initial landing: Not measured (immediate redirect)
- Search #1 ("efficient language models"): 7752ms
- Search #2 ("knowledge distillation"): 2867ms
- Research Advisor: 15000ms+ (timeout)
- Filter application ("Has Code"): ~1000ms

### Search Quality
- Relevance (1-5): **4.5/5** - Both searches returned highly relevant papers
- Consistency (1-5): **4/5** - Similar quality across queries
- Coverage (1-5): **3/5** - 1,036 papers total, unclear if comprehensive

### Metadata Completeness
- Titles: 5/5 ✓
- Authors: 5/5 ✓
- Dates: 1/5 ✗ ("Invalid Date" on most recent papers)
- Citations: 0/5 ✗ (Only 1 paper showed "9 citations", rest missing)
- Code availability: 3/5 ⚠️ (Filter works but no quality indicators)

---

## Delights and Frustrations

### 😊 Delights

1. **Search Relevance**: Both queries returned papers that directly matched my seminar needs. The AI ranking clearly understood semantic meaning beyond keyword matching.

2. **TL;DR Summaries**: These are genuinely useful. I could scan 10 papers in 2-3 minutes vs. 10+ minutes reading abstracts on arXiv.

3. **Code Filter Responsiveness**: Clicking "Has Code" reduced 31 papers to 9 instantly. No lag, clear visual feedback.

### 😤 Frustrations

1. **Research Advisor Performance**: 15+ second timeout is unacceptable. This should be the tool's killer feature, but I'd never use it in this state.

2. **"Invalid Date" Errors**: Seeing "Invalid Date" on cutting-edge 2025 papers makes me question the entire data pipeline's reliability.

3. **Missing Citation Counts**: This is TABLE STAKES for academic search. Without citation metrics, I can't build a reading list that balances seminal papers with recent innovations.

4. **No Learning Path Discovery**: I wanted to test the learning path feature for curriculum design, but skipped it due to time. This could be a major differentiator if implemented well.

---

## Priority Improvements

### 1. Fix Date Display (Impact: HIGH, Effort: LOW)
**Problem**: "Invalid Date" appears on most recent papers
**Impact**: Damages credibility, prevents temporal filtering
**Effort**: Likely a simple date parsing bug in frontend
**Priority**: CRITICAL - Fix before public launch

### 2. Add Citation Counts to All Papers (Impact: HIGH, Effort: MEDIUM)
**Problem**: Only 1/31 papers showed citation count
**Impact**: Cannot assess paper impact for reading lists
**Effort**: API integration with Semantic Scholar or OpenCitations
**Priority**: HIGH - Core academic metadata

### 3. Optimize Research Advisor Performance (Impact: HIGH, Effort: HIGH)
**Problem**: 15+ second response, synthesis unavailable
**Impact**: Feature unusable in current state
**Effort**: Requires backend optimization, possibly model caching
**Priority**: HIGH - This should be the tool's differentiator

### 4. Add Code Quality Indicators (Impact: MEDIUM, Effort: MEDIUM)
**Problem**: "Has Code" filter works but no implementation metadata
**Impact**: Can't distinguish official implementations from forks
**Effort**: GitHub API integration for stars/forks/last commit
**Priority**: MEDIUM - Enhances existing feature

### 5. Implement Learning Path Generation (Impact: MEDIUM, Effort: HIGH)
**Problem**: Couldn't test this feature (time constraints)
**Impact**: Could be killer feature for educators
**Effort**: Requires curriculum design algorithm
**Priority**: MEDIUM - High value for pedagogy use case

### 6. Add Citation Network Visualization (Impact: LOW, Effort: HIGH)
**Problem**: Cannot see which papers cite each other
**Impact**: Helps identify paper clusters and foundational work
**Effort**: Graph database + visualization library
**Priority**: LOW - Nice-to-have for advanced users

---

## Screenshots Index

1. `01-landing-first-impression.png` - Initial view of Explore page
2. `02a-nav-generate.png` - Generate page (code generation feature)
3. `03-search-results.png` - Search results for "efficient language models" (31 papers, 7.7s)
4. `03b-research-advisor.png` - Research Advisor mid-processing (timeout state)
5. `05-code-filter.png` - "Has Code" filter applied (31 → 9 papers)
6. `11-second-search.png` - Second search for "knowledge distillation" (31 papers, 2.9s)
7. `12-final-state.png` - Final state at session end

---

## Recommendations for Product Team

### Immediate (Fix before wider release):
1. Fix date parsing - "Invalid Date" is unprofessional
2. Add citation counts to all papers (API integration)
3. Add progress indicator to Research Advisor (set expectations)

### Short-term (Next sprint):
1. Optimize Advisor backend (<5s target)
2. Add GitHub metadata to code filter (stars, last commit)
3. Implement timeout graceful degradation (show partial results)

### Long-term (Product differentiation):
1. Build learning path generator for educators
2. Add citation network visualization
3. Create "seminar builder" feature (reading list export)

---

## Final Assessment

**Overall Rating**: 3/5 (Promising but needs metadata completeness)

**Likelihood to Recommend**: 30% (would wait for citation counts + date fixes)

**Best Use Case**: Exploratory research for experienced researchers who can cross-reference metadata elsewhere

**Worst Use Case**: Curriculum design / reading list creation (missing impact metrics)

**Competitive Position**: Good discovery UX, but Google Scholar still wins on metadata completeness and reliability

---

**Session End**: 2025-12-17 12:07
**Total Screenshots**: 7
**Assessment Completed**: ✓
