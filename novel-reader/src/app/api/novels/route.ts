import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const NOVEL_LIST_PATH = path.join(process.cwd(), 'novel-list.json');
const NOVELS_DIR = path.join(process.cwd(), 'novels');
const LEGACY_DIR = path.join(process.cwd());

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
      // novel-list.json 不存在，检查 legacy 数据
      const legacyMetaPath = path.join(LEGACY_DIR, 'meta.json');
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
        // 保存到 novel-list.json
        saveNovelList(novels);
      }
    }
    
    // 更新每部小说的当前章节数
    for (const novel of novels) {
      // 检查新位置
      const newMetaPath = path.join(NOVELS_DIR, novel.id, 'meta.json');
      if (fs.existsSync(newMetaPath)) {
        const meta = JSON.parse(fs.readFileSync(newMetaPath, 'utf-8'));
        novel.current_chapter = meta.current_chapter;
      }
      // 如果是新小说但没有章节数，检查 legacy 位置（仅 crazy_sanguo）
      else if (novel.id === 'crazy_sanguo') {
        const legacyMetaPath = path.join(LEGACY_DIR, 'meta.json');
        if (fs.existsSync(legacyMetaPath)) {
          const meta = JSON.parse(fs.readFileSync(legacyMetaPath, 'utf-8'));
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