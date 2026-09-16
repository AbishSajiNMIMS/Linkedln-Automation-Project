from datetime import datetime, timedelta
from html import escape
from io import BytesIO

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.database import get_db
from app.models.entities import Article, ArticleStatus, GeneratedPost
from app.schemas.dto import (
    ArticleRead,
    ArticleUpdate,
    DashboardStats,
    GeneratePostRequest,
    GeneratedPostRead,
    RewritePostRequest,
    SchedulePostRequest,
    UpdatePostRequest,
    WebhookArticle,
)
from app.services.ai_pipeline import canonicalize_url, enrich_article, generate_posts
from app.services.knowledge_graph import graph_reasoning, retrieve_context
from app.services.news_collector import collect_from_rss

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db)) -> DashboardStats:
    today = datetime.utcnow() - timedelta(hours=24)
    articles = db.query(Article).all()
    posts = db.query(GeneratedPost).all()
    themes = ", ".join(article.themes for article in articles)
    trending = []
    for theme in ["Learning Intelligence", "Skill Intelligence", "AI Tutors", "Workforce Readiness", "Assessment"]:
        if theme.lower() in themes.lower():
            trending.append(theme)
    return DashboardStats(
        todays_articles=db.query(Article).filter(Article.created_at >= today).count(),
        average_relevance=round(sum(a.relevance_score for a in articles) / max(len(articles), 1), 1),
        awaiting_approval=db.query(Article).filter(Article.status == ArticleStatus.discovered, Article.relevance_score >= 80).count(),
        posts_generated=len(posts),
        posts_scheduled=sum(1 for post in posts if post.status == "scheduled"),
        posts_published=sum(1 for post in posts if post.status == "published"),
        trending_topics=trending[:5],
        ai_confidence=round(sum(a.ai_confidence for a in articles) / max(len(articles), 1), 1),
    )


@router.get("/articles", response_model=list[ArticleRead])
def list_articles(db: Session = Depends(get_db)) -> list[Article]:
    return (
        db.query(Article)
        .options(selectinload(Article.posts))
        .filter(Article.relevance_score >= 80)
        .order_by(Article.relevance_score.desc(), Article.published_at.desc().nullslast())
        .all()
    )


@router.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(article_id: int, db: Session = Depends(get_db)) -> Article:
    article = db.query(Article).options(selectinload(Article.posts)).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article.insync_connection = graph_reasoning(article, retrieve_context(db, article))
    db.commit()
    db.refresh(article)
    return article


@router.patch("/articles/{article_id}", response_model=ArticleRead)
def update_article(article_id: int, payload: ArticleUpdate, db: Session = Depends(get_db)) -> Article:
    article = db.query(Article).options(selectinload(Article.posts)).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(article, field, value)
    db.commit()
    db.refresh(article)
    return article


@router.post("/articles/{article_id}/generate", response_model=list[GeneratedPostRead])
def create_posts(article_id: int, payload: GeneratePostRequest, db: Session = Depends(get_db)) -> list[GeneratedPost]:
    article = db.query(Article).options(selectinload(Article.posts)).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return generate_posts(db, article, payload.tones)


@router.post("/posts/{post_id}/rewrite", response_model=GeneratedPostRead)
def rewrite_post(post_id: int, payload: RewritePostRequest, db: Session = Depends(get_db)) -> GeneratedPost:
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.tone = payload.tone
    post.body = payload.body
    db.commit()
    db.refresh(post)
    return post


@router.patch("/posts/{post_id}", response_model=GeneratedPostRead)
def update_post(post_id: int, payload: UpdatePostRequest, db: Session = Depends(get_db)) -> GeneratedPost:
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if payload.body is not None:
        post.body = payload.body
    if payload.status is not None:
        post.status = payload.status
    db.commit()
    db.refresh(post)
    return post


@router.post("/posts/{post_id}/schedule", response_model=GeneratedPostRead)
def schedule_post(post_id: int, payload: SchedulePostRequest, db: Session = Depends(get_db)) -> GeneratedPost:
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.scheduled_for = payload.scheduled_for
    post.status = "scheduled"
    db.commit()
    db.refresh(post)
    return post


@router.get("/posts/{post_id}/export/{format_name}")
def export_post(post_id: int, format_name: str, db: Session = Depends(get_db)):
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if format_name not in {"linkedin", "markdown", "notion", "word", "pdf"}:
        raise HTTPException(status_code=400, detail="Unsupported export format")
    filename = f"linkedin-draft-{post.id}"
    if format_name in {"linkedin", "markdown", "notion"}:
        extension = "txt" if format_name == "linkedin" else "md"
        media_type = "text/plain; charset=utf-8" if format_name == "linkedin" else "text/markdown; charset=utf-8"
        return Response(
            content=post.body,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}.{extension}"'},
        )
    if format_name == "word":
        html = (
            "<html><head><meta charset=\"utf-8\"></head><body>"
            f"<pre style=\"font-family: Calibri, Arial, sans-serif; white-space: pre-wrap;\">{escape(post.body)}</pre>"
            "</body></html>"
        )
        return Response(
            content=html,
            media_type="application/msword",
            headers={"Content-Disposition": f'attachment; filename="{filename}.doc"'},
        )
    return Response(
        content=_simple_pdf(post.body),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'},
    )


def _simple_pdf(text: str) -> bytes:
    def pdf_escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if paragraph.strip():
            while len(paragraph) > 88:
                split_at = paragraph.rfind(" ", 0, 88)
                if split_at <= 0:
                    split_at = 88
                lines.append(paragraph[:split_at])
                paragraph = paragraph[split_at:].strip()
            lines.append(paragraph)
        else:
            lines.append("")

    content_lines = ["BT", "/F1 11 Tf", "72 760 Td", "14 TL"]
    for index, line in enumerate(lines[:46]):
        if index:
            content_lines.append("T*")
        content_lines.append(f"({pdf_escape(line)}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{number} 0 obj\n".encode("ascii"))
        buffer.write(body)
        buffer.write(b"\nendobj\n")
    xref_start = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    buffer.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii")
    )
    return buffer.getvalue()


@router.post("/collector/run")
def run_collector(db: Session = Depends(get_db)) -> dict[str, int]:
    return {"created": collect_from_rss(db)}


@router.post("/webhooks/n8n/article", response_model=ArticleRead)
def n8n_article(payload: WebhookArticle, x_insync_secret: str | None = Header(default=None), db: Session = Depends(get_db)) -> Article:
    settings = get_settings()
    if settings.n8n_webhook_secret and x_insync_secret != settings.n8n_webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    canonical = canonicalize_url(payload.url)
    article = db.query(Article).filter(Article.canonical_url == canonical).first()
    if article:
        return article
    article = Article(
        title=payload.title,
        source=payload.source,
        url=payload.url,
        canonical_url=canonical,
        author=payload.author,
        published_at=payload.published_at,
        image_url=payload.image_url,
        full_text=payload.full_text,
        category="",
    )
    enrich_article(db, article)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
