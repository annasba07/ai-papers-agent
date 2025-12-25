# UX Assessment Report: Dr. Maya Chen
**Persona**: 2nd-year Postdoc, CMU Machine Learning Department
**Research Focus**: Efficient transformers for edge/mobile deployment
**Date**: December 18, 2025
**Session Duration**: ~15 minutes
**Assessment Tool**: AI Paper Atlas (localhost:3000)

---

## Executive Summary

AI Paper Atlas shows promise for finding mobile/edge ML papers but suffers from critical reliability issues. The semantic search worked when I searched for specific techniques ("flash attention"), finding 27 relevant papers including Block Sparse Flash Attention and GatedFWA. However, the Research Advisor feature failed with errors, trending data was unavailable, and initial generic searches returned irrelevant results. The tool saved me time on targeted searches but I can't rely on it as my primary discovery tool yet.

---

## Session Timeline & Metrics

| Step | Action | Time | Emotion (1-5) | Success |
|------|--------|------|---------------|---------|
| 1 | Landing page load | ~2s | 3 | ✓ Clean interface |
| 2 | Navigate Explore/Generate | ~3s | 3 | ✓ Basic navigation clear |
| 3a | Search "efficient attention..." | 8040ms | 2 | ✗ Returned CV papers, not attention |
| 3b | Open Research Advisor | instant | 4 | ✓ Panel opened smoothly |
| 3c | Submit advisor query | ~2s | 2 | ✗ Error: "encountered an error" |
| 4 | Expand paper detail | instant | 4 | ✓ Full abstract, tabs visible |
| 5 | Apply "Has Code" filter | instant | 3 | ? Still showed 6 results, unclear if working |
| 6 | Check trending section | instant | 2 | ✗ "No trending data available" |
| 7 | Search "flash attention" | 4232ms | 4 | ✓ 27 relevant results! |

**Total productive time**: ~10 minutes
**Papers found**: 2 highly relevant (Block Sparse Flash Attention, GatedFWA)
**Blockers encountered**: 2 (Advisor error, no trending data)

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

**Visual observations**:
- Clean, professional interface with prominent search bar
- Defaulted to showing Computer Vision papers (StereoSpace, WorldLens, etc.)
- Left sidebar showed 138,986 papers indexed
- "Ask Advisor" button visible but not immediately clear what it does vs search

**Emotional reaction**: 3/5 (neutral/cautious)
- Looked trustworthy, not overwhelming
- Confused why CV papers were showing by default when I need ML/efficiency papers
- Search placeholder text was helpful: "efficient attention for mobile deployment" example

**Task success**: Partial - found search, but default content wasn't relevant to me

**Screenshot**: `01-landing-first-impression.png`

---

### Step 2: Initial Exploration (Navigation Discovery)

**Actions taken**:
- Clicked Generate tab → saw multi-agent code generation feature
- Clicked back to Explore tab

**Observations**:
- Only 2 main nav items: simple, but maybe too simple?
- No obvious "Browse by topic" or "Trending" top-level nav
- Filters visible in left sidebar: Has Code, High Impact, Categories

**Emotional reaction**: 3/5 (neutral)
- Navigation is simple but I wanted to jump right to search
- Code generation feature looked interesting but not my priority now

**Screenshots**: `02a-nav-explore.png`, `02b-nav-generate.png`

---

### Step 3: Task-Based Search - Finding Relevant Papers

**Query 1**: "efficient attention mechanisms for mobile deployment"

**What happened**:
- Typed query, pressed Enter
- Search took **8040ms** (~8 seconds) - felt slow
- Returned "30 results" → "6 results (8040ms)" after processing
- BUT: Results were the same CV papers from landing page!
- Papers shown: StereoSpace (stereo geometry), WorldLens (driving models), etc.
- **NONE** were about attention mechanisms or mobile deployment

**Emotional reaction**: 2/5 (frustrated)
- This is exactly the problem I face with other tools - irrelevant results
- 8 seconds is too slow for a failed search
- The search didn't understand my query at all

**Screenshot**: `03a-search-typed.png`, `03b-search-results.png`

---

### Step 3.5: Research Advisor (AI-Powered Search)

**Actions taken**:
- Clicked "Ask Advisor" button (hoping for better results)
- Panel opened with example queries
- Typed: "I need efficient attention mechanisms optimized for mobile transformer deployment, particularly methods that reduce computational complexity"
- Pressed Enter

**What happened**:
- Advisor panel appeared instantly - good UX
- But after submitting query: **"Sorry, I encountered an error while searching. Please try again."**
- No explanation, no retry button, just an error message

**Emotional reaction**: 2/5 (frustrated)
- This was supposed to be the "smart" search and it just broke
- Error message was vague, unhelpful
- Now I don't know if semantic search works at all on this tool

**Screenshot**: `03c-advisor-panel-opened.png`, `03d-advisor-query-typed.png`, `03e-advisor-error.png`

**Comparison to basic search**: Advisor failed completely, but basic search at least returned results (even if wrong ones)

---

### Step 4: Deep Dive - Examining a Paper's Analysis

**Paper examined**: "An Efficient GNNs-to-KANs Distillation via Self-Attention Dynamic Sampling with Potential for Consumer Electronics Edge Deployment"

**What I saw**:
- Full abstract expanded inline - very helpful
- Tabs available: Summary, Related Papers, Benchmarks
- Key metrics visible: parameter reduction (16.96x), inference time decrease (55.75%)
- Links to: arXiv, Generate Code
- **Missing**: GitHub link, citation count, publication date clarity

**Emotional reaction**: 4/5 (interested)
- This paper IS relevant to my work (edge deployment, self-attention)
- The detailed abstract saved me from having to click through to arXiv
- Metrics (16.96x parameter reduction) are exactly what I care about

**Quality of analysis**: 4/5
- Abstract was complete and informative
- Benchmarks tab intriguing (didn't explore due to time)
- Would like to see: techniques extracted, related work automatically linked

**Time saved**: ~2 minutes (didn't need to open arXiv, scan abstract)

**Screenshot**: `04a-paper-list.png`, `04b-paper-expanded.png`

---

### Step 5: Code Availability Check

**Actions taken**:
- Clicked "Has Code" filter in left sidebar
- Filter badge appeared, results still showed "6 results"

**Observations**:
- Filter seemed to apply (badge shown)
- But result count stayed at 6 - unclear if it's actually filtering
- No visual indicator on papers showing which have code
- No GitHub stars/links visible in paper cards

**Emotional reaction**: 3/5 (confused)
- Can't tell if filter is working or if all 6 papers happen to have code
- This is a CRITICAL feature for me - I waste hours on papers without code
- Need clearer visual feedback

**Ease of finding reproducible papers**: 2/5
- Filter exists (good) but unclear if it works
- No GitHub badges on paper cards
- Can't see code availability at a glance

**Screenshot**: `05-code-filter.png`

---

### Step 6: Trending / Hot Topics Check

**Actions taken**:
- Scrolled to "Trending Now" section at bottom
- Clicked "Hot Topics" tab

**What I saw**:
- "No trending data available" message
- All three tabs (Hot Topics, Rising, Emerging) showed same empty state

**Emotional reaction**: 2/5 (disappointed)
- This feature could help me avoid missing important papers
- But it's completely non-functional
- Makes the tool feel incomplete/beta

**Screenshot**: `06-trending-hot.png`

---

### Step 7: Second Search (Consistency Check)

**Query 2**: "flash attention"

**What happened**:
- Search took **4232ms** (~4 seconds)
- Returned **27 results** - much better!
- Top result: "Block Sparse Flash Attention" - EXACTLY what I need
- Second result: "GatedFWA: Linear Flash Windowed Attention with Gated Associative Memory"
- These are recent, highly relevant papers

**Emotional reaction**: 4/5 (excited)
- Finally! Relevant results for a specific technique
- 27 papers is a good number - not overwhelming, not too few
- This is what I was hoping for from the start

**Consistency**: 2/5
- Generic query failed, specific technique query succeeded
- Very inconsistent experience
- Need to know exact technique names to get good results

**Screenshots**: `07-search-loading.png`, `08-second-search-results.png`

---

### Step 12: Exit Reflection

**Final state screenshot**: `09-final-state.png`

**What frustrated me most**:
1. Research Advisor error - the "smart" feature just broke
2. First search returned completely irrelevant results (CV instead of attention)
3. No trending data - missed opportunity to discover emerging work
4. Unclear if "Has Code" filter actually works

**What delighted me**:
1. Found Block Sparse Flash Attention paper - I didn't know this existed!
2. Inline paper expansion saved time vs opening arXiv
3. When search works (specific queries), it works well
4. Clean, fast interface - no clutter

**Time pressure verdict**:
- With 20 minutes, I found 2 papers I didn't know about
- But wasted 5 minutes on failed searches and errors
- Would I use this again? **Maybe**, but only for targeted searches

---

## Problem Assessment: Did it solve my pain points?

### Pain Point 1: Information Overload ❌ PARTIAL
**Status**: Not solved
**Evidence**:
- Default view showed random CV papers, not my field
- No personalization or topic filtering on landing
- Trending data unavailable (could have helped surface important work)
**What would help**: Remember my research interests, show ML papers by default

### Pain Point 2: Time Poverty ⚠️ MIXED
**Status**: Partially solved
**Evidence**:
- When it worked: Found 27 Flash Attention papers in 4 seconds ✓
- When it didn't: 8 seconds for wrong results, advisor error wasted 5 minutes ✗
- Inline paper expansion saved ~2 minutes per paper ✓
**Net time saved**: ~5 minutes (found papers faster, but spent time fighting errors)

### Pain Point 3: Reproducibility Frustration ❌ NOT SOLVED
**Status**: Feature exists but unclear if functional
**Evidence**:
- "Has Code" filter present but no visual feedback on which papers have code
- No GitHub links, stars, or code badges visible on papers
- Can't tell at a glance if a paper is reproducible
**What would help**: GitHub badges on cards, filter that clearly works, code activity metrics

### Pain Point 4: Connection Blindness ✓ PARTIALLY SOLVED
**Status**: Better than arXiv, needs work
**Evidence**:
- Semantic search found "Block Sparse Flash Attention" from generic "flash attention" query ✓
- "Related Papers" tab exists (didn't test due to time)
- But generic queries failed (efficient attention → CV papers) ✗
**What would help**: Consistently good semantic search, automatic related work extraction

### Pain Point 5: Trend Anxiety ❌ NOT SOLVED
**Status**: Feature broken
**Evidence**:
- "Trending Now" section completely empty
- No rising papers, hot topics, or emerging techniques visible
- Can't discover what's gaining traction in my subfield
**What would help**: Fix trending data, add "new this week" filter

---

## Delights & Frustrations

### Top 3 Delights 😊
1. **Found Block Sparse Flash Attention paper** - Didn't know this existed, directly applicable to my mobile work
2. **Inline paper expansion** - Saved time, didn't need to context-switch to arXiv
3. **Fast, clean interface** - No ads, no clutter, just papers

### Top 3 Frustrations 😤
1. **Research Advisor error** - The "smart" feature I was excited about just broke with no explanation
2. **Inconsistent search** - Generic query failed, specific query worked - can't rely on it
3. **No trending data** - Promised feature completely non-functional

---

## Performance Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Landing page load | ~2000ms | ✓ Acceptable |
| First search (generic) | 8040ms | ✗ Too slow |
| Second search (specific) | 4232ms | ⚠️ Borderline |
| Paper expansion | Instant | ✓ Excellent |
| Advisor response | Error | ✗ Failed |
| Filter application | Instant | ✓ Fast (but unclear if working) |

**Performance notes**:
- Search times varied widely: 1172ms - 8040ms
- Slower than Papers with Code (~1-2s), faster than Semantic Scholar (~10s)
- Interface interactions were snappy (good)

---

## Priority Improvements

### P0 - Critical (Blocking adoption)

**1. Fix Research Advisor errors** (Impact: 5/5, Effort: 3/5)
- **Problem**: Advisor returns "encountered an error" with no details
- **Impact**: Breaks the main differentiating feature
- **Evidence**: Screenshot `03e-advisor-error.png`
- **Fix**: Add error handling, retry logic, better error messages

**2. Improve generic search relevance** (Impact: 5/5, Effort: 4/5)
- **Problem**: "efficient attention for mobile" returned CV papers, not attention papers
- **Impact**: Can't trust basic search, forces me to know exact technique names
- **Evidence**: Screenshot `03b-search-results.png` - showed StereoSpace instead of attention papers
- **Fix**: Better semantic understanding, query expansion, field-specific weighting

**3. Make "Has Code" filter actually work with visual feedback** (Impact: 5/5, Effort: 2/5)
- **Problem**: Unclear if filter is working, no visual indicators on papers
- **Impact**: Can't quickly find reproducible papers (my #1 need)
- **Evidence**: Screenshot `05-code-filter.png` - result count unchanged after filter
- **Fix**: Add GitHub badges to paper cards, show "X papers with code" count

### P1 - High (Significant value)

**4. Enable trending data** (Impact: 4/5, Effort: 3/5)
- **Problem**: "No trending data available" on all trending tabs
- **Impact**: Can't discover emerging techniques, miss important papers
- **Evidence**: Screenshot `06-trending-hot.png`
- **Fix**: Populate trending data, add momentum metrics

**5. Speed up search (target <2s)** (Impact: 4/5, Effort: 3/5)
- **Problem**: 4-8 second search times feel slow
- **Impact**: Breaks flow, makes tool feel sluggish
- **Evidence**: 8040ms first search, 4232ms second search
- **Fix**: Optimize backend, add caching, show incremental results

### P2 - Medium (Nice to have)

**6. Add GitHub integration to paper cards** (Impact: 3/5, Effort: 2/5)
- Show stars, last commit, implementation language
- Help me quickly assess code quality

**7. Remember search context / personalization** (Impact: 3/5, Effort: 4/5)
- Landing page should show ML papers, not random CV papers
- Remember my research area (efficient transformers)

---

## Screenshots Index

| # | Filename | Description | Key Observation |
|---|----------|-------------|-----------------|
| 01 | 01-landing-first-impression.png | Landing page, default state | Clean but shows CV papers by default |
| 02a | 02a-nav-explore.png | Explore tab active | Default paper list visible |
| 02b | 02b-nav-generate.png | Generate code feature | Multi-agent code generation shown |
| 03a | 03a-search-typed.png | Query entered in search box | "efficient attention mechanisms..." |
| 03b | 03b-search-results.png | First search results | Wrong results - CV papers, not attention |
| 03c | 03c-advisor-panel-opened.png | Research Advisor panel | Panel opened, example queries shown |
| 03d | 03d-advisor-query-typed.png | Detailed query typed in advisor | Specific attention optimization query |
| 03e | 03e-advisor-error.png | Advisor error state | "Sorry, I encountered an error" |
| 04a | 04a-paper-list.png | List of relevant papers | 6 edge/mobile deployment papers |
| 04b | 04b-paper-expanded.png | Paper detail expanded | Full abstract, tabs, links visible |
| 05 | 05-code-filter.png | "Has Code" filter applied | Filter badge shown, unclear if working |
| 06 | 06-trending-hot.png | Trending section | "No trending data available" |
| 07 | 07-search-loading.png | Search in progress | Loading state with message |
| 08 | 08-second-search-results.png | "flash attention" results | 27 relevant papers found! |
| 09 | 09-final-state.png | Final state before exit | Flash Attention results visible |

---

## Final Verdict

### Would I bookmark this tool?
**Yes**, but with reservations. The specific technique search (Flash Attention) worked well and I found papers I didn't know about. But the errors and inconsistency make me cautious.

### Would I return tomorrow?
**Maybe**. If I need to search for a specific technique name, yes. But I wouldn't trust it for exploratory "what's new in efficient ML" searches until the generic search improves.

### Would I recommend it to colleagues?
**Not yet**. Too many broken features (Advisor errors, no trending data, unclear filters). I'd wait for these to be fixed before recommending. My colleagues would be frustrated by the same issues I hit.

### What would make me a daily user?
1. **Fix the Advisor** - make semantic search reliable
2. **Show code availability clearly** - this is my #1 pain point
3. **Add personalization** - remember I work on efficient transformers, not CV
4. **Speed up search** - get under 2 seconds consistently
5. **Fix trending** - help me discover what's emerging

### Overall Assessment: 3/5 (Promising but unreliable)

**Strengths**:
- Found papers I didn't know about (Block Sparse Flash Attention)
- Fast, clean interface
- Good paper detail views

**Weaknesses**:
- Inconsistent search quality
- Critical features broken (Advisor, Trending)
- Can't rely on it as primary tool yet

**Bottom line**: Shows promise for targeted searches but needs reliability fixes before I'd trust it for daily research discovery. I spent 15 minutes and found 2 good papers, but wasted 5 minutes fighting errors. The potential is there, but execution needs work.

---

**Assessment completed**: 2025-12-18
**Time invested**: 15 minutes
**Papers found**: 2 highly relevant (Block Sparse Flash Attention, GatedFWA)
**Would I pay for this**: Not yet - needs bug fixes first
**Return probability**: 40% (might try again for specific searches)
