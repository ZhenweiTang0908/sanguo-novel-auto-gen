import ChapterList from '@/components/ChapterList';
import NovelList from '@/components/NovelList';
import JokeList from '@/components/JokeList';
import { ChaptersResponse, NovelListResponse, Novel } from '@/types/novel';
import { JOKE_LIST_PATH } from '@/lib/paths';
import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import { getMetaPath, getNovelDataDir, LEGACY_DATA_DIR, LEGACY_META_PATH, NOVEL_LIST_PATH, getJokeCollectionMetaPath, listJokeCollections } from '@/lib/paths';

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
        const metaPath = getMetaPath(novel.id);
        if (fs.existsSync(metaPath)) {
          const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
          novel.current_chapter = meta.current_chapter;
        } else if (novel.id === 'crazy_sanguo' && fs.existsSync(LEGACY_META_PATH)) {
          const meta = JSON.parse(fs.readFileSync(LEGACY_META_PATH, 'utf-8'));
          novel.current_chapter = meta.current_chapter;
        }
      }
      
      return { novels };
    }
    
    if (fs.existsSync(LEGACY_META_PATH)) {
      const meta = JSON.parse(fs.readFileSync(LEGACY_META_PATH, 'utf-8'));
      const novels: Novel[] = [{
        id: 'crazy_sanguo',
        title: meta.story_title || '疯狂三国：魔改演义',
        subtitle: meta.story_subtitle || '当罗贯中棺材板压不住的时候',
        created_at: new Date().toISOString(),
        current_chapter: meta.current_chapter || 0
      }];
      fs.writeFileSync(NOVEL_LIST_PATH, JSON.stringify(novels, null, 2), 'utf-8');
      return { novels };
    }
    
    return { novels: [] };
  } catch (error) {
    console.error('Error reading novels:', error);
    return { novels: [] };
  }
}

async function getJokes() {
  try {
    const collectionIds = listJokeCollections();
    const collections = [];
    
    for (const id of collectionIds) {
      const metaPath = getJokeCollectionMetaPath(id);
      if (fs.existsSync(metaPath)) {
        const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
        collections.push({
          id: meta.id,
          title: meta.title,
          created_at: meta.created_at,
          current_count: meta.current_count || 0
        });
      }
    }
    
    return collections;
  } catch (error) {
    console.error('Error reading jokes:', error);
    return [];
  }
}

export const revalidate = 30;

interface HomeProps {
  searchParams: Promise<{ novel_id?: string; joke_id?: string; tab?: string }>;
}

export default async function Home({ searchParams }: HomeProps) {
  const params = await searchParams;
  const novelId = params.novel_id || '';
  const tab = params.tab || 'novels';
  
  if (tab === 'jokes') {
    const jokeData = await getJokes();
    return <JokeList collections={jokeData} />;
  }
  
  if (!novelId) {
    const novelData = await getNovels();
    return (
      <div>
        <div className="flex gap-2 px-6 pt-6 max-w-4xl mx-auto">
          <Link 
            href="/" 
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              tab !== 'jokes' 
                ? 'bg-orange-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            📖 小说
          </Link>
          <Link 
            href="/?tab=jokes" 
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              tab === 'jokes' 
                ? 'bg-yellow-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            😄 笑话集
          </Link>
        </div>
        {tab === 'jokes' ? (
          <JokeList collections={await getJokes()} />
        ) : (
          <NovelList novels={novelData.novels} />
        )}
      </div>
    );
  }
  
  const data = await getChapters(novelId);
  return <ChapterList chapters={data.chapters} meta={data.meta} />;
}