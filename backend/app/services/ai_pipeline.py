from hashlib import sha256
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.entities import Article, ArticleStatus, GeneratedPost, PostTone


CATEGORIES = [
    "AI",
    "Education",
    "Learning Science",
    "Assessment",
    "Universities",
    "Future of Work",
    "Hiring",
    "Student Experience",
    "Faculty",
    "Personalized Learning",
    "EdTech",
    "Enterprise Learning",
    "Research",
]

SIGNALS = {
    "AI": ["ai", "artificial intelligence", "tutor", "automation", "model"],
    "Education": ["education", "learning", "student", "university", "faculty"],
    "Learning Science": ["cognition", "misconception", "learning science", "behavior", "reflection"],
    "Assessment": ["assessment", "exam", "credential", "score", "evidence"],
    "Future of Work": ["future of work", "workforce", "skills", "job", "career"],
    "Hiring": ["hiring", "employer", "degree", "readiness", "talent"],
    "Personalized Learning": ["personalized", "adaptive", "tutor", "pathway"],
}


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.netloc.lower()}{parsed.path.rstrip('/')}"


def categorize(text: str) -> str:
    lowered = text.lower()
    scores = {
        category: sum(lowered.count(signal) for signal in signals)
        for category, signals in SIGNALS.items()
    }
    category, score = max(scores.items(), key=lambda item: item[1])
    return category if score else "Education"


def summarize(text: str) -> str:
    compact = " ".join(text.split())
    if len(compact) <= 240:
        return compact
    return f"{compact[:237].rstrip()}..."


def score_article(article: Article) -> tuple[float, float, float]:
    text = f"{article.title} {article.full_text}".lower()
    keyword_hits = sum(text.count(word) for word in ["learning", "ai", "skills", "student", "university", "assessment", "workforce", "hiring", "adaptive"])
    digest = int(sha256(article.title.encode("utf-8")).hexdigest(), 16)
    virality = 55 + digest % 36
    relevance = min(100, 62 + keyword_hits * 5 + (virality - 55) * 0.25)
    confidence = min(98, 72 + keyword_hits * 3)
    return round(relevance, 1), round(virality, 1), round(confidence, 1)


def enrich_article(db: Session, article: Article) -> Article:
    text = f"{article.title}. {article.full_text}"
    article.category = article.category or categorize(text)
    article.summary = article.summary or summarize(article.full_text)
    article.relevance_score, article.virality_score, article.ai_confidence = score_article(article)
    article.analysis = (
        "The article points to a deeper shift: institutions and employers are no longer satisfied with static credentials. "
        "They need evidence of how people learn, adapt, and apply knowledge."
    )
    article.key_takeaways = "Learning signals matter; skills evidence is becoming more important; AI can help educators act earlier."
    article.personal_angle = "Connect this story to your own experience, audience, or point of view."
    article.potential_hook = f"What does this shift mean for people working in {article.category.lower()}?"
    article.founder_opinion = "A useful perspective is to focus on the practical change this creates for people and teams."
    article.themes = f"{article.category}, Trends, Practical insights"
    article.hashtags = f"#{article.category.replace(' ', '')} #ProfessionalGrowth #Trends"
    return article


def generate_posts(db: Session, article: Article, tones: list[PostTone]) -> list[GeneratedPost]:
    existing = {(post.version, post.tone) for post in article.posts}
    versions = {
        PostTone.thought_leadership: ("A", "Thought Leadership"),
        PostTone.founder: ("B", "Founder Perspective"),
        PostTone.visionary: ("C", "Visionary"),
    }
    posts: list[GeneratedPost] = []
    for tone in tones:
        version, label = versions.get(tone, ("R", tone.value.replace("_", " ").title()))
        if (version, tone) in existing:
            continue
        body = compose_post(article, tone, label)
        post = GeneratedPost(article=article, version=version, tone=tone, body=body, hashtags=article.hashtags)
        db.add(post)
        posts.append(post)
    article.status = ArticleStatus.generated
    db.commit()
    db.refresh(article)
    return posts


def compose_post(article: Article, tone: PostTone, label: str) -> str:
    opener = {
        PostTone.thought_leadership: article.potential_hook,
        PostTone.founder: "A founder's job is to notice when a familiar problem starts asking for a new language.",
        PostTone.visionary: "The future of education will be shaped by the signals we choose to trust.",
    }.get(tone, article.potential_hook)
    length_note = "In short, " if tone == PostTone.short else ""
    story = "One pattern keeps showing up across universities and employers: outcomes matter, but the path to those outcomes matters just as much."
    if tone == PostTone.storytelling:
        story = "When a student struggles, the final score rarely explains the real story. The useful signal is hidden in the attempts, misconceptions, confidence, and recovery."
    return (
        f"{opener}\n\n"
        f"{length_note}{article.title} is not just another {article.category.lower()} headline. "
        f"It highlights a structural question for education leaders: how do we understand learning before it becomes a placement, retention, or readiness problem?\n\n"
        f"{story}\n\n"
        "The useful question is how this change affects the people, teams, and customers closest to it.\n\n"
        "A strong post adds your own experience, an honest opinion, and one practical takeaway instead of repeating the headline.\n\n"
        "What learning signals do you think institutions should pay more attention to?\n\n"
        f"{article.hashtags}"
    )
