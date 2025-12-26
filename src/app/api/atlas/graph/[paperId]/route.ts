import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ paperId: string }> }
) {
  const { paperId } = await params;
  const searchParams = request.nextUrl.searchParams;

  const max_depth = searchParams.get('max_depth') || '2';
  const neighbors_per_node = searchParams.get('neighbors_per_node') || '5';
  const min_similarity = searchParams.get('min_similarity') || '0.5';

  try {
    const queryParams = new URLSearchParams({
      max_depth,
      neighbors_per_node,
      min_similarity,
    });

    const response = await fetch(
      `${API_BASE}/papers/graph/${encodeURIComponent(paperId)}?${queryParams}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      return NextResponse.json(
        { error: error.detail || 'Failed to fetch graph' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Graph fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch similarity graph' },
      { status: 500 }
    );
  }
}
