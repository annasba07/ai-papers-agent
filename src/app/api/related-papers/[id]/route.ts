import { NextResponse } from 'next/server';

const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';
const backendBase = rawBase.replace(/\/$/, '');

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  if (!backendBase) {
    return NextResponse.json(
      { error: 'Backend API not configured' },
      { status: 500 }
    );
  }

  try {
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get('limit') || '10';
    const minSimilarity = searchParams.get('min_similarity') || '0.7';

    const queryParams = new URLSearchParams({ limit, min_similarity: minSimilarity });

    const response = await fetch(
      `${backendBase}/api/v1/knowledge-graph/papers/${id}/similar?${queryParams.toString()}`
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    return NextResponse.json({ similar_papers: data }, { status: 200 });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error('Failed to fetch related papers:', message);
    return NextResponse.json(
      { error: `Failed to fetch related papers: ${message}`, similar_papers: [] },
      { status: 500 }
    );
  }
}
