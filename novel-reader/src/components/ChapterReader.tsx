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
      <div className="min-h-screen flex items-center justify-center relative z-10">
        <div className="text-center animate-fade-in">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-500 text-sm">正在加载...</p>
        </div>
      </div>
    );
  }

  if (error || !chapter) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center relative z-10">
        <div className="text-6xl mb-4 animate-float">📭</div>
        <p className="text-lg text-gray-500 mb-4 animate-fade-in-up">{error || '章节不存在'}</p>
        <Link href={buildBackUrl()} className="text-orange-500 hover:text-orange-600 font-medium animate-fade-in-up delay-200">
          返回目录
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative z-10">
      {/* Header */}
      <header className="glass sticky top-0 z-50 border-b border-orange-200/50">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link 
              href={buildBackUrl()} 
              className="flex items-center gap-2 text-gray-600 hover:text-orange-600 transition-colors group"
            >
              <div className="w-9 h-9 rounded-lg bg-orange-50 flex items-center justify-center group-hover:bg-orange-100 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </div>
              <span className="text-sm font-medium">目录</span>
            </Link>
            
            <div className="px-4 py-1.5 rounded-full bg-orange-50 border border-orange-200">
              <span className="text-sm text-orange-600 font-medium">
                第 {chapter.id} 章
              </span>
            </div>
          </div>
        </div>
        <div className="h-[3px] bg-gradient-to-r from-orange-200 via-orange-400 to-orange-300"></div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-10">
        <div className="animate-fade-in-up">
          {/* 章节标题 */}
          <h1 className="text-2xl font-bold text-gray-800 text-center mb-8">
            {chapter.title}
          </h1>

          {/* 阅读内容 */}
          <article className="bg-white rounded-2xl p-8 sm:p-10 shadow-lg shadow-orange-100/50 relative">
            {/* 装饰线 */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-px bg-gradient-to-r from-transparent via-orange-300 to-transparent"></div>
            
            <div className="relative reading-content">
              {chapter.content.split('\n').map((paragraph, index) => {
                const trimmed = paragraph.trim();
                if (!trimmed) return <div key={index} className="h-5" />;

                if (trimmed === '---' || trimmed === '***') {
                  return (
                    <div key={index} className="flex items-center justify-center my-8">
                      <div className="flex-1 h-px bg-gradient-to-r from-transparent via-orange-300 to-transparent"></div>
                      <span className="mx-4 text-orange-400">✦</span>
                      <div className="flex-1 h-px bg-gradient-to-r from-transparent via-orange-300 to-transparent"></div>
                    </div>
                  );
                }

                if (trimmed.startsWith('### ')) {
                  return (
                    <h3 key={index} className="text-base font-semibold text-orange-700 mt-6 mb-2">
                      {trimmed.replace('### ', '')}
                    </h3>
                  );
                }

                if (trimmed.startsWith('## ')) {
                  return (
                    <h2 key={index} className="text-lg font-semibold text-orange-600 mt-6 mb-3">
                      {trimmed.replace('## ', '')}
                    </h2>
                  );
                }

                if (trimmed.startsWith('# ')) {
                  return (
                    <h1 key={index} className="text-xl font-bold text-gray-800 mb-4">
                      {trimmed.replace('# ', '')}
                    </h1>
                  );
                }

                if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
                  return (
                    <p key={index} className="text-center text-orange-600 font-medium my-6 py-3 border-y border-orange-200">
                      {trimmed.replace(/\*\*/g, '')}
                    </p>
                  );
                }

                const processed = trimmed.replace(/\*\*(.+?)\*\*/g, '<strong class="text-orange-600 font-semibold">$1</strong>');

                return (
                  <p
                    key={index}
                    className="text-gray-700 leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: processed }}
                  />
                );
              })}
            </div>
          </article>
        </div>

        {/* 导航 */}
        <nav className="mt-8 flex items-center justify-between gap-4 animate-fade-in-up delay-200" style={{ opacity: 0 }}>
          {chapter.hasPrev ? (
            <Link
              href={buildNavUrl(chapter.id - 1)}
              className="nav-btn flex-1"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>上一章</span>
            </Link>
          ) : (
            <div className="flex-1"></div>
          )}

          <Link
            href={buildBackUrl()}
            className="nav-btn px-6"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <span className="hidden sm:inline">目录</span>
          </Link>

          {chapter.hasNext ? (
            <Link
              href={buildNavUrl(chapter.id + 1)}
              className="nav-btn flex-1"
            >
              <span>下一章</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          ) : (
            <div className="flex-1"></div>
          )}
        </nav>
      </main>

      {/* Footer */}
      <footer className="text-center py-10 text-gray-400 text-sm relative z-10">
        <div className="divider mb-6"></div>
        <p className="flex items-center justify-center gap-2">
          <span className="animate-pulse">📖</span>
          {chapter.novel_id || '疯狂三国：魔改演义'} · 第 {chapter.id} 章
          <span className="animate-pulse">✨</span>
        </p>
      </footer>
    </div>
  );
}