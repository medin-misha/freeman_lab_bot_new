# Analysis Module Guide For AI Agents

## Purpose

`app.modules.analysis_module` is a simple feature module for analysis
registrations.

Right now the module is responsible for:

- the `AnalysisRegistration` model;
- create / get / list / delete HTTP operations;
- publishing an `admin.analysis_registration.created` RabbitMQ notification
  after an analysis registration is created.

If a change is not about storing an analysis registration or notifying
downstream consumers about it, it probably does not belong here.

## Dependency On `system`

`analysis_module` must build on top of `app.modules.system` instead of
duplicating it.

Current dependencies:

- `Base` and `TimestampMixin` for the ORM model;
- `CRUD` for `create`, `get`, `list`, and `delete`.

Rule:

- all standard CRUD operations should go through `CRUD` from `system`;
- custom service code is only appropriate where there is domain validation or a
  side effect, such as RMQ publishing.

## What This Module Owns

The module owns one entity:

- `AnalysisRegistration` — a record saying that a user registered for an
  analysis.

The module also owns one external side effect:

- notifying `admin_bot` about analysis registration creation through
  `rmq_publisher`.

The module should not:

- store admin-facing processing states for the registration;
- know UI details of `admin_bot` or `frontend_bot`;
- duplicate RabbitMQ transport logic.

## Module Map

### `models/`

Important file:

- `models/analysis_registration.py`

Expectations:

- `AnalysisRegistration` inherits from `Base` and `TimestampMixin`;
- `user_id` uses `ForeignKey("telegramuser.id", ondelete="CASCADE")`;
- `user` is a `relationship` to `TelegramUser`;
- multiple registrations per user are allowed.

### `schemas/`

Important file:

- `schemas/analysis_registration.py`

Expectations:

- `AnalysisRegistrationCreate` is the input schema for creation;
- `AnalysisRegistrationRead` is the API response schema;
- `AnalysisRegistrationAdminNotificationUser` and
  `AnalysisRegistrationAdminNotificationPayload` are RMQ payload schemas.

### `services/`

Important file:

- `services/analysis_registration_service.py`

Expectations:

- `create_analysis_registration` validates that `TelegramUser` exists, then
  calls `CRUD.create(...)`, then publishes an RMQ event;
- `get_analysis_registration` uses `CRUD.get(...)`;
- `list_analysis_registrations` uses `CRUD.get(...)` with equality filters;
- `delete_analysis_registration` uses `CRUD.delete(...)`;
- `publish_analysis_registration_created_to_admin_bot` publishes the event
  through `rmq_publisher`.

Do not move standard read or delete flows back to handwritten SQLAlchemy
queries without a clear reason.

### `handlers.py`

Contains a thin FastAPI router with the `/analysis-registrations` prefix.

Routes:

- `POST /api/analysis-registrations`
- `GET /api/analysis-registrations/{id}`
- `GET /api/analysis-registrations`
- `DELETE /api/analysis-registrations/{id}`

Expectations:

- handlers stay thin;
- database and publish logic live in service functions;
- `SessionDep` is defined through
  `Annotated[AsyncSession, Depends(database.get_session)]`.

## Handler Contracts

### `POST /api/analysis-registrations`

1. Accepts `AnalysisRegistrationCreate`.
2. Calls the `create_analysis_registration(...)` service.
3. Returns `AnalysisRegistrationRead` with `201 Created`.

### `GET /api/analysis-registrations/{id}`

1. Calls `get_analysis_registration(...)`.
2. Reads the registration through `CRUD.get(...)`.
3. Returns `404` if the record is missing.

### `GET /api/analysis-registrations`

1. Calls `list_analysis_registrations(...)`.
2. Uses `CRUD.get(...)` internally.
3. Supports `page`, `limit`, and `user_id`.

### `DELETE /api/analysis-registrations/{id}`

1. Calls `delete_analysis_registration(...)`.
2. Uses `CRUD.delete(...)` internally.
3. Returns `{"status": "ok"}`.

## RMQ Contract

Current event:

- event: `admin.analysis_registration.created`
- queue: `admin.analysis_registration.created`

Payload must contain:

- analysis registration data;
- compact Telegram user data.

Use `rmq_publisher` from `app.modules.rmq_module`.
Do not import `aio-pika` directly in this module.

## Change Rules

Good changes:

- add domain validation around analysis registration creation;
- extend the notification payload if a downstream consumer needs it;
- add new simple fields to `AnalysisRegistration` if they clearly belong to the
  registration itself.

Unwanted changes:

- turning the module into a request-processing workflow engine;
- writing low-level RMQ transport code inside the feature module;
- duplicating CRUD operations with handwritten queries without a real need;
- moving business logic into `handlers.py`.

## Safety Notes

- if the ORM model changes, update `models`, `schemas`, migrations, and
  documentation together;
- if the RMQ event or payload changes, update both `README.md` and this file;
- if you need a new filtered list flow, first see whether `system.CRUD` can be
  extended in a general way instead of adding an `analysis_module`-only special
  case.

## Practical Agent Workflow

When working in this module:

1. First check whether the task can be solved through the existing `CRUD`.
2. Add service-layer logic only for domain validation and side effects.
3. Keep `handlers.py` transport-thin.
4. Do not silently change the RMQ contract — it is an integration point for
   `admin_bot`.
5. After any contract change, update the local module documentation.
