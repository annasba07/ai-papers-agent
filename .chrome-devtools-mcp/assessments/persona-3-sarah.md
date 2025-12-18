# UX Assessment Report - Sarah Kim (LIVE SESSION - December 16, 2025)

**Date**: December 16, 2025
**Persona**: Sarah Kim, 1st-year PhD student at Stanford Vision Lab
**Session Duration**: ~30 minutes
**Screenshot Directory**: `.chrome-devtools-mcp/assessments/screenshots/`
**Assessment Mode**: Live browser interaction via Chrome DevTools MCP

---

## Executive Summary

As a first-year PhD student trying to build my mental map of vision-language models, I just spent 30 minutes exploring AI Paper Atlas. I'm still feeling overwhelmed, honestly. The interface is clean and the search works, but I'm left with the same question I started with: **"Where do I even begin?"** I found papers, sure, but I don't know if they're the *right* papers or if I'm missing something fundamental that everyone else already knows.

**Overall Rating**: 6.5/10

**One-Line Verdict**: "It helps me find papers, but it doesn't help me learn the field."

---

## Session Overview

| Metric | Value |
|--------|-------|
| Session Duration | ~30 minutes |
| Searches Performed | 1 ("vision language models") |
| Papers Explored | 6 results |
| Research Advisor Queries | 1 |
| Features Tested | Search, Research Advisor, Paper Detail, Trending |
| Task Success Rate | 60% (felt incomplete) |

---

## What I Actually Did (Step by Step)

### Step 1: Landing on the Explore Page

**First Impression**: The page loaded with 30 papers showing - all recent Computer Vision stuff. I immediately thought, "Okay, but I'm interested in vision-language models, not random CV papers." At least there's a search box prominently at the top, and I can see filters on the left sidebar.

**Emotional State**: Slightly anxious (3/5). The interface looks professional, which is reassuring, but I don't know where to start.

**Screenshot**: `sarah-01-landing.png`

**What Worked**:
- Clean, modern interface doesn't feel intimidating
- Search box is obvious and inviting
- "Ask Advisor" button suggests I can get help

**What Confused Me**:
- Why am I seeing these specific papers? Are they popular? Recent? Relevant to me somehow?
- The trending topics on the sidebar (LLM Agents, Mixture of Experts, RLHF) - are those clickable?

### Step 2: Searching for "vision language models"

**What I Did**: Typed "vision language models" in the search box and clicked "Ask Advisor"

**What Happened**: The page said "Searching..." and then showed me 6 results in about 8 seconds. The papers all seemed relevant:
- AdaptVision: Efficient Vision-Language Models via Adaptive Visual Acquisition
- Vision Language Models are Confused Tourists
- Generalizing Vision-Language Models with Dedicated Prompt Guidance
- VisPlay: Self-Evolving Vision-Language Models from Images
- FineGRAIN: Evaluating Failure Modes...
- 10 Open Challenges Steering the Future of Vision-Language-Action Models

**Emotional State**: Mixed (2.5/5). On one hand, the papers look relevant. On the other hand... only 6? And they all say "Invalid Date" which makes me nervous about data quality.

**Screenshot**: `sarah-02-search.png`

**What Worked**:
- Results were actually about VLMs, not just generic keyword matches
- The AI-powered search badge made me feel like it was doing something smart
- TL;DR summaries helped me quickly scan what each paper was about

**What Didn't Work**:
- Only 6 results? Where are the foundational papers like CLIP?
- "Invalid Date" for every paper - is this broken?
- These all seem like very recent, specific papers (adaptive tokens, fine-tuning, evaluation). Where's the history?
- I don't know if these are the "important" papers or just papers that happen to mention VLMs

**My Biggest Question**: "Are these the papers my advisor expects me to know, or am I looking at the wrong level of work?"

### Step 3: Trying the Research Advisor

**What I Asked**: "I'm new to vision-language models. Can you help me understand how they evolved and which papers are must-reads for understanding the field?"

**What I Got**: The advisor panel opened and processed my question. It responded with:
- "Contextual synthesis temporarily unavailable" (ugh, that's disappointing)
- A list of 5 papers with titles like "Towards Understanding How Knowledge Evolves in Large Vision-Language Models"
- Suggested follow-up questions: "How do these methods scale to larger models?", "What are the training costs involved?", "Find papers that cite these works"

**Emotional State**: Disappointed (3/5). I asked for help understanding how the field evolved, but it just gave me more papers without the context I desperately need.

**Screenshot**: `sarah-03-advisor.png`

**What Worked**:
- The natural language query interface felt approachable
- The suggested follow-up questions showed me what kinds of questions I *should* be asking
- Papers appeared with direct links

**What Didn't Work**:
- "Contextual synthesis temporarily unavailable" made me feel like the feature is broken
- It didn't answer my actual question about evolution or must-reads
- No explanation of *why* these papers matter or *how* they connect
- As a newcomer, I need someone to say "Start here, then read this, then this" - not just "here are 5 papers, figure it out"

**What I Really Wanted**: A mentor-like response that says something like: "Vision-language models started with early work on image captioning, then CLIP revolutionized the field by showing you could learn from image-text pairs. Here are the 3 foundational papers, then here are 3 important extensions, and here's where recent work is heading."

### Step 4: Expanding a Paper for Details

**What I Did**: Clicked "Expand" on the "AdaptVision" paper

**What Happened**: The paper expanded inline to show:
- The full abstract (which was actually helpful for understanding what it's about)
- Tabs for "Summary", "Related Papers", and "Benchmarks"
- Buttons for "Read on arXiv" and "Generate Code"

**Emotional State**: More confident (4/5). At least now I can understand what this individual paper is trying to do - it's about making VLMs more efficient by adaptively acquiring visual tokens.

**Screenshot**: `sarah-04-paper.png`

**What Worked**:
- Inline expansion is smooth - no page reload
- The full abstract helped me understand the contribution
- "Generate Code" button is intriguing (though I didn't try it)
- Tabs suggest there's more depth available

**What I Wished For**:
- Some indication of impact - is this a seminal paper or just a recent incremental improvement?
- Citation count or metrics to help me gauge importance
- Difficulty level - can I actually understand this as a first-year?
- A visual showing papers this builds on and papers that cite it

### Step 5: Checking Trending Topics

**What I Did**: Scrolled down to the "Trending Now" section and clicked on "Hot Topics"

**What Happened**: The section just says "No trending data available"

**Emotional State**: Let down (2.5/5). This seemed like it could be really useful for understanding what's hot in the field, but it's not working.

**Screenshot**: `sarah-05-trending.png`

**What Didn't Work**:
- The feature appears to be non-functional or empty
- The sidebar trending topics (LLM Agents, Mixture of Experts, RLHF, Diffusion, RAG) aren't clickable
- Missed opportunity to help me understand where the field is heading

**What I Wanted**: Clickable trending topics that would show me related papers and help me understand emerging areas

---

## Did This Help Me With My Core Problems?

### Problem 1: Overwhelmed by Paper Volume ❌ NOT SOLVED

**Before**: Too many papers, don't know where to start
**After**: Still too many papers, still don't know where to start
**Why**: The tool reduced 30 papers to 6 papers, but I still don't know if these 6 are the *right* 6. Am I missing CLIP? Am I missing foundational work? The reduction in volume didn't come with confidence.

### Problem 2: Lack of Historical Context ❌ NOT SOLVED

**Before**: Don't understand how VLMs evolved
**After**: Still don't understand the evolution
**Why**: The Research Advisor didn't provide the historical narrative I asked for. I saw recent papers but no indication of how we got here or what came before.

### Problem 3: Building a Mental Map ❌ NOT SOLVED

**Before**: No clear picture of the field's structure
**After**: Still no mental map
**Why**: I found individual papers but no visualization of how they connect, no indication of foundational vs derivative work, no learning path from basics to advanced.

### Problem 4: Lab Meeting Anxiety ❌ NOT SOLVED

**Before**: Worried about looking clueless in lab meetings
**After**: Still worried - I don't know if I'm looking at the right papers
**Why**: No validation that these are the papers people in my lab are discussing. No indication of what's "core knowledge" vs niche.

### Problem 5: Finding Relevant Papers ✅ PARTIALLY SOLVED

**Before**: Hard to find VLM-specific papers
**After**: Found 6 relevant papers quickly
**Why**: The search actually worked and gave me semantically relevant results

---

## Emotional Journey

```
Time:      0min   5min   10min  15min  20min  25min  30min
Feeling:   [3] → [2.5] → [3] → [4] → [2.5] → [3] → [3]
           Land→ Search→ Advisor→ Paper→ Trend→ Reflect
```

**Start**: Anxious but hopeful - "Maybe this will help me get oriented"
**Middle (Lowest)**: Disappointed when Research Advisor didn't provide context - "It's just another search tool"
**Middle (Highest)**: Confident when reading the expanded paper - "At least I understand what *this* paper is doing"
**End**: Resigned - "This helps me find papers, but I'm still lost about the field"

---

## What Delighted Me

1. **Inline Paper Expansion**: Being able to read the full abstract without opening a new tab felt smooth. No context switching.

2. **Semantic Search**: The results were actually about vision-language models, not just keyword matches. It felt smarter than Google Scholar.

3. **Research Advisor Concept**: Even though it didn't work perfectly, the idea of being able to ask questions in natural language is exactly what I need. If this actually worked as promised, it would be transformative.

---

## What Frustrated Me

### 1. "Invalid Date" Everywhere - Severity: MEDIUM
- **What**: Every paper shows "Invalid Date"
- **Impact**: Makes me question the data quality. Are these even real papers?
- **Emotional Impact**: Nervous, unconfident in the platform

### 2. Research Advisor "Temporarily Unavailable" - Severity: HIGH
- **What**: The synthesis feature I need most isn't working
- **Impact**: I asked for context and evolution, got a paper list instead
- **Emotional Impact**: Disappointed, let down
- **What I Expected**: A narrative explaining how the field evolved

### 3. No Learning Path or Beginner Guidance - Severity: HIGH
- **What**: No "start here" for newcomers
- **Impact**: Still don't know what I don't know
- **Emotional Impact**: Anxious, overwhelmed
- **What I Need**: "Here are the 5 foundational papers every VLM researcher should know"

### 4. Only 6 Results, No Explanation - Severity: MEDIUM
- **What**: Search returned just 6 papers with no explanation why
- **Impact**: Don't know if these are comprehensive or if I'm missing important work
- **Emotional Impact**: Confused
- **What I Need**: "Showing the 6 most influential papers on VLMs" or "Showing recent work from top conferences"

### 5. Trending Topics Don't Work - Severity: LOW
- **What**: "No trending data available"
- **Impact**: Can't see what's hot right now
- **Emotional Impact**: Minor letdown

---

## What's Missing (That I Really Need)

### Critical Missing Features:

1. **Learning Paths** - Priority: CRITICAL
   - **What**: Curated progression from foundational to advanced papers
   - **Why I Need It**: I need to build knowledge systematically, not randomly
   - **Example**: "VLM Primer: Start with Image Captioning → CLIP → ALIGN → Flamingo → GPT-4V"

2. **Paper Importance Indicators** - Priority: CRITICAL
   - **What**: Citation counts, awards, "foundational paper" badges
   - **Why I Need It**: Help me distinguish seminal work from incremental improvements
   - **Example**: Show me "CLIP" has 10,000+ citations and changed the field

3. **Historical Timeline / Evolution View** - Priority: HIGH
   - **What**: Visualization of how the field developed over time
   - **Why I Need It**: Answers my core question: "How did we get here?"
   - **Example**: Timeline showing pre-CLIP → CLIP era → post-CLIP developments

4. **Difficulty Ratings** - Priority: HIGH
   - **What**: Labels like "Beginner-friendly", "Requires advanced knowledge"
   - **Why I Need It**: Help me know what I can actually understand right now
   - **Example**: Survey papers marked as "Great for beginners"

5. **Survey Paper Filter** - Priority: HIGH
   - **What**: Quick way to find survey/overview papers
   - **Why I Need It**: Surveys give me the context I'm desperate for
   - **Example**: One-click filter for papers marked as surveys or tutorials

### Nice-to-Have Features:

6. **Reading Lists / Bookmarks**
   - Save papers for later, organize by topic

7. **Related Papers Graph**
   - Visual showing citation relationships

8. **Researcher/Lab Following**
   - Track work from key labs (DeepMind, OpenAI, etc.)

9. **Community Indicators**
   - "Papers your labmates are reading"

10. **Confidence Builders**
    - "You've covered 60% of foundational VLM papers"

---

## Would I Use This Regularly?

### Honest Answer: Maybe, but not as my primary learning tool.

**I Would Use It For:**
- Finding papers when I already know what I'm looking for
- Quick semantic search when Google Scholar fails
- Checking if a specific paper exists

**I Wouldn't Use It For:**
- Learning a new research area (it doesn't teach)
- Building my mental map of the field
- Preparing for lab meetings or qualifying exams
- Reducing my imposter syndrome

**What Would Bring Me Back:**
- If the Research Advisor actually worked and could guide me through the field
- If there were learning paths: "New to VLMs? Start here."
- If it showed me how papers connect historically
- If it could validate that I'm on the right track

**Likelihood of Returning**: 40% - I'd check it occasionally, but I'd still rely on asking my labmates and advisor

**Likelihood of Recommending to Other First-Years**: 30% - I'd mention it exists, but warn them it won't solve the "where do I start?" problem

---

## Comparison to My Current Workflow

**What I Do Now**:
1. Ask my advisor or labmates: "What should I read on X?"
2. Find survey papers on Google Scholar
3. Follow citation trails from foundational papers
4. Check Twitter to see what people are talking about
5. Read papers in order: surveys → seminal work → recent papers

**Where Paper Atlas Fits**:
- Better than Google Scholar for semantic search
- Worse than asking humans for guided learning
- No better than arXiv for browsing
- Doesn't replace my citation trail workflow

**What Would Make It Essential**:
- If it could replace step #1 (asking for guidance)
- If it automated step #3 (citation trails) visually
- If it had curated learning paths like step #5

---

## Recommendations for Improvement

### P0 - Must Fix (Blocking Basic Functionality)

1. **Fix "Invalid Date" Bug**
   - Severity: Medium, Effort: Low
   - Impact: Professional credibility, trust
   - Quick win that improves confidence

2. **Fix Research Advisor Synthesis**
   - Severity: Critical, Effort: Unknown
   - Impact: This is THE feature that could make this tool transformative
   - Without it, the advisor is just another search interface

### P1 - Critical for First-Year PhD Students

3. **Create Learning Paths Feature**
   - Severity: Critical, Effort: High
   - Impact: Transform from search tool to learning tool
   - Example: "Understanding Vision-Language Models: A 10-Paper Journey"
   - This would directly solve my core problem

4. **Add "Foundational Papers" Filter/Tag**
   - Severity: High, Effort: Medium
   - Impact: Help students identify must-read papers
   - Example: Show CLIP as "Foundational Work, 10K+ citations"

5. **Add Survey Paper Filter**
   - Severity: High, Effort: Low
   - Impact: Quick way to get field overviews
   - Easy win for newcomers

### P2 - High Value for Learning

6. **Add Paper Importance Indicators**
   - Show citation counts, awards, conference tier
   - Help students gauge significance

7. **Create Historical Timeline View**
   - Visualize field evolution over time
   - Show how papers build on each other

8. **Add Difficulty Ratings**
   - Label papers as beginner/intermediate/advanced
   - Help students choose appropriate papers

### P3 - Nice to Have

9. **Reading List Management**
   - Let me save and organize papers

10. **Trending Topics - Make Functional**
    - Actually populate with data
    - Make topics clickable

---

## Final Verdict: 6.5/10

### The Good:
- Clean, professional interface
- Semantic search actually works
- Inline paper expansion is smooth
- The Research Advisor *concept* is exactly what I need

### The Bad:
- Doesn't solve my core problem: "Where do I start?"
- No learning path or historical context
- Research Advisor synthesis is broken
- No way to distinguish foundational from incremental work
- Doesn't reduce my imposter syndrome or overwhelm

### The Honest Truth:

I came to Paper Atlas hoping it would be like having a senior PhD student sit down with me and say, "Okay, here's how you learn vision-language models step by step." Instead, it feels like a librarian who can find books efficiently but won't tell me which ones to read first or why they matter.

**For a first-year PhD student trying to get oriented in a new field, this tool is helpful but not transformative.** It's a better search interface, but it's not a learning companion. And right now, that's what I need most.

I'd give it a **6.5/10** - there's real potential here, especially if the Research Advisor worked properly and could provide the context and guidance I'm desperate for. But in its current state, it's a nice-to-have tool, not a must-have one.

**Bottom Line**: I'd still ask my labmates "What should I read?" before relying on this tool to guide my learning.

---

**Assessment conducted by**: Sarah Kim (persona)
**Real user type**: 1st-year PhD student, Stanford Vision Lab
**Research focus**: Vision-language models (still exploring)
**Emotional state**: Eager to learn, anxious about being behind, desperately seeking guidance
**Platform tested**: AI Paper Atlas (localhost:3000)
**Browser**: Chrome via DevTools MCP
**Date**: December 16, 2025
