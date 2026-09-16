import type { Article, DashboardStats, GeneratedPost, PostTone } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

export function getDashboard() {
  return request<DashboardStats>("/dashboard");
}

export function getArticles() {
  return request<Article[]>("/articles");
}

export function getArticle(id: number) {
  return request<Article>(`/articles/${id}`);
}

export function generatePosts(articleId: number, tones: PostTone[]) {
  return request<GeneratedPost[]>(`/articles/${articleId}/generate`, {
    method: "POST",
    body: JSON.stringify({ tones })
  });
}

export function rewritePost(postId: number, tone: PostTone, body: string) {
  return request<GeneratedPost>(`/posts/${postId}/rewrite`, {
    method: "POST",
    body: JSON.stringify({ tone, body })
  });
}

export function updatePost(postId: number, body: string) {
  return request<GeneratedPost>(`/posts/${postId}`, {
    method: "PATCH",
    body: JSON.stringify({ body })
  });
}

export function schedulePost(postId: number, scheduledFor: string) {
  return request<GeneratedPost>(`/posts/${postId}/schedule`, {
    method: "POST",
    body: JSON.stringify({ scheduled_for: scheduledFor })
  });
}

export function approveArticle(articleId: number) {
  return request<Article>(`/articles/${articleId}`, {
    method: "PATCH",
    body: JSON.stringify({ status: "approved" })
  });
}

export async function exportPost(postId: number, format: "linkedin" | "markdown" | "notion" | "word" | "pdf") {
  const response = await fetch(`${API_BASE}/posts/${postId}/export/${format}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.blob();
}
