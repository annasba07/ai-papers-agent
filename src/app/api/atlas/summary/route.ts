import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const atlasDir = process.env.ATLAS_DATA_DIR || path.join(process.cwd(), 'data', 'derived');
const rawBase =
  process.env.RESEARCH_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';
const backendBase = rawBase.replace(/\/$/, '');

export async function GET() {
  if (backendBase) {
    try {
      const response = await fetch(`${backendBase}/papers/atlas/summary`);
      const payload = await response.json();
      return NextResponse.json(payload, { status: response.status });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return NextResponse.json(
        { error: `Failed to load atlas summary: ${message}` },
        { status: 502 },
      );
    }
  }

  try {
    const statsPath = path.join(atlasDir, 'build_stats.json');
    const timelinePath = path.join(atlasDir, 'category_timeline.json');
    const authorsPath = path.join(atlasDir, 'author_leaderboard.json');

    const [statsRaw, timelineRaw, authorsRaw] = await Promise.all([
      fs.readFile(statsPath, 'utf-8'),
      fs.readFile(timelinePath, 'utf-8'),
      fs.readFile(authorsPath, 'utf-8'),
    ]);

    const stats = JSON.parse(statsRaw);
    const timeline = JSON.parse(timelineRaw);
    const authors = JSON.parse(authorsRaw);

    const topCategories = Object.entries(timeline as Record<string, Array<{ month: string; count: number }>>)
      .map(([category, points]) => ({
        category,
        total: points.reduce((sum, point) => sum + point.count, 0),
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 10);

    const topAuthors = (authors as Array<{ author: string; paper_count: number }>).slice(0, 15);

    return NextResponse.json({
      stats,
      topCategories,
      topAuthors,
      timeline,
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Failed to load atlas summary: ${message}` },
      { status: 500 },
    );
  }
}
