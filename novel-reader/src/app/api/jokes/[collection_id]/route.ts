import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { 
  getJokeCollectionDir, 
  getJokeCollectionMetaPath,
  getJokeGroupPath
} from '@/lib/paths';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ collection_id: string }> }
) {
  try {
    const { collection_id } = await params;
    const decodedCollectionId = decodeURIComponent(collection_id);
    
    const metaPath = getJokeCollectionMetaPath(decodedCollectionId);
    
    if (!fs.existsSync(metaPath)) {
      return NextResponse.json(
        { error: 'Collection not found' },
        { status: 404 }
      );
    }

    const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
    
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
    
    const groups = groupIds.map(id => ({
      id,
      title: `第${id}组笑话`,
      path: `joke_${String(id).padStart(3, '0')}.md`
    }));
    
    return NextResponse.json({
      collection: meta,
      groups,
      totalJokes: groups.length * 10
    });
  } catch (error) {
    console.error('Error reading collection:', error);
    return NextResponse.json(
      { error: 'Failed to load collection' },
      { status: 500 }
    );
  }
}