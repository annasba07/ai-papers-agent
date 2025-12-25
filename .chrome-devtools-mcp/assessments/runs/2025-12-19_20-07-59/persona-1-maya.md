# UX Assessment Report: Dr. Maya Chen

## Executive Summary
I'm Dr. Maya Chen, a CMU postdoc researching efficient transformers for mobile deployment. I tested AI Paper Atlas to find papers on efficient attention mechanisms with available code. The tool successfully found highly relevant papers using AI-powered search and includes a unique code generation feature, but critical usability issues around code availability indicators and filter clarity prevented me from achieving my secondary goal efficiently.

## Session Overview
- **Date**: December 19, 2025, 8:07 PM
- **Persona**: Dr. Maya Chen, 2nd-year postdoc, CMU Machine Learning Department
- **Primary goal**: Find recent papers on efficient attention mechanisms for mobile deployment
- **Goal completion**: 80% - Found excellent papers but code availability unclear
- **Overall rating**: 3.5/5

## Phase-by-Phase Findings

### Phase 1: First Contact
- **First impression**: Clean, professional interface with clear value proposition
- **Clarity score**: 4/5
- **Key observation**: Search box placeholder text perfectly matched my use case ("efficient attention for mobile deployment")
- **Screenshots**:
  - [01] 01-landing.png - Clean explore page, Has Code filter visible immediately

### Phase 2: Primary Goal Pursuit
- **Approach taken**: Direct keyword search for "efficient attention mechanisms mobile deployment"
- **Success level**: Found 6 highly relevant AI-powered results in 2.4 seconds, but struggled to identify which had code
- **Friction points**:
  - Has Code filter activated but still showed same 6 results (confusing - does that mean all 6 have code, or is filter broken?)
  - No visual indicator on paper cards showing code availability
  - Had to navigate to Discovery page to see code badges
- **Comparison to usual tools**: Search quality better than Semantic Scholar, but code discoverability worse than Papers with Code
- **Screenshots**:
  - [02] 02-search-results.png - 6 AI-powered results in 2360ms
  - [03] 03-search-scrolled.png - Paper cards with TL;DR summaries
  - [04] 04-paper-expanded.png - Full abstract with tabs but no code indicator
  - [05] 05-has-code-filter.png - Filter activated but no change in result count

### Phase 3: Discovery & Exploration
- **Features discovered**:
  - Discovery page with curated sections (High Impact, Rising Stars, Papers with Code)
  - AI Research Advisor modal
  - Reading List (browser-local storage)
  - Multi-agent code generation system
  - Smart Results vs Keyword Match differentiation
- **Missing features**:
  - Citation counts not visible on paper cards
  - No publication venue/conference information
  - No way to filter by date range
  - No export/download functionality for search results
- **Surprises**:
  - GOOD: Multi-agent code generation is genuinely innovative
  - BAD: Has Code filter behavior completely unclear
- **Screenshots**:
  - [06] 06-discovery-page.png - Discovery page with Quick Discovery cards
  - [07] 07-papers-with-code-loading.png - Papers showing "yes" badges and "View Code" links
  - [08] 08-back-to-explore.png - Returned to search cleared state

### Phase 4: Deep Dive
- **Paper examined**: "Learning to Focus: Focal Attention for Selective and Scalable Transformers"
- **Information quality**:
  - GOOD: Full abstract, TL;DR, clear efficiency claims (42% fewer parameters)
  - GOOD: Tabs for Summary, Related Papers, Benchmarks
  - MISSING: No code availability indicator, no citation count, no author affiliations
- **AI analysis assessment**: TL;DR summaries were accurate and helpful for quick scanning
- **Screenshots**:
  - [09] 09-advisor-modal.png - Research Advisor with suggested questions
  - [10] 10-focal-attention-expanded.png - Expanded paper with full details

### Phase 5: Practical Utility
- **Secondary goal result**: FAILED to efficiently identify papers with code through search interface
- **Workflow fit**: Would replace Semantic Scholar for discovery, but not Papers with Code for reproducibility
- **Adoption barriers**:
  - CRITICAL: Must fix code availability indicators on search results
  - Need citation counts for impact assessment
  - Need clearer filter feedback (what changed when I clicked Has Code?)
- **Screenshots**:
  - [11] 11-reading-list-empty.png - Reading list feature (empty state)
  - [12] 12-generate-page.png - Code generation feature

### Phase 6: Reflection
- **Would bookmark**: YES - The AI search quality alone is valuable
- **Would return**: YES, for paper discovery; NO for finding reproducible code (until fixed)
- **Would recommend**: YES to lab mates, with caveats about code discoverability
- **Top frustration**: Cannot easily tell which papers have code from search results
- **Top delight**: Multi-agent code generation system - this could save me weeks of reimplementation work

## Pain Point Assessment

| Pain Point | Addressed? | Evidence |
|------------|-----------|----------|
| Information Overload | **Yes** | AI-powered Smart Results reduced 138K papers to 6 highly relevant matches in 2.4s |
| Time Poverty | **Partial** | Fast search but unclear filters waste time; TL;DR summaries save time |
| Reproducibility Frustration | **No** | Code availability not visible in search; must navigate to Discovery > Papers with Code |
| Connection Blindness | **Partial** | "Related Papers" tab exists but didn't test deeply |
| Trend Anxiety | **Partial** | Discovery page has Rising/Hot Topics but seemed empty during test |

## Priority Improvements

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Add code availability badge to paper cards | High | Low | **P0** |
| Show visual feedback when filters are applied | High | Low | **P0** |
| Display citation counts on paper cards | High | Medium | **P1** |
| Clarify Has Code filter behavior (0→6 results confusing) | High | Low | **P0** |
| Add date range filter | Medium | Medium | P1 |
| Show author affiliations in paper cards | Low | Low | P2 |
| Add export/bibliography generation | Medium | Medium | P2 |

## Screenshots Index

| # | Filename | Phase | Description |
|---|----------|-------|-------------|
| 1 | 01-landing.png | 1 | Initial explore page, clean layout, Has Code filter visible |
| 2 | 02-search-results.png | 2 | 6 AI-powered results for "efficient attention mechanisms mobile deployment" |
| 3 | 03-search-scrolled.png | 2 | Scrolled view showing paper cards with Expand buttons |
| 4 | 04-paper-expanded.png | 2 | Expanded paper showing full abstract and tabs |
| 5 | 05-has-code-filter.png | 2 | Has Code filter activated (orange) but result count unchanged |
| 6 | 06-discovery-page.png | 3 | Discovery page with Quick Discovery sections |
| 7 | 07-papers-with-code-loading.png | 3 | Papers with Code section showing "yes" badges and "View Code" links |
| 8 | 08-back-to-explore.png | 3 | Returned to Explore page |
| 9 | 09-advisor-modal.png | 4 | Research Advisor modal with example questions |
| 10 | 10-focal-attention-expanded.png | 4 | Focal Attention paper expanded showing efficiency metrics |
| 11 | 11-reading-list-empty.png | 5 | Empty Reading List page |
| 12 | 12-generate-page.png | 5 | Multi-agent code generation feature |

## Final Verdict

As a researcher who spends 20-30 minutes daily fighting arXiv overload, **I would absolutely use this tool** for initial paper discovery. The AI-powered search is genuinely better than what I currently use - it found "Focal Attention" which achieves 42% parameter reduction, exactly the kind of efficiency work I need for mobile deployment.

However, the code discoverability issues are a **deal-breaker for replacing my full workflow**. When I clicked "Has Code" filter and saw no change in results, I genuinely couldn't tell if:
1. All 6 papers have code (great!)
2. The filter is broken (concerning)
3. The filter only works on the full dataset, not search results (confusing)

The multi-agent code generation feature is **genuinely innovative** and could save me weeks of reimplementation work. If it actually works, this alone would make the tool valuable.

**Star rating**: ⭐⭐⭐⭐☆ (4/5)

**Bottom line**: I'll bookmark this and use it for discovery starting tomorrow, but I'll keep using Papers with Code until the code availability indicators are fixed. Fix those three P0 issues and this becomes a 5-star tool that I'd recommend to my entire lab.
