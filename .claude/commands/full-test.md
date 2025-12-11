---
allowed-tools: Bash(curl:*), Bash(jq:*), Bash(time:*)
argument-hint: [section-number]
description: Comprehensive API test suite for AI Papers Research Agent
---

# AI Papers Research Agent - Test Suite

Run systematic tests for all API endpoints. Use `$ARGUMENTS` to run specific section (1-15) or run all if empty.

## Prerequisites

Verify services are running before testing:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## Execution Strategy

1. **If $ARGUMENTS provided**: Run only that section
2. **If no arguments**: Run sections sequentially, stop on critical failures
3. **Log all failures** with endpoint, status code, and response snippet
4. **Report summary** at end with pass/fail counts

---

## Section 1: Health Checks

```bash
# 1.1 Backend health
curl -sf http://localhost:8000/health | jq -e '.status' || echo "FAIL: Backend unhealthy"

# 1.2 API root accessible
curl -sf http://localhost:8000/api/v1 | jq . || echo "FAIL: API root inaccessible"
```

**Success criteria**: Both return 200, health shows "healthy"

---

## Section 2: Ingestion Endpoints

```bash
# 2.1 List categories
curl -sf "http://localhost:8000/api/v1/ingestion/categories" | jq -e 'length > 0'

# 2.2 Check status
curl -sf "http://localhost:8000/api/v1/ingestion/status" | jq .

# 2.3 Scheduler status
curl -sf "http://localhost:8000/api/v1/ingestion/scheduler" | jq .

# 2.4 Trigger sync ingestion (small batch for testing)
curl -sf -X POST "http://localhost:8000/api/v1/ingestion/trigger-sync" \
  -H "Content-Type: application/json" \
  -d '{"categories": ["cs.LG"], "days": 1, "max_papers": 2}' | jq -e '.papers_ingested >= 0'
```

**Success criteria**: Categories array non-empty, status returns object, ingestion completes

---

## Section 3: Papers Search Endpoints

```bash
# 3.1 Embedding caches
curl -sf "http://localhost:8000/api/v1/papers/embedding-caches" | jq .

# 3.2 Atlas papers with filters
curl -sf "http://localhost:8000/api/v1/papers/atlas/papers?limit=5&category=cs.LG" | jq -e 'type == "array"'

# 3.3 Atlas summary
curl -sf "http://localhost:8000/api/v1/papers/atlas/summary" | jq -e '.total_papers'

# 3.4 Full-text search
curl -sf -X POST "http://localhost:8000/api/v1/papers/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "transformer attention", "limit": 5}' | jq -e 'length >= 0'

# 3.5 Contextual search (AI-powered)
curl -sf -X POST "http://localhost:8000/api/v1/papers/contextual-search" \
  -H "Content-Type: application/json" \
  -d '{"description": "efficient mobile deployment", "top_k": 5}' | jq .
```

**Success criteria**: All return valid JSON, atlas summary has total_papers field

---

## Section 4: Discovery Endpoints - Core

```bash
# 4.1 Discovery stats
curl -sf "http://localhost:8000/api/v1/discovery/stats" | jq .

# 4.2 High-impact papers
curl -sf "http://localhost:8000/api/v1/discovery/impact?min_score=7&limit=5" | jq -e 'type == "array"'

# 4.3 TLDR summaries
curl -sf "http://localhost:8000/api/v1/discovery/tldr?days=30&limit=5" | jq .

# 4.4 Learning path
curl -sf "http://localhost:8000/api/v1/discovery/learning-path?difficulty_level=beginner&limit=5" | jq .
```

---

## Section 5: Discovery Endpoints - Advanced

```bash
# 5.1 Techniques by novelty type
for type in architectural algorithmic theoretical empirical; do
  curl -sf "http://localhost:8000/api/v1/discovery/techniques?novelty_type=$type&limit=3" | jq -e 'type == "array"' || echo "FAIL: techniques/$type"
done

# 5.2 Rising papers
curl -sf "http://localhost:8000/api/v1/discovery/rising?min_citations=5&limit=5" | jq .

# 5.3 Reproducible papers
curl -sf "http://localhost:8000/api/v1/discovery/reproducible?code_availability=true&limit=5" | jq .

# 5.4 Practical applications
curl -sf "http://localhost:8000/api/v1/discovery/practical?industry_relevance=high&limit=5" | jq .

# 5.5 Hot topics
curl -sf "http://localhost:8000/api/v1/discovery/hot-topics?days=30&limit=10" | jq .
```

---

## Section 6: Trends Endpoints

```bash
# 6.1 Hot topics with time windows
curl -sf "http://localhost:8000/api/v1/trends/hot-topics?window_days=14&top_k=10" | jq .

# 6.2 Rising techniques
curl -sf "http://localhost:8000/api/v1/trends/rising-techniques?days=60" | jq .

# 6.3 Active authors
curl -sf "http://localhost:8000/api/v1/trends/active-authors?days=30&limit=10" | jq .

# 6.4 Emerging areas
curl -sf "http://localhost:8000/api/v1/trends/emerging-areas?days=60&min_papers=3" | jq .
```

---

## Section 7: Knowledge Graph Endpoints

```bash
# 7.1 Concepts exploration
curl -sf "http://localhost:8000/api/v1/knowledge-graph/concepts?query=attention" | jq .

# 7.2 Trending concepts
curl -sf "http://localhost:8000/api/v1/knowledge-graph/concepts?trending=true" | jq .

# 7.3 Latest research by category
curl -sf "http://localhost:8000/api/v1/knowledge-graph/latest-research?category=cs.LG&days=7" | jq .

# 7.4 Benchmarks
curl -sf "http://localhost:8000/api/v1/knowledge-graph/benchmarks" | jq .
```

---

## Section 8: Atlas Database Endpoints

```bash
# 8.1 Papers with comprehensive filters
curl -sf "http://localhost:8000/api/v1/atlas-db/papers?limit=5&category=cs.LG&days=30&has_deep_analysis=true" | jq -e 'type == "array"'

# 8.2 Pagination test
curl -sf "http://localhost:8000/api/v1/atlas-db/papers?limit=5&offset=5" | jq -e 'type == "array"'

# 8.3 Order by citations
curl -sf "http://localhost:8000/api/v1/atlas-db/papers?limit=5&order_by=citation_count" | jq .

# 8.4 Concepts lookup
curl -sf "http://localhost:8000/api/v1/atlas-db/concepts?query=neural&limit=10" | jq .

# 8.5 Database summary
curl -sf "http://localhost:8000/api/v1/atlas-db/summary" | jq -e '.total_papers > 0'

# 8.6 Categories with counts
curl -sf "http://localhost:8000/api/v1/atlas-db/categories" | jq .

# 8.7 Techniques
curl -sf "http://localhost:8000/api/v1/atlas-db/techniques?limit=10" | jq .

# 8.8 Timeline (daily granularity)
curl -sf "http://localhost:8000/api/v1/atlas-db/timeline?days=30&granularity=day" | jq .
```

---

## Section 9: Enrichment Endpoints

```bash
# 9.1 Tier 1 enrichment count
curl -sf "http://localhost:8000/api/v1/enrichment/count" | jq .

# 9.2 Tier 1 status
curl -sf "http://localhost:8000/api/v1/enrichment/status" | jq .

# 9.3 Deep enrichment count
curl -sf "http://localhost:8000/api/v1/enrichment/deep/count" | jq .

# 9.4 Deep enrichment status
curl -sf "http://localhost:8000/api/v1/enrichment/deep/status" | jq .

# 9.5 Citation enrichment count
curl -sf "http://localhost:8000/api/v1/enrichment/citations/count" | jq .

# 9.6 Citation enrichment status
curl -sf "http://localhost:8000/api/v1/enrichment/citations/status" | jq .
```

**Note**: Trigger endpoints (POST) skipped by default to avoid rate limits. Run manually if needed.

---

## Section 10: Agent Memory Endpoints

```bash
# 10.1 Agent stats
curl -sf "http://localhost:8000/api/v1/agent-memory/stats" | jq .

# 10.2 Reflections
curl -sf "http://localhost:8000/api/v1/agent-memory/reflections" | jq .

# 10.3 Patterns
curl -sf "http://localhost:8000/api/v1/agent-memory/patterns" | jq .

# 10.4 Memory summary
curl -sf "http://localhost:8000/api/v1/agent-memory/summary" | jq .
```

---

## Section 11: Frontend Accessibility

```bash
# Test all frontend routes return 200
ROUTES="/ /atlas-explore /trends /generate /discovery /discovery/impact /discovery/tldr /discovery/learning-path /discovery/techniques /discovery/rising /discovery/reproducible /discovery/practical /discovery/hot-topics"

for route in $ROUTES; do
  STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:3000$route")
  [ "$STATUS" = "200" ] && echo "✓ $route" || echo "✗ $route ($STATUS)"
done
```

---

## Section 12: Database Integrity

```bash
# 12.1 Verify paper count > 0
PAPERS=$(curl -sf "http://localhost:8000/api/v1/atlas-db/summary" | jq -r '.total_papers')
[ "$PAPERS" -gt 0 ] && echo "✓ Papers exist: $PAPERS" || echo "✗ No papers in database"

# 12.2 Verify enrichment coverage
curl -sf "http://localhost:8000/api/v1/enrichment/count" | jq '{total: .total_count, enriched: .enriched_count, ratio: (.enriched_count / .total_count * 100 | floor)}'
```

---

## Section 13: Error Handling

```bash
# 13.1 Invalid paper ID
curl -sf "http://localhost:8000/api/v1/papers/similar/INVALID_ID_12345" && echo "FAIL: Should 404" || echo "✓ Correctly rejected invalid ID"

# 13.2 Empty search query
curl -sf -X POST "http://localhost:8000/api/v1/papers/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "", "limit": 10}' | jq .

# 13.3 Malformed JSON
curl -s -X POST "http://localhost:8000/api/v1/papers/search" \
  -H "Content-Type: application/json" \
  -d 'not valid json' -w "\nHTTP: %{http_code}" | tail -1 | grep -q "422" && echo "✓ Rejects malformed JSON" || echo "✗ Should return 422"
```

---

## Section 14: Performance Benchmarks

```bash
# 14.1 Search response time (target: <2s)
time curl -sf -X POST "http://localhost:8000/api/v1/papers/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "transformer", "limit": 20}' > /dev/null

# 14.2 Contextual search time (target: <5s)
time curl -sf -X POST "http://localhost:8000/api/v1/papers/contextual-search" \
  -H "Content-Type: application/json" \
  -d '{"description": "efficient attention mechanisms", "top_k": 20}' > /dev/null

# 14.3 Atlas papers time (target: <1s)
time curl -sf "http://localhost:8000/api/v1/atlas-db/papers?limit=100" > /dev/null
```

---

## Section 15: Integration Tests

```bash
# 15.1 arXiv integration (via ingestion)
curl -sf "http://localhost:8000/api/v1/ingestion/status" | jq -e '.last_run' && echo "✓ arXiv integration working"

# 15.2 OpenAI integration (via contextual search)
curl -sf -X POST "http://localhost:8000/api/v1/papers/contextual-search" \
  -H "Content-Type: application/json" \
  -d '{"description": "test query", "top_k": 1}' | jq -e '.[0].similarity_score' && echo "✓ Embedding service working"

# 15.3 Citation service
curl -sf "http://localhost:8000/api/v1/enrichment/citations/count" | jq -e '.citation_enriched_count >= 0' && echo "✓ Citation service configured"
```

---

## Quick Summary Script

Run this for a fast health check:

```bash
echo "=== Quick Health Check ==="
curl -sf http://localhost:8000/health | jq -r '.status // "FAIL"'
curl -sf "http://localhost:8000/api/v1/atlas-db/summary" | jq '{papers: .total_papers, enriched_t1: .tier1_enriched, enriched_t2: .tier2_enriched}'
echo "Frontend:" && curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:3000/
```

---

## Test Execution Notes

1. **Run in order**: Sections 1-2 first to ensure services and data exist
2. **Rate limits**: Add 1-2s delay between external API tests
3. **Paper IDs**: For similarity/citation tests, first fetch a valid ID from atlas-db/papers
4. **Timeouts**: Set 30s timeout for enrichment operations
5. **Failures**: Empty results are acceptable for fresh databases; 500 errors are not

## Success Criteria

- ✓ All GET endpoints return 200 status
- ✓ All POST endpoints return 200/201/202 status  
- ✓ No 500 Internal Server Errors
- ✓ Response times within benchmarks
- ✓ Frontend pages accessible
- ✓ Database has papers (if previously ingested)
