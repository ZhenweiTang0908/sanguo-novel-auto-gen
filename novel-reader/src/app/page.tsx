import ChapterList from '@/components/ChapterList';
import NovelList from '@/components/NovelList';
import { ChaptersResponse, NovelListResponse, Novel } from '@/types/novel';
import fs from 'fs';
import path from 'path';

const NOVELS_DIR = path.join(process.cwd(), 'novels');
const NOVEL_LIST_PATH = path.join(process.cwd(), 'novel-list.json');
const LEGACY_DATA_DIR = path.join(process.cwd(), 'data/chapters');
const LEGACY_META_PATH = path.join(process.cwd(), 'meta.json');

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

async function getChapters(novelId: string): Promise<ChaptersResponse> {
  try {
    let meta: Meta;
    let DATA_DIR: string;
    
    if (novelId) {
      // 优先检查新位置
      const novelDataDir = path.join(NOVELS_DIR, novelId, 'chapters');
      const novelMetaPath = path.join(NOVELS_DIR, novelId, 'meta.json');
      
      if (fs.existsSync(novelMetaPath)) {
        // 新位置存在
        DATA_DIR = novelDataDir;
        const metaContent = fs.readFileSync(novelMetaPath, 'utf-8');
        meta = { ...JSON.parse(metaContent), novel_id: novelId };
      } else {
        // 新位置不存在，检查 legacy
        DATA_DIR = LEGACY_DATA_DIR;
        if (fs.existsSync(LEGACY_META_PATH)) {
          const metaContent = fs.readFileSync(LEGACY_META_PATH, 'utf-8');
          meta = { ...JSON.parse(metaContent), novel_id: novelId };
        } else {
          meta = {
            current_chapter: 0,
            story_title: novelId,
            story_subtitle: '',
            novel_id: novelId
          };
        }
      }
    } else {
      DATA_DIR = LEGACY_DATA_DIR;
      
      if (fs.existsSync(LEGACY_META_PATH)) {
        const metaContent = fs.readFileSync(LEGACY_META_PATH, 'utf-8');
        meta = { ...JSON.parse(metaContent), novel_id: '' };
      } else {
        meta = {
          current_chapter: 0,
          story_title: '疯狂三国：魔改演义',
          story_subtitle: '当罗贯中棺材板压不住的时候',
          novel_id: ''
        };
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

    return {
      chapters,
      meta,
      totalChapters: chapters.length,
    };
  } catch (error) {
    console.error('Error reading chapters:', error);
    return {
      chapters: [],
      meta: {
        current_chapter: 0,
        story_title: 'Error loading',
        story_subtitle: '',
        novel_id: ''
      },
      totalChapters: 0,
    };
  }
}

async function getNovels(): Promise<NovelListResponse> {
  try {
    if (fs.existsSync(NOVEL_LIST_PATH)) {
      const content = fs.readFileSync(NOVEL_LIST_PATH, 'utf-8');
      const novels = JSON.parse(content) as Novel[];
      
      for (const novel of novels) {
        // 优先检查新位置
        const newMetaPath = path.join(NOVELS_DIR, novel.id, 'meta.json');
        if (fs.existsSync(newMetaPath)) {
          const meta = JSON.parse(fs.readFileSync(newMetaPath, 'utf-8'));
          novel.current_chapter = meta.current_chapter;
        }
        // 检查 legacy 位置（仅 crazy_sanguo）
        else if (novel.id === 'crazy_sanguo' && fs.existsSync(LEGACY_META_PATH)) {
          const meta = JSON.parse(fs.readFileSync(LEGACY_META_PATH, 'utf-8'));
          novel.current_chapter = meta.current_chapter;
        }
      }
      
      return { novels };
    }
    
    // novel-list.json 不存在，检查 legacy
    if (fs.existsSync(LEGACY_META_PATH)) {
      const meta = JSON.parse(fs.readFileSync(LEGACY_META_PATH, 'utf-8'));
      const novels: Novel[] = [{
        id: 'crazy_sanguo',
        title: meta.story_title || '疯狂三国：魔改演义',
        subtitle: meta.story_subtitle || '当罗贯中棺材板压不住的时候',
        created_at: new Date().toISOString(),
        current_chapter: meta.current_chapter || 0
      }];
      // 保存到 novel-list.json
      fs.writeFileSync(NOVEL_LIST_PATH, JSON.stringify(novels, null, 2), 'utf-8');
      return { novels };
    }
    
    return { novels: [] };
  } catch (error) {
    console.error('Error reading novels:', error);
    return { novels: [] };
  }
}

export const revalidate = 30;

interface HomeProps {
  searchParams: Promise<{ novel_id?: string }>;
}

export default async function Home({ searchParams }: HomeProps) {
  const params = await searchParams;
  const novelId = params.novel_id || '';
  
  if (!novelId) {
    const novelData = await getNovels();
    return <NovelList novels={novelData.novels} />;
  }
  
  const data = await getChapters(novelId);
  return <ChapterList chapters={data.chapters} meta={data.meta} />;
}
