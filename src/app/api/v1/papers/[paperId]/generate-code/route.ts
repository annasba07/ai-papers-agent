import { NextRequest, NextResponse } from 'next/server';

const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';
const backendBase = rawBase.replace(/\/$/, '').replace(/\/api\/v1$/, '');

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ paperId: string }> }
) {
  if (!backendBase) {
    return NextResponse.json(
      { error: 'Backend not configured. Set RESEARCH_API_BASE_URL or NEXT_PUBLIC_API_BASE_URL.' },
      { status: 503 }
    );
  }

  const { paperId } = await params;
  const upstream = `${backendBase}/api/v1/papers/${encodeURIComponent(paperId)}/generate-code`;

  let body: string | undefined;
  try {
    const rawBody = await request.text();
    if (rawBody.trim()) {
      body = rawBody;
    }
  } catch {
    body = undefined;
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 180000);

  try {
    const response = await fetch(upstream, {
      method: 'POST',
      headers: body ? { 'Content-Type': request.headers.get('content-type') || 'application/json' } : undefined,
      body,
      signal: controller.signal,
    });

    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json')
      ? await response.json()
      : await response.text();

    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    const message = error instanceof Error && error.name === 'AbortError'
      ? 'Code generation request timed out.'
      : 'Failed to reach code generation backend.';
    return NextResponse.json(
      { error: message, details: error instanceof Error ? error.message : String(error) },
      { status: 502 },
    );
  } finally {
    clearTimeout(timeoutId);
  }
}
