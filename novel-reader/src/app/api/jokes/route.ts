import { NextResponse } from 'next/server';
import fs from 'fs';
import { 
  JOKES_DIR, 
  getJokeCollectionMetaPath,
  listJokeCollections
} from '@/lib/paths';

export async function GET() {
  try {
    const collectionIds = listJokeCollections();
    const collections = [];
    
    for (const id of collectionIds) {
      const metaPath = getJokeCollectionMetaPath(id);
      if (fs.existsSync(metaPath)) {
        const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
        collections.push({
          id: meta.id,
          title: meta.title,
          created_at: meta.created_at,
          current_count: meta.current_count || 0
        });
      }
    }
    
    return NextResponse.json({ collections });
  } catch (error) {
    console.error('Error listing collections:', error);
    return NextResponse.json(
      { error: 'Failed to list collections' },
      { status: 500 }
    );
  }
}