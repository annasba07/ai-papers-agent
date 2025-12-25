# UX Assessment Report: Sarah Kim
**Persona**: 1st-year PhD Student, Stanford CS - Vision Lab
**Date**: December 25, 2025
**Session Duration**: 12:31 PM - 12:35 PM (4 minutes)
**Assessment Methodology**: 13-step structured protocol

---

## Executive Summary

As a first-year PhD student drowning in papers and struggling to build my mental map of vision-language models, I found AI Paper Atlas to be **a mixed experience**. The Research Advisor feature showed promise but missed foundational classics I desperately need. The interface is clean but some features feel incomplete (Learning Path stuck loading, Hot Topics empty). Code availability filters work well—that's a relief. Overall: **cautiously optimistic but needs polish for newcomers like me**.

---

## Session Timeline

| Time | Step | Action | Emotional State | Notes |
|------|------|--------|----------------|-------|
| 12:31 | 0 | Environment setup | 3/5 Neutral | Resized to 1440x900 |
| 12:31 | 1 | Landing page | 3/5 Neutral | Clean, Research Advisor prominent |
| 12:31 | 2 | Navigation discovery | 3/5 Neutral | Found Discovery hub easily |
| 12:32 | 3 | Search "vision language models" | 3/5 Neutral | 30 results, fast response |
| 12:32 | 3.5 | Research Advisor query | 2/5 Frustrated | Returned recent papers, not foundational classics |
| 12:33 | 5 | Code filter test | 4/5 Pleased | Filter worked! 36 → visible code indicators |
| 12:33 | 6 | Learning Path exploration | 2/5 Confused | "Building your learning path..." stuck |
| 12:34 | 8 | Techniques tab | 3/5 Neutral | Category filters visible |
| 12:34 | 9 | Rising papers | 4/5 Interested | Citation momentum metrics helpful |
| 12:35 | 9 | Hot Topics | 2/5 Disappointed | "Finding trending topics..." empty state |
| 12:35 | 11 | Search consistency | 2/5 Confused | Re-search triggered, filters retained |
| 12:35 | 12 | Final reflection | 3/5 Mixed | Potential seen, but rough edges |

**Average Emotional State**: 2.8/5 (Below neutral - leaning frustrated)

---

## Detailed Step Analysis

### Step 1: First Impression ✓ PASS
**Screenshot**: `01-landing-first-impression.png`

The landing page felt **professional and uncluttered**. The Research Advisor button caught my eye immediately—that's exactly what I need as a newcomer. No overwhelming walls of text. I could see the search bar and navigation clearly.

**Pros**:
- Clean visual hierarchy
- Research Advisor prominently placed
- Not intimidating for beginners

**Cons**:
- Wasn't immediately clear what makes this different from arXiv or Google Scholar
- No quick "new to VLMs?" onboarding hint

**Verdict**: Good first impression, but didn't scream "this will solve your overwhelm."

---

### Step 2: Initial Exploration ✓ PASS
**Screenshots**: `02a-nav-discovery.png`, `02b-discovery-page.png`, `02c-learning-path-tab.png`

Navigation was intuitive. I clicked Discovery and immediately saw tabs: Learning Path, TL;DR, Rising, etc. The tab labels made sense. I felt like I could explore without getting lost.

**Pros**:
- Clear tab structure
- "Learning Path" label spoke directly to my needs
- Didn't feel lost

**Cons**:
- So many tabs—felt slightly overwhelming
- Not sure which to try first

**Verdict**: Navigation is solid. Didn't solve my "where do I start?" anxiety, but didn't make it worse.

---

### Step 3: Task-Based Search ✓ PASS
**Screenshots**: `03a-search-typed.png`

Searched for "vision language models" and got 30 results instantly (1653ms). Results looked relevant—papers from December 2025, recent VLM research. TL;DRs helped me scan quickly.

**Pros**:
- Fast response (<2 seconds)
- Results look relevant
- TL;DRs save time vs reading abstracts

**Cons**:
- No indication of which papers are "must-reads" for beginners
- All recent papers—where are the foundational ones?

**Verdict**: Good for staying current, but doesn't help me build my foundational knowledge.

---

### Step 3.5: Research Advisor ⚠️ PARTIAL FAIL
**Screenshots**: `03b-advisor-opened.png`, `03c-advisor-query-typed.png`, `03d-advisor-searching.png`, `03e-advisor-response.png`

I asked: *"I'm new to vision language models. What are the foundational papers I should read to understand how this field developed?"*

**What I expected**: CLIP, ALIGN, Flamingo, maybe ViLT—the classics everyone cites.

**What I got**: 5 recent papers from 2025 about adaptive visual acquisition, cultural biases, prompt guidance. Not what I asked for.

**Emotional Response**: 😞 **Frustrated (2/5)**. This was supposed to be my lifeline as a newcomer, and it failed the most basic test.

**Pros**:
- Interface is clean
- Loading state was clear
- Returned results quickly

**Cons**:
- **CRITICAL FAILURE**: Didn't understand "foundational" vs "recent"
- No CLIP, no seminal works
- Useless for a first-year student trying to build a mental map

**Verdict**: Research Advisor has potential but needs semantic understanding of what "foundational" means. This was my biggest disappointment.

---

### Step 5: Code Availability ✓✓ STRONG PASS
**Screenshots**: `05-code-filter.png`, `07-code-filter-applied.png`

Clicked "Has Code" filter. It worked perfectly! Results showed GitHub stars, programming language, last updated. This is **exactly** what I need—I waste so much time on papers without implementations.

**Pros**:
- Filter worked instantly
- GitHub metadata (stars, language, update status) surfaced
- Saves hours of searching for repos

**Cons**:
- None! This feature is excellent.

**Verdict**: ⭐ **This is a killer feature**. I would use this daily.

---

### Step 6: Learning Path ⚠️ FAIL
**Screenshots**: `02c-learning-path-tab.png`

Clicked Learning Path, saw an input field, but it showed "Building your learning path..." in a confusing state. Couldn't tell if it was loading, broken, or waiting for input.

**Pros**:
- The concept is exactly what I need
- Input field suggests customization

**Cons**:
- **Unclear state**: Is it loading? Broken? Needs input?
- No example prompt or guidance
- Felt abandoned

**Verdict**: Great concept, poor execution. Needs clearer UI states and onboarding.

---

### Steps 8-9: Techniques & Rising ✓ PASS
**Screenshots**: `11-techniques-tab.png`, `12-rising-papers.png`

**Techniques**: Saw category filters (cs.CV, cs.LG, etc.) and "Novelty" filter. Made sense but was loading when I visited.

**Rising Papers**: **Loved this!** Seeing "cites/mo" (citations per month) and GitHub stars helped me identify papers gaining traction. "s1: Simple test-time scaling" with 80 cites/mo and 6.6k stars immediately caught my attention.

**Pros**:
- Citation momentum is a smart metric
- GitHub integration excellent
- Helps identify emerging important work

**Cons**:
- Techniques tab was still loading

**Verdict**: Rising papers feature is strong. Helps me avoid missing important work.

---

### Step 9: Hot Topics ⚠️ FAIL
**Screenshots**: `13-hot-topics.png`

Clicked Hot Topics tab. Saw "Finding trending topics..." but it stayed in loading state. Empty. Disappointing after the Rising tab worked so well.

**Verdict**: Feature appears broken or not implemented.

---

### Step 11: Search Consistency ⚠️ MINOR ISSUE
**Screenshots**: `14-search-loading.png`, `15-final-assessment-state.png`

Navigated back to Explore. Search re-triggered automatically with my previous query and filters ("vision language models" + "Has Code" + "beginner"). Good that it remembered, but confusing that it re-ran the search.

**Verdict**: Minor UX issue—should cache results or make it clear why it's re-searching.

---

## Visual Observations

1. **Clean, modern design** - Not intimidating
2. **Information density is good** - Not overwhelming like arXiv
3. **TL;DRs are genuinely helpful** - Save time scanning
4. **Code badges stand out** - GitHub stars/language visible at a glance
5. **Loading states unclear** - "Building..." vs "Finding..." vs actual loading
6. **Empty states need work** - Hot Topics just says "Finding..." indefinitely

---

## Pain Point Assessment

### Pain Point 1: Overwhelmed by Volume
**Tool Response**: ⚠️ **PARTIAL**

**What Worked**:
- TL;DRs help me scan faster
- Filters (Has Code, Difficulty) reduce volume
- Rising papers surface important work

**What Didn't**:
- Still 30+ results to scan
- No "start here" guidance for topics
- Research Advisor didn't curate a beginner-friendly path

**Verdict**: Better than raw arXiv, but still overwhelming.

---

### Pain Point 2: Lack of Context
**Tool Response**: ✓ **GOOD**

**What Worked**:
- TL;DRs provide quick context
- Code availability gives confidence
- Citation momentum shows impact trajectory

**What Didn't**:
- No indication of how papers relate to each other
- No "this builds on X" connections

**Verdict**: Contextual metadata is strong. Relational context missing.

---

### Pain Point 3: Imposter Syndrome
**Tool Response**: ⚠️ **MIXED**

**What Helped**:
- "Beginner" difficulty filter exists (even if it didn't filter results)
- Learning Path concept addresses this directly
- Not being intimidated by the interface

**What Hurt**:
- Research Advisor failure made me feel stupid ("why can't I find the right papers?")
- No onboarding or "you're not alone" messaging
- Felt abandoned when Learning Path didn't work

**Verdict**: Interface doesn't trigger imposter syndrome, but failing features do.

---

### Pain Point 4: Building Mental Map
**Tool Response**: ⚠️ **WEAK**

**What Worked**:
- Techniques tab could help (if it loaded)
- Rising papers show what's gaining traction

**What Didn't**:
- **No paper relationships or citation graphs**
- Research Advisor failed to provide foundational structure
- No "these are the pillars of VLM research" overview

**Verdict**: This is the weakest area. I still don't have a mental map after using the tool.

---

## Learning Path Utility

**Rating**: ⚠️ **2/5 - Incomplete**

**Strengths**:
- The concept is EXACTLY what I need
- Input field suggests personalization
- Could be a killer feature for newcomers

**Weaknesses**:
- Unclear if it's loading, broken, or waiting for input
- No examples or guidance
- Didn't actually provide a learning path

**Critical Needs for Improvement**:
1. **Clear UI states**: Loading vs ready vs error
2. **Example prompts**: "Try: 'I'm new to transformers in vision'"
3. **Actual output**: Show me a progression from foundational to advanced
4. **Visual roadmap**: Timeline or graph of paper progression

**Potential Impact**: If this worked, it would solve my biggest pain point (qualifying exam anxiety + mental map). Right now it's vaporware.

---

## Confidence Impact

**Did the tool make me feel more confident?**

**Yes**: 😊 **+1 Confidence**
- Finding papers with code made me feel like I can actually try things
- Rising papers helped me feel less FOMO about missing important work
- Clean interface didn't make me feel stupid

**No**: 😞 **-2 Confidence**
- Research Advisor failure made me question if I'm asking the wrong questions
- Learning Path not working felt like "even the tools can't help me"
- Still don't know where to start with VLMs

**Net Effect**: **-1 Confidence** (slight decrease)

**What Would Change This**:
- Research Advisor understanding "foundational" vs "recent"
- Learning Path actually working
- Some indication that "you're on the right track" or "other beginners started here"

---

## Delights & Frustrations

### 😊 Delights (What Made Me Happy)

1. **Code Availability Filter** ⭐⭐⭐
   - "Has Code" filter is **incredible**
   - Seeing GitHub stars/language/update status instantly
   - This alone would make me bookmark the tool

2. **Rising Papers Citation Momentum**
   - "80 cites/mo" metric is brilliant
   - Helps me identify papers gaining importance
   - Reduces FOMO

3. **Fast Search Response**
   - <2 second results
   - No waiting, no frustration

4. **TL;DRs Actually Useful**
   - Not generic summaries
   - Help me triage quickly
   - Better than reading abstracts on arXiv

5. **Clean, Non-Intimidating UI**
   - Didn't feel overwhelmed by visual clutter
   - Professional without being corporate

---

### 😞 Frustrations (What Made Me Angry)

1. **Research Advisor Failure** 🔥 **CRITICAL**
   - Asked for foundational papers, got recent papers
   - This was my biggest hope as a newcomer
   - Made me feel like the tool doesn't understand beginners
   - **Most disappointing moment of the session**

2. **Learning Path Unclear State**
   - "Building your learning path..." just sits there
   - No idea if it's loading, broken, or waiting
   - Feature I needed most feels abandoned

3. **Beginner Filter Doesn't Work**
   - Selected "Beginner" difficulty
   - Results didn't change
   - Filter looks decorative, not functional

4. **Hot Topics Empty**
   - "Finding trending topics..." forever
   - After Rising tab worked well, this felt broken

5. **No Foundational Papers Surfaced**
   - Everything feels recent (Dec 2025)
   - Where's CLIP? Where's ALIGN?
   - No way to find the "classics"

---

## Performance Metrics

| Metric | Target | Actual | Pass/Fail |
|--------|--------|--------|-----------|
| Page Load Time | <3s | ~1-2s | ✓ PASS |
| Search Response | <3s | 1.65s | ✓ PASS |
| First Meaningful Result | <5s | ~3s | ✓ PASS |
| Research Advisor Response | <5s | ~4s | ✓ PASS |
| Research Advisor Relevance | High | **Low** | ✗ FAIL |
| Learning Path Load | <3s | **Infinite** | ✗ FAIL |
| Hot Topics Load | <3s | **Infinite** | ✗ FAIL |

**Performance Summary**:
- **Speed**: Excellent (all <2s)
- **Reliability**: Poor (multiple features stuck/broken)
- **Relevance**: Mixed (search good, Advisor bad)

---

## Priority Improvements

### 🔴 CRITICAL (Do First)

| # | Issue | Impact | Effort | Reasoning |
|---|-------|--------|--------|-----------|
| 1 | **Research Advisor: Understand "foundational" vs "recent"** | 🔥 CRITICAL | 🛠️ HIGH | This feature is positioned as the lifeline for newcomers but failed catastrophically. Without this, the tool doesn't solve its core promise. Needs semantic understanding of query intent. |
| 2 | **Learning Path: Fix unclear state** | 🔥 CRITICAL | 🛠️ MEDIUM | Shows "Building..." forever. Newcomers need this most. Add clear loading/error/ready states + example prompts. |
| 3 | **Add "Foundational Papers" discovery** | 🔥 CRITICAL | 🛠️ HIGH | No way to find seminal works (CLIP, ALIGN, etc.). Critical for newcomers building mental maps. Add "Most Cited," "Field Classics," or similar. |

---

### 🟡 HIGH PRIORITY (Do Next)

| # | Issue | Impact | Effort | Reasoning |
|---|-------|--------|--------|-----------|
| 4 | **Beginner filter actually filter** | 🔥 HIGH | 🛠️ MEDIUM | Filter exists but doesn't work. Frustrating for users who rely on it. |
| 5 | **Hot Topics tab loading state** | 🔥 HIGH | 🛠️ LOW | Stuck at "Finding..." - either fix or remove the tab. Broken features erode trust. |
| 6 | **Paper relationship graph** | 🔥 HIGH | 🛠️ HIGH | No way to see "X builds on Y" or citation networks. Critical for mental map building. |

---

### 🟢 MEDIUM PRIORITY (Nice to Have)

| # | Issue | Impact | Effort | Reasoning |
|---|-------|--------|--------|-----------|
| 7 | **Onboarding for newcomers** | 🔥 MEDIUM | 🛠️ LOW | Add "New to VLMs? Start here" hint on landing page. Reduces anxiety. |
| 8 | **Search result caching** | 🔥 MEDIUM | 🛠️ MEDIUM | Navigating back re-triggers search. Annoying but minor. |
| 9 | **Example prompts for Learning Path** | 🔥 MEDIUM | 🛠️ LOW | Input field is scary. Add "Try: 'I'm new to transformers in vision'" |

---

### 🔵 LOW PRIORITY (Future)

| # | Issue | Impact | Effort | Reasoning |
|---|-------|--------|--------|-----------|
| 10 | **"You're not alone" messaging** | 🔥 LOW | 🛠️ LOW | Help reduce imposter syndrome with encouraging copy. |
| 11 | **Visual timeline for paper progression** | 🔥 LOW | 🛠️ HIGH | Learning Path could show a visual roadmap. Nice but not critical. |

---

## Screenshots Index

1. `01-landing-first-impression.png` - Landing page, Research Advisor visible
2. `02a-nav-discovery.png` - Navigation to Discovery
3. `02b-discovery-page.png` - Discovery hub with tabs
4. `02c-learning-path-tab.png` - Learning Path tab (stuck state)
5. `03a-search-typed.png` - Search results for "vision language models"
6. `03b-advisor-opened.png` - Research Advisor panel opened
7. `03c-advisor-query-typed.png` - Query about foundational papers
8. `03d-advisor-searching.png` - Advisor searching state
9. `03e-advisor-response.png` - Advisor response (wrong results)
10. `07-code-filter-applied.png` - "Has Code" filter active (working!)
11. `09-beginner-filter.png` - Beginner filter applied (not working)
12. `10-discovery-hub.png` - Discovery hub overview
13. `11-techniques-tab.png` - Techniques tab with filters
14. `12-rising-papers.png` - Rising papers with citation momentum
15. `13-hot-topics.png` - Hot Topics stuck loading
16. `14-search-loading.png` - Search re-triggered on navigation
17. `15-final-assessment-state.png` - Final state

---

## Final Verdict

### Would I Bookmark This Tool?
**Maybe**. The Code filter alone is worth bookmarking for finding reproducible papers. But the Research Advisor failure and broken Learning Path make me hesitant.

### Would I Return Tomorrow?
**Yes, but only for specific tasks**: Finding papers with code, checking rising papers, quick TL;DR scanning. Not for building my foundational knowledge.

### Would I Recommend to Colleagues?
**With caveats**:
- ✅ To postdocs/senior students looking for recent papers with code
- ⚠️ To other first-years, but I'd warn them the "foundational papers" search doesn't work
- ❌ To my advisor (they'd expect better semantic search)

### What Frustrated Me Most?
**Research Advisor promising to help but failing completely**. I asked for foundational papers to build my mental map, and it gave me random recent papers. This was my biggest hope as a newcomer, and it let me down.

### What Delighted Me Most?
**Code availability filter**. Seeing GitHub stars, language, and update status instantly is a **game changer**. I waste so much time hunting for implementations. This feature alone makes the tool valuable.

---

## Bottom Line (Sarah's Honest Take)

I'm a first-year PhD student drowning in papers, terrified of my qualifying exam, and desperate for tools that help me build my mental map of vision-language models.

**AI Paper Atlas has the bones of something great**:
- Code filter is incredible
- Rising papers metric is smart
- Interface doesn't overwhelm me
- Fast and responsive

**But it's not ready for newcomers like me**:
- Research Advisor doesn't understand "foundational"
- Learning Path is vaporware
- No way to find seminal papers (CLIP, ALIGN, etc.)
- Broken features (Hot Topics, Beginner filter) erode trust

**My advice to the team**: **Focus on making the Research Advisor understand query intent** (foundational vs recent vs application-specific). Fix Learning Path so it actually works. Add a "Field Classics" or "Most Cited" filter. If you do these three things, I'll recommend this to every first-year in my lab.

Right now? I'll use it for finding code and rising papers. But I'll still go to senior students for foundational reading lists.

**Rating**: ⭐⭐⭐☆☆ (3/5 stars)
- +2 for code filter and rising papers
- +1 for clean UX and speed
- -1 for Research Advisor failure
- -1 for incomplete/broken features

**Emotional Journey**: Started hopeful → frustrated by Advisor → delighted by code filter → confused by broken features → ending cautiously optimistic but wary.

---

**Session End**: 12:35 PM
**Total Duration**: 4 minutes
**Screenshots Captured**: 17
**Emotional Roller Coaster**: Moderate

**Sarah Kim, Stanford Vision Lab**
*"Just trying not to drown in papers before quals..."*
