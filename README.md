<div align="center">

# ⚔️ DSArena

### A Modern DSA Learning Platform Built Around Striver's A2Z Sheet

*Structured roadmaps, progress tracking, XP, daily streaks, and Google Authentication — all in one place.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Auth-3ECF8E.svg?logo=supabase&logoColor=white)](https://supabase.com/)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black.svg?logo=vercel&logoColor=white)](https://dsarena-two.vercel.app)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](#-contributing)

[Live Demo](https://dsarena-two.vercel.app) · [Report Bug](https://github.com/bhuvan-0412/DSArena/issues) · [Request Feature](https://github.com/bhuvan-0412/DSArena/issues)

---

</div>

## 🌐 Live Demo

| | |
|---|---|
| **Frontend** | [https://dsarena-two.vercel.app](https://dsarena-two.vercel.app) |
| **Backend** | Deployment in progress |
| **API Docs** | Available locally at `http://localhost:8000/docs` |

---

## 📌 Overview

**DSArena** is an open-source, full-stack DSA learning platform that structures the entire [Striver A2Z Sheet](https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/) into an interactive, gamified learning experience.

Instead of manually tracking a spreadsheet, DSArena gives you:
- A fully navigable roadmap broken into Steps → Sections → Topics
- Embedded YouTube video lessons for every topic
- XP, streaks, and achievement tracking to stay motivated
- Google sign-in via Supabase Auth

---

## ⚡ Features

### 🗺️ Roadmap & Curriculum
- **Striver A2Z Roadmap** — complete curriculum organized into Steps, Sections, and individual topic nodes
- **Lesson Pages** — dedicated page per topic with embedded video, notes, and lesson tabs
- **Resume Learning** — picks up exactly where you left off
- **Search & Filter** — find any topic across the full roadmap instantly
- **Breadcrumb Navigation** — always know where you are in the curriculum

### 📊 Progress & Gamification
- **Progress Tracking** — per-topic and overall completion percentage
- **XP System** — earn XP on lesson completion
- **Daily Streaks** — maintain daily study habits
- **Learning Activity Heatmap** — GitHub-style calendar of your study activity
- **Achievements** — milestone badges displayed on your profile
- **Quick Stats** — live counts of completed, in-progress, and remaining topics

### 🔐 Authentication
- **Google OAuth** via Supabase Auth
- Session persistence across page reloads
- Protected routes — unauthenticated users are redirected to sign-in

### 🛠️ Admin
- **Curriculum Management Panel** (`/admin/curriculum`) — view, audit, and manage the full roadmap tree, video coverage, and import status

### 🎨 UI & Experience
- Responsive layout — works on desktop and mobile
- Dark-mode-ready design system
- Smooth animations and interactive hover states
- Modern dashboard with stats, recent activity, and next steps

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| [Next.js](https://nextjs.org/) | 15 (App Router, Turbopack) | Framework |
| [React](https://react.dev/) | 19 | UI library |
| [TypeScript](https://www.typescriptlang.org/) | 5 | Type safety |
| [Tailwind CSS](https://tailwindcss.com/) | 3.4 | Styling |
| [Supabase JS](https://supabase.com/docs/reference/javascript) | 2 | Auth client |
| [Lucide React](https://lucide.dev/) | latest | Icons |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | 0.111 | API framework |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.0 | ORM |
| [Alembic](https://alembic.sqlalchemy.org/) | 1.13 | DB migrations |
| [Pydantic](https://docs.pydantic.dev/) | 2.7 | Validation |
| [Uvicorn](https://www.uvicorn.org/) | 0.30 | ASGI server |
| [Python](https://www.python.org/) | 3.11 | Runtime |

### Infrastructure
| Service | Role |
|---|---|
| [Supabase](https://supabase.com/) | Authentication (Google OAuth) + PostgreSQL (production) |
| [Vercel](https://vercel.com/) | Frontend hosting |
| SQLite | Local development database |

---

## 🏗️ Architecture

```
User (Browser)
     │
     ▼
Next.js 15 Frontend  ──── Supabase Auth (Google OAuth)
     │
     ▼
FastAPI Backend  (REST API / JSON)
     │
     ▼
SQLAlchemy ORM
     │
     ├── SQLite (local development)
     └── PostgreSQL via Supabase (production)
```

Authentication is handled entirely through **Supabase Auth**. The frontend obtains a session token after Google OAuth and passes it to the backend for user identity resolution.

---

## 📂 Project Structure

```
DSArena/
├── backend/                          # FastAPI Python backend
│   ├── alembic/                      # Database migration scripts
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints.py          # Root API router
│   │   │   └── v1/                   # Versioned endpoints
│   │   │       ├── activity.py       # Heatmap & activity tracking
│   │   │       ├── adaptive.py       # Adaptive learning logic
│   │   │       ├── admin.py          # Admin curriculum endpoints
│   │   │       ├── ai.py             # AI mentor endpoints
│   │   │       ├── auth.py           # Auth sync
│   │   │       ├── contest.py        # Contest endpoints
│   │   │       ├── engagement.py     # Streaks & rewards
│   │   │       ├── roadmap.py        # Roadmap, lessons & progress
│   │   │       └── users.py          # User profile & XP
│   │   ├── core/
│   │   │   ├── config.py             # Settings & env vars
│   │   │   └── database.py           # SQLAlchemy engine setup
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   └── services/                 # Business logic & importers
│   ├── .env.example                  # Backend env template
│   ├── pyrightconfig.json            # Pyright/Pylance config
│   ├── requirements.txt              # Python dependencies
│   └── seed.py                       # Curriculum seeder
│
├── frontend/                         # Next.js 15 frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/               # Auth route group
│   │   │   ├── (dashboard)/          # Protected app routes
│   │   │   │   ├── admin/curriculum/ # Curriculum management panel
│   │   │   │   ├── contests/         # Contest arena
│   │   │   │   ├── dashboard/        # Main student dashboard
│   │   │   │   ├── profile/          # User profile & achievements
│   │   │   │   ├── roadmap/          # Roadmap overview & lesson pages
│   │   │   │   │   └── node/[nodeId] # Individual lesson page
│   │   │   │   └── settings/         # User settings
│   │   │   ├── auth/callback/        # Supabase OAuth callback
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx              # Landing page
│   │   ├── components/
│   │   │   ├── activity/             # Learning activity heatmap
│   │   │   ├── ai/                   # AI mentor drawer & settings
│   │   │   ├── auth/                 # Supabase auth provider
│   │   │   ├── contest/              # Contest cards & charts
│   │   │   ├── dashboard/            # Dashboard widgets
│   │   │   ├── engagement/           # Study calendar & engagement
│   │   │   ├── roadmap/              # Roadmap & lesson components
│   │   │   └── shared/               # Sidebar, navbar, providers
│   │   ├── hooks/                    # Custom React hooks
│   │   └── lib/
│   │       ├── supabase/             # Supabase client (browser/server)
│   │       └── services/             # API service layer
│   ├── .env.local                    # Local env vars (gitignored)
│   └── package.json
│
├── docs/                             # Project documentation & reports
├── supabase/
│   └── schema.sql                    # Supabase database schema
└── README.md
```

---

## ⚙️ Local Setup

### Prerequisites
- **Node.js** v18+
- **Python** 3.11+
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/bhuvan-0412/DSArena.git
cd DSArena
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Seed the database with curriculum data
python seed.py

# Start the development server
uvicorn app.main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`  
Interactive API docs: `http://localhost:8000/docs`

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Copy and configure environment variables
cp .env.example .env.local
# Edit .env.local with your Supabase project credentials

# Start the development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

---

## 🔑 Environment Variables

### Frontend (`frontend/.env.local`)

```env
# Supabase project credentials
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# Backend API (local development)
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL (found in project Settings → API) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase public anon key (safe to expose in browser) |
| `NEXT_PUBLIC_API_URL` | FastAPI backend base URL |

### Backend (`backend/.env`)

```env
# Supabase Auth & Service Credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret

# Database
DATABASE_URL=sqlite:///dsarena.db
```

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for admin operations (keep secret) |
| `SUPABASE_JWT_SECRET` | Used to verify Supabase JWT tokens on the backend |
| `DATABASE_URL` | SQLAlchemy connection string — SQLite for local dev, PostgreSQL for production |

> [!CAUTION]
> Never commit your `.env` or `.env.local` files. Both are listed in `.gitignore`.

---

## 📊 Current Status

| Component | Status |
|---|---|
| Frontend | ✅ Deployed on Vercel |
| Google Auth (Supabase) | ✅ Configured & live |
| Roadmap & Lesson Pages | ✅ Implemented |
| Progress & XP Tracking | ✅ Implemented |
| Learning Activity Heatmap | ✅ Implemented |
| Admin Curriculum Panel | ✅ Implemented |
| Backend | ⏳ Deployment in progress |
| Monaco Code Editor | 🔲 Planned |
| AI Mentor | 🔲 Planned |

---

## 🗺️ Roadmap

- [x] Striver A2Z curriculum engine (Steps → Sections → Topics)
- [x] Embedded YouTube video lessons
- [x] XP system & progress tracking
- [x] Daily streaks
- [x] Learning activity heatmap
- [x] Google Authentication via Supabase
- [x] Admin curriculum management
- [x] Responsive roadmap UI with search & filter
- [ ] Backend cloud deployment
- [ ] Leaderboards & rankings
- [ ] Revision mode (spaced repetition)
- [ ] Monaco code editor + Judge0 execution
- [ ] Interactive quizzes per topic
- [ ] Mock interview simulator
- [ ] Contest tracker
- [ ] Company-wise DSA sheet filters
- [ ] AI mentor chat assistant

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit using [Conventional Commits](https://www.conventionalcommits.org/)
   ```bash
   git commit -m "feat: add spaced repetition revision mode"
   ```
4. **Push** to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** against the `main` branch

### Branch Naming
| Type | Format | Example |
|---|---|---|
| Feature | `feature/name` | `feature/revision-mode` |
| Bug fix | `fix/name` | `fix/auth-redirect` |
| Docs | `docs/name` | `docs/update-readme` |

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](./LICENSE) for details.

---

## 👏 Credits & Acknowledgements

DSArena's curriculum is structured around **Striver's A2Z DSA Sheet** by [Take U Forward](https://takeuforward.org/).

> [!IMPORTANT]
> DSArena is an independent, open-source project and is not officially affiliated with or endorsed by Take U Forward or any third-party content creator.

- [FastAPI](https://fastapi.tiangolo.com/) — High-performance Python API framework
- [Next.js](https://nextjs.org/) — The React framework for the web
- [Supabase](https://supabase.com/) — Open-source Firebase alternative
- [Tailwind CSS](https://tailwindcss.com/) — Utility-first CSS framework
- [Lucide Icons](https://lucide.dev/) — Clean, consistent icon set

---

## 📫 Contact

- **GitHub**: [bhuvan-0412/DSArena](https://github.com/bhuvan-0412/DSArena)
- **Issues**: [Report bugs & request features](https://github.com/bhuvan-0412/DSArena/issues)
- **Discussions**: [Community Q&A](https://github.com/bhuvan-0412/DSArena/discussions)

<div align="center">
  <sub>Built with ❤️ by the DSArena open-source team.</sub>
</div>
