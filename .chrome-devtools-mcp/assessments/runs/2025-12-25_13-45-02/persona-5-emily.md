# UX Assessment Report: Dr. Emily Zhang
## Interdisciplinary AI Research (Climate Science + ML)

**Date**: December 25, 2025
**Session Duration**: ~30 minutes
**Persona**: Climate scientist applying ML to weather prediction
**Primary Goal**: Find transformers for time series forecasting in scientific domains

---

## Executive Summary

As an atmospheric scientist learning ML, I found AI Paper Atlas both frustrating and delightful. **The Research Advisor saved my session** - basic keyword search failed completely (0 results for "transformers time series"), but the Advisor understood my natural language query and surfaced exactly what I needed: "UNet with Axial Transformer for Weather Prediction." This cross-domain discovery capability is **gold** for interdisciplinary researchers. However, many Discovery features were broken (TL;DR, Rising, Techniques all errored), and the ML-centric category structure made me feel like an outsider. The tool shows promise for bridging domains but needs reliability fixes and better support for non-ML researchers.

---

## Session Timeline & Screenshots

### Step 1: First Impression (0:00)
- **Screenshot**: `01-landing-first-impression.png`
- **Observation**: Landed on Explore page. Categories are pure ML (Computer Vision, NLP, etc.) - no "Scientific ML" or "Physics-informed ML" visible
- **Emotion**: 2/5 (Intimidated - doesn't look designed for me)
- **Load Time**: N/A (couldn't measure due to script error)

### Step 2: Navigation Discovery (0:30)
- **Screenshots**: `02a-nav-discovery.png`, `02b-nav-techniques.png`
- **Observation**: Discovery page has promising tabs (TL;DR, Techniques, Reproducible). Clicked Techniques → immediate error "Failed to fetch technique papers"
- **Emotion**: 2/5 (Disappointed - first feature I tried broke)

### Step 3: Task-Based Search - Transformers Time Series (1:00)
- **Screenshots**: `03a-search-query-typed.png`, `03b-search-no-results.png`
- **Query**: "transformers time series"
- **Result**: **0 results** after 10 seconds
- **Observation**: This is vocabulary mismatch - I used terms from my domain (time series), but the system didn't understand the connection to ML papers
- **Emotion**: 2/5 (Frustrated - this should work)

### Step 3.5: Research Advisor - Critical Success (2:00)
- **Screenshots**: `03c-advisor-panel-opened.png`, `03d-advisor-query-typed.png`, `03e-advisor-response.png`
- **Query**: "I need to predict weather patterns using transformers. What papers cover applying transformers or deep learning to time series forecasting for scientific data?"
- **Response Time**: ~5 seconds
- **Result**: **5 highly relevant papers**, including:
  - ✅ "UNet with Axial Transformer: A Neural Weather Model for Precipitation Nowcasting" ← PERFECT
  - ✅ "EMForecaster: Time Series Forecasting in Wireless Networks"
  - ✅ "PFformer: Position-Free Transformer for Extreme-Adaptive Time Series"
- **Observation**: The Advisor understood my *problem context* (weather, scientific data) not just keywords. Follow-up buttons ("Find citing papers", "Show code") are exactly what I need next
- **Emotion**: **5/5** (Delighted - this is exactly what Google Scholar can't do)

### Step 4: Paper Detail Examination (3:30)
- **Screenshot**: `04-paper-detail-arxiv.png`
- **Observation**: Clicked paper title → went directly to arXiv (external), not an internal detail page
- **Missing**: No AI analysis, extracted techniques, or impact assessment visible
- **Emotion**: 3/5 (Neutral - got the paper but lost the value-add)

### Step 5: Code Availability Check (4:00)
- **Screenshot**: `05-code-filter.png`
- **Action**: Applied "Has Code" filter to previous search
- **Result**: Filter activated, found time series papers with code indicators
- **Observation**: Code badge is visible, which is critical for reproducibility
- **Emotion**: 4/5 (Pleased - this filters out theory-only papers quickly)

### Step 6-7: Discovery Features - Multiple Failures (5:00)
- **Screenshots**: `06-tldr-tab.png`, `07-rising-tab-error.png`
- **TL;DR Tab**: Error "Failed to fetch TL;DR papers" + "No summaries from last 7 days"
- **Rising Tab**: Error "Failed to fetch rising papers"
- **Observation**: 3 of 5 Discovery tabs failed. Pattern suggests backend API issues
- **Emotion**: 2/5 (Concerned - tool feels unstable)

### Step 11: Second Search - Climate ML (6:00)
- **Screenshot**: `08-climate-ml-search.png`
- **Query**: "machine learning climate science"
- **Result**: Found **"Machine Learning Workflows in Climate Modeling: Design Patterns and Insights from Code"** with Has Code badge
- **Observation**: This is **exactly** the cross-domain discovery I need - a paper that bridges ML techniques and climate applications. Smart Results (AI-powered) badge visible
- **Emotion**: **5/5** (Excited - found a paper I'd never have discovered in climate journals)

### Step 12: Final State (6:30)
- **Screenshot**: `09-final-state.png`
- **Observation**: Same climate ML paper, Has Code filter active, search successful
- **Overall Session**: Mixed - when it works (Advisor, Smart Search), it's transformative. When it fails (Discovery tabs), it's frustrating

---

## Pain Point Assessment

### 1. ❌ Terminology Gap (MAJOR ISSUE)
**Problem**: ML papers use different terminology than my field
**Result**: Basic search for "transformers time series" returned 0 results despite 5 relevant papers existing
**Solution**: Research Advisor bridged the gap with semantic understanding
**Impact**: **Partially Solved** - but relying on Advisor for every search is slow

### 2. ✅ Cross-Domain Discovery (SOLVED!)
**Problem**: Techniques in NLP/vision might apply to climate but published elsewhere
**Result**: Found "UNet Axial Transformer for Weather" and "ML Workflows in Climate Modeling"
**Solution**: Smart Results + Advisor understand problem context, not just keywords
**Impact**: **Fully Solved** - this is the killer feature

### 3. ⚠️ Adaptation Complexity (PARTIALLY ADDRESSED)
**Problem**: Hard to know what ML methods transfer to physical science data
**Evidence Needed**: Paper detail pages with "Domain Applicability" analysis
**Current State**: Papers mention "time series" and "scientific data" but no systematic transfer analysis
**Impact**: **Needs Improvement**

### 4. ⚠️ Limited ML Background (UNADDRESSED)
**Problem**: Haven't read foundational ML papers, miss context
**Observation**: No "Learning Path" feature visible (tab exists but untested due to errors)
**Impact**: **Not Evaluated** - feature may exist but inaccessible

### 5. ❌ Justification to Peers (NOT ADDRESSED)
**Problem**: Need to justify ML approaches to skeptical climate scientists
**Missing**: Explainability focus, domain-specific impact metrics, "why this works for physics" explanations
**Impact**: **Unaddressed** - tool assumes ML literacy

---

## Cross-Domain Discovery Assessment

### Strengths for Interdisciplinary Researchers

1. **Natural Language Queries Work** ✅
   - Advisor understood "weather patterns using transformers" → found weather ML papers
   - Didn't need to know ML jargon like "temporal attention" or "sequence-to-sequence"

2. **Problem-Centric, Not Keyword-Centric** ✅
   - Query: "predict weather patterns" → Results: papers on precipitation, climate modeling
   - Traditional search would need exact term matching

3. **Found Non-ML-Venue Papers** ✅
   - "ML Workflows in Climate Modeling" likely published in climate/computational science venue
   - Shows the tool indexes beyond cs.LG and cs.CV

### Weaknesses for Non-ML Experts

1. **Category Structure is ML-Native** ❌
   - Categories: "Computer Vision", "NLP", "Neural Networks"
   - Missing: "Scientific ML", "Physics-Informed ML", "Climate AI", "Geoscience ML"
   - **Impact**: I don't know where my work fits

2. **No Domain Translation Help** ❌
   - Papers mention "attention mechanisms" without explaining what that means
   - Missing: "For climate scientists: attention = weighing spatial regions differently"

3. **Discovery Features Assume ML Knowledge** ❌
   - "Techniques" tab (if it worked) likely shows "ResNet", "LSTM" without context
   - Need: "Techniques for Time Series in Science" with explanations

---

## Accessibility for Non-ML Experts

### Jargon & Terminology

**Barrier Level**: ⚠️ **Medium-High**

- **Example 1**: "Axial Transformer" in paper title - what does "axial" mean? (spatial decomposition)
- **Example 2**: "Position-Free Transformer" - why does position matter? (temporal ordering)
- **Example 3**: "PatchTST" - what's a patch in time series context? (subsequence window)

**What Would Help**:
- Hover tooltips: "Transformer = neural network that weighs relationships between data points"
- "Explain for domain scientists" button on papers
- Glossary linking ML terms to scientific equivalents

### Navigation Clarity

**Barrier Level**: ✅ **Low** (when features work)

- "Research Advisor" is self-explanatory
- "Has Code" filter is clear and valuable
- "Smart Results" badge indicates AI processing

**Confusing**:
- "TL;DR" tab - acronym without expansion (should be "Quick Summaries")
- "Rising" - rising in what metric? Citations? Views?

---

## Transfer Potential Evaluation

### How Well Does It Surface Applicable Techniques?

**Rating**: ⭐⭐⭐⭐☆ (4/5 - Excellent with caveats)

#### Success Cases

1. **Weather Transformers** ✅
   - Query: weather prediction
   - Found: UNet with transformers for precipitation
   - **Transfer Clarity**: High - paper explicitly addresses weather/climate

2. **Time Series Architectures** ✅
   - Query: time series forecasting
   - Found: Multiple transformer variants (PFformer, Hi-WaveTST)
   - **Transfer Clarity**: Medium - need to assess if methods work for physical data

#### Gaps

1. **No Transfer Assessment** ❌
   - Papers don't indicate: "This worked on finance data, might work for climate because..."
   - Missing: "Domain similarity score" or "Transfer learning viability"

2. **No Negative Examples** ❌
   - Don't see: "These papers tried transformers on scientific data and failed"
   - Need: Lessons learned from unsuccessful transfers

3. **Implementation Guidance Missing** ⚠️
   - "Show me code" button exists but not tested
   - Need: "Here's how to adapt this PyTorch code for NetCDF climate data"

---

## Performance Metrics

### Load Times
- **Landing Page**: Not measured (script error)
- **Basic Search**: 10 seconds → 0 results (slow failure)
- **Advisor Response**: ~5 seconds → 5 results (acceptable)
- **Climate ML Search**: ~8 seconds → 6 results (acceptable for semantic search)

### Search Quality
- **Keyword Search**: 0/10 (completely failed on "transformers time series")
- **Advisor Search**: 10/10 (perfect relevance for weather prediction query)
- **Smart Results**: 9/10 (climate ML search found cross-domain paper)

### Feature Reliability
- **Working**: Explore, Advisor, Filters (Has Code), Smart Search
- **Broken**: TL;DR, Rising, Techniques (3/5 Discovery tabs failed)
- **Reliability Score**: ⚠️ 5/10 (core features work, discovery features don't)

---

## Delights & Frustrations

### 🎉 Delights

1. **Research Advisor Saved the Session** ⭐⭐⭐⭐⭐
   - Turned 0 results into 5 perfect papers
   - Natural language understanding is MAGIC for non-ML researchers
   - Follow-up actions (citations, alternatives, code) anticipate next steps

2. **Found Climate ML Paper I'd Never See Otherwise** ⭐⭐⭐⭐⭐
   - "ML Workflows in Climate Modeling" bridges my two worlds
   - Has Code badge → I can actually use this
   - This is the cross-domain discovery that justifies using this tool

3. **Smart Results Beat Keyword Matching** ⭐⭐⭐⭐
   - "machine learning climate science" understood as problem domain, not just keywords
   - Semantic search is clearly working

### 😤 Frustrations

1. **Half the Discovery Features Are Broken** 💀💀💀
   - TL;DR error, Rising error, Techniques error
   - Feels like the tool is in beta
   - Can't recommend to colleagues if it's this unstable

2. **Basic Search Completely Failed** 💀💀
   - "transformers time series" → 0 results is unacceptable
   - I shouldn't NEED the Advisor for simple queries
   - Keyword fallback should catch basic terms

3. **No "For Scientists" Onboarding** 💀
   - Categories assume I know ML taxonomy
   - No "New to ML? Start here" guide
   - Tool assumes I understand attention mechanisms, ResNets, etc.

4. **Paper Links Go to arXiv, Not Internal Analysis** 💀
   - Clicked paper → external link
   - Lost the AI-generated insights that would help me evaluate relevance
   - What's the point of "AI Paper Atlas" if I end up on arXiv anyway?

---

## Priority Improvements

### P0: Critical (Fix Now)

| Improvement | Impact | Effort | Rationale |
|------------|--------|--------|-----------|
| **Fix Discovery tab errors** | 🔥🔥🔥 High | Medium | 3/5 tabs broken → users lose trust. TL;DR is critical for quick triage |
| **Improve keyword search fallback** | 🔥🔥🔥 High | Medium | "transformers time series" should NOT return 0 results. Add synonym expansion |
| **Paper detail pages (not external links)** | 🔥🔥 Medium | High | Users lose AI value-add when sent to arXiv. Need internal analysis page |

### P1: Important (Next Sprint)

| Improvement | Impact | Effort | Rationale |
|------------|--------|--------|-----------|
| **Add "Scientific ML" category** | 🔥🔥 Medium | Low | Non-ML researchers don't know where they fit. Add domain-specific categories |
| **Terminology tooltips/glossary** | 🔥🔥 Medium | Medium | "Axial Transformer" means nothing to climate scientists. Explain ML jargon |
| **Domain applicability indicators** | 🔥🔥 Medium | High | Show "Used for: time series, physics data, climate" on papers |

### P2: Nice to Have (Future)

| Improvement | Impact | Effort | Rationale |
|------------|--------|--------|-----------|
| **Learning path for domain scientists** | 🔥 Low | High | "ML for Climate Scientists" curriculum would help onboarding |
| **Transfer learning viability scores** | 🔥 Low | High | "This NLP technique has 70% transfer success to time series" |
| **"Explain for scientists" mode** | 🔥 Low | Medium | Toggle that adds explanations of ML concepts |

---

## Screenshots Index

1. `01-landing-first-impression.png` - Initial Explore page, ML-centric categories
2. `02a-nav-discovery.png` - Discovery page with Quick Discovery cards
3. `02b-nav-techniques.png` - Techniques tab error (failed to fetch)
4. `03a-search-query-typed.png` - "transformers time series" typed in search
5. `03b-search-no-results.png` - 0 results after 10 seconds (failure case)
6. `03c-advisor-panel-opened.png` - Research Advisor UI with example queries
7. `03d-advisor-query-typed.png` - Natural language query about weather prediction
8. `03e-advisor-response.png` - Advisor found 5 relevant papers including weather transformer
9. `04-paper-detail-arxiv.png` - External arXiv link (lost internal analysis)
10. `05-code-filter.png` - "Has Code" filter applied, found time series papers
11. `06-tldr-tab.png` - TL;DR tab error (failed to fetch)
12. `07-rising-tab-error.png` - Rising papers tab error
13. `08-climate-ml-search.png` - "machine learning climate science" found climate ML paper
14. `09-final-state.png` - Final state with climate ML paper visible

---

## Final Verdict

### Would I Bookmark This Tool?
**YES** ⭐⭐⭐⭐☆ (4/5)

Despite the broken features, the Research Advisor alone makes this valuable. Finding "UNet Axial Transformer for Weather" in 5 seconds vs. hours on Google Scholar justifies bookmarking.

### Would I Return Tomorrow?
**MAYBE** ⭐⭐⭐☆☆ (3/5)

I'd return for the Advisor and Smart Search, but avoid the broken Discovery tabs. Would check back in a month to see if stability improves.

### Would I Recommend to Climate Science Colleagues?
**WITH CAVEATS** ⭐⭐⭐☆☆ (3/5)

**Recommendation**: "Try the Research Advisor for cross-domain discovery, but ignore the Discovery page - half of it is broken. If you're new to ML, be prepared to Google a lot of jargon."

**Who I'd Recommend To**:
- Climate scientists learning ML (but warn about jargon)
- Domain scientists looking for applied ML papers (Advisor is perfect)
- Anyone frustrated with keyword search on arXiv

**Who I'd NOT Recommend To**:
- People who need reliable, production-ready tools (too many errors)
- ML beginners who need guided learning (no scaffolding)
- Researchers who need quick scans (TL;DR doesn't work)

---

## What Makes This Tool Special for Interdisciplinary Research?

The **Research Advisor** is genuinely transformative. It doesn't just match keywords - it understands **problem context across domain boundaries**. When I said "weather patterns using transformers", it knew to look for:
- Papers mentioning precipitation, climate, atmospheric science
- Time series architectures (not vision transformers)
- Scientific applications (not chatbots or image generation)

This semantic understanding is **exactly what Google Scholar lacks** and **exactly what interdisciplinary researchers need**.

**But**: The tool undermines this strength by being unstable (broken Discovery tabs) and ML-centric (no scientific domain categories). It's 70% of the way to being indispensable for climate scientists like me - fix the reliability and accessibility issues, and it becomes a must-use tool.

---

## Key Takeaway for Product Team

**You have a killer feature (Research Advisor) wrapped in an unstable product (Discovery tabs broken) with an accessibility problem (assumes ML expertise).**

**Quick wins**:
1. Fix the Discovery tab errors (restores user trust)
2. Add "Scientific ML" / "Climate AI" / "Physics-Informed ML" categories (shows you care about domain scientists)
3. Make keyword search less brittle (don't return 0 results for reasonable queries)

**Do these three things**, and I'll recommend this tool to every climate scientist I know who's trying to learn ML. Right now, I recommend it with too many caveats.

---

**Assessment completed by**: Dr. Emily Zhang (simulated persona)
**Total screenshots captured**: 14
**Session emotion range**: 2/5 (frustrated) to 5/5 (delighted)
**Overall experience**: Mixed - transformative when it works, frustrating when it doesn't
