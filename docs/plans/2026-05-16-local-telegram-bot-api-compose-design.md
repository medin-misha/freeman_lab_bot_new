# Local Telegram Bot API And Split Compose Design

## Goal

Поднять локальный Telegram Bot API server в Docker Compose и разделить запуск
проекта на два отдельных compose-стека:

- `infra/docker-compose.yml` только для инфраструктуры;
- `docker-compose.apps.yml` только для приложений.

Цель изменений:

- дать ботам доступ к local Bot API;
- подготовить стек к обработке файлов до 1000 МБ;
- сохранить независимый запуск infra и app-слоя.

## Agreed Approach

Выбран вариант с двумя compose-файлами и общей внешней Docker-сетью:

- `infra/docker-compose.yml` поднимает `postgres`, `rabbitmq`, `minio`,
  `minio-init`;
- новый `docker-compose.apps.yml` поднимает `telegram-bot-api`, `backend`,
  `frontend_bot`, `admin_bot`;
- оба compose подключаются к одной сети `freeman_lab_net`;
- infra-стек создаёт эту сеть, app-стек использует её как `external`.

Такое разделение позволяет независимо перезапускать зависимости и приложение,
не ломая внутренний DNS и не смешивая ответственность файлов.

## Telegram File Handling

Одного local Bot API недостаточно для гигабайтных файлов, если бот продолжает
читать document в `BytesIO`.

Поэтому решение состоит из двух частей:

1. Боты переключаются на local Bot API через `TELEGRAM_BOT_API_URL` и
   `TelegramAPIServer.from_base(..., is_local=True)`.
2. При наличии локального файла бот старается открывать его напрямую из общего
   тома `telegram-bot-api-data` и стримить в backend как file-like object без
   полной загрузки в память.

Fallback остаётся прежним:

- если local file path недоступен, бот скачивает файл обычным способом.

## Compose Layout

### Infrastructure Compose

`infra/docker-compose.yml` остаётся инфраструктурным и получает:

- общую сеть `freeman_lab_net`;
- явное подключение сервисов к этой сети.

### Apps Compose

`docker-compose.apps.yml` содержит:

- `telegram-bot-api` с `TELEGRAM_LOCAL=1`;
- `backend`;
- `frontend-bot`;
- `admin-bot`.

Контейнерные адреса:

- backend -> `postgres`, `rabbitmq`, `minio`;
- frontend bot -> `backend`, `telegram-bot-api`, `rabbitmq`;
- admin bot -> `backend`, `telegram-bot-api`, `rabbitmq`.

## Config Changes

Для app-стека нужны следующие изменения:

- добавить `TELEGRAM_BOT_API_URL` в конфиг обоих ботов;
- создать Dockerfile для `frontend_bot` и `admin_bot`;
- заполнить Dockerfile для `backend`;
- обновить `.env.example` и README под контейнерный режим.

Compose должен переопределять локальные `localhost`-значения на контейнерные
имена сервисов, чтобы существующие `.env` могли оставаться удобными для
локального запуска вне Docker.

## Backend Streaming

Backend сейчас читает объект MinIO целиком в память при `GET /files/{id}`.
Для больших файлов это риск по RAM.

Поэтому download endpoint переводится на потоковую отдачу:

- S3 client открывает streaming body;
- FastAPI возвращает `StreamingResponse` поверх async generator;
- файл не буферизуется целиком в памяти backend-процесса.

## Validation

Минимальная проверка после изменений:

1. `docker compose -f infra/docker-compose.yml up -d`
2. `docker compose -f docker-compose.apps.yml up -d --build`
3. проверить доступность backend health endpoint;
4. убедиться, что оба бота стартуют и используют local Bot API;
5. проверить загрузку и последующую обработку большого файла.

## Risks

- Для local Bot API нужны реальные `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`.
- Если volume `telegram-bot-api-data` не смонтирован одинаково во все нужные
  контейнеры, local file path не будет доступен ботам.
- Файлы до 1000 МБ упираются не только в Bot API, но и в свободное место на
  диске Docker host.
