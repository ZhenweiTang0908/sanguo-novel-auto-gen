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
    <div className="min-h-screen relative z-10">
      {/* Header */}
      <header className="glass sticky top-0 z-50 border-b border-orange-200/50">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-3">
            <Link 
              href={homeUrl} 
              className="flex items-center gap-2 text-gray-600 hover:text-orange-600 transition-colors group"
            >
              <div className="w-9 h-9 rounded-lg bg-orange-50 flex items-center justify-center group-hover:bg-orange-100 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </div>
              <span className="text-sm font-medium">返回</span>
            </Link>
            
            <div className="flex items-center gap-3">
              {/* 导出按钮 */}
              {meta.novel_id && (
                <a
                  href={`/api/novels/${meta.novel_id}/export`}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-orange-50 border border-orange-200 text-orange-600 hover:bg-orange-100 transition-all duration-300 text-sm font-medium"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  导出
                </a>
              )}
              
              <span className="tag">{chapters.length} 章</span>
            </div>
          </div>
          
          <div>
            <h1 className="text-xl font-bold text-gray-800">{meta.story_title}</h1>
            <p className="text-sm text-gray-500 mt-1">{meta.story_subtitle}</p>
          </div>
        </div>
        <div className="h-[3px] bg-gradient-to-r from-orange-200 via-orange-400 to-orange-300"></div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        {chapters.length === 0 ? (
          <div className="text-center py-20 animate-fade-in-up">
            <div className="text-6xl mb-4 animate-float">📖</div>
            <p className="text-lg text-gray-500">暂无章节</p>
            <p className="text-sm text-gray-400 mt-1">去生成第一章吧</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {chapters.map((chapter, index) => (
              <Link
                key={chapter.id}
                href={buildReadUrl(chapter.id)}
                className="bg-white rounded-xl p-4 shadow-sm shadow-orange-100/50 hover:shadow-md hover:shadow-orange-200/50 transition-all duration-300 group animate-fade-in-up"
                style={{ animationDelay: `${index * 0.02}s`, opacity: 0 }}
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    {/* 章节编号 */}
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-100 to-orange-50 flex items-center justify-center group-hover:from-orange-200 group-hover:to-orange-100 transition-all duration-300">
                      <span className="text-orange-600 font-bold text-sm">
                        {String(chapter.id).padStart(2, '0')}
                      </span>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="text-gray-800 font-medium truncate group-hover:text-orange-600 transition-colors">
                        {chapter.title}
                      </h3>
                    </div>
                  </div>
                  
                  {/* 阅读指示 */}
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400 text-xs hidden sm:block">点击阅读</span>
                    <div className="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center group-hover:bg-orange-100 group-hover:scale-110 transition-all duration-300">
                      <svg className="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center py-10 text-gray-400 text-sm relative z-10">
        <div className="divider mb-6"></div>
        <p className="flex items-center justify-center gap-2">
          <span className="animate-pulse">✨</span>
          {meta.story_title}
          <span className="animate-pulse">✨</span>
        </p>
      </footer>
    </div>
  );
}