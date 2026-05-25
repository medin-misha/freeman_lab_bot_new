# Core Request Module Guide For AI Agents

## Purpose

`app.modules.core_request_module` is a feature module for core program
applications submitted by the miniapp.

Right now the module is responsible for:

- the `CoreRequest` model;
- legacy-compatible `POST /api/core/submit` handling;
- `get / list / patch / delete` HTTP operations;
- updating the linked `UserProfile` from miniapp submit data;
- publishing an `admin.core_request.created` RabbitMQ notification after a
  request is created;
- notifying `stats_module` about the first submitted core application so that
  `UserBotStats.core_application_submitted` is updated automatically.

If a change is not about storing a core request, adapting the miniapp contract,
or notifying downstream consumers about creation, it probably does not belong
here.

## Dependency On `system`

`core_request_module` must build on top of `app.modules.system` instead of
duplicating it.

Current dependencies:

- `Base` and `TimestampMixin` for the ORM model;
- `CRUD` for `create`, `get`, `list`, `patch`, and `delete`.

Rule:

- all standard CRUD operations should go through `CRUD` from `system`;
- custom service code is appropriate only for domain validation, profile sync,
  and RMQ side effects.

## Dependency On `stats_module`

`core_request_module` calls `stats_module` to update aggregates after
creating a `CoreRequest`.

Import rule: import only from the specific submodule path
`app.modules.stats_module.services.user_bot_stats_service` — never from
`app.modules.stats_module` directly. This avoids any risk of circular imports
because `stats_module.__init__` triggers loading of
`stats_module.services.user_bot_stats_service`, which in turn imports
`core_request_module.models`. Importing through the direct submodule path keeps
the dependency unambiguous.

The call is **write-only through the service**: `core_request_module` never
reads from stats tables.

## What This Module Owns

The module owns one entity:

- `CoreRequest` — a record saying that a user submitted a core application.

The module also owns two domain-specific responsibilities:

- adapting the old miniapp payload to the new backend user/profile model;
- notifying `admin_bot` about core request creation through `rmq_publisher`.

The module should not:

- become a general user-profile editing module;
- duplicate Telegram user lifecycle logic from `telegram_module`;
- duplicate RabbitMQ transport logic.

## Module Map

### `models/`

Important file:

- `models/core_request.py`

Expectations:

- `CoreRequest` inherits from `Base` and `TimestampMixin`;
- `priorities` is stored as JSON;
- `user_id` uses `ForeignKey("telegramuser.id", ondelete="CASCADE")`;
- `user` is a `relationship` to `TelegramUser`.

### `schemas/`

Important file:

- `schemas/core_request.py`

Expectations:

- `CoreFormSubmit` mirrors the legacy miniapp submit payload;
- `CoreRequestCreate` is the internal create schema;
- `CoreRequestUpdate` is the patch schema for the stored request;
- `CoreRequestRead` is the API response schema;
- `CoreRequestAdminNotificationUser` and
  `CoreRequestAdminNotificationPayload` are RMQ payload schemas.

### `services/`

Important file:

- `services/core_request_service.py`

Expectations:

- `submit_core_form` validates the miniapp payload, finds `TelegramUser`,
  updates `UserProfile`, creates `CoreRequest`, calls
  `UserBotStatsService.update_core_application_submitted` on the same session,
  then publishes an RMQ event;
- `get_core_request`, `list_core_requests`, `patch_core_request`,
  `delete_core_request` use `CRUD`;
- `publish_core_request_created_to_admin_bot` publishes through
  `rmq_publisher`.

Do not move standard read, patch, or delete flows back to handwritten
SQLAlchemy queries without a clear reason.

### `handlers.py`

Contains a thin FastAPI router with the `/core` prefix.

Routes:

- `POST /api/core/submit`
- `GET /api/core`
- `GET /api/core/{id}`
- `PATCH /api/core/{id}`
- `DELETE /api/core/{id}`

Expectations:

- handlers stay thin;
- miniapp adaptation logic lives in service functions;
- `SessionDep` is defined through
  `Annotated[AsyncSession, Depends(database.get_session)]`.

## Handler Contracts

### `POST /api/core/submit`

1. Accepts `CoreFormSubmit`.
2. Resolves `TelegramUser` by `telegram_id`.
3. Updates `UserProfile`.
4. Creates `CoreRequest`.
5. Updates `UserBotStats.core_application_submitted` via `UserBotStatsService`
   (idempotent: only sets the flag on the first submission).
6. Publishes `admin.core_request.created`.
7. Returns `CoreRequestRead` with `201 Created`.

### `GET /api/core`

1. Calls `list_core_requests(...)`.
2. Uses `CRUD.get(...)` internally.
3. Supports `page`, `limit`, `search`, and `field`.

### `PATCH /api/core/{id}`

1. Accepts `CoreRequestUpdate`.
2. Updates only the request record.
3. Does not mutate `UserProfile`.

## RMQ Contract

Current event:

- event: `admin.core_request.created`
- queue: `admin.core_request.created`

Payload must contain:

- core request data;
- compact Telegram user data;
- profile fields relevant to the admin flow.

Use `rmq_publisher` from `app.modules.rmq_module`.
Do not import `aio-pika` directly in this module.

## Change Rules

Good changes:

- add domain validation around submit flow;
- extend the notification payload if a downstream consumer needs it;
- add new simple fields to `CoreRequest` if they clearly belong to the request.

Unwanted changes:

- turning the module into a complex application workflow engine;
- writing low-level RMQ transport code inside the feature module;
- moving business logic into `handlers.py`;
- editing `telegram_module` schemas or handlers unless it is strictly required.

## Safety Notes

- if the ORM model changes, update `models`, `schemas`, migrations, and
  documentation together;
- if the RMQ event or payload changes, update both `README.md` and this file;
- the route `/api/core/submit` is a compatibility contract for the miniapp, so
  do not silently rename or remove it.
