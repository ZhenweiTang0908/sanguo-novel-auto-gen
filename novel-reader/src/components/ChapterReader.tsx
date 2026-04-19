'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { ChapterDetail } from '@/types/novel';
import { useSearchParams } from 'next/navigation';

interface ChapterReaderProps {
  chapterId: number;
}

export default function ChapterReader({ chapterId }: ChapterReaderProps) {
  const [chapter, setChapter] = useState<ChapterDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const novelId = searchParams.get('novel_id') || '';

  useEffect(() => {
    async function fetchChapter() {
      try {
        setLoading(true);
        const url = novelId 
          ? `/api/chapters/${chapterId}?novel_id=${novelId}`
          : `/api/chapters/${chapterId}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('Chapter not found');
        const data = await res.json();
        setChapter(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Load failed');
      } finally {
        setLoading(false);
      }
    }
    fetchChapter();
  }, [chapterId, novelId]);

  const buildBackUrl = () => {
    return novelId ? `/?novel_id=${novelId}` : '/';
  };

  const buildNavUrl = (targetId: number) => {
    return novelId ? `/read/${targetId}?novel_id=${novelId}` : `/read/${targetId}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <p className="text-gray-400 text-sm">加载中...</p>
        </div>
      </div>
    );
  }

  if (error || !chapter) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
        <div className="text-5xl mb-4">📭</div>
        <p className="text-gray-500 mb-4">{error || '章节不存在'}</p>
        <Link href={buildBackUrl()} className="text-orange-600 hover:underline">
          返回目录
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-2xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <Link 
              href={buildBackUrl()} 
              className="flex items-center text-gray-600 hover:text-orange-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              目录
            </Link>
            <span className="text-sm text-gray-400">
              {chapter.id}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-xl font-medium text-gray-900 mb-6">
          {chapter.title}
        </h1>

        <article className="bg-white rounded-lg border border-gray-200 p-6">
          {chapter.content.split('\n').map((paragraph, index) => {
            const trimmed = paragraph.trim();
            if (!trimmed) return <div key={index} className="h-4" />;

            if (trimmed === '---' || trimmed === '***') {
              return (
                <div key={index} className="flex items-center justify-center my-6">
                  <div className="flex-1 h-px bg-gray-200"></div>
                  <span className="mx-4 text-gray-300">·</span>
                  <div className="flex-1 h-px bg-gray-200"></div>
                </div>
              );
            }

            if (trimmed.startsWith('### ')) {
              return (
                <h3 key={index} className="text-base font-medium text-gray-800 mt-5 mb-2">
                  {trimmed.replace('### ', '')}
                </h3>
              );
            }

            if (trimmed.startsWith('## ')) {
              return (
                <h2 key={index} className="text-lg font-medium text-gray-800 mt-5 mb-2">
                  {trimmed.replace('## ', '')}
                </h2>
              );
            }

            if (trimmed.startsWith('# ')) {
              return (
                <h1 key={index} className="text-xl font-medium text-gray-900 mb-3">
                  {trimmed.replace('# ', '')}
                </h1>
              );
            }

            if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
              return (
                <p key={index} className="text-gray-700 leading-relaxed mb-3 font-medium">
                  {trimmed.replace(/\*\*/g, '')}
                </p>
              );
            }

            const processed = trimmed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

            return (
              <p
                key={index}
                className="text-gray-700 leading-relaxed mb-3 text-sm"
                dangerouslySetInnerHTML={{ __html: processed }}
              />
            );
          })}
        </article>

        <nav className="mt-6 flex items-center justify-between gap-4">
          {chapter.hasPrev ? (
            <Link
              href={buildNavUrl(chapter.id - 1)}
              className="flex items-center text-orange-600 hover:text-orange-700 transition-colors text-sm"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              上一章
            </Link>
          ) : (
            <div></div>
          )}

          <Link
            href={buildBackUrl()}
            className="text-gray-400 hover:text-gray-600 transition-colors text-xs"
          >
            目录
          </Link>

          {chapter.hasNext ? (
            <Link
              href={buildNavUrl(chapter.id + 1)}
              className="flex items-center text-orange-600 hover:text-orange-700 transition-colors text-sm"
            >
              下一章
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          ) : (
            <div></div>
          )}
        </nav>
      </main>

      <footer className="text-center py-6 text-xs text-gray-400">
        {chapter.novel_id || '疯狂三国：魔改演义'}
      </footer>
    </div>
  );
}
