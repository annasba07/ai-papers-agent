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
    const topic = searchParams.get('topic') || '';
    const category = searchParams.get('category') || '';
    const difficultyLevel = searchParams.get('difficulty_level') || '';

    const params = new URLSearchParams({ limit });
    if (topic) params.set('topic', topic);
    if (category && category !== 'all') params.set('category', category);
    if (difficultyLevel && difficultyLevel !== 'all') params.set('difficulty_level', difficultyLevel);

    const response = await fetch(`${backendBase}/api/v1/discovery/learning-path?${params.toString()}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error('Failed to fetch learning path:', message);
    return NextResponse.json(
      { error: `Failed to fetch learning path: ${message}`, path: [] },
      { status: 500 }
    );
  }
}
