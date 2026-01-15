# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI backend for an AI-powered mock interview platform. Uses LiveKit for real-time voice/video, Google Gemini for AI, and Clerk for authentication.

## Commands

### Development
```bash
# Start all services (backend, worker, postgres, adminer)
docker-compose up --build

# Run backend only (local development)
uvicorn main:app --reload --port 8000

# Run LiveKit worker agent
python -m app.agents.server dev
```

### Database
```bash
# Run migrations
docker-compose run --rm backend alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Testing
```bash
# Run all tests (inside container)
docker-compose run --rm backend pytest

# Run single test file
pytest tests/test_services.py -v

# Run specific test
pytest tests/test_services.py::test_function_name -v
```

## Architecture

### Layered Pattern
- **Controllers** (`app/controllers/`): HTTP handlers, validate input, call services
- **Services** (`app/services/`): Business logic layer
- **Repositories** (`app/repositories/`): Database abstraction (Repository Pattern)
- **Models** (`app/models/`): SQLAlchemy ORM models
- **Schemas** (`app/schemas/`): Pydantic validation schemas

### Core Services (`app/services/core/`)
- `database.py`: AsyncSession factory, use `get_db` for FastAPI dependency
- `dependencies.py`: DI container with `UnitOfWork` pattern for multi-repo operations
- `exceptions.py`: Custom `AppException` subclasses for structured error responses
- `intelligence/`: AI logic module
  - `prompt_manager.py`: Manages system prompts and personas
  - `shadow_monitor.py`: Real-time conversation analysis
  - `stage_manager.py`: Interview stage configuration
  - `personas/`: YAML persona definitions
  - `templates/`: Jinja2 prompt templates

### LiveKit Agent (`app/agents/server.py`)
The `interview_agent` function is the entry point for real-time voice sessions. It:
1. Fetches session context from database
2. Builds system prompt via `prompt_manager`
3. Initializes STT (Google), LLM (Gemini), TTS (Cartesia), VAD (Silero)
4. Runs shadow analysis after each user turn for dynamic prompt injection

### Key Models
- `InterviewApplication`: User's application with resume/JD context (parent)
- `InterviewSession`: Individual interview session linked to application

### Authentication
Uses Clerk JWT verification. Key middleware:
- `verify_clerk_token`: Requires valid JWT, returns user_id
- `optional_auth`: Allows unauthenticated access

## Configuration

All settings in `config/settings.py` via Pydantic Settings, loaded from `.env`:
```python
from config.settings import get_settings
settings = get_settings()
```

Key environment variables: `DATABASE_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `GOOGLE_API_KEY`, `GEMINI_MODEL`

## Conventions

- **snake_case** for all Python code (PEP 8)
- Async database operations with `AsyncSession`
- Routes defined in `routes/api.py`, controllers in `app/controllers/`
