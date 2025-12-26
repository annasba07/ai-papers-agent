import { NextResponse } from 'next/server';

const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';
const backendBase = rawBase.replace(/\/$/, '');

export const dynamic = 'force-dynamic';
export const revalidate = 0;

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
    const days = searchParams.get('days') || '90';
    const minPapers = searchParams.get('min_papers') || '3';
    const minCitations = searchParams.get('min_citations') || '3';
    const category = searchParams.get('category') || '';
    const velocityTier = searchParams.get('velocity_tier') || '';

    const params = new URLSearchParams({
      limit,
      days,
      min_papers: minPapers,
      min_citations: minCitations
    });
    if (category && category !== 'all') params.set('category', category);
    if (velocityTier) params.set('velocity_tier', velocityTier);

    const response = await fetch(`${backendBase}/api/v1/discovery/hot-topics?${params.toString()}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error('Failed to fetch hot topics:', message);
    return NextResponse.json(
      { error: `Failed to fetch hot topics: ${message}`, topics: [] },
      { status: 500 }
    );
  }
}
