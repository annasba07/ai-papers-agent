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

export const dynamic = 'force-dynamic';
export const revalidate = 0;

function extractPaperId(value: string) {
  if (!value) return '';
  if (value.includes('arxiv.org')) {
    const match = value.match(/(?:abs|pdf)\/([^?#]+)/);
    if (match) {
      return match[1];
    }
  }
  return value;
}

function parseJsonField(value: unknown) {
  if (typeof value === 'string' && value) {
    try {
      return JSON.parse(value);
    } catch {
      return value;
    }
  }
  return value;
}

export async function GET(
  _request: Request,
  { params }: { params: { paperId: string } },
) {
  const rawId = decodeURIComponent(params.paperId || '');
  const paperId = extractPaperId(rawId);

  if (backendBase) {
    try {
      const response = await fetch(`${backendBase}/api/v1/atlas-db/papers/${paperId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      const parsed = {
        ...data,
        code_repos: parseJsonField(data.code_repos),
        external_signals: parseJsonField(data.external_signals),
        deep_analysis: parseJsonField(data.deep_analysis),
        ai_analysis: parseJsonField(data.ai_analysis),
        concepts: parseJsonField(data.concepts),
      };
      return NextResponse.json(parsed, { status: 200 });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      console.error('Backend fetch failed, falling back to file:', message);
    }
  }

  try {
    const targetId = paperId;
    const baseId = paperId.split('v')[0];
    const raw = await fs.readFile(catalogPath, 'utf-8');
    for (const line of raw.split('\n')) {
      if (!line) continue;
      const paper = JSON.parse(line) as AtlasPaper;
      const recordId = paper.id || '';
      if (recordId === targetId || recordId.split('v')[0] === baseId) {
        return NextResponse.json(paper, { status: 200 });
      }
    }
    return NextResponse.json({ error: 'Paper not found' }, { status: 404 });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Failed to read atlas paper: ${message}` },
      { status: 500 },
    );
  }
}
