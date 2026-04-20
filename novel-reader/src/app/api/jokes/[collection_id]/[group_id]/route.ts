import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { 
  JOKES_DIR, 
  getJokeGroupPath, 
  getJokeCollectionMetaPath, 
  listJokeCollections 
} from '@/lib/paths';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ collection_id: string; group_id: string }> }
) {
  try {
    const { collection_id, group_id } = await params;
    const decodedCollectionId = decodeURIComponent(collection_id);
    
    const groupId = parseInt(group_id);
    if (isNaN(groupId) || groupId <= 0) {
      return NextResponse.json(
        { error: 'Invalid group ID' },
        { status: 400 }
      );
    }

    const jokePath = getJokeGroupPath(decodedCollectionId, groupId);
    
    if (!fs.existsSync(jokePath)) {
      return NextResponse.json(
        { error: 'Joke group not found' },
        { status: 404 }
      );
    }

    const content = fs.readFileSync(jokePath, 'utf-8');
    
    const jokes = parseJokesContent(content);
    
    const metaPath = getJokeCollectionMetaPath(decodedCollectionId);
    let collectionMeta = null;
    if (fs.existsSync(metaPath)) {
      collectionMeta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
    }
    
    const prevPath = getJokeGroupPath(decodedCollectionId, groupId - 1);
    const nextPath = getJokeGroupPath(decodedCollectionId, groupId + 1);
    
    return NextResponse.json({
      jokes,
      collectionMeta,
      hasPrev: fs.existsSync(prevPath),
      hasNext: fs.existsSync(nextPath)
    });
  } catch (error) {
    console.error('Error reading jokes:', error);
    return NextResponse.json(
      { error: 'Failed to load jokes' },
      { status: 500 }
    );
  }
}

function parseJokesContent(content: string): { title: string; content: string }[] {
  const jokes: { title: string; content: string }[] = [];
  
  const sections = content.split(/^## /m);
  
  for (const section of sections) {
    if (!section.trim()) continue;
    
    const lines = section.split('\n');
    const titleLine = lines[0].trim();
    const bodyLines = lines.slice(1);
    
    const titleMatch = titleLine.match(/^笑话?\d+[：:]\s*(.+)/);
    if (titleMatch) {
      jokes.push({
        title: titleLine,
        content: bodyLines.join('\n').trim()
      });
    } else if (titleLine) {
      jokes.push({
        title: titleLine,
        content: bodyLines.join('\n').trim()
      });
    }
  }
  
  return jokes;
}