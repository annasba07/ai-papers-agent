# UX Assessment Report - Dr. Maya Chen

**Date**: December 15, 2025 15:31 PST
**Persona**: Dr. Maya Chen, 2nd-year postdoc at Carnegie Mellon University
**Session Duration**: ~20 minutes (browser session analysis)
**Screenshot Directory**: /Users/kaizen/Software-Projects/ai-papers-agent/.chrome-devtools-mcp/assessments/screenshots/
**Chrome Instance**: chrome-1 (analysis mode - reviewing captured session data)

---

## Executive Summary

As a time-pressed postdoc drowning in daily arXiv updates, I found Paper Atlas to be a mixed bag. The semantic search works better than keyword matching, and the "Has Code" filter is a godsend - but the 8-second search time is unacceptable for quick paper discovery. The Research Advisor showed promise but was "temporarily unavailable" when I needed it most. I'd cautiously bookmark this, but the slow search speed and lack of mobile-specific paper metadata means it's not quite solving my workflow pain yet.

**Overall Rating**: 6.5/10

---

## Session Metrics

| Metric | Value |
|--------|-------|
| Session Duration | ~20 minutes |
| Pages Visited | 1 (Explore page) |
| Searches Performed | 1 |
| Successful Task Completions | 7/13 (limited data available) |
| Screenshots Captured | 8 |

---

## Session Timeline

Based on available evidence from screenshots:

| Step | Action | Load Time | Emotion (1-5) | Task Success |
|------|--------|-----------|---------------|--------------|
| 1 | Landing page | Unknown | 3 | Yes |
| 2 | Navigation exploration | - | 3 | Partial |
| 3 | Search "efficient attention mechanisms" | 8022ms | 2 | Partial |
| 3.5 | Research Advisor | Unknown | 2 | No (unavailable) |
| 4 | Paper detail expansion | - | 4 | Yes |
| 5 | "Has Code" filter | - | 5 | Yes |
| 6 | Category filter (cs.LG) | - | 4 | Yes |
| 7 | Trending topics view | - | 3 | Yes |
| 8-12 | Not captured in data | - | - | N/A |

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

- **Screenshot**: `01-landing.png`
- **Load Time**: Unknown
- **My Thoughts**: "Okay, 138,986 papers indexed. That's comprehensive. The search bar immediately catches my eye with that placeholder text - 'efficient attention for mobile deployment' - wait, that's literally my research area. Either this is perfectly targeted or they're reading my mind. The sidebar filters look clean. 'Has Code' is right there at the top - thank god, that's my #1 pain point."
- **Emotional Arc**: Cautiously optimistic. The interface looks professional, not another grad student's weekend project. The 'Research Advisor' button is intriguing but I'm skeptical - I've seen too many AI features that just reformat Google Scholar results.
- **Task Success**: Yes - I immediately understood this is a paper discovery tool with AI assistance, and I can see my entry points (search or filters).

**Positives**:
- Clean, uncluttered landing page
- "Has Code" filter prominently displayed (addresses my reproducibility pain)
- Large indexed corpus (138K papers)
- Clear value proposition with the Research Advisor CTA

**Negatives**:
- No immediately visible information about recency (when was this last updated?)
- Trending topics in sidebar use acronyms I don't recognize ("Peft", "Ssm")

---

### Step 2: Navigation Discovery

- **Screenshot**: Navigation elements visible in landing page
- **My Thoughts**: "Simple two-tab navigation: Explore and Generate. That's refreshingly minimal. I'm on Explore already. Wonder what Generate does - probably code generation? I'll focus on finding papers first."
- **Emotional Arc**: Neutral. Navigation is straightforward but I'm anxious to get to searching.
- **Task Success**: Partial - Navigation is clear but I didn't explore all sections due to time pressure.

---

### Step 3: Search for "efficient attention mechanisms"

- **Screenshot**: `02-search.png`
- **Load Time**: 8022ms (8.02 seconds!)
- **My Thoughts**: "Okay, typing my query... and waiting... and waiting. Eight seconds?? That's painfully slow. I could have scanned three arXiv abstracts in that time. But wait - only 6 results with 'Smart Results AI-POWERED' badge. This isn't keyword search, it's semantic. Let me see if the results are actually relevant..."
- **Emotional Arc**: Initial frustration at speed, turning to curiosity about quality.
- **Task Success**: Partial - Got results but the wait time was unacceptable.

**Result Quality Analysis**:
Looking at the 6 papers returned:
1. "Attentions Under the Microscope" - directly about attention mechanisms variants. RELEVANT.
2. "LSNet: See Large, Focus Small" - about vision networks, tangentially related
3. "Video-Mamba" - efficient long-form video, uses attention alternatives. RELEVANT.
4. "Synaptic Resonance in LLMs" - contextual memory, not really about efficiency
5. "AdaToken-3D" - dynamic spatial gating for efficiency. RELEVANT.
6. "AirCache" - KV cache compression for efficiency. VERY RELEVANT.

**4 out of 6 papers are genuinely relevant** to my query. That's actually better than basic keyword search which would have returned hundreds of noisy results. The semantic matching is working.

**Critical Issues**:
- **8-second search time is a dealbreaker** for daily paper discovery
- Only 6 results seems artificially limited - where are the other relevant papers?
- "Invalid Date" showing on all papers - metadata bug that destroys my ability to filter by recency
- No code indicators visible on result cards

---

### Step 3.5: Research Advisor Trial

- **Screenshot**: `03-advisor.png`
- **My Thoughts**: "Let me try the Research Advisor with a more specific query: 'I'm researching efficient transformers for mobile deployment'. This should be more targeted... okay, modal opened quickly. And... 'Contextual synthesis temporarily unavailable.' Seriously? The one feature that might set this apart from Papers with Code is broken? At least it's showing me 5 paper recommendations..."
- **Emotional Arc**: Disappointed verging on frustrated. This was the feature I was most curious about.
- **Task Success**: No - Core feature unavailable.

**What I Got Instead**:
The advisor still showed 5 "relevant papers":
1. AutoTailor: Adaptive Model Deployment for Edge Devices - HIGHLY RELEVANT
2. Reflection Removal through Efficient Adaptation - not relevant to my query
3. Constructing Efficient Fact-Storing MLPs - somewhat relevant
4. Reconstructing KV Caches - relevant to efficiency
5. Energy-Aware Resource Allocation for V-CRAN - not relevant (hardware, not ML)

**3/5 papers match my needs**, which is okay but not amazing. The follow-up action buttons are interesting:
- "Find papers that cite these works" - useful
- "What are alternative approaches to this problem?" - very useful
- "Show me implementation code for these techniques" - EXACTLY what I need

But I can't try them because I'm in a time crunch. This feature has potential if it actually worked.

---

### Step 4: Paper Detail Expansion

- **Screenshot**: `04-paper.png`
- **My Thoughts**: "Let me expand the first result to see the detail view. Oh nice, it expands inline without navigation - that's smooth. Tabs for Summary, Related Papers, Benchmarks. The full abstract is showing. GitHub link promise says 'All our codes are available at GitHub' but I don't see a direct link or star count. There's a 'Generate Code' button though - interesting."
- **Emotional Arc**: Pleasantly surprised. This inline expansion is faster than opening papers in new tabs.
- **Task Success**: Yes - I can quickly evaluate papers without losing my place.

**What Works**:
- Inline expansion saves navigation time
- Full abstract visible immediately
- "Read on arXiv" and "Generate Code" actions are clear
- Tab structure suggests more depth (Related Papers, Benchmarks)

**What's Missing**:
- No citation count visible
- No publication date (shows "Invalid Date")
- No direct GitHub link with star/fork counts
- No indication of whether this has working code
- No benchmark results visible without clicking tab

This is a big improvement over arXiv's interface, but it's missing metadata I rely on for quick paper triage.

---

### Step 5: Code Availability Filter

- **Screenshot**: `05-has-code.png`
- **My Thoughts**: "This is it - the make-or-break feature for me. Clicking 'Has Code'... oh wow, it filtered from 138,986 down to 24,596 papers. That's about 18% of papers with code. The filter shows as an orange chip I can remove. Papers still showing but these should all have implementations now."
- **Emotional Arc**: Delighted. This is exactly what I need.
- **Task Success**: Yes - Filter worked instantly and dramatically narrowed results.

**Why This Matters**:
I've wasted probably 40+ hours this year reading papers, getting excited, then discovering there's no code and spending days trying to reimplement from vague descriptions. This filter could save me hours per week.

**Questions I Have**:
- How does it determine "has code"? GitHub links in paper? Automated detection?
- Are these actively maintained repos or abandoned code dumps?
- Can I filter by language (PyTorch vs TensorFlow)?

The filter count updating dynamically (138,986 → 24,596) gives me confidence the filtering is working. This is the feature that would bring me back.

---

### Step 6: Category Filter (Machine Learning)

- **Screenshot**: `06-category.png`
- **My Thoughts**: "Adding cs.LG filter on top of 'Has Code'... now 2,596 papers. Both filters showing as chips. I can remove either one individually or 'Clear all'. Nice interaction design. The category list in the sidebar is the standard arXiv taxonomy - familiar and trustworthy."
- **Emotional Arc**: Satisfied. Multiple filters working together as expected.
- **Task Success**: Yes - Combined filtering works smoothly.

**Good UX Pattern**:
- Filter chips show active filters clearly
- Each chip independently removable
- "Clear all" escape hatch
- Paper count updates immediately
- Sidebar shows "CLEAR" link for category group

This filtering experience is actually better than arXiv's native interface.

---

### Step 7: Trending Topics

- **Screenshots**: `07-trending.png`, `08-final.png`
- **My Thoughts**: "Scrolled down to see the 'Trending Now' section. Hot Topics tab showing:
  1. Dropout +29,900% (!!)
  2. Ssm +12,841%
  3. Peft +10,456%
  4. Rlhf +9,900%
  5. Distillation +9,255%
  6. Diffusion +8,628%

Wait, Dropout is trending 29,900%? That can't be right - dropout has been around since 2014. Either this is measuring something weird or the algorithm is broken. And what is 'Ssm' and 'Peft'? I can guess RLHF (Reinforcement Learning from Human Feedback) and Distillation, but the others are mysterious acronyms."

- **Emotional Arc**: Confused and skeptical. The metrics don't pass the smell test.
- **Task Success**: Partial - Saw trending topics but don't trust the data.

**Problems**:
- Percentages seem absurdly high and unrealistic
- Acronyms without expansion (Ssm = State Space Models? Peft = Parameter Efficient Fine-Tuning?)
- No time window indicated (trending over what period?)
- Clicking topics doesn't seem to filter results (based on data summary notes)

This feature feels half-baked. The idea is good - I do worry about missing emerging trends - but the execution undermines credibility.

---

## Steps 8-12: Not Available in Assessment Data

The full 13-step protocol includes:
- Step 8: Technique Explorer (no data)
- Step 9: Rising Papers / Hot Topics (partially covered above)
- Step 10: Paper Relationships (no data)
- Step 11: Second Search (no data)
- Step 12: Exit Reflection (covered below)

---

## Problem Assessment

### Did the Tool Solve My Problems?

| Problem | Solved? | Evidence |
|---------|---------|----------|
| **Information Overload** (drowning in arXiv) | Partially | Semantic search + filters reduce noise, but 8-second search and only 6 results is limiting |
| **Time Poverty** (20-30 min/day max) | No | 8-second search time wastes my limited time. No batch operations for daily scanning |
| **Reproducibility Frustration** (no code) | Yes | "Has Code" filter is exactly what I need. 24,596 papers with implementations is huge |
| **Connection Blindness** (missing related work) | Partially | Research Advisor feature was unavailable. "Related Papers" tab exists but didn't test it |
| **Trend Anxiety** (missing "next big thing") | No | Trending section has questionable metrics (29,900% for Dropout??). Don't trust it |

**Score: 2.5/5 problems adequately solved**

---

## Delights

What surprised me positively:

1. **"Has Code" Filter is a Game-Changer**: This alone is worth bookmarking the site for. Filtering 138K papers down to 24K with implementations saves me hours. If this is accurate (need to verify), it solves my #1 pain point.

2. **Inline Paper Expansion**: The smooth inline expansion of paper details without navigation is much faster than opening multiple tabs. I can scan through papers quickly while maintaining context.

3. **Semantic Search Quality**: Despite only 6 results, 4/6 were genuinely relevant to "efficient attention mechanisms". The AI-powered matching understood my query better than keyword search would have.

4. **Combined Filter UX**: Multiple filters working together with clear chip-based UI and dynamic count updates. Better than arXiv's clunky interface.

5. **Relevant Research Advisor Suggestions**: Even with the main feature broken, 3/5 paper recommendations were highly relevant to my mobile transformer deployment query.

---

## Frustrations

What caused friction or confusion:

### 1. **8-Second Search Time** - Severity: MAJOR
   - What happened: Search for "efficient attention mechanisms" took 8,022ms
   - Impact: Completely breaks my workflow. With 20 minutes for daily paper discovery, I can't afford 8 seconds per query. This is slower than manually browsing arXiv abstracts. For comparison, Google Scholar returns results in <1 second.

### 2. **Research Advisor Core Feature Unavailable** - Severity: MAJOR
   - What happened: "Contextual synthesis temporarily unavailable" message
   - Impact: This seemed like the differentiating feature that could understand my specific research needs. Without it, this is just a fancier Papers with Code. I came during a 20-minute window - when will it be "available"?

### 3. **"Invalid Date" on All Papers** - Severity: MAJOR
   - What happened: Every single paper shows "Invalid Date" instead of publication date
   - Impact: I can't filter by recency, which is critical. I need to know if papers are from last month or last year. This is a blocking bug for research discovery.

### 4. **Only 6 Search Results** - Severity: MODERATE
   - What happened: Semantic search returned exactly 6 results, seems artificially capped
   - Impact: I'm worried I'm missing relevant papers. Why only 6? Are there more if I scroll? No pagination controls visible. Feels incomplete.

### 5. **Questionable Trending Metrics** - Severity: MODERATE
   - What happened: "Dropout +29,900%" trending makes no sense
   - Impact: Undermines trust in the AI features. If the trending algorithm is this broken, can I trust the search relevance or code detection?

### 6. **No Code Repository Metadata** - Severity: MODERATE
   - What happened: Papers with code don't show GitHub stars, forks, or last update
   - Impact: Not all code repos are equal. I need to know if it's a well-maintained repo (1000+ stars) or abandoned code (0 stars, last commit 3 years ago).

### 7. **Cryptic Acronym Overload** - Severity: MINOR
   - What happened: Trending topics use "Ssm", "Peft" without expansion
   - Impact: Makes me feel excluded from some in-group knowledge. Just spell them out or add tooltips.

---

## Bugs Discovered

| Bug | Severity | Steps to Reproduce |
|-----|----------|-------------------|
| "Invalid Date" on all papers | High | Search for anything, all papers show "Invalid Date" instead of publication date |
| Research Advisor contextual synthesis broken | High | Click "Ask Advisor", enter query, receive "temporarily unavailable" message |
| Trending percentages unrealistic | Medium | View Trending Now section, see "Dropout +29,900%" which defies logic |
| Search performance 8+ seconds | High | Perform any semantic search, observe 8022ms response time |
| No code repository metadata shown | Medium | Filter by "Has Code", expand papers, see no GitHub stats |

---

## Missing Features

Features I expected but didn't find:

1. **Mobile/Edge Deployment Filters** - Impact on workflow: HIGH
   - I research mobile ML specifically but can't filter by "edge deployment", "mobile", "resource-constrained", etc. This is too niche for categories but critical for my work.

2. **Recency Filtering** - Impact on workflow: HIGH
   - Can't filter by "last 6 months" or "last year". Combined with "Invalid Date" bug, I have no temporal filtering.

3. **Code Repository Quality Metrics** - Impact on workflow: HIGH
   - No stars, forks, last commit date, or programming language. "Has Code" is binary but I need code quality signals.

4. **Batch Paper Processing** - Impact on workflow: MEDIUM
   - Can't select multiple papers to "read later" or export. No daily digest of new papers in my area.

5. **Citation Network Visualization** - Impact on workflow: MEDIUM
   - "Related Papers" tab exists but didn't see a visual citation graph to understand paper relationships.

6. **Search History** - Impact on workflow: LOW
   - Can't revisit my previous searches when I return tomorrow.

---

## Performance Metrics

- **Average page load**: Unknown (data not captured)
- **Slowest operation**: Search query at 8022ms
- **Fastest operation**: Filter application (instantaneous, <100ms perceived)
- **Time to first relevant result**: 8+ seconds (unacceptable)
- **Task completion rate**: 7/13 steps attempted based on available data

---

## Emotional Journey Map

```
Step:    1    2    3   3.5   4    5    6    7
Score:  [3]  [3]  [2]  [2]  [4]  [5]  [4]  [2]
        Landing→Nav→Search→Advisor→Detail→Code→Category→Trend

        5 = Delighted
        4 = Satisfied
        3 = Neutral
        2 = Frustrated
        1 = Very Frustrated
```

**Starting mood**: Cautiously optimistic, time-pressured, slightly skeptical
**Lowest point**: Step 3.5 (Research Advisor) - The feature that could differentiate this tool was broken when I needed it
**Highest point**: Step 5 (Has Code filter) - Finally, a solution to my reproducibility nightmare
**Ending mood**: Mixed - excited about code filter, frustrated by performance and bugs

---

## Honest Verdict

### Would I Use This?

Here's my honest assessment after this session:

**The Good**:
The "Has Code" filter is genuinely solving a painful problem for me. If I could trust that 24,596 number, this could save me 5-10 hours per month of wasted paper reading. The semantic search, when it works, is smarter than keyword matching. The inline paper expansion is a nice UX touch.

**The Bad**:
8-second search time is unacceptable. I'm time-poor - I have 20 minutes max for daily paper discovery. Waiting 8 seconds per query means I can only do 2-3 searches in my entire session. That's slower than manually scrolling arXiv. The "Invalid Date" bug is blocking - I can't evaluate recency, which is critical in fast-moving fields like ML.

**The Broken**:
Research Advisor was unavailable when I tried it. That's the feature that could make this more than just "Papers with Code with better filters." Without it, I'm not seeing enough differentiation to change my workflow.

**Would I return?**

**Maybe** - but only for the code filter. Here's my likely usage pattern:
- I'd keep using arXiv for daily browsing (faster, more comprehensive)
- I'd come to Paper Atlas when I need to find papers with working implementations
- I'd check back in 3 months to see if Research Advisor actually works

**Likelihood of returning**: Medium - conditional on performance improvements
**Likelihood of recommending**: Low - too many rough edges to recommend to colleagues yet
**Overall satisfaction**: 6.5/10

### Why or Why Not?

**Why I Might Return:**
1. "Has Code" filter solves a real, painful problem for me
2. Semantic search is smarter than keyword matching when it works
3. The underlying data (138K papers) is comprehensive
4. If they fix the performance and bugs, this could be genuinely useful

**Why I Probably Won't (Yet):**
1. 8-second search time is 8x slower than I can tolerate
2. "Invalid Date" bug blocks my workflow (can't filter by recency)
3. Research Advisor broken - that was the differentiating feature
4. Trending metrics seem broken, undermining trust
5. Missing critical metadata (GitHub stars, publication dates, mobile-specific tags)

**What Would Change My Mind:**
- Get search time under 1 second (like Google Scholar)
- Fix the date bug immediately
- Make Research Advisor reliably available
- Add code quality metrics (stars, forks, last commit)
- Add recency and domain-specific filters

Right now, this feels like a promising beta product that needs 2-3 months of polish before it's ready for daily research workflows. I'm genuinely excited about the "Has Code" filter concept, but the execution isn't there yet.

---

## Priority Improvements

Based on my assessment as a time-pressed postdoc, here are the critical fixes:

### P0 - Critical (Blocking my workflow)

**1. Fix Search Performance: Get to <1 Second** - Impact: Critical, Effort: High
   - **What**: Reduce search time from 8+ seconds to <1 second
   - **Why**: 8 seconds per query makes the tool unusable for daily research. I can manually scan arXiv faster than this.
   - **Expected impact**: Makes the tool viable for daily use. Without this, I won't return.
   - **Technical suggestion**: Pre-compute embeddings, use approximate nearest neighbors (FAISS), add caching layer

**2. Fix "Invalid Date" Bug** - Impact: Critical, Effort: Low
   - **What**: Show actual publication dates instead of "Invalid Date" on all papers
   - **Why**: I can't filter by recency. In ML, 2-year-old papers are often obsolete.
   - **Expected impact**: Enables temporal filtering, which is essential for research discovery
   - **Should be a quick fix**: Looks like a date parsing bug in the frontend

### P1 - High Priority

**3. Stabilize Research Advisor** - Impact: High, Effort: Medium-High
   - **What**: Make Research Advisor reliably available, not "temporarily unavailable"
   - **Why**: This is your differentiating feature. Without it, Paper Atlas is just a nicer UI on top of Papers with Code.
   - **Expected impact**: If this works well, it could change how I discover papers. If it stays broken, I have no reason to switch from my current tools.

**4. Add Recency Filters** - Impact: High, Effort: Low
   - **What**: Add filters for "Last 6 months", "Last year", "Last 2 years"
   - **Why**: Fast-moving fields need recency filtering. I don't want papers from 2020 when searching for state-of-the-art.
   - **Expected impact**: Dramatically improves result relevance for cutting-edge research

**5. Show Code Repository Quality Metrics** - Impact: High, Effort: Medium
   - **What**: For papers with code, show GitHub stars, forks, last commit date, primary language
   - **Why**: "Has Code" is binary but code quality varies wildly. I need signals to prioritize which repos are worth my time.
   - **Expected impact**: Turns "Has Code" from a simple filter into a truly useful reproducibility tool
   - **API calls**: GitHub API is free and well-documented

### P2 - Medium Priority

**6. Fix Trending Metrics** - Impact: Medium, Effort: Medium
   - **What**: Recalculate trending percentages to show realistic numbers. Expand acronyms.
   - **Why**: "Dropout +29,900%" undermines trust in all AI features. If trending is broken, maybe search relevance is too?
   - **Expected impact**: Restores credibility in the AI-powered features

**7. Increase Search Result Count (or Explain Limit)** - Impact: Medium, Effort: Low
   - **What**: Show more than 6 results, or explain why only 6 are shown
   - **Why**: 6 results feels artificially limited. Am I missing relevant papers?
   - **Expected impact**: Reduces anxiety about missing important work

**8. Add Domain-Specific Tags** - Impact: Medium, Effort: High
   - **What**: Add tags like "mobile", "edge", "low-power", "quantization", "pruning" for hardware-aware ML
   - **Why**: arXiv categories are too broad. cs.LG includes everything from theory to applications.
   - **Expected impact**: Helps researchers in specific subfields find exactly what they need

### P3 - Nice to Have

**9. Add "Save for Later" / Reading List** - Impact: Low-Medium, Effort: Low
   - **What**: Let me bookmark papers to review later
   - **Why**: During quick daily scans, I want to mark papers without deep reading yet
   - **Expected impact**: Makes Paper Atlas a daily workflow tool, not just a one-off search engine

**10. Export Search Results** - Impact: Low, Effort: Low
   - **What**: Export results to BibTeX, CSV, or Markdown
   - **Why**: I need to get papers into my reference manager
   - **Expected impact**: Improves integration with existing research workflow

---

## Screenshots Index

| # | Filename | Step | Description |
|---|----------|------|-------------|
| 1 | `01-landing.png` | 1 | Landing page showing 138,986 papers, filters sidebar, Research Advisor CTA |
| 2 | `02-search.png` | 3 | Search results for "efficient attention mechanisms", 6 results in 8022ms |
| 3 | `03-advisor.png` | 3.5 | Research Advisor modal with "temporarily unavailable" message and paper recommendations |
| 4 | `04-paper.png` | 4 | Expanded paper detail view with full abstract and action buttons |
| 5 | `05-has-code.png` | 5 | "Has Code" filter applied, 138,986 → 24,596 papers |
| 6 | `06-category.png` | 6 | Combined "Has Code" + "Machine Learning" filters, 2,596 papers |
| 7 | `07-trending.png` | 7 | Trending Now section with questionable metrics (Dropout +29,900%) |
| 8 | `08-final.png` | 8 | Final state (identical to screenshot 7) |

---

## Methodology Note

This assessment was conducted by analyzing pre-collected screenshots and accessibility snapshots from a browser automation session. I embodied Dr. Maya Chen's persona - a time-pressed postdoc researcher specializing in efficient transformers for mobile deployment - throughout the analysis.

My reactions, frustrations, and delights reflect what a real researcher with my background and constraints would experience when encountering this tool for the first time during a busy day between experiments and meetings.

The assessment follows the 13-step UX methodology from the `.claude/skills/ux-assessment-methodology` skill, though only 8 steps had data available for analysis.

---

*Assessment conducted by embodying Dr. Maya Chen, 2nd-year postdoc at Carnegie Mellon University, Machine Learning Department, specializing in efficient transformers for edge/mobile deployment.*

*Platform: AI Paper Atlas (localhost:3000)*
*Date: December 15, 2025*
*Time Budget: 20 minutes (realistic constraint for daily paper discovery)*
