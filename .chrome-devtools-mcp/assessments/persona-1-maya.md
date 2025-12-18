# UX Assessment Report: Dr. Maya Chen (LIVE SESSION 2025-12-16)

**Persona**: 2nd-year postdoc at CMU, researching efficient transformers for edge/mobile deployment
**Date**: 2025-12-16
**Time Constraint**: 20 minutes before advisor meeting
**Assessment Duration**: ~15 minutes
**Screenshots**: 10 total in `.chrome-devtools-mcp/assessments/maya-chen/`

---

## Executive Summary

AI Paper Atlas shows promise for semantic paper discovery but falls short on critical features for time-pressed researchers. The Research Advisor feature delivered relevant papers quickly, but missing code visibility, broken trending data, and slow/hanging features create friction. Would use cautiously for initial discovery, but not as primary tool yet.

**Would I return tomorrow?** Maybe (50/50)
**Would I recommend to colleagues?** Not yet - needs stability improvements first

---

## Session Timeline & Metrics

| Step | Action | Time/Outcome | Emotional State (1-5) |
|------|--------|--------------|----------------------|
| 0 | Environment setup | <1s | 3 - Neutral |
| 1 | Landing page load | ~2s, showed 30 CV papers | 3 - Cautious |
| 2 | Navigation exploration | Found Explore + Generate | 3 - Neutral |
| 3 | Search: "efficient attention mechanisms for mobile deployment" | 8003ms, 6 results | 4 - Excited |
| 3.5 | Research Advisor query | 15s, 5 relevant papers + follow-ups | 4 - Useful |
| 4 | Expanded paper detail | Full abstract + tabs visible | 3 - Okay |
| 5 | "Has Code" filter test | Filter applied but no change in results | 2 - Confused |
| 9 | Check trending topics | "No trending data available" | 2 - Disappointed |
| 10 | Related Papers tab | Stuck loading, timed out after 10s | 2 - Frustrated |
| 11 | Second search: "flash attention optimization" | 2188ms, 6 different relevant results | 4 - Satisfied |

**Key Performance Metrics**:
- First search: 8003ms (acceptable but slow)
- Second search: 2188ms (much better)
- Research Advisor response: ~15s (adequate)
- Related Papers: Failed to load (critical issue)

---

## Detailed Step Analysis

### Step 1: First Impression
**Visual**: Clean, modern interface. Search box prominent. "Ask Advisor" button in orange catches eye.
**Issue**: Page loaded showing 30 papers in Computer Vision - not my field. Confusing default state.
**What I expected**: Empty state or prompt to search, not random papers.
**Emotion**: 3/5 - Neutral but slightly confused

### Step 2: Navigation Discovery
**Found**: Two main sections - "Explore" (current) and "Generate" (multi-agent code generation)
**Generate feature**: Interesting concept but not my immediate need. Would explore later if tool proves valuable.
**Emotion**: 3/5 - Clear navigation structure

### Step 3: Initial Search
**Query**: "efficient attention mechanisms for mobile deployment"
**Results**: 6 papers, marked as "Smart Results" with AI-POWERED badge
**Relevance**: First result (GNN-to-KAN distillation for edge deployment) was directly on target
**Speed**: 8003ms - slow but acceptable. Shows "AI-powered semantic search in progress" messaging.
**Emotion**: 4/5 - Excited to find relevant work I didn't know about

### Step 3.5: Research Advisor
**Query**: "I'm working on making transformer attention mechanisms more efficient for mobile and edge devices. Specifically looking for sparse attention, linear attention, or flash attention approaches with real benchmark results on mobile hardware."

**Response**: 5 highly relevant papers:
- "Attentions Under the Microscope" - comparative resource study
- "SageAttention2" - INT4 quantization approach
- "Explore Activation Sparsity" - neuromorphic computing angle
- PureKV - KV cache optimization
- Plus 2 more

**Follow-up actions offered**:
- Find citing papers
- Alternative approaches
- Show implementation code

**Issue**: "Contextual synthesis temporarily unavailable" message - backend problem?
**Strength**: Papers were more relevant than basic search. Natural language understanding worked well.
**Emotion**: 4/5 - This feature could save significant time, but truncated response was frustrating

### Step 4: Paper Deep Dive
**Clicked**: First result (GNN-to-KAN distillation paper)
**Expanded view showed**:
- Full abstract (detailed, helpful)
- Tabs: Summary | Related Papers | Benchmarks
- Key metrics: 16.96x parameter reduction, 55.75% faster inference
- Links: "Read on arXiv" and "Generate Code"

**What I wanted to see**:
- ✓ Full abstract
- ✓ Performance numbers
- ✗ AI-generated summary of key techniques
- ✗ Code availability indicator
- ✗ Practical implications for my work
- ✗ Related work comparison

**Emotion**: 3/5 - Good baseline info, but not much value-add beyond arXiv

### Step 5: Code Availability Check
**Action**: Clicked "Has Code" quick filter
**Result**: Filter badge appeared, but still showed same 6 results
**Confusion**: Either all 6 have code (unlikely), filter isn't working, or filter doesn't exclude non-code papers
**Critical issue**: As someone who won't use papers without code, this is a deal-breaker feature. I need confidence that code exists before investing time reading.
**Emotion**: 2/5 - Confused and concerned about filter reliability

### Step 6-8: Missing Features
**Learning Path**: No visible route to `/discovery/learning-path` - feature may not exist yet
**TL;DR Mode**: No `/discovery/tldr` route found - would be valuable for quick scanning
**Techniques Explorer**: No `/discovery/techniques` section visible
**Impact**: These features appeared in methodology but aren't implemented. Sets wrong expectations.
**Emotion**: N/A - Skipped unavailable features

### Step 9: Trending Topics Check
**Location**: Bottom of page, tabs for "Hot Topics | Rising | Emerging"
**Result**: "No trending data available" for all three tabs
**Critical miss**: This addresses my "Trend Anxiety" pain point directly - I worry about missing emerging techniques. Empty state is disappointing.
**Sidebar**: Showed static trending topics (LLM Agents, MoE, RLHF, Diffusion, RAG) but these aren't clickable or dynamic
**Emotion**: 2/5 - Disappointed, feels like incomplete feature

### Step 10: Related Papers
**Action**: Clicked "Related Papers" tab on expanded paper
**Result**: Showed "Finding similar papers..." spinner, timed out after 10+ seconds
**Impact**: Can't discover paper connections or expand my reading list intelligently
**This matters because**: Following citation trails is core to literature review. If this doesn't work, I'm back to manual searching.
**Emotion**: 2/5 - Frustrated by hanging UI

### Step 11: Consistency Check
**Second search**: "flash attention optimization"
**Results**: 6 completely different papers, all highly relevant:
- "Block Sparse Flash Attention"
- "GatedFWA: Linear Flash Windowed Attention"
- "MiniKV: 2-Bit Layer-Discriminative KV Cache"
- "SageAttention2" (from advisor results)
- "Attentions Under the Microscope" (from advisor results)

**Performance**: 2188ms - much faster than first search
**Consistency**: High quality results both times, semantic understanding worked well
**Emotion**: 4/5 - Satisfied with search quality, speed improved

### Step 12: Exit Reflection
**Time spent**: ~15 minutes (would have been 10 without waiting on broken features)
**Papers discovered**: 11+ unique papers across searches, several new to me
**Success criteria met**:
- ✓ Found 2+ relevant papers I didn't know about (exceeded)
- ✓ Discovered paper with code potential (though couldn't verify due to filter issue)
- ✗ Did NOT learn something that changed my understanding - would need working deep analysis features

---

## Pain Point Assessment

### 1. Information Overload (Drowning in arXiv flood)
**Did it help?** ✓ Partially
**Evidence**: Semantic search filtered 30 papers down to 6 highly relevant ones. Research Advisor found 5 more with natural language query.
**But**: No way to save/track papers for later. No notification system for new papers in my area.
**Grade**: B- (helps discovery, doesn't help management)

### 2. Time Poverty (20-30 min max per day)
**Did it help?** ✗ Mixed
**Evidence**: When features worked (search, advisor), they were fast. But waiting 10s+ for broken features wastes precious minutes.
**Calculation**:
- First search: 8s
- Advisor query: 15s
- Waiting on related papers: 10s (wasted)
- **Total: 33s productive + 10s wasted**

**Grade**: C+ (fast when working, but reliability issues cost time)

### 3. Reproducibility Frustration (Need code)
**Did it help?** ✗ No
**Evidence**: "Has Code" filter exists but unclear if working. No GitHub stars/forks shown. No code preview.
**What I need**:
- Clear badge showing "✓ Code Available" on each paper
- Link to GitHub repo
- Stars/activity indicators
- Last commit date

**Grade**: D (filter exists but not trustworthy)

### 4. Connection Blindness (Missing relevant work)
**Did it help?** ✓ Yes
**Evidence**: Research Advisor found papers using different terminology (KV cache optimization, activation sparsity) that I wouldn't have searched for.
**Strength**: Semantic understanding bridged terminology gaps
**Grade**: A- (excellent at discovering cross-connections)

### 5. Trend Anxiety (Missing "next big thing")
**Did it help?** ✗ No
**Evidence**: Trending section completely empty. No momentum metrics. No "rising papers" indication.
**Grade**: F (feature exists but broken)

---

## Delights & Frustrations

### Delights (What Worked Well)

1. **Research Advisor Feature** ⭐
   - Natural language understanding was impressive
   - Found papers I wouldn't have discovered with keyword search
   - Follow-up action buttons (citations, alternatives, code) show smart UX thinking
   - **Would use this as primary entry point**

2. **Semantic Search Quality**
   - Both searches returned highly relevant results
   - "Smart Results" label + AI-POWERED badge set expectations correctly
   - Searched beyond exact keywords (found "KV cache" when I said "attention")

3. **Clean, Fast Interface**
   - No clutter, clear hierarchy
   - Second search was notably fast (2.2s)
   - Good use of whitespace, readable typography

4. **Generate Code Feature** (didn't test but noted)
   - Multi-agent code generation is ambitious and interesting
   - Could solve reproducibility pain if it works
   - Sets this tool apart from Papers with Code

### Frustrations (What Failed)

1. **Broken/Hanging Features** 🚫
   - Related Papers tab never loaded (10s+ timeout)
   - Trending section completely empty
   - "Contextual synthesis temporarily unavailable" in advisor
   - **Impact**: Erodes trust in tool reliability

2. **Code Availability Unclear**
   - Filter appears to do nothing
   - No visual indicators on paper cards
   - Can't trust whether code actually exists
   - **This is critical for my workflow**

3. **Missing Dates**
   - Every paper showed "Invalid Date"
   - Can't tell if papers are recent (last 6 months) or old
   - **Recency is crucial for avoiding outdated techniques**

4. **No Context/AI Analysis**
   - Paper details just show arXiv abstract
   - No "why this matters for your work" synthesis
   - No technique extraction or comparison
   - **Not much value-add over going to arXiv directly**

5. **Default State Confusion**
   - Landing page showed random CV papers
   - Why show anything before user searches?
   - **Creates false impression tool is CV-focused**

---

## Critical Issues (Blockers)

### P0: Date Information Missing
**Problem**: All papers show "Invalid Date"
**Why critical**: I specifically need papers from last 6 months. Can't make decisions without dates.
**Fix**: Parse publication dates from arXiv metadata
**Impact**: High - affects core discovery workflow

### P0: Code Filter Unreliable
**Problem**: "Has Code" filter doesn't appear to filter anything
**Why critical**: Reproducibility is non-negotiable for my work
**Fix**:
1. Verify GitHub links for each paper
2. Show clear badge on papers with code
3. Make filter actually exclude non-code papers

**Impact**: High - determines whether I can use papers

### P1: Related Papers Timeout
**Problem**: Related Papers tab hangs indefinitely
**Why critical**: Citation exploration is core literature review workflow
**Fix**: Add timeout + error handling, or remove feature until stable
**Impact**: Medium-High - blocks discovery workflow

### P1: Trending Data Empty
**Problem**: "No trending data available" in all trending sections
**Why critical**: Addresses stated pain point (trend anxiety)
**Fix**: Implement momentum/velocity metrics or remove empty feature
**Impact**: Medium - missing stated value proposition

---

## Priority Improvements

### Impact: HIGH, Effort: LOW
1. **Show paper publication dates** (fix Invalid Date bug)
2. **Add loading states with timeouts** (stop infinite spinners)
3. **Remove empty trending section** (or populate it)
4. **Fix code filter** (verify it actually filters)

### Impact: HIGH, Effort: MEDIUM
5. **Add code badges to paper cards** (GitHub link + stars + last updated)
6. **Add recency filter** (last week/month/6 months)
7. **Improve error messages** ("Contextual synthesis unavailable" - when will it be back?)

### Impact: MEDIUM, Effort: LOW
8. **Clear default state** (empty search, or explain why showing papers)
9. **Add save/bookmark feature** (can't track papers for later)
10. **Show search result count** (6 results out of how many total?)

### Impact: MEDIUM, Effort: MEDIUM
11. **AI-powered paper summaries** (extract key techniques, not just TL;DR)
12. **Visual similarity/citation graph** (replace broken related papers tab)
13. **Notification system** (alert me to new papers in my area)

### Impact: HIGH, Effort: HIGH
14. **Reading list management** (save papers, organize by project)
15. **Comparison view** (compare 2-3 papers side-by-side on techniques/results)
16. **Practical implications synthesis** ("How this applies to your mobile deployment problem")

---

## Screenshots Index

1. `01-landing-first-impression.png` - Initial page load with 30 CV papers
2. `02a-nav-generate.png` - Generate page (multi-agent code generation)
3. `03-search-waiting.png` - Search in progress state (first query)
4. `03b-research-advisor-response.png` - Research Advisor dialog with 5 papers + follow-ups
5. `04-paper-detail.png` - Expanded paper with tabs (Summary/Related/Benchmarks)
6. `05-code-filter.png` - "Has Code" filter applied (unclear effect)
7. `09-trending-empty.png` - Empty trending section ("No trending data available")
8. `10-related-papers-loading.png` - Related Papers tab stuck loading
9. `11-second-search.png` - Second search results (flash attention query)
10. `12-final-state.png` - Final view of search results

---

## Final Verdict

### Would I Bookmark This Tool?
**Yes**, but with reservations. The Research Advisor feature is genuinely useful and could save me 30+ minutes per week on paper discovery.

### Would I Return Tomorrow?
**Maybe (50/50)**. Depends on whether:
- Dates get fixed (can't use without them)
- Code filter becomes reliable (need to trust it)
- Broken features get fixed or removed (wastes time waiting)

### Would I Recommend to Colleagues?
**Not yet**. Too many broken features would damage my reputation if I recommended it. I'd wait for:
1. Date information working
2. Code indicators trustworthy
3. Hanging features fixed
4. More stability/polish

### What Would Make This a Daily Driver?
If the tool added:
1. **Reliable code indicators** (so I can filter with confidence)
2. **Date-based filtering** (last 6 months priority)
3. **Paper bookmarking** (save for weekly deep reading sessions)
4. **Email digest** (weekly summary of new papers in my area)
5. **Comparison tool** (side-by-side technique/results comparison)

Then this would replace my current workflow (arXiv + Papers with Code + Semantic Scholar).

### Time Saved vs. Current Workflow
**Current**: 30 min/day scanning arXiv, 2 hours/week deep reading
**With Atlas (if working)**: 15 min/day discovery, 2 hours/week reading
**Potential savings**: 1.75 hours/week

**But only if**:
- Features work reliably
- Code filter is trustworthy
- AI synthesis adds genuine insight

---

## Comparison to Existing Tools

### vs. Papers with Code
- **Atlas better**: Semantic search, Research Advisor, broader coverage
- **PwC better**: Reliable code links, benchmark leaderboards, community trust
- **Verdict**: Atlas has better discovery, PwC has better verification

### vs. Semantic Scholar
- **Atlas better**: Faster, cleaner UI, Research Advisor is more useful than S2's recommendations
- **S2 better**: Citations working, dates showing, more mature/stable
- **Verdict**: Atlas is more innovative but S2 is more reliable

### vs. Raw arXiv
- **Atlas better**: Pre-filtered relevance, semantic understanding, saves massive time
- **arXiv better**: Complete coverage, reliable, no broken features
- **Verdict**: Atlas is huge improvement over raw arXiv *when it works*

---

## Bottom Line: Would a Time-Pressed Postdoc Use This?

**Current state**: 6/10 - Promising but rough
**Potential**: 9/10 - Could be game-changing for discovery

**The gap**: Reliability and trust. I need to know:
- Dates are correct
- Code indicators are accurate
- Features won't waste my time hanging

**One sentence summary**: AI Paper Atlas found me 4 papers I didn't know about in 15 minutes, but broken features and missing dates prevent me from trusting it as a primary tool yet.

**Recommendation to developers**: Focus on reliability over features. A tool that does 5 things perfectly is more valuable than one that does 15 things poorly. Fix dates, fix code indicators, remove broken features, then expand.

---

## Personal Context: Why This Matters

I'm 2 years into my postdoc with 2-3 years left to establish myself. Every week I don't stay current is a week I fall behind. The difference between finding a key paper in week 1 vs. week 12 can be 3 months of wasted experiments.

If AI Paper Atlas could reliably:
1. Alert me to new relevant papers (weekly digest)
2. Show me which have working code (so I can test quickly)
3. Help me understand connections between papers (working related papers feature)

It would genuinely change my research velocity. But "could" and "would" depend on fixing the critical reliability issues first.

**My time is too valuable to spend waiting on broken features.**

---

**Assessment completed**: 2025-12-16
**Total time**: 15 minutes interaction + 25 minutes report writing
**Papers discovered**: 11+ (exceeded goal of 2+)
**Overall experience**: Promising but needs polish