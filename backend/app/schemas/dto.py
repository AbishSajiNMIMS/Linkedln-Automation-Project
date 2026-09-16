from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import ArticleStatus, PostTone


class GeneratedPostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    version: str
    tone: PostTone
    body: str
    hashtags: str
    status: str
    scheduled_for: datetime | None


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str | None
    source: str
    url: str
    published_at: datetime | None
    image_url: str | None
    category: str
    summary: str
    relevance_score: float
    virality_score: float
    ai_confidence: float
    status: ArticleStatus
    analysis: str
    key_takeaways: str
    personal_angle: str
    potential_hook: str
    founder_opinion: str
    themes: str
    hashtags: str
    posts: list[GeneratedPostRead] = []


class DashboardStats(BaseModel):
    todays_articles: int
    average_relevance: float
    awaiting_approval: int
    posts_generated: int
    posts_scheduled: int
    posts_published: int
    trending_topics: list[str]
    ai_confidence: float


class ArticleUpdate(BaseModel):
    status: ArticleStatus | None = None
    category: str | None = None
    relevance_score: float | None = Field(default=None, ge=0, le=100)


class GeneratePostRequest(BaseModel):
    tones: list[PostTone] = [PostTone.thought_leadership, PostTone.founder, PostTone.visionary]


class RewritePostRequest(BaseModel):
    tone: PostTone
    body: str


class UpdatePostRequest(BaseModel):
    body: str | None = None
    status: str | None = None


class SchedulePostRequest(BaseModel):
    scheduled_for: datetime


class LinkedInStatus(BaseModel):
    connected: bool
    display_name: str | None = None
    expires_at: datetime | None = None


class WebhookArticle(BaseModel):
    title: str
    source: str
    url: str
    author: str | None = None
    published_at: datetime | None = None
    image_url: str | None = None
    full_text: str = ""
