import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const atlasDir = process.env.ATLAS_DATA_DIR || path.join(process.cwd(), 'data', 'derived');
const catalogPath = path.join(atlasDir, 'papers_catalog.ndjson');

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const limit = Math.min(parseInt(searchParams.get('limit') || '12', 10), 100);

  try {
    const fileHandle = await fs.open(catalogPath, 'r');
    const stream = fileHandle.createReadStream({ encoding: 'utf-8' });

    const papers: any[] = [];
    let buffer = '';

    for await (const chunk of stream) {
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        if (!line.trim()) continue;
        papers.push(JSON.parse(line));
        if (papers.length >= limit) break;
      }
      if (papers.length >= limit) break;
    }

    await fileHandle.close();

    return NextResponse.json({ papers });
  } catch (error: any) {
    const message = error?.message ?? 'Unknown error';
    return NextResponse.json(
      { error: `Failed to read atlas papers: ${message}` },
      { status: 500 },
    );
  }
}
