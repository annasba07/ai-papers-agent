# UX Assessment Report: Sarah Kim - First-Year PhD Student
## LIVE SESSION - December 15, 2025

**Persona:** Sarah Kim
**Role:** 1st-year PhD student, Stanford Vision Lab
**Research Focus:** Vision-language models (exploratory phase)
**Date:** December 15, 2025
**Assessment Type:** Live interactive UX testing
**Assessment Duration:** ~20 minutes

---

## Executive Summary

**Overall Rating: 2/10**

As a first-year PhD student feeling overwhelmed and uncertain about where to start with vision-language models, this experience was unfortunately more frustrating than helpful. The platform appears well-designed with features I desperately need (Research Advisor, difficulty filters, beginner-friendly content), but **nothing actually works because there are no papers in the database**. This left me feeling even more lost than when I started.

---

## Critical Finding: Empty Database

The fundamental issue that broke the entire experience:

- **0 papers indexed** in the database
- All backend API calls to `localhost:8000` return 404 errors
- Search endpoints return empty results: `{"semanticResults":[],"keywordResults":[],"totalSemantic":0,"totalKeyword":0}`
- Without data, even the best-designed UI is completely useless

---

## Detailed Experience

### Initial Impressions (Landing Page)

**What I saw:**
- Clean, modern interface that looked professional
- Clear navigation with "Explore" and "Generate" sections
- A prominent search box asking me to "Describe what you're researching"
- Helpful filters on the left including a "Beginner" difficulty option (exactly what I need!)
- Trending topics listed (LLM Agents, Mixture of Experts, RLHF, Diffusion, RAG)
- **"0 papers" displayed prominently** - this immediately made me worried

**Errors visible:**
- "Failed to fetch papers: 404" error message
- "No trending data available"

**How it made me feel:**
- Initially hopeful - the UI looked like it was designed for someone like me
- The "Beginner" filter suggested this platform understands that not everyone is an expert
- Confused by "0 papers indexed" - is this a demo? Is it broken?
- The technical error message "Failed to fetch papers: 404" was confusing and made me feel like maybe I did something wrong

### Attempting to Search

**What I tried:**
1. Typed "vision language models for beginners" in the search box
2. Clicked "Ask Advisor" button
3. Applied "Computer Vision" category filter (cs.CV)
4. Applied "Beginner" difficulty filter

**What happened:**
- Search showed "0 results (15ms)" - very fast but unhelpful
- The filters worked visually (I could see "cs.CV" and "beginner" tags applied)
- But still no papers showed up
- Message: "No papers found. Try different keywords or describe your research goal in more detail."

**How it made me feel:**
- **Frustrated** - maybe I'm using the wrong keywords? (classic imposter syndrome kicking in)
- **Confused** - if there are 0 papers total, why suggest I try different keywords?
- **More overwhelmed than before** - I can't even get a tool designed to help me to work
- **Self-doubt** - am I doing something wrong? Am I not technical enough to use this?

### Research Advisor Feature

**What I tried:**
- Clicked the "Ask Research Advisor" button
- Dialog opened with friendly greeting: "Hi! I'm your Research Advisor. Describe what you're working on or what problem you're trying to solve, and I'll help you find relevant papers and techniques."
- Saw helpful example buttons like "State-of-the-art in multimodal learning" (exactly my area!)
- I typed: "I'm a first year PhD student and I need to understand vision-language models. Where should I start? What are the foundational papers I should read first?"
- Clicked submit

**What happened:**
- Got an error: **"Sorry, I encountered an error while searching. Please try again."**
- No helpful guidance
- No paper recommendations
- No context about the field
- The dialog was also difficult to close (timeout error when clicking close button, had to use Escape key)

**How it made me feel:**
- **Defeated** - this was supposed to be my safety net as a confused newcomer
- **Even more anxious** about my lack of knowledge
- Like I broke something (even though I didn't)
- **Excluded** by technical error messages (what's a 404? What does "timeout" mean?)
- **Alone** - the one tool that promised to guide me also failed

### Generate Page (Multi-Agent Code Generation)

**What I tried:**
- Navigated to the "Generate" page
- Saw the multi-agent code generation feature explained
- Searched for "CLIP" (one of the foundational vision-language papers my advisor mentioned)

**What happened:**
- The page explained a cool concept: 5-agent system to turn papers into code (Paper Analyzer → Test Designer → Code Generator → Test Executor → Debugger)
- But when I searched for "CLIP", nothing happened
- No results, no feedback, just silence
- Network request showed: `GET http://localhost:8000/api/v1/atlas-db/papers?query=CLIP&limit=10 [failed - 404]`

**How it made me feel:**
- **Intrigued** by the concept (turning papers into code sounds amazing!)
- But **disappointed** it doesn't work
- This could have been a game-changer for understanding paper implementations
- **Frustrated** by another dead end

### Trending Topics

**What I observed:**
- Listed topics in sidebar: LLM Agents, Mixture of Experts, RLHF, Diffusion, RAG
- Main trending section showed: "No trending data available"

**How it made me feel:**
- These topics sound important but I don't know what most of them mean
- Would have been helpful if I could click them and see papers/explanations
- Another feature that looks promising but delivers nothing

---

## What Would Have Helped Me

### As a Confused Newcomer:

1. **Contextual Explanations**
   - I need to understand WHY papers are important, not just titles
   - What problem did CLIP solve? Why should I care about attention mechanisms?
   - How do different papers relate to each other?

2. **Learning Pathways**
   - "Start here if you're new to vision-language models"
   - A curated sequence: "Read paper A to understand concept X, then paper B builds on it"
   - Visual roadmap showing how the field evolved

3. **Beginner-Friendly Content**
   - The "Beginner" filter is exactly what I need! (But it needs papers to filter)
   - Papers with clearer explanations
   - Maybe summaries written for people without deep expertise
   - Glossary for terms I don't understand

4. **Confidence Building**
   - Understanding which papers are "must-reads" vs. "nice to know"
   - Knowing I'm not expected to understand everything at once
   - Seeing what concepts I should learn before diving into complex papers
   - Feeling less alone in my confusion

5. **Lab Meeting Prep**
   - Quick summaries I can reference
   - Key contributions of each paper
   - What questions to ask when discussing papers
   - Understanding the intellectual lineage

---

## Technical Issues Discovered

### Critical: Empty Database
- **0 papers indexed** - this is the root cause of all problems
- Database appears to be completely empty
- Without data, the entire platform is non-functional

### Backend API Failures
All API calls to `localhost:8000` are failing with 404 errors:

| Endpoint | Status | Impact |
|----------|--------|--------|
| `/api/v1/trends/summary` | 404 | Trending topics don't work |
| `/api/v1/atlas-db/papers` | 404 | Paper browsing broken |
| `/api/v1/papers/contextual-search` | 404 | Research Advisor fails |
| `/api/v1/atlas-db/papers?query=CLIP` | 404 | Generate page search fails |

### Frontend API (Working but Empty)
Search endpoints at `localhost:3000` return 200 OK but with empty results:
- `/api/search/hybrid?query=vision+language+models+for+beginners` → `{"semanticResults":[],"keywordResults":[]}`
- This suggests the Next.js API routes are working, but have no data to return

### UI/UX Issues
1. **Error messages are too technical**
   - "Failed to fetch papers: 404" is developer speak, not user-friendly
   - Users don't know what a 404 means
   - Should say: "Unable to load papers. Please try again later."

2. **No indication this is a development/demo version**
   - Should have a banner: "Demo version - data is being loaded"
   - Or: "Development environment - limited functionality"

3. **Misleading UI when empty**
   - Showing filters and trending topics when there's no data creates false expectations
   - Better to show an onboarding/setup state

4. **Dialog close button timeout**
   - Research Advisor dialog close button times out on click
   - Had to use Escape key to close
   - Indicates a JavaScript event handling issue

5. **Unhelpful "No papers found" message**
   - When database is empty, says "Try different keywords"
   - This is misleading - the problem isn't my keywords, it's the empty database

---

## What Works Well (In Theory)

### Thoughtful Design for Newcomers

1. **Difficulty Filters**
   - Shows someone thought about users at different experience levels
   - "Beginner", "Intermediate", "Advanced", "Expert" options
   - This directly addresses my anxiety about being overwhelmed

2. **Research Advisor Concept**
   - Natural language interface: "Describe what you're researching"
   - Exactly what I need as someone who doesn't know where to start
   - Example prompts are helpful and relevant
   - Modal design keeps context

3. **Category Filters**
   - Familiar arXiv categories (cs.CV, cs.LG, etc.)
   - Helps narrow down the overwhelming amount of content
   - Visual chips make active filters clear

4. **Clean, Approachable UI**
   - Not intimidating or overly academic
   - Clear hierarchy and layout
   - Professional design builds trust
   - Good use of whitespace

### Innovative Features

1. **Multi-Agent Code Generation**
   - Turning papers into working code could be huge for understanding
   - Test-driven approach (design tests first) is pedagogically sound
   - 5-agent pipeline seems well thought out
   - Would help me move from theory to implementation

2. **Trending Topics**
   - Helps me know what's hot in the field right now
   - Could prevent me from studying obsolete approaches
   - Relevant for staying current

3. **Contextual Search**
   - Searching by describing my problem, not just keywords
   - This is how beginners naturally think about research
   - More intuitive than boolean search operators

4. **"Has Code" Filter**
   - Critical for reproducibility and learning
   - Saves time by showing only papers with implementations
   - Addresses a real pain point for PhD students

---

## Emotional Journey

My experience as Sarah, minute by minute:

**Minute 0-2: Initial Hope**
- "This looks like it might help me!"
- Clean interface, promising features
- Maybe this will make me feel less overwhelmed

**Minute 2-5: Confusion Sets In**
- "Why are there 0 papers? Is this broken?"
- "Did I navigate to the wrong page?"
- "Is this even a real tool?"

**Minute 5-10: Frustration Building**
- "Nothing I try works..."
- "Maybe I'm typing the wrong thing?"
- "I don't understand these error messages"

**Minute 10-15: Self-Doubt**
- "Am I doing something wrong?"
- "Maybe I'm not technical enough to use this?"
- "Everyone else probably knows how to use this..."

**Minute 15-18: Disappointment**
- "Even the 'Research Advisor' can't help me"
- "This was supposed to be my guide"
- "I feel more lost than before"

**Minute 18-20: Defeat**
- "I'm still completely lost about vision-language models"
- "AND I've wasted 20 minutes"
- "Back to Google Scholar I guess..."

**Overall Arc:** Hope → Confusion → Frustration → Self-Doubt → Disappointment → Defeat

This emotional journey mirrors my general PhD experience: excited about a promising tool or approach, but it doesn't deliver, leaving me feeling inadequate and alone.

---

## Would I Use This Regularly?

### Current State: Absolutely Not (0% chance)

Right now, I **cannot** use it at all because there's literally no data. Even if I wanted to persist through the frustration, there's nothing to work with.

### If It Were Working: Potentially Yes (65% chance)

If the database had papers and the features actually worked, I would probably try it regularly because:

**Reasons I'd Use It:**
- The "Beginner" filter directly addresses my anxiety
- Research Advisor concept is exactly what I need for guidance
- Multi-agent code generation could help me understand implementations
- Better than browsing arXiv blindly
- Category filters help narrow scope

**Reasons I'd Hesitate:**
- Would need to see that it actually reduces my overwhelm, not increases it
- Would need the "Beginner" content to truly be beginner-friendly, not just marketing
- Would need proof that the Research Advisor gives good guidance, not generic responses
- Would need it to help me build mental models, not just find papers
- Would need to trust the data quality and currency

**What would make it indispensable:**
- Historical context and learning pathways ("Read these 5 papers in this order")
- Visual maps showing how papers relate and build on each other
- Confidence that I'm not missing foundational knowledge
- Community features (what are other first-years reading?)
- Progress tracking (what have I read, what do I understand)

---

## Recommendations for Improvement

### Immediate (Blockers - Must Fix to Be Usable)

1. **INDEX PAPERS INTO THE DATABASE** - Priority: P0
   - This is the #1 blocker
   - Without papers, nothing else matters
   - Suggests backend services aren't running or configured
   - Action: Investigate why `localhost:8000` returns 404s

2. **Fix Backend API Server** - Priority: P0
   - Get `localhost:8000` server running and responding
   - Fix all 404 endpoints
   - Ensure database connection is working
   - Action: Check service status, database migrations, configuration

3. **Improve Error Messaging** - Priority: P0
   - Replace "Failed to fetch papers: 404" with user-friendly messages
   - "We're having trouble loading papers. Please try again later."
   - Don't show technical error codes to users
   - Add a "Report Problem" button for users to give feedback

4. **Add Development Mode Banner** - Priority: P0
   - If this is a development/demo environment, make that clear
   - Banner: "Demo version - paper database is being populated"
   - Set user expectations appropriately
   - Prevents frustration from broken features

5. **Fix Dialog Close Button Timeout** - Priority: P1
   - Research Advisor modal doesn't close on button click
   - Investigate JavaScript event handling
   - Ensure all interactive elements are responsive

### Short-term (For Newcomers Like Me)

6. **Create Onboarding Flow** - Priority: P1
   - Guide first-time users through the platform
   - Explain key features (Research Advisor, filters, code generation)
   - Set expectations about what the tool can and can't do
   - Help users like me feel less lost

7. **Add Example Searches** - Priority: P1
   - Show what successful searches look like
   - "Try searching: 'attention mechanisms for transformers'"
   - Give me confidence I'm using it correctly

8. **Build Curated Collections** - Priority: P1
   - "Essential papers for vision-language models"
   - "Getting started with multimodal learning"
   - "Foundational papers in computer vision"
   - Help me know where to start

9. **Create Glossary/Explainer** - Priority: P2
   - Explain terms like "multimodal learning", "contrastive learning", "zero-shot"
   - Linked from papers or search results
   - Reduces my anxiety about not knowing terminology

10. **Add "Survey Papers" Filter** - Priority: P1
    - Survey papers are gold for newcomers
    - Give me overview and context
    - Should be a prominent quick filter

### Long-term (Dream Features)

11. **Learning Pathways Generator** - Priority: High
    - Structured curriculum for different topics
    - "To understand vision-language models: Start with these 3 papers, then..."
    - Visual progress tracking
    - Adaptive based on my current knowledge

12. **Paper Relationship Visualization** - Priority: High
    - Graph showing how papers cite and build on each other
    - See intellectual lineage and key branching points
    - Helps me build mental map of the field
    - Interactive exploration

13. **Community Features** - Priority: Medium
    - See what other first-year students are reading
    - Reading groups or study cohorts
    - Discussion threads on papers
    - Reduces feeling of isolation

14. **Progress Tracking** - Priority: Medium
    - Track what I've read and understood
    - Mark papers as "to read", "reading", "read", "understood"
    - Notes and highlights
    - Review system for myself

15. **Lab Meeting Mode** - Priority: Low
    - Quick summaries optimized for presenting
    - Key contributions, methods, results
    - Questions to ask about the paper
    - Help me participate confidently in discussions

---

## Comparison to Alternatives

### vs. Google Scholar
- **Scholar wins:** Actually has papers, works reliably
- **Atlas could win:** Better filters, contextual search, code generation
- **Current state:** Scholar wins by default (Atlas is broken)

### vs. arXiv Browse
- **arXiv wins:** Comprehensive, reliable, fast
- **Atlas could win:** Better discovery, difficulty filters, learning paths
- **Current state:** arXiv wins (Atlas has no papers)

### vs. Papers with Code
- **PWC wins:** Code availability, benchmarks, task organization
- **Atlas could win:** Research Advisor, multi-agent code gen, broader scope
- **Current state:** PWC wins (Atlas non-functional)

### vs. Semantic Scholar
- **Semantic wins:** Paper recommendations, citation graphs, reliability
- **Atlas could win:** Beginner focus, learning paths, contextual search
- **Current state:** Semantic wins (Atlas empty)

**Verdict:** Currently, every alternative is better because they actually work. Atlas has promising ideas but zero execution.

---

## Screenshots Captured

1. `sarah-01-landing.png` - Landing page showing 0 papers error
2. `sarah-02-advisor-dialog.png` - Research Advisor dialog interface
3. `sarah-03-advisor-error.png` - Error message after submitting question
4. `sarah-04-filters.png` - Computer Vision and Beginner filters applied (0 results)
5. `sarah-05-generate.png` - Multi-agent code generation page
6. `sarah-06-final.png` - Final state after exploration

---

## Network Analysis

Examined network requests to understand failures:

**Failed Requests (Backend - localhost:8000):**
- `GET /api/v1/trends/summary` → 404
- `GET /api/v1/atlas-db/papers?limit=30&offset=0&order_by=published_date&order_dir=desc` → 404
- `POST /api/v1/papers/contextual-search` → 404
- `GET /api/v1/atlas-db/papers?query=CLIP&limit=10` → 404

**Successful Requests (Frontend - localhost:3000):**
- `GET /api/search/hybrid?query=...` → 200 OK (but empty results)
  - Response: `{"semanticResults":[],"keywordResults":[],"totalSemantic":0,"totalKeyword":0}`

**Analysis:**
- Backend services are either not running or misconfigured
- Frontend API routes work but have no data source
- Suggests the vector database or paper index is empty/unavailable

---

## Final Thoughts

This platform has **tremendous potential** to help someone like me. The features listed - Research Advisor, difficulty filters, code generation, learning pathways - are precisely what I desperately need as I navigate my overwhelming first year.

But potential doesn't help me right now.

### The Worst Part

The worst part isn't that it's broken. The worst part is that it **gave me hope and then let me down**.

I came here feeling:
- Overwhelmed about vision-language models
- Anxious about lab meetings
- Unsure where to start
- Desperate for guidance

I left feeling:
- Still overwhelmed about vision-language models
- Still anxious about lab meetings
- Still unsure where to start
- Still desperate for guidance
- **PLUS frustrated that another tool failed me**

### What This Experience Taught Me

This mirrors a common PhD experience: discovering a tool or resource that promises to solve your problems, only to find it doesn't work or doesn't deliver. Each disappointment adds to imposter syndrome ("maybe I'm not smart enough to figure this out") and isolation ("everyone else seems to have this figured out").

### If This Were Working...

If this platform had papers and the features worked as designed, I genuinely believe it could become indispensable for first-year PhD students. The design demonstrates real understanding of what newcomers struggle with:

- **Overwhelm**: Addressed by filters and difficulty levels
- **Lack of context**: Addressed by Research Advisor and learning paths
- **Practical needs**: Addressed by code generation and implementation focus
- **Confidence**: Addressed by beginner-friendly framing

But design without execution is just mockups.

### My Advice to the Developers

1. **Get papers in the database ASAP** - This is table stakes
2. **Test with actual first-year students** - We'll tell you honestly what helps
3. **Make error messages less scary** - "404" intimidates newcomers
4. **Show development status clearly** - Don't pretend it's production-ready if it's not
5. **Focus on the learning path feature** - This is your killer differentiator
6. **Build for the struggling student** - Not the confident expert

### Would I Try Again?

If someone told me in 3 months "Paper Atlas now has 100,000 papers indexed and the Research Advisor works," I would absolutely give it another chance. The concept is too compelling to ignore.

But I'd approach it with skepticism, not hope. You only get to disappoint users once.

---

**Rating Breakdown:**

- **Functionality:** 1/10 (Nothing works, database empty)
- **Design/UI:** 8/10 (Clean, thoughtful, well-organized)
- **Newcomer Friendliness:** 2/10 (Good concepts, zero execution)
- **Potential if Working:** 8/10 (Could be transformative)
- **Current Usefulness:** 0/10 (Cannot use at all)

**Overall Rating: 2/10**

The 2 points are for the thoughtful UI design and promising feature concepts. Everything else fails due to the empty database.

---

*Assessment conducted as part of AI Paper Atlas UX evaluation*
*Persona: Sarah Kim, Stanford Vision Lab, 1st-year PhD student*
*Method: Live interactive testing with Chrome DevTools MCP*
*Date: December 15, 2025*
