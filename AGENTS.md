# Freeman Lab — Monorepo Guide for Agents

Telegram bots + FastAPI backend + Vue mini apps for the "Психология Масштаба"
project. This file covers cross-cutting context; each app has its own
`AGENTS.md`/`README.md` with details — read those before changing an app.

## Repository map

| Path | What it is | Stack |
| ---- | ---------- | ----- |
| `apps/backend` | REST API, DB, file storage, RMQ events | FastAPI, SQLAlchemy (async), Alembic, `uv` |
| `apps/frontend_bot` | User-facing Telegram bot | aiogram 3, polling, `uv` |
| `apps/admin_bot` | Admin Telegram bot | aiogram 3, polling, `uv` |
| `apps/core-mini-app` | "Ядро" Telegram mini app (served at `/`) | Vue 3, Vite, pnpm |
| `apps/admin-mini-app` | Admin panel mini app (served at `/admin/`) | Vue 3, Vite, pnpm |
| `apps/html-screen-builder` | Standalone AI Studio tool for bot HTML screens; NOT part of the Docker stack | React, Gemini API |
| `infra/` | Infra compose (PostgreSQL, RabbitMQ, MinIO, Loki, Promtail, Prometheus, cAdvisor, Grafana) + `Caddyfile` | Docker Compose |
| `docker-compose.apps.yml` | Apps compose (bots, backend, mini apps, local Bot API, Caddy) | Docker Compose |
| `docs/plans/` | Design notes | — |

## How things connect

- Bots talk to `backend` over HTTP (`/api` prefix) and consume RabbitMQ events.
- Bots use a **local Telegram Bot API** container (large files, up to 2 GB);
  both bots mount the shared `telegram_bot_api_data` volume read-only to read
  downloaded files from disk.
- Caddy routes: `/api/*` → backend, `/admin*` → admin-mini-app,
  `/logs*` → grafana, everything else → core-mini-app.
- The `freeman_lab_net` Docker network is created by the infra stack —
  always start `infra/docker-compose.yml` before `docker-compose.apps.yml`.

## Commands

```bash
# Python apps (from the app directory)
uv sync                          # install deps
uv run pytest                    # run tests
uv run uvicorn main:app --reload # backend only
uv run python main.py            # bots

# Mini apps (from the app directory)
pnpm install && pnpm dev

# Full stack
docker compose -f infra/docker-compose.yml up -d
docker compose -f docker-compose.apps.yml up -d --build
```

Migrations: Alembic, run inside `apps/backend`; the `alembic/versions`
directory is bind-mounted into the backend container, so migration files
generated in Docker land on the host and must be committed.

## Environment conventions

- Root `.env` (template `.env.example`) is read by Docker Compose itself —
  infra credentials, ports, Caddy/ZeroSSL, Telegram API id/hash.
- Per-service `.env` files (`apps/*/.env`, templates alongside) are read by
  the containers via `env_file` — bot tokens and app runtime settings.
- In Docker, `BACKEND_URL`, `TELEGRAM_BOT_API_URL`, `AMQP_URL`,
  `database_url`, `minio_*` are injected by `docker-compose.apps.yml`;
  do NOT duplicate them in service `.env` files.
- Bot settings use pydantic `validation_alias` — env var names must match
  exactly (e.g. frontend_bot requires `CHANNEL`, not `CHANNEL_ID`).

## Conventions

- Backend settings/env vars are lowercase (`debug`, `database_url`);
  bot env vars are UPPERCASE (`TOKEN`, `CHANNEL`).
- Code comments are written in Russian across Python apps.
- Commit messages in English; keep commits atomic.
- Docs: `README.md` in Russian, `AGENTS.md`/`CLAUDE.md` in English.
- Launch/env documentation lives in `DOCKER_SETUP.md` — keep it in sync when
  changing compose files, Caddy routes, or `.env.example` templates.
