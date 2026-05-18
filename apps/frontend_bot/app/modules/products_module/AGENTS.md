# Products Module Agent Context

## Purpose

`app/modules/products_module` is the user-facing services module of
`frontend_bot`.

It owns:

- the `Посмотреть услуги` flow
- service descriptions for `Консультации`, `Регрессии`, and `Наставничество`
- submission of product requests into backend `products_module`

## What Belongs Here

- reply-keyboard navigation for the services menu
- FSM state that binds `Оставить заявку` to the currently opened service
- backend lookup of `TelegramUser` through `GET /api/telegram/users`
- product request creation through `POST /api/products`

## What Does Not Belong Here

- onboarding and channel subscription logic
- generic backend transport helpers already owned by `system`
- admin-side processing workflows after a product is created

## Design Rules

- keep Telegram handlers thin and user-facing
- keep backend orchestration in `service.py`
- keep texts in `messages.json`
- preserve the explicit product-code mapping in code
- keep reply-keyboard navigation simple and predictable

## Backend Contract

Current service mapping:

- `Консультации` -> `Counseling`
- `Регрессии` -> `Regression`
- `Наставничество` -> `Mentoring`

Request flow:

1. resolve `user_id` with `GET /api/telegram/users`
2. if needed, provision the Telegram user through `POST /api/telegram/users`
3. create product request through `POST /api/products`

## Safe Extension Points

- add more product cards and product-code mappings
- extend user-facing success and error messages
- add deduplication or anti-spam protection if business rules require it

## Caution

- do not duplicate the shared `aiohttp` client from `system`
- do not move this domain flow into `menu_module`
- if backend payloads change, update both `README.md` and this file
