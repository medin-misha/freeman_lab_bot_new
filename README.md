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

Подробная инструкция по Docker-запуску и env-файлам:

- [DOCKER_SETUP.md](/home/misha/code/freeman_lab_bot_new/DOCKER_SETUP.md)

Поднять инфраструктуру:

```bash
docker compose -f infra/docker-compose.yml up -d
```

Поднять приложения:

```bash
docker compose -f docker-compose.apps.yml up -d --build
```

Для local Telegram Bot API нужны `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` в
окружении shell или в корневом `.env`, который читает Docker Compose.

Остановить приложения:

```bash
docker compose -f docker-compose.apps.yml down
```

Остановить инфраструктуру:

```bash
docker compose -f infra/docker-compose.yml down
```

Ручной локальный запуск без Docker:

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
