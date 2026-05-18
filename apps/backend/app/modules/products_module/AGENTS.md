# Products Module Guide For AI Agents

## Purpose

`app.modules.products_module` is a simple feature module for product requests.

Right now the module is responsible for:

- the `Product` model;
- create / get / list / delete HTTP operations;
- publishing an `admin.product.created` RabbitMQ notification after a product is created.

This is not a complex product-workflow module. If a change is not about storing a product request or notifying downstream consumers about it, it probably does not belong here.

## Dependency On `system`

`products_module` must build on top of `app.modules.system` instead of duplicating it.

Current dependencies:

- `Base` and `TimestampMixin` for the ORM model;
- `CRUD` for `create`, `get`, `list`, and `delete`.

Rule:

- all standard CRUD operations should go through `CRUD` from `system`;
- custom service code is only appropriate where there is domain validation or a side effect, such as RMQ publishing.

## What This Module Owns

The module owns one entity:

- `Product` — a record saying that a user submitted a product request.

The module also owns one external side effect:

- notifying `admin_bot` about product creation through `rmq_publisher`.

The module should not:

- store admin-facing processing states for the request;
- know UI details of `admin_bot` or `frontend_bot`;
- duplicate RabbitMQ transport logic.

## Module Map

### `models/`

Important file:

- `models/product.py`

Expectations:

- `Product` inherits from `Base` and `TimestampMixin`;
- `product_code` is stored as `String(128)` and indexed;
- `user_id` uses `ForeignKey("telegramuser.id", ondelete="CASCADE")`;
- `user` is a `relationship` to `TelegramUser`.

### `schemas/`

Important file:

- `schemas/product.py`

Expectations:

- `ProductCreate` is the input schema for creation;
- `ProductRead` is the API response schema;
- `ProductAdminNotificationUser` and `ProductAdminNotificationPayload` are RMQ payload schemas.

### `services/`

Important file:

- `services/product_service.py`

Expectations:

- `create_product` validates that `TelegramUser` exists, then calls `CRUD.create(...)`, then publishes an RMQ event;
- `get_product` uses `CRUD.get(...)`;
- `list_products` uses `CRUD.get(...)` with equality filters;
- `delete_product` uses `CRUD.delete(...)`;
- `publish_product_created_to_admin_bot` publishes the event through `rmq_publisher`.

Do not move standard read or delete flows back to handwritten SQLAlchemy queries without a clear reason.

### `handlers.py`

Contains a thin FastAPI router with the `/products` prefix.

Routes:

- `POST /api/products`
- `GET /api/products/{id}`
- `GET /api/products`
- `DELETE /api/products/{id}`

Expectations:

- handlers stay thin;
- database and publish logic live in service functions;
- `SessionDep` is defined through `Annotated[AsyncSession, Depends(database.get_session)]`.

## Handler Contracts

### `POST /api/products`

1. Accepts `ProductCreate`.
2. Calls the `create_product(...)` service.
3. Returns `ProductRead` with `201 Created`.

### `GET /api/products/{id}`

1. Calls `get_product(...)`.
2. Reads the product through `CRUD.get(...)`.
3. Returns `404` if the record is missing.

### `GET /api/products`

1. Calls `list_products(...)`.
2. Uses `CRUD.get(...)` internally.
3. Supports `page`, `limit`, and `user_id`.

### `DELETE /api/products/{id}`

1. Calls `delete_product(...)`.
2. Uses `CRUD.delete(...)` internally.
3. Returns `{"status": "ok"}`.

## RMQ Contract

Current event:

- event: `admin.product.created`
- queue: `admin.product.created`

Payload must contain:

- product data;
- compact Telegram user data.

Use `rmq_publisher` from `app.modules.rmq_module`.
Do not import `aio-pika` directly in this module.

## Change Rules

Good changes:

- add domain validation around product creation;
- extend the notification payload if a downstream consumer needs it;
- add new simple fields to `Product` if they clearly belong to the product request itself.

Unwanted changes:

- turning the module into a request-processing workflow engine;
- writing low-level RMQ transport code inside the feature module;
- duplicating CRUD operations with handwritten queries without a real need;
- moving business logic into `handlers.py`.

## Safety Notes

- if the ORM model changes, update `models`, `schemas`, migrations, and documentation together;
- if the RMQ event or payload changes, update both `README.md` and this file;
- if you need a new filtered list flow, first see whether `system.CRUD` can be extended in a general way instead of adding a `products_module`-only special case.

## Practical Agent Workflow

When working in this module:

1. First check whether the task can be solved through the existing `CRUD`.
2. Add service-layer logic only for domain validation and side effects.
3. Keep `handlers.py` transport-thin.
4. Do not silently change the RMQ contract — it is an integration point for `admin_bot`.
5. After any contract change, update the local module documentation.

This module should stay small, predictable, and easy to integrate with the bots later.
