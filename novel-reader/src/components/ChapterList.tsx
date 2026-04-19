'use client';

import Link from 'next/link';
import { ChapterInfo, Meta } from '@/types/novel';

interface ChapterListProps {
  chapters: ChapterInfo[];
  meta: Meta;
}

export default function ChapterList({ chapters, meta }: ChapterListProps) {
  const buildReadUrl = (chapterId: number) => {
    if (meta.novel_id) {
      return `/read/${chapterId}?novel_id=${meta.novel_id}`;
    }
    return `/read/${chapterId}`;
  };

  const homeUrl = meta.novel_id ? `/?novel_id=${meta.novel_id}` : '/';

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link 
              href={homeUrl} 
              className="flex items-center text-gray-600 hover:text-orange-600 transition-colors"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              返回
            </Link>
            <span className="text-sm text-gray-400">{chapters.length}章</span>
          </div>
          <h1 className="text-lg font-medium text-gray-900 mt-2 truncate">
            {meta.story_title}
          </h1>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6">
        {chapters.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-5xl mb-4">📖</div>
            <p className="text-gray-500">暂无章节</p>
            <p className="text-sm text-gray-400 mt-1">去生成第一章吧</p>
          </div>
        ) : (
          <div className="space-y-2">
            {chapters.map((chapter) => (
              <Link
                key={chapter.id}
                href={buildReadUrl(chapter.id)}
                className="block bg-white rounded-lg border border-gray-200 px-4 py-3 hover:border-orange-300 hover:shadow-sm transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <span className="text-sm text-gray-400 w-8 shrink-0">
                      {chapter.id}
                    </span>
                    <span className="text-gray-800 text-sm truncate">
                      {chapter.title}
                    </span>
                  </div>
                  <span className="text-gray-300 text-xs">›</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>

      <footer className="text-center py-6 text-xs text-gray-400">
        {meta.story_title}
      </footer>
    </div>
  );
}
