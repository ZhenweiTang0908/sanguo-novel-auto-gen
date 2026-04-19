import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const NOVELS_DIR = path.join(process.cwd(), 'novels');
const LEGACY_DATA_DIR = path.join(process.cwd(), 'data/chapters');

function findChapterFile(novelId: string, chapterId: number): string | null {
  // 优先检查新位置
  if (novelId) {
    const newPath = path.join(NOVELS_DIR, novelId, 'chapters', `chapter_${String(chapterId).padStart(3, '0')}.md`);
    if (fs.existsSync(newPath)) {
      return newPath;
    }
  }
  // 检查 legacy 位置
  const legacyPath = path.join(LEGACY_DATA_DIR, `chapter_${String(chapterId).padStart(3, '0')}.md`);
  if (fs.existsSync(legacyPath)) {
    return legacyPath;
  }
  return null;
}

function findDataDir(novelId: string): string {
  if (novelId) {
    const newPath = path.join(NOVELS_DIR, novelId, 'chapters');
    if (fs.existsSync(newPath)) {
      return newPath;
    }
  }
  return LEGACY_DATA_DIR;
}

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const { searchParams } = new URL(request.url);
    const novelId = searchParams.get('novel_id') || '';
    
    const chapterId = parseInt(id);
    const filePath = findChapterFile(novelId, chapterId);
    const DATA_DIR = findDataDir(novelId);
    
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
    
    const prevPath = path.join(DATA_DIR, `chapter_${String(chapterId - 1).padStart(3, '0')}.md`);
    const nextPath = path.join(DATA_DIR, `chapter_${String(chapterId + 1).padStart(3, '0')}.md`);
    
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
