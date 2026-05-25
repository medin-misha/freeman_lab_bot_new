# Stats Module

`stats_module` — модуль агрегированной статистики по пользователю Telegram и его диагностическим сессиям.

Модуль не хранит первичные бизнес-данные. Источники истины:

- заявки: `core_request_module`
- диагностические прогоны: `base_diagnostic_module`

`stats_module` хранит готовые агрегаты для быстрого чтения и API-выдачи.

## Что хранится

## `UserBotStats`

Одна запись на пользователя (`telegram_user_id`, unique):

- воронка/UX-флаги: `source`, `current_branch`, `channel_subscribe`, `received_methodology`, `review_link_clicked`, `review_public_consent_given`
- backend-агрегаты: `core_application_submitted`, `core_application_submitted_at`, `diagnostics_total`, `diagnostics_completed_total`, `last_diagnostic_at`

## `UserDiagnosticStats`

Одна запись на пару `(telegram_user_id, diagnostic_code)`:

- `attempts_total`
- `completed_total`
- `last_started_at`
- `last_completed_at`
- `last_status`

## Базовые правила API

Базовый префикс: `/api/stats`

Идентификация пользователя для user-scoped endpoint'ов:

- передать нужно ровно один параметр: `user_id` или `chat_id`
- если не передан ни один: `400`
- если переданы оба: `400`
- если пользователь не найден: `404`

Таймстемпы возвращаются в формате ISO 8601 (`datetime`, UTC).

## Карта endpoint'ов

- `GET /api/stats/user` — получить `UserBotStats`
- `PATCH /api/stats/user/external` — обновить внешние (bot-driven) поля
- `PATCH /api/stats/user/internal` — обновить внутренние (backend-driven) поля
- `GET /api/stats/diagnostic` — получить `UserDiagnosticStats` по `diagnostic_code`
- `PATCH /api/stats/diagnostic/event` — применить событие к диагностическому агрегату
- `POST /api/stats/admin/rebuild/user` — пересчитать агрегаты одного пользователя
- `POST /api/stats/admin/rebuild/batch` — пакетный пересчёт пользователей

## Контракты endpoint'ов

## 1) `GET /api/stats/user`

Query:

- `user_id: int` или `chat_id: int` (ровно один)

Response `200` (`UserBotStatsRead`):

```json
{
  "id": 10,
  "created_at": "2026-05-19T18:00:00Z",
  "updated_at": "2026-05-19T18:05:00Z",
  "telegram_user_id": 42,
  "source": "ads",
  "current_branch": "onboarding-v2",
  "channel_subscribe": true,
  "received_methodology": true,
  "received_methodology_at": "2026-05-19T18:03:00Z",
  "core_application_submitted": true,
  "core_application_submitted_at": "2026-05-19T18:04:00Z",
  "diagnostics_total": 3,
  "diagnostics_completed_total": 2,
  "last_diagnostic_at": "2026-05-19T18:05:00Z",
  "review_link_clicked": false,
  "review_public_consent_given": false
}
```

Ошибки:

- `400` — неверная комбинация `user_id/chat_id`
- `404` — пользователь или агрегат не найден

## 2) `PATCH /api/stats/user/external`

Назначение: обновление полей, которые приходят из внешнего бота.

Query:

- `user_id: int` или `chat_id: int` (ровно один)

Body (`UserBotStatsExternalUpdate`):

```json
{
  "source": "ads",
  "current_branch": "onboarding-v2",
  "channel_subscribe": true,
  "received_methodology": true,
  "review_link_clicked": false,
  "review_public_consent_given": true
}
```

Поведение:

- можно передавать частичный payload (только нужные поля)
- `false` применяется явно (не игнорируется)
- при `received_methodology=true` модуль проставит `received_methodology_at`
- при `received_methodology=false` поле `received_methodology_at` сбрасывается в `null`

Важно:

- `core_application_submitted` и другие internal поля сюда не входят по контракту

Response `200`: `UserBotStatsRead`

## 3) `PATCH /api/stats/user/internal`

Назначение: обновление backend-агрегатов из внутренних модулей.

Query:

- `user_id: int` или `chat_id: int` (ровно один)

Body (`UserBotStatsInternalUpdate`):

```json
{
  "core_application_submitted": true,
  "diagnostics_total": 8,
  "diagnostics_completed_total": 5,
  "last_diagnostic_at": "2026-05-19T18:05:00Z"
}
```

Инварианты:

- `diagnostics_total >= 0`
- `diagnostics_completed_total >= 0`
- `diagnostics_completed_total <= diagnostics_total`

Если нарушены: `400 Bad Request`.

Response `200`: `UserBotStatsRead`

## 4) `GET /api/stats/diagnostic`

Query:

- `diagnostic_code: str` (обязателен)
- `user_id: int` или `chat_id: int` (ровно один)

Response `200` (`UserDiagnosticStatsRead`):

```json
{
  "id": 21,
  "created_at": "2026-05-19T18:00:00Z",
  "updated_at": "2026-05-19T18:05:00Z",
  "telegram_user_id": 42,
  "diagnostic_code": "default",
  "attempts_total": 4,
  "completed_total": 3,
  "last_started_at": "2026-05-19T18:04:00Z",
  "last_completed_at": "2026-05-19T18:05:00Z",
  "last_status": "completed"
}
```

Ошибки:

- `400` — неверная комбинация `user_id/chat_id`
- `404` — пользователь или агрегат по `diagnostic_code` не найден

## 5) `PATCH /api/stats/diagnostic/event`

Назначение: применить событие к per-diagnostic агрегату.

Query:

- `user_id: int` или `chat_id: int` (ровно один)

Body (`UserDiagnosticStatsEventUpdate`):

```json
{
  "diagnostic_code": "default",
  "attempts_delta": 1,
  "completed_delta": 1,
  "started": true,
  "completed": true,
  "status": "completed"
}
```

Поведение:

- если агрегат по `diagnostic_code` отсутствует, он будет создан
- `attempts_delta` и `completed_delta` должны быть `>= 0`, иначе `400`
- сохраняется инвариант `completed_total <= attempts_total`
- `started=true` обновляет `last_started_at`
- `completed=true` обновляет `last_completed_at`
- `status` обновляет `last_status`

Response `200`: `UserDiagnosticStatsRead`

## 6) `POST /api/stats/admin/rebuild/user`

Назначение: ручной пересчёт агрегатов одного пользователя.

Query:

- `user_id: int` или `chat_id: int` (ровно один)

Что пересчитывается:

- `UserBotStats` internal-поля из `CoreRequest` и `DiagnosticRun`
- весь набор `UserDiagnosticStats` из `DiagnosticRun` по `diagnostic_code`

Response `200` (`UserStatsRebuildRead`):

```json
{
  "rebuilt_at": "2026-05-19T18:10:00Z",
  "user_bot_stats": { "id": 10 },
  "diagnostic_stats": [
    { "id": 21 },
    { "id": 22 }
  ]
}
```

## 7) `POST /api/stats/admin/rebuild/batch`

Назначение: пакетный пересчёт пользователей (удобно для cron/scheduler).

Query:

- `offset: int = 0`
- `limit: int = 100`, `>= 1`

Response `200`:

- массив `UserStatsRebuildRead`

## Источник данных для rebuild

`UserBotStats`:

- `core_application_submitted` и `core_application_submitted_at` — из таблицы `CoreRequest`
- `diagnostics_total`, `diagnostics_completed_total`, `last_diagnostic_at` — из `DiagnosticRun`

`UserDiagnosticStats`:

- группировка `DiagnosticRun` по `diagnostic_code`
- пересчёт `attempts_total`, `completed_total`, `last_started_at`, `last_completed_at`, `last_status`
- агрегаты без source-данных удаляются как устаревшие

## Типовые сценарии использования

## Сценарий A: бот обновил внешние флаги

1. Вызвать `PATCH /api/stats/user/external`.
2. Считать актуальное состояние через `GET /api/stats/user`.

## Сценарий B: backend завершил диагностику

1. Вызвать `PATCH /api/stats/diagnostic/event` с `completed=true`.
2. При необходимости обновить user-level totals через `PATCH /api/stats/user/internal`.

## Сценарий C: пользователь отправил core-заявку

`core_request_module` вызывает `UserBotStatsService.update_core_application_submitted`
напрямую после создания `CoreRequest`. Никакого внешнего HTTP-вызова не требуется —
обновление происходит автоматически в рамках той же сессии. Метод идемпотентен:
если флаг уже выставлен, он остаётся без изменений (сохраняется время первой подачи).

## Сценарий E: создана или завершена диагностика

`base_diagnostic_module`, `default_diagnostic_module` и `invisible_diagnostic_module`
вызывают методы `UserBotStatsService` напрямую в рамках той же сессии:

- при создании `DiagnosticRun` → `increment_diagnostics_created(telegram_user_id, at)` —
  инкрементирует `diagnostics_total` и обновляет `last_diagnostic_at`
- при успешном завершении `DiagnosticRun` → `increment_diagnostics_completed(telegram_user_id, at)` —
  инкрементирует `diagnostics_completed_total` и обновляет `last_diagnostic_at`

Оба метода принимают `flush=False`, чтобы не нарушать транзакцию вызывающего кода.
Коммит остаётся за вызывающим сервисом.

## Сценарий D: контрольная сверка

1. Запустить `POST /api/stats/admin/rebuild/user`.
2. Сравнить возвращенные агрегаты с ожидаемыми бизнес-метриками.

## Ошибки и коды

Стандартные ошибки модуля:

- `400 Bad Request` — невалидный input или нарушение инварианта
- `404 Not Found` — пользователь/агрегат не найден

Пример `400`:

```json
{
  "detail": "Provide only one identifier: user_id or chat_id."
}
```

Пример `404`:

```json
{
  "detail": "TelegramUser with id=123 not found."
}
```

## Ограничения текущей версии

- сервис-level authorization для stats endpoint'ов пока не включен
- rate limiting для stats endpoint'ов пока не включен

Эти ограничения операционные и могут быть ужесточены без изменения бизнес-модели агрегатов.
