# CreatorFlow AI Backend (MVP)

Backend MVP for AI-assisted YouTube Shorts automation using FastAPI + PostgreSQL + SQLAlchemy + Alembic.

## 1) Install dependencies

```bash
pip install -r requirements.txt
```

## 2) Configure environment

Copy `.env.example` to `.env` and set values:

- `DATABASE_URL`
- `GROQ_API_KEY`
- `GROQ_MODEL` (optional)
- `AUTO_CREATE_TABLES` (local MVP convenience; use Alembic migrations for production)

## 3) Run database migrations (recommended)

```bash
alembic upgrade head
```

## 4) Run the API locally

```bash
uvicorn app.main:app --reload
```

API base: `http://127.0.0.1:8000/api`

## 5) Smoke test commands

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/api/channels ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"CreatorFlow Lab\",\"platform\":\"youtube\",\"niche\":\"AI creator tools\",\"audience\":\"US\",\"tone\":\"dramatic\",\"content_type\":\"shorts\",\"youtube_handle\":\"@creatorflowlab\",\"language\":\"en\",\"about\":\"Shorts about practical AI automation for creators.\"}"
curl http://127.0.0.1:8000/api/channels
```

Then use the returned `channel.id` for:

```bash
curl -X POST http://127.0.0.1:8000/api/ai/generate-ideas ^
  -H "Content-Type: application/json" ^
  -d "{\"channel_id\":1,\"topic\":\"Shorts automation\",\"count\":3}"

curl -X POST http://127.0.0.1:8000/api/ai/generate-script ^
  -H "Content-Type: application/json" ^
  -d "{\"channel_id\":1,\"idea_title\":\"3 AI Shorts Automation Mistakes\",\"hook\":\"Most creators automate the wrong step first\",\"duration_seconds\":30,\"style\":\"fast-paced\",\"target_audience\":\"solo YouTube creators\"}"

curl -X POST http://127.0.0.1:8000/api/ai/generate-seo ^
  -H "Content-Type: application/json" ^
  -d "{\"channel_id\":1,\"script_text\":\"This is a short test script for CreatorFlow AI that is long enough to pass validation.\",\"title\":\"3 AI Shorts Automation Mistakes\",\"script_id\":1,\"target_keywords\":[\"youtube shorts automation\",\"ai creator tools\"],\"platform\":\"youtube\"}"

curl -X POST http://127.0.0.1:8000/api/ai/analyze-channel ^
  -H "Content-Type: application/json" ^
  -d "{\"channel_id\":1,\"recent_context\":\"New creator channel focused on AI Shorts workflows.\"}"

curl http://127.0.0.1:8000/api/history

curl -OJ http://127.0.0.1:8000/api/export/excel
```

## Swagger JSON examples

Open `http://127.0.0.1:8000/docs` and use these request bodies.

### POST /api/channels

```json
{
  "name": "CreatorFlow Lab",
  "platform": "youtube",
  "niche": "AI creator tools",
  "audience": "US",
  "tone": "dramatic",
  "content_type": "shorts",
  "youtube_handle": "@creatorflowlab",
  "language": "en",
  "about": "Shorts about practical AI automation for creators."
}
```

### POST /api/ai/generate-ideas

```json
{
  "channel_id": 1,
  "topic": "Shorts automation",
  "count": 3
}
```

### POST /api/ai/generate-script

```json
{
  "channel_id": 1,
  "idea_title": "3 AI Shorts Automation Mistakes",
  "hook": "Most creators automate the wrong step first.",
  "duration_seconds": 30,
  "style": "fast-paced",
  "target_audience": "solo YouTube creators"
}
```

### POST /api/ai/generate-seo

```json
{
  "channel_id": 1,
  "script_text": "Stop scrolling. Here is the simple CreatorFlow AI workflow that turns one idea into a Shorts script, SEO title, hashtags, and a content calendar.",
  "title": "AI Shorts Automation Workflow",
  "script_id": 1,
  "target_keywords": ["youtube shorts automation", "ai creator tools"],
  "platform": "youtube"
}
```

### POST /api/ai/analyze-channel

```json
{
  "channel_id": 1,
  "recent_context": "New creator channel focused on AI Shorts workflows."
}
```

## 6) Automated smoke tests

The smoke suite uses a temporary SQLite database and the AI fallback path, so it does not need PostgreSQL or a Groq key.

```bash
pytest
```

## Temporary MVP behavior

- Authentication is not implemented yet.
- Endpoints currently use `demo_user_id=1`.
- Demo user is auto-created on startup.
- If `GROQ_API_KEY` is missing or Groq returns invalid JSON, the API returns safe fallback content with `used_fallback=true`.
