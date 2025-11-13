import { NextRequest, NextResponse } from 'next/server';

const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';

const backendBase = rawBase.replace(/\/$/, '');
const backendEnabled = backendBase.length > 0;

export const runtime = 'nodejs';

export async function GET() {
  return NextResponse.json({ enabled: backendEnabled });
}

export async function POST(req: NextRequest) {
  if (!backendEnabled) {
    return NextResponse.json(
      {
        error: 'Contextual analysis backend is not configured. Set RESEARCH_API_BASE_URL or NEXT_PUBLIC_API_BASE_URL.',
      },
      { status: 503 },
    );
  }

  let payload: unknown;
  try {
    payload = await req.json();
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid JSON payload', details: error instanceof Error ? error.message : String(error) },
      { status: 400 },
    );
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(`${backendBase}/papers/contextual-search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    const contentType = response.headers.get('content-type') || '';
    const payloadData = contentType.includes('application/json')
      ? await response.json()
      : await response.text();

    return NextResponse.json(payloadData, { status: response.status });
  } catch (error) {
    const message = error instanceof Error && error.name === 'AbortError'
      ? 'Contextual search request timed out.'
      : 'Failed to reach contextual analysis backend.';
    return NextResponse.json(
      { error: message, details: error instanceof Error ? error.message : String(error) },
      { status: 502 },
    );
  } finally {
    clearTimeout(timeout);
  }
}
