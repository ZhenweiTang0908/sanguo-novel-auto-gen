import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { isValidNovelId, getMetaPath, getNovelDataDir } from '@/lib/paths';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: novelId } = await params;
    
    if (!isValidNovelId(novelId)) {
      return NextResponse.json({ error: 'Invalid novel ID' }, { status: 400 });
    }
    
    const metaPath = getMetaPath(novelId);
    const dataDir = getNovelDataDir(novelId);
    
    if (!fs.existsSync(metaPath)) {
      return NextResponse.json({ error: 'Novel not found' }, { status: 404 });
    }
    
    let meta;
    try {
      meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
    } catch {
      return NextResponse.json({ error: 'Invalid meta.json' }, { status: 500 });
    }
    
    const title = meta.story_title || '未命名小说';
    const subtitle = meta.story_subtitle || '';
    const currentChapter = meta.current_chapter || 0;
    
    let markdown = `# ${title}\n\n`;
    if (subtitle) {
      markdown += `> ${subtitle}\n\n`;
    }
    markdown += `---\n\n`;
    
    for (let i = 1; i <= currentChapter; i++) {
      const chapterPath = path.join(dataDir, `chapter_${String(i).padStart(3, '0')}.md`);
      
      if (fs.existsSync(chapterPath)) {
        const content = fs.readFileSync(chapterPath, 'utf-8');
        markdown += content + '\n\n';
      }
    }
    
    const safeTitle = title.replace(/[^\w\u4e00-\u9fa5]/g, '_');
    const fileName = `${safeTitle}.md`;
    
    return new NextResponse(markdown, {
      headers: {
        'Content-Type': 'text/markdown; charset=utf-8',
        'Content-Disposition': `attachment; filename*=UTF-8''${encodeURIComponent(fileName)}`,
      },
    });
  } catch (error) {
    console.error('Error exporting novel:', error);
    return NextResponse.json({ error: 'Failed to export novel' }, { status: 500 });
  }
}