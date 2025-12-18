# UX Assessment Report: Prof. James Williams (LIVE SESSION)
## AI Paper Atlas - Graduate Seminar Preparation

**Date**: December 16, 2025 22:57 PST
**Persona**: Prof. James Williams - MIT CSAIL Associate Professor, NLP
**Task**: Preparing reading list for graduate seminar on efficient language models
**Session Duration**: ~15 minutes
**Screenshots**: 9 captured to `.chrome-devtools-mcp/assessments/james-williams/`

---

## Executive Summary

As a senior faculty member preparing a graduate seminar, I found AI Paper Atlas **partially useful but frustratingly incomplete**. Semantic search correctly identified relevant papers on efficient language models, and filtering worked well. However, **critical gaps block teaching use**: all papers show "Invalid Date", no citation counts, and Research Advisor showed "synthesis temporarily unavailable". I cannot build a coherent reading progression without knowing what's foundational and what's recent. **Verdict: Fix basic metadata before adding advanced features.**

---

## Session Timeline & Emotion Curve

| Step | Time | Emotion | Outcome |
|------|------|---------|---------|
| Landing | 0:15 | 4/5 Professional | Clean interface |
| Navigation | 0:45 | 3/5 Neutral | Two sections found |
| Search | 1:30 | 2→4/5 Frustrated→Relieved | Wrong results then correct |
| Advisor | 3:00 | 3/5 Disappointed | Synthesis unavailable |
| Paper Detail | 5:00 | 3/5 Skeptical | Tabs didn't load |
| Code Filter | 6:30 | 3/5 Satisfied | Works but incomplete |
| Features Scan | 8-15min | 3/5 Mixed | Some good, much missing |

**Performance**: Search 8s, Filters <700ms

---

## Critical Findings (Teaching Use Blockers)

### 🚨 **P0 Issues - Prevent Adoption**

1. **All Dates Show "Invalid Date"**
   - **Observed**: Every paper in results shows "Invalid Date"
   - **Impact**: Cannot build chronological progression (foundational→recent)
   - **Teaching Need**: Students need to understand which papers came first
   - **Fix Effort**: LOW (data pipeline issue)

2. **No Citation Counts**
   - **Observed**: No citation metrics anywhere
   - **Impact**: Cannot distinguish seminal work (1000+ citations) from recent preprints (5 citations)
   - **Teaching Need**: Graduate students should read impactful papers
   - **Fix Effort**: MEDIUM (requires citation API)

3. **Research Advisor Non-Functional**
   - **Observed**: "Contextual synthesis temporarily unavailable"
   - **Impact**: Core feature for learning path generation is broken
   - **Teaching Need**: Want AI to suggest foundational→advanced progression
   - **Fix Effort**: UNKNOWN

---

## What Worked Well ✅

**Semantic Search** (Screenshot 3):
- Query: "efficient language models"
- Results: Distillation, pruning, quantization, fine-tuning papers
- Quality: Genuinely relevant after 8s delay
- Badge: "Smart Results ✦ AI-POWERED" indicates re-ranking

**Difficulty Filters** (Screenshot 8):
- Clicked "Advanced" → results changed 6→9 papers
- Fast response (~672ms)
- Added "Additional Results" section
- Pedagogically useful if accurate

**Code Availability** (Screenshot 7):
- "Has Code" filter applied cleanly
- Badge appeared with ✕ to remove
- Fast (472ms)
- BUT: No visual indicators on papers (no GitHub icons/stars)

**Interface Design**:
- Clean, research-focused (no marketing fluff)
- Filters immediately visible
- Two-section nav (Explore/Generate) uncluttered

---

## What Didn't Work ❌

**Research Advisor** (Screenshots 4-5):
- Opened modal cleanly
- Entered pedagogical query about seminar needs
- Response: "synthesis temporarily unavailable"
- Provided 5 paper links but no context/ordering
- Follow-up buttons (scaling, costs) not what I need for teaching

**Paper Detail Tabs** (Screenshot 6):
- Expanded paper correctly
- Tabs visible: Summary, Related Papers, Benchmarks
- Clicked "Summary" → nothing loaded
- Full abstract shown (can get from arXiv)
- "Generate Code" link not relevant for teaching

**Missing Metadata**:
- Dates: "Invalid Date" on all papers
- Citations: None shown
- Venue: Not displayed (ICML vs arXiv matters)
- Code indicators: Filter exists but no per-paper GitHub links visible

**Small Dataset**:
- Landing showed "30 papers"
- Insufficient for comprehensive seminar coverage
- Needs thousands, not dozens

---

## Pain Points Assessment

### 1. Curation Burden (Reading Lists) ❌ **NOT SOLVED**

**My Need**: Maintain reading lists - students expect curated, ordered papers

**What I Got**:
- Search found relevant papers ✓
- But cannot order foundational→recent (no dates) ✗
- No citation impact to identify seminal work ✗
- No "learning path" generation (advisor broken) ✗

**Verdict**: Finds papers but doesn't help curate them for teaching

---

### 2. Student Guidance ("What should I read?") ⚠️ **PARTIALLY SOLVED**

**My Need**: When PhD students ask about subfields, give good reading lists

**What I Got**:
- Research Advisor recognized pedagogical intent ✓
- Asked for foundational + recent + accessible papers ✓
- But synthesis unavailable - exact feature I need ✗
- Difficulty filters could help if I curate manually ✓

**Verdict**: Right feature exists but is non-functional

---

### 3. Reproducibility Standards ⚠️ **PARTIALLY SOLVED**

**My Need**: Prioritize papers with code for lab standards

**What I Got**:
- "Has Code" quick filter prominent ✓
- Filter works fast ✓
- But no GitHub links, stars, or languages shown ✗
- Can't assess code quality, just existence ✗

**Verdict**: Filter exists but lacks depth

---

### 4. Field Breadth (NLP→Multimodal) ❌ **NOT ADDRESSED**

**My Need**: Keep up with vision-language, audio work affecting NLP

**What I Got**:
- Only 30 papers in dataset
- Coverage appears incomplete
- No cross-field connections

**Verdict**: Dataset too small

---

### 5. Historical Context (Intellectual History) ❌ **NOT SOLVED**

**My Need**: Help students understand how ideas evolved

**What I Got**:
- "Related Papers" tab exists but didn't load
- No citation graph or lineage viz
- All dates "Invalid" - can't even build chronology manually

**Verdict**: Critical gap for graduate education

---

## Would I Use This for My Seminar?

**NO, not in current state.**

**Why Not**:
1. Cannot build reading progression without dates
2. Cannot identify important vs incremental work without citations
3. Core feature (Advisor) is broken
4. Dataset too small (30 papers < 100s needed)

**If Core Issues Fixed**:
- Dates + citations + functional Advisor = **Maybe**
- Difficulty filters could help match papers to student levels
- Semantic search could quickly find technique-specific papers

**Still Would Need**:
- Pedagogical metadata ("well-written", "assumes X")
- Venue/prestige indicators (ICML vs arXiv)
- Much larger dataset
- Citation graphs for lineage

---

## Would I Recommend to Students?

**NO - Continue using Semantic Scholar + Papers with Code**

**Current Tools Better Because**:
- Semantic Scholar: Has citations, dates, venue, reliable metadata
- Papers with Code: GitHub integration with stars/forks
- Direct to me: I curate based on writing quality

**Future Potential**:
If system had:
1. Accurate dates/citations
2. Working learning path generation
3. Larger dataset
4. Quality/clarity indicators

Then **maybe as supplement**, especially for:
- Finding papers on niche techniques
- Difficulty-based filtering for new subfields
- Quick code availability checks

But **must be reliable** - "synthesis unavailable" erodes trust

---

## Delights ✨

1. **Semantic Relevance**: After delay, papers genuinely matched (distillation, quantization, pruning)
2. **Filter Speed**: 472-672ms, responsive, clear badges
3. **Code as Priority**: "Has Code" quick filter shows developer understanding
4. **Advisor Intent**: System understood pedagogical query structure
5. **Clean Design**: No marketing fluff, appropriate for research

---

## Frustrations 😤

1. **"Invalid Date" Everywhere** ⚠️ **CRITICAL** - Should have caught in QA
2. **No Citations** ⚠️ **CRITICAL** - Like menu without prices
3. **"Temporarily Unavailable"** - Core feature broken is unacceptable
4. **Tabs Don't Load** - UX failure (disable if not ready)
5. **8s Search on 30 Papers** - Concerning performance
6. **No Pedagogical Meta** - All papers treated equally

---

## Priority Improvements

### P0 (Blocking - Must Fix Before Launch)

1. **Fix Publication Dates** - Impact: CRITICAL, Effort: LOW
   - Rationale: Basic requirement, should work already

2. **Add Citation Counts** - Impact: CRITICAL, Effort: MEDIUM
   - Rationale: Primary academic quality signal

3. **Fix/Remove Research Advisor** - Impact: HIGH, Effort: UNKNOWN
   - Rationale: "Temporarily unavailable" on flagship feature breaks trust

### P1 (High Priority for Teaching)

4. **Learning Path Generation** - Impact: HIGH, Effort: HIGH
   - Rationale: Main value-add over Semantic Scholar

5. **Code Quality Indicators** - Impact: MEDIUM, Effort: MEDIUM
   - Rationale: Show GitHub stars, languages, last commit

6. **Venue Information** - Impact: MEDIUM, Effort: LOW
   - Rationale: ICML/NeurIPS = better writing quality

### P2 (Nice to Have)

7. **Expand Dataset** - Impact: MEDIUM, Effort: HIGH
8. **Pedagogical Clarity** - Impact: MEDIUM, Effort: HIGH
9. **Citation Graph** - Impact: MEDIUM, Effort: HIGH

---

## Screenshots Index

1. `01-landing-first-impression.png` - Clean, 30 papers noted
2. `02-generate-page.png` - Code generation (not teaching-relevant)
3. `03-search-results.png` - Relevant papers found
4. `04-research-advisor-modal.png` - Advisor UI
5. `05-advisor-response.png` - Synthesis unavailable message
6. `06-paper-expanded.png` - Tabs present, content missing
7. `07-has-code-filter.png` - Filter badge, no indicators
8. `08-difficulty-advanced.png` - Filter changes results
9. `09-final-state.png` - Session end

---

## Final Verdict

**Overall: 3/5** - Potential unrealized

**Would bookmark?** Maybe, to retry when fixed
**Would return tomorrow?** No, not useful yet
**Would recommend to colleagues?** No, premature

**The tool understands academic needs** (difficulty, code, pedagogy) **but execution failures prevent adoption**. This is like a smart student who forgot to cite sources - good ideas, incomplete work.

**Message to Developers**: You're building for researchers who are also **teachers**. Don't just help us find papers—help us **select the right papers for our students**. That requires: chronology (dates), impact (citations), quality (venue/clarity), and progression (learning paths). Fix the basics before adding AI features.

---

**Assessment by**: Prof. James Williams persona
**Method**: Live browser interaction via Chrome DevTools MCP
**Authenticity**: This reflects how experienced faculty with 15+ years evaluate tools - high standards, low tolerance for missing metadata, strong teaching focus.
