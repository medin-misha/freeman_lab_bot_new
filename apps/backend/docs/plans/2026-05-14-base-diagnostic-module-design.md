# Base Diagnostic Module Design

## Goal

Add a shared `base_diagnostic_module` that owns the generic lifecycle of any diagnostic run and can be reused by current and future diagnostic product modules.

## Scope

The module stores only fields common to every diagnostic:

- run identity and timestamps;
- user link;
- diagnostic discriminator;
- lifecycle status;
- generic text fields;
- generic file attachments.

The module must not store diagnostic-specific scoring, formulas, or product-only fields.

## Chosen Approach

Use a hybrid module layout:

- ORM model for `DiagnosticRun`;
- thin FastAPI handlers;
- service layer for lifecycle orchestration and event publishing;
- explicit schemas for create/read/patch-like operations.

This keeps domain logic out of handlers while still exposing a reusable HTTP API and a Python service surface for other diagnostic modules.

## Data Model

`DiagnosticRun` fields:

- `id`
- `created_at`
- `updated_at`
- `voice_file_id`
- `result_file_id`
- `transcribation_file_id`
- `user_id`
- `diagnostic_code`
- `status`
- `completed_at`
- `note`
- `description`
- `tag`

Relationships:

- `user_id -> telegramuser.id` with `ON DELETE CASCADE`
- `voice_file_id -> file.id` with `ON DELETE SET NULL`
- `result_file_id -> file.id` with `ON DELETE SET NULL`
- `transcribation_file_id -> file.id` with `ON DELETE SET NULL`

## Status Model

V1 uses a simple constants class instead of an enum:

- `created`
- `completed`
- `failed`

The service validates incoming status values against this class.

## Lifecycle

Service methods:

- `create_run(...)`
- `get_run(...)`
- `list_runs(...)`
- `change_status(...)`
- `attach_voice_file(...)`
- `attach_result_file(...)`
- `attach_transcribation_file(...)`
- `complete_run(...)`

Lifecycle rules:

- create always starts with `status="created"`;
- status changes publish only on actual change;
- completion always sets `status="completed"` and `completed_at`;
- attaching a result file publishes `diagnostic.result_attached`.

## Events

The module publishes through `rmq_publisher`:

- `diagnostic.created`
- `diagnostic.status_changed`
- `diagnostic.completed`
- `diagnostic.result_attached`

Publishing happens after successful DB commit so events reflect durable state.

## HTTP API

Router prefix: `/diagnostics`

Endpoints:

- `POST /api/diagnostics/runs`
- `GET /api/diagnostics/runs/{id}`
- `GET /api/diagnostics/runs`
- `PATCH /api/diagnostics/runs/{id}/status`
- `PATCH /api/diagnostics/runs/{id}/voice-file`
- `PATCH /api/diagnostics/runs/{id}/result-file`
- `PATCH /api/diagnostics/runs/{id}/transcribation-file`
- `POST /api/diagnostics/runs/{id}/complete`

The list endpoint supports filtering by `user_id` and `diagnostic_code`.

## Validation And Error Handling

- service validates status values;
- referenced `TelegramUser` and `File` records are resolved before attachment/update;
- DB failures are normalized through shared `DBErrorHandler` patterns already used in backend modules.

## Verification

Implementation verification should cover:

- imports and module wiring;
- migration syntax;
- lifecycle service happy paths;
- router compilation with schemas.
