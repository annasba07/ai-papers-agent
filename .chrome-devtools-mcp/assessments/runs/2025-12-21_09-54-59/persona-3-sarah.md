# UX Assessment Report: AI Paper Atlas
**Persona**: Sarah Kim - 1st-year PhD Student, Stanford Vision Lab
**Session Date**: December 21, 2025
**Duration**: ~6 minutes (09:55:48 - 10:01:06 PST)
**Scenario**: Literature review for vision-language models research

---

## Executive Summary

As a first-year PhD student overwhelmed by the research landscape, I found AI Paper Atlas promising but frustratingly broken. The Learning Path feature I desperately needed failed completely. While the search and Research Advisor showed potential, multiple features returned errors. The code generation tool is exciting, but I couldn't assess if it helps newcomers build understanding or just skips the learning process.

**Overall Impression**: 3/5 - Good ideas undermined by technical issues.

---

## Session Timeline

| Time | Step | Action | Outcome | Emotion |
|------|------|--------|---------|---------|
| 09:55:48 | Start | Navigated to localhost:3000 | Landed on /explore, clean interface | 4/5 hopeful |
| 09:56 | 1 | First impression | Clear search box, "Ask Advisor" button prominent | 4/5 |
| 09:56 | 2 | Clicked Discovery nav | Saw tabs including "Learning Path" | 4/5 excited |
| 09:57 | 3 | Clicked Learning Path tab | Error: "Failed to fetch learning path" | 2/5 disappointed |
| 09:57 | 4 | Tried generating path for "vision language models" | Feature failed again | 2/5 frustrated |
| 09:58 | 5 | Returned to Explore, searched "vision language models CLIP" | Got 6 results with "Smart Results" badge | 4/5 |
| 09:59 | 6 | Clicked "Ask Advisor" | Panel opened with helpful prompt | 4/5 |
| 10:00 | 7-8 | Asked advisor about foundational papers as first-year | Got papers but "contextual synthesis unavailable" | 3/5 |
| 10:00 | 9 | Expanded paper details | Saw full abstract, tabs for Summary/Related/Benchmarks | 4/5 |
| 10:01 | 10-11 | Clicked "Related Papers" tab | Error: "Failed to fetch related papers" | 2/5 frustrated |
| 10:01 | 12-13 | Applied "Has Code" + "Beginner" filters | Filters worked, still showed 6 results | 4/5 |
| 10:01 | 14 | Checked Reading List | Empty state with clear instructions | 3/5 |
| 10:01 | 15 | Checked Generate page | Code generation feature looks amazing | 5/5 excited |
| 10:01 | 16 | Returned to Explore | Session complete | 3/5 |

**Performance Notes**:
- Search response: ~2 seconds (acceptable)
- Smart Results: ~1.9 seconds (good)
- Multiple features failed to load (Learning Path, Related Papers)

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)
**Screenshot**: 01-landing-first-impression.png

**What I Saw**: Clean, uncluttered interface. Large search box in center. "Ask Advisor" button in orange stood out. Sidebar with filters on left. Starter prompt suggestions visible ("Not sure where to start?").

**Thoughts**: "This looks approachable, not intimidating like arXiv. The 'Ask Advisor' button makes me feel like I can get help. I like that it says 'Not sure where to start?' - that's exactly how I feel."

**Emotion**: 4/5 - Hopeful and encouraged

---

### Step 2: Navigation Discovery
**Screenshot**: 02-discovery-page.png

**What I Saw**: Discovery page with multiple tabs: Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, **Learning Path**. Got an error message about failed to fetch impact papers.

**Thoughts**: "Learning Path! That's exactly what I need as a first-year. Let me click that."

**Emotion**: 4/5 - Excited to see Learning Path feature

---

### Step 3-4: Learning Path Attempt (CRITICAL FAILURE)
**Screenshots**: 03-learning-path-empty.png, 04-learning-path-error.png

**What I Saw**: Input box asking for a topic. I entered "vision language models". Clicked "Generate Path". Got error: "Failed to fetch learning path".

**Thoughts**: "This is SO disappointing. This is the feature I need most as a newcomer. If it worked, it could tell me which papers to read first, which are foundational, which are advanced. This would solve my biggest problem - not knowing where to start. But it's broken."

**Pain Point Impact**: **CRITICAL** - This directly addresses my #1 pain point (overwhelmed by volume, don't know where to start). Feature exists but doesn't work.

**Emotion**: 2/5 - Very frustrated and disappointed

---

### Step 5: Basic Search (SUCCESS)
**Screenshot**: 05-search-results-clip.png

**What I Saw**: Searched for "vision language models CLIP". Got 6 results quickly. Saw "Smart Results" badge with "AI-POWERED" label. First result showed a TL;DR summary.

**Thoughts**: "OK, at least search works. The 'Smart Results' label makes me curious - what makes these smart? The TL;DR is helpful for quick scanning."

**Emotion**: 4/5 - Relieved that something works

---

### Step 6-8: Research Advisor (PARTIAL SUCCESS)
**Screenshots**: 06-advisor-panel-opened.png, 07-advisor-searching.png, 08-advisor-response.png

**What I Saw**: Clicked "Ask Advisor". Panel slid in from right with friendly greeting and example questions. I asked: "I'm a first-year PhD student trying to understand vision-language models. Where should I start? What are the foundational papers everyone should know?"

Got response with 5 papers but message said "Contextual synthesis temporarily unavailable." Papers had titles like "Towards Understanding How Knowledge Evolves in Large Vision-Language Models" and "10 Open Challenges..."

Follow-up buttons: "How do these methods scale to larger models?", "What are the training costs involved?", "Find papers that cite these works"

**Thoughts**: "The advisor understands my question and tried to help. But 'contextual synthesis unavailable' means it's not giving me the structured answer I need. Are these foundational papers or just recent papers? I can't tell. The follow-up buttons are smart though."

**Pain Point Impact**: MODERATE - Partially addresses #2 (lack of context) but doesn't provide the historical narrative I need.

**Emotion**: 3/5 - Mixed feelings, feature exists but incomplete

---

### Step 9-11: Paper Details Exploration (MIXED)
**Screenshots**: 09-paper-expanded.png, 10-related-papers-loading.png, 11-related-papers-error.png

**What I Saw**: Expanded first paper. Saw tabs: Summary, Related Papers, Benchmarks. Full abstract shown with link to arXiv and "Generate Code" button. Clicked "Related Papers" tab. Got error: "Failed to fetch related papers" with Retry button.

**Thoughts**: "The paper expansion is nice - full abstract helps. But Related Papers failing is another blow. That's exactly what I need to build my mental map of the field. How does this paper connect to others? What came before it? What built on it? Can't find out."

**Pain Point Impact**: HIGH - Directly relates to pain point #4 (building mental map). Feature exists but broken.

**Emotion**: 2/5 - Frustrated by another failure

---

### Step 12-13: Filter Application (SUCCESS)
**Screenshots**: 12-has-code-filter.png, 13-beginner-filter.png

**What I Saw**: Applied "Has Code" filter - worked immediately, showed badge. Then added "Beginner" difficulty filter. Both filters applied, showed clear badges with X to remove. Still 6 results.

**Thoughts**: "Finally something that works reliably! The 'Has Code' filter is important to me - I want to run experiments. And 'Beginner' filter existing shows they thought about newcomers like me. But do these papers actually match both criteria, or is the filtering not working properly?"

**Emotion**: 4/5 - Satisfied that core functionality works

---

### Step 14: Reading List
**Screenshot**: 14-reading-list-empty.png

**What I Saw**: Empty state with bookmark icon. Clear message: "Bookmark papers from the Explore page to build your reading list."

**Thoughts**: "Simple and clear. I understand how to use it. Would be useful for keeping track of papers I want to read for my qualifying exam."

**Emotion**: 3/5 - Neutral, makes sense but haven't used it yet

---

### Step 15: Code Generation (EXCITING DISCOVERY)
**Screenshot**: 15-generate-page.png

**What I Saw**: "Turn Papers into Working Code" with 5-agent system explanation. Steps: Paper Analyzer → Test Designer → Code Generator → Test Executor → Debugger.

**Thoughts**: "This is AMAZING if it works! As someone new to the field, actually running code would help me understand papers better than just reading. But I'm also worried - will this let me skip understanding? Or will it help me learn by doing?"

**Ambivalence**: This is both exciting and concerning for a newcomer. Could be incredibly helpful for hands-on learning, or could enable me to fake understanding without building real knowledge.

**Emotion**: 5/5 - Very excited but with questions

---

## Pain Point Assessment

### Pain Point #1: Overwhelmed by Volume
**Did it help?**: **NO - Feature exists but broken**

The Learning Path feature would directly solve this ("where should I start?") but it failed completely. The Research Advisor partially helped by suggesting papers but didn't provide the structured progression I need.

**Status**: ❌ Core solution broken

---

### Pain Point #2: Lack of Context
**Did it help?**: **PARTIALLY**

The TL;DR summaries help with quick understanding. Research Advisor tries to provide context but "contextual synthesis unavailable" means it's not giving me the historical narrative I need. The Related Papers feature (which would show how papers connect) is broken.

**Status**: ⚠️ Some help but key features missing

---

### Pain Point #3: Imposter Syndrome
**Did it help?**: **MAYBE**

The "Beginner" difficulty filter existing shows they thought about newcomers, which is comforting. The Research Advisor's friendly tone helps. But the broken features make me feel like even the tool isn't working for me - reinforcing that feeling of being behind.

**Status**: ⚠️ UI is encouraging but broken features undermine confidence

---

### Pain Point #4: Building Mental Map
**Did it help?**: **NO - Feature exists but broken**

The Related Papers feature would be PERFECT for this - showing me how papers connect, what came before, what built on what. But it failed. Learning Path would also help with this structured overview. Both broken.

**Status**: ❌ Core features broken

---

### Pain Point #5: Qualifying Exam Anxiety
**Did it help?**: **POTENTIALLY**

If the Learning Path feature worked, it would directly help me prepare by showing progression from foundational to advanced papers. The Reading List could help me track "must-read" papers. The code generation could help me deeply understand key papers.

**Status**: ⚠️ Potential is there but execution is broken

---

## Learning Path Utility (CRITICAL FOR THIS PERSONA)

**Expected Value**: 10/10 - This would be THE killer feature for first-year PhD students
**Actual Value**: 0/10 - Completely broken

**What I Needed**:
- Suggested reading order from foundational to advanced
- Indication of which papers "everyone knows"
- Structured progression through the field
- Confidence that I'm learning in the right order

**What I Got**: Error messages

**Impact**: This failure significantly undermines the tool's value for newcomers. It's like advertising a GPS that doesn't work - the promise makes the failure worse.

---

## Delights

1. **"Ask Advisor" Conversational Interface** - Feels like talking to a senior grad student, not intimidating
2. **Beginner Difficulty Filter** - Shows they thought about newcomers like me
3. **Code Generation Feature** - Exciting possibility for hands-on learning
4. **TL;DR Summaries** - Quick scanning is helpful
5. **Clean UI** - Not overwhelming, feels approachable
6. **Smart Results Badge** - Makes me trust the AI is doing something useful

---

## Frustrations

1. **Learning Path Feature Broken** ⭐⭐⭐ CRITICAL - This is THE feature I need most
2. **Related Papers Feature Broken** ⭐⭐⭐ CRITICAL - Essential for building context
3. **Contextual Synthesis Unavailable** ⭐⭐ - Advisor gives papers but not narrative
4. **No Guidance on Which Papers are Foundational** ⭐⭐ - Can't tell what's a "must-read" vs recent variation
5. **No Indication of Paper Difficulty in Results** ⭐ - "Beginner" filter exists but can't see difficulty on individual papers
6. **No Way to See Citation Count or Impact** ⭐ - Can't tell which papers are actually influential

---

## Confidence Impact

**Before Using Tool**: 3/5 - Anxious but hopeful about finding good tools
**After Using Tool**: 2/5 - More anxious because even tools don't work for me

**Why Decreased**:
- Multiple features I specifically need (Learning Path, Related Papers) failed
- Makes me feel like even when I try to be proactive, things don't work
- Reinforces feeling of being behind ("everyone else probably has working tools")

**Positive Note**: The existence of beginner-focused features shows someone understands my problems, even if execution failed.

---

## Performance Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Initial page load | ~2s | Good |
| Search response time | ~2s | Good |
| Smart Results | ~1.9s | Good |
| Learning Path | ERROR | Failed |
| Related Papers | ERROR | Failed |
| Research Advisor response | ~5s | Acceptable but incomplete |

**Overall Performance**: Core search is fast, but critical features are completely broken.

---

## Priority Improvements (Impact/Effort)

### P0 - CRITICAL (Fix Immediately)

1. **Fix Learning Path Feature** - Impact: 10/10, Effort: ?
   - This is THE differentiator for helping newcomers
   - Current state is worse than not having the feature (broken promises)

2. **Fix Related Papers Feature** - Impact: 9/10, Effort: ?
   - Essential for building mental map
   - Core to understanding paper relationships

3. **Fix "Contextual Synthesis" in Research Advisor** - Impact: 8/10, Effort: ?
   - Currently gives papers without explaining WHY these papers or HOW they relate
   - Need narrative, not just list

### P1 - HIGH PRIORITY

4. **Add "Foundational" or "Highly Cited" Indicator** - Impact: 8/10, Effort: Low
   - Help me identify "must-read" papers
   - Add badge like "Classic Paper" or "Highly Influential (1000+ citations)"

5. **Show Difficulty Level on Each Paper Card** - Impact: 7/10, Effort: Low
   - Filter exists but can't see difficulty in results
   - Add small badge: "Beginner", "Intermediate", etc.

6. **Add "New to This Field?" Quick Start Guide** - Impact: 8/10, Effort: Medium
   - Landing page for newcomers
   - "Start here if you're learning vision-language models"
   - Curated "starter pack" of 5-7 essential papers

### P2 - MEDIUM PRIORITY

7. **Add "Prerequisites" Section to Paper Details** - Impact: 7/10, Effort: Medium
   - "To understand this paper, you should know: [concepts/papers]"
   - Helps me assess if I'm ready for a paper

8. **Add Citation Count and Trend** - Impact: 6/10, Effort: Low
   - Help me identify influential work
   - "2,341 citations, trending up"

9. **Improve Code Generation Guidance for Learners** - Impact: 6/10, Effort: Medium
   - Add explanation: "Understanding the code will help you understand the paper"
   - Provide learning prompts with generated code

### P3 - NICE TO HAVE

10. **Add "Reading Level" Estimate** - Impact: 5/10, Effort: Medium
    - "Expected reading time: 2 hours for newcomers"
    - "Math level: Advanced (requires understanding of __ "

11. **Add "Explains Concept" Tags** - Impact: 5/10, Effort: Medium
    - Papers tagged with concepts they explain well
    - "Good explanation of attention mechanism"

---

## Screenshots Index

1. **01-landing-first-impression.png** - Initial page load, clean explore interface
2. **02-discovery-page.png** - Discovery tabs with error on impact papers
3. **03-learning-path-empty.png** - Learning path input screen
4. **04-learning-path-error.png** - Learning path generation failed
5. **05-search-results-clip.png** - Search results with Smart Results badge
6. **06-advisor-panel-opened.png** - Research Advisor panel with examples
7. **07-advisor-searching.png** - Advisor processing query
8. **08-advisor-response.png** - Advisor response with papers (synthesis unavailable)
9. **09-paper-expanded.png** - Paper details with tabs
10. **10-related-papers-loading.png** - Related papers loading state
11. **11-related-papers-error.png** - Related papers failed error
12. **12-has-code-filter.png** - Has Code filter applied
13. **13-beginner-filter.png** - Both Has Code and Beginner filters applied
14. **14-reading-list-empty.png** - Reading list empty state
15. **15-generate-page.png** - Code generation feature overview
16. **16-final-state.png** - Returned to explore page

---

## Final Verdict

### Would I bookmark this tool?
**Maybe** - If the critical features (Learning Path, Related Papers) get fixed, absolutely yes. Currently, too broken.

### Would I return tomorrow?
**Probably not** - The features I need most don't work. I'd come back if I heard they fixed the Learning Path feature.

### Would I recommend to other first-years?
**No, not yet** - I'd feel embarrassed recommending a broken tool. I'd say "interesting ideas but wait until they fix the bugs."

### Would this help me prepare for qualifying exams?
**Potentially, if fixed** - The Learning Path feature would be invaluable. The code generation could help deep understanding. But in current state, no.

---

## Key Insight for Developers

**You built EXACTLY the right features for first-year PhD students, then didn't make them work.**

As a newcomer to research, I don't need "more papers" - Google Scholar gives me that. I need:
1. Structure (Learning Path) ❌ BROKEN
2. Context (Related Papers, historical narrative) ❌ BROKEN
3. Guidance (what to read first, what's foundational) ⚠️ PARTIAL
4. Confidence (am I learning the right things?) ⚠️ PARTIAL

The fact that you built Learning Path and Related Papers features shows you understand my needs. The fact that they're broken is devastating because you're SO CLOSE to being incredibly useful.

**Fix these two features and I'll tell everyone in my cohort about this tool. Leave them broken and I'll forget it exists.**

---

**Assessment completed**: December 21, 2025, 10:01 PST
**Total session time**: ~6 minutes
**Overall experience rating**: 3/5 - Promising but broken when it matters most
