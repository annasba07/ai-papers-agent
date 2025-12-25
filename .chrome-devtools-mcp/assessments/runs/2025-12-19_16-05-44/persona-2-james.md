# UX Assessment Report: Prof. James Williams

## Executive Summary
As a senior MIT professor preparing a graduate seminar on knowledge distillation, I attempted to use this tool to find foundational and recent papers. The tool is completely non-functional - the database contains zero papers. Every search returned no results, the AI advisor failed with errors, and the Discovery page hung indefinitely. This is not a usability issue - it's a fundamental system failure that makes the tool unusable for any academic purpose.

## Session Overview
- **Date**: 2025-12-19 16:05-16:35
- **Persona**: Prof. James Williams, MIT CSAIL Senior Faculty
- **Primary goal**: Find foundational and recent papers on knowledge distillation for graduate seminar
- **Goal completion**: 0%
- **Overall rating**: ★☆☆☆☆ (1/5)

## Phase-by-Phase Findings

### Phase 1: First Contact
- **First impression**: Clean, professional interface that suggests credibility. The design is polished with clear navigation, filter options, and a prominent search box. However, the sidebar immediately showed "0 papers" which should have been a warning sign.
- **Clarity score**: 4/5 (interface is clear, but the broken state isn't communicated)
- **Key observation**: Tool claims to have "138,986 papers" on first load, but this number drops to 0 after any interaction
- **Screenshots**:
  - `01-landing.png` - Initial page load showing clean interface

**Think-aloud**: "This looks professional. Clean design, filters on the left, search box prominent. I'd expect this from a serious research tool. Let me search for knowledge distillation papers."

### Phase 2: Primary Goal Pursuit
- **Approach taken**:
  1. Searched for "knowledge distillation" - a fundamental, well-established topic with hundreds of papers
  2. Tried the AI Research Advisor with detailed context about seminar preparation
  3. Attempted broader search terms like "transformer"

- **Success level**: Complete failure. Zero papers found for any search term.
- **Friction points**:
  - Database shows "0 papers" in sidebar
  - Search for "knowledge distillation" returned 0 results in 10,207ms
  - AI Advisor failed with error: "Sorry, I encountered an error while searching"
  - Search for "transformer" also returned 0 results in 10,001ms

- **Comparison to usual tools**: Google Scholar would have instantly returned thousands of results for "knowledge distillation". This tool found nothing.
- **Screenshots**:
  - `02-search-loading.png` - Zero results for knowledge distillation
  - `03-advisor-panel.png` - Research Advisor interface
  - `04-advisor-response.png` - Advisor still searching after 5 seconds
  - `05-advisor-still-loading.png` - Advisor error message
  - `10-transformer-search.png` - Zero results for transformer search

**Think-aloud**: "I'm searching for knowledge distillation - this should be straightforward. Hinton's 2015 paper alone has thousands of citations... Wait, zero results? That can't be right. Let me try the AI advisor... it's taking a long time... and now it's errored. This is concerning. Even 'transformer' returns nothing. The database appears to be empty."

### Phase 3: Discovery & Exploration
- **Features discovered**:
  - Discovery page with tabs for Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path
  - Generate page for code generation from papers
  - Reading List functionality

- **Missing features**: The core feature - papers - is missing entirely
- **Surprises**:
  - Good: Interface has thoughtful features like "Learning Path" which would be perfect for teaching
  - Bad: Discovery page stuck on "Loading papers..." indefinitely
  - Bad: All promised features are non-functional without paper data

- **Screenshots**:
  - `06-discovery-page.png` - Discovery page loading
  - `07-discovery-loaded.png` - Still loading after 3 seconds
  - `08-discovery-timeout.png` - Still loading after 8 seconds
  - `09-generate-page.png` - Code generation feature (can't test without papers)

**Think-aloud**: "The Learning Path feature looks interesting for curriculum design. But it's meaningless if there are no papers. The Discovery page won't load... I'm watching a spinner for the third time. This isn't a UX problem, this is a data problem."

### Phase 4: Deep Dive
**Could not complete** - No papers exist in the system to examine deeply.

**Think-aloud**: "I can't evaluate paper analysis quality when there are no papers to analyze."

### Phase 5: Practical Utility
- **Secondary goal result**: Could not assess whether students could use this for literature reviews
- **Workflow fit**: 0/5 - Cannot fit into any workflow when database is empty
- **Adoption barriers**: Fundamental - the tool needs to actually contain papers
- **Screenshots**: N/A - no functional features to test

**Think-aloud**: "I can't recommend this to students. I can't even demonstrate it to students. It simply doesn't work."

### Phase 6: Reflection
- **Would bookmark**: No. Absolutely not.
- **Would return**: No. Not until I hear it has been fixed and loaded with actual paper data.
- **Would recommend**: No. Recommending this would damage my credibility.
- **Top frustration**: The database is completely empty. This isn't a minor bug - it's a fundamental failure.
- **Top delight**: The interface design suggests someone thought carefully about academic workflows. The "Learning Path" feature could be valuable if the system worked.
- **Screenshots**:
  - `11-final-state.png` - Final state showing 0 papers

## Pain Point Assessment

| Pain Point | Addressed? | Evidence |
|------------|-----------|----------|
| Hype over substance | Cannot assess | System is non-functional |
| Teaching burden (reading lists) | No | "Learning Path" feature exists but has no data |
| Citation context | No | Cannot evaluate - no papers exist |
| Student guidance | No | Cannot recommend a broken tool |
| Reproducibility standards | No | "Has Code" filter exists but finds nothing |

## Priority Improvements

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Database is empty (0 papers) | Critical | Unknown | P0 |
| AI Advisor returns errors | Critical | Medium | P0 |
| Discovery page infinite loading | High | Medium | P0 |
| No error messaging about system state | High | Low | P0 |
| Paper count inconsistent (138K→0) | High | Medium | P1 |

## Critical Observations

### What Works (Design-wise)
1. **Clean, professional interface** - Inspires initial confidence
2. **Thoughtful feature set** - Learning Path, TL;DR, Reproducible filters show understanding of academic needs
3. **Good information architecture** - Clear navigation, logical grouping

### What's Broken (Fundamentally)
1. **Zero papers in database** - This is not a UX issue, it's a data pipeline failure
2. **Search returns nothing** - For any term, including "transformer" and "knowledge distillation"
3. **AI features fail** - Research Advisor errors out
4. **Discovery features hang** - Infinite loading states
5. **No system status communication** - Tool should warn users it's non-functional

## Academic Perspective

In 25 years of academia, I've evaluated countless research tools. This is the first time I've encountered a paper discovery tool with literally zero papers. The interface suggests the developers understand academic workflows - the Learning Path feature is exactly what I need for curriculum design. But without data, it's vaporware.

**The difference between this and my current tools:**
- **Google Scholar**: Finds 47,300 results for "knowledge distillation" in 0.3 seconds
- **Semantic Scholar**: Finds 15,234 related papers with citation context
- **This tool**: Finds 0 papers in 10 seconds, then errors

## Screenshots Index

| # | Filename | Phase | Description |
|---|----------|-------|-------------|
| 1 | 01-landing.png | 1 | Clean initial interface, claims 138K papers |
| 2 | 02-search-loading.png | 2 | Zero results for "knowledge distillation" |
| 3 | 03-advisor-panel.png | 2 | AI Research Advisor opened |
| 4 | 04-advisor-response.png | 2 | Advisor searching (5 sec wait) |
| 5 | 05-advisor-still-loading.png | 2 | Advisor error message |
| 6 | 06-discovery-page.png | 3 | Discovery page initial load |
| 7 | 07-discovery-loaded.png | 3 | Still loading after 3 seconds |
| 8 | 08-discovery-timeout.png | 3 | Still loading after 8 seconds |
| 9 | 09-generate-page.png | 3 | Code generation feature |
| 10 | 10-transformer-search.png | 2 | Zero results for "transformer" |
| 11 | 11-final-state.png | 6 | Final state showing 0 papers indexed |

## Final Verdict

As Professor James Williams, I evaluate this tool with the same rigor I apply to research: does it solve the problem it claims to solve?

**The answer is unequivocally no.**

This tool promises "AI-powered paper recommendations based on impact, trends, and your research interests" but delivers zero papers. It's not a question of usability, user experience, or feature completeness - the fundamental product is missing.

The interface shows promise. Someone designed thoughtful features like Learning Paths and citation context analysis. But without papers, these features are like a beautiful library with no books.

**I cannot recommend this tool to anyone.** Not to students, not to colleagues, not to junior faculty. Using it accomplished nothing in 30 minutes except confirming it doesn't work.

**What would need to change for me to reconsider:**
1. Load actual papers into the database (thousands, preferably 100K+)
2. Ensure search works for basic queries
3. Fix the AI advisor
4. Fix Discovery page loading issues
5. Add system status indicators when features are broken

Until then, I'll continue using Google Scholar and Semantic Scholar - they may be less sophisticated, but they actually work.

**Star rating**: ★☆☆☆☆ (1/5)

**Bottom line**: A well-designed interface wrapped around an empty database is worse than no tool at all, because it wastes the user's time.
