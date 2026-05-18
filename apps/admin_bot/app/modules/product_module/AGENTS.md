# Product Module Agent Context

## Purpose

`app/modules/product_module` is the admin-side notification module for product
requests created in backend `products_module`.

It owns:

- RabbitMQ consumption of `admin.product.created`
- payload validation for product notifications
- formatting and delivery of admin-facing Telegram notifications

## What Belongs Here

- RMQ consumer registration for product events
- compact message formatting with hashtag from `product_code`
- inline button linking to the requesting Telegram user
- lightweight runtime storage of `bot` instance for background delivery

## What Does Not Belong Here

- backend CRUD logic for products
- generic RabbitMQ transport code already owned by `rmq_module`
- diagnostic-specific admin workflows
- admin processing state beyond notification delivery

## Design Rules

- keep `handlers.py` empty unless user-facing admin commands are added later
- keep RMQ registration in `rmq_consumers.py`
- keep payload shape mirrored in local `schemas.py`
- keep delivery fan-out based on shared `ADMINS_CHAT_IDS`
- preserve message formatting as short and actionable

## RMQ Contract

- event: `admin.product.created`
- queue: `admin.product.created`

Payload currently includes:

- product identifiers and timestamps
- `product_code`
- compact Telegram user data

## Safe Extension Points

- add product-code display mapping if admins need friendlier labels
- enrich the notification text with new payload fields if backend adds them
- add follow-up callback actions later if a processing workflow appears

## Caution

- do not duplicate RabbitMQ client/runtime logic from `rmq_module`
- do not couple this module to backend HTTP endpoints unless payload stops being sufficient
- if the payload contract changes, update both `schemas.py` and the local docs

