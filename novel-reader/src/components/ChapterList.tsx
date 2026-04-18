'use client';

import Link from 'next/link';
import { ChapterInfo, Meta } from '@/types/novel';

interface ChapterListProps {
  chapters: ChapterInfo[];
  meta: Meta;
}

export default function ChapterList({ chapters, meta }: ChapterListProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-red-700 via-red-600 to-orange-600 text-white py-12 px-4 shadow-lg">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
            {meta.story_title}
          </h1>
          <p className="text-xl text-red-100 opacity-90">
            {meta.story_subtitle}
          </p>
          <div className="mt-6 inline-flex items-center gap-2 bg-white/20 px-4 py-2 rounded-full">
            <span className="text-2xl">📚</span>
            <span className="text-lg font-medium">
              已更新 {chapters.length} 章
            </span>
          </div>
        </div>
      </header>

      {/* Novel intro */}
      <section className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-orange-100">
          <div className="flex items-start gap-4">
            <div className="text-5xl">⚔️</div>
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">作品简介</h2>
              <p className="text-gray-600 leading-relaxed">
                当三国英雄遇上外星科技，当忠义值变成虚拟货币，当气运战争成为创业大赛……
                刘备、关羽、张飞三兄弟将如何在这个魔改的世界中杀出一条血路？
                诸葛亮口中的惊天秘密又是何人所为？
                一切尽在这部脑洞大开的《疯狂三国：魔改演义》！
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Chapter list */}
      <main className="max-w-4xl mx-auto px-4 pb-16">
        <div className="flex items-center gap-3 mb-6">
          <span className="text-2xl">📖</span>
          <h2 className="text-2xl font-bold text-gray-800">章节列表</h2>
        </div>
        
        {chapters.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-medium text-gray-600">
              小说正在创作中...
            </h3>
            <p className="text-gray-500 mt-2">
              敬请期待精彩内容
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {chapters.map((chapter, index) => (
              <Link
                key={chapter.id}
                href={`/read/${chapter.id}`}
                className="group bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-5 border border-gray-100 hover:border-orange-300 hover:-translate-y-1"
              >
                <div className="flex items-center gap-4">
                  <div className={`
                    w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold
                    ${index === 0 
                      ? 'bg-gradient-to-br from-red-500 to-orange-500 text-white' 
                      : 'bg-gray-100 text-gray-600 group-hover:bg-orange-100'}
                  `}>
                    {chapter.id}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-800 group-hover:text-orange-600 transition-colors truncate">
                      {chapter.title}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      第 {chapter.id} 章
                    </p>
                  </div>
                  <div className="text-orange-400 group-hover:text-orange-600 transition-colors">
                    <svg 
                      className="w-6 h-6" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path 
                        strokeLinecap="round" 
                        strokeLinejoin="round" 
                        strokeWidth={2} 
                        d="M9 5l7 7-7 7" 
                      />
                    </svg>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Latest chapter highlight */}
        {chapters.length > 0 && (
          <div className="mt-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl p-6 text-white">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">🔥</span>
              <span className="font-semibold">最新章节</span>
            </div>
            <Link 
              href={`/read/${chapters[chapters.length - 1].id}`}
              className="text-xl font-bold hover:underline"
            >
              {chapters[chapters.length - 1].title} →
            </Link>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-8 px-4 mt-auto">
        <div className="max-w-4xl mx-auto text-center">
          <p className="flex items-center justify-center gap-2">
            <span>Made with 💖</span>
          </p>
          <p className="text-sm mt-2">
            自动同步自 data/chapters 目录
          </p>
        </div>
      </footer>
    </div>
  );
}
