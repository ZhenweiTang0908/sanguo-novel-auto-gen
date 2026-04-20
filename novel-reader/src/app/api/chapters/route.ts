import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { getMetaPath, getNovelDataDir, LEGACY_DATA_DIR, LEGACY_META_PATH } from '@/lib/paths';

interface ChapterInfo {
  id: number;
  title: string;
  path: string;
}

interface Meta {
  current_chapter: number;
  story_title: string;
  story_subtitle: string;
  novel_id: string;
}

function getDefaultMeta(novelId: string): Meta {
  return {
    current_chapter: 0,
    story_title: novelId,
    story_subtitle: '',
    novel_id: novelId
  };
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const novelId = searchParams.get('novel_id') || '';
    
    let meta: Meta;
    let DATA_DIR: string;
    
    if (novelId) {
      const dataDir = getNovelDataDir(novelId);
      const metaPath = getMetaPath(novelId);
      
      if (fs.existsSync(metaPath)) {
        DATA_DIR = dataDir;
        const metaContent = fs.readFileSync(metaPath, 'utf-8');
        meta = { ...JSON.parse(metaContent), novel_id: novelId };
      } else {
        DATA_DIR = LEGACY_DATA_DIR;
        if (fs.existsSync(LEGACY_META_PATH)) {
          const metaContent = fs.readFileSync(LEGACY_META_PATH, 'utf-8');
          meta = { ...JSON.parse(metaContent), novel_id: novelId };
        } else {
          meta = getDefaultMeta(novelId);
        }
      }
    } else {
      DATA_DIR = LEGACY_DATA_DIR;
      
      if (fs.existsSync(LEGACY_META_PATH)) {
        const metaContent = fs.readFileSync(LEGACY_META_PATH, 'utf-8');
        meta = { ...JSON.parse(metaContent), novel_id: '' };
      } else {
        meta = getDefaultMeta('');
      }
    }

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