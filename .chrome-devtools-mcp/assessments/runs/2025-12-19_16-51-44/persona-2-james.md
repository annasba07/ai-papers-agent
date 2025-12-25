# UX Assessment Report: Professor James Williams

## Executive Summary

As a senior MIT CSAIL professor preparing a graduate seminar on knowledge distillation, I evaluated AI Paper Atlas to determine if it could help me build a comprehensive reading list spanning foundational classics to cutting-edge research. **The tool failed my primary goal**: it prioritizes recent papers (2024-2025) so heavily that foundational works like Hinton's seminal 2015 "Distilling the Knowledge in a Neural Network" paper are completely absent. While the interface is polished and some features show promise, this recency bias makes it unsuitable for academic curriculum design where students need to understand the intellectual progression of a field.

## Session Overview

- **Date**: 2025-12-19 16:51:44
- **Persona**: Professor James Williams, MIT CSAIL, 25 years experience, h-index 75
- **Primary goal**: Find both foundational AND recent papers on knowledge distillation for a graduate seminar
- **Goal completion**: 15% (found recent papers but zero foundational work)
- **Overall rating**: 2/5

## Phase-by-Phase Findings

### Phase 1: First Contact

**First impression**: Clean, professional interface with 138,986 papers indexed. The Explore page immediately presented filters (Has Code, High Impact, Category) and a prominent search box with helpful placeholder text suggesting natural language queries.

**Clarity score**: 4/5 - The purpose is immediately clear: search and filter AI research papers.

**Key observation**: The interface feels polished and modern, similar to contemporary research tools, but more visually appealing than Google Scholar. The "Ask Advisor" button suggests AI capabilities beyond simple keyword matching.

**Screenshots**:
- 01-landing.png: Initial Explore page showing clean layout and filters

### Phase 2: Primary Goal Pursuit

**Approach taken**: I searched for "knowledge distillation" expecting to find both classic foundational papers (particularly Hinton 2015) and recent work. My mental model was that a comprehensive research database would surface papers by relevance and impact across all years.

**Success level**: **Failed fundamentally**. The system returned 36 results (6 AI-matched + 30 keyword), but every single paper was from November-December 2025. Not one foundational paper appeared. When I applied the "High Impact (7+)" filter hoping to surface classics, it reduced to 18 papers but still showed only 2024-2025 publications.

**Friction points**:
1. **Temporal bias**: The tool appears to be a "recent papers database" rather than a comprehensive archive. This is a dealbreaker for academic use.
2. **No temporal controls**: No date range picker or ability to explicitly search for older, foundational work
3. **Impact metric unclear**: "High Impact (7+)" didn't help find classics - unclear what this measures

**Comparison to usual tools**: Google Scholar would immediately show Hinton 2015 at the top. arXiv lets me filter by date. Semantic Scholar shows citation counts and paper influence. This tool is dramatically worse for building a syllabus because it hides the intellectual history of the field.

**Screenshots**:
- 02-search-results.png: All 36 results from Nov/Dec 2025
- 03-high-impact-filter.png: Still only recent papers after filtering

### Phase 3: Discovery & Exploration

**Features discovered**:
1. **Discovery page**: Curated high-impact papers (though still very recent - saw a Hopfield appreciation paper rated 10/10 impact)
2. **Learning Path**: "Curated learning progression by difficulty" - this seemed perfect for my seminar!
3. **Reading List**: Bookmark papers for later (browser local storage)
4. **Generate**: Multi-agent code generation from papers (5-agent TDD system)

**Missing features**:
1. **Citation counts**: Essential for evaluating paper influence
2. **Publication year/date in results**: Have to click into each paper to see when it was published
3. **Date range filter**: Cannot search by year or date range
4. **"Sort by citations"**: No way to find most-cited foundational papers
5. **Author search**: Cannot find papers by specific researchers (e.g., Hinton, Bengio)

**Surprises**:
- **Negative**: The Learning Path feature claimed to be "curated learning progression by difficulty" but when I entered "knowledge distillation," it started at "1. Intermediate" with a 2025 paper. No "Beginner" or "Foundational" section existed despite the interface suggesting progressive difficulty levels. This is false advertising for an educational feature.
- **Positive**: The multi-agent code generation feature is genuinely novel and could be valuable for students trying to implement papers.

**Screenshots**:
- 04-discovery-page.png: Discovery page loading
- 05-discovery-loaded.png: Hopfield paper with 10/10 impact
- 06-learning-path.png: Learning Path input interface
- 07-learning-path-generating.png: Generated path with "Intermediate" level
- 08-learning-path-scrolled.png: "Expert" section visible, no beginner section
- 09-learning-path-top.png: Confirmed path starts at Intermediate level

### Phase 4: Deep Dive

**Paper examined**: "Rethinking Decoupled Knowledge Distillation: A Predictive Distribution Perspective" (Dec 2025)

**Information quality**:
- **Good**: Full abstract displayed inline when expanded, clean presentation
- **Good**: Multiple tabs (Summary, Related Papers, Benchmarks) suggest depth
- **Good**: "Read on arXiv" and "Generate Code" buttons provide clear next actions
- **Disappointing**: The "Summary" tab just showed the same full abstract again - I expected AI-generated insights, key contributions, or critical analysis

**AI analysis assessment**: The Summary tab was a missed opportunity. As an experienced researcher, I can read abstracts myself. I wanted the AI to tell me:
- What are the key contributions vs. prior work?
- What are the limitations or weaknesses?
- How does this compare to other approaches in the field?
- Is this a methodology paper, empirical results, or theoretical advancement?

The tool provides no value-add beyond what I'd get reading the arXiv abstract.

**Screenshots**:
- 10-paper-expanded.png: Paper card with tabs and action buttons
- 11-summary-tab.png: Summary tab showing identical abstract content

### Phase 5: Practical Utility

**Secondary goal result**: I wanted to assess if students could use this for literature reviews. **No** - students would get a distorted view of the field by only seeing the last 2 months of papers. They'd miss the conceptual foundation entirely. A student using only this tool would think knowledge distillation was invented in 2024.

**Workflow fit**: The tool has some nice UX touches (bookmark feature, reading list, AI advisor), but none of these matter if the paper corpus is fundamentally incomplete. I cannot replace Google Scholar or Semantic Scholar with this because:
1. It lacks foundational papers
2. No citation metrics to gauge influence
3. No way to understand which papers built on which prior work

**Adoption barriers**:
1. **Critical**: Need complete historical coverage, not just recent papers
2. **Critical**: Need citation counts and citation graph to understand paper relationships
3. **Important**: Learning Path must actually start with foundational/beginner papers
4. **Important**: Summary tab needs real AI analysis, not just abstract regurgitation
5. **Nice to have**: "Has Code" filter appears non-functional (didn't reduce result count from 36)

**Screenshots**:
- 12-has-code-filter.png: Filter active but still 36 results (same as before)
- 13-reading-list.png: Empty reading list with clear instructions
- 14-generate-page.png: Multi-agent code generation interface

### Phase 6: Reflection & Final Verdict

**Would bookmark**: No. The tool doesn't solve any problem I currently have.

**Would return**: No. Every time I need to find papers, I need access to foundational work, not just the last 60 days of arXiv.

**Would recommend to colleagues**: Only with a strong caveat: "This shows very recent papers if you already know the field and want to stay current. Do NOT use it for literature reviews, teaching, or learning a new area."

**Would recommend to students**: Absolutely not in its current state. Students would develop a fundamentally broken understanding of knowledge distillation without seeing Hinton 2015, the early logit-based vs. feature-based debates, or the progression of techniques over time.

**Top frustration**: The Learning Path feature is misleading. It promises "curated learning progression by difficulty" but delivers only recent papers starting at "Intermediate" level. For a field like knowledge distillation with a clear foundational paper (Hinton 2015), this is inexcusable. A true learning path would be:
- **Beginner**: Hinton et al. 2015 - the foundational paper
- **Intermediate**: Feature-based distillation methods (FitNets, etc.)
- **Advanced**: Recent applications and extensions
- **Expert**: Cutting-edge techniques from 2024-2025

Instead, I got papers from the last 2 months only.

**Top delight**: The multi-agent code generation feature is genuinely innovative. The 5-agent system (Paper Analyzer → Test Designer → Code Generator → Test Executor → Debugger) with TDD principles could help students bridge the gap from paper to implementation. This is the one feature that offers something novel beyond existing tools.

**One thing to fix immediately**: Add foundational papers to the database and fix the temporal bias. A research tool is useless for academics if it only shows the most recent 2-3 months of publications. Either index papers back to at least 2012-2015 (the "modern deep learning era"), or clearly label this as a "recent papers only" tool so users don't waste time expecting comprehensive coverage.

**One thing to never change**: The clean, uncluttered interface. Google Scholar is functional but ugly. This tool feels modern and pleasant to use. The visual design, typography, and interaction patterns are all excellent.

**Screenshots**:
- 15-final-state.png: Back at main Explore page

## Pain Point Assessment

| Pain Point | Addressed? | Evidence |
|------------|-----------|----------|
| Finding foundational + recent papers for seminar | No | Zero foundational papers appear; only 2024-2025 results |
| Understanding which papers are most influential | Partial | "High Impact" filter exists but unclear metric; no citation counts |
| Identifying papers with reproducible code | No | "Has Code" filter doesn't reduce results (36 → 36) |
| Helping students learn field progressively | No | Learning Path starts at "Intermediate" with recent papers only |
| Quickly assessing if paper is worth reading | Partial | Abstracts shown but "Summary" tab offers no AI insights |
| Staying current with latest research | Yes | Excellent coverage of November-December 2025 papers |

## Priority Improvements

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Add papers from 2012-2025, especially foundational classics | Critical | High (data ingestion) | P0 |
| Fix Learning Path to include beginner/foundational papers | Critical | Medium (query logic) | P0 |
| Add citation counts to paper cards | High | Medium (data source) | P1 |
| Make Summary tab provide real AI analysis, not just abstract | High | Medium (LLM prompting) | P1 |
| Add publication date/year visible in search results | High | Low (UI change) | P1 |
| Add date range filter to search interface | High | Medium (query + UI) | P1 |
| Fix "Has Code" filter (currently non-functional) | Medium | Low (bug fix) | P2 |
| Add author search capability | Medium | Medium (indexing) | P2 |
| Add "Sort by citations" option | Medium | Medium (ranking logic) | P2 |

## Screenshots Index

| # | Filename | Phase | Description |
|---|----------|-------|-------------|
| 1 | 01-landing.png | 1 | First impression of Explore page with filters and 138,986 papers |
| 2 | 02-search-results.png | 2 | Search for "knowledge distillation" returning 36 recent papers |
| 3 | 03-high-impact-filter.png | 2 | High Impact filter applied, still only recent papers visible |
| 4 | 04-discovery-page.png | 3 | Discovery page while loading |
| 5 | 05-discovery-loaded.png | 3 | Discovery page showing Hopfield paper (10/10 impact) |
| 6 | 06-learning-path.png | 3 | Learning Path feature input interface |
| 7 | 07-learning-path-generating.png | 3 | Generated learning path starting at "Intermediate" level |
| 8 | 08-learning-path-scrolled.png | 3 | Expert section visible, no beginner section found |
| 9 | 09-learning-path-top.png | 3 | Confirmed path starts at Intermediate, missing foundational papers |
| 10 | 10-paper-expanded.png | 4 | Paper card expanded showing abstract, tabs, and action buttons |
| 11 | 11-summary-tab.png | 4 | Summary tab displaying same abstract, no AI insights |
| 12 | 12-has-code-filter.png | 5 | Has Code filter active but result count unchanged (36) |
| 13 | 13-reading-list.png | 5 | Empty reading list with clear instructions for bookmarking |
| 14 | 14-generate-page.png | 5 | Multi-agent code generation feature with 5-agent TDD system |
| 15 | 15-final-state.png | 6 | Final state back at Explore page |

## Final Verdict

From the perspective of a senior professor who has taught graduate seminars for two decades, AI Paper Atlas is fundamentally unsuitable for academic use in its current form. The tool suffers from severe **recency bias** that makes it impossible to construct proper educational materials or conduct comprehensive literature reviews.

When I teach knowledge distillation, my students need to understand the evolution of ideas:
- Where did the concept originate? (Hinton 2015)
- What were the early debates and alternative approaches? (logit vs. feature distillation)
- How has the field progressed over the years?
- What are the current frontiers?

This tool only answers the last question. It's like trying to teach American history using only newspapers from the last two months - you'd get current events but no context, no causation, no understanding of how we got here.

The **Learning Path** feature is particularly disappointing because it promises exactly what I need ("curated learning progression by difficulty") but delivers a shallow substitute. Starting students at "Intermediate" level with 2025 papers would leave them confused and missing critical conceptual foundations.

That said, I see genuine potential in two areas:

1. **The multi-agent code generation** is innovative and could help students bridge the theory-implementation gap. This addresses a real pain point in research education.

2. **The interface design** is excellent - clean, modern, and pleasant to use. The UX is significantly better than Google Scholar's utilitarian design.

If the developers fix the temporal bias and add comprehensive historical coverage, this could become a valuable tool for academics. Until then, it's a "recent papers aggregator" that's useful only for researchers who already deeply understand their field and want to stay current.

**Star rating**: ⭐⭐☆☆☆ (2/5)

**Bottom line**: I would not use this tool for my seminar preparation, nor would I recommend it to students or colleagues, unless it adds foundational papers from 2012-2025 and fixes the Learning Path to actually start with beginner-level classics.

---

**Technical Details:**
- Assessment conducted: December 19, 2025
- Application URL: http://localhost:3000
- Browser: Chrome (via Chrome DevTools MCP)
- Total screenshots captured: 15
- Assessment duration: ~25 minutes
- Persona: Professor James Williams (MIT CSAIL, NLP/Deep Learning)
