# UX Assessment Report: Prof. James Williams
**MIT CSAIL Senior Faculty - NLP Research**
**Date**: December 25, 2025
**Session Duration**: ~25 minutes
**Outcome**: Complete failure - could not accomplish any research goals

---

## Executive Summary

AI Paper Atlas is completely non-functional. The database contains 0 papers, all searches return no results, Discovery pages hang indefinitely, and the Research Advisor times out. I could not find a single paper for my graduate seminar, let alone evaluate pedagogical quality or build a reading list. This tool is not ready for any use.

**Verdict**: Would not use. Would not recommend to students. Would not return.

---

## Session Timeline

| Time | Action | Result | Emotion |
|------|--------|--------|---------|
| 0:00 | Landed on Explore page | Loading state, no value prop | 3/5 Neutral |
| 0:15 | Clicked Discovery nav | "Failed to fetch impact papers" error | 2/5 Frustrated |
| 1:00 | Searched "efficient language models" | 0 results after 10s | 1/5 Very frustrated |
| 2:00 | Tried Research Advisor | Hung at "Searching papers..." indefinitely | 1/5 |
| 3:30 | Clicked "Seminal Papers" filter | Still searching, no results | 1/5 |
| 4:00 | Navigated to Discovery tabs | All tabs stuck "Loading..." | 1/5 |
| 5:00 | Tried Generate page search | Also returned no results | 1/5 |
| 6:00 | Final check | Database shows "0 papers indexed" | 1/5 |

**Average Emotional State**: 1.4/5 (Highly Frustrated)

---

## Critical Findings

### 1. Database Empty (Blocking Issue)
- System reports "0 papers indexed"
- No search returns any results
- No filters work
- Complete data pipeline failure

### 2. Infinite Loading States
- Discovery High Impact: "Failed to fetch"
- Discovery TL;DR: "Loading summaries..." forever
- Discovery Techniques: "Loading techniques..." forever
- Discovery Reproducible: "Finding reproducible papers..." forever
- Explore search: "AI-powered semantic search in progress..." loops indefinitely

### 3. Research Advisor Non-Functional
- Query: "I'm preparing a graduate seminar on efficient language models..."
- Stuck at "Searching papers..." for 15+ seconds
- Had to reload page (Advisor became unresponsive)
- Critical feature completely broken

### 4. No Error Recovery
- No timeout messages
- No fallback states
- No "data unavailable" messaging
- User has no idea if broken or slow

---

## Pain Points Assessment

Could not evaluate ANY pain points because core functionality is broken:

1. **Curation Burden**: ❌ Cannot curate - no papers found
2. **Student Guidance**: ❌ Cannot guide - no recommendations work
3. **Reproducibility Standards**: ❌ Cannot filter by code - database empty
4. **Field Breadth**: ❌ Cannot explore adjacent fields - nothing loads
5. **Historical Context**: ❌ Cannot find foundational work - 0 results

**Success Rate**: 0/5 pain points addressed

---

## Teaching Utility Assessment

**Would this help prepare my graduate seminar?** Absolutely not.

Required capabilities for seminar prep:
- [ ] Find seminal papers (BERT, DistilBERT, etc.) - **FAILED**
- [ ] Identify recent breakthroughs - **FAILED**
- [ ] Create reading progression - **FAILED**
- [ ] Filter by pedagogical value - **FAILED**
- [ ] Check code availability - **FAILED**

The tool cannot accomplish ANY educational task.

---

## Student Recommendation Potential

**Would I recommend to PhD students?** No.

**Would I recommend to master's students?** No.

**Would I mention in class?** No.

**Reasoning**: A broken tool wastes students' limited time. They're better off using Semantic Scholar, Google Scholar, or even just searching arXiv directly. At least those systems return results.

---

## Delights

None. The system is completely non-functional.

---

## Frustrations (Ranked by Impact)

1. **Database empty** - Nothing works without data (CRITICAL)
2. **No error messages** - Infinite loading gives no feedback (HIGH)
3. **Research Advisor timeout** - Core feature totally broken (HIGH)
4. **No graceful degradation** - Every feature fails silently (HIGH)
5. **Wasted time** - 25 minutes with zero results (MEDIUM)

---

## Performance Metrics

- **Search latency**: 10+ seconds before showing "0 results"
- **Page load**: ~1-2s (acceptable)
- **Discovery tabs**: Never complete loading
- **Research Advisor**: Times out after 15+ seconds
- **Database size**: 0 papers (root cause)

---

## Visual Evidence

### Core Failures Documented

1. **Landing Page** (`01-landing-first-impression.png`)
   - Loaded cleanly, but in loading state with skeleton cards

2. **Discovery Error** (`02a-nav-discovery.png`)
   - "Error: Failed to fetch impact papers"

3. **Search Zero Results** (`03b-search-zero-results.png`)
   - "efficient language models" → 0 results in 10020ms

4. **Advisor Timeout** (`03e-advisor-timeout.png`)
   - Stuck "Searching papers..." indefinitely

5. **Seminal Papers Broken** (`06-seminal-papers-zero.png`)
   - Filter active but still searching forever

6. **All Discovery Tabs Broken** (`07-10`)
   - TL;DR: Loading summaries...
   - Techniques: Loading techniques...
   - Reproducible: Finding reproducible papers...

7. **Generate Search Broken** (`12-generate-search-no-results.png`)
   - Even "BERT" returns nothing

8. **Final State** (`13-final-state.png`)
   - "Seminal Papers" filter checked
   - "0 papers" in sidebar
   - Still shows "Searching..." spinner

---

## Priority Improvements

| Priority | Issue | Impact | Effort | Fix |
|----------|-------|--------|--------|-----|
| P0 | Database contains 0 papers | BLOCKS ALL USE | Unknown | Investigate data pipeline |
| P0 | Infinite loading states | BLOCKS ALL FEATURES | Low | Add timeouts + error messages |
| P0 | Research Advisor hangs | BLOCKS CORE FEATURE | Medium | Add timeout + fallback |
| P1 | No error recovery | POOR UX | Low | Show "No papers available" |
| P1 | Discovery tabs all broken | BLOCKS DISCOVERY | Medium | Fix data fetching |
| P2 | No system health indicator | CONFUSING | Low | Add "Papers indexed: X" status |

**Estimated time to basic functionality**: Unknown - depends on root cause of empty database

---

## Screenshots Index

1. `01-landing-first-impression.png` - Explore page, loading state
2. `02a-nav-discovery.png` - Discovery page error
3. `03b-search-zero-results.png` - Search returned 0 results
4. `03c-advisor-opened.png` - Research Advisor panel
5. `03d-advisor-query-entered.png` - Query entered in Advisor
6. `03e-advisor-timeout.png` - Advisor stuck searching
7. `05-reloaded-page.png` - Page reload attempt
8. `06-seminal-papers-zero.png` - Seminal Papers filter broken
9. `07-discovery-loading.png` - Discovery overview loading
10. `08-tldr-loading.png` - TL;DR tab stuck
11. `09-techniques-loading.png` - Techniques tab stuck
12. `10-reproducible-loading.png` - Reproducible tab stuck
13. `11-generate-page.png` - Generate page loaded
14. `12-generate-search-no-results.png` - Generate search failed
15. `13-final-state.png` - Final state showing 0 papers

---

## Comparison to Existing Tools

| Feature | AI Paper Atlas | Semantic Scholar | Google Scholar |
|---------|---------------|------------------|----------------|
| Find papers | ❌ 0 results | ✅ Works | ✅ Works |
| Semantic search | ❌ Broken | ✅ Good | ⚠️ Basic |
| Code filtering | ❌ Broken | ✅ Works | ❌ No |
| Citation data | ❌ No data | ✅ Complete | ✅ Complete |
| Research Advisor | ❌ Timeout | ❌ No | ❌ No |
| Reliability | ❌ 0% | ✅ 99%+ | ✅ 99%+ |

**Conclusion**: Existing tools are infinitely better because they return results.

---

## Final Verdict

**Would I use this for my seminar?** No.

**Would I bookmark this?** No.

**Would I return tomorrow?** No.

**Would I recommend to colleagues?** Absolutely not.

**What frustrated me most?** The complete absence of data. Every feature looks polished but returns nothing. It's like a beautiful library with no books.

**What would make me reconsider?**
1. Fix the database - get papers indexed
2. Add proper error states so users know it's broken
3. Make at least ONE search return results
4. Add a system health check visible to users

**Time wasted**: 25 minutes with zero value delivered.

**Recommendation to developers**: Do not deploy this. Fix the data pipeline first. No amount of UI polish matters if the database is empty. Check `/api/v1/papers/count` or equivalent - something is fundamentally broken at the data layer.

---

## Academic Context

As a professor who has reviewed hundreds of research tools, this is the worst failure mode: **silent data absence**. The interface suggests capability but delivers nothing. This is worse than a simple error page because it wastes the user's time.

For graduate education, reliability trumps features. A simple working search is worth more than ten broken "AI-powered" features. Semantic Scholar may lack sophistication, but it works consistently.

**Grade**: F (non-functional)
**Retest required**: After database is populated

---

**End of Assessment**
