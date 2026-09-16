from sqlalchemy.orm import Session

from app.models.entities import Article, KnowledgeNode


def retrieve_context(db: Session, article: Article) -> list[KnowledgeNode]:
    text = f"{article.title} {article.full_text} {article.summary} {article.category}".lower()
    scored: list[tuple[float, KnowledgeNode]] = []
    for node in db.query(KnowledgeNode).all():
        title_terms = node.title.lower().replace("-", " ").split()
        description_terms = node.description.lower().replace("-", " ").split()
        score = sum(2 for term in title_terms if term in text) + sum(1 for term in description_terms if term in text)
        score *= node.weight
        if score > 0:
            scored.append((score, node))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [node for _, node in scored[:5]]


def graph_reasoning(article: Article, nodes: list[KnowledgeNode]) -> str:
    if not nodes:
        return "This story is relevant because it exposes a shift in how education, work, and AI are being reconnected."
    primary = nodes[0]
    supporting = ", ".join(node.title for node in nodes[1:4])
    if supporting:
        return (
            f"This article strengthens the case for {primary.title}: {primary.description} "
            f"It also connects with {supporting}, which helps DASCAIN build a consistent Learning Intelligence narrative."
        )
    return f"This article strengthens the case for {primary.title}: {primary.description}"
