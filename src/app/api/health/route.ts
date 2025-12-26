import { NextResponse } from "next/server";

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const revalidate = 0;

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function GET() {
  const startTime = Date.now();
  const checks: Record<string, { status: string; latency?: number; error?: string }> = {};

  // Check backend connectivity
  try {
    const backendStart = Date.now();
    const response = await fetch(`${API_BASE}/api/v1/atlas-db/papers?limit=1`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(5000), // 5s timeout
    });

    if (response.ok) {
      const data = await response.json();
      const paperCount = Array.isArray(data) ? data.length : (data.papers?.length || 0);
      checks.backend = {
        status: paperCount > 0 ? 'healthy' : 'degraded',
        latency: Date.now() - backendStart,
      };
    } else {
      checks.backend = {
        status: 'unhealthy',
        error: `HTTP ${response.status}`,
      };
    }
  } catch (error) {
    checks.backend = {
      status: 'unhealthy',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }

  // Check Next.js API route (local route, not backend)
  try {
    const apiStart = Date.now();
    // Use localhost:3000 to test Next.js API proxy route
    const response = await fetch(
      'http://localhost:3000/api/atlas/papers?limit=1',
      {
        cache: 'no-store',
        signal: AbortSignal.timeout(5000),
      }
    );

    if (response.ok) {
      checks.nextjs_api = {
        status: 'healthy',
        latency: Date.now() - apiStart,
      };
    } else {
      checks.nextjs_api = {
        status: 'unhealthy',
        error: `HTTP ${response.status}`,
      };
    }
  } catch (error) {
    checks.nextjs_api = {
      status: 'unhealthy',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }

  // Determine overall health
  const allHealthy = Object.values(checks).every(check => check.status === 'healthy');
  const anyUnhealthy = Object.values(checks).some(check => check.status === 'unhealthy');

  const overallStatus = allHealthy ? 'healthy' : anyUnhealthy ? 'unhealthy' : 'degraded';
  const totalLatency = Date.now() - startTime;

  const response = {
    status: overallStatus,
    timestamp: new Date().toISOString(),
    latency_ms: totalLatency,
    checks,
  };

  const statusCode = overallStatus === 'healthy' ? 200 : overallStatus === 'degraded' ? 200 : 503;

  return NextResponse.json(response, { status: statusCode });
}
