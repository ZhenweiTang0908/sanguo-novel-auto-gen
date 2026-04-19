export interface ChapterInfo {
  id: number;
  title: string;
  path: string;
}

export interface Meta {
  current_chapter: number;
  story_title: string;
  story_subtitle: string;
  novel_id?: string;
}

export interface Novel {
  id: string;
  title: string;
  subtitle: string;
  created_at: string;
  last_updated?: string;
  current_chapter?: number;
}

export interface NovelListResponse {
  novels: Novel[];
}

export interface ChapterDetail {
  id: number;
  title: string;
  content: string;
  hasPrev: boolean;
  hasNext: boolean;
  novel_id?: string;
}

export interface ChaptersResponse {
  chapters: ChapterInfo[];
  meta: Meta;
  totalChapters: number;
}
