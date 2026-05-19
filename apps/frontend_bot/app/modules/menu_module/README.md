# Menu Module

`app/modules/menu_module` owns the user onboarding entrypoint for
`frontend_bot`.

## Responsibility

The module:

- handles `/start` and `/start <source>`
- checks whether a user is subscribed to the required Telegram channel
- shows the subscription prompt with inline buttons
- routes subscribed users into the main menu
- reports onboarding `source` payload into backend stats when present
- reports confirmed channel subscription into backend stats as
  `UserBotStats.channel_subscribe=true`

## Configuration

The module relies on the shared `CHANNEL` environment variable exposed through
`app.core.settings`.

Recommended values:

- `@channel_name`
- `https://t.me/channel_name`

## Flow

1. The user sends `/start` or `/start <source>`.
2. If a start payload is present, the module trims it and reports it into
   `UserBotStats.source` through `stats_module`.
3. The module checks the subscription with `bot.get_chat_member(...)`.
4. If the user is subscribed, the module reports
   `UserBotStats.channel_subscribe=true` through `stats_module`.
5. The bot sends the main menu message.
6. If not, the bot sends a subscription prompt with:
   - `Подписаться`
   - `Я подписался(ась)`

The confirmation button triggers a callback that repeats the same check and,
after a successful result, also reports `channel_subscribe=true`.

## File Map

- `handlers.py`
  Owns the `/start` flow, source extraction, subscription stats reporting, and
  confirmation callback.
- `config.py`
  Menu-specific config projection from the shared app settings.
- `messages.py` and `messages.json`
  User-facing text templates.
- `service/subscription.py`
  Reusable subscription check helpers.
- `decorators/subscription_required.py`
  Thin access decorator based on the shared service function.
- `keyboards/subscription.py`
  Inline keyboard for the subscription prompt.
- `files/videos/`
  Reserved location for the future intro video asset.

## Notes

- The module depends on backend auth through `@login_required`.
- `/start <source>` uses raw `CommandObject.args`, trims whitespace, and ignores
  empty payloads.
- Source reporting is auxiliary; stats failures must not break onboarding UX.
- Channel subscription reporting is also auxiliary; stats failures must not
  block access to the main menu after a successful subscription check.
- The exported service function is the source of truth for subscription checks.
- The decorator exists for future handlers that should also be gated by channel
  subscription.
