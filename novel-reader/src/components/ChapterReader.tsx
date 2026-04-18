'use client';

import Link from 'next/link';
import { useEffect, useState, use } from 'react';
import { ChapterDetail } from '@/types/novel';

interface ChapterReaderProps {
  chapterId: number;
}

export default function ChapterReader({ chapterId }: ChapterReaderProps) {
  const [chapter, setChapter] = useState<ChapterDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchChapter() {
      try {
        setLoading(true);
        const res = await fetch(`/api/chapters/${chapterId}`);
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
  }, [chapterId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  if (error || !chapter) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-gray-500">
        <p>{error || 'Not found'}</p>
        <Link href="/" className="mt-4 text-orange-600 hover:underline">
          Back to list
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-gray-500 hover:text-orange-600 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <span className="text-sm text-gray-500">Chapter {chapter.id}</span>
          <div className="w-5"></div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">
          {chapter.title}
        </h1>

        <article className="prose prose-gray max-w-none">
          {chapter.content.split('\n').map((paragraph, index) => {
            const trimmed = paragraph.trim();
            if (!trimmed) return <div key={index} className="h-4" />;

            if (trimmed === '---' || trimmed === '***') {
              return (
                <div key={index} className="flex items-center justify-center my-8">
                  <div className="flex-1 h-px bg-gray-200"></div>
                  <span className="mx-4 text-gray-300">·</span>
                  <div className="flex-1 h-px bg-gray-200"></div>
                </div>
              );
            }

            if (trimmed.startsWith('### ')) {
              return (
                <h3 key={index} className="text-lg font-bold text-gray-800 mt-6 mb-3">
                  {trimmed.replace('### ', '')}
                </h3>
              );
            }

            if (trimmed.startsWith('## ')) {
              return (
                <h2 key={index} className="text-xl font-bold text-gray-800 mt-6 mb-3">
                  {trimmed.replace('## ', '')}
                </h2>
              );
            }

            if (trimmed.startsWith('# ')) {
              return (
                <h1 key={index} className="text-2xl font-bold text-gray-900 mb-4">
                  {trimmed.replace('# ', '')}
                </h1>
              );
            }

            if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
              return (
                <p key={index} className="text-gray-700 leading-relaxed mb-4 font-semibold">
                  {trimmed.replace(/\*\*/g, '')}
                </p>
              );
            }

            const processed = trimmed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

            return (
              <p
                key={index}
                className="text-gray-700 leading-relaxed mb-4"
                dangerouslySetInnerHTML={{ __html: processed }}
              />
            );
          })}
        </article>

        <nav className="mt-12 flex items-center justify-between gap-4 border-t border-gray-100 pt-8">
          {chapter.hasPrev ? (
            <Link
              href={`/read/${chapter.id - 1}`}
              className="text-orange-600 hover:text-orange-700 transition-colors"
            >
              ← Chapter {chapter.id - 1}
            </Link>
          ) : (
            <div></div>
          )}

          {chapter.hasNext ? (
            <Link
              href={`/read/${chapter.id + 1}`}
              className="text-orange-600 hover:text-orange-700 transition-colors"
            >
              Chapter {chapter.id + 1} →
            </Link>
          ) : (
            <div></div>
          )}
        </nav>
      </main>

      <footer className="border-t border-gray-200 py-8 px-4 mt-16">
        <div className="max-w-2xl mx-auto text-center text-sm text-gray-400">
          <p>疯狂三国：魔改演义</p>
        </div>
      </footer>
    </div>
  );
}