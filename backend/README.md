# AI Interviewer Backend

FastAPI backend for the AI Interviewer platform, built with a robust, scalable architecture.

## 📁 Folder Structure (Laravel-style)

The project follows a **Layered Architecture** with **snake_case** conventions (PEP 8 compliant).

```
backend/
├── app/                        # 🧠 Main Application Logic
│   ├── agents/                 # 🤖 LiveKit Worker Agents
│   │   └── server.py           # Worker entry point
│   │
│   ├── controllers/            # 📡 HTTP Layer (API Handlers)
│   ├── middleware/             # 🛡️ HTTP Middleware
│   │
│   ├── services/               # 💼 Business Logic Layer
│   │   ├── core/               # Shared logic (Intelligence, Gamification)
│   │   ├── interview_service.py
│   │   └── ...
│   │
│   ├── repositories/           # 💾 Data Access Layer (Repository Pattern)
│   ├── models/                 # �️ Database Models (SQLAlchemy)
│   └── schemas/                # 📋 Pydantic Schemas (Validation)
│
├── config/                     # ⚙️ Configuration (Settings, Stages)
├── database/                   # �️ Database Migrations & Seeds
│   ├── migrations/             # Alembic versions
│   └── seeders/                # Initial data
│
├── routes/                     # 🚦 Route Definitions
├── tests/                      # 🧪 Unit & Integration Tests
├── main.py                     # 🚀 Application Bootstrap
└── docker-compose.yml          # 🐳 Local Development
```

## 🚀 Quick Start

### 1. Prerequisites
- Docker & Docker Compose (Mandatory)
- Python 3.11+ (local)

### 2. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configure your keys:
```env
GOOGLE_API_KEY=your_gemini_api_key  # Required for GenAI v1.0
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/interviewer
```

### 3. Run with Docker (Recommended)
We use Docker for a consistent development environment.

```bash
# Start all services (Backend + Worker + DB)
docker-compose up --build

# Run migrations (auto-runs on startup, but manual command:)
docker-compose run --rm backend alembic upgrade head
```

## 🧪 Testing

Run strict tests inside the container:

```bash
docker-compose run --rm backend pytest
```

## � Architecture

### The "Laravel-style" Pattern
We separate concerns to ensure scalability:
1.  **Routes (`routes/`)**: Define URLs.
2.  **Controllers (`app/controllers`)**: Validate inputs, call Services.
3.  **Services (`app/services`)**: Business logic (AI, scoring, complex flows).
4.  **Repositories (`app/repositories`)**: Abstraction over Database.
5.  **Models (`app/models`)**: Database schema definition.

### AI Integration
- **SDK**: `google-genai` (v1.0+)
- **Logic**: Located in `app/services/core/intelligence`
- **Prompts**: Managed dynamically via `PromptManager`.

## ☁️ Deployment

### Cloud Run (GCP)
```bash
# Deploy API
gcloud builds submit --config=cloudbuild.yaml

# Deploy Worker
gcloud builds submit --config=cloudbuild_worker.yaml
```
