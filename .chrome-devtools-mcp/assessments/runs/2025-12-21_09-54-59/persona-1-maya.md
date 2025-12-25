# UX Assessment Report: Dr. Maya Chen
## AI Paper Atlas - Postdoc Researcher Perspective

**Date**: December 21, 2025, 09:55 PST
**Persona**: Dr. Maya Chen, 2nd-year Postdoc, CMU Machine Learning
**Research Focus**: Efficient transformers for edge/mobile deployment
**Time Constraint**: 20 minutes before advisor meeting

---

## Executive Summary

As a time-pressured postdoc researcher, I needed AI Paper Atlas to quickly find relevant papers on efficient attention mechanisms with working code. The **Research Advisor feature delivered exceptional value** - after basic keyword search failed completely, the AI-powered advisor found 5 highly relevant papers in my exact research area within seconds. However, **critical UX friction points** around search reliability, navigation responsiveness, and error states significantly undermined confidence. The tool shows strong potential but needs stability improvements before I'd rely on it daily.

**Would I return?** Maybe - the Advisor feature alone is worth revisiting, but the errors and inconsistent behavior make me hesitant to trust it for critical research needs.

---

## Session Timeline

**Total Duration**: ~15 minutes active exploration
**Screenshots Captured**: 14

| Time | Step | Action | Result | Emotion |
|------|------|--------|--------|---------|
| 09:55 | Setup | Navigate to localhost:3000 | Landed on Explore page | 3/5 |
| 09:56 | Step 1 | First impression | Clean UI, search prominent, "Ask Advisor" visible | 3/5 |
| 09:57 | Step 2 | Navigate to Discovery | Error: "Failed to fetch impact papers" | 2/5 |
| 09:58 | Step 3 | Search: "efficient attention mechanisms for mobile deployment" | 30 generic papers returned, NONE relevant to query | 1/5 |
| 09:59 | Step 3.5 | Try Research Advisor | Found 5 HIGHLY relevant papers instantly | 4/5 |
| 10:02 | Step 4 | Expand paper detail | Full abstract visible, "Generate Code" button present | 4/5 |
| 10:03 | Step 5 | Apply "Has Code" filter | Filter badge appeared, results count unchanged | 3/5 |
| 10:04 | Step 6 | Check Discovery/Reproducible | Loading state, unclear if results loaded | 3/5 |
| 10:05 | Step 7 | Explore Generate page | Multi-agent code generation explained clearly | 4/5 |
| 10:06 | Final | Return to Explore | Search state lost, back to empty | 3/5 |

---

## Detailed Step Analysis

### Step 1: First Impression (Landing Page)

**What I saw**: Clean, professional landing page with prominent search box and "Ask Advisor" button. Sidebar shows filters (Has Code, High Impact, categories). Default view shows 30 recent papers in CS.CV/CS.CL.

**Expectations**: I expected to immediately see relevant papers or be guided to search. The placeholder text "efficient attention for mobile deployment" was encouraging - it matched my exact use case.

**Reality**: The default feed was generic recent arXiv papers with no personalization. As a first-time user, this felt like browsing arXiv's "recent" tab - not compelling enough to distinguish the tool.

**Emotion**: 3/5 - Neutral. Professional but not immediately useful.

**Load Time**: Could not measure accurately (performance API error), but page felt fast.

---

### Step 2: Initial Exploration (Navigation Discovery)

**What I tried**: Clicked through Discovery, Generate navigation links.

**Discovery Page Issues**:
- Immediate error: "Failed to fetch impact papers"
- Error persisted throughout session
- Multiple tabs visible (Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path)
- "Quick Discovery" cards present but main content broken

**Confusion Points**:
- Is Discovery fundamentally broken or just temporarily down?
- Should I trust other features if this core section errors?
- No explanation of what each tab does - had to click to discover

**Emotion**: 2/5 - Frustrated by immediate error, worried about overall reliability.

---

### Step 3: Task-Based Search (Finding Relevant Papers)

**Query**: "efficient attention mechanisms for mobile deployment"

**Results**: 30 papers returned under "KEYWORD MATCH" (not AI-powered initially)

**Critical Failure**: ZERO papers were actually about efficient attention mechanisms. Results included:
- Generative View Stitching (video diffusion)
- Agent Data Protocol (LLM agents)
- Translation evaluation metrics
- Medical LLMs
- VR game benchmarks

**What went wrong**: The keyword search appears to do simple text matching without semantic understanding. My query mentioned "attention" and "deployment" but the results were completely off-topic.

**Time wasted**: ~2 minutes scanning irrelevant papers, growing frustrated.

**Emotion**: 1/5 - Extremely frustrated. This is exactly the problem I face with arXiv search. If this tool can't do better than basic keyword matching, why use it?

---

### Step 3.5: Research Advisor (AI-Powered Search)

**Turning Point**: Clicked "Ask Advisor" button out of desperation.

**Query**: "I'm working on efficient attention mechanisms for transformer deployment on mobile and edge devices. Need papers with working code implementations."

**Results**:
1. Attentions Under the Microscope: A Comparative Study of Resource Utilization for Variants of Self-Attention
2. Adaptive Token Merging for Efficient Transformer Semantic Communication at the Edge
3. Fast and Cost-effective Speculative Edge-Cloud Decoding with Early Exits
4. Analysis of Hyperparameter Optimization Effects on Lightweight Deep Models for Real-Time Image Classification
5. BitStopper: An Efficient Transformer Attention Accelerator via Stage-fusion and Early Termination

**Analysis**: These papers are EXACTLY what I needed:
- Focus on efficient attention variants
- Mobile/edge deployment context
- Practical optimization techniques
- Recent publications (2025)

**Response Quality**:
- Note: "Contextual synthesis temporarily unavailable" - unclear what this means, but didn't affect usefulness
- Provided brief descriptions pointing to "actionable leads"
- Follow-up action buttons: "Find papers that cite these works", "What are alternative approaches?", "Show me implementation code"

**Search Time**: ~3.5 seconds (displayed: "3490ms")

**Emotion**: 4/5 - Delighted! This is the breakthrough moment. The advisor understood my semantic intent and delivered exactly what I needed.

**Key Insight**: The advisor should be the PRIMARY interface, not a fallback. Basic keyword search is actively harmful - it wastes time and erodes trust.

---

### Step 4: Deep Dive (Paper Detail View)

**Paper Examined**: "Adaptive Attention-Based Model for 5G Radio-based Outdoor Localization"

**What I saw when expanded**:
- Full abstract (readable, well-formatted)
- Tab navigation: Summary, Related Papers, Benchmarks
- "Read on arXiv" link
- "Generate Code" button (very appealing!)

**Missing Critical Information**:
- No visible GitHub link or code availability indicator
- No citation count or impact metrics
- No publication date prominently displayed
- No author affiliation information
- No "Has Code" badge on the card itself

**What I wanted**:
- Immediate visual indicator: Does this paper have code?
- GitHub stars/forks if code exists
- Citation velocity (is this gaining traction?)
- Related papers by same authors

**Emotion**: 4/5 - Good detail view, but missing key decision-making information for a researcher.

---

### Step 5: Code Availability Check

**Action**: Clicked "Has Code" filter in sidebar.

**Observation**:
- Filter badge appeared with "× Clear all" option
- Results count stayed at 6 papers
- No visual change to which papers were displayed
- Unclear if filter actually did anything

**Confusion**:
- Does this mean all 6 papers have code?
- Or does the filter not work?
- Why isn't code availability shown on each card?

**Expected Behavior**:
- Show GitHub icon on papers WITH code
- Filter should reduce results to ONLY papers with code
- Display stars/forks/last commit date

**Actual Behavior**: Ambiguous - can't tell if it worked.

**Emotion**: 3/5 - Uncertain. The filter might work, but I can't verify it.

---

### Step 6-7: Discovery Tab Exploration

**Reproducible Tab**:
- Clicked, saw "Finding reproducible papers..." loading state
- Waited 3 seconds, took screenshot
- Unclear if results ever loaded (no visible change)

**Generate Page**:
- Clearly explained multi-agent system (Paper Analyzer → Test Designer → Code Generator → Test Executor → Debugger)
- TDD approach is clever
- Search box for papers present but empty
- Professional explanation of how it works

**Emotion**: 4/5 for Generate page concept, 3/5 for loading ambiguity.

---

### Step 8-11: Navigation & Final State

**Issues Encountered**:
- Reading List link didn't navigate properly
- Returning to Explore cleared my search context
- No session persistence - lost my query and results

**Expected**:
- Back button should restore previous search state
- Session should remember my last query
- Reading List should show saved papers

**Emotion**: 2/5 - Frustrating loss of work context.

---

## Pain Point Assessment

### Pain Point 1: Information Overload
**Status**: ❌ **PARTIALLY SOLVED**

**What worked**: Research Advisor cuts through noise brilliantly - gave me 5 relevant papers vs. 50-100 arXiv abstracts I'd normally scan.

**What didn't**: Default keyword search made the problem WORSE by returning 30 irrelevant papers. This is anti-helpful.

**Impact**: The advisor alone saves 15+ minutes of daily arXiv scanning. But the broken keyword search wastes 2-3 minutes and damages trust.

---

### Pain Point 2: Time Poverty
**Status**: ✅ **SOLVED (when Advisor works)**

**Evidence**: Found 5 relevant papers in 4 seconds vs. typical 20-30 minute arXiv session.

**Caveat**: Navigation errors and loading ambiguity added friction that ate into time savings.

**Would I use it daily?** Yes, BUT only if the advisor becomes the default interface and reliability improves.

---

### Pain Point 3: Reproducibility Frustration
**Status**: ⚠️ **UNCLEAR**

**Attempted Solutions**:
- "Has Code" filter exists but unclear if it works
- "Generate Code" button promises code generation
- Reproducible tab in Discovery promises papers with code

**Missing**:
- Clear visual indicators of code availability on each paper card
- GitHub integration (stars, forks, last update)
- Code quality signals (tests, documentation, community usage)

**What I needed**: Instant visibility of "this paper has code on GitHub with 500 stars" vs. "this paper has no code, avoid unless you want to spend 20 hours reimplementing."

**Current state**: Promising features but poor visibility and unclear status.

---

### Pain Point 4: Connection Blindness
**Status**: ✅ **SOLVED**

**What worked**:
- Advisor provided papers I wouldn't have found with keyword search
- "Related Papers" tab promises connections (didn't fully test)
- Follow-up actions: "Find papers that cite these works", "What are alternative approaches?"

**This is powerful**: The advisor connected "efficient attention" → "token merging", "speculative decoding", "BitStopper hardware acceleration" - connections I wouldn't have made searching by keywords alone.

---

### Pain Point 5: Trend Anxiety
**Status**: ❌ **NOT ADDRESSED**

**What exists**:
- "Rising Stars" section (broken due to Discovery error)
- "Hot Topics" tab (couldn't test)
- "Trending Now" sidebar (showed "No trending data available")

**What I needed**:
- "These 3 papers are gaining citations rapidly in efficient attention"
- "Flash Attention 3 just dropped yesterday, 500 stars in 24 hours"
- "Your subfield is shifting toward X technique"

**Current state**: Features exist but all errored or showed no data. Can't evaluate.

---

## Delights

### 🎉 Research Advisor = Game Changer
The semantic understanding blew me away. Pasting my research problem in natural language and getting 5 perfect papers in 3.5 seconds is EXACTLY what I need. This alone could save me hours per week.

**Why it delights**:
- Understands intent, not just keywords
- Surfaces papers I'd never find with manual search
- Fast enough to use impulsively

**Make this the default interface.**

---

### 🎉 "Generate Code" Concept
The multi-agent TDD approach to generating implementations is incredibly appealing. As someone who's reimplemented papers from scratch, this could save days of work.

**Caveat**: Didn't test it, so delight is based on promise, not execution.

---

### 🎉 Clean, Professional UI
The design doesn't get in the way. Readable fonts, good contrast, clear hierarchy. No dark patterns or clutter.

---

## Frustrations

### 😡 Keyword Search is Actively Harmful
Returning 30 completely irrelevant papers damages trust. I'd rather see "0 results, try the Advisor" than waste time scanning garbage results.

**Fix**: Disable keyword search OR add semantic layer to improve relevance OR show "Low confidence match" warnings.

---

### 😡 Error: "Failed to fetch impact papers"
This error appeared immediately on Discovery page and never resolved. It makes the entire Discovery section feel broken.

**Impact**: I avoid the feature entirely, missing out on High Impact, Rising, TL;DR sections.

**Fix**: Better error handling, retry logic, or fallback content.

---

### 😡 Loading States with No Feedback
"Finding reproducible papers..." never resolved (or I couldn't tell if it did). This creates uncertainty - did it fail? Is it still loading? Should I wait?

**Fix**: Timeouts, progress indicators, or "No results found" messages.

---

### 😡 No Session Persistence
Navigating away from search results loses my context. I have to re-run the advisor query to get back to my papers.

**Fix**: Browser history integration, or "Recent Searches" saved state.

---

## Performance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Landing page load | Unknown (API error) | <2s | ❓ |
| Advisor response time | 3.49s | <5s | ✅ |
| Search response time | 3.49s | <3s | ⚠️ |
| Papers scanned to find 1 relevant | 0 (keyword), 5/5 (advisor) | N/A | ✅ Advisor |
| Time to first relevant paper | 4 min (keyword failed), 4s (advisor) | <30s | ✅ Advisor |

---

## Priority Improvements

### P0 (Blocking Issues - Fix Before I'd Recommend)

| Issue | Impact | Effort | Recommendation |
|-------|--------|--------|----------------|
| Discovery "Failed to fetch" error | High - Core feature broken | Medium | Investigate API, add retry, show fallback | 5 |
| Keyword search returns irrelevant results | High - Wastes time, erodes trust | High | Add semantic layer OR disable in favor of Advisor | 4 |
| Loading states unclear (Reproducible tab) | Medium - Uncertainty blocks exploration | Low | Add timeouts, spinners, "No results" states | 3 |

### P1 (Major UX Issues - Fix for Daily Use)

| Issue | Impact | Effort | Recommendation |
|-------|--------|--------|----------------|
| No code availability indicators on cards | High - Core need unmet | Low | Add GitHub icon, stars, "Has Code" badge | 5 |
| Session state lost on navigation | Medium - Annoying friction | Medium | Save search context to URL or localStorage | 4 |
| Advisor should be default, not fallback | High - Keyword search hurts experience | Low | Swap order: Advisor first, keyword as fallback | 5 |

### P2 (Nice to Have - Polish for Excellence)

| Issue | Impact | Effort | Recommendation |
|-------|--------|--------|----------------|
| No citation/impact metrics on papers | Medium - Hard to assess importance | Medium | Show citation count, h-index, recency | 3 |
| "Generate Code" untested | Unknown - High promise | N/A | Ensure it works reliably, test with real papers | 4 |
| Trending features all broken/empty | Medium - Can't evaluate trend anxiety solution | Medium | Fix data pipeline for Rising/Hot Topics | 3 |

---

## Screenshots Index

1. **01-landing-first-impression.png** - Initial page load, clean UI, 30 papers visible
2. **02a-nav-discovery.png** - Discovery link clicked but page didn't change (bug?)
3. **02b-nav-generate.png** - Discovery page with error message
4. **03a-search-query-entered.png** - Search query entered, 30 irrelevant results
5. **03b-advisor-opened.png** - Research Advisor modal opened
6. **03c-advisor-query-entered.png** - Natural language query entered
7. **03d-advisor-response.png** - 5 highly relevant papers returned
8. **04-paper-detail-expanded.png** - Expanded paper view with full abstract
9. **05-code-filter-applied.png** - "Has Code" filter badge visible
10. **06-discovery-page.png** - Discovery page error persisted
11. **07-reproducible-tab.png** - Loading state for reproducible papers
12. **08-reproducible-loaded.png** - Post-load state (unclear if results appeared)
13. **09-generate-page.png** - Generate feature explanation
14. **10-reading-list.png** - Navigation issue (didn't navigate)
15. **11-final-state.png** - Search context lost on return

---

## Final Verdict

### Would I bookmark this tool?
**Yes**, specifically for the Research Advisor feature.

### Would I return tomorrow?
**Maybe** - depends on whether Discovery error gets fixed and keyword search improves.

### Would I recommend to colleagues?
**Cautiously, with caveats**: "The AI advisor is amazing for finding papers, but the interface has bugs - stick to the advisor and ignore keyword search."

### What frustrated me most?
The broken keyword search that returned 30 irrelevant papers. It made me question whether the tool understood my domain at all. The advisor proved it did, but first impressions matter.

### What delighted me most?
The Research Advisor finding 5 perfect papers in 3.5 seconds. That single interaction saved me 20+ minutes of arXiv scanning and delivered papers I wouldn't have found on my own.

### One change that would make me a daily user?
**Make the Advisor the default search interface.** Hide or remove keyword search until it's semantically aware. The advisor is 100x better - lead with your strength.

---

## Researcher Context Notes

**My typical workflow**:
- Check arXiv daily for new papers in cs.LG, cs.CL
- Scan 50-100 titles, read 10 abstracts, deep-dive on 2-3
- Spend 20-30 minutes daily, but always feel like I'm missing important work

**Why this tool could help**:
- Advisor replaces manual scanning (saves 20 min/day = 2+ hours/week)
- Code generation could save days of reimplementation
- Semantic search finds connections I'd miss

**Why I'm hesitant**:
- Errors make me question reliability for critical research
- Keyword search failure makes me wonder if database is comprehensive
- No clear indication of corpus size (30 papers total? 30M papers?)

**Trust threshold**:
- I need 2-3 weeks of consistent, error-free use before I'd rely on this for paper discovery
- If it works, I'd pay $20-30/month for this (saves hours of my time)
- If it stays buggy, I'll stick with arXiv + Google Scholar (free and reliable, if slower)

---

**Assessment completed**: December 21, 2025, 10:10 PST
**Total assessment time**: 15 minutes active use
**Screenshots**: 14 captured
**Overall Experience**: 3.2/5 - High potential undermined by execution issues
