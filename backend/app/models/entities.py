from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ArticleStatus(str, Enum):
    discovered = "discovered"
    approved = "approved"
    rejected = "rejected"
    generated = "generated"
    scheduled = "scheduled"
    published = "published"


class PostTone(str, Enum):
    thought_leadership = "thought_leadership"
    founder = "founder"
    visionary = "visionary"
    professional = "professional"
    short = "short"
    long = "long"
    storytelling = "storytelling"


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (UniqueConstraint("canonical_url", name="uq_articles_canonical_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    author: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(160), index=True)
    url: Mapped[str] = mapped_column(Text)
    canonical_url: Mapped[str] = mapped_column(String(768), index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    image_url: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), index=True)
    full_text: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    relevance_score: Mapped[float] = mapped_column(Float, default=0)
    virality_score: Mapped[float] = mapped_column(Float, default=0)
    ai_confidence: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[ArticleStatus] = mapped_column(SqlEnum(ArticleStatus), default=ArticleStatus.discovered)
    analysis: Mapped[str] = mapped_column(Text, default="")
    key_takeaways: Mapped[str] = mapped_column(Text, default="")
    insync_connection: Mapped[str] = mapped_column(Text, default="")
    potential_hook: Mapped[str] = mapped_column(Text, default="")
    founder_opinion: Mapped[str] = mapped_column(Text, default="")
    themes: Mapped[str] = mapped_column(Text, default="")
    hashtags: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    posts: Mapped[list["GeneratedPost"]] = relationship(back_populates="article", cascade="all, delete-orphan")


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True)
    node_type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    weight: Mapped[float] = mapped_column(Float, default=1)


class GeneratedPost(Base):
    __tablename__ = "generated_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    version: Mapped[str] = mapped_column(String(40))
    tone: Mapped[PostTone] = mapped_column(SqlEnum(PostTone))
    body: Mapped[str] = mapped_column(Text)
    hashtags: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="draft")
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    article: Mapped[Article] = relationship(back_populates="posts")
