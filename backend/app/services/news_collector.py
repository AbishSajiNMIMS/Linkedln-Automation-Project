from datetime import datetime

import feedparser
from sqlalchemy.orm import Session

from app.models.entities import Article
from app.services.ai_pipeline import canonicalize_url, enrich_article


RSS_FEEDS = {
    "EdTech Review": "https://www.edtechreview.in/feed/",
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
    "World Economic Forum": "https://www.weforum.org/agenda/feed",
    "Inside Higher Ed": "https://www.insidehighered.com/rss.xml",
}


def collect_from_rss(db: Session) -> int:
    created = 0
    for source, feed_url in RSS_FEEDS.items():
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries[:12]:
            link = entry.get("link")
            title = entry.get("title")
            if not link or not title:
                continue
            canonical = canonicalize_url(link)
            if db.query(Article).filter(Article.canonical_url == canonical).first():
                continue
            article = Article(
                title=title,
                source=source,
                url=link,
                canonical_url=canonical,
                author=entry.get("author"),
                published_at=_published(entry),
                image_url=_image(entry),
                full_text=entry.get("summary", ""),
                category="",
            )
            enrich_article(db, article)
            if article.relevance_score >= 80:
                db.add(article)
                created += 1
    db.commit()
    return created


def _published(entry) -> datetime | None:
    if entry.get("published_parsed"):
        return datetime(*entry.published_parsed[:6])
    return None


def _image(entry) -> str | None:
    media = entry.get("media_content") or []
    if media and isinstance(media, list):
        return media[0].get("url")
    return None
