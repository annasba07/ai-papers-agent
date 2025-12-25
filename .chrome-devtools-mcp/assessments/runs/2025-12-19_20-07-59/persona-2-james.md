# UX Assessment Report: Professor James Williams

## Executive Summary

As a senior MIT professor attempting to build a graduate seminar reading list on knowledge distillation, I found the AI Paper Atlas **fundamentally unsuitable for academic curriculum development**. While the tool successfully surfaced recent research (2024-2025), it completely failed to provide access to foundational papers—specifically the seminal Hinton et al. 2015 "Distilling the Knowledge in a Neural Network" paper that any serious treatment of this topic requires. Without citation counts, publication dates, or the ability to sort by historical impact, this tool cannot support the pedagogical need to trace a field's evolution from its theoretical foundations to modern applications.

## Session Overview

- **Date**: 2025-12-19 20:07:59
- **Persona**: Professor James Williams, Senior Faculty (MIT NLP/ML)
- **Primary goal**: Build graduate seminar reading list covering knowledge distillation from foundational papers (Hinton 2015) to recent advances
- **Goal completion**: 15% (found recent papers but zero foundational work)
- **Overall rating**: 2/5

## Phase-by-Phase Findings

### Phase 1: First Contact

**First impression**: Landing page was clean and professional with clear value proposition about AI research discovery. The interface felt modern and the "Explore" tab was intuitive to start with.

**Clarity score**: 4/5 - Immediately understood it was for finding ML papers
**Key observation**: No indication this was recency-biased rather than comprehensive
**Screenshots**:
- [01] 01-landing.png - Professional design, clear purpose

**Emotion**: 4/5 - Promising start, looked credible

### Phase 2: Primary Goal Pursuit

**Approach taken**: Searched for "knowledge distillation" expecting to find both foundational and recent papers, with ability to sort chronologically or by citations to build a pedagogical progression.

**Success level**: Found 36 relevant papers (6 AI-matched + 30 keyword matches) but ALL were from late 2024 to December 2025. **Zero foundational papers** from the critical 2015-2020 period when the field was established.

**Friction points**:
1. No way to find the **Hinton 2015 paper** that originated the field
2. No visible citation counts to identify seminal work
3. No sorting options when viewing search results (dropdown only appeared on non-search pages)
4. Research Advisor feature **completely failed** with error message when I asked for "foundational and recent papers"
5. Cannot identify paper publication dates in search results (only "Dec 11, 2025" style relative dates)

**Comparison to usual tools**:
- **Google Scholar**: Shows citations, allows date range filtering, surfaces classics first
- **arXiv**: Can browse chronologically, see full publication history
- **Semantic Scholar**: Highlights "highly influential" papers with citation context

This tool is **significantly worse** for academic curriculum development. It's optimized for finding cutting-edge research, not understanding a field's intellectual history.

**Screenshots**:
- [02] 02-first-search.png - Search shows "Smart Results" with only 1 visible paper
- [03] 03-search-results.png - Recent 2024-2025 papers only, missing classics
- [04] 04-ask-advisor.png - Research Advisor panel opened
- [05] 05-advisor-query.png - Advisor returned ERROR (not helpful)
- [09] 09-kd-search-scrolled.png - Found actual KD papers (all recent)
- [10] 10-kd-more-papers.png - More 2025 papers, no foundational work

**Emotion**: 2/5 - Growing frustration at inability to find classics

### Phase 3: Discovery & Exploration

**Features discovered**:
- Reading List (browser-local bookmarking)
- Generate tab (multi-agent code generation from papers)
- Discovery tab (loaded but didn't explore fully)
- Quick Filters: "Has Code", "High Impact (7+)"
- Category filters (AI, ML, CV, etc.)
- Trending topics sidebar

**Missing features**:
- **Citation counts** (critical for academic assessment)
- **Publication year filtering** (essential for curriculum building)
- **"Most Cited" or "Most Influential" sorting** (to find foundational papers)
- **Historical coverage** (pre-2024 papers seem absent or unsurfaceable)
- **Export to BibTeX** (standard for academic workflows)
- **Pedagogical tools** (e.g., "learning path" or "curriculum builder")

**Surprises**:
- **Good**: Multi-agent code generation feature is innovative
- **Bad**: Complete absence of foundational papers in knowledge distillation
- **Bad**: Research Advisor feature doesn't work

**Screenshots**:
- [06] 06-discovery-tab.png - Discovery page loading
- [07] 07-back-to-explore.png - Explore showing search state
- [14] 14-generate-tab.png - Code generation feature (impressive but not for pedagogy)
- [15] 15-reading-list.png - Empty reading list

**Emotion**: 2/5 - Interesting features but fundamentally wrong tool for my needs

### Phase 4: Deep Dive

**Paper examined**: "Rethinking Decoupled Knowledge Distillation: A Predictive Distribution Perspective" (Dec 2025)

**Information quality**:
- **Helpful**: Full abstract available, tabs for Summary/Related Papers/Benchmarks, "Read on arXiv" link, "Generate Code" feature
- **Missing**:
  - NO citation count
  - NO author affiliations visible in expanded view
  - NO publication date (just "Dec 4, 2025" relative)
  - NO "cited by" section to understand impact
  - NO indication if this has code repository
  - NO comparison to related foundational work

For a **recent** paper (2025), the information might be adequate for a researcher staying current. But for building a curriculum, I need to know: Is this paper already influential? Who are the authors and their credibility? How does this relate to earlier work?

**AI analysis assessment**: Did not test AI-generated summaries deeply, but the TL;DR seemed accurate for the papers I glanced at.

**Screenshots**:
- [12] 12-paper-expanded.png - Paper detail with tabs
- [13] 13-paper-detail-full.png - Full abstract view with action buttons

**Emotion**: 3/5 - Good detail view for modern papers, but pedagogically incomplete

### Phase 5: Practical Utility

**Secondary goal result**: Could students use this for literature reviews? **Partially** - only if they need very recent papers (2024-2025) and don't need to understand field history.

**Workflow fit**: **Cannot replace** Google Scholar or Semantic Scholar for academic work because:
1. No access to foundational/historical papers
2. No citation metrics to assess influence
3. No export to reference managers
4. No tools for curriculum/syllabus building

**Adoption barriers**:
- Must still use Google Scholar to find classics
- No integration with academic workflows (Zotero, Mendeley, LaTeX)
- Reading List is browser-local (won't sync across devices)
- Cannot organize papers into topics/weeks for a syllabus

**Unique value**: The **code generation** feature is genuinely novel and could help students implement techniques. But that's implementation, not pedagogy.

**Screenshots**:
- [11] 11-kd-search-top.png - Search interface showing result count
- [08] 08-returned-to-explore.png - Main explore view

**Emotion**: 2/5 - Interesting tech demos, wrong tool for professors

### Phase 6: Reflection

**Would bookmark this?** No. It doesn't solve my primary problem (curriculum development from foundations to cutting edge).

**Would return tomorrow?** Only if I needed to find **very recent** papers (2024-2025) on a topic I already understand deeply. Not for learning or teaching.

**Would recommend to a colleague?**
- **To PhD students tracking latest work**: Yes, with caveats
- **To professors building courses**: No, completely inadequate
- **To industry ML engineers**: Maybe, for implementation ideas

**Top frustration**: **Cannot find foundational papers**. The Hinton 2015 distillation paper is THE starting point for any serious treatment of this topic. A tool that can't surface it is fundamentally broken for academic use.

**Top delight**: The multi-agent code generation system is genuinely innovative. If it works, that could help students move from theory to practice faster.

**One thing to fix immediately**: **Add citation counts and historical paper coverage**. Without the ability to identify and access seminal work, this tool is only useful for narrow "what's new in the last 6 months" queries.

**One thing to never change**: The clean, fast, modern interface. It's pleasant to use even when it's not delivering what I need.

**Final screenshot**:
- [15] 15-reading-list.png - Reading List empty state

**Overall ratings (1-5 scale)**:
- Usefulness for academic curriculum development: **1/5**
- Usefulness for tracking recent research: **4/5**
- Ease of use / learnability: **4/5**
- Trust in the AI-generated content: **3/5** (didn't test deeply)
- Likelihood to use regularly: **1/5**
- Likelihood to recommend to professors: **1/5**
- Likelihood to recommend to PhD students: **3/5**

## Pain Point Assessment

| Pain Point (from persona) | Addressed? | Evidence |
|---------------------------|-----------|----------|
| Finding foundational papers for pedagogical progression | **No** | Hinton 2015 paper completely absent; no pre-2024 content accessible |
| Assessing paper quality/influence for reading lists | **No** | No citation counts, no "most cited" sort, no influence metrics |
| Organizing papers into coherent curriculum | **No** | Only basic bookmarking; no syllabus builder or topic organization |
| Understanding field evolution over time | **No** | Cannot access historical papers; only see 2024-2025 snapshot |
| Balancing foundational theory with modern techniques | **No** | Modern techniques present, foundational theory completely missing |
| Ensuring readings are accessible to graduate students | **Partial** | TL;DR summaries helpful, but can't find beginner-friendly classics |

## Priority Improvements

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| **Add historical paper coverage (pre-2024)** | **Critical** | High | **P0** |
| **Show citation counts on all papers** | **Critical** | Medium | **P0** |
| **Enable "Most Cited" / "Most Influential" sorting** | High | Medium | **P0** |
| **Fix Research Advisor error handling** | Medium | Low | P1 |
| **Add publication date/year filtering** | High | Medium | P1 |
| **Add curriculum/syllabus builder tool** | High | High | P2 |
| **BibTeX export for reading lists** | Medium | Low | P2 |
| **Show author affiliations and credentials** | Medium | Low | P2 |

## Critical Finding: Data Coverage Gap

The most serious issue isn't UX—it's **data**. The system appears to only index very recent papers (2024-2025). For academic use, this is a dealbreaker:

- **What's needed**: Comprehensive coverage back to at least 2012 (the "deep learning revolution")
- **What's provided**: Excellent coverage of 2024-2025, nothing earlier accessible
- **Impact**: Tool is useless for teaching, literature reviews, or understanding field history

Even with perfect UX, without foundational papers, this tool cannot serve academia.

## Screenshots Index

| # | Filename | Phase | Description |
|---|----------|-------|-------------|
| 1 | 01-landing.png | 1 | Clean landing page, professional first impression |
| 2 | 02-first-search.png | 2 | First search showing "Smart Results" with 1 visible paper |
| 3 | 03-search-results.png | 2 | Recent 2024-2025 knowledge distillation papers |
| 4 | 04-ask-advisor.png | 2 | Research Advisor panel opened |
| 5 | 05-advisor-query.png | 2 | Advisor query returned ERROR message |
| 6 | 06-discovery-tab.png | 3 | Discovery page in loading state |
| 7 | 07-back-to-explore.png | 3 | Explore page showing search in progress |
| 8 | 08-returned-to-explore.png | 3 | Explore page after navigation |
| 9 | 09-kd-search-scrolled.png | 2 | Actual KD papers visible (all recent 2024-2025) |
| 10 | 10-kd-more-papers.png | 2 | More recent papers, no foundational work |
| 11 | 11-kd-search-top.png | 5 | Search interface showing 36 results count |
| 12 | 12-paper-expanded.png | 4 | Paper detail view with Summary/Related Papers/Benchmarks tabs |
| 13 | 13-paper-detail-full.png | 4 | Full abstract with "Read on arXiv" and "Generate Code" buttons |
| 14 | 14-generate-tab.png | 5 | Multi-agent code generation feature (5-agent system) |
| 15 | 15-reading-list.png | 6 | Empty reading list (browser-local storage) |

## Final Verdict

As a professor who has taught graduate ML courses for two decades, I approach new tools with both enthusiasm and scrutiny. AI Paper Atlas demonstrates impressive technical sophistication—the code generation feature is genuinely novel, the interface is polished, and the AI-powered search clearly works for recent publications.

But **the tool fundamentally misunderstands academic needs**.

In academia, we don't just need "the latest papers"—we need to understand how ideas evolved. When I teach knowledge distillation, I start with Hinton's 2015 paper not because it's the best technique (it's not), but because it's the clearest explanation of the core insight. Then I show how Zagoruyko & Komodakis (2017) extended it, how DKD (2022) refined it, and finally how 2024-2025 papers are applying it to LLMs and multimodal systems.

**This tool shows me only the final chapter of that story.** It's like teaching calculus by starting with Stokes' theorem—technically advanced, but pedagogically backwards.

For a tool targeting "research intelligence," the absence of citation counts is baffling. Citations are the primary signal of influence in academia. Without them, I'm flying blind—unable to distinguish between a paper with 3000 citations (field-defining) and one with 30 (interesting but niche).

The irony is that the infrastructure is mostly there. The search works, the UI is excellent, the code generation feature shows real ambition. The problem is **data coverage and academic tooling**. Fix those, and this could genuinely compete with Google Scholar for course planning.

As it stands, I'd use this tool for exactly one thing: Finding very recent papers (last 6 months) on a topic I already understand deeply from years of reading the foundational literature elsewhere.

**Star rating**: ⭐⭐☆☆☆ (2/5)

**Bottom line**: Impressive technology demonstrator, but not ready for academic curriculum development due to missing historical papers and lack of citation metrics.

---

**Recommendation to developers**: If your goal is to serve academics (professors and PhD students doing lit reviews), you must:
1. Index papers back to at least 2012 (ideally earlier for classic ML)
2. Add citation counts from Google Scholar or Semantic Scholar
3. Enable sorting/filtering by citations, year, and influence
4. Build curriculum/syllabus tools (not just reading lists)
5. Export to BibTeX and integrate with reference managers

If your goal is to serve industry ML engineers who just need the latest techniques, the current tool is fine. But then you should market it as such, not as "research intelligence" which implies comprehensive scholarly coverage.
