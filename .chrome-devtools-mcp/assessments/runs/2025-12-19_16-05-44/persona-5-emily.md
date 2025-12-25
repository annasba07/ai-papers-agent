# UX Assessment Report: Dr. Emily Zhang

## Executive Summary
As a climate scientist trying to find ML techniques for weather prediction, this tool was completely unusable. The database appears empty (0 papers indexed), all searches returned zero results, and even the AI advisor crashed when asked about cross-domain applications. For interdisciplinary researchers like me, this tool doesn't just fail to bridge the domain gap—it doesn't work at all.

## Session Overview
- **Date**: 2025-12-19
- **Persona**: Dr. Emily Zhang, Climate Scientist applying ML to atmospheric science
- **Primary goal**: Find papers on transformers for time series prediction in climate modeling
- **Goal completion**: 0% - Could not find a single paper
- **Overall rating**: 1/5

## Phase-by-Phase Findings

### Phase 1: First Contact
- **First impression**: Clean UI, but immediately concerning that categories are all ML-focused (Computer Vision, NLP, etc.) with no mention of scientific domains like climate, physics, or geoscience.
- **Clarity score**: 3/5 - Clear it's for AI papers, unclear if it's for domain scientists
- **Key observation**: The sidebar showed "138,986 papers" initially, but this turned out to be misleading
- **Screenshots**:
  - [01] 01-landing.png - Categories feel ML-centric, no domain science representation
  - [02] 02-landing-scrolled.png - All papers shown are vision/ML, none climate-related

### Phase 2: Primary Goal Pursuit
- **Approach taken**: Searched for "transformers time series climate data" - exactly how I'd describe my research need
- **Success level**: Complete failure - 0 results found
- **Friction points**:
  - Search returned "0 results" despite sidebar claiming papers exist
  - Database appears broken or empty
  - No guidance on what terms might work
- **Comparison to usual tools**: Google Scholar would have found thousands of papers. This found nothing.
- **Screenshots**:
  - [03] 03-search-results.png - "No papers found" for domain-specific query
  - [07] 07-transformer-search.png - Even simple "transformer" returned 0 results

### Phase 3: Discovery & Exploration
- **Features discovered**:
  - Research Advisor (AI assistant)
  - Discovery page with categories
  - Filter sidebar
- **Missing features**:
  - No working paper database
  - No cross-domain search capabilities
  - No papers to actually browse
- **Surprises**:
  - BAD: The AI advisor crashed when I described my research problem
  - BAD: The Discovery page shows "Loading papers..." indefinitely
  - BAD: "1 Issue" badge suggests known problems
- **Screenshots**:
  - [04] 04-advisor-panel.png - Advisor examples all ML applications, no science domains
  - [05] 05-advisor-response.png - Advisor searching for my climate query
  - [06] 06-advisor-results.png - "Sorry, I encountered an error" - even AI can't help
  - [08] 08-discovery-page.png - Discovery page stuck loading

### Phase 4: Deep Dive
- **Paper examined**: None - no papers were accessible
- **Information quality**: N/A - tool completely non-functional
- **AI analysis assessment**: The AI advisor crashed when given a cross-domain query about weather prediction
- **Screenshots**: None available - couldn't access any papers

### Phase 5: Practical Utility
- **Secondary goal result**: Failed - couldn't find papers that explain ML concepts accessibly
- **Workflow fit**: 0/5 - Cannot replace Google Scholar when it returns zero results
- **Adoption barriers**:
  - Database appears completely empty
  - Search doesn't work
  - AI advisor crashes on cross-domain queries
  - No domain science vocabulary
- **Screenshots**: None - no functionality to test

### Phase 6: Reflection
- **Would bookmark**: No - the tool doesn't work
- **Would return**: No - Google Scholar is infinitely more useful
- **Would recommend**: Absolutely not - would warn colleagues to avoid
- **Top frustration**: The tool appears completely broken. Zero papers found, database shows "0 papers", AI crashes.
- **Top delight**: None - found no working functionality
- **One thing to fix immediately**: Fix the database - it shows "0 papers indexed" which suggests a critical infrastructure failure
- **One thing to never change**: The UI is clean and professional-looking (though it doesn't matter if nothing works)

## Pain Point Assessment

| Pain Point | Addressed? | Evidence |
|------------|-----------|----------|
| Terminology gap between ML and climate science | No | Search for "climate data" returned 0 results |
| Cross-domain discovery (NLP→climate) | No | No papers found, AI crashed when asked |
| Adaptation complexity (will it work on my data?) | No | Couldn't access any papers to evaluate |
| Limited ML background needs explanation | No | No papers to read explanations from |
| Justifying techniques to climate peers | No | No content accessible |

**Critical Finding**: All pain points are unaddressable because the fundamental infrastructure is broken. The database shows "0 papers indexed" and all searches fail.

## Critical Issues Found

### P0: Database Empty/Broken
- **Evidence**: Sidebar shows "0 papers indexed"
- **Impact**: Tool is completely unusable
- **User Impact**: Cannot accomplish any research task
- **Screenshot**: [03] 03-search-results.png, [07] 07-transformer-search.png

### P0: Search Returns Zero Results
- **Evidence**: Every query tried returned "No papers found"
- **Impact**: Core functionality completely broken
- **Queries tried**:
  - "transformers time series climate data" - 0 results
  - "transformer" - 0 results
- **Screenshot**: [03], [07]

### P0: AI Advisor Crashes on Cross-Domain Queries
- **Evidence**: "Sorry, I encountered an error while searching"
- **Impact**: The one feature that might help bridge domains also doesn't work
- **Screenshot**: [06] 06-advisor-results.png

### P1: No Domain Science Vocabulary
- **Evidence**: All examples, categories, trending topics are pure ML
- **Impact**: Domain scientists feel unwelcome/excluded
- **Examples**: Categories are "Computer Vision", "NLP", etc. No "Climate", "Physics", "Geoscience"
- **Screenshot**: [01], [02], [04]

### P1: Discovery Page Indefinitely Loading
- **Evidence**: Shows "Loading papers..." with spinner
- **Impact**: Cannot browse or discover papers
- **Screenshot**: [08] 08-discovery-page.png

## Priority Improvements

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Fix database (0 papers indexed) | Critical | Unknown | P0 |
| Fix search functionality | Critical | Unknown | P0 |
| Fix AI advisor errors | High | Unknown | P0 |
| Add domain science vocabulary | High | Medium | P1 |
| Add cross-domain search examples | High | Low | P1 |
| Fix Discovery page loading | Medium | Unknown | P1 |

## Screenshots Index

| # | Filename | Phase | Description |
|---|----------|-------|-------------|
| 1 | 01-landing.png | 1 | Initial landing page - ML-centric categories |
| 2 | 02-landing-scrolled.png | 1 | Papers shown all vision/ML, no climate |
| 3 | 03-search-results.png | 2 | Zero results for "transformers time series climate data" |
| 4 | 04-advisor-panel.png | 3 | AI Advisor examples all ML apps, no science |
| 5 | 05-advisor-response.png | 3 | Advisor searching for climate query |
| 6 | 06-advisor-results.png | 3 | AI error: "Sorry, I encountered an error" |
| 7 | 07-transformer-search.png | 2 | Even "transformer" alone = 0 results |
| 8 | 08-discovery-page.png | 3 | Discovery stuck on "Loading papers..." |

## Final Verdict

This tool is **completely unusable** in its current state. The database appears to be empty (showing "0 papers indexed"), all searches return zero results, and the AI advisor crashes when asked about interdisciplinary research.

As a climate scientist trying to apply ML to my work, I need tools that:
1. Actually contain papers I can read
2. Understand queries that mix domain terms ("climate", "weather") with ML terms ("transformer", "attention")
3. Help me discover techniques from other domains that might apply to my data
4. Explain ML concepts in accessible ways

This tool does none of these things. It appears to have a critical infrastructure failure preventing any basic functionality.

### For Interdisciplinary Researchers

The design suggests this tool was built entirely for ML experts, with no consideration for domain scientists:
- All examples assume ML knowledge and ML applications
- Categories are ML subdisciplines, not application domains
- No vocabulary from physical sciences, climate, biology, etc.
- AI advisor crashes when given a cross-domain problem

**Even if the database worked**, the tool would still struggle with cross-domain discovery because it speaks only one language: ML-native terminology.

**Star rating**: ⭐☆☆☆☆ 1/5

**Bottom line**: Do not use this tool. Google Scholar finds orders of magnitude more papers and actually works. This tool appears to have a critical database failure that makes it completely non-functional, and even if that were fixed, it shows no understanding of cross-domain research needs.
