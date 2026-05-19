# Stats Module Agent Context

## Purpose

`app/modules/stats_module` reports frontend-driven statistics to backend
`/api/stats` endpoints.

It exists to keep product and UX handlers free from transport details and to
reuse the shared auth/session infrastructure from `system`.

## What Belongs Here

- user-scoped helpers that send stats for the current authenticated user
- local schemas for backend stats payloads used by `frontend_bot`
- convenience methods for common events such as methodology delivery
- onboarding source reporting for `/start <payload>`

## What Does Not Belong Here

- Telegram menu or message handlers for unrelated user journeys
- backend auth lifecycle ownership
- direct database access
- product-specific business flows that do more than stats reporting

## Design Rules

- Reuse `app.modules.system.client.get_backend_client()`.
- Resolve the current user through `app.core.context.get_current_auth_session()`.
- Keep the module service-first; handlers may stay empty.
- Wrap low-level backend transport errors into `StatsModuleError`.
- Prefer small reusable methods over ad hoc dict payloads in feature modules.
- Keep source reporting generic: the module stores a string value, while
  `menu_module` owns how `/start` payloads are extracted and normalized.

## Current Contract

- `PATCH /api/stats/user/external`
- `PATCH /api/stats/diagnostic/event`

User identification must go through `user_id` from the authenticated backend
Telegram user payload.

## Integration Guidance

- Call stats helpers only from handlers already protected by `@login_required`
  or from code paths where auth context is explicitly available.
- `/start <source>` flows should call `set_current_user_source(...)` instead of
  constructing `UserBotStatsExternalUpdate(source=...)` inline.
- If the stats update is non-critical, log and suppress `StatsModuleError`
  instead of failing the primary UX action.
