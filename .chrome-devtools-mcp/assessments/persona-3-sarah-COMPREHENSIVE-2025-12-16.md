# UX Assessment Report: Sarah Kim - COMPREHENSIVE SESSION
**Persona**: First-Year PhD Student, Stanford Vision Lab
**Research Focus**: Vision-Language Models (exploratory phase)
**Assessment Date**: 2025-12-16, 15:05 PST
**Session Duration**: ~45 minutes
**Chrome Instance**: mcp__chrome-3
**Assessment Type**: Complete 13-Step UX Methodology

---

## Executive Summary

As a first-year PhD student drowning in papers about vision-language models, I was hopeful this tool could help me build a mental map of the field before my qualifying exams. The Research Advisor feature genuinely helped me find CLIP-related papers I needed, and seeing "Beginner" difficulty filters made me feel less alone in my confusion. However, the Learning Path feature—which sounded like exactly what I needed—gave me papers about Scratch programming and dental AI when I asked about vision-language models. That moment crushed my confidence more than helped it. This tool has potential but feels unfinished in critical areas that matter most to anxious first-years like me.

---

## Session Timeline & Metrics

| Step | Time | Action | Load Time | Emotional State | Success |
|------|------|--------|-----------|-----------------|---------|
| 1 | 15:05 | Landing page (redirected to /explore) | N/A | 3/5 (curious but uncertain) | ✓ |
| 2 | 15:08 | Navigation discovery (Generate page) | ~1s | 3/5 (confused by purpose) | Partial |
| 3 | 15:12 | Search "multimodal learning vision language" | ~2s | 4/5 (found relevant papers!) | ✓ |
| 3.5 | 15:15 | Research Advisor query about CLIP | ~3s | 5/5 (delighted by AI help) | ✓ |
| 4 | 15:20 | Expanded paper detail view | <1s | 4/5 (useful metadata) | Partial |
| 4b | 15:22 | Tried "Related Papers" tab | N/A | 2/5 (frustrated by error) | ✗ |
| 5 | 15:25 | "Has Code" filter test | <1s | 4/5 (exactly what I needed) | ✓ |
| 6 | 15:28 | "Beginner" difficulty filter | <1s | 5/5 (reduced imposter syndrome!) | ✓ |
| 7 | 15:32 | Discovery page navigation | ~1s | 4/5 (promising structure) | ✓ |
| 8 | 15:35 | Learning Path for "vision language models" | ~2s | 1/5 (completely wrong results) | ✗ |
| 9 | 15:40 | TL;DR page check | <1s | 2/5 (empty, disappointing) | ✗ |
| 10 | 15:43 | Techniques page exploration | ~1s | 3/5 (overwhelming categories) | Partial |
| 11 | 15:45 | Final reflection | N/A | 3/5 (mixed feelings) | N/A

**Average Emotional State**: 3.4/5 (slightly above neutral, but with high variance)
**Task Success Rate**: 6/11 full success, 3/11 partial, 2/11 failed

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)
**Screenshot**: `01-landing-first-impression.png`

**What I Saw**: The page immediately redirected to `/explore` showing a search interface with papers listed. Clean design, professional look. I saw:
- Search bar with "Ask Advisor" button (intriguing!)
- Paper cards showing titles, authors, citations, impact scores
- Filters on the left sidebar (Difficulty, Has Code, etc.)

**Emotional Reaction**: "Okay, this looks professional. Not some grad student's weekend project. But where's the landing page explaining what this does?"

**First Impression Evaluation**:
- ❌ No value proposition—I landed directly in the app
- ✓ Looks trustworthy and well-designed
- ✓ Clear path to finding papers (search bar obvious)
- ✓ Not overwhelming—clean interface

**Notes**: I was immediately thrown into the deep end without context. For someone like me who's already anxious about not knowing enough, a brief "What is this tool?" would have helped. But the clean design did make me feel like this was a serious tool, not a toy.

---

### Step 2: Initial Exploration (Navigation Discovery)
**Screenshots**: `02a-nav-generate.png`, `02b-nav-generate-page.png`

**What I Did**: Clicked around the top navigation. Found "Explore" (current page), "Discovery", and "Generate".

**Confusion Points**:
- "Generate" link wasn't clearly highlighted when active
- Clicking "Generate" took me to a code generation page—not relevant to my literature review
- No clear indication of what "Discovery" would show me

**Mental Model Match**:
- ✓ "Explore" = search/browse papers (matched expectation)
- ❓ "Discovery" = unclear what this means vs. Explore
- ❌ "Generate" = I expected paper generation/summarization, got code generation

**Emotional State**: 3/5 (slightly confused but willing to explore)

---

### Step 3: Task-Based Search
**Screenshot**: `03-search-results.png`

**Query**: "multimodal learning vision language"

**Results Quality**:
- ✓ Found relevant papers (BLIP, CLIP-related work)
- ✓ Fast response (~2 seconds)
- ✓ Titles were immediately scannable
- ❌ All dates showed "Invalid Date" (bug)
- ✓ Impact scores visible (helpful for prioritizing)
- ✓ Citation counts shown

**Metadata Evaluation**:
- Authors: ✓ Shown
- Date: ✗ "Invalid Date" bug everywhere
- Citations: ✓ Shown and useful
- Category: ❓ Not immediately visible
- Code availability: ✓ GitHub icon when available

**Emotional State**: 4/5 (excited to find relevant papers despite date bug)

**Time to First Relevant Result**: ~2 seconds (felt fast)

---

### Step 3.5: Research Advisor (AI-Powered Search)
**Screenshots**: `03a-research-advisor-opened.png`, `03b-advisor-searching.png`, `03c-advisor-response-clip.png`

**Query**: "Can you explain CLIP and find related papers on vision-language pretraining?"

**AI Response Quality**:
- ✓✓✓ **EXCELLENT**: Gave clear explanation of CLIP (Contrastive Language-Image Pre-training)
- ✓ Found specific relevant papers (CLIP, ALIGN, BLIP)
- ✓ Explained concepts in accessible language
- ✓ Provided follow-up action buttons (Citations, Similar Papers, Code, Alternatives)

**Comparison to Basic Search**:
- Basic search: Found papers with keywords
- Research Advisor: Understood semantic intent, explained concepts, curated specific recommendations

**Would I Use This as Primary Search?**: **YES, absolutely.** This is the feature that made me feel like I had a smart senior PhD student helping me. It didn't just find papers—it explained what CLIP actually is, which helps with my imposter syndrome.

**Emotional State**: 5/5 (delighted—this is what I needed!)

**Follow-Up Actions Tested**:
- Clicked "Related Papers" button → led to expanded paper view
- Did not test "Citations", "Code", or "Alternatives" buttons due to time

---

### Step 4: Deep Dive - Paper Analysis
**Screenshots**: `04-paper-expanded.png`, `04-paper-detail-failed-related.png`

**Paper Examined**: One of the CLIP-related papers from advisor results

**Expanded View Showed**:
- ✓ Full abstract
- ✓ Authors and affiliations
- ✓ Citation count and impact score
- ✓ "Summary" tab (AI-generated)
- ✓ "Related Papers" tab
- ❌ **BUG**: "Related Papers" tab showed "Failed to fetch related papers" error

**AI Summary Quality**:
- ✓ Concise key points
- ✓ Saved time vs. reading full abstract
- ✓ Highlighted main contribution

**Time Saved**: Estimated ~1-2 minutes per paper vs. reading full abstract and skimming intro

**What Was Missing**:
- ❌ Techniques/methodologies not extracted (would help me learn the field)
- ❌ Related Papers failed to load (critical for building mental map)
- ❌ No "Key Equations" or "Visual Summaries" for vision papers

**Emotional State**: 4/5 initially, dropped to 2/5 when Related Papers failed

---

### Step 5: Code Availability Check
**Screenshot**: `05-has-code-filter.png`

**What I Tested**:
1. Looked for code indicators on paper cards → Found GitHub icons
2. Applied "Has Code" filter in left sidebar
3. Verified filtered results showed only papers with code

**Code Availability Surfacing**:
- ✓ GitHub icon prominently displayed on paper cards
- ✓ "Has Code" filter easy to find and apply
- ✓ Filter worked correctly (results updated immediately)
- ❌ GitHub stars/forks NOT shown (would help assess code quality)

**Ease of Finding Reproducible Papers**: 5/5 (exactly what I needed)

**Why This Matters to Me**: As a first-year, I learn best by running code. Wasting hours on papers without implementations is my biggest frustration. This filter is a lifesaver.

**Emotional State**: 4/5 (relieved to find this filter)

---

### Step 6: Learning Path Assessment
**Screenshots**: `08-learning-path-input.png`, `09-learning-path-wrong-results.png`

**Query**: "vision language models"

**Expected Results**: Papers progressing from:
- Foundational: Early multimodal learning, image captioning basics
- Intermediate: CLIP, ALIGN (contrastive learning)
- Advanced: BLIP, Flamingo (more complex architectures)
- Expert: Recent state-of-the-art VLMs

**Actual Results**: 🚨 **COMPLETELY WRONG** 🚨

**Intermediate Level Papers Shown**:
- "Program Repair via LLMs with Scratch" (about Scratch programming language?!)
- "SWE-bench: AI Software Engineering"
- "Brain Imaging with Transformers"
- "Dental AI from X-rays"
- "Chart QA"

**Advanced Level Papers**:
- "Neural Radiance Fields" (NeRF—3D rendering, not VLMs)
- "Ultrasound Imaging"
- "3D Gaussian Splatting"

**Expert Level Papers**:
- "Graph Theory Applications"
- "Quantum Mechanics and Color Perception"

**Analysis of Failure**:
- ❌ Zero papers about CLIP, BLIP, ALIGN, or actual vision-language models
- ❌ Results seem to match random "vision" or "language" keywords independently
- ❌ No logical progression from foundational to advanced
- ❌ Includes completely unrelated domains (Scratch programming, dental AI, quantum mechanics)

**Impact on My Research Goals**:
This was the feature I was most excited about. The assessment methodology said "learning paths and 'start here' guidance would be a dream come true" for me. Instead, this made me feel MORE confused and MORE like an imposter. If the AI doesn't understand what "vision language models" means, how can I trust any of its recommendations?

**Emotional State**: 1/5 (frustrated, confused, confidence damaged)

**Would This Help Someone New to the Subfield?**: **Absolutely not.** This would actively mislead them.

---

### Step 7: TL;DR / Quick Scan Mode
**Screenshot**: `10-tldr-empty.png`

**What I Found**: Empty page with just the "TL;DR" heading. No papers, no summaries.

**Expected**: Quick summaries of recent hot papers for efficient triage

**Actual**: Nothing to evaluate

**Emotional State**: 2/5 (disappointed—this sounded useful)

**Time to Scan 10 Papers**: N/A (feature not implemented)

---

### Step 8: Technique Explorer
**Screenshot**: `11-techniques-page.png`

**What I Saw**: A page with hundreds of technique categories listed:
- Attention Mechanisms, Transformers, GANs, VAEs, etc.
- Organized alphabetically
- Clickable categories (presumably lead to filtered papers)

**Technique Taxonomy Evaluation**:
- ✓ Comprehensive list of ML techniques
- ❌ Overwhelming for a first-year (200+ categories?)
- ❓ No hierarchy or grouping by subfield
- ❓ Didn't test clicking through to see paper-technique linkage

**Findability**: 3/5 (I can Ctrl+F search, but browsing is overwhelming)

**What Would Help**:
- Group techniques by subfield (Vision, NLP, Reinforcement Learning, etc.)
- Show "Popular in Vision-Language Models" section
- Add short descriptions for unfamiliar techniques

**Emotional State**: 3/5 (neutral—useful reference but intimidating)

---

### Step 9: Rising Papers / Hot Topics
**Note**: Did not fully test this step due to time constraints. The Discovery page had sections for trending content, but I didn't navigate to a dedicated `/discovery/rising` page.

**Emotional State**: N/A

---

### Step 10: Paper Relationships / Similarity Graph
**Note**: Attempted during Step 4 (Related Papers tab), but feature failed with error message.

**Attempted**: Yes
**Success**: No (server error)
**Emotional State**: 2/5 (frustrating when features don't work)

---

### Step 11: Second Search (Consistency Check)
**Note**: Did not perform a completely separate second search. However, multiple searches during the assessment (basic search, Research Advisor search) showed consistent interface and behavior.

**Consistency Observed**: ✓ Yes, across different search methods

---

### Step 12: Exit Reflection
**Screenshot**: `12-final-state.png`

**Time Investment**: ~45 minutes
**Overall Impression**: Mixed—powerful features marred by critical bugs

**Would I bookmark this tool?**: Maybe. The Research Advisor alone is valuable enough to return to.

**Would I return tomorrow?**: Yes, but only to use Research Advisor for semantic search. I wouldn't trust Learning Paths or rely on broken features.

**Would I recommend to colleagues?**: "Try the Research Advisor feature, but ignore Learning Paths—they're broken."

**What frustrated me most?**:
1. Learning Path giving completely wrong results (destroyed trust)
2. Related Papers feature broken (can't build mental map)
3. Invalid Date bug everywhere (makes it hard to assess recency)

**What delighted me most?**:
1. Research Advisor explaining CLIP and finding relevant papers
2. "Beginner" difficulty filter (made me feel less alone)
3. "Has Code" filter (exactly what I need)

---

## Pain Point Assessment

My five pain points as Sarah Kim:

### 1. **Overwhelming Volume** (500+ new papers/week)
**Did the tool help?**: Partially ✓

- **What worked**: Research Advisor helped curate relevant papers, "Has Code" filter reduced noise
- **What didn't**: TL;DR feature empty, no email digests or alerts
- **Impact**: 3/5 (helps but doesn't solve the volume problem)

### 2. **Lack of Context** (What's foundational? What's worth reading?)
**Did the tool help?**: No ✗

- **What worked**: Difficulty filters (Beginner/Intermediate/Advanced) exist
- **What didn't**: Learning Path completely failed to provide field context
- **Impact**: 1/5 (Learning Path failure actively hurt my understanding)

### 3. **Imposter Syndrome** (Everyone else seems to know what they're doing)
**Did the tool help?**: Mixed ±

- **What worked**: "Beginner" filter made me feel less alone, Research Advisor explained concepts without judgment
- **What hurt**: Learning Path giving nonsense results made me question my own understanding
- **Impact**: 3/5 (net neutral—one step forward, one step back)

### 4. **Building Mental Map** (How does everything connect?)
**Did the tool help?**: No ✗

- **What worked**: Nothing (Related Papers broken)
- **What didn't**: Related Papers feature failed, no graph visualization
- **Impact**: 1/5 (critical feature for my needs is broken)

### 5. **Qualifying Exam Anxiety** (Need to look competent in broad discussions)
**Did the tool help?**: Partially ✓

- **What worked**: Research Advisor could help me understand key papers quickly
- **What didn't**: Can't trust Learning Path for exam prep, no "classic papers" recommendations
- **Impact**: 2/5 (helps with individual papers, not comprehensive exam prep)

**Overall Pain Point Resolution**: 2/5 (Many good ideas, but critical failures in execution)

---

## Performance Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Average Load Time | ~1-2s | ✓ Fast enough |
| Research Advisor Response | ~3s | ✓ Acceptable for AI query |
| Search Responsiveness | <2s | ✓ Feels snappy |
| "Invalid Date" Bug Frequency | 100% of papers | ✗ Critical bug |
| Related Papers Failure Rate | 100% (1/1 attempts) | ✗ Feature broken |
| Learning Path Accuracy | 0% relevant results | ✗ Catastrophic failure |

---

## Delights

1. **Research Advisor is genuinely helpful**: The AI explained CLIP in plain language and found exactly the papers I needed. This feature alone makes the tool valuable.

2. **Beginner difficulty filter**: Seeing papers marked "Beginner" made me feel less alone in my confusion. This is huge for imposter syndrome.

3. **Has Code filter**: As someone who learns by doing, being able to filter for reproducible work saves hours of frustration.

4. **Clean, professional design**: The interface doesn't feel like a hacked-together grad student project. It looks trustworthy.

5. **Fast search**: Everything loads quickly. No frustrating waiting.

---

## Frustrations

1. **Learning Path is completely broken**: Asked for "vision language models," got Scratch programming and dental AI. This is the feature I needed most, and it's unusable.

2. **Related Papers feature doesn't work**: I need to build a mental map of the field, but the feature gives server errors.

3. **Invalid Date bug everywhere**: Every single paper shows "Invalid Date" instead of publication year. How do I know what's recent?

4. **TL;DR page is empty**: Promised feature isn't implemented. Don't show me empty pages.

5. **No onboarding or value proposition**: I was thrown into /explore with no explanation of what makes this tool special.

6. **Technique taxonomy overwhelming**: 200+ categories with no hierarchy. Intimidating for first-years.

---

## Priority Improvements

| Priority | Issue | Impact | Effort | Rationale |
|----------|-------|--------|--------|-----------|
| **P0** | Fix Learning Path relevance | Critical | High | Core value prop for anxious first-years; currently destroys trust |
| **P0** | Fix "Invalid Date" bug | High | Low | 100% of papers affected; breaks recency assessment |
| **P0** | Fix "Related Papers" server error | High | Medium | Critical for building mental map of field |
| **P1** | Implement TL;DR feature or remove page | Medium | High | Don't show empty promised features |
| **P1** | Add onboarding/landing page | Medium | Low | First-time users need context on value prop |
| **P2** | Group techniques by subfield | Low | Medium | Current taxonomy overwhelming for newcomers |
| **P2** | Show GitHub stars/forks on code | Low | Low | Helps assess code quality |
| **P3** | Add classic/foundational paper tags | Medium | High | Helps with qualifying exam prep |
| **P3** | Highlight active nav item | Low | Low | Minor UX polish |

**Impact Scale**: Critical = Feature unusable, High = Major pain point, Medium = Moderate friction, Low = Nice-to-have
**Effort Scale**: Low = <1 day, Medium = 1-3 days, High = 1+ weeks

---

## Screenshots Index

1. `01-landing-first-impression.png` - Initial /explore page view
2. `02a-nav-generate.png` - Generate navigation link
3. `02b-nav-generate-page.png` - Generate page (code generation feature)
4. `03a-research-advisor-opened.png` - Research Advisor dialog opened
5. `03b-advisor-searching.png` - Advisor searching state
6. `03c-advisor-response-clip.png` - Advisor explaining CLIP and showing papers
7. `03-search-results.png` - Search results for "multimodal learning vision language"
8. `04-paper-expanded.png` - Expanded paper detail view
9. `04-paper-detail-failed-related.png` - Related Papers tab showing error
10. `05-has-code-filter.png` - "Has Code" filter applied successfully
11. `06-beginner-filter.png` - "Beginner" difficulty filter applied
12. `07-discovery-page.png` - Discovery page overview
13. `08-learning-path-input.png` - Learning Path input field
14. `09-learning-path-wrong-results.png` - Learning Path showing irrelevant results
15. `10-tldr-empty.png` - Empty TL;DR page
16. `11-techniques-page.png` - Techniques page with hundreds of categories
17. `12-final-state.png` - Final assessment state

---

## Final Verdict

### Would this tool help me prepare for qualifying exams?

**Short answer**: Not yet.

**Long answer**: The Research Advisor feature could help me understand individual papers quickly, which is valuable. But qualifying exams require comprehensive field knowledge and understanding paper relationships—both areas where this tool fails (Learning Path broken, Related Papers broken). I can't trust a tool that thinks "vision language models" means Scratch programming.

### Would this reduce my imposter syndrome?

**Mixed**: The Beginner filter and helpful Research Advisor made me feel supported. But the Learning Path failure made me question whether I even understand what "vision-language models" means. Net neutral at best.

### What would make me a daily user?

**Fix these three things**:
1. **Fix Learning Path algorithm**: This should be the killer feature for first-years
2. **Fix Related Papers feature**: I need to see connections
3. **Add "Classic Papers" tags**: Help me find foundational work for exam prep

If those worked reliably, I'd use this daily. The Research Advisor alone is worth bookmarking, but the tool needs to nail the fundamentals before adding more features.

### Recommendation to other first-years?

**Current state**: "Try the Research Advisor if you need quick paper explanations. Don't trust anything else yet."

**Potential state** (if fixed): "This is the tool I wish I had when I started my PhD."

---

## Closing Thoughts (In Character)

I really wanted to love this tool. As a first-year drowning in papers and imposter syndrome, the promise of AI-powered learning paths and contextual guidance sounded perfect. The Research Advisor gave me hope—it actually explained CLIP in a way that made sense and didn't make me feel stupid.

But then the Learning Path told me "vision language models" involves Scratch programming and dental AI. That moment hurt. It made me wonder if I'm using the wrong terminology, if I don't understand my own research area. That's the opposite of what I need as an anxious first-year.

The bones of this tool are good. The design is clean, the search is fast, and the Research Advisor is genuinely smart. But right now, it feels like a beta product that shipped too early. Fix the Learning Path relevance, fix the Related Papers feature, and fix the date bug. Then we'll talk about whether this is the tool that saves first-years from drowning.

I'll keep it bookmarked for the Research Advisor. But I'll keep using my advisor's paper recommendations for building my mental map of the field. Trust is everything when you already feel like an imposter.

---

**Assessment completed**: 2025-12-16, 15:50 PST
**Total time invested**: 45 minutes
**Overall emotional arc**: Hopeful → Delighted (Research Advisor) → Crushed (Learning Path) → Resigned
**Final emotional state**: 3/5 (cautiously optimistic about potential, disappointed by execution)
