# PlacementPilot AI

**An AI-Powered Placement Preparation & Career Guidance Platform**

PlacementPilot AI is a full-stack application that helps students prepare for campus placements using personalized study roadmaps, DSA progress tracking, resume analysis, mock interviews, and an AI mentor — all powered by **Ollama (phi2)** and **Retrieval-Augmented Generation (RAG)**.

---

## Resume Description

> Built a full-stack AI-driven placement preparation platform that generates personalized study roadmaps, analyzes resumes, tracks coding progress, provides company-specific interview preparation, and offers an AI mentor using LLMs and Retrieval-Augmented Generation (RAG).

**Tech Stack:** React · FastAPI · PostgreSQL · Ollama (phi2) · ChromaDB / Vector RAG

---

## Features

| Module | Description |
|--------|-------------|
| **User Authentication** | Register, login, JWT auth, user profile |
| **Placement Dashboard** | DSA progress, CS subjects, resume score, mock interview score, upcoming companies |
| **DSA Tracker** | **LeetCode auto-sync** — fetches solved problems, contest rating, streak & topic tags from your LeetCode profile |
| **Resume Analyzer** | Upload PDF → AI extracts text → LLM feedback (strengths, weaknesses, missing skills) |
| **Resume Rewriter** | Transform bullet points into professional resume lines |
| **AI Mentor** | Chat-based personalized guidance with conversation history |
| **Company Roadmaps** | LLM-generated weekly prep plans for Google, Amazon, Microsoft, Adobe, etc. |
| **Interview Experience RAG** | Ask questions about real interview experiences via vector search + LLM |
| **Mock Interview** | AI-generated DSA/OS/DBMS/HR questions with answer evaluation |
| **Placement Analytics** | Readiness score, strong/weak areas, topic breakdown charts |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                     │
│                   http://localhost:5173                     │
└─────────────────────────┬───────────────────────────────────┘
                          │  REST API (/api/*)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python)                    │
│                   http://localhost:8000                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │   Auth   │ │   DSA    │ │  Resume  │ │  AI Services     │ │
│  │  (JWT)   │ │ Tracker  │ │ Analyzer │ │  Mentor / Mock   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐
│ PostgreSQL  │  │ Ollama phi2  │  │ ChromaDB / Local Vector  │
│   :5432     │  │   :11434     │  │ Store (Interview RAG)    │
└─────────────┘  └──────────────┘  └──────────────────────────┘
```

---

## Project Structure

```
placement_preparation/
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Environment settings
│   │   ├── database.py             # Async SQLAlchemy
│   │   ├── dependencies.py         # JWT auth middleware
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── routers/                # API route handlers
│   │   ├── services/               # LLM, RAG, business logic
│   │   └── utils/                  # Security, PDF extraction
│   ├── scripts/
│   │   └── seed_data.py            # Seed DB + interview experiences
│   ├── alembic/                    # Database migrations
│   ├── requirements.txt
│   ├── docker-compose.yml          # PostgreSQL + Ollama
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── api/                    # Axios HTTP client
    │   ├── context/                # Auth context (React)
    │   ├── components/             # Layout, Card, etc.
    │   ├── pages/                  # All feature screens
    │   ├── types/                  # TypeScript interfaces
    │   ├── App.tsx                 # Router setup
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts              # Dev proxy → backend
```

---

## Prerequisites

Install these before running the project:

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Backend |
| **Node.js** | 18+ | Frontend |
| **Docker Desktop** | Latest | PostgreSQL + Ollama |
| **Git** | Latest | Version control |

Optional (for better RAG on Linux/macOS):
- **ChromaDB** — installed automatically via `requirements.txt` on non-Windows systems
- On **Windows**, a local JSON vector store fallback is used automatically if ChromaDB cannot be built

---

## Quick Start

### Step 1 — Clone & enter project

```bash
cd placement_preparation
```

### Step 2 — Start infrastructure (PostgreSQL + Ollama)

```bash
cd backend
docker-compose up -d
```

Wait ~10 seconds for containers to be healthy, then pull the LLM model:

```bash
docker exec placementpilot_ollama ollama pull phi2
```

Verify Ollama is running:

```bash
curl http://localhost:11434/api/tags
```

### Step 3 — Backend setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux

# Seed database (companies, DSA topics, interview experiences)
python -m scripts.seed_data

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend is now live at:
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Step 4 — Frontend setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend is now live at: **http://localhost:5173**

> The Vite dev server automatically proxies `/api` requests to `http://localhost:8000`.

### Step 5 — Use the app

1. Open http://localhost:5173
2. Click **Register** and create an account
3. Set target companies in **Profile** (e.g. `Google, Amazon, Microsoft`)
4. Explore all modules from the sidebar

---

## Environment Variables

### Backend (`backend/.env`)

Copy from `.env.example` and customize:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/placementpilot

# JWT (change in production!)
SECRET_KEY=change-me-in-production-use-a-long-random-string-at-least-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Ollama LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# ChromaDB / Vector store
CHROMA_PERSIST_DIR=./chroma_data
CHROMA_COLLECTION_NAME=interview_experiences

# CORS
CORS_ORIGINS=["*"]
```

### Frontend (`frontend/.env`)

Optional — only needed if backend is on a different host:

```env
# Leave empty to use Vite proxy (default for local dev)
VITE_API_URL=

# Production example:
# VITE_API_URL=https://api.yourdomain.com/api
```

---

## API Reference

All endpoints are prefixed with `/api`. Protected routes require `Authorization: Bearer <token>`.

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/profile` | Get current user |
| PUT | `/auth/profile` | Update profile |

### Dashboard & DSA
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Placement dashboard stats |
| GET | `/dsa/progress` | User DSA progress per topic (includes LeetCode stats) |
| PUT | `/dsa/progress` | Update problems solved / rating |
| GET | `/dsa/topics` | List all DSA topics |
| POST | `/dsa/leetcode/sync` | Sync DSA progress from LeetCode profile |
| GET | `/dsa/leetcode/preview/{username}` | Preview LeetCode stats without saving |

### Resume
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/resume/analyze` | Upload PDF, get AI analysis |
| GET | `/resume/reports` | List past resume reports |
| POST | `/resume/rewrite` | Rewrite a resume bullet point |

### AI Features
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mentor/chat` | Chat with AI mentor |
| GET | `/mentor/history` | Get chat history |
| GET | `/companies` | List target companies |
| POST | `/companies/{id}/roadmap` | Generate company roadmap |
| POST | `/interview/ask` | RAG query on interview experiences |
| POST | `/mock-interview/start` | Start mock interview session |
| POST | `/mock-interview/{id}/answer` | Submit & evaluate answer |
| GET | `/analytics` | Placement readiness analytics |

Full interactive docs: **http://localhost:8000/docs**

---

## Seeded Data

Running `python -m scripts.seed_data` populates:

**DSA Topics (10):** Arrays, Strings, Linked Lists, Stacks & Queues, Trees, Graphs, Dynamic Programming, Greedy, Binary Search, Heaps

**Companies (11):** Google, Microsoft, Amazon, Adobe, Atlassian, TCS, Infosys, Wipro, Flipkart, Razorpay, Goldman Sachs

**Interview Experiences (7):** Detailed experiences for Google, Microsoft, Amazon, Adobe, TCS, Flipkart — ingested into the vector store for RAG queries

---

## Development

### Backend — run tests / lint

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend — build for production

```bash
cd frontend
npm run build        # Output: frontend/dist/
npm run preview      # Preview production build locally
```

### Database migrations (Alembic)

```bash
cd backend
alembic upgrade head
```

### Re-seed data

```bash
cd backend
python -m scripts.seed_data
```

---

## Deployment

### Backend (Render / Railway / VPS)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Recommended services:
- **PostgreSQL:** [Neon](https://neon.tech) or [Supabase](https://supabase.com)
- **Ollama:** Self-hosted VPS with GPU, or use a remote Ollama instance
- **Backend:** [Render](https://render.com), [Railway](https://railway.app)

Set environment variables from `.env.example` in your hosting dashboard.

### Frontend (Vercel / Netlify)

```bash
cd frontend
npm run build
# Deploy the dist/ folder
```

Set `VITE_API_URL` to your deployed backend URL (e.g. `https://your-api.onrender.com/api`).

---

## LeetCode Auto-Sync

PlacementPilot fetches your **public LeetCode profile** via the official LeetCode GraphQL API and syncs it into the DSA Tracker automatically.

### What gets synced

| LeetCode Data | Mapped To |
|---------------|-----------|
| Total / Easy / Medium / Hard solved | `user_stats` totals |
| Contest rating & attended count | Contest rating |
| Submission calendar | Current streak (days) |
| Tag problem counts (Array, DP, Tree…) | DSA topic progress bars |
| Global ranking | LeetCode stats panel |

### Setup

1. Go to **Profile** → set **LeetCode Username** (e.g. `soumyapoddar16`)
2. Open **DSA Tracker** → click **Sync LeetCode**
3. Progress auto-syncs on first visit if username is set

### API usage

```bash
# Sync your profile (requires JWT token)
curl -X POST http://localhost:8000/api/dsa/leetcode/sync \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "soumyapoddar16"}'

# Preview without saving
curl http://localhost:8000/api/dsa/leetcode/preview/soumyapoddar16 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Database migration (existing installs)

If your database was created before LeetCode sync:

```bash
cd backend
python -m scripts.migrate_leetcode_columns
# or: alembic upgrade head
```

### Tag → Topic mapping

LeetCode tags are aggregated into PlacementPilot topics:

- **Arrays** ← Array, Matrix, Two Pointers, Sliding Window, Sorting
- **Strings** ← String
- **Linked Lists** ← Linked List
- **Stacks & Queues** ← Stack, Monotonic Stack
- **Trees** ← Tree, Binary Tree, Trie, Segment Tree
- **Graphs** ← DFS, BFS, Union-Find
- **Dynamic Programming** ← Dynamic Programming
- **Greedy** ← Greedy
- **Binary Search** ← Binary Search
- **Heaps** ← Ordered Set, Quickselect

---

## Troubleshooting

### Ollama not responding

```bash
# Check container is running
docker ps

# Restart Ollama
docker restart placementpilot_ollama

# Re-pull model
docker exec placementpilot_ollama ollama pull phi2

# Test directly
curl http://localhost:11434/api/generate -d '{"model":"phi2","prompt":"Hello","stream":false}'
```

### Database connection error

```bash
# Check PostgreSQL container
docker logs placementpilot_db

# Restart
docker-compose restart postgres
```

### AI features return 503

This means Ollama is unreachable. Ensure:
1. `docker-compose up -d` is running
2. `phi2` model is pulled
3. `OLLAMA_BASE_URL=http://localhost:11434` in `.env`

### ChromaDB fails on Windows

This is expected. The backend automatically falls back to a **local JSON vector store** (`backend/chroma_data/local_vectors.json`). RAG still works — no action needed.

### Frontend can't reach backend

- Ensure backend is running on port `8000`
- Check Vite proxy in `frontend/vite.config.ts`
- For production, set `VITE_API_URL` in `frontend/.env`

### CORS errors in production

Update `CORS_ORIGINS` in `backend/.env`:

```env
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

---

## Interview Talking Points

**Why FastAPI?**
Async-native, automatic OpenAPI docs, excellent Python AI ecosystem integration.

**Why React?**
Component-based UI, large ecosystem, easy to deploy on Vercel/Netlify, great for dashboards.

**Why PostgreSQL?**
Relational data (users, progress, roadmaps), ACID compliance, scales well.

**Why Ollama + phi2?**
Runs locally — no API costs, data privacy, offline capable, interview-friendly ("I used a local LLM").

**Why RAG?**
Grounds AI answers in real interview experiences stored in a vector DB, reducing hallucination.

**JWT vs Session?**
JWT is stateless — scales horizontally, perfect for SPA + API architecture.

**How would you scale to 1M users?**
- Cache LLM responses (Redis)
- Queue long AI jobs (Celery + Redis)
- Read replicas for PostgreSQL
- CDN for React static assets
- Separate Ollama inference servers with load balancing

---

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Recharts, Axios |
| Backend | FastAPI, SQLAlchemy (async), Pydantic, Alembic |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt |
| LLM | Ollama — phi2 model |
| Vector DB | ChromaDB (Linux/macOS) / Local fallback (Windows) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| PDF | pdfplumber |
| Infrastructure | Docker Compose |

---

## License

This project is built for educational and placement preparation purposes.

---

## Author

Built as part of M.Tech CSE placement preparation at NIT Rourkela.

**PlacementPilot AI** — *Navigate your placement journey with AI.*