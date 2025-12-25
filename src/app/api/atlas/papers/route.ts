import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import type { AtlasPaper } from '@/types/Atlas';

const atlasDir = process.env.ATLAS_DATA_DIR || path.join(process.cwd(), 'data', 'derived');
const catalogPath = path.join(atlasDir, 'papers_catalog.ndjson');
const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';
const backendBase = rawBase.replace(/\/$/, '');

function matchesQuery(paper: AtlasPaper, query: string) {
  const lower = query.toLowerCase();
  return (
    (paper.title && paper.title.toLowerCase().includes(lower)) ||
    (paper.abstract && paper.abstract.toLowerCase().includes(lower))
  );
}

function matchesDays(paper: AtlasPaper, days: number) {
  if (!days || days <= 0) return true;
  const published = paper.published ? new Date(paper.published) : null;
  if (!published || Number.isNaN(published.getTime())) return false;
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
  return published.getTime() >= cutoff;
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  if (backendBase) {
    try {
      // Build query params for the database API
      const limit = searchParams.get('limit') || '40';
      const offset = searchParams.get('offset') || '';
      const query = searchParams.get('query') || '';
      const category = searchParams.get('category') || 'all';
      const days = searchParams.get('days') || '';
      const orderBy = searchParams.get('order_by') || '';
      const orderDir = searchParams.get('order_dir') || '';

      // Deep analysis filters
      const hasDeepAnalysis = searchParams.get('has_deep_analysis') || '';
      const minReproducibility = searchParams.get('min_reproducibility') || '';
      const minImpactScore = searchParams.get('min_impact_score') || '';
      const difficultyLevel = searchParams.get('difficulty_level') || '';

      const params = new URLSearchParams({ limit });
      if (offset && parseInt(offset) > 0) params.set('offset', offset);
      if (query) params.set('query', query);
      if (category && category !== 'all') params.set('category', category);
      if (days && parseInt(days) > 0) params.set('days', days);
      if (orderBy) params.set('order_by', orderBy);
      if (orderDir) params.set('order_dir', orderDir);

      // Forward deep analysis filters
      if (hasDeepAnalysis === 'true') params.set('has_deep_analysis', 'true');
      if (minReproducibility) params.set('min_reproducibility', minReproducibility);
      if (minImpactScore) params.set('min_impact_score', minImpactScore);
      if (difficultyLevel) params.set('difficulty_level', difficultyLevel);

      const response = await fetch(`${backendBase}/api/v1/atlas-db/papers?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();

      // Transform to match expected frontend format
      const papers = data.papers.map((p: Record<string, unknown>) => ({
        id: p.id,
        title: p.title,
        abstract: p.abstract,
        authors: p.authors,
        published: p.published,
        category: p.category,
        link: p.link,
        concepts: p.concepts || [],
      }));

      return NextResponse.json({
        papers,
        total: data.total || papers.length,
        has_more: data.has_more,
        limit: data.limit,
        offset: data.offset,
      }, { status: 200 });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      console.error('Backend fetch failed, falling back to file:', message);
      // Fall through to file-based approach
    }
  }

  try {
    const limit = Math.min(parseInt(searchParams.get('limit') || '40', 10), 500);
    const query = searchParams.get('query')?.trim() || '';
    const category = searchParams.get('category')?.trim() || 'all';
    const days = parseInt(searchParams.get('days') || '0', 10);

    const raw = await fs.readFile(catalogPath, 'utf-8');
    const papers: AtlasPaper[] = raw
      .split('\n')
      .filter(Boolean)
      .map((line) => JSON.parse(line));

    let filtered = papers;

    if (category !== 'all') {
      filtered = filtered.filter((paper) => paper.category === category);
    }

    if (query) {
      filtered = filtered.filter((paper) => matchesQuery(paper, query));
    }

    if (!Number.isNaN(days) && days > 0) {
      filtered = filtered.filter((paper) => matchesDays(paper, days));
    }

    const limited = filtered.slice(0, limit);

    return NextResponse.json({ papers: limited });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Failed to read atlas papers: ${message}` },
      { status: 500 },
    );
  }
}
