# Freeman Lab

Монорепозиторий проекта Freeman Lab: Telegram-боты, backend и mini apps
для проекта «Психология Масштаба».

## Архитектура

```text
Telegram ──► frontend_bot ──┐
Telegram ──► admin_bot ─────┤          ┌─► PostgreSQL
                            ├─► backend ─► RabbitMQ
Mini Apps (через Caddy) ────┘          └─► MinIO
```

- Боты работают через **local Telegram Bot API** (поддержка файлов до 2 ГБ).
- Mini apps и backend публикуются наружу через **Caddy** (HTTPS).
- Логи всех контейнеров собираются в **Loki**, метрики — в **Prometheus**,
  просмотр — в **Grafana**.

## Структура

```text
.
├── apps/
│   ├── backend/             # FastAPI backend: API, Alembic, MinIO, RabbitMQ
│   ├── frontend_bot/        # Пользовательский Telegram-бот (aiogram 3)
│   ├── admin_bot/           # Административный Telegram-бот (aiogram 3)
│   ├── core-mini-app/       # Mini app «Ядро» (Vue 3 + Vite), заявки пользователей
│   ├── admin-mini-app/      # Mini app админ-панели (Vue 3 + Vite)
│   └── html-screen-builder/ # Вспомогательный AI Studio-инструмент для вёрстки
│                            #   экранов ботов (не входит в Docker-стек)
├── infra/
│   ├── docker-compose.yml   # Инфраструктура: PostgreSQL, RabbitMQ, MinIO,
│   │                        #   Loki, Promtail, Grafana, Prometheus, cAdvisor
│   ├── Caddyfile            # Маршрутизация HTTPS-трафика
│   ├── grafana/             # Провижининг datasources и дашбордов
│   ├── loki/  promtail/  prometheus/
├── docker-compose.apps.yml  # Приложения: боты, backend, mini apps, Caddy
├── docs/plans/              # Проектные заметки и дизайн-документы
└── DOCKER_SETUP.md          # Подробная инструкция по запуску и env-файлам
```

## Быстрый старт (Docker)

Полная инструкция с описанием всех переменных — в [DOCKER_SETUP.md](DOCKER_SETUP.md).

```bash
# 1. Подготовить env-файлы из шаблонов
cp .env.example .env
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend_bot/.env.example apps/frontend_bot/.env
cp apps/admin_bot/.env.example apps/admin_bot/.env

# 2. Заполнить реальные значения (минимум):
#    .env                      → TELEGRAM_API_ID, TELEGRAM_API_HASH
#    apps/frontend_bot/.env    → TOKEN, CHANNEL, CORE_URL
#    apps/admin_bot/.env       → TOKEN, ADMINS_CHAT_IDS, ADMIN_URL

# 3. Поднять инфраструктуру (создаёт сеть freeman_lab_net)
docker compose -f infra/docker-compose.yml up -d

# 4. Поднять приложения
docker compose -f docker-compose.apps.yml up -d --build
```

Проверка после запуска:

| Сервис               | URL                                     |
| -------------------- | --------------------------------------- |
| Backend health       | `http://localhost:8000/api/system/health` |
| Mini app «Ядро»      | `https://localhost/`                     |
| Админ-панель         | `https://localhost/admin/`               |
| Grafana (логи/метрики) | `http://localhost:3000` или `https://localhost/logs/` |
| RabbitMQ management  | `http://localhost:15672`                 |
| MinIO console        | `http://localhost:9001`                  |
| Local Bot API        | `http://localhost:8081`                  |

HTTPS-адреса указаны для `CADDY_SITE_ADDRESS=localhost`. Если там домен или
публичный IP — заходите через него; подробности в
[DOCKER_SETUP.md](DOCKER_SETUP.md#4-проверить-сервисы).

Остановка:

```bash
docker compose -f docker-compose.apps.yml down
docker compose -f infra/docker-compose.yml down
```

## Локальный запуск без Docker

Инфраструктуру (PostgreSQL, RabbitMQ, MinIO) всё равно проще поднять через
Docker; приложения можно запускать напрямую через `uv`:

```bash
# Backend (http://localhost:8000)
cd apps/backend
uv sync
uv run uvicorn main:app --reload

# Пользовательский бот
cd apps/frontend_bot
uv sync
uv run python main.py

# Админ-бот
cd apps/admin_bot
uv sync
uv run python main.py

# Mini apps (Vite dev server)
cd apps/core-mini-app && pnpm install && pnpm dev
cd apps/admin-mini-app && pnpm install && pnpm dev
```

При ручном запуске ботов вне Docker переменные `BACKEND_URL`,
`TELEGRAM_BOT_API_URL` и `AMQP_URL` нужно задать в сервисных `.env` —
в Docker их подставляет `docker-compose.apps.yml`.

## Документация по приложениям

- [apps/backend/README.md](apps/backend/README.md) — архитектура backend, модули, миграции
- [apps/frontend_bot/README.md](apps/frontend_bot/README.md) — устройство пользовательского бота
- [apps/admin_bot/README.md](apps/admin_bot/README.md) — устройство админ-бота
- [apps/core-mini-app/README.md](apps/core-mini-app/README.md) — mini app «Ядро»
- [apps/admin-mini-app/README.md](apps/admin-mini-app/README.md) — mini app админ-панели
