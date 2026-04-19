import ChapterReader from '@/components/ChapterReader';
import fs from 'fs';
import path from 'path';
import { notFound } from 'next/navigation';

const NOVELS_DIR = path.join(process.cwd(), 'novels');

interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ novel_id?: string }>;
}

function findChapterFile(novelId: string, chapterId: number): string | null {
  if (novelId) {
    const newPath = path.join(NOVELS_DIR, novelId, 'chapters', `chapter_${String(chapterId).padStart(3, '0')}.md`);
    if (fs.existsSync(newPath)) {
      return newPath;
    }
  }
  return null;
}

function findDataDir(novelId: string): string {
  if (novelId) {
    const newPath = path.join(NOVELS_DIR, novelId, 'chapters');
    if (fs.existsSync(newPath)) {
      return newPath;
    }
  }
  return path.join(process.cwd(), 'data/chapters');
}

async function getChapterData(chapterId: number, novelId: string) {
  const filePath = findChapterFile(novelId, chapterId);
  const DATA_DIR = findDataDir(novelId);
  
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
  
  const prevPath = path.join(DATA_DIR, `chapter_${String(chapterId - 1).padStart(3, '0')}.md`);
  const nextPath = path.join(DATA_DIR, `chapter_${String(chapterId + 1).padStart(3, '0')}.md`);
  
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
