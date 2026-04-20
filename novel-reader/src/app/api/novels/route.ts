import { NextResponse } from 'next/server';
import fs from 'fs';
import { getMetaPath, LEGACY_META_PATH, NOVEL_LIST_PATH } from '@/lib/paths';

interface Novel {
  id: string;
  title: string;
  subtitle: string;
  created_at: string;
  current_chapter?: number;
}

function saveNovelList(novels: Novel[]) {
  fs.writeFileSync(NOVEL_LIST_PATH, JSON.stringify(novels, null, 2), 'utf-8');
}

export async function GET() {
  try {
    let novels: Novel[] = [];
    
    if (fs.existsSync(NOVEL_LIST_PATH)) {
      const content = fs.readFileSync(NOVEL_LIST_PATH, 'utf-8');
      novels = JSON.parse(content);
    } else {
      const legacyMetaPath = LEGACY_META_PATH;
      if (fs.existsSync(legacyMetaPath)) {
        const meta = JSON.parse(fs.readFileSync(legacyMetaPath, 'utf-8'));
        const legacyNovel: Novel = {
          id: 'crazy_sanguo',
          title: meta.story_title || '疯狂三国：魔改演义',
          subtitle: meta.story_subtitle || '当罗贯中棺材板压不住的时候',
          created_at: new Date().toISOString(),
          current_chapter: meta.current_chapter || 0
        };
        novels = [legacyNovel];
        saveNovelList(novels);
      }
    }
    
    for (const novel of novels) {
      const metaPath = getMetaPath(novel.id);
      if (fs.existsSync(metaPath)) {
        const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
        novel.current_chapter = meta.current_chapter;
      } else if (novel.id === 'crazy_sanguo') {
        if (fs.existsSync(LEGACY_META_PATH)) {
          const meta = JSON.parse(fs.readFileSync(LEGACY_META_PATH, 'utf-8'));
          novel.current_chapter = meta.current_chapter;
        }
      }
    }

    return NextResponse.json({ novels });
  } catch (error) {
    console.error('Error reading novel list:', error);
    return NextResponse.json({ novels: [] });
  }
}