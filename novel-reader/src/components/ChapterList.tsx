'use client';

import Link from 'next/link';
import { ChapterInfo, Meta } from '@/types/novel';

interface ChapterListProps {
  chapters: ChapterInfo[];
  meta: Meta;
}

export default function ChapterList({ chapters, meta }: ChapterListProps) {
  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-gray-200 py-16 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {meta.story_title}
          </h1>
          <p className="text-gray-500">
            {meta.story_subtitle}
          </p>
          <p className="text-sm text-gray-400 mt-4">
            {chapters.length} chapters
          </p>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-12">
        {chapters.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <p>No chapters yet</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {chapters.map((chapter) => (
              <Link
                key={chapter.id}
                href={`/read/${chapter.id}`}
                className="block py-4 group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-400 w-8">
                      {chapter.id}
                    </span>
                    <span className="text-gray-800 group-hover:text-orange-600 transition-colors">
                      {chapter.title}
                    </span>
                  </div>
                  <span className="text-gray-400">›</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>

      <footer className="border-t border-gray-200 py-8 px-4 mt-16">
        <div className="max-w-2xl mx-auto text-center text-sm text-gray-400">
          <p>疯狂三国：魔改演义</p>
        </div>
      </footer>
    </div>
  );
}