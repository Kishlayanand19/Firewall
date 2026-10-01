# Thought Firewall

**A Cognitive Cybersecurity Layer for Human Decision-Making**

Thought Firewall is an Agentic AI-powered platform that detects manipulation, misinformation, persuasion tactics, emotional influence, propaganda, and social engineering in digital content.

## Architecture

```
┌─────────────────┐     SSE/REST      ┌──────────────────────────────┐
│  Next.js 15     │ ◄──────────────► │  FastAPI Backend              │
│  React + TW      │                  │  7 AI Agents + Orchestrator    │
│  Framer Motion  │                  │  LangChain + OpenAI            │
│  Recharts       │                  │  PostgreSQL / SQLite           │
└─────────────────┘                   └──────────────────────────────┘
```

### AI Agents

1. **Content Analysis** — framing, urgency, clickbait, entities
2. **Emotional Influence** — fear, outrage, tribalism, dopamine hooks
3. **Persuasion & Manipulation** — scarcity, authority, gaslighting, propaganda
4. **Misinformation Detection** — factuality, credibility, coordinated signals
5. **Social Engineering** — phishing, scams, impersonation
6. **Behavioral Reasoning** — synthesis and threat scoring
7. **User Safety Advisor** — reframing and critical thinking guidance

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker (optional)
- OpenAI API key (optional — heuristic fallback included)

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Copy and configure environment
cp ../.env.example .env
# Set OPENAI_API_KEY for full AI capabilities

# Run (SQLite fallback if PostgreSQL unavailable)
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
cp ../.env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

npm run dev
```

App: http://localhost:3000

### 3. Docker (Full Stack)

```bash
docker compose up postgres backend -d
cd frontend && npm run dev
```

## Features

- **Live Content Scanner** — paste text, stream real-time agent analysis
- **Feed Simulation** — analyze social posts with threat highlighting
- **Threat Dashboard** — gauges, radar charts, manipulation trends
- **AI Agent Monitor** — agent status, communication graph
- **Explainability Panel** — why content was flagged
- **AI Reframing** — safe interpretation of manipulative content
- **Risk Timeline** — manipulation progression visualization
- **Dark/Light mode** — cyberpunk glassmorphism UI
- **REST API** — full programmatic access

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analyze` | Full analysis |
| POST | `/api/v1/analyze/stream` | SSE streaming analysis |
| GET | `/api/v1/reports/{id}` | Get report |
| GET | `/api/v1/reports/dashboard/stats` | Dashboard data |
| GET | `/api/v1/agents/registry` | Agent list |

## Scoring System

| Score | Range | Description |
|-------|-------|-------------|
| Manipulation Score | 0-100 | Overall persuasive pressure |
| Emotional Pressure | 0-100 | Emotional manipulation intensity |
| Misinformation Probability | 0-100 | Likelihood of false claims |
| Trustworthiness Index | 0-100 | Content reliability |
| Cognitive Threat Level | 0-100 | Combined human risk |

**Threat Levels:** Safe → Mild Influence → Manipulative → Dangerous → Coordinated Attack

## Deployment

### Vercel (Frontend)
```bash
cd frontend
vercel --prod
# Set NEXT_PUBLIC_API_URL to your backend URL
```

### Railway/Render (Backend)
- Deploy `backend/` with start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `DATABASE_URL`, `OPENAI_API_KEY`, `CORS_ORIGINS`

## Environment Variables

See `.env.example` for full list.

## Tech Stack

- **Frontend:** Next.js 15, React, TypeScript, TailwindCSS, Framer Motion, Recharts, Shadcn-style UI
- **Backend:** FastAPI, LangChain, OpenAI, SQLAlchemy, PostgreSQL
- **AI:** Multi-agent orchestration with heuristic fallback
- **Deploy:** Docker, Vercel, Railway/Render

## License

MIT
