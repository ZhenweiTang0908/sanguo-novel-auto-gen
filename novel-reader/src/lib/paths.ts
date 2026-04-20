import path from 'path';
import fs from 'fs';

export const NOVELS_DIR = path.join(process.cwd(), 'novels');
export const LEGACY_DATA_DIR = path.join(process.cwd(), 'data/chapters');
export const LEGACY_META_PATH = path.join(process.cwd(), 'meta.json');
export const NOVEL_LIST_PATH = path.join(process.cwd(), 'novel-list.json');

export function getChapterFileName(chapterId: number): string {
  return `chapter_${String(chapterId).padStart(3, '0')}.md`;
}

export function findChapterPath(novelId: string, chapterId: number): string | null {
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
    const dir = path.join(NOVELS_DIR, novelId, 'chapters');
    if (fs.existsSync(dir)) return dir;
  }
  return LEGACY_DATA_DIR;
}

export function getMetaPath(novelId: string): string {
  if (novelId) {
    const metaPath = path.join(NOVELS_DIR, novelId, 'meta.json');
    if (fs.existsSync(metaPath)) return metaPath;
  }
  return LEGACY_META_PATH;
}