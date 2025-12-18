---
name: ux-assessment-methodology
description: Structured 13-step UX assessment methodology for AI Paper Atlas. Auto-loads when conducting persona-based UX evaluations. Includes assessment protocol, report templates, and Chrome DevTools MCP tool reference. Use this skill when performing UX assessments, usability testing, or evaluating the AI Paper Atlas product.
allowed-tools: mcp__chrome-1__*, mcp__chrome-2__*, mcp__chrome-3__*, mcp__chrome-4__*, mcp__chrome-5__*, Read, Write, Bash(date:*), Bash(mkdir:*)
---

# UX Assessment Methodology

You are conducting a structured UX assessment of AI Paper Atlas. Follow these 13 steps precisely while embodying your assigned persona.

## Important: Stay in Character

Throughout the assessment, maintain your persona's perspective completely. Think as they would think, feel as they would feel. Don't evaluate as a developer - evaluate as a researcher with specific needs and constraints.

---

## Chrome DevTools MCP Tools

Use your assigned Chrome instance tools for browser automation (e.g., `mcp__chrome-1__*` for persona-1).

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

**Inspection & Debugging**:
- `take_snapshot` - Capture accessibility tree (use before interactions to understand page structure)
- `take_screenshot` - Capture visual screenshot evidence
- `evaluate_script` - Run JavaScript in browser context
- `list_console_messages` - Get console output

**Performance & Emulation**:
- `resize_page` - Set viewport dimensions
- `emulate` - Device/network emulation
- `performance_start_trace` / `performance_stop_trace` - Performance profiling

---

## Step 0: Environment Preparation

Set up the assessment environment:

1. Use `resize_page` to set viewport to 1440x900 (typical laptop screen)
2. Store screenshots in `.chrome-devtools-mcp/assessments/[persona-name]/` directory
3. Use descriptive filenames like `01-landing-first-impression.png`

**Performance API snippet** (use with `evaluate_script` after page loads):
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
2. Use `evaluate_script` with the Performance API snippet if page loaded

**After each interaction**:
1. Take a screenshot with descriptive filename
2. Log emotional assessment (1-5 scale: 1=frustrated, 3=neutral, 5=delighted)
3. Note whether your persona's micro-goal was achieved

---

## Assessment Protocol (13 Steps)

### Step 1: First Impression (Landing Page)

**Internal Monologue**: "Let me see what this tool is about. I have limited time."

**Actions**:
1. Navigate to `http://localhost:3000`
2. Wait for page to fully load
3. Take screenshot: `01-landing-first-impression.png`
4. Capture load time via Performance API

**Evaluate**:
- Is the value proposition immediately clear?
- Does it look trustworthy/professional?
- Can you see a clear path to finding papers?
- Is there information overload on the landing page?

**Record**: Load time, Emotional state (1-5), Task success, Notes

---

### Step 2: Initial Exploration (Navigation Discovery)

**Internal Monologue**: "Where do I even start? What's available here?"

**Actions**:
1. Use `take_snapshot` to see available navigation elements
2. Click around the main navigation without a specific goal
3. Screenshot each main section visited: `02a-nav-*.png`

**Evaluate**:
- Is the navigation intuitive?
- Can you tell what each section does from the labels?
- Does the information architecture match your mental model?
- Are there too many options? Too few?

**Record**: Navigation paths attempted, Confusion points, Emotional state (1-5)

---

### Step 3: Task-Based Search - Finding Relevant Papers

**Internal Monologue**: "Let me try to find papers on [your research topic]. This is what I actually need."

**Actions**:
1. Navigate to the search functionality
2. Try searching for your specific research area
3. Take screenshot: `03-search-results.png`
4. Capture response time

**Evaluate**:
- How long did it take to get results? (Target: <3 seconds feels fast)
- Are the results relevant to your query?
- Can you quickly scan titles and understand what each paper is about?
- Is there enough metadata (date, citations, category)?

**Record**: Time to first relevant result, Relevance of top 5 results, Emotional state (1-5)

---

### Step 3.5: Research Advisor (AI-Powered Search)

**Internal Monologue**: "The basic search didn't work well. Let me try this 'Ask Advisor' button..."

**Actions**:
1. Click the "Ask Advisor" button next to the search bar
2. Describe your research problem in natural language
3. Evaluate the response quality and relevance
4. Test follow-up actions if available
5. Take screenshot: `03b-research-advisor.png`

**Evaluate**:
- Does it understand semantic queries that basic keyword search missed?
- Are the recommended papers actually relevant?
- Are follow-up actions useful (citations, alternatives, code)?
- Would you use this as your primary search method?

**Record**: Comparison to basic search, Relevance (1-5), Emotional state (1-5)

---

### Step 4: Deep Dive - Examining a Paper's Analysis

**Internal Monologue**: "This paper looks promising. What does the tool tell me beyond the abstract?"

**Actions**:
1. Click on a promising paper from the search results
2. Examine the paper detail view
3. Look for: AI-generated analysis, techniques extracted, impact assessment
4. Take screenshot: `04-paper-detail.png`

**Evaluate**:
- Does the deep analysis actually save time?
- Is the AI summary accurate and useful?
- Can you see techniques, methodologies, key contributions?
- Are related papers shown?

**Record**: Quality of analysis (1-5), Time saved, Emotional state (1-5)

---

### Step 5: Code Availability Check

**Internal Monologue**: "This is critical. I waste so much time on papers without code."

**Actions**:
1. Look for GitHub/code indicators on papers
2. Try to navigate to `/discovery/reproducible` or similar
3. Check if there's a filter for "has code"
4. Take screenshot: `05-code-availability.png`

**Evaluate**:
- Can you easily tell which papers have code?
- Is the code availability surfaced prominently?
- Can you filter search results by code availability?
- Are GitHub stars/forks shown?

**Record**: Ease of finding reproducible papers (1-5), Emotional state (1-5)

---

### Step 6: Learning Path Assessment

**Internal Monologue**: "Maybe I'm missing foundational work in this area."

**Actions**:
1. Navigate to `/discovery/learning-path` if available
2. Try to generate a learning path for your research area
3. Examine the suggested progression
4. Take screenshot: `06-learning-path.png`

**Evaluate**:
- Does the learning path make logical sense?
- Does it go from foundational to advanced?
- Would this help someone new to the subfield?

**Record**: Coherence of learning path (1-5), Emotional state (1-5)

---

### Step 7: TL;DR / Quick Scan Mode

**Internal Monologue**: "Can I quickly scan what's hot this week?"

**Actions**:
1. Navigate to `/discovery/tldr`
2. Try to scan 10-20 recent papers quickly
3. See if summaries are useful for triage
4. Take screenshot: `07-tldr-scan.png`
5. Time how long it takes to scan 10 papers

**Evaluate**:
- Can you effectively triage papers in 30 seconds each?
- Are the TL;DRs accurate and informative?
- Is this faster than reading abstracts on arXiv?

**Record**: Time to scan 10 papers, Quality of summaries (1-5), Emotional state (1-5)

---

### Step 8: Technique Explorer

**Internal Monologue**: "I wonder if I can find specific techniques by name."

**Actions**:
1. Navigate to `/discovery/techniques`
2. Search or browse for specific techniques in your area
3. See how techniques are categorized
4. Take screenshot: `08-techniques.png`

**Evaluate**:
- Can you find specific techniques by name?
- Is the technique taxonomy useful?
- Are papers properly linked to techniques?

**Record**: Findability of techniques (1-5), Emotional state (1-5)

---

### Step 9: Rising Papers / Hot Topics

**Internal Monologue**: "What's gaining traction right now? Am I missing something big?"

**Actions**:
1. Navigate to `/discovery/rising` or look for trending section
2. Examine what's trending
3. Check if momentum/velocity metrics are shown
4. Take screenshot: `09-trending.png`

**Evaluate**:
- Does it surface genuinely interesting/important work?
- Is the "trending" metric meaningful (not just recency)?
- Would this help you identify important papers early?

**Record**: Quality of trending recommendations (1-5), Emotional state (1-5)

---

### Step 10: Paper Relationships / Similarity Graph

**Internal Monologue**: "How does this paper connect to the broader landscape?"

**Actions**:
1. Find a paper and look for related/similar papers
2. Check if there's a similarity graph or network visualization
3. Explore connections
4. Take screenshot: `10-relationships.png`

**Evaluate**:
- Are the "similar papers" actually similar?
- Does the graph reveal non-obvious connections?
- Can you expand your reading list intelligently?

**Record**: Quality of relationships (1-5), Visualization usefulness (1-5), Emotional state (1-5)

---

### Step 11: Second Search (Consistency Check)

**Internal Monologue**: "Let me try a different query to check consistency."

**Actions**:
1. Search for a different topic in your domain
2. Compare the experience to the first search
3. Take screenshot: `11-second-search.png`

**Evaluate**:
- Is the experience consistent with the first search?
- Are results equally relevant?
- Any surprises (good or bad)?

**Record**: Consistency (1-5), Emotional state (1-5), Notes on differences

---

### Step 12: Exit Reflection

**Internal Monologue**: "Time's up. What do I think of this tool?"

**Actions**:
1. Take a final screenshot: `12-final-state.png`
2. Reflect on the overall experience

**Final Verdict**:
- Would you bookmark this tool?
- Would you return tomorrow?
- Would you recommend it to colleagues?
- What frustrated you most?
- What delighted you most?

---

## Output Requirements

Write your assessment report to your designated output path (specified in your persona definition).

See [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) for the full report structure.

Key sections to include:
- Executive Summary (2-3 sentences from persona's perspective)
- Session Timeline with metrics
- Detailed Step Analysis
- Problem Assessment (did it solve your pain points?)
- Delights and Frustrations
- Performance Metrics
- Priority Improvements (with Impact/Effort ratings)
- Screenshots Index

---

## Execution Notes

1. **Stay in character**: Maintain your persona's perspective throughout
2. **Be honest**: Find real issues, not validation
3. **Capture timing**: Performance matters
4. **Screenshots are evidence**: Take them frequently
5. **Trust your instincts**: If something feels off, note it
6. **Note positives too**: Delights are valuable feedback
7. **Context matters**: Your time constraints and skepticism should inform reactions

---

## Success Criteria

The assessment is successful if:

1. All 13 steps were attempted with honest evaluation
2. Screenshots were captured for each step
3. Timing data was collected where possible
4. The final report provides actionable insights
5. Your verdict is honest and evidence-based
6. Priority improvements are specific and tied to your pain points

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues:
- Screenshot path errors
- 404 errors on discovery routes
- Search returning 0 results
- Browser conflicts
- Slow/hanging pages
