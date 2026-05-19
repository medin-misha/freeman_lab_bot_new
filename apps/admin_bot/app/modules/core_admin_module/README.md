# Core Admin Module

`app/modules/core_admin_module` отвечает за уведомления `admin_bot` о новых
заявках на ядро из backend `core_request_module`.

## Responsibility

Модуль:

- регистрирует RabbitMQ consumer для события `admin.core_request.created`
- валидирует входящий payload через локальные Pydantic-схемы
- отправляет уведомление во все `ADMINS_CHAT_IDS`
- показывает базовую информацию о заявке и пользователе
- добавляет inline-кнопку-ссылку на Telegram-пользователя

## RMQ Contract

Текущие константы:

- `ADMIN_CORE_REQUEST_CREATED_EVENT = "admin.core_request.created"`
- `ADMIN_CORE_REQUEST_CREATED_QUEUE = "admin.core_request.created"`

Модуль ожидает payload вида:

- `id`
- `created_at`
- `updated_at`
- `user_id`
- `activity`
- `request`
- `priorities`
- `motivation`
- `difficulties`
- `readiness`
- `weekly_time`
- `rules`
- `payment`
- `user.telegram_id`
- `user.username`
- `user.full_name`
- `user.date_of_birth`
- `user.city`

## File Map

- `handlers.py`
  Пустой router для соблюдения канонической структуры модулей.
- `runtime.py`
  Хранит `bot` instance для фоновых RMQ уведомлений.
- `schemas.py`
  Локальные Pydantic-схемы payload.
- `rmq_consumers.py`
  Регистрация consumer и доставка уведомлений в admin-чаты.

## Notes

- модуль переиспользует общий `rmq_module` для consumer registration
- доставка идёт через `settings.admins_chat_ids`
- модуль не зависит от backend HTTP API, потому что все нужные данные уже
  приходят в RMQ payload
