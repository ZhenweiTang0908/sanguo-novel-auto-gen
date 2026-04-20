import ChapterReader from '@/components/ChapterReader';
import { notFound } from 'next/navigation';
import { isValidNovelId } from '@/lib/paths';

interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ novel_id?: string }>;
}

export default async function ReadPage({ params, searchParams }: PageProps) {
  const { id } = await params;
  const { novel_id: novelId } = await searchParams;
  const chapterId = parseInt(id);

  if (isNaN(chapterId) || chapterId <= 0) {
    notFound();
  }

  if (novelId && !isValidNovelId(novelId)) {
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

export const dynamic = 'force-dynamic';