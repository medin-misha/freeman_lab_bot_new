# Admin Mini App

Telegram Mini App (WebApp) для панели администратора «Психология Масштаба» (PML).

## Стек технологий

- Vue 3 (Composition API)
- Vite
- Axios (HTTP-клиент)
- Telegram Mini Apps SDK (`@telegram-apps/sdk`)
- Nginx (в контейнере)

## Переменные окружения (.env)

Для конфигурации приложения используются переменные окружения. Создайте файл `.env` на основе шаблона `.env.example`:

```bash
# Base URL для запросов к API бэкенда
VITE_API_URL=/api
```

## Локальная разработка

При запуске локального dev-сервера запросы к `/api` автоматически проксируются на бэкенд, запущенный на порту `8000` (см. `vite.config.js`).

1. Установите зависимости:
   ```bash
   npm install
   ```

2. Запустите dev-сервер:
   ```bash
   npm run dev
   ```

3. Для проверки и сборки продакшн-бандла:
   ```bash
   npm run build
   ```

