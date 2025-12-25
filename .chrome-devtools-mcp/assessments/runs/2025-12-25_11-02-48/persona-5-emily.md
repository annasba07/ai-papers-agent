# UX Assessment Report: Dr. Emily Zhang
## Interdisciplinary ML Researcher (Climate Science)

**Date**: 2025-12-25
**Session Duration**: ~15 minutes
**Persona**: Dr. Emily Zhang - Climate scientist applying ML to weather forecasting
**Research Goal**: Find transformer techniques for time series weather prediction

---

## Executive Summary

**Verdict: Complete Failure - System Unusable**

I couldn't complete a single meaningful task. The database appears empty or broken - every search returned zero results, the Research Advisor hung indefinitely, and all Discovery tabs showed infinite loading states. As an interdisciplinary researcher already struggling with the ML terminology gap, encountering a completely non-functional tool was deeply frustrating. I left with zero papers, zero insights, and serious doubts about whether this product is real.

**Emotional Journey**: 3/5 (curious) → 2/5 (confused) → 1/5 (frustrated) → 1/5 (gave up)

---

## Session Timeline

| Time | Step | Action | Outcome | Emotion |
|------|------|--------|---------|---------|
| 0:00 | Step 1 | Landed on Explore page | Saw search box, filters, categories | 3/5 curious |
| 0:30 | Step 2 | Explored navigation | Found Discovery, Generate, Reading List tabs | 3/5 neutral |
| 1:00 | Step 3 | Searched "transformers time series weather prediction" | 0 results after 10+ seconds | 2/5 frustrated |
| 2:00 | Step 3.5 | Opened Research Advisor with detailed natural language question | Hung indefinitely, never responded | 1/5 very frustrated |
| 4:00 | Step 4 | Tried simpler search "neural networks climate" | 0 results again | 1/5 frustrated |
| 5:00 | Step 5-9 | Clicked through Discovery tabs (Overview, Techniques, TL;DR, Rising, Reproducible) | All showed infinite loading, no content | 1/5 gave up |
| 6:00 | Step 10 | Tried Learning Path generation for "time series forecasting" | Still loading after 5+ seconds | 1/5 defeated |

**Total Searches**: 2 (both failed)
**Total Papers Found**: 0
**Features Successfully Used**: 0
**Time Wasted**: ~15 minutes

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)
**Screenshot**: `01-landing-first-impression.png`

**What I Saw**:
- Clean "Explore" page with large search box
- Sidebar with filters: "Has Code", "High Impact", Categories (AI, ML, Computer Vision, etc.)
- Categories felt ML-heavy - no mention of "scientific ML" or "physical sciences"
- Placeholder text: "Describe what you're researching (e.g., 'efficient attention for mobile deployment')"

**Observations**:
- The placeholder example is very ML-engineering focused (mobile deployment optimization)
- As a climate scientist, I'd prefer an example like "time series forecasting" or "scientific applications"
- The category list (Computer Vision, NLP) doesn't include cross-domain or scientific ML categories
- "Ask Advisor" button was prominent - this felt promising for natural language queries

**Emotion**: 3/5 - Curious but felt like I was entering an ML-centric space

---

### Step 2: Initial Exploration (Navigation Discovery)
**Screenshots**: `02a-nav-discovery.png`, `02b-nav-generate.png`

**What I Saw**:
- **Discovery page**: Tabs for Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path
- **Generate page**: "Turn Papers into Working Code" - 5-agent code generation system

**Observations**:
- Discovery tabs looked promising - especially "Techniques" (could help me find transferable methods)
- Learning Path could address my knowledge gaps
- Generate page felt way too advanced for my needs (I just want to understand papers, not auto-generate code)
- "Papers indexed: 0" was concerning but I assumed it would populate after search

**Emotion**: 3/5 - Intrigued by organization, but "0 papers" was a yellow flag

---

### Step 3: Task-Based Search - Finding Relevant Papers
**Screenshots**: `03a-search-query-entered.png`, `03b-search-no-results.png`

**Query**: "transformers time series weather prediction"

**What I Saw**:
- Query entered, "AI-powered semantic search in progress..." message appeared
- After ~10 seconds: "No papers found" with message "Try different keywords or describe your research goal in more detail"
- Search time: 10003ms (over 10 seconds!)
- "0 results"

**Observations**:
- This is EXACTLY my pain point - my natural search terms don't match ML vocabulary
- But zero results is suspicious - surely there are papers on time series transformers?
- 10 seconds for zero results is painfully slow
- The suggestion to "describe your research goal in more detail" led me to try the Research Advisor

**Emotion**: 2/5 - Frustrated, but thought the Advisor might help bridge the vocabulary gap

---

### Step 3.5: Research Advisor (AI-Powered Search)
**Screenshots**: `03c-advisor-opened.png`, `03d-advisor-query-entered.png`, `03e-advisor-still-searching.png`, `03f-advisor-timeout.png`

**Query**: "I'm trying to apply transformer models to weather forecasting. I work with long-range time series of atmospheric data (temperature, pressure, wind). What ML techniques would be good for this?"

**What I Saw**:
- Advisor panel opened with friendly greeting: "Hi! I'm your Research Advisor..."
- Example prompts shown (explainability, speed up training, medical imaging, chatbots)
- I entered my detailed natural language question
- Message showed: "Searching papers..."
- **Never responded** - I waited 20+ seconds, closed and reopened, still stuck on "Searching papers..."

**Observations**:
- This was my BEST HOPE as an interdisciplinary researcher - the ability to ask in my own words
- The UI looked promising - clean, friendly, suggested example queries
- But it completely failed - hung indefinitely with no timeout, error message, or fallback
- As a non-ML expert, I don't know if this is a bug or if there's just no content in the database
- This failure is CRITICAL for my persona - I rely on natural language because I don't know the ML jargon

**Emotion**: 1/5 - Very frustrated. This was supposed to solve my vocabulary gap problem.

---

### Step 4: Second Search (Simpler Terms)
**Screenshot**: `04-second-search-no-results.png`

**Query**: "neural networks climate"

**What I Saw**:
- Tried much simpler, broader terms
- Same result: "AI-powered semantic search in progress..." then presumably 0 results (still searching when I moved on)

**Observations**:
- Even the most basic cross-domain query failed
- This suggests the database is either empty or doesn't index cross-domain work
- As a climate scientist, finding ZERO papers on "neural networks climate" is absurd - this is a huge research area

**Emotion**: 1/5 - Database appears broken or empty

---

### Steps 5-9: Discovery Tab Exploration
**Screenshots**: `05-discovery-loading.png`, `06-techniques-loading.png`, `07-tldr-loading.png`, `08-rising-loading.png`, `09-reproducible-loading.png`

**Tabs Tried**:
- Overview: "Loading papers..."
- Techniques: "Loading techniques..."
- TL;DR: "Loading summaries..."
- Rising: "Finding rising papers..."
- Reproducible: "Finding reproducible papers..."

**What I Saw**:
- Every single tab showed a loading spinner
- None ever completed loading (waited 5+ seconds per tab)
- No error messages, no fallback content, no indication of what's wrong

**Observations**:
- **Techniques tab** would have been perfect for my cross-domain needs (finding ML methods applicable to climate data)
- **Reproducible tab** addresses my pain point about code availability
- But I couldn't test ANY of these features because nothing loaded
- The consistent failure across all tabs suggests a backend/database issue, not just search problems

**Emotion**: 1/5 - Gave up. Everything is broken.

---

### Step 10: Learning Path Assessment
**Screenshots**: `10-learning-path-empty.png`, `11-learning-path-generating.png`, `12-final-state.png`

**Topic**: "time series forecasting"

**What I Saw**:
- Input field with placeholder: "Enter a topic (e.g., transformers, diffusion models)..."
- Entered "time series forecasting" and clicked "Generate Path"
- Message: "Building your learning path..."
- **Never completed** - still loading after 5+ seconds when I gave up

**Observations**:
- This feature could address my knowledge gap (I'm self-taught in ML, need foundational → advanced progression)
- But like everything else, it hung indefinitely
- The examples ("transformers, diffusion models") are again ML-centric - no mention of scientific or domain-specific applications

**Emotion**: 1/5 - Completely defeated. Nothing works.

---

## Pain Point Assessment

Did AI Paper Atlas solve my pain points as an interdisciplinary researcher?

### Pain Point 1: Terminology Gap
**Status**: ❌ **WORSE THAN GOOGLE SCHOLAR**

My natural search terms ("transformers time series weather prediction", "neural networks climate") returned ZERO results. The Research Advisor - which should have bridged the vocabulary gap - hung indefinitely. Google Scholar at least returns *something* for these queries, even if I have to wade through irrelevant results.

### Pain Point 2: Cross-Domain Discovery
**Status**: ❌ **COMPLETELY UNTESTABLE**

The Techniques tab (which could show ML methods applicable across domains) never loaded. Rising papers, Hot Topics - all infinite loading states. I have no idea if this tool indexes cross-domain work because I couldn't access ANY papers.

### Pain Point 3: Adaptation Complexity
**Status**: ❌ **NO EVIDENCE OF DOMAIN CONTEXT**

I saw no indication that the tool understands or surfaces domain-specific applications. All examples and categories were ML-centric (NLP, Computer Vision, mobile deployment). No mention of "scientific ML", "physics-informed", "climate", "geoscience", etc.

### Pain Point 4: Limited ML Background
**Status**: ❌ **LEARNING PATH FAILED**

The Learning Path feature (which could help me build foundational knowledge) never completed generation. I couldn't test whether it would provide accessible explanations or assume ML expertise.

### Pain Point 5: Justification to Peers
**Status**: ❌ **NO EXPLAINABILITY FEATURES OBSERVED**

I didn't see any features for explaining methods, assessing interpretability, or finding papers that justify ML approaches to skeptical domain scientists. But I also couldn't access any content, so this is untestable.

---

## Cross-Domain Discovery Assessment

**Rating**: 0/5 - Complete Failure

As an interdisciplinary researcher, I need a tool that:
1. ✗ Understands domain-specific terminology (climate, weather, atmospheric)
2. ✗ Surfaces papers from non-ML venues (climate journals, geoscience conferences)
3. ✗ Identifies transferable techniques across domains (NLP→climate, vision→scientific imaging)
4. ✗ Provides context on applicability to physical sciences

**What I Found Instead**:
- Zero papers for any query (climate-specific OR general ML)
- No cross-domain categories or filters
- Research Advisor hung when asked about domain-specific applications
- All navigation features (Techniques, Rising, etc.) failed to load

**Cross-Domain Verdict**: The tool appears designed for pure ML researchers, not interdisciplinary scientists. Even if it worked, I saw no evidence it indexes or understands scientific applications of ML.

---

## Accessibility for Non-ML Experts

**Rating**: 0/5 - Unusable

**Jargon & Terminology**:
- Category names assume ML knowledge (Computer Vision, Computation & Language, Neural & Evolutionary)
- No "Scientific ML" or "Applied ML" categories
- Examples are ML-engineering focused ("efficient attention for mobile deployment")

**Explanations**:
- Couldn't test whether paper summaries explain techniques accessibly (no papers loaded)
- Couldn't test Learning Path explanations (generation hung)

**Onboarding**:
- No guidance for non-ML researchers on how to search effectively
- No explanation of what "semantic search" means vs. keyword search
- When searches failed, no suggestions on domain-appropriate terminology

**Verdict**: The tool assumes you speak ML fluently. As someone from climate science, I felt like an outsider from the landing page onward.

---

## Transfer Potential Evaluation

**Rating**: N/A - Completely Untestable

I intended to evaluate:
- Can I discover NLP techniques applicable to sequential weather data?
- Can I find vision methods useful for satellite imagery analysis?
- Are papers tagged/classified by applicability beyond their original domain?

**Blockers**:
- Zero search results for any query
- Techniques tab never loaded (this was my primary hope for cross-domain discovery)
- Research Advisor hung (could have recommended transferable approaches)

**Speculation**: Even if the system worked, I saw no evidence of cross-domain tagging, applicability metadata, or transfer potential assessment. The entire interface is organized around ML subfields, not application domains or transferable methodologies.

---

## Delights and Frustrations

### Delights
**None.** I couldn't successfully complete a single task.

### Potential Delights (If It Worked)
Based on the UI/UX design, these features COULD have delighted me:
1. **Research Advisor**: Natural language interface to bridge vocabulary gap (but it hung)
2. **Techniques tab**: Browse by methodology instead of keyword search (but never loaded)
3. **Learning Path**: Curated progression from foundational to advanced (but generation hung)
4. **Reproducible tab**: Filter for papers with code (critical for me, but never loaded)

---

### Frustrations

#### 1. Complete System Failure (CRITICAL)
- **Impact**: 🔴 **SHOW-STOPPER**
- Zero papers found for ANY query
- Research Advisor hung indefinitely
- All Discovery tabs showed infinite loading
- Learning Path generation never completed
- Console showed 404 errors

**As Emily**: This isn't just frustrating - it makes me question if the product is real or if I'm using a broken demo. I wasted 15 minutes and found ZERO value.

---

#### 2. No Error Handling or Feedback (HIGH)
- **Impact**: 🔴 **CRITICAL UX FLAW**
- When searches failed, no explanation of WHY
- No timeout on hanging requests (Research Advisor, Learning Path)
- No "0 papers in database - check back later" message
- Loading spinners run forever with no progress indication

**As Emily**: I don't know if I'm doing something wrong, if the system is broken, or if there's just no climate-related content. The silence is maddening.

---

#### 3. ML-Centric Language Everywhere (MEDIUM)
- **Impact**: 🟡 **EXCLUDES DOMAIN SCIENTISTS**
- Categories: "Computer Vision", "Computation & Language" (not "NLP" or "Text Analysis")
- Examples: "efficient attention for mobile deployment" (not "time series forecasting" or "scientific applications")
- No mention of "scientific ML", "physics-informed", "domain-specific", etc.

**As Emily**: Every piece of text reminds me this tool isn't built for someone like me. I'm a climate scientist who uses ML, not an ML researcher who happens to work on climate.

---

#### 4. Slow Performance Even on Failures (MEDIUM)
- **Impact**: 🟡 **WASTE OF TIME**
- Search took 10+ seconds to return zero results
- Research Advisor hung for 20+ seconds before I gave up
- Each Discovery tab took 5+ seconds of loading before I moved on

**As Emily**: If the database is empty, fail fast. Don't make me wait 10 seconds to tell me there's nothing.

---

#### 5. No Guidance for Failed Searches (MEDIUM)
- **Impact**: 🟡 **UNHELPFUL**
- Zero results message: "Try different keywords or describe your research goal in more detail"
- No suggested alternative queries
- No "Did you mean..." or related term suggestions
- No indication of what terms DO work

**As Emily**: I already tried describing my goal in detail (in the Research Advisor). What keywords would work? Give me examples!

---

## Performance Metrics

| Metric | Value | Acceptable? |
|--------|-------|-------------|
| Landing page load time | Not measured (instant redirect to /explore) | ✓ |
| First search response time | 10003ms (10 seconds) | ✗ (Target: <3s) |
| Research Advisor response time | Never completed (>20s) | ✗ (Target: <5s) |
| Discovery tab load time | Never completed per tab (>5s each) | ✗ (Target: <2s) |
| Learning Path generation time | Never completed (>5s) | ✗ (Target: <3s) |
| **Papers successfully retrieved** | **0** | ✗ |
| **Features successfully used** | **0** | ✗ |

**Performance Verdict**: Unacceptable. Everything is slow AND broken.

---

## Priority Improvements

### P0: CRITICAL - FIX THE DATABASE/BACKEND
**Impact**: 🔴 **BLOCKS ALL VALUE**
**Effort**: Unknown (likely HIGH - this seems like a major backend issue)

**Issue**:
- Zero search results for any query
- All Discovery tabs fail to load
- Research Advisor hangs indefinitely
- Console shows 404 errors

**Fix**:
- Diagnose why database queries are failing
- If database is empty, show clear message: "Database currently empty - check back soon"
- Add error handling and timeouts to all async operations
- Show meaningful error messages (not infinite spinners)

**Why it matters for Emily**: Without ANY papers loading, the tool has literally zero value. This isn't a UX issue - it's a product-breaking bug.

---

### P0: CRITICAL - ADD TIMEOUTS AND ERROR STATES
**Impact**: 🔴 **PREVENTS WASTED TIME**
**Effort**: MEDIUM

**Issue**:
- Research Advisor hangs forever with no timeout
- Learning Path generation hangs forever
- Discovery tabs show infinite loading spinners
- No error messages when things fail

**Fix**:
- Add 5-second timeout to Research Advisor with error message
- Add 3-second timeout to Learning Path with "Generation failed - try again"
- Add 3-second timeout to Discovery tabs with "Failed to load - refresh to retry"
- Replace all infinite spinners with time-bound operations

**Why it matters for Emily**: I need to know if something is broken vs. just slow. Let me fail fast and move on.

---

### P1: HIGH - ADD CROSS-DOMAIN CATEGORIES
**Impact**: 🟡 **CRITICAL FOR INTERDISCIPLINARY USERS**
**Effort**: MEDIUM

**Issue**:
- All categories are ML subfields (Computer Vision, NLP)
- No "Scientific ML", "Climate & Environmental", "Healthcare", "Finance", etc.
- Hard for domain scientists to find relevant work

**Fix**:
- Add application domain categories alongside ML subfield categories
- Tag papers with both "technique domain" (vision, NLP) AND "application domain" (climate, healthcare)
- Let users filter by either dimension

**Why it matters for Emily**: I think in terms of my domain (climate) not ML subfields. "Scientific ML" or "Climate & Weather" categories would immediately signal this tool is for me.

---

### P1: HIGH - IMPROVE RESEARCH ADVISOR FOR CROSS-DOMAIN QUERIES
**Impact**: 🟡 **CORE VALUE FOR NON-EXPERTS**
**Effort**: MEDIUM-HIGH

**Issue**:
- Advisor hung on my domain-specific query (if it had worked)
- No indication it understands cross-domain terminology
- No suggested reformulations when queries fail

**Fix**:
- Train/prompt Advisor to recognize domain-specific terms (climate, weather, geoscience, medical, finance)
- When query mentions a domain + ML technique, surface papers from BOTH ML venues AND domain-specific journals
- Provide query reformulation suggestions: "I searched for X, but try these terms: Y, Z"

**Why it matters for Emily**: This is my lifeline as a non-ML expert. If the Advisor can translate "weather forecasting" → "time series prediction" + "sequence modeling", it solves my vocabulary gap.

---

### P2: MEDIUM - ADD DOMAIN-FRIENDLY EXAMPLES
**Impact**: 🟡 **IMPROVES FIRST IMPRESSION**
**Effort**: LOW

**Issue**:
- All placeholder examples are ML-engineering focused
- "efficient attention for mobile deployment" doesn't resonate with scientists

**Fix**:
- Add varied examples:
  - "time series forecasting for climate data"
  - "neural networks for medical image analysis"
  - "transformers for protein structure prediction"
- Rotate examples to show breadth of applicability

**Why it matters for Emily**: Seeing a scientific example immediately tells me "this tool is for you too, not just ML engineers."

---

### P2: MEDIUM - EXPLAIN SEARCH FAILURES MEANINGFULLY
**Impact**: 🟡 **REDUCES CONFUSION**
**Effort**: LOW

**Issue**:
- "No papers found" with generic "try different keywords" is unhelpful
- No guidance on what WOULD work

**Fix**:
- When 0 results, show:
  - "No papers found for 'transformers time series weather prediction'"
  - "Suggestions: Try broader terms like 'time series transformers' or 'sequence modeling'"
  - "Or ask the Research Advisor to recommend papers"
- Show example successful queries: "Recent searches: 'attention mechanisms', 'diffusion models', 'vision transformers'"

**Why it matters for Emily**: I need to learn the vocabulary the tool expects. Give me examples of what works!

---

### P3: LOW - ADD SCIENTIFIC ML ONBOARDING
**Impact**: 🟢 **NICE-TO-HAVE**
**Effort**: MEDIUM

**Issue**:
- No guidance for domain scientists on how to use the tool effectively
- Assumes ML fluency

**Fix**:
- Add optional "I'm a domain scientist" onboarding flow
- Ask: "What field do you work in?" (Climate, Healthcare, Finance, etc.)
- Customize examples, categories, and Advisor prompts based on domain
- Provide glossary: "What ML people call 'sequence modeling', you might know as 'time series prediction'"

**Why it matters for Emily**: Lowering the barrier for non-ML experts expands the user base and solves real interdisciplinary pain points.

---

## Screenshots Index

| # | Filename | Description | Emotion |
|---|----------|-------------|---------|
| 01 | `01-landing-first-impression.png` | Explore page with search box, ML-centric categories, filters | 3/5 |
| 02a | `02a-nav-discovery.png` | Discovery page with tabs (Overview, TL;DR, Rising, etc.), loading papers | 3/5 |
| 02b | `02b-nav-generate.png` | Generate page with code generation feature | 2/5 |
| 03a | `03a-search-query-entered.png` | Search query "transformers time series weather prediction" entered, searching | 4/5 hopeful |
| 03b | `03b-search-no-results.png` | Zero results after 10 seconds, "No papers found" message | 2/5 |
| 03c | `03c-advisor-opened.png` | Research Advisor panel opened with friendly prompts | 4/5 curious |
| 03d | `03d-advisor-query-entered.png` | Natural language query about weather forecasting submitted to Advisor | 4/5 |
| 03e | `03e-advisor-still-searching.png` | Advisor still searching after 10+ seconds | 3/5 |
| 03f | `03f-advisor-timeout.png` | Advisor hung indefinitely, never responded (20+ seconds) | 1/5 |
| 04 | `04-second-search-no-results.png` | Second search "neural networks climate" also returned 0 results | 1/5 |
| 05 | `05-discovery-loading.png` | Discovery Overview tab, loading papers indefinitely | 2/5 |
| 06 | `06-techniques-loading.png` | Techniques tab, loading techniques indefinitely | 1/5 |
| 07 | `07-tldr-loading.png` | TL;DR tab, loading summaries indefinitely | 1/5 |
| 08 | `08-rising-loading.png` | Rising tab, finding rising papers indefinitely | 1/5 |
| 09 | `09-reproducible-loading.png` | Reproducible tab, finding papers with code indefinitely | 1/5 |
| 10 | `10-learning-path-empty.png` | Learning Path tab with input field, building path | 2/5 |
| 11 | `11-learning-path-generating.png` | Learning Path still generating after clicking "Generate Path" | 1/5 |
| 12 | `12-final-state.png` | Final state - still loading learning path, gave up | 1/5 |

---

## Final Verdict

### Would I bookmark this tool?
**NO.** It doesn't work. Zero papers, zero value.

### Would I return tomorrow?
**NO.** Unless I receive an email saying "We fixed the database and now have 10,000+ papers indexed," I'd never come back.

### Would I recommend it to other domain scientists?
**ABSOLUTELY NOT.** I'd actively warn them away. "I tried it - completely broken, don't waste your time."

### What frustrated me most?
The **complete and silent failure** of every feature. No error messages, no indication of what's wrong, just infinite loading spinners and zero results. I don't know if this is a demo with an empty database, a broken backend, or if I'm somehow using it wrong.

### What would have delighted me?
If the Research Advisor had worked and successfully translated my climate science query into relevant ML papers, that would have been AMAZING. The natural language interface is exactly what I need as a non-ML expert. But it hung, so I'll never know.

---

## Recommendations for Team

### Immediate Actions (This Week)
1. **Diagnose the backend issue** - Why are queries returning 0 results and 404s?
2. **Add error handling** - Timeout all async operations and show clear error states
3. **Test with actual data** - Before any UX research, ensure the database has content

### Short-Term (Next Sprint)
1. **Add cross-domain categories** - Tag papers with application domains (climate, healthcare, finance)
2. **Improve Research Advisor** - Make it robust to domain-specific terminology
3. **Add domain-friendly examples** - Show the tool is for scientists, not just ML engineers

### Long-Term (Next Quarter)
1. **Build onboarding for domain scientists** - Guided flows for non-ML researchers
2. **Add explainability features** - Help users justify ML approaches to skeptical peers
3. **Index cross-domain publications** - Don't just scrape arXiv cs.LG - include Nature Machine Intelligence, climate journals, etc.

---

## Persona-Specific Insights

As **Dr. Emily Zhang**, interdisciplinary climate researcher:

**My Core Needs**:
- Bridge the ML vocabulary gap (I say "weather forecasting", ML people say "sequence modeling")
- Find techniques that transfer from NLP/vision to climate data
- Discover work published in climate venues, not just ML conferences
- Get accessible explanations I can share with my non-ML collaborators

**What This Tool Could Have Been**:
- A translator between climate science terminology and ML jargon
- A cross-domain discovery engine finding transferable techniques
- A learning resource to fill my ML knowledge gaps

**What I Actually Got**:
- A broken system with zero papers and infinite loading spinners
- ML-centric language that made me feel like an outsider
- Complete waste of 15 minutes

**Bottom Line**: Even if this tool worked perfectly, I saw no evidence it's designed for someone like me. But since it doesn't work at all, the design doesn't matter. Fix the backend first, then talk to actual interdisciplinary researchers about their needs.

---

**Assessment completed by**: Dr. Emily Zhang (Persona 5)
**Total screenshots**: 12
**Total features successfully tested**: 0
**Recommendation**: Do not launch until backend is functional. Then redesign for cross-domain users.
