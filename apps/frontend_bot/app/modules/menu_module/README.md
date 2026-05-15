# Menu Module

`app/modules/menu_module` owns the user onboarding entrypoint for
`frontend_bot`.

## Responsibility

The module:

- handles `/start`
- checks whether a user is subscribed to the required Telegram channel
- shows the subscription prompt with inline buttons
- routes subscribed users into the main menu

## Configuration

The module relies on the shared `CHANNEL` environment variable exposed through
`app.core.settings`.

Recommended values:

- `@channel_name`
- `https://t.me/channel_name`

## Flow

1. The user sends `/start`.
2. The module checks the subscription with `bot.get_chat_member(...)`.
3. If the user is subscribed, the bot sends the main menu message.
4. If not, the bot sends a subscription prompt with:
   - `Подписаться`
   - `Я подписался(ась)`

The confirmation button triggers a callback that repeats the same check.

## File Map

- `handlers.py`
  Owns the `/start` flow and confirmation callback.
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

- The module intentionally does not depend on backend auth.
- The exported service function is the source of truth for subscription checks.
- The decorator exists for future handlers that should also be gated by channel
  subscription.

