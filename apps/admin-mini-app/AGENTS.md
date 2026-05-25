# Руководство разработчика и AI-агентов (AGENTS.md)

Добро пожаловать в модуль интеграции API для **admin-mini-app** (панель администратора «Психология Масштаба» - PML). В данном документе описана архитектура API-клиента, структура эндпоинтов, маппинги и инструкции по дальнейшему расширению функционала.

---

## 🛠 Архитектура API-модуля

Для взаимодействия с бэкендом (Python FastAPI) на первом шаге был создан централизованный модуль HTTP-клиента с использованием библиотеки **Axios**.

### 1. Конфигурация окружения
Переменные окружения хранятся в корне модуля в файлах:
- `.env.example` — шаблон конфигурации.
- `.env` — локальные настройки.

Основная переменная:
```bash
VITE_API_URL=/api
```
Во время локальной разработки Vite dev-сервер автоматически проксирует все запросы, начинающиеся с `/api`, на порт бэкенда `http://localhost:8000`.

Конфигурация прокси в [vite.config.js](file:///home/medynskyi/freeman_lab_bot_new/apps/admin-mini-app/vite.config.js):
```javascript
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
```

---

## 📂 Структура файлов модуля API

- **[api.js](file:///home/medynskyi/freeman_lab_bot_new/apps/admin-mini-app/src/services/api.js)** — Создает инстанс Axios и описывает методы взаимодействия с API.
- **[UserList.vue](file:///home/medynskyi/freeman_lab_bot_new/apps/admin-mini-app/src/components/UserList.vue)** — Компонент списка пользователей. Управляет своим состоянием загрузки (`loading`), номером страницы (`currentPage`), признаком наличия следующей страницы (`hasNext`) и строкой поиска с дебаунсом.
- **[App.vue](file:///home/medynskyi/freeman_lab_bot_new/apps/admin-mini-app/src/App.vue)** — Корневой компонент. Подписывается на событие `@usersLoaded` от списка пользователей, чтобы держать в актуальном состоянии глобальный реактивный массив `users` (например, для вычисления статистики на текущей странице или рассылок).

---

## 🔄 Маппинг моделей (Бэкенд ➡️ Фронтенд)

Модель пользователя бэкенда (`TelegramUserRead`) имеет связанный объект `user_profile`. Метод `mapBackendUserToList` в [api.js](file:///home/medynskyi/freeman_lab_bot_new/apps/admin-mini-app/src/services/api.js) преобразует эту вложенную структуру в плоский формат, совместимый с существующим UI админ-панели:

| Поле на бэкенде (`TelegramUserRead`) | Поле во фронтенде (UI) | Примечание |
| :--- | :--- | :--- |
| `id` | `id` | Первичный ключ в БД |
| `telegram_id` | `telegram_id` | Преобразуется в строку `String(telegram_id)` |
| `username` | `username` | Юзернейм в Telegram |
| `user_profile.full_name` | `full_name` | ФИО (по умолчанию "Без имени") |
| `user_profile.phone` | `phone` | Телефон пользователя |
| `user_profile.city` | `city` | Город проживания |
| `user_profile.email` | `email` | Электронная почта |
| `user_profile.timezone` | `timezone` | Временная зона |
| `user_profile.date_of_birth` | `birth_date` | Дата рождения (формат DD.MM.YYYY) |
| `created_at` | `registration_date`| Дата регистрации в боте |
| `last_seen_at` | `last_active` | Последнее действие пользователя |

---

## 📈 Спецификация API эндпоинтов (Шаг 1)

### Получение списка пользователей
- **Метод**: `GET`
- **Эндпоинт**: `/api/telegram/users`
- **Query параметры**:
  - `page` (int, default: 1) — Номер страницы.
  - `limit` (int, default: 8) — Количество записей на странице.
  - `search` (str, optional) — Поисковый запрос (выполняет полнотекстовый поиск по `username` на стороне базы данных бэкенда).
- **Формат ответа**: `list[TelegramUserRead]`

---

## 🚀 Инструкции по дальнейшему расширению для следующих шагов

При переходе к следующим шагам интеграции API:

1. **Интеграция статистики (`stats_module`)**:
   Для получения реальных полей `in_core`, `current_branch` (`current_step`), `channel_subscribed` и `methodology_received`:
   - Добавьте метод `fetchUserStats(userId)` в `api.js` с запросом к `GET /api/stats/user?user_id={userId}`.
   - Запрашивайте эту статистику параллельно с детальной информацией о пользователе при клике на строку таблицы (внутри обработчика `selectUser` в `App.vue`).

2. **Интеграция запусков диагностик (`base_diagnostic_module`)**:
   - Добавьте метод `fetchUserDiagnosticRuns(userId)` с запросом к `GET /api/runs?user_id={userId}`.
   - Сопоставляйте полученные запуски в массив `diagnostics` выбранного пользователя.

3. **Сохранение изменений профиля**:
   - Реализуйте метод `updateUserProfile(profileId, data)` с запросом `PATCH /api/telegram/profile/{id}`.
   - Реализуйте метод `updateTelegramUser(userId, data)` с запросом `PATCH /api/telegram/users/{id}`.
