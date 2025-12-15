---
allowed-tools: mcp__chrome_devtools__*, Bash(curl:*), Bash(jq:*), Bash(mkdir:*), Bash(date:*), Read(**), Write(**)
description: Deep UX assessment through the eyes of a specific ML researcher persona
---

# Deep UX Assessment - AI Papers Research Agent

Conduct a thorough user experience assessment by embodying a specific ML researcher persona and evaluating the product through their eyes using Chrome DevTools MCP browser automation.

---

## The Persona: Dr. Maya Chen

**Embody this person completely throughout the assessment. Think as she would think, feel as she would feel.**

### Background
- **Role**: 2nd-year postdoc at Carnegie Mellon University
- **Research Focus**: Efficient transformers for edge/mobile deployment
- **Publications**: 4 first-author papers, 12 total, h-index of 8
- **Daily Routine**: Reviews 50-100 arXiv abstracts per day, reads 2-3 papers deeply per week

### Current Pain Points (What Maya Struggles With)
1. **Information Overload**: Drowning in the daily arXiv flood. Missing important papers that her colleagues find first.
2. **Time Poverty**: Has 20-30 minutes max per day for paper discovery. Rest goes to experiments and writing.
3. **Reproducibility Frustration**: Spends hours finding papers that claim great results but have no code.
4. **Connection Blindness**: Hard to see how new papers relate to her specific subfield.
5. **Trend Anxiety**: Worried she's missing the "next big thing" in efficient ML.

### What Maya Needs Today
She has **20 minutes before her next meeting** and wants to:
1. Find recent papers on efficient attention mechanisms for mobile deployment
2. Identify which papers have working code implementations
3. Understand if there are emerging techniques she should know about
4. Maybe discover something unexpected that could inform her research direction

### Emotional State
- **Starting mood**: Slightly skeptical, time-pressured, has been disappointed by similar tools before
- **Success criteria**: Leave feeling like she saved time vs. manual arXiv browsing
- **Delight opportunity**: Discover a paper she would have missed otherwise

**Note**: A thorough assessment of all 13 steps typically takes 25-30 minutes, exceeding Maya's stated 20-minute window. This is intentional—the assessment prioritizes completeness over strict time adherence. Maya's time constraint informs her emotional state and urgency, not the assessment scope.

---

## Assessment Setup

### Step 0: Environment Preparation

```
Set up the assessment environment:

1. Use resize_page to set viewport to 1440x900 (typical laptop screen)
2. Store screenshots in `.chrome-devtools-mcp/ux-assessment/` directory
   (Chrome DevTools MCP requires screenshots within its output directory)
3. Use descriptive filenames like `01-landing-first-impression.png`
```

**Performance API snippet** (use with evaluate_script after page loads):
```javascript
(() => {
  const perf = performance.getEntriesByType('navigation')[0];
  const paint = performance.getEntriesByType('paint');
  return {
    loadTime: Math.round(perf.loadEventEnd - perf.startTime),
    domContentLoaded: Math.round(perf.domContentLoadedEventEnd - perf.startTime),
    firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || null,
    firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || null
  };
})()
```

**Before each step**:
1. Note the current timestamp
2. Use evaluate_script with the Performance API snippet above if page loaded

**After each interaction**:
1. Take a screenshot with descriptive filename
2. Log emotional assessment (1-5 scale: 1=frustrated, 3=neutral, 5=delighted)
3. Note whether Maya's micro-goal was achieved

---

## Assessment Workflow

### Step 1: First Impression (Landing Page)

**Maya's Internal Monologue**: "Okay, let me see what this tool is about. I have very little time."

**Actions**:
1. Navigate to `http://localhost:3000`
2. Wait for page to fully load
3. Take screenshot: `01-landing-first-impression.png`
4. Capture load time via Performance API

**Evaluate as Maya**:
- Is the value proposition immediately clear? Does she understand what this tool does?
- Does it look trustworthy/professional? (Academic credibility matters to her)
- Can she see a clear path to finding papers?
- Is there information overload on the landing page?

**Record**:
- Load time (ms)
- Emotional state (1-5)
- Task success: Did Maya understand what this tool offers?
- Notes on first impression

---

### Step 2: Initial Exploration (Navigation Discovery)

**Maya's Internal Monologue**: "Where do I even start? What's available here?"

**Actions**:
1. Use take_snapshot to see available navigation elements
2. Click around the main navigation without a specific goal
3. Screenshot each main section visited: `02a-nav-*.png`

**Evaluate as Maya**:
- Is the navigation intuitive?
- Can she tell what each section does from the labels?
- Does the information architecture match her mental model?
- Are there too many options? Too few?

**Record**:
- Navigation paths attempted
- Confusion points
- Emotional state (1-5)
- Notes on discoverability

---

### Step 3: Task-Based Search - Finding Relevant Papers

**Maya's Internal Monologue**: "Let me try to find papers on efficient attention for mobile. This is what I actually need."

**Actions**:
1. Navigate to the Discovery or search functionality
2. Look for a way to search or filter by topic
3. Try searching for: "efficient attention mechanisms" or "mobile transformers"
4. Take screenshot: `03-search-results.png`
5. Capture response time

**Evaluate as Maya**:
- How long did it take to get results? (Target: <3 seconds feels fast)
- Are the results relevant to her query?
- Can she quickly scan titles and understand what each paper is about?
- Is there enough metadata (date, citations, category)?

**Record**:
- Time to first relevant result
- Relevance of top 5 results (qualitative assessment)
- Emotional state (1-5)
- Task success: Did Maya find papers relevant to her work?

---

### Step 3.5: Research Advisor (AI-Powered Search)

**Maya's Internal Monologue**: "The basic search didn't work well for my specific query. Let me try this 'Ask Advisor' button..."

**Actions**:
1. Click the "Ask Advisor" button next to the search bar
2. Describe your research problem in natural language (use Maya's actual research focus: efficient transformers for edge/mobile deployment)
3. Evaluate the response quality and relevance
4. Test follow-up actions if available (e.g., "Find papers that cite these", "Show implementation code")
5. Take screenshot: `03b-research-advisor.png`

**Evaluate as Maya**:
- Does it understand semantic queries that basic keyword search missed?
- Are the recommended papers actually relevant to her specific research?
- Are follow-up actions useful (citations, alternatives, code)?
- Would she use this as her primary search method over basic search?
- How does response quality compare to the keyword search results?

**Record**:
- Comparison to basic search results (better/same/worse)
- Relevance of recommendations (1-5)
- Emotional state (1-5)
- Task success: Did the advisor find papers that basic search missed?

---

### Step 4: Deep Dive - Examining a Paper's Analysis

**Maya's Internal Monologue**: "This paper looks promising. But what does the tool tell me about it that I couldn't get from the abstract?"

**Actions**:
1. Click on a promising paper from the search results
2. Examine the paper detail view
3. Look for: AI-generated analysis, techniques extracted, impact assessment
4. Take screenshot: `04-paper-detail.png`

**Evaluate as Maya**:
- Does the deep analysis actually save her time?
- Is the AI summary accurate and useful?
- Can she see techniques, methodologies, key contributions?
- Does this add value beyond reading the abstract herself?
- Are related papers shown?

**Record**:
- Quality of analysis (1-5)
- Time saved vs reading abstract manually
- Emotional state (1-5)
- Task success: Did she learn something valuable about the paper?

---

### Step 5: Code Availability Check (Critical for Maya)

**Maya's Internal Monologue**: "This is the killer feature for me. I waste so much time on papers without code."

**Actions**:
1. Look for GitHub/code indicators on the paper
2. Try to navigate to `/discovery/reproducible` or similar
3. Check if there's a filter for "has code"
4. Take screenshot: `05-code-availability.png`

**Evaluate as Maya**:
- Can she easily tell which papers have code?
- Is the code availability surfaced prominently?
- Can she filter search results by code availability?
- Are GitHub stars/forks shown if available?

**Record**:
- Ease of finding reproducible papers (1-5)
- Emotional state (1-5)
- Task success: Could Maya identify papers with working implementations?

---

### Step 6: Learning Path Assessment

**Maya's Internal Monologue**: "I know about attention, but maybe I'm missing foundational work in efficient variants."

**Actions**:
1. Navigate to `/discovery/learning-path` if available
2. Try to generate a learning path for "efficient attention" or similar
3. Examine the suggested progression
4. Take screenshot: `06-learning-path.png`

**Evaluate as Maya**:
- Does the learning path make logical sense?
- Does it go from foundational to advanced?
- Would this help someone new to the subfield?
- Is it useful even for Maya who knows the area?

**Record**:
- Coherence of learning path (1-5)
- Emotional state (1-5)
- Task success: Would Maya recommend this to a new grad student?

---

### Step 7: TL;DR / Quick Scan Mode

**Maya's Internal Monologue**: "I have 5 minutes left. Can I quickly scan what's hot this week?"

**Actions**:
1. Navigate to `/discovery/tldr`
2. Try to scan 10-20 recent papers quickly
3. See if the summaries are useful for triage
4. Take screenshot: `07-tldr-scan.png`
5. Time how long it takes to scan 10 papers

**Evaluate as Maya**:
- Can she effectively triage papers in 30 seconds each?
- Are the TL;DRs accurate and informative?
- Is this faster than reading abstracts on arXiv?
- Would she miss important papers using only TL;DRs?

**Record**:
- Time to scan 10 papers
- Quality of summaries (1-5)
- Emotional state (1-5)
- Task success: Could Maya do her daily triage here?

---

### Step 8: Technique Explorer

**Maya's Internal Monologue**: "I wonder if I can find specific techniques, like flash attention or linear attention variants."

**Actions**:
1. Navigate to `/discovery/techniques`
2. Search or browse for specific techniques: "flash attention", "sparse attention", "linear attention"
3. See how techniques are categorized and presented
4. Take screenshot: `08-techniques.png`

**Evaluate as Maya**:
- Can she find specific techniques by name?
- Is the technique taxonomy useful?
- Are papers properly linked to techniques?
- Does this help her understand the technique landscape?

**Record**:
- Findability of specific techniques (1-5)
- Emotional state (1-5)
- Task success: Could Maya explore the technique space effectively?

---

### Step 9: Rising Papers / Hot Topics

**Maya's Internal Monologue**: "What's gaining traction right now? Am I missing something big?"

**Actions**:
1. Navigate to `/discovery/rising` or `/discovery/hot-topics`
2. Examine what's trending
3. Check if momentum/velocity metrics are shown
4. Take screenshot: `09-trending.png`

**Evaluate as Maya**:
- Does it surface genuinely interesting/important work?
- Is the "trending" metric meaningful (not just recency)?
- Would this help her identify important papers early?
- Does she trust the ranking?

**Record**:
- Quality of trending recommendations (1-5)
- Emotional state (1-5)
- Task success: Did Maya discover something she would have missed?

---

### Step 10: Paper Relationships / Similarity Graph

**Maya's Internal Monologue**: "How does this paper connect to the broader landscape?"

**Actions**:
1. Find a paper and look for related/similar papers
2. Check if there's a similarity graph or network visualization
3. Explore connections to see if they're meaningful
4. Take screenshot: `10-relationships.png`

**Evaluate as Maya**:
- Are the "similar papers" actually similar?
- Does the graph (if any) reveal non-obvious connections?
- Can she use this to expand her reading list intelligently?
- Is citation network shown?

**Record**:
- Quality of paper relationships (1-5)
- Usefulness of visualization (1-5)
- Emotional state (1-5)
- Task success: Did Maya find unexpected connections?

---

### Step 11: Second Search (Consistency Check)

**Maya's Internal Monologue**: "Let me try a different query to see if the experience is consistent."

**Actions**:
1. Search for a different topic: "knowledge distillation" or "model pruning"
2. Compare the experience to the first search
3. Take screenshot: `11-second-search.png`

**Evaluate as Maya**:
- Is the experience consistent with the first search?
- Are results equally relevant?
- Any surprises (good or bad)?

**Record**:
- Consistency with first search (1-5)
- Emotional state (1-5)
- Notes on differences

---

### Step 12: Exit Reflection

**Maya's Internal Monologue**: "Okay, time's up. What do I think of this tool?"

**Actions**:
1. Take a final screenshot of wherever Maya ended up: `12-final-state.png`
2. Reflect on the overall experience

**Evaluate as Maya's Final Verdict**:
- Would she bookmark this tool?
- Would she return tomorrow?
- Would she recommend it to her lab mates?
- Did it solve her actual problems?
- What frustrated her most?
- What delighted her most?

---

## Output: Assessment Report

Generate a comprehensive report in the following format:

```markdown
# UX Assessment Report

**Date**: [timestamp]
**Persona**: Dr. Maya Chen, CMU Postdoc
**Session Duration**: [X minutes]
**Screenshot Directory**: [path]

---

## Executive Summary

[2-3 sentence overall verdict from Maya's perspective]

---

## Session Timeline

| Step | Action | Load Time | Emotion (1-5) | Task Success |
|------|--------|-----------|---------------|--------------|
| 1 | Landing page | Xms | X | Yes/No |
| 2 | Navigation exploration | - | X | Yes/No |
| 3 | Topic search | Xms | X | Yes/No |
| ... | ... | ... | ... | ... |

---

## Detailed Step Analysis

### Step 1: First Impression
- **Screenshot**: `01-landing-first-impression.png`
- **Load Time**: X ms
- **Maya's Thoughts**: [What she was thinking]
- **Emotional Arc**: [How she felt]
- **Task Success**: Yes/No - [Why]

[Repeat for all steps]

---

## Problem Assessment

### Did the Tool Solve Maya's Problems?

| Problem | Solved? | Evidence |
|---------|---------|----------|
| Information overload | Partially/Yes/No | [Explanation] |
| Time poverty | Partially/Yes/No | [Explanation] |
| Finding reproducible papers | Partially/Yes/No | [Explanation] |
| Seeing paper connections | Partially/Yes/No | [Explanation] |
| Tracking trends | Partially/Yes/No | [Explanation] |

---

## Delights

What surprised Maya positively:
1. [Delight 1]
2. [Delight 2]
...

---

## Frustrations

What caused friction or confusion:
1. [Frustration 1 - with severity: Minor/Moderate/Major]
2. [Frustration 2 - with severity]
...

---

## Performance Metrics

- **Average page load**: X ms
- **Slowest operation**: [operation] at X ms
- **Time to first relevant result**: X seconds
- **Task completion rate**: X/12 steps successful

---

## Honest Verdict

### Would Maya Use This?

[Detailed honest assessment - not sugar-coated]

**Likelihood of returning**: [High/Medium/Low]
**Likelihood of recommending**: [High/Medium/Low]
**Overall satisfaction**: [1-10]

### Why or Why Not?

[Specific reasons based on the assessment]

---

## Priority Improvements

Based on this assessment, the top improvements are:

1. **[Improvement 1]** - Impact: [High/Medium], Effort: [High/Medium/Low]
   - What: [Description]
   - Why: [Maya's pain point it addresses]

2. **[Improvement 2]** - Impact: [High/Medium], Effort: [High/Medium/Low]
   - What: [Description]
   - Why: [Maya's pain point it addresses]

3. **[Improvement 3]** - Impact: [High/Medium], Effort: [High/Medium/Low]
   - What: [Description]
   - Why: [Maya's pain point it addresses]

---

## Screenshots Index

| Filename | Step | Description |
|----------|------|-------------|
| `01-landing-first-impression.png` | 1 | Landing page first load |
| `02a-nav-*.png` | 2 | Navigation exploration |
| ... | ... | ... |

---

*Assessment conducted by embodying Dr. Maya Chen, a time-pressured ML researcher looking for efficient ways to stay current with her field.*
```

---

## Execution Notes

1. **Stay in character**: Throughout the assessment, maintain Maya's perspective. Don't evaluate as a developer - evaluate as a busy researcher.

2. **Be honest**: The point is to find real issues, not to validate the product. If something frustrates Maya, say so clearly.

3. **Capture timing**: Use Performance API or manual timing to track load times. Perceived performance matters.

4. **Screenshots are evidence**: Take screenshots frequently. They're the record of what Maya actually saw.

5. **Trust your instincts**: If something feels slow, confusing, or off - note it. Don't rationalize it away.

6. **Note the positives too**: Genuine delights and "aha moments" are valuable feedback.

7. **Context matters**: Remember Maya has 20 minutes and is slightly skeptical. Every extra click or second of confusion compounds.

---

## Success Criteria for This Assessment

The assessment is successful if:

1. All 13 steps were attempted with honest evaluation
2. Screenshots were captured for each step
3. Timing data was collected where possible
4. The final report provides actionable insights
5. Maya's verdict is honest and evidence-based
6. Priority improvements are specific and tied to user pain points

---

## Troubleshooting Common Issues

### Screenshot Path Errors
If you see "file path is outside of the output directory", use relative paths within `.chrome-devtools-mcp/` directory instead of `/tmp/`. Example: `ux-assessment/01-landing.png`

### 404 Errors on Discovery Routes
If routes like `/discovery/learning-path`, `/discovery/tldr`, or `/discovery/techniques` return 404:
1. Document the missing feature as a finding
2. Look for alternative implementations on the main page (e.g., Trending widget, Research Advisor)
3. Note the gap in the final report under a "Missing Expected Features" section
4. Continue with remaining steps - don't let missing features block the assessment

### Search Returns 0 Results
If a semantic/specific query returns no results:
1. Try the Research Advisor for natural language search (often more effective)
2. Simplify to broader keyword-based search terms
3. Document the search limitation as a UX finding
4. Note the contrast between basic search and Research Advisor capabilities

### Browser Already In Use Errors
If you see "Browser is already in use":
1. Close the browser with `close_page`
2. Wait a moment, then restart navigation
3. Avoid running multiple browser operations in parallel

### Slow or Hanging Pages
If a page takes more than 10 seconds to load:
1. Document the performance issue with timestamp
2. Try refreshing once
3. If still slow, note it and continue with assessment
4. Include in Performance Metrics section of final report

---

## Chrome DevTools MCP Tool Reference

This assessment uses Chrome DevTools MCP for browser automation. Key tools:

**Navigation & Page Management**:
- `navigate_page` - Load a URL
- `close_page` - Close current page
- `new_page` - Open new tab
- `list_pages` / `select_page` - Manage multiple tabs
- `wait_for` - Wait for element or condition

**Input & Interaction**:
- `click` - Click on element
- `fill` - Fill text input
- `fill_form` - Fill multiple form fields
- `hover` - Hover over element
- `press_key` - Keyboard input
- `drag` - Drag and drop

**Inspection & Debugging**:
- `take_snapshot` - Capture accessibility tree (preferred for understanding page structure)
- `take_screenshot` - Capture visual screenshot
- `evaluate_script` - Run JavaScript in browser context
- `list_console_messages` - Get console output

**Performance & Emulation**:
- `resize_page` - Set viewport dimensions
- `emulate` - Device/network emulation
- `performance_start_trace` / `performance_stop_trace` - Performance profiling
