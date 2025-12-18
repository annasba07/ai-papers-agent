# UX Assessment Report Template

Use this template structure for your assessment report.

---

```markdown
# UX Assessment Report - [Persona Name]

**Date**: [timestamp]
**Persona**: [Full name and role]
**Session Duration**: [X minutes]
**Screenshot Directory**: [path]
**Chrome Instance**: [which MCP server used]

---

## Executive Summary

[2-3 sentence overall verdict from your persona's perspective. Be honest and specific.]

**Overall Rating**: [X/10]

---

## Session Metrics

| Metric | Value |
|--------|-------|
| Session Duration | X minutes |
| Pages Visited | X |
| Searches Performed | X |
| Successful Task Completions | X/13 |
| Screenshots Captured | X |

---

## Session Timeline

| Step | Action | Load Time | Emotion (1-5) | Task Success |
|------|--------|-----------|---------------|--------------|
| 0 | Environment setup | - | - | Yes/No |
| 1 | Landing page | Xms | X | Yes/No |
| 2 | Navigation exploration | - | X | Yes/No |
| 3 | Topic search | Xms | X | Yes/No |
| 3.5 | Research Advisor | Xms | X | Yes/No |
| 4 | Paper detail view | Xms | X | Yes/No |
| 5 | Code availability | - | X | Yes/No |
| 6 | Learning path | Xms | X | Yes/No |
| 7 | TL;DR scan | - | X | Yes/No |
| 8 | Technique explorer | Xms | X | Yes/No |
| 9 | Trending/Rising | Xms | X | Yes/No |
| 10 | Paper relationships | - | X | Yes/No |
| 11 | Second search | Xms | X | Yes/No |
| 12 | Exit reflection | - | X | - |

---

## Detailed Step Analysis

### Step 1: First Impression
- **Screenshot**: `01-landing-first-impression.png`
- **Load Time**: X ms
- **My Thoughts**: [What you were thinking as this persona]
- **Emotional Arc**: [How you felt]
- **Task Success**: Yes/No - [Why]

### Step 2: Navigation Discovery
- **Screenshot**: `02a-nav-*.png`
- **My Thoughts**: [...]
- **Emotional Arc**: [...]
- **Task Success**: Yes/No - [Why]

[Continue for all steps...]

---

## Problem Assessment

### Did the Tool Solve My Problems?

| Problem | Solved? | Evidence |
|---------|---------|----------|
| [Pain Point 1] | Partially/Yes/No | [Specific evidence] |
| [Pain Point 2] | Partially/Yes/No | [Specific evidence] |
| [Pain Point 3] | Partially/Yes/No | [Specific evidence] |
| [Pain Point 4] | Partially/Yes/No | [Specific evidence] |
| [Pain Point 5] | Partially/Yes/No | [Specific evidence] |

---

## Delights

What surprised me positively:

1. **[Delight 1]**: [Description and why it mattered]
2. **[Delight 2]**: [Description and why it mattered]
3. **[Delight 3]**: [Description and why it mattered]

---

## Frustrations

What caused friction or confusion:

1. **[Frustration 1]** - Severity: Minor/Moderate/Major
   - What happened: [Description]
   - Impact: [How it affected my workflow]

2. **[Frustration 2]** - Severity: Minor/Moderate/Major
   - What happened: [Description]
   - Impact: [How it affected my workflow]

---

## Bugs Discovered

| Bug | Severity | Steps to Reproduce |
|-----|----------|-------------------|
| [Bug description] | Low/Medium/High | [Steps] |

---

## Missing Features

Features I expected but didn't find:

1. [Feature 1] - Impact on workflow: [High/Medium/Low]
2. [Feature 2] - Impact on workflow: [High/Medium/Low]

---

## Performance Metrics

- **Average page load**: X ms
- **Slowest operation**: [operation] at X ms
- **Fastest operation**: [operation] at X ms
- **Time to first relevant result**: X seconds
- **Task completion rate**: X/13 steps successful

---

## Emotional Journey Map

```
Step:    1    2    3   3.5   4    5    6    7    8    9   10   11   12
Score:  [X]  [X]  [X]  [X]  [X]  [X]  [X]  [X]  [X]  [X]  [X]  [X]  [X]
        Landing→Nav→Search→Advisor→Detail→Code→Learn→TLDR→Tech→Trend→Rel→Search2→Exit
```

**Starting mood**: [Description]
**Lowest point**: Step [X] - [Why]
**Highest point**: Step [X] - [Why]
**Ending mood**: [Description]

---

## Honest Verdict

### Would I Use This?

[Detailed honest assessment - not sugar-coated. Be specific about what would make you return or not.]

**Likelihood of returning**: High/Medium/Low - [Why]
**Likelihood of recommending**: High/Medium/Low - [Why]
**Overall satisfaction**: [1-10]

### Why or Why Not?

[Specific reasons based on the assessment, tied to your persona's actual needs]

---

## Priority Improvements

Based on this assessment, the top improvements are:

### P0 - Critical (Blocking my workflow)

1. **[Improvement]** - Impact: High, Effort: [High/Medium/Low]
   - What: [Specific description]
   - Why: [Which pain point it addresses]
   - Expected impact: [What would change]

### P1 - High Priority

2. **[Improvement]** - Impact: High, Effort: [High/Medium/Low]
   - What: [Description]
   - Why: [Pain point]

3. **[Improvement]** - Impact: Medium-High, Effort: [High/Medium/Low]
   - What: [Description]
   - Why: [Pain point]

### P2 - Medium Priority

4. **[Improvement]** - Impact: Medium, Effort: [High/Medium/Low]
   - What: [Description]
   - Why: [Pain point]

### P3 - Nice to Have

5. **[Improvement]** - Impact: Low-Medium, Effort: Low
   - What: [Description]
   - Why: [Pain point]

---

## Screenshots Index

| # | Filename | Step | Description |
|---|----------|------|-------------|
| 1 | `01-landing-first-impression.png` | 1 | Landing page first load |
| 2 | `02a-nav-explore.png` | 2 | Navigation - Explore section |
| 3 | `02b-nav-generate.png` | 2 | Navigation - Generate section |
| ... | ... | ... | ... |

---

*Assessment conducted by embodying [Persona Name], [brief description of persona and their context].*
*Platform: AI Paper Atlas (localhost:3000)*
*Date: [timestamp]*
```
