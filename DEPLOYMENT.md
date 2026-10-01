# Thought Firewall — Production Deployment Guide

Secure deployment: **Vercel (frontend)** + **Railway or Render (backend)** + **hosted PostgreSQL**.

---

## Security checklist (before going public)

- [ ] Rotate any API key ever committed to git or shared in chat
- [ ] Never commit `.env` files (root `.gitignore` enforces this)
- [ ] Set `ENVIRONMENT=production`, `DEBUG=false`, `ENABLE_DOCS=false` on the API
- [ ] Set `CORS_ORIGINS` to your **HTTPS** Vercel/custom domain only (no `*`, no localhost)
- [ ] Use hosted PostgreSQL; do not expose SQLite or local DB ports
- [ ] Store `OPENAI_API_KEY` only in Railway/Render secrets (never `NEXT_PUBLIC_*`)
- [ ] Set `NEXT_PUBLIC_API_URL` in Vercel to your public API URL
- [ ] Confirm `/docs` returns 404 on production API
- [ ] Confirm health endpoint does not leak config (`GET /api/v1/health` → `{"status":"healthy"}` only)

---

## 1. PostgreSQL (hosted)

Create a database on **Railway**, **Render**, **Neon**, or **Supabase**.

Copy the connection string. For SQLAlchemy async use:

```text
postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE
```

Render/Heroku often provide `postgresql://...` — the backend auto-converts to `postgresql+asyncpg://`.

---

## 2. Backend (Railway)

### Option A — Dockerfile (recommended)

1. New project → **Deploy from GitHub**
2. Service root: `backend`
3. Add **PostgreSQL** plugin; link `DATABASE_URL`
4. Variables:

| Variable | Value |
|----------|--------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `ENABLE_DOCS` | `false` |
| `OPENAI_API_KEY` | your OpenRouter/OpenAI key |
| `OPENAI_BASE_URL` | `https://openrouter.ai/api/v1` |
| `OPENAI_MODEL` | `openai/gpt-4o-mini` |
| `CORS_ORIGINS` | `https://your-app.vercel.app,https://www.yourdomain.com` |
| `RATE_LIMIT` | `30/minute` |
| `ANALYZE_RATE_LIMIT` | `10/minute` |

5. Generate domain: `https://your-api.up.railway.app`
6. Health check path: `/api/v1/health`

### Option B — Render

Use `render.yaml` in the repo or create a **Web Service** with Docker context `./backend`.

---

## 3. Frontend (Vercel)

1. Import repository; set **Root Directory** to `frontend`
2. Environment variables (Production):

| Variable | Example |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | `https://your-api.up.railway.app/api/v1` |
| `NEXT_PUBLIC_WS_URL` | `wss://your-api.up.railway.app` (if using WS later) |

3. Deploy. Vercel provides HTTPS automatically.

4. Update backend `CORS_ORIGINS` with the final Vercel URL.

---

## 4. Custom domain (optional)

- **Vercel:** Project → Domains → add `www.yourdomain.com`
- **Railway/Render:** Add custom domain to API service
- Update `CORS_ORIGINS` and `NEXT_PUBLIC_API_URL` to match

---

## 5. Docker (self-hosted)

```bash
cp .env.example .env
# Edit .env with strong POSTGRES_PASSWORD, CORS_ORIGINS, OPENAI_API_KEY

docker compose -f docker-compose.production.yml up -d --build
```

Do not publish PostgreSQL port `5432` to the internet. Terminate TLS with nginx/Caddy in front.

---

## 6. Local development (unchanged)

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

---

## Production security features (implemented)

| Area | Implementation |
|------|----------------|
| Secrets | Server-side env only; sanitized `.env.example` |
| CORS | Explicit origin list; localhost stripped in production |
| Rate limits | Global + stricter analyze limits (`slowapi`) |
| Request size | 1 MB body cap middleware |
| Errors | Generic 500 messages; no stack traces to clients |
| OpenAPI | Disabled when `ENABLE_DOCS=false` or production |
| Health | Minimal JSON in production |
| Input | Length limits, content sanitization, injection hints |
| Headers | HSTS (prod), CSP, X-Frame-Options, nosniff |
| Logging | Secret redaction in structured logs |
| Frontend | CSP connect-src to API origin; no secret env vars |

---

## Key rotation

If a key was exposed (chat, commit, screenshot):

1. Revoke at OpenRouter/OpenAI dashboard
2. Issue new key
3. Update Railway/Render variable only
4. Redeploy backend (no frontend change)

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS error in browser | Add exact Vercel URL (with `https://`) to `CORS_ORIGINS` |
| `NEXT_PUBLIC_API_URL is required` on build | Set variable in Vercel before build |
| 413 Request too large | Content exceeds 50k chars or body > 1 MB |
| 429 Too Many Requests | Rate limit; wait or increase `ANALYZE_RATE_LIMIT` |
| DB connection fails | Use `postgresql+asyncpg://` or plain `postgresql://` (auto-fixed) |

---

## Files reference

| File | Purpose |
|------|---------|
| `.env.example` | Full template (placeholders only) |
| `frontend/.env.example` | Local frontend vars |
| `backend/.env.example` | Local backend vars |
| `docker-compose.production.yml` | Production compose |
| `railway.toml` | Railway hints |
| `render.yaml` | Render blueprint |
| `vercel.json` | Vercel monorepo root |
