'use client';

import Link from 'next/link';
import { Novel } from '@/types/novel';

export default function NovelList({ novels }: { novels: Novel[] }) {
  if (novels.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📚</div>
          <h2 className="text-xl font-medium text-gray-600 mb-2">暂无小说</h2>
          <p className="text-gray-400">生成你的第一部小说吧</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <h1 className="text-lg font-medium text-gray-900">我的小说</h1>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6">
        <div className="space-y-3">
          {novels.map((novel) => (
            <Link
              key={novel.id}
              href={`/?novel_id=${novel.id}`}
              className="block bg-white rounded-lg border border-gray-200 p-4 hover:border-orange-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <h2 className="text-base font-medium text-gray-900 truncate">
                    {novel.title}
                  </h2>
                  {novel.subtitle && (
                    <p className="text-sm text-gray-500 truncate mt-0.5">
                      {novel.subtitle}
                    </p>
                  )}
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                    <span>{novel.current_chapter || 0} 章</span>
                    <span className="text-orange-500 text-xs">阅读 ›</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>

      <footer className="text-center py-6 text-xs text-gray-400">
        小说阅读器
      </footer>
    </div>
  );
}
