import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const atlasDir = process.env.ATLAS_DATA_DIR || path.join(process.cwd(), 'data', 'derived');

export async function GET() {
  try {
    const statsPath = path.join(atlasDir, 'build_stats.json');
    const timelinePath = path.join(atlasDir, 'category_timeline.json');
    const authorsPath = path.join(atlasDir, 'author_leaderboard.json');

    const [statsRaw, timelineRaw, authorsRaw] = await Promise.all([
      fs.readFile(statsPath, 'utf-8'),
      fs.readFile(timelinePath, 'utf-8'),
      fs.readFile(authorsPath, 'utf-8'),
    ]);

    const stats = JSON.parse(statsRaw) as {
      input_files: number;
      unique_papers: number;
      categories: string[];
      output_catalog: string;
      output_timeline: string;
      output_authors: string;
    };

    const timeline = JSON.parse(timelineRaw) as Record<string, Array<{ month: string; count: number }>>;
    const authors = JSON.parse(authorsRaw) as Array<{ author: string; paper_count: number }>;

    const topCategories = Object.entries(timeline)
      .map(([category, points]) => ({
        category,
        total: points.reduce((sum, point) => sum + point.count, 0),
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 10);

    const topAuthors = authors.slice(0, 15);

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
