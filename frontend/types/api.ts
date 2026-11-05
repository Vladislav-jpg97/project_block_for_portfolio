export type FeedType = "new" | "top" | "hot";

export type UserBrief = {
  id: number;
  username: string;
  karma: number;
  avatar_url: string | null;
};

export type User = UserBrief & {
  email: string;
  bio: string | null;
  created_at: string;
};

export type Category = {
  id: number;
  name: string;
  description: string | null;
};

export type Tag = {
  id: number;
  name: string;
  slug: string;
  posts_count: number;
};

export type Post = {
  id: number;
  slug: string;
  title: string;
  content: string;
  is_published: boolean;
  views_count: number;
  votes_count: number;
  created_at: string;
  author: UserBrief;
  category: Category | null;
  tags: Tag[];
  is_bookmarked: boolean;
  user_vote: number | null;
};

export type ApiPage<T> = {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
};

export type Comment = {
  id: number;
  content: string;
  post_id: number;
  parent_id: number | null;
  author: { id: number; username: string };
  created_at: string;
  updated_at: string;
  replies: Comment[];
};

export type Tokens = {
  access_token: string;
  refresh_token: string;
};

export type PostInput = {
  title: string;
  content: string;
  category_id: number;
  tags_ids: number[];
  is_published: boolean;
};
