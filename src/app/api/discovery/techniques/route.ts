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
    const noveltyType = searchParams.get('novelty_type') || '';
    const category = searchParams.get('category') || '';

    const params = new URLSearchParams({ limit });
    if (noveltyType && noveltyType !== 'all') params.set('novelty_type', noveltyType);
    if (category && category !== 'all') params.set('category', category);

    const response = await fetch(`${backendBase}/discovery/techniques?${params.toString()}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error('Failed to fetch techniques:', message);
    return NextResponse.json(
      { error: `Failed to fetch techniques: ${message}`, papers: [] },
      { status: 500 }
    );
  }
}
