# Analysis Admin Module Agent Context

## Purpose

`app/modules/analysis_admin_module` is the admin-side notification module for
analysis registrations created in backend `analysis_module`.

It owns:

- RabbitMQ consumption of `admin.analysis_registration.created`
- payload validation for analysis registration notifications
- formatting and delivery of admin-facing Telegram notifications

## What Belongs Here

- RMQ consumer registration for analysis registration events
- compact message formatting with registration id, creation time, and user link
- inline button linking to the requesting Telegram user
- lightweight runtime storage of `bot` instance for background delivery

## What Does Not Belong Here

- backend CRUD logic for analysis registrations
- generic RabbitMQ transport code already owned by `rmq_module`
- unrelated product or diagnostic admin workflows
- admin processing state beyond notification delivery

## Design Rules

- keep `handlers.py` empty unless user-facing admin commands are added later
- keep RMQ registration in `rmq_consumers.py`
- keep payload shape mirrored in local `schemas.py`
- keep delivery fan-out based on shared `ADMINS_CHAT_IDS`
- preserve message formatting as short and actionable

## RMQ Contract

- event: `admin.analysis_registration.created`
- queue: `admin.analysis_registration.created`

Payload currently includes:

- analysis registration identifiers and timestamps
- compact Telegram user data

## Safe Extension Points

- enrich the notification text with new payload fields if backend adds them
- add follow-up callback actions later if a processing workflow appears
- add label mapping if admins later want a different display name for the flow

## Caution

- do not duplicate RabbitMQ client/runtime logic from `rmq_module`
- do not couple this module to backend HTTP endpoints unless payload stops being sufficient
- if the payload contract changes, update both `schemas.py` and the local docs
