# UX Assessment: Sarah Kim (1st-year PhD Student)
**Assessment Date**: 2025-12-25
**Session Duration**: ~20 minutes
**Persona**: Sarah Kim - Stanford CS PhD student (Year 1), researching vision-language models

---

## Executive Summary

As a first-year PhD student trying to build foundational knowledge in vision-language models, I found the tool moderately helpful but missing critical features for newcomers. The Research Advisor showed promise but lacked the historical context I desperately need. The Learning Path feature exists but wasn't well-integrated into my workflow. Search returned only 6 relevant papers for "vision language models" — missing foundational work like CLIP that I know I should read. Overall: **3/5** - Useful for recent papers, but doesn't solve my core problem of understanding how the field evolved.

---

## Pain Points Assessment

### Did it solve my 5 pain points?

1. **Overwhelmed by Volume** ❌ **NOT SOLVED**
   - Search returned only 6 AI-matched papers + 30 keyword matches
   - No clear "start here" guidance for newcomers
   - Missing obvious foundational papers (CLIP, VisualBERT, etc.)

2. **Lack of Context** ⚠️ **PARTIALLY ADDRESSED**
   - Research Advisor mentioned "evolution" but gave recent papers
   - No timeline view or historical progression shown
   - Paper detail view shows abstract but not "why this matters"

3. **Imposter Syndrome** ⚠️ **MIXED IMPACT**
   - Positive: "Not sure where to start?" panel felt welcoming
   - Negative: No beginner-friendly explanations or guided paths
   - Still don't know if I'm missing "must-read" papers

4. **Building Mental Map** ❌ **NOT SOLVED**
   - No visualization of paper relationships or field structure
   - "Related Papers" tab exists but didn't explore deeply
   - Can't see "who are the key researchers" or "major threads"

5. **Qualifying Exam Prep** ⚠️ **LIMITED VALUE**
   - Learning Path feature exists (!!) but wasn't surfaced in search flow
   - Would need to explicitly navigate to Discovery > Learning Path
   - Unclear if it covers breadth needed for qualifying exams

**Overall Problem-Solving Score: 2/5** - Found some recent papers but didn't reduce my anxiety or build understanding.

---

## Session Timeline

### Step 1: First Impression (Landing Page - 0:00-0:15)
- **Load Time**: ~2 seconds
- **Emotional State**: 3/5 (neutral, slightly hopeful)
- **Observations**:
  - Redirected to /explore immediately
  - "Not sure where to start?" advisor panel appeared - felt welcoming
  - Clean interface, not overwhelming
  - Search box prominent and obvious

**Screenshot**: `01-landing-first-impression.png`, `01b-landing-loaded.png`

---

### Step 2: Navigation Discovery (0:15-1:00)
- **Emotional State**: 4/5 (excited to find Learning Path)
- **Actions**: Clicked Discovery tab, explored Learning Path
- **Observations**:
  - Found Learning Path tab!! This is exactly what I need as a newcomer
  - But it was in Discovery, not surfaced in main search flow
  - Input field for generating custom learning paths
  - Shows "Building your learning path..." loading state

**Screenshots**: `02a-nav-discovery.png`, `02b-learning-path-empty.png`

**Key Frustration**: Learning Path wasn't suggested during search - had to discover it myself

---

### Step 3: Search - Finding VLM Papers (1:00-3:00)
- **Query**: "vision language models"
- **Response Time**: 8772ms (~9 seconds) - felt slow
- **Results**: 6 AI-matched + 30 keyword matches = 36 total
- **Emotional State**: 2/5 (confused, disappointed)

**Observations**:
- Only 6 semantically relevant papers found
- All papers from Dec 2024 - very recent
- **Missing foundational papers**: No CLIP, no VisualBERT, no early VLM work
- Papers shown: AdaptVision, "Confused Tourists", VisPlay, etc. - all advanced/recent
- "Smart Results ✦ AI-POWERED" badge - but results feel incomplete

**Screenshots**: `03a-search-typing.png`, `03b-search-results.png`, `03c-search-results-all.png`

**Critical Gap**: As a newcomer, I need chronological progression (2019 → 2024), not just latest papers.

---

### Step 3.5: Research Advisor (3:00-5:00)
- **Emotional State**: 4/5 (hopeful - this might help!)
- **Query**: "I'm starting research on vision-language models and need to understand how they evolved from early work to current state. What are the foundational papers I should read?"

**Observations**:
- Advisor panel opened smoothly
- Showed "Searching papers..." state
- Response: "Contextual synthesis temporarily unavailable"
- Gave 3-5 papers focused on VLA (vision-language-action) models for robotics
- **Not what I asked for**: I wanted VLM evolution, got robotics papers
- Suggested papers: "How Knowledge Evolves in LVLMs", "VLA Model Post-Training", etc.

**Screenshots**: `03d-advisor-opened.png`, `03e-advisor-response.png`, `03f-advisor-response-full.png`

**Major Disappointment**: Advisor didn't understand my need for foundational/historical papers. Gave advanced research instead.

---

### Step 4: Paper Detail View (5:00-6:00)
- **Emotional State**: 3/5 (interested but still confused)
- **Action**: Expanded "AdaptVision" paper

**Observations**:
- Full abstract shown - detailed and technical
- Tabs: Summary | Related Papers | Benchmarks
- Links: "Read on arXiv" | "Generate Code"
- **Missing for newcomers**:
  - No "Prerequisites" or "Background needed"
  - No "Difficulty: Advanced" warning
  - No "This builds on CLIP (2021)" context
  - Abstract assumes I know what VLMs are

**Screenshot**: `04-paper-expanded.png`

**Beginner's Frustration**: Can't tell if this paper is appropriate for my level or what I should read first.

---

### Step 5: Code Availability Filter (6:00-7:00)
- **Emotional State**: 4/5 (practical feature I need!)
- **Action**: Clicked "Has Code" filter

**Observations**:
- Filter applied successfully
- "Has Code" badge shown in active filters
- Same 36 results still shown (unclear how many have code)
- **Missing**: No visual indicator on papers (GitHub icon, star count, etc.)
- **Missing**: Can't see if code is official implementation or third-party

**Screenshot**: `05-has-code-filter.png`

**Usefulness**: Filter exists but unclear which papers actually have code without clicking each one.

---

## What I Didn't Test (Due to Time/Context)

- **Learning Path Generation**: Saw the feature but didn't generate a path for VLMs
- **Difficulty Filters**: Didn't try "Beginner" filter (would be crucial!)
- **Seminal Papers Filter**: This might have found CLIP! Didn't test
- **Related Papers Tab**: Didn't explore paper relationships
- **TL;DR Feed**: Didn't try quick scanning mode
- **Techniques Explorer**: Might help understand VLM methods

---

## Delights

1. **"Not sure where to start?" Panel** 🎉
   - Felt welcoming and acknowledged my confusion
   - Showed the tool understands newcomer anxiety
   - Suggested example queries

2. **Learning Path Feature Exists** 🎉
   - Exactly what I need as a PhD student!
   - "Curated learning progression by difficulty"
   - Could be transformative if well-executed

3. **Clean, Uncluttered Interface**
   - Not overwhelming like arXiv
   - Search box obvious and prominent
   - Filters well-organized in sidebar

4. **Research Advisor Concept**
   - Good idea to have AI guide me
   - Natural language queries feel approachable

---

## Frustrations

1. **Foundational Papers Missing** 😞
   - Search for "vision language models" didn't return CLIP
   - All results from late 2024 - no historical context
   - Can't build mental map without seeing evolution

2. **Learning Path Not Integrated** 😞
   - Found it in Discovery tab, not during search
   - Should have been suggested when I searched VLMs
   - Felt like hidden feature

3. **Advisor Misunderstood My Query** 😞
   - Asked for "how VLMs evolved" + "foundational papers"
   - Got robotics papers and recent research
   - "Contextual synthesis temporarily unavailable" - felt broken

4. **No Beginner Guidance** 😞
   - Can't tell which papers are appropriate for my level
   - No "start here" recommendations
   - No prerequisites or background shown

5. **Difficulty Indicators Missing** 😞
   - Papers look advanced but no confirmation
   - Can't filter to "papers accessible to 1st-year PhD"
   - Risk of reading papers I can't understand

---

## Priority Improvements (Sarah's Perspective)

### HIGH IMPACT / LOW EFFORT

1. **Surface Learning Path in Search Results** ⭐⭐⭐
   - **Impact**: 5/5 - Would solve my #1 problem
   - **Effort**: 2/5 - Just add suggestion box
   - **How**: When searching "vision language models", show: "🎓 Want a learning path for this topic? Click here"

2. **Add "Seminal Papers" Badge to Search** ⭐⭐⭐
   - **Impact**: 5/5 - Would highlight foundational work
   - **Effort**: 1/5 - Filter already exists, just show badge
   - **How**: Visual indicator on CLIP, VisualBERT, etc.: "📚 Seminal - Top 1% cited"

3. **Show Difficulty Level on Papers** ⭐⭐⭐
   - **Impact**: 4/5 - Prevents wasted time on inappropriate papers
   - **Effort**: 2/5 - Already have Beginner/Intermediate/Advanced categories
   - **How**: Badge on each paper: "🎯 Advanced" or "🌱 Beginner-Friendly"

### HIGH IMPACT / MEDIUM EFFORT

4. **Improve Advisor Understanding** ⭐⭐
   - **Impact**: 5/5 - Could become my primary way to explore
   - **Effort**: 4/5 - Requires better LLM prompting/RAG
   - **How**: When user mentions "foundational" or "evolution", prioritize chronological + high-citation papers

5. **Add Timeline/Evolution View** ⭐⭐
   - **Impact**: 5/5 - Solves "building mental map" problem
   - **Effort**: 4/5 - New visualization component
   - **How**: Show VLMs on timeline: 2019 (VisualBERT) → 2021 (CLIP) → 2024 (recent)

6. **Add "Prerequisites" to Paper Cards** ⭐⭐
   - **Impact**: 4/5 - Helps me understand learning path
   - **Effort**: 3/5 - Requires paper analysis
   - **How**: "📖 Background: Familiarity with transformers and contrastive learning"

### MEDIUM IMPACT / LOW EFFORT

7. **Show Code Indicators Visually** ⭐
   - **Impact**: 3/5 - Saves clicks to find reproducible work
   - **Effort**: 1/5 - Just add GitHub icon
   - **How**: "⭐ 2.3k GitHub stars" on paper cards

8. **Add "For Beginners" Section to Advisor** ⭐
   - **Impact**: 3/5 - Makes newcomers feel supported
   - **Effort**: 2/5 - Predefined prompt template
   - **How**: Suggested query button: "I'm new to [topic], where should I start?"

---

## Performance Metrics

- **Landing Page Load**: ~2 seconds (acceptable)
- **Search Response Time**: 8,772ms (~9 seconds) - **Too slow**, felt sluggish
- **Advisor Response Time**: ~5-7 seconds - Acceptable for AI query
- **Page Interactions**: Smooth, no lag

---

## Screenshots Index

1. `01-landing-first-impression.png` - Initial loading state
2. `01b-landing-loaded.png` - "Not sure where to start?" advisor panel
3. `02a-nav-discovery.png` - Discovery tab navigation
4. `02b-learning-path-empty.png` - Learning Path feature (empty state)
5. `03a-search-typing.png` - Search box with "vision language models" query
6. `03b-search-results.png` - Initial search results (1 paper visible)
7. `03c-search-results-all.png` - Full search results scrolled
8. `03d-advisor-opened.png` - Research Advisor panel opened
9. `03e-advisor-response.png` - Advisor processing query
10. `03f-advisor-response-full.png` - Advisor recommendations
11. `04-paper-expanded.png` - AdaptVision paper detail view
12. `05-has-code-filter.png` - "Has Code" filter applied

---

## Final Verdict

### Would this help me prepare for qualifying exams?

**Maybe** (2.5/5) - The Learning Path feature could be transformative, but it's hidden and I haven't tested it. Search results are too recent-focused. I'd need to manually find foundational papers elsewhere (Google Scholar, advisor recommendations) and then possibly use this tool to track recent advances.

### Would I recommend to other first-years?

**With caveats** (3/5) - I'd say: "Try the Learning Path feature in Discovery tab - it might help. But don't rely on search alone; you'll miss foundational papers. Good for staying current once you have the basics."

### Would I bookmark and return tomorrow?

**Uncertain** (2.5/5) - I'd give it another chance with the Learning Path feature. But if search continues to miss foundational work and Advisor doesn't understand "beginner" queries, I'd probably stick with Google Scholar + advisor guidance.

---

## The Newcomer Experience Gap

**Core Issue**: The tool feels optimized for researchers who already know the field. As a first-year PhD student:

- I don't know what I don't know
- I can't evaluate if papers are appropriate for my level
- I need **scaffolding** (prerequisites, learning paths, "start here")
- I need **context** (why does this paper matter? what came before?)
- I need **confidence** (am I missing key papers? is this the right learning order?)

**What would make me confident?**
- "You've read 3/10 foundational VLM papers"
- "Recommended next: CLIP (most cited, beginner-friendly)"
- "This learning path used by 50 other PhD students"

Without this, the tool adds to my imposter syndrome rather than reducing it.

---

## Emotional Journey

- **Start**: 3/5 (hopeful but anxious)
- **After Navigation**: 4/5 (excited about Learning Path!)
- **After Search**: 2/5 (disappointed - where's CLIP?)
- **After Advisor**: 2/5 (frustrated - didn't understand my need)
- **After Paper Detail**: 3/5 (neutral - good info but unclear fit)
- **End**: 3/5 (mixed feelings - potential but gaps)

**Overall Session**: The tool has good bones but doesn't solve the core first-year PhD problem: **How do I efficiently build foundational knowledge and confidence in a new research area?**
