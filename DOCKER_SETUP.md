# Docker Setup

Этот документ описывает, как запускать проект через Docker Compose и куда
класть переменные окружения.

## Структура запуска

Проект разбит на два compose-стека:

- `infra/docker-compose.yml` — инфраструктура
- `docker-compose.apps.yml` — приложения

Инфраструктура поднимает:

- `postgres`
- `rabbitmq`
- `minio`
- `minio-init`

Приложения поднимают:

- `telegram-bot-api`
- `backend`
- `core-mini-app`
- `frontend-bot`
- `admin-bot`
- `caddy`

Оба compose-файла работают через общую Docker-сеть `freeman_lab_net`.

## Куда класть env

Есть два уровня переменных окружения.

### 1. Корневой `.env`

Файл: `.env` в корне репозитория.

Он нужен именно для Docker Compose и используется в:

- `infra/docker-compose.yml`
- `docker-compose.apps.yml`

Что хранить в корневом `.env`:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_BOT_API_PORT`
- `BACKEND_PORT`
- `CORE_MINI_APP_API_URL`
- `CADDY_SITE_ADDRESS`
- `CADDY_HTTP_PORT`
- `CADDY_HTTPS_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `RABBITMQ_DEFAULT_USER`
- `RABBITMQ_DEFAULT_PASS`
- `RABBITMQ_PORT`
- `RABBITMQ_MANAGEMENT_PORT`
- `MINIO_ROOT_USER`
- `MINIO_ROOT_PASSWORD`
- `MINIO_BUCKET`
- `MINIO_PORT`
- `MINIO_CONSOLE_PORT`

Шаблон:

- [.env.example](/home/misha/code/freeman_lab_bot_new/.env.example)

### 2. Сервисные `.env`

Эти файлы читаются уже самими контейнерами через `env_file`.

Файлы:

- `apps/backend/.env`
- `apps/frontend_bot/.env`
- `apps/admin_bot/.env`

Шаблоны:

- [apps/backend/.env.example](/home/misha/code/freeman_lab_bot_new/apps/backend/.env.example)
- [apps/frontend_bot/.env.example](/home/misha/code/freeman_lab_bot_new/apps/frontend_bot/.env.example)
- [apps/admin_bot/.env.example](/home/misha/code/freeman_lab_bot_new/apps/admin_bot/.env.example)

## Что хранить в каждом файле

### Корневой `.env`

Минимально:

```env
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=your_telegram_api_hash

CORE_MINI_APP_API_URL=/api
CADDY_SITE_ADDRESS=localhost

POSTGRES_DB=fastapi_template
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

RABBITMQ_DEFAULT_USER=app
RABBITMQ_DEFAULT_PASS=app

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET=backend
```

Важно:

- `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` обязательны для local Telegram Bot API
- это не bot token, а данные вашего Telegram API приложения

### `apps/backend/.env`

Этот файл хранит backend-настройки приложения.

Минимально:

```env
debug=true
database_pool_size=5
database_max_overflow=10
database_pool_timeout=30
database_pool_recycle=1800

rabbitmq_enabled=true
rabbitmq_default_exchange=app.events
rabbitmq_default_exchange_type=direct
rabbitmq_default_queue=app.events.default
rabbitmq_default_routing_key=app.events.default
rabbitmq_prefetch_count=10
rabbitmq_consumer_enabled=true
rabbitmq_publish_timeout=5
rabbitmq_reconnect_interval=5
rabbitmq_debug_endpoints_enabled=false
```

Важно:

- для Docker `database_url`, `amqp_url`, `minio_*` задаются через `docker-compose.apps.yml`
- в `apps/backend/.env` оставляйте только backend-специфичные runtime-настройки
- каталог `apps/backend/alembic/versions` смонтирован в контейнер backend, поэтому
  `init`-миграция и последующие файлы миграций должны храниться на хосте

### `apps/frontend_bot/.env`

Минимально:

```env
TOKEN=your_frontend_bot_token
BACKEND_API_PREFIX=/api
BACKEND_REQUEST_TIMEOUT=10
AUTH_CACHE_MAX_SIZE=1000
BOT_PARSE_MODE=HTML
CHANNEL=@your_channel
CORE_URL=https://example.com/app/
```

Важно:

- `CHANNEL` обязателен
- `CORE_URL` обязателен и должен указывать на Telegram mini app Ядра
- в Docker `BACKEND_URL`, `TELEGRAM_BOT_API_URL` и `AMQP_URL` задаются
  через `docker-compose.apps.yml`; не дублируйте их в сервисном `.env`
- `TOKEN` должен быть реальным токеном именно пользовательского бота

### `apps/admin_bot/.env`

Минимально:

```env
TOKEN=your_admin_bot_token
BACKEND_API_PREFIX=/api
BACKEND_REQUEST_TIMEOUT=10
AUTH_CACHE_MAX_SIZE=1000
BOT_PARSE_MODE=HTML
ADMINS_CHAT_IDS=123456789,987654321
```

Важно:

- `ADMINS_CHAT_IDS` — список chat id через запятую
- `TOKEN` должен быть токеном admin-бота
- в Docker `BACKEND_URL`, `TELEGRAM_BOT_API_URL` и `AMQP_URL` задаются
  через `docker-compose.apps.yml`; не дублируйте их в сервисном `.env`

## Порядок запуска

### 1. Подготовить env-файлы

Создать:

- `.env` в корне
- `apps/backend/.env`
- `apps/frontend_bot/.env`
- `apps/admin_bot/.env`
- `apps/core-mini-app/.env` по желанию, только для локального Vite запуска вне Docker

Проще всего:

```bash
cp .env.example .env
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend_bot/.env.example apps/frontend_bot/.env
cp apps/admin_bot/.env.example apps/admin_bot/.env
```

После этого заполнить реальные значения:

- Telegram bot tokens
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `CHANNEL`
- `ADMINS_CHAT_IDS`
- `CADDY_SITE_ADDRESS`:
  - `localhost` для локальной проверки
  - публичный IP сервера для деплоя без домена

### 2. Поднять инфраструктуру

```bash
docker compose -f infra/docker-compose.yml up -d
```

### 3. Поднять приложения

```bash
docker compose -f docker-compose.apps.yml up -d --build
```

### 4. Проверить сервисы

Backend:

```bash
curl http://localhost:8000/api/system/health
```

MinIO console:

```text
http://localhost:9001
```

RabbitMQ management:

```text
http://localhost:15672
```

Local Telegram Bot API:

```text
http://localhost:8081
```

Mini App через Caddy:

```text
https://localhost/app/
```

Для сервера без домена откройте:

```text
https://<PUBLIC_SERVER_IP>/app/
```

Важно:

- `core-mini-app` ходит в backend через `Caddy` route `/api/*`
- `Caddy` слушает `80` и `443`, поэтому эти порты должны быть открыты на сервере
- при деплое без домена проверьте в браузере, какой именно сертификат выдался на IP:
  публично-доверенный или `Caddy Local Authority`

## Остановка

Остановить приложения:

```bash
docker compose -f docker-compose.apps.yml down
```

Остановить инфраструктуру:

```bash
docker compose -f infra/docker-compose.yml down
```

Если нужно удалить и тома:

```bash
docker compose -f docker-compose.apps.yml down -v
docker compose -f infra/docker-compose.yml down -v
```

## Важные замечания

- Для файлов до 1000 МБ нужен именно local Telegram Bot API.
- Боты используют общий том `telegram_bot_api_data`, чтобы читать большие файлы
  напрямую без полной загрузки в память.
- Backend теперь отдаёт файлы из MinIO потоково, поэтому скачивание больших
  файлов не должно упираться в RAM backend-процесса.
- Если поменяете имя сети вручную, оба compose-файла должны ссылаться на одно и
  то же имя.
