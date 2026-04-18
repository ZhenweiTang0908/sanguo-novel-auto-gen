import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const DATA_DIR = path.join(process.cwd(), '../data/chapters');

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const chapterId = parseInt(id);
    const filePath = path.join(DATA_DIR, `chapter_${String(chapterId).padStart(3, '0')}.md`);
    
    if (!fs.existsSync(filePath)) {
      return NextResponse.json(
        { error: 'Chapter not found' },
        { status: 404 }
      );
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    
    // 提取标题
    const titleMatch = content.match(/^#\s+(.+)$/m);
    const title = titleMatch ? titleMatch[1] : `第${chapterId}章`;
    
    // 提取纯文本内容（去除标题行）
    const lines = content.split('\n');
    const bodyLines = lines.filter((line, index) => {
      // 跳过第一行的标题
      if (index === 0 && line.startsWith('#')) return false;
      return true;
    });
    
    // 检查是否有上一章和下一章
    const prevPath = path.join(DATA_DIR, `chapter_${String(chapterId - 1).padStart(3, '0')}.md`);
    const nextPath = path.join(DATA_DIR, `chapter_${String(chapterId + 1).padStart(3, '0')}.md`);
    
    return NextResponse.json({
      id: chapterId,
      title,
      content: bodyLines.join('\n').trim(),
      hasPrev: fs.existsSync(prevPath),
      hasNext: fs.existsSync(nextPath)
    });
  } catch (error) {
    console.error('Error reading chapter:', error);
    return NextResponse.json(
      { error: 'Failed to load chapter' },
      { status: 500 }
    );
  }
}
