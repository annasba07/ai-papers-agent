# UX Assessment Report: Prof. James Williams
**Date**: December 21, 2025
**Session Duration**: ~4 minutes (09:55:38 - 09:58:46)
**Persona**: Senior NLP Faculty, MIT CSAIL
**Task**: Prepare seminar reading list on efficient language models

---

## Executive Summary

The AI advisor feature successfully identified relevant recent papers on model compression, but critically failed to surface foundational work (BERT, DistilBERT) that students need. For a graduate seminar, this recency bias undermines pedagogical value. The tool feels optimized for practitioners, not educators building learning progressions.

---

## Session Timeline

| Time | Step | Action | Outcome | Emotion |
|------|------|--------|---------|---------|
| 09:55:38 | 1 | Landing page load | 30 papers visible, filters clear | 3/5 |
| 09:55:40 | 2 | Navigate to Discovery | Error: "Failed to fetch impact papers" | 2/5 |
| 09:55:48 | 3 | Return to Explore, type query | "efficient language models" → 30 results, all irrelevant CV papers | 2/5 |
| 09:56:12 | 4 | Click Ask Advisor | Retrieved 6 highly relevant papers in 1781ms | 4/5 |
| 09:56:58 | 5 | Detailed advisor query | 5 papers + follow-up questions, no foundational works | 3/5 |
| 09:57:20 | 6-9 | Test filters | Has Code + Beginner filters → same 6 papers | 2/5 |
| 09:58:30 | 10 | Explore Generate page | Code generation feature discovered | 3/5 |

**Key Metric**: Advisor response time 1.7-2.8s (acceptable)

---

## Step-by-Step Analysis

### Step 1: First Impression (Landing Page)
**Screenshot**: `01-landing-first-impression.png`

The landing page showed 30 recent papers with visible filters. Clean professional design. However, immediately noticed:
- No citation counts visible on paper cards
- No indication of "foundational vs. recent" in the UI
- "Trending Topics" section empty ("No trending data available")

**Emotion**: 3/5 (cautious) - Looks professional but unclear if it understands academic curation needs.

### Step 2: Navigation Discovery
**Screenshot**: `02-discovery-nav.png`

Clicked "Discovery" to explore curated collections. Encountered error: "Failed to fetch impact papers". The page showed discovery tabs (Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path) but couldn't load content.

**Emotion**: 2/5 (frustrated) - A feature designed for discovery is broken. This would have been useful for identifying high-impact foundational work.

### Step 3: Basic Keyword Search
**Screenshots**: `03-back-to-explore.png`, `04-search-query-entered.png`

Returned to Explore, typed "efficient language models". Results showed:
- 30 papers labeled "KEYWORD MATCH"
- Top results: "Generative View Stitching", "Uniform Discrete Diffusion", "Routing Matters in MoE"
- All computer vision/diffusion papers, not language models

**Critical Issue**: Keyword search is essentially broken for NLP queries. A search for "efficient language models" returning CV papers is unacceptable for academic use.

**Emotion**: 2/5 (disappointed) - This is worse than Google Scholar.

### Step 3.5: Research Advisor (Semantic Search)
**Screenshots**: `05-advisor-clicked.png`, `06-advisor-query-typed.png`, `07-advisor-searching.png`, `08-advisor-response.png`

Clicked "Ask Advisor" button. The AI-powered search **immediately** improved relevance:

**Smart Results** (6 papers, 1780ms):
1. EfficientXpert: Efficient Domain Adaptation for Large Language Models via Propagation-Aware Pruning
2. E³-Pruner: Towards Efficient, Economical, and Effective Layer Pruning for Large Language Models
3. MuonAll: Muon Variant for Efficient Finetuning of Large Language Models
4. Iterative Layer-wise Distillation for Efficient Compression of Large Language Models
5. Reversing Large Language Models for Efficient Training and Fine-Tuning
6. SingleQuant: Efficient Quantization of Large Language Models in a Single Pass

**Follow-up questions offered**:
- "How do these methods scale to larger models?"
- "What are the training costs involved?"
- "Find papers that cite these works"

Then I asked a more detailed query: "I need papers on model compression and distillation for language models, especially BERT and transformer variants. Looking for foundational papers and recent techniques."

**Response** (5 papers):
- Can bidirectional encoder become the ultimate winner for downstream applications of foundation models?
- Comparison of Large Language Models for Deployment Requirements
- Iterative Layer-wise Distillation for Efficient Compression of Large Language Models
- Cache Me If You Must: Adaptive Key-Value Quantization for Large Language Models
- AfroXLMR-Comet: Multilingual Knowledge Distillation with Attention Matching for Low-Resource languages

**Critical Gap**: Despite explicitly requesting "foundational papers" and mentioning "BERT", the system returned ONLY recent 2024-2025 papers. Missing:
- DistilBERT (Sanh et al., 2019) - THE foundational distillation paper for BERT
- ALBERT (Lan et al., 2019) - Parameter-efficient BERT variant
- MobileBERT (Sun et al., 2020) - Mobile-optimized BERT compression
- TinyBERT (Jiao et al., 2020) - Multi-stage distillation

**Emotion**: 4/5 → 3/5 (hopeful then disappointed) - The advisor understands semantic queries well, but has a severe recency bias that makes it unsuitable for creating learning progressions.

### Step 4-5: Code Availability Check
**Screenshots**: `10-has-code-filter.png`, `11-code-filter-applied.png`

Applied "Has Code" filter. Same 6 papers remained. No visual indication on paper cards of which have code, GitHub stars, or repo links.

**Missing**: For reproducibility-focused academics, I need:
- GitHub repo links prominently displayed
- Star counts to gauge community adoption
- Last commit date (is the code maintained?)
- Issues/PRs count (is it production-ready?)

**Emotion**: 3/5 (neutral) - Filter works but provides minimal value without metadata.

### Step 6: Learning Path / Difficulty Filters
**Screenshots**: `12-difficulty-filter.png`, `13-beginner-filter-applied.png`

Applied "Beginner" difficulty filter on top of "Has Code". Still returned the same 6 papers.

**Critical Issue for Teaching**: A "Beginner" filter that returns papers on "Adaptive Key-Value Quantization" and "Propagation-Aware Pruning" is mis calibrated. Beginner-level papers for my seminar would be:
- Attention is All You Need (foundational understanding)
- BERT (architecture basics)
- DistilBERT (introduction to distillation)

The difficulty tagging appears broken or based on wrong criteria (writing clarity vs. technical prerequisites?).

**Emotion**: 2/5 (frustrated) - This feature promised to help create learning progressions but doesn't deliver.

### Step 7-10: Additional Exploration
**Screenshot**: `15-generate-navigation.png`

Discovered the "Generate" page advertising a "5-agent system" to turn papers into working code. Interesting concept but not relevant to my immediate task of curating a reading list.

**Emotion**: 3/5 (curious) - Potentially useful for students implementing papers, but didn't test it.

---

## Pain Point Assessment

### 1. Curation Burden ❌ **NOT SOLVED**
**Problem**: Need to maintain reading lists for graduate seminar, field moves too fast.

**Outcome**: The tool helped find RECENT papers efficiently but failed to help build a coherent reading list from foundational to advanced. The recency bias means I still need to manually add the classics.

### 2. Student Guidance ⚠️ **PARTIALLY SOLVED**
**Problem**: PhD students ask "what should I read?" in newer subfields.

**Outcome**: If a student asks about "the latest in model compression," the advisor is excellent. If they ask "where do I start?" the tool doesn't provide learning paths.

### 3. Reproducibility Standards ⚠️ **PARTIALLY ADDRESSED**
**Problem**: Want papers with code to set lab standards.

**Outcome**: "Has Code" filter exists but lacks critical metadata (stars, maintenance status, documentation quality). I can't distinguish between "toy code" and "production-ready implementation."

### 4. Field Breadth ✅ **POTENTIALLY SOLVED**
**Problem**: Can't keep up with vision-language, audio, multimodal work.

**Outcome**: Didn't test cross-domain queries, but semantic search seems capable of bridging subfields.

### 5. Historical Context ❌ **MAJOR FAILURE**
**Problem**: Young researchers miss foundational work.

**Outcome**: The tool actively makes this problem WORSE by surfacing only recent papers. A student using this would never discover DistilBERT.

---

## Teaching Utility Assessment

### For Graduate Seminar Preparation: **C+**
- ✅ Fast discovery of recent techniques
- ❌ Cannot build foundational → advanced progression
- ❌ Difficulty filters don't align with pedagogical needs
- ❌ No citation network visualization to show influence

### For Student Recommendations: **B-**
- ✅ Good for advanced students who know the basics
- ❌ Dangerous for beginners (will miss foundations)
- ⚠️ Follow-up questions are thoughtful but surface-level

### For Staying Current: **A-**
- ✅ Advisor quickly finds relevant recent work
- ✅ Semantic understanding is strong
- ✅ Response time is acceptable (~2s)

---

## Delights

1. **Semantic Search Works**: The advisor immediately understood "efficient language models" when keyword search failed completely.
2. **Fast Response**: 1.7-2.8 second response times feel snappy for AI-powered search.
3. **Follow-up Questions**: The suggested next queries ("How do these methods scale?") show understanding of research workflow.
4. **Filter UX**: Clean chip-based filter UI with clear active state.

---

## Frustrations

1. **Recency Bias is Crippling**: For academic use, surfacing ONLY 2024-2025 papers is a fatal flaw. Research builds on foundations.
2. **Keyword Search is Broken**: "efficient language models" returning CV papers means keyword search is worse than useless.
3. **Discovery Page Broken**: The one feature designed for high-impact curation threw an error.
4. **Missing Citation Context**: No h-index, citation counts, or influence metrics visible anywhere.
5. **Difficulty Calibration Wrong**: "Beginner" filter returning advanced optimization papers suggests mis-tagged data.
6. **No Learning Path Generation**: Despite having difficulty tags, the tool can't generate foundational → advanced sequences.

---

## Performance Metrics

- **Advisor Response Time**: 1.7-2.8s (Good)
- **Relevance (Recent Papers)**: 6/6 relevant (Excellent)
- **Relevance (Foundational Papers)**: 0/4 expected papers found (Critical Failure)
- **Keyword Search Accuracy**: 0/30 top results relevant (Broken)
- **Page Load Time**: Not measured (seemed fast)
- **Error Rate**: 1 major error (Discovery page) in 4-minute session

---

## Priority Improvements

### CRITICAL (Must-Have for Academic Use)

1. **Temporal Range Control** (Impact: 10/10, Effort: 3/10)
   - Add year range slider: [Foundational (pre-2020)] [Recent (2020-2023)] [Cutting-Edge (2024-2025)]
   - Default to "All years" not "Recent only"
   - Label papers as "Foundational" vs. "Recent work" vs. "Follow-up"

2. **Fix Keyword Search** (Impact: 9/10, Effort: 5/10)
   - "efficient language models" should not return computer vision papers
   - Basic keyword matching needs semantic disambiguation

3. **Citation Network Visualization** (Impact: 9/10, Effort: 7/10)
   - Show "This paper built on: [DistilBERT, BERT, ...]"
   - Enable "walk backward in time" to find foundations
   - Visualize influence (what cited this paper)

### HIGH PRIORITY (Significant Academic Value)

4. **Learning Path Generator** (Impact: 8/10, Effort: 6/10)
   - "Generate reading list for: beginner | intermediate | advanced"
   - Explicitly order: Foundations → Core Methods → Recent Advances
   - Export to BibTeX for syllabus

5. **Enhanced Code Metadata** (Impact: 7/10, Effort: 4/10)
   - Show GitHub stars, forks, last commit
   - Link to official implementations, not just repos
   - Flag "well-documented" vs. "research code"

6. **Fix Difficulty Tagging** (Impact: 7/10, Effort: 5/10)
   - Retag based on **prerequisites** not writing clarity
   - Beginner = "Requires undergrad ML only"
   - Expert = "Requires deep knowledge of multiple subfields"

### MEDIUM PRIORITY (Nice to Have)

7. **"Build Syllabus" Feature** (Impact: 6/10, Effort: 8/10)
   - Select papers → Auto-generate week-by-week reading schedule
   - Estimate reading time based on paper length/difficulty
   - Suggest "anchor paper + 2 follow-ups" per week

8. **Pedagogical Value Tags** (Impact: 6/10, Effort: 5/10)
   - "Good for teaching" (clear figures, strong motivation)
   - "Survey paper" (good for overviews)
   - "Toy example included" (helps students understand)

---

## Final Verdict

### Would I use this for my seminar? **No, not yet.**

The tool's recency bias makes it unsuitable for academic course preparation. I cannot build a coherent learning progression when the system only surfaces 2024-2025 papers. My students would miss the intellectual foundations of the field.

**Current State**: Excellent for staying current on recent work, but fails at the core academic task of teaching foundations.

### Would I recommend to students? **Conditionally.**

- **Advanced PhD students**: Yes, with caveats. Use it to discover recent techniques after you know the classics.
- **First-year PhD students**: No. They would get a distorted view of the field.
- **Undergrads**: Absolutely not. They need guided learning paths, not raw paper discovery.

### What would change my mind?

If the tool added:
1. Temporal range controls (foundational vs. recent)
2. Citation network visualization ("walk backward to foundations")
3. Learning path generation (beginner → advanced sequences)

Then this becomes a **must-recommend** tool for academic researchers.

---

## Screenshots Index

1. `01-landing-first-impression.png` - Initial page load, 30 papers visible
2. `02-discovery-nav.png` - Discovery page error
3. `03-back-to-explore.png` - Return to Explore, searching state
4. `04-search-query-entered.png` - Keyword search results (irrelevant CV papers)
5. `05-advisor-clicked.png` - AI advisor panel opened, 6 relevant results
6. `06-advisor-query-typed.png` - Detailed query entered
7. `07-advisor-searching.png` - Advisor processing
8. `08-advisor-response.png` - 5 papers + follow-up questions (missing foundations)
9. `09-paper-expanded.png` - Attempted paper expansion (didn't work)
10. `10-has-code-filter.png` - Filters visible
11. `11-code-filter-applied.png` - Has Code filter active
12. `12-difficulty-filter.png` - Loading state after Beginner filter
13. `13-beginner-filter-applied.png` - Both filters active, same 6 results
14. `14-generate-page.png` - Same view (stale navigation)
15. `15-generate-navigation.png` - Code generation feature page
16. `16-final-state.png` - Final session state

---

**Assessment completed**: 2025-12-21 09:58:46
**Total screenshots**: 16
**Session duration**: ~4 minutes
