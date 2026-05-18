# Core Request Module

`core_request_module` — прикладной backend-модуль для работы с заявками на
“ядро”.

Сейчас модуль intentionally simple и отвечает только за:

- хранение записей `CoreRequest` в базе данных;
- совместимый с legacy miniapp submit endpoint `POST /api/core/submit`;
- чтение, список, patch и удаление заявок через HTTP API;
- обновление `UserProfile` по данным формы при submit;
- отправку RMQ-уведомления в `admin_bot` при создании заявки.

Модуль построен поверх `app.modules.system` и переиспользует его общий
CRUD-слой вместо локального дублирования запросов.

## Структура

```text
core_request_module/
├── __init__.py
├── handlers.py
├── models/
│   ├── __init__.py
│   └── core_request.py
├── schemas/
│   ├── __init__.py
│   └── core_request.py
├── services/
│   ├── __init__.py
│   └── core_request_service.py
├── AGENTS.md
└── README.md
```

## Зависимости

Модуль использует:

- `Base` и `TimestampMixin` из `app.modules.system` для ORM-модели;
- `CRUD` из `app.modules.system` для `create / get / list / patch / delete`;
- `TelegramUser` и `UserProfile` из `app.modules.telegram_module`;
- `rmq_publisher` из `app.modules.rmq_module` для уведомления `admin_bot`.

## Основная модель

### `CoreRequest`

Находится в [models/core_request.py](models/core_request.py).

`CoreRequest` хранит заявку пользователя на участие в программе “ядро”.

Поля:

- `id: int`
- `created_at: datetime`
- `updated_at: datetime`
- `activity: str | None`
- `request: str | None`
- `priorities: list[str] | None`
- `motivation: str | None`
- `difficulties: str | None`
- `readiness: str | None`
- `weekly_time: str | None`
- `rules: str | None`
- `payment: str | None`
- `user_id: int`

Связи:

- `user` — `relationship` к `TelegramUser`;
- `ForeignKey("telegramuser.id", ondelete="CASCADE")`, поэтому удаление
  пользователя удаляет и связанные заявки.

## Pydantic-схемы

Схемы находятся в [schemas/core_request.py](schemas/core_request.py).

Основные DTO:

- `CoreFormSubmit` — legacy-compatible payload от miniapp;
- `CoreRequestCreate` — внутренняя схема создания заявки;
- `CoreRequestUpdate` — схема patch-обновления заявки;
- `CoreRequestRead` — схема ответа API;
- `CoreRequestAdminNotificationUser` и `CoreRequestAdminNotificationPayload` —
  payload события для `admin_bot`.

## Service Layer

Сервис находится в
[services/core_request_service.py](services/core_request_service.py).

Сервис отвечает за:

- поиск `TelegramUser` по `telegram_id`;
- обновление `UserProfile` при submit;
- создание заявки через `CRUD.create()`;
- публикацию RMQ-события после успешного создания;
- стандартные `get / list / patch / delete` сценарии через `CRUD`.

Константы уведомления:

- event: `admin.core_request.created`
- queue: `admin.core_request.created`

Payload включает:

- данные заявки;
- краткие данные пользователя: `telegram_id`, `username`;
- данные профиля: `full_name`, `date_of_birth`, `city`.

## HTTP API

Router объявлен в [handlers.py](handlers.py) с префиксом `/core`.

### Endpoints

- `POST /api/core/submit`
- `GET /api/core`
- `GET /api/core/{id}`
- `PATCH /api/core/{id}`
- `DELETE /api/core/{id}`

### `POST /api/core/submit`

Принимает `CoreFormSubmit` и:

1. ищет `TelegramUser` по `telegram_id`;
2. обновляет `UserProfile` значениями `full_name`, `birth_date`, `city`;
3. создаёт заявку через `CRUD.create()`;
4. публикует RMQ-уведомление в `admin_bot`;
5. возвращает `CoreRequestRead` со статусом `201 Created`.

### `GET /api/core`

Возвращает список заявок через `CRUD.get(...)`.

Поддерживает:

- `page`
- `limit`
- `search`
- `field`

### `PATCH /api/core/{id}`

Обновляет только саму заявку. Profile fields miniapp здесь не меняются.

## Практические заметки

- если меняется модель `CoreRequest`, синхронно обновляйте `models`, `schemas`
  и Alembic-миграции;
- если меняется RMQ event/queue/payload, обновляйте и `README.md`, и
  `AGENTS.md`;
- legacy miniapp зависит от маршрута `/api/core/submit`, поэтому его нельзя
  менять без синхронного обновления клиента.
