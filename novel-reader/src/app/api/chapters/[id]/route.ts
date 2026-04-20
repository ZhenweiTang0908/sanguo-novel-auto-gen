import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { findChapterPath, getNovelDataDir, getChapterFileName } from '@/lib/paths';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const { searchParams } = new URL(request.url);
    const novelId = searchParams.get('novel_id') || '';
    
    const chapterId = parseInt(id);
    if (isNaN(chapterId) || chapterId <= 0) {
      return NextResponse.json(
        { error: 'Invalid chapter ID' },
        { status: 400 }
      );
    }

    const filePath = findChapterPath(novelId, chapterId);
    const DATA_DIR = getNovelDataDir(novelId);
    
    if (!filePath) {
      return NextResponse.json(
        { error: 'Chapter not found' },
        { status: 404 }
      );
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    
    const titleMatch = content.match(/^#\s+(.+)$/m);
    const title = titleMatch ? titleMatch[1] : `第${chapterId}章`;
    
    const lines = content.split('\n');
    const bodyLines = lines.filter((line, index) => {
      if (index === 0 && line.startsWith('#')) return false;
      return true;
    });
    
    const prevPath = path.join(DATA_DIR, getChapterFileName(chapterId - 1));
    const nextPath = path.join(DATA_DIR, getChapterFileName(chapterId + 1));
    
    return NextResponse.json({
      id: chapterId,
      title,
      content: bodyLines.join('\n').trim(),
      hasPrev: fs.existsSync(prevPath),
      hasNext: fs.existsSync(nextPath),
      novel_id: novelId
    });
  } catch (error) {
    console.error('Error reading chapter:', error);
    return NextResponse.json(
      { error: 'Failed to load chapter' },
      { status: 500 }
    );
  }
}