# Stats Module

`stats_module` is a service-first frontend module for reporting user statistics
from `frontend_bot` to backend `/api/stats` endpoints.

## Purpose

The module keeps stats transport out of feature handlers such as
`guide_module`, `menu_module`, or future diagnostic/product flows.

It is responsible for:

- resolving the current authenticated backend user through shared auth context
- sending bot-driven stats updates through the shared backend HTTP client
- exposing small reusable helpers for common events
- recording onboarding metadata such as `/start <source>` payloads

It does not own Telegram UX, storage, or runtime lifecycle.

## Public API

- `get_stats_client()`
  Returns a user-scoped `FrontendStatsClient` for the current update.
- `FrontendStatsClient.update_user_external_stats(...)`
  Sends `PATCH /api/stats/user/external`.
- `FrontendStatsClient.mark_methodology_received()`
  Marks `received_methodology=true`.
- `FrontendStatsClient.set_source(...)`
  Stores onboarding source in `UserBotStats.source`.
- `FrontendStatsClient.apply_diagnostic_event(...)`
  Sends `PATCH /api/stats/diagnostic/event`.
- `mark_current_user_received_methodology()`
  Convenience helper for guide delivery flows.
- `set_current_user_source()`
  Convenience helper for `/start <source>` onboarding flows.

## Integration Pattern

Protected handlers should use `@login_required`, then call the stats helper:

```python
from app.modules.stats_module import mark_current_user_received_methodology


@login_required
async def handler(message: Message) -> None:
    await message.answer_document(...)
    await mark_current_user_received_methodology()
```

If the stats update is auxiliary, callers should catch `StatsModuleError` and
avoid breaking the user-facing flow.

Current production usage:

- `guide_module` marks methodology delivery after sending the guide.
- `menu_module` stores `/start <source>` into `UserBotStats.source` before the
  subscription gate.
