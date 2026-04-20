import Link from 'next/link';
import fs from 'fs';
import { getJokeCollectionDir, getJokeCollectionMetaPath } from '@/lib/paths';
import { JokeCollectionMeta, JokeGroupInfo } from '@/types/joke';

interface JokeCollectionPageProps {
  params: Promise<{ collection_id: string }>;
}

async function getCollectionData(collectionId: string) {
  // Decode URL-encoded collection_id
  const decodedCollectionId = decodeURIComponent(collectionId);
  const metaPath = getJokeCollectionMetaPath(decodedCollectionId);
  
  if (!fs.existsSync(metaPath)) {
    return null;
  }

  const meta: JokeCollectionMeta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
  
  const jokesDir = getJokeCollectionDir(decodedCollectionId);
  const groupIds: number[] = [];
  
  if (fs.existsSync(jokesDir)) {
    const files = fs.readdirSync(jokesDir)
      .filter(f => f.match(/^joke_\d+\.md$/));
    
    for (const file of files) {
      const match = file.match(/joke_(\d+)\.md/);
      if (match) {
        groupIds.push(parseInt(match[1]));
      }
    }
  }
  
  groupIds.sort((a, b) => a - b);
  
  const groups: JokeGroupInfo[] = groupIds.map(id => ({
    id,
    title: `第${id}组 · 10个笑话`,
    path: `joke_${String(id).padStart(3, '0')}.md`
  }));
  
  return { meta, groups };
}

export default async function JokeCollectionPage({ params }: JokeCollectionPageProps) {
  const { collection_id } = await params;
  const decodedCollectionId = decodeURIComponent(collection_id);
  const data = await getCollectionData(decodedCollectionId);
  
  if (!data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center relative z-10">
        <div className="text-6xl mb-4">📭</div>
        <p className="text-lg text-gray-500 mb-4">笑话集不存在</p>
        <Link href="/?tab=jokes" className="text-orange-500 hover:text-orange-600 font-medium">
          返回首页
        </Link>
      </div>
    );
  }

  const { meta, groups } = data;

  return (
    <div className="min-h-screen relative z-10">
      <header className="glass sticky top-0 z-50 border-b border-orange-200/50">
        <div className="max-w-4xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <Link 
              href="/?tab=jokes" 
              className="flex items-center gap-2 text-gray-600 hover:text-orange-600 transition-colors group"
            >
              <div className="w-9 h-9 rounded-lg bg-orange-50 flex items-center justify-center group-hover:bg-orange-100 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </div>
              <span className="text-sm font-medium">返回</span>
            </Link>
            
            <div>
              <h1 className="text-xl font-bold text-gray-800">{meta.title}</h1>
              <p className="text-sm text-gray-500">{meta.keywords?.join(', ')}</p>
            </div>
            
            <div className="px-4 py-1.5 rounded-full bg-yellow-50 border border-yellow-200">
              <span className="text-sm text-yellow-600 font-medium">
                {groups.length} 组
              </span>
            </div>
          </div>
        </div>
        <div className="h-[3px] bg-gradient-to-r from-yellow-200 via-yellow-400 to-orange-300"></div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        <div className="mb-6">
          <p className="text-gray-500 text-sm">
            风格：{meta.creative_direction || '轻松幽默'}
          </p>
        </div>

        {groups.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📝</div>
            <p className="text-lg text-gray-500">暂无笑话</p>
            <p className="text-sm text-gray-400 mt-2">在命令行中生成笑话</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {groups.map((group, index) => (
              <Link
                key={group.id}
                href={`/jokes/${encodeURIComponent(meta.id)}/${group.id}`}
                className="animate-fade-in-up"
                style={{ animationDelay: `${index * 0.1}s`, opacity: 0 }}
              >
                <div className="bg-white rounded-2xl p-6 shadow-md shadow-orange-100/50 card-hover relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-yellow-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  
                  <div className="relative flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                        <span className="text-2xl">😄</span>
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-800 group-hover:text-orange-600 transition-colors">
                          第{group.id}组
                        </h3>
                        <p className="text-gray-500 text-sm">10个笑话</p>
                      </div>
                    </div>
                    
                    <div className="w-10 h-10 rounded-xl bg-yellow-50 flex items-center justify-center group-hover:bg-yellow-100 group-hover:scale-110 transition-all duration-300">
                      <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

      <footer className="text-center py-10 text-gray-400 text-sm relative z-10">
        <div className="divider mb-6"></div>
        <p className="flex items-center justify-center gap-2">
          <span className="animate-pulse">😄</span>
          {meta.title} · {groups.length * 10} 个笑话
          <span className="animate-pulse">✨</span>
        </p>
      </footer>
    </div>
  );
}