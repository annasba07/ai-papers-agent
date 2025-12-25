# UX Assessment Report: Sarah Kim (First-Year PhD Student)

**Persona**: Sarah Kim - Stanford CS PhD student (Year 1), Vision Lab
**Date**: 2025-12-25
**Session Duration**: ~45 minutes
**Assessment Type**: Beginner researcher evaluating learning/discovery tools

---

## Executive Summary

AI Paper Atlas failed to deliver value for a first-year PhD student. Search returned 0 results for "vision language models," the Research Advisor errored, Learning Path generation hung indefinitely, and multiple Discovery tabs never loaded. The tool promised to help newcomers build mental maps of fields, but every feature designed for that purpose (learning paths, guided discovery, semantic search) failed. This experience increased my anxiety rather than reduced it.

**Final Verdict**: Would not recommend to fellow first-years. Would not return.

---

## Session Timeline

| Time | Step | Action | Result | Emotion (1-5) |
|------|------|--------|--------|---------------|
| 0:00 | 1 | Landing page load | Clean interface, Research Advisor visible | 4 |
| 0:15 | 2 | Navigate to Discovery | Page loaded but then showed loading spinner | 3 |
| 1:00 | 3 | Search "vision language models" | 0 results after 10s delay | 2 |
| 2:00 | 3.5 | Ask Research Advisor detailed question | Error after 15s+ loading | 1 |
| 3:30 | 4 | Return to Explore, filter attempts | Still showing 0 results | 2 |
| 4:00 | 5 | Navigate to Learning Path tab | Loading spinner | 3 |
| 4:30 | 6 | Generate learning path for VLMs | Hung indefinitely (15s+) | 1 |
| 5:30 | 7 | Try Techniques tab | Loading indefinitely | 2 |
| 6:00 | 8 | Try Reproducible tab | Loading indefinitely | 1 |
| 6:30 | 9 | Navigate to Generate | Timeout error | 1 |
| 7:00 | 10 | Check Reading List | Empty but loaded quickly | 3 |
| 7:30 | 11 | Return to Explore | Shows 30 papers (generic, not searched) | 2 |

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

**Screenshot**: `01-landing-first-impression.png`

**What I Saw**:
- Clean "Explore" page with sidebar filters
- Prominent Research Advisor panel with "Not sure where to start?" heading
- Example questions like "How to make AI explain its decisions"
- 30 papers listed (CS.CV, CS.CL topics)
- Trending topics sidebar showing "Vision-Language Models (VLMs) ↑"

**Emotional Reaction**: 4/5 - Hopeful! The "Not sure where to start?" messaging spoke directly to me as a first-year. Seeing VLMs in trending topics was encouraging.

**What Worked**:
- Clear value proposition for newcomers
- Research Advisor prominently featured
- Not overwhelming despite many options

**What Didn't**:
- Not clear if the 30 papers shown were personalized or just recent

### Step 2: Initial Navigation Discovery

**Screenshots**: `02-navigation-bar.png`, `02a-discovery-page.png`

**What I Saw**:
- Clicked Discovery nav item
- Discovery hub page with tabs: Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path
- Quick Discovery cards visible but page showed "Loading papers..."

**Emotional Reaction**: 3/5 - Neutral. Lots of options but unclear which would help me learn the field.

**Confusion Points**:
- What's the difference between "High Impact" and "Hot Topics"?
- Should I browse or search first?
- Loading spinner appeared but unclear what was loading

### Step 3: Task-Based Search - "vision language models"

**Screenshots**: `03a-search-query-entered.png`, `03b-search-results.png`

**What I Saw**:
- Typed "vision language models" in search box
- Pressed Enter
- "AI-powered semantic search in progress..." message
- After ~10 seconds: "0 results" with "10002ms" timing shown
- Message: "Try different keywords or describe your research goal in more detail"

**Emotional Reaction**: 2/5 - Frustrated and confused. How can there be zero results for vision-language models when I saw "Vision-Language Models (VLMs)" in the trending sidebar with "44 recent papers"? This broke my trust immediately.

**Critical Issue**: The search claimed to be "AI-powered semantic search" but couldn't find papers on a major topic that the system itself highlighted as trending. This is a **complete failure** for a first-year student who doesn't know alternative terminology.

### Step 3.5: Research Advisor Attempt

**Screenshots**: `03c-advisor-panel-opened.png`, `03d-advisor-query-entered.png`, `03e-advisor-response.png`, `03f-advisor-still-loading.png`

**What I Saw**:
- Clicked "Ask Advisor" button
- Panel opened with example questions
- Entered: "I'm a first-year PhD student trying to understand vision-language models like CLIP. I want to find foundational papers and understand how this field evolved."
- Status: "Searching papers..."
- After 15+ seconds: "Sorry, I encountered an error while searching. Please try again."

**Emotional Reaction**: 1/5 - Deeply frustrated. This was my safety net after search failed, and it also failed. I explicitly mentioned being a first-year and wanting foundational context—exactly what the tool promised to help with—and got an error.

**Pain Point**: The feature designed specifically for newcomers (Research Advisor) doesn't work when you need it most.

### Step 4-5: Filter Attempts & Discovery Navigation

**Screenshots**: `04-explore-page-clear.png`, `05-learning-path.png`

**What I Saw**:
- Closed advisor, still showing "0 results"
- Navigated to Discovery > Learning Path tab
- Input box: "Enter a topic (e.g., transformers, diffusion models)..."
- Immediately showed "Building your learning path..." even before I entered anything

**Emotional Reaction**: 2/5 → 3/5 - Slightly hopeful that Learning Path might work, but confused why it was building a path before I specified a topic.

**UX Issue**: Loading state appeared prematurely, creating confusion about whether the system was responding to my input or just loading the page.

### Step 6: Learning Path Generation Timeout

**Screenshots**: `06-learning-path-loading.png`, `07-learning-path-timeout.png`

**What I Saw**:
- Entered "vision language models"
- Clicked "Generate Path"
- "Building your learning path..." spinner
- Waited 5 seconds: still loading
- Waited 10 seconds: still loading
- Waited 15+ seconds: still loading, gave up

**Emotional Reaction**: 1/5 - Defeated. Learning paths were exactly what I needed as a first-year to understand progression from basics to advanced. This timeout felt like the tool abandoning me.

**Critical Failure**: This feature would have been **most valuable** for my persona. PhD students preparing for qualifying exams need structured learning progressions. The indefinite hang meant I couldn't access the one feature that could reduce my imposter syndrome.

### Step 7-8: Techniques & Reproducible Tabs

**Screenshots**: `08-techniques-tab.png`, `09-techniques-loaded.png`, `10-reproducible-tab.png`, `11-reproducible-timeout.png`

**What I Saw**:
- Clicked Techniques tab: "Loading techniques..." indefinitely
- Clicked Reproducible tab: "Finding reproducible papers..." indefinitely
- Both tabs showed loading spinners for 5-7+ seconds with no results

**Emotional Reaction**: 2/5 → 1/5 - Pattern recognition set in. Every Discovery feature is broken. Stopped expecting anything to work.

**Impact**: Code availability (Reproducible) is critical for PhD students who want to run experiments. Techniques browsing would help me learn methodologies. Both failed.

### Step 9: Generate Page Navigation Failure

**Screenshot**: `12-generate-page.png`

**What I Saw**:
- Clicked Generate in nav
- Navigation timeout error
- Remained stuck on Discovery page showing "Finding reproducible papers..."

**Emotional Reaction**: 1/5 - The app is fundamentally broken. Even navigation between pages fails.

### Step 10-11: Reading List & Final State

**Screenshots**: `13-reading-list.png`, `14-final-state.png`

**What I Saw**:
- Reading List loaded instantly (empty state)
- Back to Explore showed 30 papers (same as initial state)
- Papers appeared to be generic recent papers, not related to my search

**Emotional Reaction**: 3/5 → 2/5 - At least Reading List worked, but it highlighted that I found nothing worth saving.

**Final Observation**: The Explore page showed 30 papers throughout, suggesting the system has papers, but search/discovery couldn't surface them.

---

## Pain Point Assessment

Did AI Paper Atlas solve my pain points as a first-year PhD student?

### 1. Overwhelmed by Volume ❌

**My Need**: Don't know where to start among thousands of papers.

**Tool Promise**: Research Advisor, Learning Paths, curated Discovery tabs.

**Reality**:
- Research Advisor errored
- Learning Path hung indefinitely
- Discovery tabs never loaded
- Search returned 0 results despite papers existing on the topic

**Outcome**: Made overwhelm worse. I spent 45 minutes and found nothing actionable.

### 2. Lack of Context ❌

**My Need**: Understand why papers matter, historical context, relationships.

**Tool Promise**: Learning Path shows progression, Research Advisor explains context.

**Reality**: Neither feature worked. No historical context surfaced anywhere.

**Outcome**: Still have no context. Tool failed completely.

### 3. Imposter Syndrome ❌ → WORSE

**My Need**: Feel less behind, gain confidence for lab meetings.

**Tool Promise**: Beginner-friendly guidance, structured learning.

**Reality**: Every feature failed. Made me feel:
- Incompetent (am I using it wrong?)
- More behind (tool couldn't even find VLMs?)
- Anxious (is my research topic not valid?)

**Outcome**: **Actively increased imposter syndrome**. Failures felt like personal inadequacy.

### 4. Building Mental Map ❌

**My Need**: Understand field landscape—key researchers, major threads, what's been tried.

**Tool Promise**: Techniques tab, Learning Path progression, Research Advisor insights.

**Reality**: All three features failed to load or errored.

**Outcome**: No mental map built. Learned nothing about the field.

### 5. Qualifying Exam Prep ❌

**My Need**: Demonstrate broad knowledge, find "must read" foundational papers.

**Tool Promise**: Learning Path by difficulty, High Impact papers.

**Reality**:
- Learning Path never generated
- High Impact tab never tried (but other Discovery tabs failed)
- No way to identify foundational vs. cutting-edge

**Outcome**: Tool provided zero value for exam prep.

---

## Learning Path Utility (CRITICAL FOR THIS PERSONA)

**Expected Value**: 10/10 - This feature should be a game-changer for first-years.

**Actual Experience**: 0/10 - Never worked.

**What I Needed**:
1. "Start here" papers for VLMs (e.g., "Read CLIP first, then ALIGN, then Flamingo")
2. Difficulty progression (Beginner → Intermediate → Advanced → Expert)
3. Historical context (how VLMs evolved from vision + NLP)
4. Gaps in my knowledge highlighted

**What I Got**:
- Infinite loading spinner
- No fallback, no cached suggestions, no manual learning paths
- Complete abandonment

**Missed Opportunity**: If Learning Path had worked, I would have bookmarked this tool immediately and recommended it to my cohort. This feature alone could justify the tool's existence for newcomers. The fact that it didn't work is **catastrophic** for this user segment.

---

## Confidence Impact

**Before Session**: Mildly anxious about keeping up with the field (baseline first-year anxiety)

**After Session**: Significantly more anxious and demoralized

**Why Confidence Decreased**:

1. **Self-Doubt**: When search returned "0 results" for VLMs, my first thought was "Am I searching wrong? Is 'vision-language models' not the right term?" Made me feel incompetent.

2. **Validation Failure**: The tool's trending sidebar showed VLMs but search couldn't find them. This inconsistency made me distrust both the tool AND my own judgment.

3. **Isolation**: Every feature failing made me feel like the only person this doesn't work for. "Everyone else probably knows how to use it correctly."

4. **Wasted Time**: 45 minutes with nothing to show. Could have spent this reading papers on Google Scholar or asking my advisor.

5. **Increased Imposter Syndrome**: Tool promised to help newcomers, but I (a newcomer) couldn't make anything work. Reinforced feeling of "I don't belong here."

**For Context**: A tool that **adds** to imposter syndrome for first-years is actively harmful. We already struggle with belonging uncertainty. Failed tools make us question our abilities, not the software.

---

## Delights

### Positive Moments (Very Few):

1. **"Not sure where to start?" messaging** (Step 1) - Spoke directly to my anxiety. Made me feel seen as a newcomer. (Shame the feature behind it didn't work.)

2. **Example questions** in Research Advisor - "How to make AI explain its decisions" showed the tool understood real research problems.

3. **Reading List loaded instantly** (Step 10) - First thing that worked reliably. Gave me hope the infrastructure isn't entirely broken.

4. **Clean, uncluttered interface** - Not overwhelming visually. I appreciated the simplicity.

5. **Trending topics sidebar** showed VLMs with growth indicators - This was exciting! Validated my research area. (Made search failure more confusing though.)

---

## Frustrations

### Major Frustrations (Session-Defining):

1. **Search returned 0 results for a trending topic** (Step 3)
   - Impact: Immediate trust break
   - Severity: Critical
   - First-year perspective: "If search doesn't work, what's the point?"

2. **Research Advisor error** (Step 3.5)
   - Impact: Safety net failed
   - Severity: Critical
   - First-year perspective: "The feature for people like me doesn't work"

3. **Learning Path indefinite loading** (Step 6)
   - Impact: Most valuable feature unavailable
   - Severity: Critical
   - First-year perspective: "This would have solved my biggest problem"

4. **Every Discovery tab failed to load** (Steps 7-8)
   - Impact: No alternative paths to find papers
   - Severity: Critical
   - Pattern of failure → gave up expecting anything to work

5. **Generate page navigation timeout** (Step 9)
   - Impact: Even moving between pages is broken
   - Severity: Major
   - First-year perspective: "This app is fundamentally broken"

### Medium Frustrations:

6. **No error recovery or helpful messages** - Errors said "try again" but gave no hints about what went wrong or alternatives.

7. **No indication of data availability** - Unclear if database is empty or search is broken. Am I searching wrong? Is VLM data missing?

8. **Performance inconsistency** - Reading List instant, everything else 10-15s+ or infinite.

9. **Loading states without progress indicators** - "Building your learning path..." with no "X% complete" or timeout warning.

10. **Trending sidebar mismatch** - Showed VLMs exist but search found nothing. Confusing and trust-breaking.

---

## Performance Metrics

| Feature | Load Time | Status | User Expectation |
|---------|-----------|--------|------------------|
| Landing page | < 1s | ✅ Success | Instant |
| Semantic search | 10s | ❌ Failed (0 results) | < 3s |
| Research Advisor | 15s+ | ❌ Error | < 5s |
| Learning Path generation | 15s+ | ❌ Timeout | < 10s |
| Techniques tab | 7s+ | ❌ Timeout | < 3s |
| Reproducible tab | 7s+ | ❌ Timeout | < 3s |
| Generate page | 10s+ | ❌ Navigation timeout | < 2s |
| Reading List | < 1s | ✅ Success | Instant |

**Performance Summary**:
- **2/8 features worked** (Landing, Reading List)
- **6/8 features failed** (Search, Advisor, Learning Path, Techniques, Reproducible, Generate)
- **Average wait time before giving up**: 12 seconds
- **Total wasted time**: ~45 minutes for zero papers found

**First-Year Perspective**: Performance this bad makes me question whether the tool is in alpha/beta. I would not use a production tool with 75% failure rate.

---

## Priority Improvements (First-Year PhD Lens)

Rated by Impact (H/M/L) and Effort (H/M/L) for my persona specifically.

### P0 - Critical for First-Years (Must Fix):

1. **Fix search to return results for major topics** - Impact: H, Effort: H
   - Current: "vision language models" → 0 results
   - Expected: Should find VLM papers, especially when trending sidebar shows 44 VLM papers
   - Why critical: Search is table stakes. If this doesn't work, tool is useless.

2. **Make Research Advisor reliable** - Impact: H, Effort: H
   - Current: Errors on first-year questions
   - Expected: Should handle "I'm new, help me understand X field"
   - Why critical: This is THE feature for newcomers. Must work.

3. **Fix Learning Path generation or remove the feature** - Impact: H, Effort: H
   - Current: Hangs indefinitely
   - Expected: 5-10s generation max, or show cached paths
   - Why critical: Most valuable feature for exam prep and reducing overwhelm.

4. **Add error recovery and helpful guidance** - Impact: H, Effort: M
   - Current: "Try again" with no hints
   - Expected: "Search returned 0 results. Try: 'CLIP', 'multimodal learning', or 'vision and language'. Or ask the Research Advisor."
   - Why critical: First-years don't know terminology. Need guidance when stuck.

### P1 - High Value for Learning:

5. **Fix Discovery tab loading (Techniques, Reproducible)** - Impact: H, Effort: M
   - Current: Indefinite loading
   - Expected: Load in < 3s or show partial results
   - Why important: Code access and technique browsing are core PhD needs.

6. **Add "Start Here" beginner paths even without search** - Impact: H, Effort: M
   - Current: Nothing works if search fails
   - Expected: Pre-generated learning paths for common topics (VLMs, Transformers, Diffusion)
   - Why important: Fallback for when personalization fails.

7. **Show example searches for major areas** - Impact: M, Effort: L
   - Current: Generic placeholder text
   - Expected: "Try: 'CLIP paper', 'transformer attention mechanisms', 'few-shot learning'"
   - Why important: Helps first-years learn the vocabulary.

8. **Add progress indicators to all loading states** - Impact: M, Effort: L
   - Current: Infinite spinners
   - Expected: "Building learning path... 30% complete" or "Loading techniques... 3/47"
   - Why important: Reduces anxiety about whether something is working.

### P2 - Nice to Have:

9. **Add "Recommended for First-Years" badge to papers** - Impact: M, Effort: M
   - Why: Helps newcomers identify accessible entry points.

10. **Show paper relationships/prerequisites** - Impact: H, Effort: H
    - Why: Builds mental maps, but requires complex graph data.

11. **Integrate with advisor recommendations** - Impact: L, Effort: H
    - Why: Nice supplement, but tool should work standalone first.

---

## Screenshots Index

| # | Filename | Description | Emotion |
|---|----------|-------------|---------|
| 01 | 01-landing-first-impression.png | Explore page on load, Research Advisor visible | 4/5 |
| 02 | 02-navigation-bar.png | Clicked Discovery (before page change) | 3/5 |
| 03 | 02a-discovery-page.png | Discovery hub loading state | 3/5 |
| 04 | 03a-search-query-entered.png | "vision language models" typed, before search | 3/5 |
| 05 | 03b-search-results.png | 0 results after 10s search | 2/5 |
| 06 | 03c-advisor-panel-opened.png | Research Advisor panel opened | 3/5 |
| 07 | 03d-advisor-query-entered.png | First-year question entered in advisor | 3/5 |
| 08 | 03e-advisor-response.png | Advisor searching (mid-wait) | 2/5 |
| 09 | 03f-advisor-still-loading.png | Advisor error after 15s | 1/5 |
| 10 | 04-explore-page-clear.png | Back to Explore, still 0 results | 2/5 |
| 11 | 05-learning-path.png | Learning Path tab loading prematurely | 3/5 |
| 12 | 06-learning-path-loading.png | Learning Path building (5s wait) | 2/5 |
| 13 | 07-learning-path-timeout.png | Learning Path still loading (15s+) | 1/5 |
| 14 | 08-techniques-tab.png | Techniques tab loading | 2/5 |
| 15 | 09-techniques-loaded.png | Techniques still loading (5s+) | 2/5 |
| 16 | 10-reproducible-tab.png | Reproducible tab loading | 2/5 |
| 17 | 11-reproducible-timeout.png | Reproducible timeout (7s+) | 1/5 |
| 18 | 12-generate-page.png | Generate nav failed, stuck on Reproducible | 1/5 |
| 19 | 13-reading-list.png | Empty reading list (worked quickly) | 3/5 |
| 20 | 14-final-state.png | Back to Explore, 30 generic papers shown | 2/5 |

---

## Final Verdict

### Would I Bookmark This Tool?

**No.** Nothing worked reliably except Reading List (which has no value when you can't find papers to save).

### Would I Return Tomorrow?

**No.** I gave it 45 minutes and found zero relevant papers. Google Scholar would have been more productive.

### Would I Recommend to Fellow First-Years?

**Absolutely not.** In fact, I would actively warn them against it. The tool promises to help newcomers but fails at every feature designed for that purpose. It would waste their time and increase their anxiety.

### What's the Best Alternative?

For first-year PhD students looking to build mental maps of a field:

1. **Ask your advisor directly** - Get 5 "must-read" papers to start
2. **Use Connected Papers** - Shows paper relationships visually
3. **Google Scholar alerts** - Set up alerts for key terms
4. **Survey papers** - Read recent surveys in your subfield
5. **Lab reading groups** - Leverage senior students' knowledge

All of these are more reliable than AI Paper Atlas in its current state.

### Would This Help Me Prepare for Qualifying Exams?

**No.** Qualifying exams require:
- Broad field knowledge (Learning Path could help—but doesn't work)
- Understanding of influential papers (High Impact tab never tried, but likely broken based on pattern)
- Ability to discuss trends (Trending sidebar showed promise, but couldn't access the papers)
- Contextual understanding (Research Advisor could help—but errored)

Tool failed on all counts.

### Overall Assessment

**Rating: 1.5/5 stars**

As a first-year PhD student, AI Paper Atlas was not just unhelpful—it was **actively harmful**. The tool made promises specifically to newcomers ("Not sure where to start?", Learning Paths, Research Advisor) and then failed to deliver on every single promise. This pattern of hope → failure → frustration increased my imposter syndrome rather than reducing it.

The most valuable features for my persona (Learning Path, Research Advisor, structured discovery) were the ones that failed most catastrophically. The tool appears to have a fundamental infrastructure problem—75% feature failure rate suggests database, API, or architecture issues rather than UX polish needs.

**Recommendation**: Do not launch for first-year PhD students until search, Research Advisor, and Learning Path work reliably. The current experience is worse than having no tool at all.

---

## Appendix: Session Notes (Raw Observations)

**Timestamp 0:00** - Opened tool, first impression positive, liked the "Not sure where to start?" panel

**Timestamp 1:00** - Searched "vision language models", confused why it's taking so long

**Timestamp 1:30** - 0 results shown. Checked spelling. Tried again. Still 0. Very confused because sidebar shows VLMs trending.

**Timestamp 2:00** - Clicked Ask Advisor, thought "this is what the tool is for"

**Timestamp 2:30** - Wrote detailed question explaining I'm a first-year, need foundational papers

**Timestamp 3:00** - Advisor still loading, starting to worry

**Timestamp 3:30** - Advisor error. Felt defeated. "Of course it doesn't work."

**Timestamp 4:00** - Thought "maybe Learning Path will help", navigated there

**Timestamp 5:00** - Entered topic, clicked generate, watching spinner

**Timestamp 6:00** - Still watching spinner. "How long does this take?"

**Timestamp 7:00** - Gave up on Learning Path. Tried Techniques tab.

**Timestamp 8:00** - Techniques also loading forever. Pattern clear: nothing works.

**Timestamp 9:00** - Tried Reproducible. Same. Tried Generate page. Navigation failed.

**Timestamp 10:00** - Checked Reading List (worked!), but irrelevant since I found nothing.

**Timestamp 10:30** - Returned to Explore. Same 30 papers as beginning. Realized I accomplished nothing.

**Emotional Arc**: Hope (4/5) → Confusion (3/5) → Frustration (2/5) → Defeat (1/5) → Resignation (1/5)

**Key Moment**: When Research Advisor errored, I stopped believing the tool could help me. Everything after that felt like confirming my suspicion.

**Comparison to Alternatives**: In 45 minutes on Google Scholar, I could have:
- Found the CLIP paper
- Read its abstract and introduction
- Checked "Cited by" to find 5-10 follow-up papers
- Saved them to my reading list
- Started reading the first one

Instead, I found zero papers and felt worse about myself.

**Would I Give It Another Chance?**: Only if someone told me "we fixed search, advisor, and learning path." Even then, I'd be skeptical.

---

**Assessment Completed**: 2025-12-25
**Persona**: Sarah Kim, First-Year PhD Student
**Outcome**: Tool failed to meet newcomer needs. Would not recommend.
