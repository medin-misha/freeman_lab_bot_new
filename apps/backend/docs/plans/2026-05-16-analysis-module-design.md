# Analysis Module Design

## Goal

Добавить в `backend` отдельный модуль для хранения записей на разбор и
публикации событий в RabbitMQ для будущей обработки в `admin_bot`.

## Chosen Approach

Выбран отдельный `analysis_module`, а не расширение `products_module`.

Причины:

- у записи на разбор своя модель и свой API-контракт;
- модуль должен оставаться минимальным и независимым от продуктовых заявок;
- будущая админская обработка будет отдельным интеграционным потоком.

## Structure

Модуль включает:

- `models/analysis_registration.py` для ORM-модели;
- `schemas/analysis_registration.py` для API и RMQ payload схем;
- `services/analysis_registration_service.py` для CRUD orchestration и RMQ;
- `handlers.py` для HTTP endpoints;
- `README.md` и `AGENTS.md` для локальной документации;
- Alembic migration для таблицы `analysisregistration`.

## Data Model

Сущность `AnalysisRegistration` содержит только:

- `id`
- `created_at`
- `updated_at`
- `user_id`

`user_id` ссылается на `TelegramUser.id` через
`ForeignKey("telegramuser.id", ondelete="CASCADE")`.

Несколько записей на одного пользователя разрешены. Уникального ограничения по
`user_id` нет.

## API

Router размещается по префиксу `/analysis-registrations`.

Endpoints:

- `POST /api/analysis-registrations`
- `GET /api/analysis-registrations/{id}`
- `GET /api/analysis-registrations`
- `DELETE /api/analysis-registrations/{id}`

Список поддерживает `page`, `limit` и фильтр `user_id`.

## RMQ Contract

При создании записи публикуется событие:

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

## Notes

Паттерн публикации сохраняется таким же, как в `products_module`: сначала
создаётся запись через `CRUD.create()`, затем публикуется RMQ-событие.

Это оставляет известный архитектурный компромисс: если publish упадёт после
успешного commit, запись уже останется в БД. Пока этот компромисс принят ради
консистентности с текущими backend feature-модулями.
