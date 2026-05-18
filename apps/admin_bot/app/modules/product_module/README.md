# Product Module

`app/modules/product_module` отвечает за уведомления `admin_bot` о новых
продуктовых заявках из backend `products_module`.

## Responsibility

Модуль:

- регистрирует RabbitMQ consumer для события `admin.product.created`
- валидирует входящий payload через локальные Pydantic-схемы
- отправляет уведомление во все `ADMINS_CHAT_IDS`
- показывает `product_code` как hashtag
- добавляет inline-кнопку-ссылку на Telegram-пользователя

## RMQ Contract

Текущие константы:

- `ADMIN_PRODUCT_CREATED_EVENT = "admin.product.created"`
- `ADMIN_PRODUCT_CREATED_QUEUE = "admin.product.created"`

Модуль ожидает payload вида:

- `id`
- `created_at`
- `updated_at`
- `product_code`
- `user_id`
- `user.telegram_id`
- `user.username`
- `user.first_name`
- `user.last_name`

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

