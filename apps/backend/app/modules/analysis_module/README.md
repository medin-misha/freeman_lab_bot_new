# Analysis Module

`analysis_module` — прикладной backend-модуль для хранения записей на разбор.

Сейчас модуль intentionally simple и отвечает только за:

- хранение записей `AnalysisRegistration` в базе данных;
- создание, чтение, список и удаление записей через HTTP API;
- отправку RMQ-уведомления в `admin_bot` при создании записи на разбор.

Модуль построен поверх `app.modules.system` и переиспользует его общий
CRUD-слой вместо локального дублирования запросов.

## Структура

```text
analysis_module/
├── __init__.py
├── handlers.py
├── models/
│   ├── __init__.py
│   └── analysis_registration.py
├── schemas/
│   ├── __init__.py
│   └── analysis_registration.py
├── services/
│   ├── __init__.py
│   └── analysis_registration_service.py
├── AGENTS.md
└── README.md
```

## Зависимости

Модуль использует:

- `Base` и `TimestampMixin` из `app.modules.system` для ORM-модели;
- `CRUD` из `app.modules.system` для `create / get / list / delete`;
- `TelegramUser` из `app.modules.telegram_module` для проверки владельца записи;
- `rmq_publisher` из `app.modules.rmq_module` для уведомления `admin_bot`.

## Основная модель

### `AnalysisRegistration`

Находится в [models/analysis_registration.py](models/analysis_registration.py).

`AnalysisRegistration` хранит простую запись пользователя на разбор.

Поля:

- `id: int` — первичный ключ;
- `created_at: datetime` — время создания записи;
- `updated_at: datetime` — время последнего обновления;
- `user_id: int` — внешний ключ на `TelegramUser.id`.

Связи:

- `user` — `relationship` к `TelegramUser`;
- `ForeignKey("telegramuser.id", ondelete="CASCADE")`, поэтому удаление
  пользователя удаляет и связанные записи на разбор.

Несколько записей на одного пользователя разрешены. Уникального ограничения на
`user_id` нет.

## Pydantic-схемы

Схемы находятся в [schemas/analysis_registration.py](schemas/analysis_registration.py).

Основные DTO:

- `AnalysisRegistrationCreate` — входная схема создания записи;
- `AnalysisRegistrationRead` — схема ответа API;
- `AnalysisRegistrationAdminNotificationUser` — вложенная схема пользователя
  для RMQ;
- `AnalysisRegistrationAdminNotificationPayload` — payload события для
  `admin_bot`.

## Service Layer

Сервис находится в
[services/analysis_registration_service.py](services/analysis_registration_service.py).

Сервис отвечает только за ту логику, которую не должен знать общий `CRUD`:

- проверка, что `TelegramUser` существует перед созданием;
- сбор payload для `admin_bot`;
- публикация RMQ-сообщения после успешного создания записи.

Константы уведомления:

- event: `admin.analysis_registration.created`
- queue: `admin.analysis_registration.created`

Payload включает:

- данные записи: `id`, `created_at`, `updated_at`, `user_id`;
- краткие Telegram-данные пользователя: `telegram_id`, `username`,
  `first_name`, `last_name`.

## HTTP API

Router объявлен в [handlers.py](handlers.py) с префиксом
`/analysis-registrations`.

### Endpoints

- `POST /api/analysis-registrations`
- `GET /api/analysis-registrations/{id}`
- `GET /api/analysis-registrations?user_id=...&page=...&limit=...`
- `DELETE /api/analysis-registrations/{id}`

### `POST /api/analysis-registrations`

Принимает `AnalysisRegistrationCreate` и:

1. проверяет существование `TelegramUser`;
2. создаёт запись через `CRUD.create()`;
3. публикует RMQ-уведомление в `admin_bot`;
4. возвращает `AnalysisRegistrationRead` со статусом `201 Created`.

### `GET /api/analysis-registrations/{id}`

Возвращает одну запись через `CRUD.get(...)`.

### `GET /api/analysis-registrations`

Возвращает список записей через `CRUD.get(...)`.

Поддерживает:

- `page`
- `limit`
- `user_id` — equality-фильтр по владельцу

### `DELETE /api/analysis-registrations/{id}`

Удаляет запись через `CRUD.delete(...)` и возвращает `{"status": "ok"}`.

## Экспорт модуля

В [__init__.py](__init__.py) наружу экспортируются:

- `AnalysisRegistration`
- `create_analysis_registration`
- `get_analysis_registration`
- `list_analysis_registrations`
- `delete_analysis_registration`
- `router`

## Правила изменений

Хорошие изменения в этом модуле:

- добавление новых полей, которые действительно относятся к записи на разбор;
- расширение RMQ payload, если это нужно `admin_bot`;
- добавление простой доменной валидации вокруг создания.

Нежелательные изменения:

- дублирование CRUD-логики, которая уже есть в `system`;
- тяжёлая бизнес-логика прямо в `handlers.py`;
- прямой импорт низкоуровневого RabbitMQ-клиента вместо `rmq_publisher`.

## Практические заметки

- если меняется модель `AnalysisRegistration`, синхронно обновляйте `models`,
  `schemas` и Alembic-миграции;
- если меняется RMQ event/queue/payload, обновляйте и `README.md`, и
  `AGENTS.md`;
- если появятся новые сценарии кроме create/get/list/delete, сначала
  проверьте, можно ли опереться на `system.CRUD`, и только потом добавляйте
  кастомный service-код.
