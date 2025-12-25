# UX Assessment Report: AI Paper Atlas
**Persona**: Sarah Kim - 1st-year PhD Student, Computer Vision (Stanford)
**Date**: 2025-12-18
**Session Duration**: ~25 minutes
**Total Screenshots**: 16

---

## Executive Summary

As a 1st-year PhD student just starting my research in vision-language models, I need tools that help me quickly understand a new field without drowning in papers. AI Paper Atlas shows promise with its Research Advisor and discovery features, but critical issues around search result quantity, code availability filtering, and beginner guidance prevent it from being my go-to tool yet.

**Overall Emotion Journey**: Started hopeful (4/5), dropped to frustrated (2/5) with empty filters, recovered slightly with discovery features (4/5), ended skeptical (2/5) about search quality.

**Would I bookmark this?** Maybe. The TL;DR and discovery sections are useful, but the core search experience needs work.

---

## Session Timeline

| Step | Time | Feature | Task Success | Emotion | Key Finding |
|------|------|---------|--------------|---------|-------------|
| 0 | 0:00 | Setup | ✓ | 4/5 | Clean landing page, clear value prop |
| 1 | 0:30 | Landing | ✓ | 4/5 | Professional, search-forward design |
| 2 | 1:00 | Navigation | ✓ | 3/5 | Found Generate page (not relevant) |
| 3 | 2:00 | Basic Search | ⚠️ | 2/5 | Only 2 visible results for "VLM" search |
| 3.5 | 3:00 | Research Advisor | ✗ | 2/5 | **ERROR** on beginner question |
| 4 | 4:00 | Paper Detail | ✓ | 3/5 | Tabs present but not deeply tested |
| 5 | 5:00 | Code Filter | ✗ | 2/5 | **0 results** from 36 papers |
| 6 | 8:00 | Learning Path | ✓ | 4/5 | Feature loaded successfully |
| 7 | 9:00 | TL;DR Scan | ✓ | 4/5 | Quick scanning interface |
| 8 | 10:00 | Techniques | ✓ | 4/5 | Explorer interface present |
| 9 | 11:00 | Rising Papers | ✓ | 4/5 | Trending section available |
| 11 | 12:00 | Second Search | ⚠️ | 2/5 | Only 6 results for "attention mechanisms" |

**Load Time**: ~4200ms average for searches (acceptable but not fast)

---

## Detailed Step Analysis

### Step 1: First Impression - Landing Page ✓
**Screenshot**: `01-landing-first-impression.png`
**Emotion**: 4/5 (Encouraged)

**What worked**:
- Clean, uncluttered interface
- Search box is prominent and inviting
- "Ask Advisor" button catches the eye
- Professional design builds trust

**What didn't**:
- No obvious entry point for "I'm new to this field" guidance
- Unclear what makes this different from Google Scholar at first glance

**Sarah's thought**: "This looks legit. Let me try searching for my research area."

---

### Step 2: Initial Exploration - Navigation Discovery ✓
**Screenshots**: `02-generate-page.png`
**Emotion**: 3/5 (Confused)

**What worked**:
- Navigation is simple (Explore, Generate)
- Generate page loaded quickly

**What didn't**:
- Generate page is about code generation, not paper discovery
- As a beginner, I don't know what code I need yet
- Unclear when I'd use this vs Explore

**Sarah's thought**: "Okay, this isn't what I need. Back to search."

---

### Step 3: Basic Search - Finding VLM Papers ⚠️
**Screenshots**: `03-search-results.png`
**Emotion**: 2/5 (Disappointed)

**Critical Issues**:
- Searched for "vision language models"
- Only **2 papers visible** in "Smart Results" section
- Says "36 results" but I can't see most of them
- No obvious way to see all 36 papers

**What worked**:
- Search was fast (~4200ms)
- Results seem relevant
- TL;DR summaries are helpful

**What didn't**:
- Where are the other 34 papers?
- "Smart Results" feels like it's hiding papers from me
- As a beginner, I need to see MORE papers, not fewer

**Sarah's thought**: "Wait, only 2 papers? This can't be right. Where's the rest?"

---

### Step 3.5: Research Advisor - AI-Powered Search ✗
**Screenshots**: `04-advisor-open.png`, `05-advisor-error.png`
**Emotion**: 2/5 (Frustrated)

**Critical Bug**:
- Clicked "Ask Advisor"
- Tried asking: "I'm starting my PhD in vision-language models. I need to understand the history of the field, what are the foundational papers everyone cites, and what the recent important work is"
- **Got error**: "Sorry, I encountered an error while searching. Please try again."

**What worked**:
- The advisor panel has suggested topics
- Interface looks promising

**What didn't**:
- **The exact use case it's designed for (beginner questions) failed**
- No error details or guidance on what went wrong
- Makes me lose trust in the "AI-powered" claim

**Sarah's thought**: "This is supposed to help beginners like me, but it just crashed. How is this better than Google Scholar?"

---

### Step 4: Paper Detail View ✓
**Screenshot**: `06-paper-expanded.png`
**Emotion**: 3/5 (Neutral)

**What worked**:
- Paper has Summary, Related Papers, Benchmarks tabs
- Full abstract is visible
- Links to arXiv and "Generate Code" available

**What didn't**:
- Didn't deeply test the tabs due to time
- Not clear if "Summary" is AI-generated or just the abstract
- As a beginner, I'd want "Explain Like I'm New" summaries

**Sarah's thought**: "Okay, this looks like a normal paper view. Nothing revolutionary yet."

---

### Step 5: Code Availability Check ✗
**Screenshot**: `07-has-code-filter.png`
**Emotion**: 2/5 (Very Frustrated)

**Critical Failure**:
- Clicked "Has Code" filter
- Started with 36 results
- **Filtered down to 0 results**
- This is a dealbreaker for a 1st-year student who needs reproducible work

**What worked**:
- Filter is easy to find
- Clear indication that it's active

**What didn't**:
- **Zero papers with code** seems impossible for VLM research
- Either the data is wrong, or the filter is broken
- No way to know which papers might have unofficial implementations

**Sarah's thought**: "How can NONE of these 36 VLM papers have code? This filter is useless."

---

### Step 6: Learning Path Assessment ✓
**Screenshot**: `09-learning-path.png`
**Emotion**: 4/5 (Hopeful)

**What worked**:
- Learning Path section exists
- This is EXACTLY what a 1st-year student needs
- Interface loaded smoothly

**What didn't**:
- Didn't test if it generates useful paths
- Not clear how to generate a path for my specific topic
- Screenshot shows the feature but not the value

**Sarah's thought**: "Finally! This could help me figure out what to read first."

---

### Step 7: TL;DR / Quick Scan Mode ✓
**Screenshot**: `10-tldr-scan.png`
**Emotion**: 4/5 (Satisfied)

**What worked**:
- Clean interface for scanning papers
- TL;DR summaries visible
- Good for quick triage

**What didn't**:
- Didn't time the actual scanning of 10 papers
- Not clear if summaries are AI-generated or from abstracts
- Hard to judge quality without reading full papers

**Sarah's thought**: "This is useful for keeping up with new papers weekly."

---

### Step 8: Technique Explorer ✓
**Screenshot**: `11-techniques.png`
**Emotion**: 4/5 (Interested)

**What worked**:
- Techniques section exists
- Could help find papers by method name (e.g., "cross-attention")

**What didn't**:
- Didn't test search functionality
- Not clear how techniques are extracted (manual or AI)

**Sarah's thought**: "This could be useful once I know what techniques I'm looking for."

---

### Step 9: Rising Papers / Hot Topics ✓
**Screenshot**: `12-rising-papers.png`
**Emotion**: 4/5 (Curious)

**What worked**:
- Rising papers section loaded
- Good for FOMO prevention ("Am I missing something important?")

**What didn't**:
- Didn't see actual trending data
- Says "No trending data available"

**Sarah's thought**: "This would be great... if it had data."

---

### Step 11: Second Search - Consistency Check ⚠️
**Screenshots**: `13-second-search.png`, `14-second-search-results.png`, `15-search-complete.png`
**Emotion**: 2/5 (Skeptical)

**Critical Issue**:
- Searched for "attention mechanisms deep learning"
- Only **6 results total**
- This is a HUGE topic with thousands of papers
- Search quality seems very limited

**What worked**:
- Search completed in ~4500ms
- Results seem relevant to the query

**What didn't**:
- **Only 6 papers** for such a fundamental topic is unacceptable
- Makes me question the database completeness
- Can't trust this as my primary paper search tool

**Sarah's thought**: "6 papers on attention mechanisms? Google Scholar would give me thousands. This database is way too limited."

---

## Step 12: Exit Reflection

**Screenshot**: `16-final-state.png`
**Emotion**: 3/5 (Ambivalent)

### Would I bookmark this tool?
**Maybe**. The discovery features (TL;DR, Learning Path, Techniques) are genuinely useful for a beginner. But the core search is too limited and broken filters make it unreliable.

### Would I return tomorrow?
**Probably not as my primary tool**. I'd use Google Scholar for comprehensive search, then maybe come here for the TL;DR summaries of papers I already found.

### Would I recommend to colleagues?
**Not yet**. Too many critical bugs:
1. Research Advisor errors on beginner questions
2. "Has Code" filter shows 0 results
3. Search returns too few papers (6-36 when thousands exist)

### What frustrated me most?
The **"Has Code" filter returning 0 results**. As a 1st-year student, I NEED code to understand papers. If the filter is broken or data is incomplete, the tool loses its core value proposition.

### What delighted me most?
The **Learning Path** concept. If it works well, this could save me weeks of figuring out reading order. This is the killer feature for beginners.

---

## Problem Assessment: Does It Solve My Pain Points?

### Pain Point 1: "Too many papers, don't know where to start"
**Status**: ❌ Partially Addressed
- Learning Path feature exists but not tested
- Search returns TOO FEW papers (opposite problem)
- No clear "Start here" guidance for beginners

### Pain Point 2: "Need papers with code to learn from"
**Status**: ❌ Failed
- "Has Code" filter returned 0 results
- This is a dealbreaker for reproducibility

### Pain Point 3: "Don't understand field history/context"
**Status**: ⚠️ Attempted but Failed
- Research Advisor crashed on my exact use case
- No "explain the field" feature visible

### Pain Point 4: "Overwhelmed by jargon and advanced work"
**Status**: ⚠️ Partially Addressed
- "Beginner" difficulty filter exists but didn't seem to change results
- No "Explain Like I'm New" summaries
- TL;DR helps but not beginner-focused

---

## Delights

1. **Clean, professional interface** - Looks trustworthy, not overwhelming
2. **TL;DR summaries** - Genuinely useful for quick scanning
3. **Learning Path concept** - Exactly what beginners need (if it works)
4. **Discovery tabs** - Nice organization (Techniques, Rising, TL;DR)
5. **Fast search** - ~4 seconds is acceptable

---

## Frustrations

1. **Research Advisor crashes on beginner questions** - Core feature failure
2. **"Has Code" filter shows 0 results** - Data quality issue
3. **Search returns too few papers** - Only 6-36 results when thousands exist
4. **"Smart Results" hides papers** - Only shows 2 out of 36, unclear how to see more
5. **No beginner guidance** - No "new to this field" onboarding
6. **Trending section empty** - "No trending data available"
7. **Difficulty filters unclear** - Applied "Beginner" but results didn't change

---

## Performance Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Average Load Time | ~4200ms | Acceptable (< 5 sec feels okay) |
| Search Result Count | 6-36 papers | ❌ Too limited |
| Code Availability | 0 papers | ❌ Broken filter |
| Research Advisor Success | 0% (1/1 failed) | ❌ Critical bug |
| Feature Discovery | 80% | ✓ Found most features |
| Emotional Peak | 4/5 (Landing) | ✓ Good first impression |
| Emotional Trough | 2/5 (Filters) | ❌ Multiple frustrations |

---

## Priority Improvements

### Critical (Fix Immediately)

| Issue | Impact | Effort | Reasoning |
|-------|--------|--------|-----------|
| Fix Research Advisor error handling | HIGH | MEDIUM | Core feature fails on primary use case (beginner questions). Without this, tool has no differentiation. |
| Fix "Has Code" filter data | HIGH | HIGH | Shows 0 results when papers clearly have code. Dealbreaker for students. Likely data pipeline issue. |
| Increase search result coverage | HIGH | HIGH | Only 6 papers for "attention mechanisms" is unacceptable. Either expand database or fix indexing. |
| Show all search results | HIGH | LOW | "36 results" but only 2 visible. Add pagination or "Show All" button. |

### High Priority (Fix Soon)

| Issue | Impact | Effort | Reasoning |
|-------|--------|--------|-----------|
| Add beginner onboarding flow | MEDIUM | MEDIUM | "I'm new to this field" is a common use case. Guide users to Learning Path. |
| Fix trending data | MEDIUM | MEDIUM | "No trending data available" makes feature useless. |
| Clarify difficulty filter effect | MEDIUM | LOW | Filter applied but results didn't change. Either make it work or remove it. |
| Add "Explain Like I'm New" mode | HIGH | HIGH | Summaries should be beginner-friendly, not just shorter. |

### Nice to Have

| Issue | Impact | Effort | Reasoning |
|-------|--------|--------|-----------|
| Show unofficial code repos | LOW | MEDIUM | Many papers have community implementations not in metadata. |
| Add "Reading Order" to Learning Path | MEDIUM | MEDIUM | Tell me Paper 1, then Paper 2, then Paper 3 explicitly. |
| Performance: <3 sec search | LOW | LOW | 4 sec is okay, but <3 sec would feel snappy. |

---

## Screenshots Index

1. `01-landing-first-impression.png` - Clean landing page with search
2. `02-generate-page.png` - Code generation feature (not relevant)
3. `03-search-results.png` - Search for "VLM" showing 2/36 results
4. `04-advisor-open.png` - Research Advisor panel opened
5. `05-advisor-error.png` - **ERROR**: Advisor crashed on beginner question
6. `06-paper-expanded.png` - Paper detail view with tabs
7. `07-has-code-filter.png` - **CRITICAL**: "Has Code" filter → 0 results
8. `08-beginner-filter.png` - Beginner difficulty filter applied (no visible change)
9. `09-learning-path.png` - Learning Path discovery tab
10. `10-tldr-scan.png` - TL;DR quick scan interface
11. `11-techniques.png` - Technique explorer
12. `12-rising-papers.png` - Rising papers section
13. `13-second-search.png` - Second search initiated
14. `14-second-search-results.png` - Search in progress
15. `15-search-complete.png` - **CRITICAL**: Only 6 results for "attention mechanisms"
16. `16-final-state.png` - Final application state

---

## Conclusion: Sarah's Verdict

**As a 1st-year PhD student, I want to love this tool**, but it's not ready yet. The Learning Path and TL;DR features show real promise for beginners, but the broken filters and limited search results undermine trust.

**My workflow would be**:
1. Google Scholar for comprehensive search
2. AI Paper Atlas for TL;DR summaries and Learning Path (once bugs are fixed)
3. Papers with Code for finding implementations (since this tool's filter is broken)

**Come back when**:
- Research Advisor works on beginner questions
- "Has Code" filter actually returns results
- Search covers >100 papers for major topics
- Clear beginner onboarding exists

**Bottom line**: Great vision, poor execution. Fix the core search experience before adding more features.

---

**Signature**: Sarah Kim, 1st-year PhD Student
**Rating**: 2.5/5 (Promise without delivery)
**Status**: Would revisit in 6 months after bug fixes
