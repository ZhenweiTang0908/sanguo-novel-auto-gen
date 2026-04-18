import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const DATA_DIR = path.join(process.cwd(), '../data/chapters');
const META_PATH = path.join(process.cwd(), '../meta.json');

interface ChapterInfo {
  id: number;
  title: string;
  path: string;
}

interface Meta {
  current_chapter: number;
  story_title: string;
  story_subtitle: string;
}

export async function GET() {
  try {
    // 读取meta信息
    let meta: Meta = {
      current_chapter: 0,
      story_title: '疯狂三国：魔改演义',
      story_subtitle: '当罗贯中棺材板压不住的时候'
    };
    
    if (fs.existsSync(META_PATH)) {
      const metaContent = fs.readFileSync(META_PATH, 'utf-8');
      meta = JSON.parse(metaContent);
    }

    // 读取章节文件
    const chapters: ChapterInfo[] = [];
    
    if (fs.existsSync(DATA_DIR)) {
      const files = fs.readdirSync(DATA_DIR)
        .filter(f => f.endsWith('.md'))
        .sort();
      
      for (const file of files) {
        const match = file.match(/chapter_(\d+)\.md/);
        if (match) {
          const id = parseInt(match[1]);
          const filePath = path.join(DATA_DIR, file);
          const content = fs.readFileSync(filePath, 'utf-8');
          
          // 提取标题（从第一个 # 标题）
          const titleMatch = content.match(/^#\s+(.+)$/m);
          const title = titleMatch ? titleMatch[1] : `第${id}章`;
          
          chapters.push({ id, title, path: file });
        }
      }
    }

    return NextResponse.json({
      chapters,
      meta,
      totalChapters: chapters.length
    });
  } catch (error) {
    console.error('Error reading chapters:', error);
    return NextResponse.json(
      { error: 'Failed to load chapters' },
      { status: 500 }
    );
  }
}
