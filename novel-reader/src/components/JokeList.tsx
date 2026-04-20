'use client';

import Link from 'next/link';
import { JokeCollection } from '@/types/joke';

export default function JokeList({ collections }: { collections: JokeCollection[] }) {
  if (collections.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center relative z-10">
        <div className="text-center animate-fade-in-up">
          <div className="text-7xl mb-5 animate-float">😄</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">笑话库空空</h2>
          <p className="text-gray-500">用命令行创建你的第一个笑话集吧</p>
          <p className="text-sm text-gray-400 mt-2">cd crazy_sanguo_serial && python3 main.py</p>
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
              <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg shadow-orange-200/50">
                <span className="text-2xl">😄</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">笑话集</h1>
                <p className="text-sm text-gray-500">{collections.length} 个笑话集</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="tag">共 {collections.reduce((acc, n) => acc + (n.current_count || 0), 0)} 组</span>
            </div>
          </div>
        </div>
        <div className="h-[3px] bg-gradient-to-r from-yellow-200 via-yellow-400 to-orange-300"></div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-10">
        <div className="grid gap-5">
          {collections.map((collection, index) => (
            <Link
              key={collection.id}
              href={`/jokes/${collection.id}`}
              className="animate-fade-in-up"
              style={{ animationDelay: `${index * 0.1}s`, opacity: 0 }}
            >
              <div className="bg-white rounded-2xl p-6 shadow-md shadow-orange-100/50 card-hover relative overflow-hidden group">
                {/* 背景装饰 */}
                <div className="absolute inset-0 bg-gradient-to-br from-yellow-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="absolute -top-16 -right-16 w-32 h-32 bg-yellow-100/30 rounded-full blur-2xl group-hover:bg-yellow-200/40 transition-all duration-500"></div>
                
                <div className="relative flex items-start justify-between gap-6">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-lg font-bold text-gray-800 group-hover:text-orange-600 transition-colors">
                        {collection.title}
                      </h2>
                      <span className="tag">
                        {collection.current_count || 0} 组
                      </span>
                    </div>
                    <p className="text-gray-500 text-sm">
                      {(collection.current_count || 0) * 10} 个笑话
                    </p>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    {/* 箭头 */}
                    <div className="w-10 h-10 rounded-xl bg-yellow-50 flex items-center justify-center group-hover:bg-yellow-100 group-hover:scale-110 transition-all duration-300">
                      <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
          笑话集
          <span className="animate-pulse">✨</span>
        </p>
      </footer>
    </div>
  );
}