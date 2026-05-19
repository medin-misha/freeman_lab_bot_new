# Menu Module Agent Context

## Purpose

`app/modules/menu_module` is the user-facing onboarding module of
`frontend_bot`.
It controls the `/start` entrypoint, required channel subscription flow and
delivery into the main menu, including optional `/start <source>` payloads and
reporting confirmed subscriptions into backend stats.

## What Belongs Here

- `/start` onboarding UX
- source payload extraction from `/start <source>`
- channel subscription checks
- reporting `channel_subscribe=true` after a confirmed subscription check
- inline keyboards for subscription confirmation
- user-facing menu texts
- future onboarding assets under `files/`

## What Does Not Belong Here

- backend auth against application APIs
- process-wide runtime state unrelated to onboarding
- Telegram infrastructure shared by all modules
- business logic that should live in another domain module

## Design Rules

- Keep reusable subscription logic in `service/`.
- Keep decorators thin and based on exported service functions.
- Keep keyboards in `keyboards/`.
- Keep user-facing strings in `messages.json`.
- Report onboarding source through `stats_module` helpers instead of building
  ad hoc backend payloads in the handler.
- Report confirmed channel subscriptions through `stats_module` helpers instead
  of building ad hoc backend payloads in the handler.
- Preserve package-based folder structure instead of flattening helpers into
  one file per concern.
- Treat `files/videos/` as a stable asset location for future onboarding media.

## Safe Extension Points

- add more service helpers under `service/`
- add more decorators under `decorators/`
- add more keyboard builders under `keyboards/`
- extend `handlers.py` with additional menu callbacks and commands
- add more assets under `files/`

## Caution

- `CHANNEL` must remain available through the shared app config
- numeric channel IDs cannot be converted into a public subscribe URL
- start payloads should be trimmed and empty values should be ignored
- stats failures during source or subscription reporting must not block
  onboarding or main-menu access
- errors from Telegram API should fail clearly instead of silently granting
  access
