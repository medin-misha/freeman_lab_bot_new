# Analysis Admin Module Design

## Goal

Добавить в `admin_bot` отдельный модуль, который получает RMQ-уведомления о
новых записях на разбор и отправляет администраторам короткое Telegram-сообщение.

## Chosen Approach

Выбран отдельный `analysis_admin_module` по образцу существующего
`product_module`.

Причины:

- это уже принятый в проекте паттерн для admin-side RMQ уведомлений;
- модуль не зависит от backend HTTP API и работает только через payload;
- дальше его можно расширить отдельными callback-действиями, не затрагивая
  соседние модули.

## Structure

Модуль включает:

- `handlers.py` с пустым router для канонической структуры;
- `runtime.py` для хранения `bot` instance;
- `schemas.py` для локальной валидации RMQ payload;
- `rmq_consumers.py` для регистрации consumer и доставки уведомлений;
- `README.md` и `AGENTS.md` для локальной документации.

## RMQ Contract

Модуль подписывается на:

- event: `admin.analysis_registration.created`
- queue: `admin.analysis_registration.created`

Payload содержит:

- `id`
- `created_at`
- `updated_at`
- `user_id`
- `user.telegram_id`
- `user.username`
- `user.first_name`
- `user.last_name`

## Notification Format

Админу отправляется короткое сообщение:

- заголовок `Новая запись на разбор`
- `ID`
- время создания записи
- отображаемое имя пользователя
- `telegram_id`

Также добавляется inline-кнопка-ссылка `tg://user?id=...` для быстрого
перехода к пользователю.

## Integration

- модульный router регистрируется в `app/bot/registry.py`
- runtime инициализируется в `app/bot/lifecycle.py`
- RMQ consumer регистрируется импортом модуля через `__init__.py`
