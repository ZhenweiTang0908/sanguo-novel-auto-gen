export interface ChapterInfo {
  id: number;
  title: string;
  path: string;
}

export interface Meta {
  current_chapter: number;
  story_title: string;
  story_subtitle: string;
}

export interface ChapterDetail {
  id: number;
  title: string;
  content: string;
  hasPrev: boolean;
  hasNext: boolean;
}

export interface ChaptersResponse {
  chapters: ChapterInfo[];
  meta: Meta;
  totalChapters: number;
}
