# InSync Thought Leadership Engine

Production-oriented internal workspace for turning high-relevance education, AI, hiring, and future-of-work news into DASCAIN LinkedIn thought leadership.

## What Is Included

- Next.js, TypeScript, TailwindCSS frontend with a Notion/Perplexity-style three-panel AI workspace.
- FastAPI backend with SQLAlchemy models for articles, knowledge nodes, generated posts, scheduling, and exports.
- RSS collector, deduplication by canonical URL, AI categorization, relevance scoring, and n8n-compatible ingestion webhook.
- Knowledge graph reasoning across Learning Intelligence, PEARLS, AI Tutors, Skill Intelligence, Workforce Readiness, and related themes.
- LinkedIn draft generation for thought leadership, founder perspective, and visionary angles.
- Docker Compose stack with PostgreSQL plus pgvector image.

## Run Locally

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Docker

```bash
docker compose up --build
```

The frontend runs on `http://localhost:3000` and the API on `http://localhost:8000/api`.

## API Highlights

- `GET /api/dashboard`
- `GET /api/articles`
- `GET /api/articles/{id}`
- `POST /api/articles/{id}/generate`
- `POST /api/posts/{id}/rewrite`
- `POST /api/posts/{id}/schedule`
- `GET /api/posts/{id}/export/{linkedin|markdown|notion|word|pdf}`
- `POST /api/collector/run`
- `POST /api/webhooks/n8n/article`

## Environment

Copy `.env.example` to `.env` and fill in keys as integrations are connected.

The current AI pipeline has deterministic fallbacks so the app is usable without OpenAI credentials. The service boundary is ready for replacing the local composer with the OpenAI Responses API and embedding writes to pgvector.
