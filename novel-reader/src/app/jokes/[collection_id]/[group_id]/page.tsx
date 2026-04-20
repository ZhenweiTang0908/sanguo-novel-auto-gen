import JokeReader from '@/components/JokeReader';

interface JokeGroupPageProps {
  params: Promise<{ collection_id: string; group_id: string }>;
}

export default async function JokeGroupPage({ params }: JokeGroupPageProps) {
  const { collection_id, group_id } = await params;
  const groupId = parseInt(group_id);
  
  if (isNaN(groupId) || groupId <= 0) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center relative z-10">
        <div className="text-6xl mb-4">📭</div>
        <p className="text-lg text-gray-500 mb-4">无效的笑话组编号</p>
        <a href={`/jokes/${collection_id}`} className="text-orange-500 hover:text-orange-600 font-medium">
          返回目录
        </a>
      </div>
    );
  }
  
  return <JokeReader groupId={groupId} collectionId={collection_id} />;
}