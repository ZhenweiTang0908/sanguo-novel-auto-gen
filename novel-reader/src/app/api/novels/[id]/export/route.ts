import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const NOVELS_DIR = path.join(process.cwd(), 'novels');
const LEGACY_DIR = path.join(process.cwd());

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: novelId } = await params;
    
    let meta = null;
    let chaptersDir = '';
    
    const newMetaPath = path.join(NOVELS_DIR, novelId, 'meta.json');
    
    if (fs.existsSync(newMetaPath)) {
      meta = JSON.parse(fs.readFileSync(newMetaPath, 'utf-8'));
      chaptersDir = path.join(NOVELS_DIR, novelId, 'chapters');
    } else {
      const legacyMetaPath = path.join(LEGACY_DIR, 'meta.json');
      if (fs.existsSync(legacyMetaPath)) {
        meta = JSON.parse(fs.readFileSync(legacyMetaPath, 'utf-8'));
        chaptersDir = path.join(LEGACY_DIR, 'data', 'chapters');
      }
    }
    
    if (!meta || !chaptersDir) {
      return NextResponse.json({ error: 'Novel not found' }, { status: 404 });
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
      const chapterPath = path.join(chaptersDir, `chapter_${String(i).padStart(3, '0')}.md`);
      
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