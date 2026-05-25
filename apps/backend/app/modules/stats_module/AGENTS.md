# Stats Module Guide For Agents

This file is a working guide for developers and AI agents modifying
`app.modules.stats_module`.

The goal is to make changes safely, without breaking API contracts,
invariants, or module boundaries.

## 1. Module Purpose

`stats_module` stores aggregated, read-optimized data for users and diagnostics.

The module is not the source of truth for business entities.

Source-of-truth modules:

- `core_request_module` for core requests
- `base_diagnostic_module` for `DiagnosticRun`
- `telegram_module` for user identity

`stats_module` is responsible for:

- updating aggregates through controlled service methods
- rebuilding aggregates from source data
- exposing aggregates through the API

## 2. Structure And Responsibilities

```text
stats_module/
├── __init__.py
├── handlers.py
├── models/
├── schemas/
├── services/
├── utils/
├── README.md
└── AGENTS.md
```

Layering rules:

- `handlers.py`: HTTP layer only, including FastAPI input validation and service calls
- `services/`: business logic, invariants, and rebuild logic
- `models/`: ORM models and domain methods such as `set_*`, `mark_*`, `increment_*`
- `schemas/`: Pydantic API contracts

Do not move business logic into handlers.

## 3. Data And Invariants

## `UserBotStats`

One row per user (`telegram_user_id`, unique).

Invariants:

- `diagnostics_completed_total <= diagnostics_total`
- if `received_methodology == True`, then `received_methodology_at != None`

## `UserDiagnosticStats`

One row per `(telegram_user_id, diagnostic_code)`.

Invariants:

- `completed_total <= attempts_total`
- counters must be non-negative

If input breaks an invariant, the service must return `HTTP 400`.

## 4. API Contracts Summary

Base prefix: `/api/stats`

- `GET /user`
- `PATCH /user/external`
- `PATCH /user/internal`
- `GET /diagnostic`
- `PATCH /diagnostic/event`
- `POST /admin/rebuild/user`
- `POST /admin/rebuild/batch`

For user-scoped endpoints:

- accept exactly one identifier: `user_id` or `chat_id`
- if both or neither are provided, return `400`
- if the user is not found, return `404`

See the full request and response contracts in
[README.md](/home/medynskyi/freeman_lab_bot_new/apps/backend/app/modules/stats_module/README.md).

## 5. External Vs Internal Updates

## External Bot-Driven Fields

Allowed through `PATCH /user/external`:

- `source`
- `current_branch`
- `channel_subscribe`
- `received_methodology`
- `review_link_clicked`
- `review_public_consent_given`

## Internal Backend-Driven Fields

Updated through `PATCH /user/internal`, rebuild flows, **and direct service
calls from other modules**:

- `core_application_submitted`
- `core_application_submitted_at`
- `diagnostics_total`
- `diagnostics_completed_total`
- `last_diagnostic_at`
- all `UserDiagnosticStats` fields

`core_application_submitted` is also updated automatically when
`core_request_module` creates a `CoreRequest`: it calls
`UserBotStatsService.update_core_application_submitted(telegram_user_id, submitted_at)`
directly on the same DB session, bypassing the HTTP API.

`diagnostics_total`, `diagnostics_completed_total`, and `last_diagnostic_at` are also
updated automatically by diagnostic modules on the same DB session:

- `base_diagnostic_module`, `default_diagnostic_module`, `invisible_diagnostic_module`
  call `UserBotStatsService.increment_diagnostics_created(telegram_user_id, at)`
  when a `DiagnosticRun` is created (`status=CREATED`).
- `base_diagnostic_module` calls
  `UserBotStatsService.increment_diagnostics_completed(telegram_user_id, at)`
  when a `DiagnosticRun` transitions to `status=COMPLETED` (via `complete_run` or
  `change_status`). The increment fires only on a real status transition, not on
  idempotent re-completion.

Both methods accept `flush=False` to integrate into the caller's transaction;
the caller is responsible for the final commit.

Do not add internal fields to external schemas.

## 6. Rebuild Design

Services:

- `UserBotStatsService.rebuild_for_user(...)` — full recalculation from source tables
- `UserBotStatsService.update_core_application_submitted(telegram_user_id, submitted_at)` —
  idempotent direct update called by `core_request_module`; no-ops if the flag
  is already set so the first-submission timestamp is preserved
- `UserBotStatsService.increment_diagnostics_created(telegram_user_id, at, flush)` —
  increments `diagnostics_total`; called by diagnostic modules on `DiagnosticRun` creation
- `UserBotStatsService.increment_diagnostics_completed(telegram_user_id, at, flush)` —
  increments `diagnostics_completed_total`; called by `base_diagnostic_module` on completion
- `UserDiagnosticStatsService.rebuild_for_user(...)`
- `StatsRebuildService` for orchestration and batch rebuild

User rebuild behavior:

- `UserBotStats` internal fields are recalculated from `CoreRequest` and `DiagnosticRun`
- per-diagnostic aggregates are recalculated from `DiagnosticRun`, grouped by `diagnostic_code`
- stale `UserDiagnosticStats` rows without source runs are removed

Admin flow:

- `POST /api/stats/admin/rebuild/user`
- `POST /api/stats/admin/rebuild/batch`

The batch endpoint is the current extension point for future scheduler or cron usage.

## 7. Pattern For Adding A New Aggregate Field

If you need to add a new statistics field:

1. Update the ORM model in `models/`.
2. Add or update the domain method such as `set_*`, `mark_*`, or `increment_*`.
3. Update the schema in `schemas/`.
4. Update the services, including external/internal update paths and rebuild if the field is derived.
5. Update handlers if the public contract changes.
6. Add an Alembic migration.
7. Update `README.md` and this `AGENTS.md`.
8. Add or update tests.

## 8. Testing Minimum

When changing logic, cover at least:

- updates by `user_id` and `chat_id`
- `404` when the user does not exist
- explicit `false` updates for boolean fields
- per-diagnostic counter increments
- rebuild correctness
- invariant enforcement

Current module tests:

- [test_stats_module_services.py](/home/medynskyi/freeman_lab_bot_new/apps/backend/tests/test_stats_module_services.py)

## 9. Do / Don't

Do:

- write aggregates only through services
- preserve invariants before commit
- keep handlers thin
- document API contracts in `README.md`

Don't:

- write directly into stats tables from other modules
- accept internal fields in external endpoints
- duplicate source-of-truth data in stats as primary storage
- add module-specific side effects into generic `system.CRUD`

## 10. Pre-Merge Checklist

- models, schemas, and services are aligned
- invariants are still enforced
- rebuild still works
- a migration has been added
- the API contract is documented in `README.md`
- tests have been updated
