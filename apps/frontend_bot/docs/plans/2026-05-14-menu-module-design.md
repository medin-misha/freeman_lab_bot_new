# Menu Module Design

## Goal

Add a dedicated `menu_module` to `frontend_bot` that:

- owns the `/start` onboarding flow
- checks whether a user is subscribed to a required Telegram channel
- shows a subscription prompt when access is blocked
- sends the user to the main menu after a successful subscription check

The required channel is configured through the shared environment variable
`CHANNEL`.

## Why A Separate Module

The existing `system` module is the infrastructure layer for shared runtime
services such as backend auth and debug commands. The onboarding menu and
channel-gating flow are user-facing product behavior, so they should live in a
separate module with an explicit router and isolated resources.

## Module Structure

The new module uses package folders for future growth instead of flat helper
files:

```text
app/modules/menu_module/
├── __init__.py
├── AGENTS.md
├── README.md
├── config.py
├── handlers.py
├── messages.py
├── messages.json
├── decorators/
│   ├── __init__.py
│   └── subscription_required.py
├── files/
│   └── videos/
│       └── .gitkeep
├── keyboards/
│   ├── __init__.py
│   └── subscription.py
└── service/
    ├── __init__.py
    └── subscription.py
```

## Configuration

`app/core/config.py` is extended with a shared `channel` field sourced from
`CHANNEL`. The menu module then builds its own settings projection in
`app/modules/menu_module/config.py`.

The module treats `CHANNEL` as a Telegram channel reference that can be used:

- as the URL target of the "Subscribe" button
- as the chat reference for `bot.get_chat_member(...)`

Supported values should include common Telegram forms such as `@channel_name`
and `https://t.me/channel_name`.

## Runtime Flow

### `/start`

1. Receive `/start` in `menu_module.handlers`.
2. Validate that `message.from_user` exists.
3. Check the subscription through the exported service function.
4. If the user is subscribed, send the main menu message.
5. If the user is not subscribed, send the subscription prompt with inline
   buttons.

### Recheck Callback

1. The user taps "Я подписался(ась)".
2. A callback handler repeats the same subscription check.
3. If the user is now subscribed, the bot answers the callback and sends or
   replaces the content with the main menu.
4. If the user is still not subscribed, the bot answers with a short warning.

## Subscription API

The service layer exposes a reusable subscription function. The decorator is
built on top of that function instead of owning the logic itself.

Planned API:

- `normalize_channel_reference(raw_channel: str) -> str`
- `build_channel_url(channel_reference: str) -> str`
- `async is_user_subscribed(bot: Bot, user_id: int) -> bool`

The decorator contract:

- `@subscription_required`
- works with both `Message` and `CallbackQuery`
- blocks handler execution when the user is not subscribed
- delegates prompt rendering to shared module helpers

## Status Handling

`bot.get_chat_member(...)` is treated as subscribed when Telegram reports one
of these statuses:

- `member`
- `administrator`
- `creator`

These statuses are treated as not subscribed:

- `left`
- `kicked`

Unexpected Telegram API failures should return a controlled user-facing error
message instead of allowing silent access.

## Text And UI

User-facing strings live in `messages.json`, with keys for:

- `subscription_welcome`
- `subscription_still_missing`
- `subscription_check_failed`
- `subscription_confirmed`
- `main_menu`

Inline keyboard:

- `Подписаться` opens the configured channel URL
- `Я подписался(ась)` triggers a callback-based recheck

## Router Registration

`app/bot/registry.py` explicitly registers:

- `system_router`
- `menu_router`

The `system` module should no longer own `/start`, because `menu_module`
becomes the canonical onboarding entrypoint.

## Documentation And Testing

The module ships with:

- `README.md` for human-oriented usage notes
- `AGENTS.md` for change constraints and extension guidance

Verification targets:

- Python compile check for the app package
- focused unit tests for subscription reference normalization and subscription
  status handling
