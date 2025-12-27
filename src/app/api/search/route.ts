import { NextRequest, NextResponse } from 'next/server';

const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';
const backendBase = rawBase.replace(/\/$/, '').replace(/\/api\/v1$/, '');

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const revalidate = 0;

async function proxySearch(request: NextRequest, init?: RequestInit) {
  if (!backendBase) {
    return NextResponse.json(
      { error: 'Backend not configured. Set RESEARCH_API_BASE_URL or NEXT_PUBLIC_API_BASE_URL.' },
      { status: 503 }
    );
  }

  const url = new URL(request.url);
  const upstream = `${backendBase}/api/v1/search${url.search}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 12000);

  try {
    const response = await fetch(upstream, { signal: controller.signal, ...init });
    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json')
      ? await response.json()
      : await response.text();
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    const message = error instanceof Error && error.name === 'AbortError'
      ? 'Search request timed out.'
      : 'Failed to reach search backend.';
    return NextResponse.json(
      { error: message, details: error instanceof Error ? error.message : String(error) },
      { status: 502 },
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function GET(request: NextRequest) {
  return proxySearch(request, { method: 'GET' });
}

export async function POST(request: NextRequest) {
  let payload: unknown;
  try {
    payload = await request.json();
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid JSON payload', details: error instanceof Error ? error.message : String(error) },
      { status: 400 },
    );
  }

  return proxySearch(request, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}
