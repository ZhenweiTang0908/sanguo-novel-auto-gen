import path from 'path';
import fs from 'fs';

// 项目根目录（novel-reader 的上一级 = free-world）
const PROJECT_ROOT = path.join(process.cwd(), '..');

export const NOVELS_DIR = path.join(process.cwd(), 'novels');
export const LEGACY_DATA_DIR = path.join(process.cwd(), 'data/chapters');
export const LEGACY_META_PATH = path.join(process.cwd(), 'meta.json');
export const NOVEL_LIST_PATH = path.join(process.cwd(), 'novel-list.json');

// 笑话集在项目根目录
export const JOKES_DIR = path.join(PROJECT_ROOT, 'jokes');
export const JOKE_LIST_PATH = path.join(JOKES_DIR, 'meta.json');

const SAFE_NOVEL_ID_REGEX = /^[a-zA-Z0-9_-]+$/;

export function isValidNovelId(novelId: string): boolean {
  return SAFE_NOVEL_ID_REGEX.test(novelId);
}

export function getChapterFileName(chapterId: number): string {
  return `chapter_${String(chapterId).padStart(3, '0')}.md`;
}

export function findChapterPath(novelId: string, chapterId: number): string | null {
  if (novelId && !isValidNovelId(novelId)) {
    return null;
  }

  const fileName = getChapterFileName(chapterId);

  if (novelId) {
    const newPath = path.join(NOVELS_DIR, novelId, 'chapters', fileName);
    if (fs.existsSync(newPath)) return newPath;

    const legacyPath = path.join(LEGACY_DATA_DIR, fileName);
    if (fs.existsSync(legacyPath)) return legacyPath;
    return null;
  }

  const legacyPath = path.join(LEGACY_DATA_DIR, fileName);
  return fs.existsSync(legacyPath) ? legacyPath : null;
}

export function getNovelDataDir(novelId: string): string {
  if (novelId) {
    if (!isValidNovelId(novelId)) {
      return LEGACY_DATA_DIR;
    }
    const dir = path.join(NOVELS_DIR, novelId, 'chapters');
    if (fs.existsSync(dir)) return dir;
  }
  return LEGACY_DATA_DIR;
}

export function getMetaPath(novelId: string): string {
  if (novelId) {
    if (!isValidNovelId(novelId)) {
      return LEGACY_META_PATH;
    }
    const metaPath = path.join(NOVELS_DIR, novelId, 'meta.json');
    if (fs.existsSync(metaPath)) return metaPath;
  }
  return LEGACY_META_PATH;
}

// ==================== 笑话集相关路径 ====================

export function getJokeCollectionDir(collectionId: string): string {
  return path.join(JOKES_DIR, collectionId, 'jokes');
}

export function getJokeGroupPath(collectionId: string, groupId: number): string {
  return path.join(getJokeCollectionDir(collectionId), `joke_${String(groupId).padStart(3, '0')}.md`);
}

export function getJokeCollectionMetaPath(collectionId: string): string {
  return path.join(JOKES_DIR, collectionId, 'meta.json');
}

export function listJokeCollections(): string[] {
  if (!fs.existsSync(JOKES_DIR)) return [];
  return fs.readdirSync(JOKES_DIR)
    .filter(f => {
      const metaPath = path.join(JOKES_DIR, f, 'meta.json');
      return fs.statSync(path.join(JOKES_DIR, f)).isDirectory() && fs.existsSync(metaPath);
    });
}