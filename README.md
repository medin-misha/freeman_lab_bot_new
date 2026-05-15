# freeman_lab_bot_new

Монорепозиторий проекта Freeman Lab.

## Структура

```text
.
├── apps/
│   ├── admin_bot/
│   ├── backend/
│   └── frontend_bot/
├── infra/
│   └── docker-compose.yml
└── README.md
```

## Сервисы

- `apps/backend` — FastAPI backend, миграции Alembic, файловый и RMQ-модули.
- `apps/admin_bot` — административный Telegram-бот.
- `apps/frontend_bot` — пользовательский Telegram-бот.
- `infra/docker-compose.yml` — локальная инфраструктура: PostgreSQL, RabbitMQ, MinIO.

## Базовые команды

Поднять инфраструктуру:

```bash
docker compose -f infra/docker-compose.yml up -d
```

Установить зависимости backend:

```bash
cd apps/backend
uv sync
```

Запустить backend:

```bash
cd apps/backend
uv run uvicorn main:app --reload
```

Запустить Telegram-ботов:

```bash
cd apps/admin_bot
uv run python main.py
```

```bash
cd apps/frontend_bot
uv run python main.py
```
