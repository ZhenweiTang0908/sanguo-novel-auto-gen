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
        if (!res.ok) throw new Error('章节不存在');
        const data = await res.json();
        setChapter(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载失败');
      } finally {
        setLoading(false);
      }
    }
    fetchChapter();
  }, [chapterId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">正在加载章节...</p>
        </div>
      </div>
    );
  }

  if (error || !chapter) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">😢</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">{error || '章节不存在'}</h2>
          <Link href="/" className="text-orange-600 hover:underline">
            ← 返回目录
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link 
            href="/"
            className="flex items-center gap-2 text-gray-600 hover:text-orange-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>目录</span>
          </Link>
          <h1 className="font-semibold text-gray-800 truncate max-w-xs">
            第{chapter.id}章
          </h1>
          <div className="w-16"></div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Chapter title */}
        <div className="text-center mb-8">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">
            {chapter.title}
          </h2>
          <div className="w-20 h-1 bg-gradient-to-r from-red-500 to-orange-500 mx-auto rounded-full"></div>
        </div>

        {/* Article content */}
        <article className="bg-white rounded-2xl shadow-lg p-6 md:p-10">
          <div className="prose prose-lg max-w-none">
            {chapter.content.split('\n').map((paragraph, index) => {
              const trimmed = paragraph.trim();
              if (!trimmed) return <div key={index} className="h-4" />;
              
              // Handle headings
              if (trimmed.startsWith('### ')) {
                return (
                  <h3 key={index} className="text-xl font-bold text-gray-800 mt-8 mb-4">
                    {trimmed.replace('### ', '')}
                  </h3>
                );
              }
              
              // Handle separators
              if (trimmed === '---' || trimmed === '***') {
                return (
                  <div key={index} className="flex items-center justify-center my-8">
                    <div className="w-16 h-0.5 bg-orange-300"></div>
                    <span className="mx-4 text-orange-400">✦</span>
                    <div className="w-16 h-0.5 bg-orange-300"></div>
                  </div>
                );
              }
              
              // Handle special blocks (钩子, etc.)
              if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
                return (
                  <p key={index} className="text-lg font-semibold text-orange-700 my-6 bg-orange-50 p-4 rounded-xl border-l-4 border-orange-400">
                    {trimmed.replace(/\*\*/g, '')}
                  </p>
                );
              }
              
              // Handle quotes/notes
              if (trimmed.startsWith('（') && trimmed.endsWith('）')) {
                return (
                  <p key={index} className="text-gray-600 italic my-4 pl-4 border-l-4 border-gray-300">
                    {trimmed}
                  </p>
                );
              }
              
              // Regular paragraphs
              return (
                <p key={index} className="text-gray-700 leading-relaxed mb-4">
                  {trimmed}
                </p>
              );
            })}
          </div>
        </article>

        {/* Navigation */}
        <nav className="mt-8 flex items-center justify-between gap-4">
          {chapter.hasPrev ? (
            <Link
              href={`/read/${chapter.id - 1}`}
              className="flex-1 bg-white rounded-xl shadow-md p-4 hover:shadow-lg transition-all group border border-gray-100"
            >
              <div className="flex items-center gap-2 text-gray-500 group-hover:text-orange-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span>上一章</span>
              </div>
              <p className="text-sm text-gray-400 mt-1 truncate">
                第 {chapter.id - 1} 章
              </p>
            </Link>
          ) : (
            <div className="flex-1"></div>
          )}
          
          {chapter.hasNext ? (
            <Link
              href={`/read/${chapter.id + 1}`}
              className="flex-1 bg-gradient-to-r from-red-600 to-orange-600 rounded-xl shadow-md p-4 hover:shadow-lg transition-all text-white text-right"
            >
              <div className="flex items-center justify-end gap-2">
                <span>下一章</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
              <p className="text-sm text-red-100 mt-1">
                第 {chapter.id + 1} 章
              </p>
            </Link>
          ) : (
            <div className="flex-1"></div>
          )}
        </nav>

        {/* Back to list */}
        <div className="mt-8 text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-gray-500 hover:text-orange-600 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <span>返回目录</span>
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-8 px-4 mt-16">
        <div className="max-w-4xl mx-auto text-center text-sm">
          <p>《疯狂三国：魔改演义》</p>
          <p className="mt-2">世俗搞笑风格 · 脑洞大开</p>
        </div>
      </footer>
    </div>
  );
}
