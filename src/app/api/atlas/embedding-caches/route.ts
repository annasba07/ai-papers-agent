import { NextResponse } from 'next/server';

const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';

const backendBase = rawBase.replace(/\/$/, '');

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET() {
  if (!backendBase) {
    return NextResponse.json([]);
  }

  try {
    const response = await fetch(`${backendBase}/api/v1/papers/embedding-caches`);
    const payload = await response.json();
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        error: 'Failed to fetch embedding caches.',
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}
