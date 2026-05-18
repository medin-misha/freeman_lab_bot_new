# Core Request Module Design

## Goal

Добавить в `backend` новый модуль `core_request_module` по текущей модульной
спецификации проекта и поднять совместимый с legacy `freeman_bot` HTTP API для
miniapp.

Новый модуль должен:

- хранить заявку `CoreRequest` в БД;
- принимать старый miniapp submit-контракт через `POST /api/core/submit`;
- обновлять профиль Telegram-пользователя на основе формы;
- публиковать RMQ-событие после создания заявки;
- оставаться изолированным feature-модулем в структуре
  `models / schemas / services / handlers`.

## Chosen Approach

Выбран отдельный модуль `core_request_module`, а не встраивание логики в
`telegram_module`.

Причины:

- заявка на “ядро” — отдельная доменная сущность;
- miniapp API относится к самой заявке, а не к жизненному циклу Telegram
  пользователя;
- модуль должен оставаться совместимым со старым `freeman_bot`, но при этом
  жить в новой backend-архитектуре.

## Structure

Модуль включает:

- `models/core_request.py` для ORM-модели;
- `schemas/core_request.py` для API DTO и RMQ payload схем;
- `services/core_request_service.py` для orchestration логики;
- `handlers.py` для HTTP endpoints;
- `README.md` и `AGENTS.md` для локальной документации;
- Alembic migration для таблицы `corerequest`.

Router подключается в общий [app/api/router.py](../../app/api/router.py).

## Data Model

Сущность `CoreRequest` повторяет legacy `Core` из старого проекта, но
привязывается к текущему `TelegramUser`.

Поля:

- `id`
- `created_at`
- `updated_at`
- `activity`
- `request`
- `priorities`
- `motivation`
- `difficulties`
- `readiness`
- `weekly_time`
- `rules`
- `payment`
- `user_id`

`user_id` использует `ForeignKey("telegramuser.id", ondelete="CASCADE")`.

Несколько заявок на одного пользователя разрешены. Уникального ограничения по
`user_id` нет.

## API

Router размещается по префиксу `/core`, чтобы miniapp мог продолжить работу без
изменений маршрутов.

Endpoints:

- `POST /api/core/submit`
- `GET /api/core`
- `GET /api/core/{id}`
- `PATCH /api/core/{id}`
- `DELETE /api/core/{id}`

### Submit Contract

`POST /api/core/submit` принимает legacy-compatible payload:

- `telegram_id`
- `full_name`
- `birth_date`
- `city`
- поля заявки `activity/request/priorities/motivation/difficulties/readiness/weekly_time/rules/payment`

### Read / Patch Contracts

- `CoreRequestRead` возвращает поля самой заявки;
- `CoreRequestUpdate` позволяет менять только поля заявки и `user_id`;
- miniapp profile-поля (`full_name`, `birth_date`, `city`) через `PATCH` не
  обновляются.

## Service Flow

`POST /api/core/submit` работает так:

1. Находит `TelegramUser` по `telegram_id`.
2. Возвращает `404`, если пользователь не найден.
3. Находит связанный `UserProfile`.
4. Возвращает `404`, если профиль отсутствует.
5. Обновляет профиль:
   - `full_name`
   - `date_of_birth`
   - `city`
6. Создаёт `CoreRequest` через `CRUD.create()`.
7. Публикует RMQ-событие.
8. Возвращает созданную запись.

Остальные endpoints используют текущий `system.CRUD`:

- `GET /api/core` — список с `page`, `limit`, `search`, `field`
- `GET /api/core/{id}` — точечное чтение
- `PATCH /api/core/{id}` — частичное обновление
- `DELETE /api/core/{id}` — удаление

## Date Handling

Legacy miniapp отправляет `birth_date` как `date`.

В новом backend профиль хранит `date_of_birth` как `DateTime`, поэтому API
принимает `date`, а сервис преобразует его в `datetime` на полуночь. Это
сохраняет совместимость miniapp и не требует менять текущую профильную модель
в рамках этой задачи.

## RMQ Contract

При создании заявки публикуется новое событие в стиле текущего backend:

- event: `admin.core_request.created`
- queue: `admin.core_request.created`

Payload включает:

- поля заявки;
- `user_id`;
- компактные данные пользователя и профиля, которые нужны downstream consumer:
  `telegram_id`, `username`, `full_name`, `birth_date`, `city`.

## Error Handling

- `404`, если `TelegramUser` по `telegram_id` не найден;
- `404`, если у найденного пользователя отсутствует `UserProfile`;
- остальные DB-ошибки обрабатываются через существующий `CRUD` / `DBErrorHandler`
  паттерн проекта.

## Notes

Паттерн side effects сохраняется таким же, как в `products_module` и
`analysis_module`: сначала commit данных в БД, затем publish в RMQ.

Из этого следует известный компромисс:

- если publish упадёт после успешного commit, профиль и заявка уже останутся в
  базе.

Этот компромисс принят ради консистентности с текущими feature-модулями backend.

## Verification Scope

Минимальная проверка после реализации:

- модуль корректно импортируется и подключён в общий router;
- `POST /api/core/submit` создаёт заявку и обновляет профиль;
- `POST /api/core/submit` возвращает `404` для неизвестного `telegram_id`;
- `GET /api/core` и `GET /api/core/{id}` отдают созданную запись.
