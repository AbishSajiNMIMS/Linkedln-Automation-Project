export type ArticleStatus = "discovered" | "approved" | "rejected" | "generated" | "scheduled" | "published";

export type PostTone =
  | "thought_leadership"
  | "founder"
  | "visionary"
  | "professional"
  | "short"
  | "long"
  | "storytelling";

export type GeneratedPost = {
  id: number;
  article_id: number;
  version: string;
  tone: PostTone;
  body: string;
  hashtags: string;
  status: string;
  scheduled_for: string | null;
};

export type Article = {
  id: number;
  title: string;
  author: string | null;
  source: string;
  url: string;
  published_at: string | null;
  image_url: string | null;
  category: string;
  summary: string;
  relevance_score: number;
  virality_score: number;
  ai_confidence: number;
  status: ArticleStatus;
  analysis: string;
  key_takeaways: string;
  personal_angle: string;
  potential_hook: string;
  founder_opinion: string;
  themes: string;
  hashtags: string;
  posts: GeneratedPost[];
};

export type DashboardStats = {
  todays_articles: number;
  average_relevance: number;
  awaiting_approval: number;
  posts_generated: number;
  posts_scheduled: number;
  posts_published: number;
  trending_topics: string[];
  ai_confidence: number;
};

export type LinkedInStatus = {
  connected: boolean;
  display_name: string | null;
  expires_at: string | null;
};
