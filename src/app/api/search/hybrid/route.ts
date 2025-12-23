import { NextRequest, NextResponse } from 'next/server';

const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';
const backendBase = rawBase.replace(/\/$/, '');

export const runtime = 'nodejs';

interface SemanticPaper {
  id: string;
  title: string;
  summary: string;
}

interface KeywordPaper {
  id: string;
  title: string;
  abstract: string;
  authors: string[];
  published: string;
  category: string;
  link: string;
  citation_count?: number;
  concepts?: string[];
  deep_analysis?: Record<string, unknown>;
  external_signals?: Record<string, unknown>;
}

interface HybridSearchResult {
  semanticResults: KeywordPaper[];
  keywordResults: KeywordPaper[];
  totalSemantic: number;
  totalKeyword: number;
  timing: {
    semantic_ms: number;
    keyword_ms: number;
    total_ms: number;
  };
  searchMode: 'hybrid' | 'keyword_only' | 'semantic_only';
}

/**
 * Hybrid Search API
 *
 * Performs both semantic (AI-powered) and keyword (ILIKE) search in parallel,
 * then merges and deduplicates results for optimal relevance.
 *
 * Query params:
 * - query: Search query (required for semantic search)
 * - limit: Max results per source (default: 20)
 * - category: Filter by category
 * - has_deep_analysis: Only papers with deep analysis
 * - min_impact_score: Minimum impact score
 * - min_reproducibility: Minimum reproducibility score
 * - difficulty_level: Filter by difficulty
 */
export async function GET(request: NextRequest) {
  const startTime = performance.now();
  const { searchParams } = new URL(request.url);

  const query = searchParams.get('query')?.trim() || '';
  const limit = Math.min(parseInt(searchParams.get('limit') || '20', 10), 50);
  const category = searchParams.get('category');
  const hasDeepAnalysis = searchParams.get('has_deep_analysis');
  const minImpactScore = searchParams.get('min_impact_score');
  const minReproducibility = searchParams.get('min_reproducibility');
  const difficultyLevel = searchParams.get('difficulty_level');

  if (!backendBase) {
    return NextResponse.json(
      { error: 'Backend not configured. Set RESEARCH_API_BASE_URL or NEXT_PUBLIC_API_BASE_URL.' },
      { status: 503 }
    );
  }

  // Build keyword search params
  const keywordParams = new URLSearchParams({
    limit: String(limit * 2), // Fetch more for deduplication buffer
    order_by: 'published_date',
    order_dir: 'desc',
  });

  if (query) keywordParams.set('query', query);
  if (category) keywordParams.set('category', category);
  if (hasDeepAnalysis) keywordParams.set('has_deep_analysis', hasDeepAnalysis);
  if (minImpactScore) keywordParams.set('min_impact_score', minImpactScore);
  if (minReproducibility) keywordParams.set('min_reproducibility', minReproducibility);
  if (difficultyLevel) keywordParams.set('difficulty_level', difficultyLevel);

  // Prepare semantic search payload (only if we have a query)
  const semanticPayload = query ? {
    description: query,
    fast_mode: true, // Skip AI synthesis for speed (~200-500ms)
    skip_reranking: false, // Keep reranking for better relevance
  } : null;

  const timing = {
    semantic_ms: 0,
    keyword_ms: 0,
    total_ms: 0,
  };

  try {
    // Run both searches in parallel
    const semanticStart = performance.now();
    const keywordStart = performance.now();

    const [semanticResponse, keywordResponse] = await Promise.allSettled([
      // Semantic search (only if query exists)
      semanticPayload
        ? fetch(`${backendBase}/papers/contextual-search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(semanticPayload),
            signal: AbortSignal.timeout(10000), // 10s timeout
          })
        : Promise.resolve(null),

      // Keyword search
      fetch(`${backendBase}/atlas-db/papers?${keywordParams.toString()}`, {
        signal: AbortSignal.timeout(8000), // 8s timeout
      }),
    ]);

    timing.semantic_ms = performance.now() - semanticStart;
    timing.keyword_ms = performance.now() - keywordStart;

    // Process semantic results
    let semanticPapers: KeywordPaper[] = [];
    let semanticError: string | null = null;
    if (semanticResponse.status === 'fulfilled' && semanticResponse.value) {
      const response = semanticResponse.value;
      if (response.ok) {
        const data = await response.json();
        // Transform semantic results to match keyword format
        semanticPapers = (data.papers || []).map((p: SemanticPaper) => ({
          id: extractPaperId(p.id),
          title: p.title,
          abstract: p.summary,
          authors: [],
          published: '',
          category: '',
          link: p.id.startsWith('http') ? p.id : `https://arxiv.org/abs/${p.id}`,
          _source: 'semantic' as const,
          _relevanceScore: 1.0, // Semantic results are pre-ranked
        }));
      } else {
        semanticError = `Semantic search failed: ${response.status}`;
        console.warn('[Hybrid Search]', semanticError);
      }
    } else if (semanticResponse.status === 'rejected') {
      semanticError = `Semantic search error: ${semanticResponse.reason}`;
      console.warn('[Hybrid Search]', semanticError);
    }

    // Process keyword results
    let keywordPapers: KeywordPaper[] = [];
    let totalKeyword = 0;
    let keywordError: string | null = null;
    if (keywordResponse.status === 'fulfilled') {
      const response = keywordResponse.value;
      if (response.ok) {
        const data = await response.json();
        keywordPapers = (data.papers || []).map((p: KeywordPaper) => ({
          ...p,
          _source: 'keyword' as const,
        }));
        totalKeyword = data.total || keywordPapers.length;
      } else {
        keywordError = `Keyword search failed: ${response.status}`;
        console.warn('[Hybrid Search]', keywordError);
      }
    } else if (keywordResponse.status === 'rejected') {
      keywordError = `Keyword search error: ${keywordResponse.reason}`;
      console.warn('[Hybrid Search]', keywordError);
    }

    // Log if both searches failed
    if (semanticPapers.length === 0 && keywordPapers.length === 0) {
      console.error('[Hybrid Search] Both searches returned 0 results', {
        query,
        semanticError,
        keywordError,
        timing,
      });
    }

    // Deduplicate: semantic results take priority
    const seenIds = new Set(semanticPapers.map(p => p.id));
    const uniqueKeywordPapers = keywordPapers.filter(p => !seenIds.has(p.id));

    // Enrich semantic results with full data from keyword results where possible
    const keywordById = new Map(keywordPapers.map(p => [p.id, p]));
    const enrichedSemanticPapers = semanticPapers.map(sp => {
      const fullData = keywordById.get(sp.id);
      if (fullData) {
        return {
          ...fullData,
          _source: 'semantic' as const,
          _relevanceScore: 1.0,
        };
      }
      return sp;
    });

    timing.total_ms = performance.now() - startTime;

    const result: HybridSearchResult = {
      semanticResults: enrichedSemanticPapers.slice(0, limit),
      keywordResults: uniqueKeywordPapers.slice(0, limit),
      totalSemantic: semanticPapers.length,
      totalKeyword: totalKeyword,
      timing,
      searchMode: query ? 'hybrid' : 'keyword_only',
    };

    return NextResponse.json(result);

  } catch (error) {
    console.error('Hybrid search error:', error);
    timing.total_ms = performance.now() - startTime;

    return NextResponse.json(
      {
        error: 'Hybrid search failed',
        details: error instanceof Error ? error.message : String(error),
        timing,
      },
      { status: 500 }
    );
  }
}

/**
 * Extract paper ID from various formats:
 * - "https://arxiv.org/abs/2401.12345" -> "2401.12345"
 * - "2401.12345v1" -> "2401.12345"
 * - "2401.12345" -> "2401.12345"
 */
function extractPaperId(idOrUrl: string): string {
  // Extract from URL if needed
  let id = idOrUrl;
  if (id.includes('arxiv.org')) {
    const match = id.match(/(?:abs|pdf)\/(\d+\.\d+)/);
    if (match) id = match[1];
  }

  // Remove version suffix
  if (id.includes('v')) {
    id = id.split('v')[0];
  }

  return id;
}
