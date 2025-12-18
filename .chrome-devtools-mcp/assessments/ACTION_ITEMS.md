# Action Items - UX Assessment Follow-up

**Based on**: Dr. Maya Chen persona assessment (2025-12-14)
**Priority**: P0 (Critical) → P1 (High) → P2 (Medium) → P3 (Nice-to-have)

---

## P0 - Critical (Ship This Week)

### Navigation & Discovery

- [ ] **Add Discovery to main navigation**
  - File: `src/components/GlobalNav.tsx`
  - Change: Add `{ href: "/discovery", label: "Discovery", icon: "..." }` to navItems
  - Impact: Users will discover the 8 curated tabs (TL;DR, Reproducible, Rising, etc.)
  - Effort: 15 minutes
  - Owner: Frontend

- [ ] **Add "Has Code" badge to paper cards**
  - File: `src/components/explore/PaperCard.tsx`
  - Change: Show GitHub icon + "Has Code" badge when `paper.github_urls.length > 0`
  - Impact: Surface code availability in search results
  - Effort: 30 minutes
  - Owner: Frontend

- [ ] **Add "Has Code" filter to Explore sidebar**
  - File: `src/components/explore/FilterSidebar.tsx`
  - Change: Add checkbox for `hasCode` filter (already exists in state)
  - Impact: Let users filter search results by code availability
  - Effort: 20 minutes
  - Owner: Frontend

---

## P1 - High Priority (Ship Next Sprint)

### Information Architecture

- [ ] **Add use case hint text to pages**
  - Files: `src/app/explore/page.tsx`, `src/app/discovery/page.tsx`
  - Change: Add subtitle: "Search & ask research questions" (Explore) vs "Browse trending & curated papers" (Discovery)
  - Impact: Clarify when to use which tool
  - Effort: 10 minutes
  - Owner: Frontend

### Bookmarking & Saving

- [ ] **Implement bookmark functionality**
  - Files: New `src/contexts/BookmarkContext.tsx`, update `PaperCard.tsx`
  - Change: Add bookmark icon → LocalStorage → "My Reading List" page
  - Impact: Users can build reading queues
  - Effort: 3-4 hours
  - Owner: Frontend

- [ ] **Create "My Reading List" page**
  - File: New `src/app/reading-list/page.tsx`
  - Change: Show bookmarked papers with folder organization
  - Impact: Complete the bookmark workflow
  - Effort: 2-3 hours
  - Owner: Frontend

### Trust & Transparency

- [ ] **Add impact score methodology tooltip**
  - File: `src/components/explore/PaperCard.tsx` or `src/app/discovery/page.tsx`
  - Change: Add info icon with tooltip: "Impact score (1-10) combines citation potential, novelty, and industry relevance using AI analysis."
  - Impact: Build trust in AI-generated scores
  - Effort: 30 minutes
  - Owner: Frontend

---

## P2 - Medium Priority (Next Quarter)

### Data & Performance

- [ ] **Add data coverage stats to Discovery Overview**
  - File: `src/app/discovery/page.tsx` (Overview tab)
  - Change: Show: "Covering X papers from arXiv cs.LG, cs.CL, cs.CV (2020-2024)"
  - Impact: Set user expectations about coverage
  - Effort: 1 hour (fetch from backend stats API)
  - Owner: Frontend + Backend

- [ ] **Parallelize hybrid search API calls**
  - File: `src/app/explore/page.tsx` (fetchPapers function)
  - Change: Use `Promise.all()` to call semantic and keyword APIs in parallel
  - Impact: 20-30% faster search results
  - Effort: 1 hour
  - Owner: Frontend

- [ ] **Add client-side result caching**
  - Files: Install React Query or SWR, wrap API calls
  - Change: Cache search results for 5 minutes
  - Impact: Instant results on back navigation
  - Effort: 2-3 hours
  - Owner: Frontend

### Personalization

- [ ] **Track user paper views**
  - File: New analytics/tracking module
  - Change: Log paper IDs when user expands/views details
  - Impact: Foundation for personalized recommendations
  - Effort: 2 hours
  - Owner: Frontend + Backend

- [ ] **Build recommendation engine**
  - File: New backend endpoint `/api/recommendations`
  - Change: Analyze user view history → Suggest similar papers
  - Impact: Proactive paper suggestions
  - Effort: 1-2 weeks
  - Owner: Backend + ML

- [ ] **Create personalized feed page**
  - File: New `src/app/for-you/page.tsx`
  - Change: "Papers recommended for you" based on history
  - Impact: Daily engagement driver
  - Effort: 1 week
  - Owner: Frontend + Backend

---

## P3 - Nice to Have (Backlog)

### Workflow Integration

- [ ] **Add BibTeX export**
  - File: `src/components/explore/PaperCard.tsx`
  - Change: "Export" button → Download `.bib` file
  - Impact: Integration with Zotero/Mendeley
  - Effort: 2 hours
  - Owner: Frontend

- [ ] **Email alerts for topics**
  - File: New notification system
  - Change: "Set Alert" button → Daily/weekly email digest
  - Impact: User retention via push notifications
  - Effort: 1-2 weeks
  - Owner: Backend + Infrastructure

- [ ] **Paper similarity graph visualization**
  - File: New `src/components/PaperGraph.tsx`
  - Change: D3.js citation network visualization
  - Impact: Explore paper relationships visually
  - Effort: 2 weeks
  - Owner: Frontend

- [ ] **Compare papers side-by-side**
  - File: New `src/app/compare/page.tsx`
  - Change: Checkbox to select papers → Compare view
  - Impact: Evaluate multiple approaches
  - Effort: 1 week
  - Owner: Frontend

### Accessibility

- [ ] **Add focus management to modals**
  - File: `src/components/explore/ResearchAdvisor.tsx`
  - Change: Focus trap in advisor panel, return focus on close
  - Impact: Better keyboard navigation
  - Effort: 1 hour
  - Owner: Frontend

- [ ] **Add screen reader announcements**
  - File: All search/filter components
  - Change: Announce "X results found" when results load
  - Impact: Screen reader accessibility
  - Effort: 2 hours
  - Owner: Frontend

---

## Quick Wins (Do These Now - <1 Hour Each)

- [ ] Add Discovery to main nav (15 min)
- [ ] Add "Has Code" filter checkbox (20 min)
- [ ] Add impact score tooltip (30 min)
- [ ] Add use case hint text (10 min)
- [ ] Add "Has Code" badge to paper cards (30 min)

**Total quick wins time: ~2 hours = ship today!**

---

## Effort Summary

| Priority | Items | Total Effort |
|----------|-------|--------------|
| P0 (Critical) | 3 | ~1 hour |
| P1 (High) | 4 | ~8 hours |
| P2 (Medium) | 6 | ~3-4 weeks |
| P3 (Nice-to-have) | 6 | ~6-8 weeks |

**Critical path to 9/10 rating**: Ship P0 + P1 (total ~9 hours of work)

---

## Success Metrics

After implementing P0 + P1, track:

1. **Feature Discovery Rate**
   - Before: Users only see Explore page
   - Target: 80% of users visit Discovery tabs within first session

2. **Code Filter Usage**
   - Track % of searches using "Has Code" filter
   - Target: 30% of searches (reproducibility is top concern)

3. **Bookmark Adoption**
   - Track % of users who save at least 1 paper
   - Target: 50% within first week

4. **Return Rate**
   - Track 7-day return rate
   - Current: Unknown
   - Target: 60% (daily use tool)

5. **Research Advisor Engagement**
   - Track % of sessions using Research Advisor
   - Target: 40% (killer feature)

---

## Release Plan

### Sprint 1 (This Week)
- Ship all P0 items (1 hour)
- QA testing
- Deploy to production

### Sprint 2 (Next 2 Weeks)
- Implement bookmarking (5 hours)
- Add tooltips and hints (1 hour)
- Create Reading List page (2 hours)
- Deploy

### Month 2
- Parallelize search APIs
- Add data coverage stats
- Start personalization tracking

### Quarter 2
- Build recommendation engine
- Email alerts system
- Advanced features (graph viz, compare)

---

## Notes

- **Philosophy**: Ship P0 fixes immediately. They're low-effort, high-impact.
- **User feedback**: Re-test with Maya Chen persona after P0+P1 ships. Target: 9/10 rating.
- **Analytics**: Instrument everything. Data-driven decisions for P2+P3 prioritization.
- **Accessibility**: Don't defer P3 accessibility items. They should be P1.

---

*Generated from UX assessment: 2025-12-14*
*Next review: After P0+P1 deployment*
