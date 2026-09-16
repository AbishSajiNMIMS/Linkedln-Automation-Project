from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.entities import Article, KnowledgeNode
from app.services.ai_pipeline import enrich_article


KNOWLEDGE_NODES = [
    ("Learning Intelligence", "core_theme", "Understanding how learners think, struggle, progress, and transfer knowledge across contexts.", 1.0),
    ("PEARLS Framework", "framework", "A structured lens for performance, engagement, assessment, reflection, learning pathways, and skill readiness.", 0.95),
    ("Industry-University Collaboration", "ecosystem", "A bridge between academic learning, employer expectations, and real workforce problems.", 0.9),
    ("AI Tutors", "capability", "Personalized academic support that adapts to each learner's behavior and evidence of understanding.", 0.8),
    ("Adaptive Learning", "capability", "Learning experiences that change based on demonstrated needs rather than fixed pacing.", 0.85),
    ("Student Thinking Analytics", "capability", "Signals that reveal misconceptions, confidence, strategy, and readiness beyond final scores.", 0.95),
    ("Skill Intelligence", "theme", "A data-rich view of what people can actually do, where gaps exist, and how they become employable.", 0.9),
    ("Workforce Readiness", "theme", "The ability to connect learning outcomes with changing roles, projects, and industry demand.", 0.86),
    ("Professor Enablement", "theme", "Tools that help faculty see learning patterns and intervene with better timing and context.", 0.82),
]


SAMPLE_ARTICLES = [
    {
        "title": "Universities turn to AI tutors as student support demand rises",
        "source": "Inside Higher Ed",
        "url": "https://example.com/ai-tutors-student-support",
        "author": "Editorial Desk",
        "category": "Personalized Learning",
        "image_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80",
        "full_text": "Universities are experimenting with AI tutoring systems to support learners outside office hours. The strongest pilots focus less on answer delivery and more on feedback, misconceptions, and learning behavior.",
    },
    {
        "title": "Employers question whether degrees still signal job readiness",
        "source": "World Economic Forum",
        "url": "https://example.com/skills-readiness-hiring",
        "author": "Future of Work Team",
        "category": "Hiring",
        "image_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1200&q=80",
        "full_text": "Hiring leaders are shifting toward skills evidence, project portfolios, and continuous assessment. The debate is no longer degree versus no degree, but whether education can produce trusted signals of capability.",
    },
    {
        "title": "Learning analytics research points to the limits of final exams",
        "source": "Nature Education",
        "url": "https://example.com/learning-analytics-assessment",
        "author": "Research Brief",
        "category": "Assessment",
        "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80",
        "full_text": "Researchers argue that single-point assessments miss the process of learning. New models combine interaction data, reflection, and formative evidence to help educators understand how students arrive at answers.",
    },
]


def seed_database(db: Session) -> None:
    if db.query(KnowledgeNode).count() == 0:
        for title, node_type, description, weight in KNOWLEDGE_NODES:
            db.add(KnowledgeNode(title=title, node_type=node_type, description=description, weight=weight))

    if db.query(Article).count() == 0:
        for index, item in enumerate(SAMPLE_ARTICLES):
            article = Article(
                title=item["title"],
                source=item["source"],
                url=item["url"],
                canonical_url=item["url"],
                author=item["author"],
                image_url=item["image_url"],
                category=item["category"],
                full_text=item["full_text"],
                published_at=datetime.utcnow() - timedelta(hours=index * 4),
            )
            enrich_article(db, article)
            db.add(article)

    db.commit()
