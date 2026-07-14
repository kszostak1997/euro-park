# Euro Park: backend

FastAPI REST API for the parking-application management system.

## Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0 (async) + Alembic migrations
- PostgreSQL (docker) or SQLite (default local dev)
- Pydantic v2 (validation)
- PyJWT (access + refresh tokens) + `pwdlib[argon2]` (password hashing)
- `slowapi` (rate limiting)
- pytest + pytest-asyncio + httpx (tests), ruff + black (lint/format)

## Project structure

```
app/
├── controllers/   # FastAPI routers (HTTP layer)
├── services/      # business logic
├── repositories/  # data access (SQLAlchemy queries)
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic request/response models + validators
├── middleware/    # ASGI middleware
├── core/          # config, security, db session, exceptions, logging, rate limiting
└── main.py         # app factory, router registration, startup seeding
tests/              # pytest suite (API-level, via ASGI test client)
alembic/            # migrations
```

## Running locally (without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # defaults to SQLite, no changes needed for local dev
alembic upgrade head
fastapi dev app/main.py
```

API available at http://localhost:8000, interactive docs at http://localhost:8000/docs (Swagger) and http://localhost:8000/redoc.

## Running with Docker

See the [root README](../README.md). `docker compose up --build` builds this service against PostgreSQL and applies migrations automatically on container start (see `Dockerfile`'s `CMD`).

## Environment variables

Defined in `.env` (see `.env.example`), loaded via `app/core/config.py`:

| Variable | Default | Notes |
|---|---|---|
| `APP_NAME` | `Euro Park API` | Shown in OpenAPI docs |
| `DEBUG` | `true` | When `false`, a real (non-placeholder) `JWT_SECRET` is required at startup |
| `DATABASE_URL` | `sqlite+aiosqlite:///./euro_park.db` | Use `postgresql+asyncpg://user:pass@host:5432/db` for Postgres |
| `JWT_SECRET` | `PLACEHOLDER` | **Must be overridden with a real random secret outside local dev.** Generate with `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `JWT_ALGORITHM` | `HS256` | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | JSON array (pydantic-settings) of allowed frontend origins; override if the frontend is served from a different origin |

## Seeded accounts

On every startup, `app/core/seed.py` idempotently ensures three accounts exist (see root README for the table of credentials): one `ADMIN`, one `MANAGER`, one `USER`.

## Tests

```bash
pytest
```

52 tests covering auth, applications (CRUD + ownership + status transitions), barrier access checks, manager review workflow, admin user management, rate limiting, and seeding.

## Lint / format

```bash
ruff check .
black --check .
```

## API overview

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | none | Create a `USER` account |
| POST | `/auth/login` | none | Get access + refresh token pair |
| POST | `/auth/refresh` | none | Rotate a refresh token for a new pair |
| GET | `/auth/current-user` | Bearer | Current user profile |
| POST | `/applications` | Bearer | Submit a parking application |
| GET | `/applications` | Bearer | List own applications |
| GET | `/applications/{id}` | Bearer | Get own application |
| PATCH | `/applications/{id}` | Bearer | Edit own application (only while `PENDING`/`NEEDS_CHANGES`) |
| POST | `/barrier/check-access` | none | Barrier hardware: check whether a plate has an `APPROVED` application |
| GET | `/manager/applications` | Manager/Admin | List all applications (paginated, filterable by status, sortable) |
| POST | `/manager/applications/{id}/approve` | Manager/Admin | Approve |
| POST | `/manager/applications/{id}/reject` | Manager/Admin | Reject |
| POST | `/manager/applications/{id}/request-changes` | Manager/Admin | Send back for changes (comment required) |
| POST | `/manager/applications/{id}/revoke` | Manager/Admin | Revert an `APPROVED` application back to `PENDING` |
| GET | `/manager/users` | Manager/Admin | List users (paginated) |
| POST | `/manager/users` | Admin | Create a user with a given role |
| PATCH | `/manager/users/{id}/role` | Admin | Change a user's role |
| DELETE | `/manager/users/{id}` | Admin | Delete a user |

Full request/response schemas are in the Swagger UI (`/docs`).
