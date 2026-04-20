'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { JokeGroupDetail, JokeCollectionMeta } from '@/types/joke';
import { Suspense } from 'react';

interface JokeReaderProps {
  groupId: number;
  collectionId?: string;
}

interface JokeItem {
  title: string;
  content: string;
}

function LoadingState() {
  return (
    <div className="min-h-screen flex items-center justify-center relative z-10">
      <div className="text-center animate-fade-in">
        <div className="loading-spinner mx-auto mb-4"></div>
        <p className="text-gray-500 text-sm">正在加载...</p>
      </div>
    </div>
  );
}

function ErrorState({ error, backUrl }: { error: string; backUrl: string }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative z-10">
      <div className="text-6xl mb-4 animate-float">📭</div>
      <p className="text-lg text-gray-500 mb-4 animate-fade-in-up">{error || '笑话不存在'}</p>
      <Link href={backUrl} className="text-orange-500 hover:text-orange-600 font-medium animate-fade-in-up delay-200">
        返回目录
      </Link>
    </div>
  );
}

function JokeContent({ 
  jokes, 
  collectionTitle,
  collectionId,
  groupId,
  buildBackUrl,
  buildNavUrl,
  hasPrev,
  hasNext
}: { 
  jokes: JokeItem[];
  collectionTitle: string;
  collectionId: string;
  groupId: number;
  buildBackUrl: () => string;
  buildNavUrl: (id: number) => string;
  hasPrev: boolean;
  hasNext: boolean;
}) {
  return (
    <div className="min-h-screen relative z-10">
      <header className="glass sticky top-0 z-50 border-b border-orange-200/50">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link 
              href={buildBackUrl()} 
              className="flex items-center gap-2 text-gray-600 hover:text-orange-600 transition-colors group"
            >
              <div className="w-9 h-9 rounded-lg bg-orange-50 flex items-center justify-center group-hover:bg-orange-100 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </div>
              <span className="text-sm font-medium">返回</span>
            </Link>
            
            <div className="px-4 py-1.5 rounded-full bg-yellow-50 border border-yellow-200">
              <span className="text-sm text-yellow-600 font-medium">
                {collectionTitle}
              </span>
            </div>
          </div>
        </div>
        <div className="h-[3px] bg-gradient-to-r from-yellow-200 via-yellow-400 to-orange-300"></div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        <div className="grid gap-6">
          {jokes.map((joke, index) => (
            <div 
              key={index}
              className="bg-white rounded-2xl p-6 shadow-md shadow-orange-100/50 animate-fade-in-up"
              style={{ animationDelay: `${index * 0.1}s`, opacity: 0 }}
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center flex-shrink-0">
                  <span className="text-lg">😄</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-800 mb-3">
                    {joke.title.replace(/^笑话\d+：/, '')}
                  </h3>
                  <p className="text-gray-600 leading-relaxed whitespace-pre-wrap">
                    {joke.content}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <nav className="mt-8 flex items-center justify-between gap-4 animate-fade-in-up delay-200" style={{ opacity: 0 }}>
          {hasPrev ? (
            <Link href={buildNavUrl(groupId - 1)} className="nav-btn flex-1">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>上一组</span>
            </Link>
          ) : (
            <div className="flex-1"></div>
          )}

          <Link href={buildBackUrl()} className="nav-btn px-6">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <span className="hidden sm:inline">目录</span>
          </Link>

          {hasNext ? (
            <Link href={buildNavUrl(groupId + 1)} className="nav-btn flex-1">
              <span>下一组</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          ) : (
            <div className="flex-1"></div>
          )}
        </nav>
      </main>

      <footer className="text-center py-10 text-gray-400 text-sm relative z-10">
        <div className="divider mb-6"></div>
        <p className="flex items-center justify-center gap-2">
          <span className="animate-pulse">😄</span>
          {collectionTitle} · {jokes.length} 个笑话
          <span className="animate-pulse">✨</span>
        </p>
      </footer>
    </div>
  );
}

interface GroupInfo {
  jokes: JokeItem[];
  collectionMeta: JokeCollectionMeta | null;
  hasPrev: boolean;
  hasNext: boolean;
}

function JokeReaderInner({ groupId, collectionId }: JokeReaderProps) {
  const [data, setData] = useState<GroupInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const buildBackUrl = () => {
    return collectionId ? `/jokes/${collectionId}` : '/?tab=jokes';
  };

  const buildNavUrl = (targetId: number) => {
    return collectionId ? `/jokes/${collectionId}/${targetId}` : `/jokes/${targetId}`;
  };

  useEffect(() => {
    let ignore = false;
    
    async function fetchJokes() {
      try {
        setLoading(true);
        const res = await fetch(`/api/jokes/${collectionId}/${groupId}`);
        if (!res.ok) throw new Error('Jokes not found');
        const result = await res.json();
        if (!ignore) {
          setData(result);
        }
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : 'Load failed');
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }
    fetchJokes();
    
    return () => { ignore = true; };
  }, [groupId, collectionId]);

  if (loading) {
    return <LoadingState />;
  }

  if (error || !data) {
    return <ErrorState error={error || '笑话不存在'} backUrl={buildBackUrl()} />;
  }

  return (
    <JokeContent 
      jokes={data.jokes}
      collectionTitle={data.collectionMeta?.title || '笑话集'}
      collectionId={collectionId || ''}
      groupId={groupId}
      buildBackUrl={buildBackUrl}
      buildNavUrl={buildNavUrl}
      hasPrev={data.hasPrev}
      hasNext={data.hasNext}
    />
  );
}

export default function JokeReader({ groupId, collectionId }: JokeReaderProps) {
  return (
    <Suspense fallback={<LoadingState />}>
      <JokeReaderInner groupId={groupId} collectionId={collectionId} />
    </Suspense>
  );
}