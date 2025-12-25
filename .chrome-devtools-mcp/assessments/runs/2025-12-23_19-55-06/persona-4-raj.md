# UX Assessment: Dr. Raj Patel (Production ML Engineer)
**Date**: December 23, 2025
**Session Duration**: 8.5 minutes (19:56:58 - 20:05:30)
**Persona**: Senior ML Engineer at FAANG, focused on production ML optimization
**Use Case**: Find quantization/pruning techniques with production-ready code and latency benchmarks

---

## Executive Summary

This tool is completely unusable for production ML work. Zero results for "model quantization production", Research Advisor crashed after 30+ seconds, and every Discovery tab failed to load. The "Has Code" filter exists but returned nothing. For someone who needs to ship optimized models this week, this is a non-starter. Sticking with Papers with Code.

**Verdict**: Would not use. Would not recommend to team. **Rating: 1/5**

---

## Session Timeline

| Time | Step | Action | Outcome | Emotion |
|------|------|--------|---------|---------|
| 19:57 | 1 | Landed on Explore page | Found Has Code filter, navigation clear | 3/5 neutral |
| 19:58 | 2 | Clicked Discovery nav | Page loaded with tabs visible | 3/5 neutral |
| 19:59 | 3 | Searched "model quantization production" | 0 results in 10 seconds | 1/5 frustrated |
| 20:00 | 3.5 | Tried Research Advisor with detailed query | Error after 30+ second timeout | 1/5 frustrated |
| 20:02 | 5 | Checked Discovery > Reproducible | Stuck on "Finding reproducible papers..." | 2/5 skeptical |
| 20:03 | 7 | Checked TL;DR tab | Stuck on "Loading summaries..." | 2/5 skeptical |
| 20:04 | 8 | Checked Techniques tab | Stuck loading, 404 errors in console | 1/5 frustrated |
| 20:05 | 9 | Applied Has Code filter on Explore | Still 0 results | 1/5 frustrated |

---

## Detailed Step Analysis

### Step 1: First Impression ⭐

**What I saw**: Landed directly on Explore page (not a marketing landing page). Clean interface with search bar, "Ask Advisor" button, and sidebar filters including "Has Code" and "High Impact (7+)".

**Initial reaction**: Decent. The filters are exactly what I need - code availability and impact scoring. No time wasted on marketing fluff.

**Screenshot**: `01-landing-first-impression.png`

---

### Step 2: Navigation Discovery ⭐⭐

**What I explored**:
- Main nav: Explore, Discovery, Reading List, Generate
- Discovery page has tabs: Overview, High Impact, TL;DR, Rising, Hot Topics, Techniques, Reproducible, Learning Path

**Observations**:
- "Reproducible" tab is promising - exactly what I need
- Navigation labels are clear
- Discovery page started loading but got stuck

**Screenshot**: `02-discovery-page.png`

---

### Step 3: Task-Based Search ❌ CRITICAL FAILURE

**Query**: "model quantization production"

**Result**: **0 results in 10,018ms (10 seconds)**

**Why this is unacceptable**:
- Quantization is a mainstream ML optimization technique
- This is literally my job - compressing models for production
- 10 seconds to return nothing is brutally slow
- Papers with Code would have returned dozens of results instantly

**Screenshot**: `03-search-zero-results.png`

**Emotion**: 1/5 - This is where the tool lost me completely.

---

### Step 3.5: Research Advisor ❌ CRITICAL FAILURE

**What I tried**: Clicked "Ask Research Advisor", entered:
> "I need to compress a production model that's too slow. Looking for quantization or pruning techniques with production-ready code and latency benchmarks."

**Result**: After 30+ seconds, received error message:
> "Sorry, I encountered an error while searching. Please try again."

**Why this is unacceptable**:
- 30 second timeout is unacceptable for any production tool
- The error gives no indication of what went wrong or how to fix it
- I explicitly asked for production metrics (latency benchmarks) and production-ready code
- This was supposed to be the fallback when basic search failed

**Screenshots**:
- `04-advisor-panel-opened.png` - Panel opened successfully
- `05-advisor-timeout.png` - Error state after timeout

**Emotion**: 1/5 - Both search methods failed. No path forward.

---

### Step 5: Code Availability Check ⚠️ PARTIAL

**What I tested**:
1. Discovery > Reproducible tab: Stuck on "Finding reproducible papers..." (never loaded)
2. Explore > Has Code filter: Works (checkbox selectable), but combined with failed search = 0 results

**Observations**:
- The "Has Code" filter EXISTS, which is good
- But if search returns 0 results, the filter is pointless
- No indication of:
  - GitHub stars/forks
  - Code quality metrics
  - Production readiness indicators
  - Framework compatibility (TensorFlow, PyTorch, ONNX)

**What I actually need**:
- Not just "has code" but "production-grade code"
- Latency benchmarks on real hardware (V100, A100, CPU)
- Memory footprint metrics
- Batch processing performance
- Quantization format support (INT8, FP16, etc.)

**Screenshots**:
- `06-reproducible-loading.png` - Reproducible tab stuck loading
- `09-has-code-filter-applied.png` - Filter applied but 0 results

**Emotion**: 2/5 - Right idea, poor execution

---

### Steps 6-9: Discovery Tabs ❌ ALL BROKEN

Tested multiple Discovery tabs:
- **TL;DR**: Stuck on "Loading summaries..."
- **Techniques**: Stuck on "Loading techniques..."
- **Reproducible**: Stuck on "Finding reproducible papers..."

**Console errors**:
```
Failed to load resource: the server responded with a status of 404 (Not Found)
Error fetching stats: JSHandle@error
```

**Screenshots**:
- `07-tldr-loading.png`
- `08-techniques-loading.png`

**Why this matters**: Every single Discovery feature is non-functional. This isn't a UX issue - the backend is broken.

**Emotion**: 1/5 - Complete system failure

---

## Pain Point Assessment

### My Pain Points (from persona):

1. **Academic Hype Filter** ❌
   - **Needed**: Quickly filter hype from practical improvements
   - **Got**: Zero results for practical queries, no content to filter
   - **Impact**: Complete failure

2. **Production Constraints** ❌
   - **Needed**: Latency, memory, batch processing metrics
   - **Got**: No papers found, no way to filter by production metrics
   - **Impact**: Useless for production work

3. **Code Quality** ❌
   - **Needed**: Production-ready implementations, not research code
   - **Got**: "Has Code" filter exists but no papers to apply it to
   - **Impact**: Cannot evaluate code quality when there's no code

4. **Time to Value** ❌
   - **Needed**: Justify reading papers to management with clear ROI
   - **Got**: Wasted 8.5 minutes, found nothing, learned nothing
   - **Impact**: Negative ROI

5. **Reproducibility** ❌
   - **Needed**: Papers with reproducible results, clear implementations
   - **Got**: Reproducible tab stuck loading forever
   - **Impact**: Core feature doesn't work

**Overall Pain Point Resolution**: 0/5 - Tool solved nothing, created frustration

---

## Production Utility Assessment

### For My Actual Job (Optimizing Production Models):

**Can I use this tool to**:
- [ ] Find quantization techniques? **NO** - 0 results
- [ ] Compare pruning methods? **NO** - 0 results
- [ ] Get latency benchmarks? **NO** - No data shown
- [ ] Find production-ready code? **NO** - Filter exists but no results
- [ ] Evaluate memory tradeoffs? **NO** - No metrics visible
- [ ] Filter by framework compatibility? **NO** - Feature doesn't exist
- [ ] Check hardware compatibility? **NO** - Feature doesn't exist
- [ ] See real-world deployments? **NO** - No production case studies

**Production readiness score**: 0/10

---

## Comparison to Papers with Code

| Feature | Papers with Code | AI Paper Atlas | Winner |
|---------|-----------------|----------------|--------|
| Search speed | <1 second | 10+ seconds | PwC |
| Search results | Hundreds | Zero | PwC |
| Code availability | Links to GitHub + stars | Filter exists, no results | PwC |
| Production metrics | Sometimes in README | Not shown | PwC |
| Leaderboards | Yes (task-specific) | Not visible | PwC |
| Benchmark results | Yes | Not visible | PwC |
| Framework filters | Yes | No | PwC |
| Hardware benchmarks | Community-provided | Not visible | PwC |
| Reproducibility | GitHub stars/forks indicate quality | Tab broken | PwC |
| Time to value | Immediate | Negative (wasted time) | PwC |

**Overall**: Papers with Code wins on every dimension. There is zero reason to switch.

---

## Code Quality Evaluation

**Cannot evaluate** - No papers returned, no code links visible.

**What I would need to see**:
- GitHub stars/forks (community validation)
- Last commit date (maintained vs abandoned)
- Framework (PyTorch, TensorFlow, JAX, ONNX)
- License (can I use this commercially?)
- Dependencies (production-friendly or research bloat?)
- Docker support (easy deployment?)
- Model checkpoints available (don't want to retrain)
- Inference optimization (TorchScript, ONNX export, TensorRT support)

**Conclusion**: Tool provides no visibility into code quality.

---

## Time-to-Value for Practitioners

**Time spent**: 8.5 minutes
**Value gained**: Zero
**Papers found**: Zero
**Techniques learned**: Zero
**Code links discovered**: Zero

**Opportunity cost**:
- Could have searched Papers with Code and found 20+ quantization papers in 2 minutes
- Could have read an abstract in this time
- Could have cloned a repo and run inference benchmark

**ROI**: Massively negative

---

## Delights and Frustrations

### Delights: ✅ (1)

1. **"Has Code" filter exists** - Right feature for practitioners, just doesn't work with broken search

### Frustrations: ❌ (8)

1. **Zero search results** - Fundamental failure for mainstream query
2. **10 second search time** - Brutally slow for returning nothing
3. **Research Advisor timeout** - 30+ seconds then error
4. **All Discovery tabs broken** - Reproducible, TL;DR, Techniques all stuck loading
5. **No production metrics** - Latency, memory, throughput completely absent
6. **No framework filters** - Can't filter by PyTorch vs TensorFlow
7. **No hardware indicators** - Don't know what GPU was used for benchmarks
8. **404 errors in console** - Backend is broken, not just UX issues

**Frustration-to-Delight Ratio**: 8:1 - Overwhelmingly negative

---

## Performance Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Search latency (keyword) | 10,018ms | Unacceptable (>3s) |
| Research Advisor latency | 30,000ms+ (timeout) | Critical failure |
| Page load time | Not measured (Explore loaded immediately) | OK |
| Discovery tab load time | Never completed | Critical failure |
| Filter response time | Instant | Good |
| Console errors | 2 (404, stats fetch error) | System broken |

---

## Critical Issues (Blockers for Production Use)

### P0 - Cannot Use Tool At All:
1. **Search returns 0 results for mainstream ML terms** - "model quantization" should return dozens of papers
2. **Research Advisor crashes** - 30+ second timeout is unacceptable
3. **All Discovery features broken** - Every tab stuck loading

### P1 - Missing Critical Features for Production:
4. **No latency metrics** - Need ms/inference, throughput, batch performance
5. **No memory metrics** - Need model size, RAM requirements, VRAM usage
6. **No framework filters** - Need to filter by PyTorch/TensorFlow/ONNX
7. **No hardware compatibility** - Need to know what GPU/CPU was used

### P2 - Code Quality Indicators Missing:
8. **No GitHub stars/forks** - Can't assess community validation
9. **No last updated date** - Can't tell if code is maintained
10. **No license info** - Can't tell if commercially usable

---

## Priority Improvements (Impact × Effort)

### High Impact, Low Effort:
1. **Fix search** - 0 results for "quantization" is a data problem, not UX (HIGH PRIORITY)
2. **Fix Research Advisor backend** - Currently timing out (HIGH PRIORITY)
3. **Fix Discovery tab loading** - 404 errors indicate missing endpoints (HIGH PRIORITY)
4. **Show GitHub stars next to code badges** - Easy to add, high value

### High Impact, Medium Effort:
5. **Add production metrics fields** - Latency, memory, throughput (structured data needed)
6. **Add framework tags** - PyTorch, TensorFlow, ONNX filters
7. **Add hardware tags** - V100, A100, CPU, M1 benchmarks
8. **Add "Production Ready" badge** - Beyond just "Has Code", indicate deployment-ready

### Medium Impact, Low Effort:
9. **Show last commit date** - Indicates if code is maintained
10. **Add license badges** - MIT, Apache, GPL visibility
11. **Show paper venue** - NeurIPS/ICML papers often more rigorous than arXiv-only

### Low Priority:
12. Learning paths, trending topics - Nice to have but not critical for practitioners

---

## Screenshots Index

1. `01-landing-first-impression.png` - Explore page on first load, Has Code filter visible
2. `02-discovery-page.png` - Discovery page with tab navigation
3. `03-search-zero-results.png` - Zero results for "model quantization production" query
4. `04-advisor-panel-opened.png` - Research Advisor sidebar opened
5. `05-advisor-timeout.png` - Research Advisor error after 30s timeout
6. `06-reproducible-loading.png` - Reproducible tab stuck on loading
7. `07-tldr-loading.png` - TL;DR tab stuck on loading
8. `08-techniques-loading.png` - Techniques tab stuck on loading
9. `09-has-code-filter-applied.png` - Has Code filter applied, still 0 results

---

## Final Verdict

### Would I use this instead of Papers with Code?

**No. Absolutely not.**

**Reasons**:
1. Search doesn't work - 0 results for my core use case
2. Research Advisor doesn't work - crashes after 30 seconds
3. Discovery features don't work - all tabs stuck loading
4. No production metrics - can't evaluate deployment feasibility
5. No code quality indicators - can't assess if implementations are usable

### Would I recommend this to my team?

**No.**

**Why**:
- Tool is fundamentally broken (not just rough edges)
- Would waste team time with no results
- Missing critical features for production ML (latency, memory, hardware compatibility)
- Papers with Code works perfectly fine for our needs

### What would it take to change my mind?

**Minimum viable**:
1. **Fix search** - Actually return papers for "quantization", "pruning", "compression"
2. **Fix Research Advisor** - Sub-5 second responses, no crashes
3. **Fix Discovery tabs** - All features must load

**To compete with Papers with Code**:
4. **Add production metrics** - Latency, memory, throughput benchmarks
5. **Add code quality indicators** - GitHub stars, maintenance status, licenses
6. **Add framework/hardware filters** - PyTorch, TensorFlow, V100, A100, CPU
7. **Add "Production Ready" curation** - Beyond just "has code"

**To actually be better**:
8. **Real-world deployment case studies** - Who's using this in production?
9. **Benchmark comparison tools** - Compare techniques side-by-side
10. **Hardware-specific leaderboards** - Best quantization for V100 vs A100 vs CPU

---

## Emotional Journey

Start: 3/5 - Neutral, willing to try
After zero results: 1/5 - Frustrated, losing patience
After Advisor crash: 1/5 - Irritated, this is broken
After Discovery tabs fail: 1/5 - Done, this is unusable
End: 1/5 - Would not recommend, going back to Papers with Code

---

## Key Quote (as Raj)

*"I have 20 minutes between meetings to find a quantization technique I can prototype this week. This tool gave me zero results in 10 seconds, crashed the AI assistant after 30 seconds, and every discovery feature is broken. Papers with Code would have had me reading a README in under a minute. This isn't rough around the edges - it's fundamentally broken. I'm out."*

---

**Assessment completed**: December 23, 2025, 20:05:30
**Total time invested**: 8.5 minutes
**Papers found**: 0
**Value generated**: 0
**Likelihood of return visit**: 0%
