# Core Admin Module Agent Context

## Purpose

`app/modules/core_admin_module` is the admin-side notification module for core
program requests created in backend `core_request_module`.

It owns:

- RabbitMQ consumption of `admin.core_request.created`
- payload validation for core request notifications
- formatting and delivery of admin-facing Telegram notifications

## What Belongs Here

- RMQ consumer registration for core request events
- compact message formatting with request id, creation time, and user link
- inline button linking to the requesting Telegram user
- lightweight runtime storage of `bot` instance for background delivery

## What Does Not Belong Here

- backend CRUD logic for core requests
- generic RabbitMQ transport code already owned by `rmq_module`
- unrelated product, analysis, or diagnostic workflows
- admin processing state beyond notification delivery

## Design Rules

- keep `handlers.py` empty unless user-facing admin commands are added later
- keep RMQ registration in `rmq_consumers.py`
- keep payload shape mirrored in local `schemas.py`
- keep delivery fan-out based on shared `ADMINS_CHAT_IDS`
- preserve message formatting as short and actionable

## RMQ Contract

- event: `admin.core_request.created`
- queue: `admin.core_request.created`

Payload currently includes:

- core request identifiers and timestamps
- core request questionnaire fields
- compact Telegram user data

## Safe Extension Points

- enrich the notification text with new payload fields if backend adds them
- add follow-up callback actions later if a processing workflow appears
- add label mapping if admins later want a different display name for the flow

## Caution

- do not duplicate RabbitMQ client/runtime logic from `rmq_module`
- do not couple this module to backend HTTP endpoints unless payload stops being sufficient
- if the payload contract changes, update both `schemas.py` and local docs
