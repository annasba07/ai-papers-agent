# UX Assessment Report: AI Paper Atlas - LIVE SESSION
## Persona: Sarah Kim - First-Year PhD Student

**Date:** December 16, 2025
**Session Start:** 15:39 PST
**Session Duration:** ~30 minutes
**Viewport:** 1440x900
**Chrome Instance:** chrome-3
**Assessment Type:** Live browser interaction via Chrome DevTools MCP

---

## Executive Summary

As a first-year PhD student desperately trying to understand vision-language models and build foundational knowledge, I found AI Paper Atlas to have a promising, welcoming interface that quickly devolved into crushing disappointment. The landing page spoke directly to my anxieties with "Not sure where to start?" messaging, and the AI-powered search delivered relevant results in ~2.6 seconds. However, **EVERY SINGLE discovery feature designed to help newcomers like me - learning paths, TL;DR views, technique explorers, and trending papers - returned 404 errors.** The Research Advisor feature, which could have been transformative, showed "contextual synthesis temporarily unavailable" and completely misunderstood my request for foundational historical context, instead recommending advanced papers that assume I already understand the field.

**Final Verdict:** Would NOT recommend to fellow first-year students. The tool feels half-built, with critical beginner features either broken or missing entirely.

**Overall Rating:** 3.5/10 (reduced from 6.5 in previous session due to discovering extent of missing features)

---

## Pain Point Assessment: Did It Solve My Problems?

### ❌ FAILED: Overwhelmed by Volume
**Before:** Don't know where to start among thousands of papers
**After:** Still overwhelmed, now also worried the tool is incomplete
**Why It Failed:** AI search narrowed results but provided no prioritization, impact indicators, or "must-read" guidance

### ❌ FAILED: Lack of Historical Context
**Before:** Don't understand how vision-language models evolved
**After:** Even more confused about evolution and foundations
**Why It Failed:**
- Research Advisor gave WRONG papers (about CLIP vs. before CLIP)
- Learning path feature = 404 error
- No timeline or progression visualization

### ❌ MADE WORSE: Imposter Syndrome
**Before:** Anxious about being behind peers
**After:** Feel more behind AND questioning if I'm using the right tools
**Why It Made It Worse:**
- "Temporarily unavailable" messages signal broken product
- Tool assumed I knew more than I do
- All beginner-support features are missing
- Multiple 404s made me feel like I'm navigating wrong

### ❌ FAILED: Building Mental Map
**Before:** No clear picture of field structure
**After:** No progress on mental map
**Why It Failed:**
- Technique explorer = 404
- No paper relationship graphs
- No indication of which papers are foundational vs. derivative

### ⚠️ PARTIALLY: Finding Relevant Papers
**Before:** Hard to find VLM-specific work
**After:** Found 10 relevant papers in 2.6 seconds
**Why Only Partial:** Found papers but no way to know if they're the RIGHT papers

---

## Detailed Session Timeline

### Step 0: Environment Setup (15:39)
- ✅ Set viewport 1440x900
- ✅ Created screenshot directory `.chrome-devtools-mcp/assessments/sarah-kim/`
- **Status:** Complete

### Step 1: First Impression (15:40)
**Screenshot:** `01-landing-first-impression.png`

**Visual Observations:**
- Clean beige/cream color palette - not intimidating
- Prominent search box with placeholder: "Describe what you're researching..."
- **CRITICAL POSITIVE:** Large beige card saying "Not sure where to start?" with message: "Tell me what you're working on and I'll find the most relevant papers, techniques, and implementations"
- Example queries visible: "Latest advances in LLM reasoning", "State-of-the-art multimodal learning"
- Sidebar filters: Has Code, High Impact, Categories, Difficulty levels (Beginner/Intermediate/Advanced/Expert)
- 30 papers pre-loaded (recent CV papers)
- Trending topics listed: LLM Agents, Mixture of Experts, RLHF, Diffusion, RAG

**Emotional State:** 4/5 (Pleasantly surprised)

**Reaction:** "Wow, this 'Not sure where to start?' message feels like it was written specifically for anxious first-years like me. I don't feel judged for not knowing what I'm doing."

**Load Time:** Unable to measure (Performance API returned error)

### Step 2: Navigation Discovery (15:42)
**Screenshot:** `02a-nav-generate-attempt.png`

**Actions:** Clicked "Generate" navigation item

**Findings:**
- Navigate to http://localhost:3000/generate
- Page shows: "MULTI-AGENT CODE GENERATION - Turn Papers into Working Code"
- Description: "Select a research paper and let our 5-agent system analyze, design tests, generate code, and debug until it works"
- Two-step interface: 1) Find a Paper, 2) Generate Code

**Emotional State:** 3/5 (Confused but intrigued)

**Reaction:** "Oh, so Generate is about turning papers into runnable code. That's actually cool for running experiments later, but not what I need right now. I need to understand papers before I can implement them. The navigation label 'Generate' didn't make this clear."

**Concern:** Only 2 nav items total - where are the other discovery features?

### Step 3: Task-Based Search (15:45)
**Screenshot:** `03-search-and-advisor-panel.png`

**Action:** Clicked suggested query button "State-of-the-art multimodal learning"

**Search Results:**
- Response time: 2573ms (~2.6 seconds)
- Results count: 10 papers (down from 30)
- Badge shown: "Smart Results ✦ AI-POWERED"
- Research Advisor panel auto-opened on right side

**Top Results:**
1. "Modality Curation: Building Universal Embeddings for Advanced Multimodal Information Retrieval"
2. "Exploring Embodied Multimodal Large Models: Development, Datasets, and Future Directions"
3. "Unimodal-driven Distillation in Multimodal Emotion Recognition with Dynamic Fusion"
4. [Additional results visible]

**Visual Issues Noted:**
- ALL papers show "Invalid Date" instead of publication dates
- Paper count mysteriously dropped from 30 to 10

**Emotional State:** 4/5 (Hopeful)

**Reaction:** "The search understood what I meant! These papers look relevant. The AI-POWERED badge makes me feel like it's doing something smart. And the Research Advisor opened automatically - maybe it can help guide me?"

**Positive:** Fast response (~2.6 sec feels responsive), semantically relevant results, TL;DR snippets helpful

**Concerns:** Only 10 results? Where are foundational papers like CLIP? All dates say "Invalid Date" which makes me nervous about data quality.

### Step 3.5: Research Advisor - CRITICAL FAILURE (15:48)
**Screenshot:** `03b-research-advisor-response.png`

**My Question:** "I'm a first-year PhD student trying to understand vision-language models like CLIP. I've read the CLIP paper but I'm missing the historical context - what foundational work should I read first to understand why CLIP was important?"

**Response:**
- **ERROR MESSAGE:** "Contextual synthesis temporarily unavailable"
- Quick brief: "Here is a quick brief of promising papers"
- 5 papers recommended:
  1. "Does CLIP perceive art the same way we do?"
  2. "Towards Understanding How Knowledge Evolves in Large Vision-Language Models"
  3. "A Novel Framework for Automated Explain Vision Model Using Vision-Language Models"
  4. "How Far Are AI Scientists from Changing the World?"
  5. "Verifying Cross-modal Entity Consistency in News using Vision-language Models"

- Follow-up suggestions:
  - "How do these methods scale to larger models?"
  - "What are the training costs involved?"
  - "Find papers that cite these works"

**Emotional State:** 2/5 (Frustrated and disappointed)

**Critical Analysis of Failure:**
1. **"Temporarily unavailable"** = Core feature is broken
2. **Wrong paper level:** I asked for papers BEFORE CLIP (foundational), got papers ABOUT CLIP (advanced)
3. **No historical context:** Recommendations assume I already understand the field
4. **No explanation:** Papers listed with no reasoning for why they matter or how they relate

**What I Actually Needed:**
- Papers on early image-text matching (pre-CLIP era)
- Visual semantic embeddings foundational work
- Contrastive learning fundamentals
- Historical progression showing how we got to CLIP

**Impact:** Made me feel like the tool doesn't understand where newcomers are starting from. INCREASED my imposter syndrome rather than reducing it.

### Step 4: Deep Dive - Paper Analysis (15:52)
**Screenshot:** `04-paper-detail.png`

**Action:** Clicked "Expand" button on "Modality Curation" paper

**Paper Detail View Shows:**
- Full abstract (complete text)
- Three tabs: "Summary" | "Related Papers" | "Benchmarks"
- Two action buttons: "Read on arXiv" | "Generate Code"
- Date still shows "Invalid Date"

**Full Abstract Text:**
"Multimodal information retrieval (MIR) faces inherent challenges due to the heterogeneity of data sources and the complexity of cross-modal alignment. While previous studies have identified modal gaps in feature spaces, a systematic approach to address these challenges remains unexplored. In this work, we introduce UNITE, a universal framework..."

**Emotional State:** 3/5 (Neutral - expected more value)

**What Was Good:**
- Full abstract helpful for understanding contribution
- Inline expansion smooth (no page reload)
- Tabs suggest additional depth available
- "Generate Code" button interesting for later experimentation

**What Was Missing (Critical for Newcomers):**
- No AI-generated plain-language summary ("ELI5" style)
- No difficulty level indicator (can I actually understand this?)
- No citation count or impact metrics
- No "this builds on X, extended by Y" relationship info
- No indication of code availability despite "Has Code" filter existing
- No extraction of key techniques/methodologies
- No indication whether this is foundational vs. incremental

**Verdict:** Shows the abstract I can get on arXiv. Not adding significant value beyond basic search.

### Steps 5-11: Discovery Features - CATASTROPHIC FAILURES (15:55-16:05)

#### Attempted Feature 1: Learning Path
- **URL:** `/discovery/learning-path`
- **Result:** **404 ERROR**
- **Screenshot:** `06-learning-path.png`
- **Emotional State:** 1/5 (Devastated)

**Impact:** This feature would be THE MOST VALUABLE for a first-year student trying to build systematic knowledge. Its absence is a dealbreaker.

#### Attempted Feature 2: TL;DR View
- **URL:** `/discovery/tldr`
- **Result:** **404 ERROR**
- **Screenshot:** `07-tldr-404.png`
- **Emotional State:** 1/5 (Increasingly concerned)

**Impact:** Quick scanning feature for staying current - unavailable

#### Attempted Feature 3: Technique Explorer
- **URL:** `/discovery/techniques`
- **Result:** **404 ERROR**
- **Screenshot:** `08-techniques-404.png`
- **Emotional State:** 1/5 (Losing faith)

**Impact:** Can't explore field's methodological landscape

#### Attempted Feature 4: Rising Papers
- **URL:** `/discovery/rising`
- **Result:** **404 ERROR**
- **Screenshot:** `09-rising-404.png`
- **Emotional State:** 1/5 (Completely let down)

**Impact:** Can't see what's gaining traction to avoid FOMO

**COMPREHENSIVE FINDING:** All advanced discovery features return 404. The tool appears to be in an incomplete/alpha state with only basic search functional.

### Step 12: Final State & Exit Reflection (16:08)
**Screenshot:** `12-final-state.png`

**Returned to:** http://localhost:3000/explore

**Overall Emotional Journey:**
- Start: Hopeful (4/5) → "Maybe this will help me feel oriented!"
- After search: Cautiously optimistic (4/5) → "The AI search works!"
- After Advisor failure: Frustrated (2/5) → "It doesn't understand my needs"
- After 404s: Devastated (1/5) → "All the features for people like me are broken"
- Final: Resigned (1/5) → "This isn't ready for first-year students"

---

## Delights (Few)

1. **"Not sure where to start?" message** - Empathetic, spoke directly to my anxiety ⭐⭐⭐⭐⭐
2. **Fast AI-powered search** - 2.6 seconds felt responsive ⭐⭐⭐⭐
3. **Clean, non-intimidating interface** - Didn't feel overwhelming on first load ⭐⭐⭐⭐
4. **TL;DR snippets** - Helpful for quick scanning without opening papers ⭐⭐⭐
5. **Code generation concept** - Interesting idea for future experimentation ⭐⭐⭐

---

## Frustrations (Many)

### P0 - CRITICAL (Tool-Breaking):

1. **ALL discovery features return 404** ⚠️⚠️⚠️⚠️⚠️
   - Learning paths, TL;DR view, techniques, rising papers all broken
   - These are EXACTLY the features newcomers need
   - Makes tool feel incomplete/alpha quality

2. **Research Advisor "contextual synthesis temporarily unavailable"** ⚠️⚠️⚠️⚠️⚠️
   - Core differentiating feature is broken
   - Destroys trust in platform reliability
   - "Temporarily" implies it usually works - feels like false advertising

3. **Advisor misunderstood my beginner-level question** ⚠️⚠️⚠️⚠️
   - Asked for foundational/historical papers
   - Got advanced papers assuming I already know the field
   - No ability to specify "I'm a beginner, start from basics"

### P1 - HIGH (Significant Impact):

4. **ALL papers show "Invalid Date"** ⚠️⚠️⚠️
   - Professional credibility issue
   - Makes me question data quality
   - Are these even real papers?

5. **No impact/importance indicators** ⚠️⚠️⚠️
   - Can't tell foundational from incremental work
   - No citation counts visible
   - No "highly influential" or "award-winning" badges

6. **No beginner guidance despite difficulty filters** ⚠️⚠️⚠️
   - Sidebar has Beginner/Intermediate/Advanced filters
   - Suggests someone knew users have different levels
   - But zero actual support for beginners

7. **Paper count dropped mysteriously** ⚠️⚠️
   - Went from 30 to 10 papers after search
   - No explanation why
   - Don't know if I'm seeing all relevant results

### P2 - MEDIUM (Annoyances):

8. **Navigation labels unclear** ⚠️⚠️
   - "Generate" doesn't communicate code generation
   - Have to click to discover what sections do

9. **Related Papers tab slow/didn't complete** ⚠️⚠️
   - Showed "Finding similar papers..." but didn't finish loading

10. **Trending topics not clickable** ⚠️
    - LLM Agents, MoE, RLHF, etc. listed but not interactive
    - Missed opportunity for discovery

---

## Confidence Impact: STRONGLY NEGATIVE

**Confidence Level Before:** 3/5 (anxious but willing to try)
**Confidence Level After:** 1/5 (more anxious, feel further behind)

### Why It Made Things Worse:

1. **Broken promises erode trust**
   - "Temporarily unavailable" = unreliable tool
   - Multiple 404s = incomplete product
   - Makes me question if I should invest time learning it

2. **Tool assumes I know more than I do**
   - Advisor gave advanced papers when I asked for basics
   - No "start here" guidance
   - No acknowledgment of different expertise levels

3. **Increased imposter syndrome**
   - All beginner-support features are missing
   - Feel like tool was built for people who already know what they're doing
   - Reinforces feeling that I'm behind

4. **Lost time and momentum**
   - Spent 30 minutes exploring broken features
   - Could have been reading actual papers
   - Feel like I wasted effort on wrong tool

### What Would Actually Help My Confidence:

- **Acknowledge my level** - "You're new to VLMs? Let's start here."
- **Show progress** - "You've covered 3/10 foundational papers in this area"
- **Normalize not knowing** - "Most people read X before attempting Y"
- **Provide roadmaps** - Clear progression from basics to advanced
- **Celebrate small wins** - "You now understand the pre-CLIP era!"

---

## Learning Path Utility: DEALBREAKER FAILURE

**Expected:** Curated progression from foundational to advanced papers
**Reality:** 404 ERROR
**Impact:** This is a **CRITICAL MISSING FEATURE** that makes the tool unsuitable for newcomers

### Why This Matters So Much:

The tool has a "Difficulty" filter with Beginner/Intermediate/Advanced/Expert options. This shows that *someone* understood that users at different levels need different things. But the one feature that would *actually* help beginners - a curated learning path - **doesn't exist**.

### What I Desperately Needed:

1. **Curated progression:** "To understand CLIP, read these 5 papers first in this order"
2. **Historical context:** Show how ideas evolved from early work to CLIP
3. **Concept building:** Start with simple ideas, gradually increase complexity
4. **Visual roadmap:** See the path from beginner to expert
5. **Validation:** Know I'm covering the right foundational material

### What I Got:

- A 404 page that says "This page could not be found"

### Emotional Impact:

**This made me feel:**
- Abandoned (tool doesn't care about newcomers)
- Behind (everyone else probably knows these foundational papers already)
- Frustrated (the one feature I need most doesn't work)
- Skeptical (if this basic feature is missing, what else is broken?)

---

## Qualifying Exam Preparation: COMPLETELY UNSUITABLE

**My Timeline:** Qualifying exam in 18 months
**What I Need:** Demonstrate broad, systematic knowledge with historical understanding
**Can This Tool Help?** **NO**

### Why It Fails for Exam Prep:

1. **No systematic coverage** - Can't verify I've covered all foundational work
2. **No learning paths** - Can't build knowledge progressively
3. **No historical context** - Can't explain how field evolved (exam questions ask this)
4. **No difficulty indicators** - Can't tell what's grad-student-appropriate
5. **No completion tracking** - Can't track what I've read vs. still need to read
6. **Unreliable features** - "Temporarily unavailable" means I can't depend on it

### What I'll Use Instead:

- **Google Scholar** - Citation counts, "cited by" relationships
- **arXiv** - Browse by recency and relevance
- **My advisor** - Ask for curated reading lists
- **Lab mates** - See what others recommend
- **Connected Papers** - Visualize paper relationships
- **Surveys/review papers** - Get structured field overviews

**Verdict:** Would NOT use this tool for qualifying exam preparation. Too unreliable, too incomplete, doesn't provide the structure and validation I need.

---

## Performance Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Landing page load | Unable to measure (API error) | - |
| Search response time | 2573ms (2.6 sec) | ✅ Acceptable |
| Research Advisor response | ~3-4 seconds | ✅ Acceptable (if it worked) |
| Paper detail expansion | <500ms | ✅ Fast |
| Discovery page loads | Instant 404s | ❌ Routing broken |

**Subjective Performance Feel:**
- Initial interactions: Responsive and smooth
- Feature access: Instant failures destroy experience
- Overall: Performance is fine, but features don't exist

---

## Priority Improvements - From Sarah's Perspective

### P0 - ABSOLUTELY CRITICAL (Blocking All Newcomer Adoption):

| Improvement | Impact | Effort | Urgency | Sarah's Rationale |
|------------|--------|--------|---------|-------------------|
| **Implement learning path feature** | EXTREME | High | IMMEDIATE | Without this, the tool has ZERO value for building foundational knowledge. This is the #1 feature I need. NON-NEGOTIABLE. |
| **Fix Research Advisor synthesis** | EXTREME | High | IMMEDIATE | The core differentiator is broken. "Temporarily unavailable" destroys all trust. Either fix it or remove it - broken features worse than no features. |
| **Improve Advisor query understanding** | EXTREME | Medium | IMMEDIATE | Must distinguish "explain CLIP" from "what came before CLIP". Needs to understand I'm a beginner asking for foundations, not advanced analysis. |
| **Implement TL;DR discovery view** | HIGH | Medium | IMMEDIATE | All discovery features 404. At minimum get ONE working for quick paper scanning. |

### P1 - CRITICAL (Necessary for Acceptable Experience):

| Improvement | Impact | Effort | Sarah's Rationale |
|------------|--------|--------|-------------------|
| **Add "Start Here" topic guidance** | HIGH | Medium | Every topic needs a "New to X? Read these 3 papers first" entry point. Hand-hold newcomers. |
| **Implement technique explorer** | HIGH | Medium | Help me understand the methodological landscape. What techniques exist? How do they relate? |
| **Add paper importance indicators** | HIGH | Medium | MUST know what's foundational vs. incremental. Show citation counts, awards, influence scores. |
| **Fix "Invalid Date" bug** | MEDIUM | Low | Professional credibility issue. Makes tool look broken and untrustworthy. EASY FIX. |
| **Show difficulty levels on papers** | MEDIUM | Low | You have difficulty filters - USE THEM. Tag papers as beginner/advanced so I know what I can handle. |

### P2 - HIGH VALUE (Significantly Improves Usefulness):

| Improvement | Impact | Effort | Sarah's Rationale |
|------------|--------|--------|-------------------|
| **Implement rising papers feature** | HIGH | Medium | FOMO is real. Need to know what's gaining traction so I don't miss important developments. |
| **Add "Why is this relevant?" explanations** | HIGH | Medium | When AI surfaces a paper, explain WHY it matched my query in plain language I can understand. |
| **Show technique extraction from papers** | MEDIUM | Medium | Help me understand WHAT each paper contributes without reading the whole thing first. |
| **Improve Related Papers performance** | MEDIUM | Medium | Feature started loading but never finished. Either make it fast or show partial results progressively. |
| **Add paper-to-paper connections** | MEDIUM | High | Show citation graphs, build visual map of influence. Help me see relationships. |

### P3 - NICE TO HAVE (Future Enhancements):

| Improvement | Impact | Effort | Sarah's Rationale |
|------------|--------|--------|-------------------|
| **Reading list management** | LOW | Medium | Let me save papers to "must read," "completed," "not relevant" lists to track progress. |
| **Completion tracking/progress badges** | LOW | Medium | "You've covered 60% of foundational VLM papers!" would boost confidence. |
| **Collaborative features** | LOW | High | Share reading lists with labmates, see what my cohort is reading. |
| **Personalized recommendations** | LOW | High | Learn from what I've read, suggest logical next papers based on my journey. |

---

## Screenshots Index with Context

### Landing & Search:
1. **01-landing-first-impression.png** - Initial welcoming interface, shows empathetic "Not sure where to start?" message
2. **02a-nav-generate-attempt.png** - Code generation feature page (interesting but not my current need)
3. **03-search-and-advisor-panel.png** - Search results with Research Advisor auto-opened, AI-POWERED badge visible

### Research Advisor Failure:
4. **03b-research-advisor-response.png** - Shows "temporarily unavailable" error and wrong paper recommendations for beginner question

### Paper Detail:
5. **04-paper-detail.png** - Expanded paper view with abstract, tabs, action buttons - basic but functional

### Discovery Feature Failures (ALL 404):
6. **06-learning-path.png** - 404 error for THE most critical newcomer feature
7. **07-tldr-404.png** - 404 error for quick scanning view
8. **08-techniques-404.png** - 404 error for technique taxonomy
9. **09-rising-404.png** - 404 error for trending papers

### Final State:
10. **12-final-state.png** - Back on explore page after discovering all advanced features are broken

---

## Would I Use This? Would I Recommend It?

### Would I bookmark this tool?
**NO.** Too many broken features. No clear value over Google Scholar + arXiv for someone at my level.

### Would I return tomorrow?
**NO.** The features I desperately need (learning paths, beginner guidance, historical context) either don't exist or are broken. Why would I come back?

### Would I recommend to other first-year PhD students?
**ABSOLUTELY NOT.** I would actively WARN them:
- "The discovery features are all broken (404s)"
- "The Research Advisor doesn't understand beginner questions"
- "It's designed for people who already know what they're looking for"
- "Don't waste your time - just ask your advisor for a reading list instead"

### Would I recommend to senior researchers?
**MAYBE, with caveats:**
- If they already know what papers they want and just need fast semantic search
- If they don't need learning paths or beginner guidance
- If they're okay with a tool that feels incomplete

### Would this help me prepare for qualifying exams?
**NO.** Absolutely not. Qualifying exams require:
- Systematic coverage of foundational work (tool can't provide)
- Historical understanding of field evolution (tool can't explain)
- Broad knowledge across subfields (no learning paths to guide)
- Confidence I've covered essential material (no validation/tracking)

I would use traditional methods instead: advisor guidance, survey papers, citation chains, and manual curation.

### What would make me return and recommend it?

**Three Critical Changes:**

1. **Working learning paths** - "New to vision-language models? Follow this 10-paper sequence from basics to state-of-the-art"

2. **Reliable Research Advisor** - Actually understand when I'm a beginner asking for foundations vs. an expert asking for cutting-edge. Provide contextual guidance, not just paper lists.

3. **Impact indicators everywhere** - Show me what's foundational (10K+ citations, seminal work), what's influential (award-winning, widely cited), what's recent (hot new directions).

**With those three changes**, this could transform from "just another search engine" to "the learning companion I desperately need."

**Without them**, it's unusable for first-year PhD students trying to build foundational knowledge.

---

## Final Verdict: 3.5/10

### Rating Breakdown:
- **Interface/Design:** 8/10 (Clean, professional, welcoming)
- **Search Functionality:** 7/10 (Fast, semantic, relevant results)
- **Research Advisor:** 2/10 (Broken synthesis, wrong recommendations)
- **Discovery Features:** 0/10 (All return 404 errors)
- **Beginner Support:** 1/10 (Exists in theory, missing in practice)
- **Reliability/Trust:** 2/10 (Too many broken features)
- **Value for Newcomers:** 2/10 (Doesn't solve core problems)

### The Honest Truth:

I came to AI Paper Atlas hoping for a **learning companion** that would help me build systematic knowledge and reduce my overwhelming anxiety about being behind.

What I found was a **broken search engine** that:
- Works for basic queries (barely)
- Fails at everything designed to help newcomers
- Makes promises it can't keep ("temporarily unavailable")
- Assumes I already know what I'm looking for

**For a first-year PhD student**, this tool is worse than useless - it's **actively harmful** because:
1. It wastes time on broken features
2. It increases anxiety by highlighting what I don't know
3. It provides no scaffolding for learning
4. It damages trust with unreliability

### My Emotional State Now vs. Before:

**Before:** Anxious but hopeful (3/5)
**After:** More anxious and discouraged (1/5)

The tool made me feel **more behind** rather than helping me catch up.

### What I'll Do Instead:

1. **Ask my advisor** for a curated reading list (what I should have done first)
2. **Find survey papers** on Google Scholar to get field overviews
3. **Follow citation trails** from foundational papers manually
4. **Ask labmates** what they read as first-years
5. **Use Connected Papers** to visualize relationships when I find a good seed paper

### Bottom Line:

**This tool is not ready for first-year PhD students.** It's an alpha-stage product with basic search and a lot of broken promises. I would not waste my time with it again until I hear that:
- Learning paths are implemented and working
- Research Advisor can handle beginner questions
- Discovery features are functional (not 404)
- Someone I trust confirms it's actually helpful for learning

Until then, I'll stick to asking humans for guidance. At least they understand when I'm a beginner.

---

**Assessment completed by:** Sarah Kim (persona embodiment)
**Actual user type:** First-year PhD student, Stanford Vision Lab
**Research interest:** Vision-language models (still exploring foundations)
**Emotional journey:** Hopeful → Disappointed → Devastated
**Key learning:** Broken beginner features are worse than no features
**Recommendation:** Do NOT use until discovery features are implemented
**Browser:** Chrome DevTools MCP (instance chrome-3)
**Assessment methodology:** 13-step structured UX protocol
**Date:** December 16, 2025, 15:39-16:08 PST
