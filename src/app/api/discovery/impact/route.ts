import { NextResponse } from 'next/server';

const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';
const backendBase = rawBase.replace(/\/$/, '');

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  if (!backendBase) {
    return NextResponse.json(
      { error: 'Backend API not configured' },
      { status: 500 }
    );
  }

  try {
    // Forward all query params to backend
    const limit = searchParams.get('limit') || '20';
    const minScore = searchParams.get('min_score') || '7';
    const maxScore = searchParams.get('max_score') || '';
    const industryRelevance = searchParams.get('industry_relevance') || '';
    const citationPotential = searchParams.get('citation_potential') || '';
    const category = searchParams.get('category') || '';
    const days = searchParams.get('days') || '';

    const params = new URLSearchParams({ limit, min_score: minScore });
    if (maxScore) params.set('max_score', maxScore);
    if (industryRelevance) params.set('industry_relevance', industryRelevance);
    if (citationPotential) params.set('citation_potential', citationPotential);
    if (category && category !== 'all') params.set('category', category);
    if (days) params.set('days', days);

    const response = await fetch(`${backendBase}/discovery/impact?${params.toString()}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error('Failed to fetch impact papers:', message);
    return NextResponse.json(
      { error: `Failed to fetch impact papers: ${message}`, papers: [] },
      { status: 500 }
    );
  }
}
