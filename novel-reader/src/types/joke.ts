export interface JokeCollection {
  id: string;
  title: string;
  created_at: string;
  current_count?: number;
}

export interface JokeCollectionMeta {
  id: string;
  title: string;
  keywords: string[];
  creative_direction: string;
  current_count: number;
  created_at: string;
}

export interface JokeGroupInfo {
  id: number;
  title: string;
  path: string;
}

export interface JokeGroupDetail {
  id: number;
  title: string;
  content: string;
  hasPrev: boolean;
  hasNext: boolean;
  collection_id: string;
}

export interface JokeListResponse {
  collections: JokeCollection[];
}

export interface JokeGroupsResponse {
  collection: JokeCollectionMeta;
  groups: JokeGroupInfo[];
  totalJokes: number;
}