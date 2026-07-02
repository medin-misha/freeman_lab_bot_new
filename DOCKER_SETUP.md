# Docker Setup

Этот документ описывает, как запускать проект через Docker Compose и куда
класть переменные окружения.

## Структура запуска

Проект разбит на два compose-стека:

- `infra/docker-compose.yml` — инфраструктура (поднимается первой, создаёт сеть)
- `docker-compose.apps.yml` — приложения

Инфраструктура поднимает:

- `postgres` — база данных
- `rabbitmq` — брокер сообщений
- `minio` — S3-совместимое файловое хранилище
- `minio-init` — одноразовый контейнер, создаёт бакет
- `loki` — агрегация логов
- `promtail` — сборщик логов контейнеров
- `prometheus` — хранилище метрик (retention 30 дней)
- `cadvisor` — метрики контейнеров (CPU, RAM, сеть) для Prometheus
- `grafana` — UI для просмотра логов и метрик

Приложения поднимают:

- `telegram-bot-api` — local Telegram Bot API (файлы до 2 ГБ)
- `backend` — FastAPI backend
- `core-mini-app` — mini app «Ядро» (Vue, отдаётся nginx)
- `admin-mini-app` — mini app админ-панели (Vue, отдаётся nginx)
- `frontend-bot` — пользовательский Telegram-бот
- `admin-bot` — административный Telegram-бот
- `caddy` — reverse proxy с HTTPS

Оба compose-файла работают через общую Docker-сеть `freeman_lab_net`.
Сеть создаёт инфраструктурный стек, поэтому он должен подниматься первым.

## Маршрутизация Caddy

Caddy слушает `80`/`443` и раздаёт трафик по путям (`infra/Caddyfile`):

| Путь       | Сервис          |
| ---------- | --------------- |
| `/api/*`   | `backend:8000`  |
| `/logs*`   | `grafana:3000`  |
| `/admin*`  | `admin-mini-app` |
| остальное  | `core-mini-app` |

То есть mini app «Ядро» доступен с корня сайта (`https://<host>/`),
а не с отдельного пути.

## Куда класть env

Есть два уровня переменных окружения.

### 1. Корневой `.env`

Файл: `.env` в корне репозитория. Шаблон: [.env.example](.env.example).

Его читает сам Docker Compose и подставляет значения в оба compose-файла.

| Группа | Переменные |
| ------ | ---------- |
| Local Bot API | `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_BOT_API_PORT` |
| Backend | `BACKEND_PORT`, `CORE_MINI_APP_API_URL` |
| Caddy | `CADDY_SITE_ADDRESS`, `CADDY_HTTP_PORT`, `CADDY_HTTPS_PORT` |
| ZeroSSL | `ZEROSSL_KID`, `ZEROSSL_MAC_KEY` |
| PostgreSQL | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` |
| RabbitMQ | `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`, `RABBITMQ_PORT`, `RABBITMQ_MANAGEMENT_PORT` |
| MinIO | `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_BUCKET`, `MINIO_PORT`, `MINIO_CONSOLE_PORT` |
| Grafana | `GRAFANA_PORT`, `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD` |

Важно:

- `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` обязательны для local Telegram Bot API.
  Это **не** bot token, а данные вашего Telegram API-приложения
  (получить на <https://my.telegram.org>).
- `ZEROSSL_KID` / `ZEROSSL_MAC_KEY` нужны только для HTTPS на публичном IP
  без домена (EAB-креды: <https://app.zerossl.com> → Developer → EAB Credentials).
  Для локального запуска (`CADDY_SITE_ADDRESS=localhost`) их можно не заполнять.

### 2. Сервисные `.env`

Эти файлы читаются уже самими контейнерами через `env_file`:

- `apps/backend/.env` — шаблон [apps/backend/.env.example](apps/backend/.env.example)
- `apps/frontend_bot/.env` — шаблон [apps/frontend_bot/.env.example](apps/frontend_bot/.env.example)
- `apps/admin_bot/.env` — шаблон [apps/admin_bot/.env.example](apps/admin_bot/.env.example)

Для mini apps сервисный `.env` (`VITE_API_URL`) нужен только при локальном
запуске Vite вне Docker — в Docker значение передаётся build-аргументом
из `CORE_MINI_APP_API_URL`.

## Что хранить в каждом файле

### `apps/backend/.env`

Backend-специфичные runtime-настройки:

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

- для Docker `database_url`, `amqp_url`, `minio_*` задаются через
  `docker-compose.apps.yml` — не дублируйте их здесь
- каталог `apps/backend/alembic/versions` смонтирован в контейнер backend,
  поэтому файлы миграций хранятся на хосте и попадают в git

### `apps/frontend_bot/.env`

```env
TOKEN="your_frontend_bot_token"
BACKEND_API_PREFIX="/api"
BACKEND_REQUEST_TIMEOUT="10"
AUTH_CACHE_MAX_SIZE="1000"
BOT_PARSE_MODE="HTML"
CHANNEL="@your_channel"
CORE_URL="https://your-domain.com/"
```

Важно:

- `CHANNEL` обязателен — публичный username канала для проверки подписки
  (именно `CHANNEL`, бот не прочитает переменную с другим именем)
- `CORE_URL` обязателен — полный URL mini app «Ядро»; так как Caddy отдаёт
  его с корня сайта, обычно это просто `https://<ваш-домен-или-IP>/`
- `TOKEN` — токен именно пользовательского бота
- в Docker `BACKEND_URL`, `TELEGRAM_BOT_API_URL` и `AMQP_URL` задаются
  через `docker-compose.apps.yml`; не дублируйте их в сервисном `.env`

### `apps/admin_bot/.env`

```env
TOKEN="your_admin_bot_token"
BACKEND_API_PREFIX="/api"
BACKEND_REQUEST_TIMEOUT="10"
AUTH_CACHE_MAX_SIZE="1000"
BOT_PARSE_MODE="HTML"
ADMINS_CHAT_IDS="123456789,987654321"
ADMIN_URL="https://your-domain.com/admin/"
```

Важно:

- `ADMINS_CHAT_IDS` — список chat id через запятую; только эти пользователи
  получают доступ к боту
- `ADMIN_URL` — полный URL админ-панели (mini app), Caddy отдаёт её с `/admin/`
- `TOKEN` — токен admin-бота
- в Docker `BACKEND_URL`, `TELEGRAM_BOT_API_URL` и `AMQP_URL` задаются
  через `docker-compose.apps.yml`; не дублируйте их в сервисном `.env`

## Порядок запуска

### 1. Подготовить env-файлы

```bash
cp .env.example .env
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend_bot/.env.example apps/frontend_bot/.env
cp apps/admin_bot/.env.example apps/admin_bot/.env
```

После этого заполнить реальные значения:

- Telegram bot tokens (`TOKEN` в обоих ботах)
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`
- `CHANNEL`, `CORE_URL` (frontend_bot)
- `ADMINS_CHAT_IDS`, `ADMIN_URL` (admin_bot)
- `CADDY_SITE_ADDRESS`:
  - `localhost` для локальной проверки
  - публичный IP сервера для деплоя без домена (плюс `ZEROSSL_*`)

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

Web-интерфейсы:

| Сервис | URL | Доступ |
| ------ | --- | ------ |
| Mini app «Ядро» | `https://localhost/` | — |
| Админ-панель | `https://localhost/admin/` | — |
| Grafana | `http://localhost:3000` или `https://localhost/logs/` | `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` |
| RabbitMQ management | `http://localhost:15672` | `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS` |
| MinIO console | `http://localhost:9001` | `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` |
| Local Bot API | `http://localhost:8081` | — |

Если в `CADDY_SITE_ADDRESS` указан домен или публичный IP (не `localhost`),
HTTPS-адреса проверяйте через него: `https://<CADDY_SITE_ADDRESS>/...`.
Запрос на `https://localhost/` при этом упадёт с TLS-ошибкой — Caddy выдаёт
сертификат только на адрес из `CADDY_SITE_ADDRESS`.

Нюанс: с самого сервера его публичный адрес может быть недоступен
(hairpin NAT — например, в GCP). Проверяйте с внешней машины или локально
с подстановкой адреса:

```bash
curl --resolve <CADDY_SITE_ADDRESS>:443:127.0.0.1 https://<CADDY_SITE_ADDRESS>/api/system/health
```

Вместо «сырого» публичного IP удобно использовать `sslip.io`:
домен вида `1-2-3-4.sslip.io` автоматически резолвится в IP `1.2.3.4`,
и на него можно получить обычный публично-доверенный сертификат.

Grafana: источники данных Loki (логи) и Prometheus (метрики контейнеров)
подключаются автоматически через провижининг, дашборд «Apps Overview» — тоже.
Логи смотрите через **Explore → Loki**.

Важно:

- mini apps ходят в backend через Caddy-маршрут `/api/*`
- Caddy слушает `80` и `443` — эти порты должны быть открыты на сервере
- при деплое без домена проверьте в браузере, какой сертификат выдался на IP:
  публично-доверенный (ZeroSSL) или `Caddy Local Authority`

## Остановка

Остановить приложения:

```bash
docker compose -f docker-compose.apps.yml down
```

Остановить инфраструктуру:

```bash
docker compose -f infra/docker-compose.yml down
```

Если нужно удалить и тома (данные БД, файлы MinIO, логи — безвозвратно):

```bash
docker compose -f docker-compose.apps.yml down -v
docker compose -f infra/docker-compose.yml down -v
```

## Важные замечания

- Для файлов больше 20 МБ (до 2 ГБ) нужен именно local Telegram Bot API —
  облачный Bot API такие файлы не отдаёт.
- Боты используют общий том `telegram_bot_api_data` (read-only), чтобы читать
  большие файлы напрямую с диска без полной загрузки в память.
- Backend отдаёт файлы из MinIO потоково, поэтому скачивание больших файлов
  не упирается в RAM backend-процесса.
- Если поменяете имя сети вручную, оба compose-файла должны ссылаться на одно
  и то же имя.
- `apps/html-screen-builder` — вспомогательный инструмент (AI Studio) для
  вёрстки HTML-экранов ботов; в Docker-стек не входит и для запуска проекта
  не нужен.
