import ChapterReader from '@/components/ChapterReader';
import fs from 'fs';
import path from 'path';
import { notFound } from 'next/navigation';

const NOVELS_DIR = path.join(process.cwd(), 'novels');
const LEGACY_DATA_DIR = path.join(process.cwd(), 'data/chapters');

interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ novel_id?: string }>;
}

function findChapterFile(novelId: string, chapterId: number): { filePath: string | null; dataDir: string } {
  const chapterFileName = `chapter_${String(chapterId).padStart(3, '0')}.md`;
  
  if (novelId) {
    // 优先检查新位置 novels/{novelId}/chapters/
    const newPath = path.join(NOVELS_DIR, novelId, 'chapters', chapterFileName);
    if (fs.existsSync(newPath)) {
      return { filePath: newPath, dataDir: path.join(NOVELS_DIR, novelId, 'chapters') };
    }
    
    // 检查 legacy 位置 data/chapters/（crazy_sanguo等旧小说在这里）
    const legacyPath = path.join(LEGACY_DATA_DIR, chapterFileName);
    if (fs.existsSync(legacyPath)) {
      return { filePath: legacyPath, dataDir: LEGACY_DATA_DIR };
    }
    
    return { filePath: null, dataDir: LEGACY_DATA_DIR };
  }
  
  // 没有 novelId，使用 legacy
  const legacyPath = path.join(LEGACY_DATA_DIR, chapterFileName);
  return { filePath: fs.existsSync(legacyPath) ? legacyPath : null, dataDir: LEGACY_DATA_DIR };
}

async function getChapterData(chapterId: number, novelId: string) {
  const { filePath, dataDir } = findChapterFile(novelId, chapterId);
  
  if (!filePath) {
    return null;
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  
  const titleMatch = content.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1] : `第${chapterId}章`;
  
  const lines = content.split('\n');
  const bodyLines = lines.filter((line, index) => {
    if (index === 0 && line.startsWith('#')) return false;
    return true;
  });
  
  const prevPath = path.join(dataDir, `chapter_${String(chapterId - 1).padStart(3, '0')}.md`);
  const nextPath = path.join(dataDir, `chapter_${String(chapterId + 1).padStart(3, '0')}.md`);
  
  return {
    id: chapterId,
    title,
    content: bodyLines.join('\n').trim(),
    hasPrev: fs.existsSync(prevPath),
    hasNext: fs.existsSync(nextPath),
  };
}

export default async function ReadPage({ params, searchParams }: PageProps) {
  const { id } = await params;
  const { novel_id: novelId } = await searchParams;
  const chapterId = parseInt(id) || 1;

  const chapterData = await getChapterData(chapterId, novelId || '');
  
  if (!chapterData) {
    notFound();
  }

  return <ChapterReader chapterId={chapterId} />;
}

export async function generateMetadata({ params }: PageProps) {
  const { id } = await params;
  const chapterId = parseInt(id) || 1;
  
  return {
    title: `第${chapterId}章 - 疯狂三国：魔改演义`,
    description: '阅读《疯狂三国：魔改演义》最新章节',
  };
}

// 启用动态路由
export const dynamic = 'force-dynamic';
