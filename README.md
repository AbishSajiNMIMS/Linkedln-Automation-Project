# PostPilot

PostPilot is a neutral LinkedIn content workspace for individuals and small teams. It discovers professional stories from RSS feeds, helps you turn them into editable post drafts, and lets you schedule or publish from your own LinkedIn account.

## Features

- Discover and score stories by topic and relevance.
- Generate multiple post angles and edit the copy before publishing.
- Schedule drafts for a future time.
- Connect a LinkedIn account with OAuth 2.0; no LinkedIn password is stored.
- Publish through LinkedIn's official API when the LinkedIn application has the required product permissions.
- Export drafts as Markdown, Word-compatible HTML, PDF, or plain text.

## Run locally

```powershell
Copy-Item .env.example .env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## LinkedIn setup

Create an application in the LinkedIn Developer Portal, enable the Sign In with LinkedIn using OpenID Connect and Share on LinkedIn products, and add this redirect URL:

`http://localhost:8000/api/linkedin/callback`

Copy the client ID and secret into `.env`. For production, use your HTTPS domain as `LINKEDIN_REDIRECT_URI`. LinkedIn must approve the required scopes for your application; the app cannot bypass those permissions.

## Docker

```powershell
docker compose up --build
```

## Production deployment

The simplest production layout is a small DigitalOcean droplet or App Platform service running the Docker Compose stack behind HTTPS. Set a persistent PostgreSQL database, `CORS_ORIGINS`, the public frontend API URL, and the LinkedIn OAuth values as platform secrets. Update the LinkedIn redirect URL to the public API callback URL, then run health checks against `/api/health`.

For reliable delayed publishing, run a worker/cron process that finds posts whose `scheduled_for` is in the past and calls the same publish service. The current UI stores schedules and publishes immediately; it intentionally does not pretend to run a production scheduler inside a web request.
