# Products Module

`products_module` — прикладной backend-модуль для работы с заявками на продукты.

Сейчас модуль intentionally simple и отвечает только за:

- хранение записей `Product` в базе данных;
- создание, чтение, список и удаление продуктов через HTTP API;
- отправку RMQ-уведомления в `admin_bot` при создании продукта.

Модуль построен поверх `app.modules.system` и переиспользует его общий CRUD-слой вместо локального дублирования запросов.

## Структура

```text
products_module/
├── __init__.py
├── handlers.py
├── models/
│   ├── __init__.py
│   └── product.py
├── schemas/
│   ├── __init__.py
│   └── product.py
├── services/
│   ├── __init__.py
│   └── product_service.py
├── AGENTS.md
└── README.md
```

## Зависимости

Модуль использует:

- `Base` и `TimestampMixin` из `app.modules.system` для ORM-модели;
- `CRUD` из `app.modules.system` для `create / get / list / delete`;
- `TelegramUser` из `app.modules.telegram_module` для проверки владельца продукта;
- `rmq_publisher` из `app.modules.rmq_module` для уведомления `admin_bot`.

Предпочтительные импорты:

```python
from app.modules.system import Base, TimestampMixin, CRUD
from app.modules.telegram_module import TelegramUser
from app.modules.rmq_module import rmq_publisher
```

## Основная модель

### `Product`

Находится в [models/product.py](models/product.py).

`Product` хранит простую заявку пользователя на продукт.

Поля:

- `id: int` — первичный ключ;
- `created_at: datetime` — время создания записи;
- `updated_at: datetime` — время последнего обновления;
- `product_code: str` — код продукта;
- `user_id: int` — внешний ключ на `TelegramUser.id`.

Связи:

- `user` — `relationship` к `TelegramUser`;
- `ForeignKey("telegramuser.id", ondelete="CASCADE")`, поэтому удаление пользователя удаляет и связанные продукты.

## Pydantic-схемы

Схемы находятся в [schemas/product.py](schemas/product.py).

Основные DTO:

- `ProductCreate` — входная схема создания продукта;
- `ProductRead` — схема ответа API;
- `ProductAdminNotificationUser` — вложенная схема пользователя для RMQ;
- `ProductAdminNotificationPayload` — payload события для `admin_bot`.

## Service Layer

Сервис находится в [services/product_service.py](services/product_service.py).

Сервис отвечает только за ту логику, которую не должен знать общий `CRUD`:

- проверка, что `TelegramUser` существует перед созданием;
- сбор payload для `admin_bot`;
- публикация RMQ-сообщения после успешного создания продукта.

Константы уведомления:

- event: `admin.product.created`
- queue: `admin.product.created`

Payload включает:

- данные продукта: `id`, `created_at`, `updated_at`, `product_code`, `user_id`;
- краткие Telegram-данные пользователя: `telegram_id`, `username`, `first_name`, `last_name`.

## HTTP API

Router объявлен в [handlers.py](handlers.py) с префиксом `/products`.

### Endpoints

- `POST /api/products`
- `GET /api/products/{id}`
- `GET /api/products?user_id=...&page=...&limit=...`
- `DELETE /api/products/{id}`

### `POST /api/products`

Принимает `ProductCreate` и:

1. проверяет существование `TelegramUser`;
2. создаёт запись через `CRUD.create()`;
3. публикует RMQ-уведомление в `admin_bot`;
4. возвращает `ProductRead` со статусом `201 Created`.

### `GET /api/products/{id}`

Возвращает один продукт через `CRUD.get(...)`.

### `GET /api/products`

Возвращает список продуктов через `CRUD.get(...)`.

Поддерживает:

- `page`
- `limit`
- `user_id` — equality-фильтр по владельцу

### `DELETE /api/products/{id}`

Удаляет продукт через `CRUD.delete(...)` и возвращает `{"status": "ok"}`.

## Экспорт модуля

В [__init__.py](__init__.py) наружу экспортируются:

- `Product`
- `create_product`
- `get_product`
- `list_products`
- `delete_product`
- `router`

Предпочтительный импорт:

```python
from app.modules.products_module import Product
```

## Правила изменений

Хорошие изменения в этом модуле:

- добавление новых полей, которые действительно относятся к заявке на продукт;
- расширение RMQ payload, если это нужно `admin_bot`;
- добавление простой доменной валидации вокруг создания.

Нежелательные изменения:

- дублирование CRUD-логики, которая уже есть в `system`;
- тяжёлая бизнес-логика прямо в `handlers.py`;
- прямой импорт низкоуровневого RabbitMQ-клиента вместо `rmq_publisher`.

## Практические заметки

- если меняется модель `Product`, синхронно обновляйте `models`, `schemas` и Alembic-миграции;
- если меняется RMQ event/queue/payload, обновляйте и `README.md`, и `AGENTS.md`;
- если появятся новые сценарии кроме create/get/list/delete, сначала проверьте, можно ли опереться на `system.CRUD`, и только потом добавляйте кастомный service-код.
