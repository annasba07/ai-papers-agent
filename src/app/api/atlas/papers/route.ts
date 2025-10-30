import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import type { AtlasPaper } from '@/types/Atlas';

const atlasDir = process.env.ATLAS_DATA_DIR || path.join(process.cwd(), 'data', 'derived');
const catalogPath = path.join(atlasDir, 'papers_catalog.ndjson');

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
  try {
    const { searchParams } = new URL(request.url);
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
