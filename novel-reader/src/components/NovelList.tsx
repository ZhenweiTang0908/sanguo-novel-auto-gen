'use client';

import Link from 'next/link';
import { Novel } from '@/types/novel';

export default function NovelList({ novels }: { novels: Novel[] }) {
  if (novels.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center relative z-10">
        <div className="text-center animate-fade-in-up">
          <div className="text-7xl mb-5 animate-float">📚</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">书库空空</h2>
          <p className="text-gray-500">创作你的第一部小说吧</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative z-10">
      {/* Header */}
      <header className="glass sticky top-0 z-50 border-b border-orange-200/50">
        <div className="max-w-4xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-orange-400 to-orange-500 flex items-center justify-center shadow-lg shadow-orange-200/50">
                <span className="text-2xl">📖</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">我的书库</h1>
                <p className="text-sm text-gray-500">{novels.length} 部作品</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="tag">共 {novels.reduce((acc, n) => acc + (n.current_chapter || 0), 0)} 章</span>
            </div>
          </div>
        </div>
        <div className="h-[3px] bg-gradient-to-r from-orange-200 via-orange-400 to-orange-300"></div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-10">
        <div className="grid gap-5">
          {novels.map((novel, index) => (
            <Link
              key={novel.id}
              href={`/?novel_id=${novel.id}`}
              className="animate-fade-in-up"
              style={{ animationDelay: `${index * 0.1}s`, opacity: 0 }}
            >
              <div className="bg-white rounded-2xl p-6 shadow-md shadow-orange-100/50 card-hover relative overflow-hidden group">
                {/* 背景装饰 */}
                <div className="absolute inset-0 bg-gradient-to-br from-orange-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="absolute -top-16 -right-16 w-32 h-32 bg-orange-100/30 rounded-full blur-2xl group-hover:bg-orange-200/40 transition-all duration-500"></div>
                
                <div className="relative flex items-start justify-between gap-6">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-lg font-bold text-gray-800 group-hover:text-orange-600 transition-colors">
                        {novel.title}
                      </h2>
                      <span className="tag">
                        {novel.current_chapter || 0} 章
                      </span>
                    </div>
                    {novel.subtitle && (
                      <p className="text-gray-500 text-sm mb-3 line-clamp-1">
                        {novel.subtitle}
                      </p>
                    )}
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        更新于 {novel.last_updated ? new Date(novel.last_updated).toLocaleDateString('zh-CN') : '未知'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    {/* 阅读进度指示 */}
                    <div className="hidden sm:flex flex-col items-end gap-1">
                      <div className="w-20 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-orange-400 to-orange-500 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, (novel.current_chapter || 0) * 2)}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-400">{novel.current_chapter || 0} 章已读</span>
                    </div>
                    
                    {/* 箭头 */}
                    <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center group-hover:bg-orange-100 group-hover:scale-110 transition-all duration-300">
                      <svg className="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-10 text-gray-400 text-sm relative z-10">
        <div className="divider mb-6"></div>
        <p className="flex items-center justify-center gap-2">
          <span className="animate-pulse">✨</span>
          用爱发电 · 疯狂三国：魔改演义
          <span className="animate-pulse">✨</span>
        </p>
      </footer>
    </div>
  );
}