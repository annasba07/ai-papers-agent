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
    const limit = searchParams.get('limit') || '12';
    const minCitations = searchParams.get('min_citations') || '5';
    const maxMonths = searchParams.get('max_months') || '24';
    const category = searchParams.get('category') || '';
    const velocityTier = searchParams.get('velocity_tier') || '';

    const params = new URLSearchParams({ limit, min_citations: minCitations, max_months: maxMonths });
    if (category && category !== 'all') params.set('category', category);
    if (velocityTier) params.set('velocity_tier', velocityTier);

    const response = await fetch(`${backendBase}/api/v1/discovery/rising?${params.toString()}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error('Failed to fetch rising papers:', message);
    return NextResponse.json(
      { error: `Failed to fetch rising papers: ${message}`, papers: [] },
      { status: 500 }
    );
  }
}
