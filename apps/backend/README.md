# FastAPI Template

`fastapi_template` - это модульный backend-шаблон для сервисов на основе:

- FastAPI
- PostgreSQL
- async SQLAlchemy
- Alembic migrations
- Pydantic settings
- `uv` для управления зависимостями

Репозиторий намеренно остаётся компактным. Он даёт чистую основу для новых модулей, общей инфраструктуры и API с базой данных без жёсткой привязки к конкретной предметной области.

В шаблоне есть два уровня встроенной инфраструктуры:

- `app/core/` для общих process-level примитивов;
- built-in модули в `app/modules/`, например `system` и `rmq_module`.

Все built-in модули в `app/modules/` должны жить в основном репозитории `fastapi_template`. Вложенные `.git` внутри модулей не являются целевой структурой для этого шаблона.

## Что Уже Есть

- Точка входа приложения в [main.py](/home/misha/code/module_service/fastapi_template/main.py:1)
- Общий lifecycle приложения в [app/lifecycle.py](/home/misha/code/module_service/fastapi_template/app/lifecycle.py:1)
- Центральный API router в [app/api/router.py](/home/misha/code/module_service/fastapi_template/app/api/router.py:1)
- Загрузчик настроек в [app/core/config.py](/home/misha/code/module_service/fastapi_template/app/core/config.py:1)
- Async engine базы данных и dependency для сессий в [app/core/database.py](/home/misha/code/module_service/fastapi_template/app/core/database.py:1)
- Базовый инфраструктурный модуль в [app/modules/system/README.md](/home/misha/code/module_service/fastapi_template/app/modules/system/README.md:1)
- Встроенный RabbitMQ transport-модуль в [app/modules/rmq_module/README.md](/home/misha/code/module_service/fastapi_template/app/modules/rmq_module/README.md:1)
- Настройка Alembic для миграций схемы в [alembic/env.py](/home/misha/code/module_service/fastapi_template/alembic/env.py:1)

## Текущий Объём Шаблона

Сейчас шаблон уже покрывает:

- модульную структуру проекта;
- настройки из `.env`;
- async-доступ к БД с пулом соединений;
- общие ORM-базовые классы;
- переиспользуемые CRUD-хелперы;
- health-check endpoints;
- встроенный RMQ transport layer с lifecycle-хуками и debug-инструментами.

Следующие части пока либо представлены как заглушки, либо сознательно не реализованы:

- [app/core/security.py](/home/misha/code/module_service/fastapi_template/app/core/security.py:1) пустой;
- [Dockerfile](/home/misha/code/module_service/fastapi_template/Dockerfile:1) пустой;
- отдельного тестового сетапа пока нет.

Если тебе нужны auth, контейнеризация или тесты, готовые для CI, это следующий слой, который нужно добавить поверх шаблона.

## Структура Проекта

```text
fastapi_template/
├── alembic/
├── app/
│   ├── api/
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── lifecycle.py
│   └── modules/
│       ├── system/
│       ├── rmq_module/
│       └── <your_module>/
├── main.py
├── pyproject.toml
└── README.md
```

Рекомендуемая структура для бизнес-модуля:

```text
module_name/
├── handlers.py
├── models/
├── schemas/
├── services/
├── utils/
└── README.md
```

## Требования

- Python 3.11+
- PostgreSQL
- `uv`

Метаданные проекта и runtime-зависимости описаны в [pyproject.toml](/home/misha/code/module_service/fastapi_template/pyproject.toml:1).

## Конфигурация

Настройки загружаются через `pydantic-settings` из `.env` в корне проекта. Загрузчик настроен в [app/core/config.py](/home/misha/code/module_service/fastapi_template/app/core/config.py:9).

Если ты добавляешь новую переменную окружения или новую настройку приложения, обновляй и [app/core/config.py](/home/misha/code/module_service/fastapi_template/app/core/config.py:9), добавляя соответствующее поле в `MainSettings`. Обновить только `.env.example` или документацию недостаточно.

Пример файла окружения:

```env
debug=true
database_url=postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_template
database_pool_size=5
database_max_overflow=10
database_pool_timeout=30
database_pool_recycle=1800
```

Доступные настройки:

- `project_name`: заголовок приложения в FastAPI; необязательная, по умолчанию `"Fast API Template"`.
- `debug`: включает более подробные ошибки в некоторых инфраструктурных handlers.
- `database_url`: async SQLAlchemy URL, обязательная.
- `database_pool_size`: базовый размер пула соединений.
- `database_max_overflow`: сколько дополнительных временных соединений можно открыть сверх базового пула.
- `database_pool_timeout`: сколько секунд ждать свободное соединение.
- `database_pool_recycle`: через сколько секунд переоткрывать соединения из пула.
- `rabbitmq_enabled`: включает встроенный `rmq_module` как часть приложения.
- `amqp_url`: URL подключения к RabbitMQ; может быть пустым, если `rmq_module` не используется.
- `rabbitmq_consumer_enabled`: разрешает startup фоновых consumer-listener'ов.
- `rabbitmq_debug_endpoints_enabled`: открывает debug endpoints `POST /api/rmq/publish` и `POST /api/rmq/consume`.
- `minio_*`: настройки для отдельного файлового модуля, если он подключён поверх шаблона.

В качестве базового шаблона используй [.env.example](/home/misha/code/module_service/fastapi_template/.env.example:1).

## Установка И Запуск

Установить зависимости:

```bash
uv sync
```

Запустить приложение локально:

```bash
uv run uvicorn main:app --reload
```

FastAPI-приложение создаётся в [main.py](/home/misha/code/module_service/fastapi_template/main.py:17). При остановке через `lifespan` закрывается shared SQLAlchemy engine.

Process-level startup/shutdown теперь централизован в [app/lifecycle.py](/home/misha/code/module_service/fastapi_template/app/lifecycle.py:1). Это позволяет держать built-in инфраструктурные runtime-компоненты вне `main.py`.

## Структура API

Центральный API router использует префикс `/api` в [app/api/router.py](/home/misha/code/module_service/fastapi_template/app/api/router.py:6).

Сейчас доступны следующие инфраструктурные endpoints:

- `GET /api/system/health`
- `GET /api/system/health/db`
- `GET /api/rmq/health`
- `GET /api/rmq/registrations`

Системный router реализован в [app/modules/system/handlers.py](/home/misha/code/module_service/fastapi_template/app/modules/system/handlers.py:11).
RabbitMQ router реализован в [app/modules/rmq_module/handlers.py](/home/misha/code/module_service/fastapi_template/app/modules/rmq_module/handlers.py:1).

`POST /api/rmq/publish` и `POST /api/rmq/consume` считаются debug-only и доступны только когда включён `rabbitmq_debug_endpoints_enabled=true`.

## База Данных И Сессии

Общий объект базы данных создаётся в [app/core/database.py](/home/misha/code/module_service/fastapi_template/app/core/database.py:46).

Важное поведение:

- для процесса приложения создаётся один async engine;
- handlers должны получать `AsyncSession` через `Depends(database.get_session)`;
- если исключение выходит за пределы dependency, выполняется автоматический `rollback()`;
- низкоуровневые SQLAlchemy-ошибки нормализуются инфраструктурным обработчиком ошибок, который используется в CRUD-слое модуля `system`.

## Миграции

Alembic настроен для async SQLAlchemy в [alembic/env.py](/home/misha/code/module_service/fastapi_template/alembic/env.py:1).

Применить все миграции:

```bash
uv run alembic upgrade head
```

Создать новую миграцию после изменения схемы:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

### Важно: Как Autogenerate Видит Модели

Alembic не сканирует файловую систему автоматически. Он использует `Base.metadata`, который импортируется в [alembic/env.py](/home/misha/code/module_service/fastapi_template/alembic/env.py:23) через:

- [app/__init__.py](/home/misha/code/module_service/fastapi_template/app/__init__.py:1)
- [app/modules/__init__.py](/home/misha/code/module_service/fastapi_template/app/modules/__init__.py:1)

Когда ты добавляешь новый модуль с ORM-моделями, убедись, что его модели импортированы в эту цепочку. Иначе Alembic autogenerate не увидит таблицы.

## Добавление Нового Модуля

Если создаёшь новый модуль, отличный от `system`, используй такой чеклист:

1. Создай директорию модуля в `app/modules/<module_name>/`.
2. Добавь `handlers.py`, `models/`, `schemas/`, `services/` и `README.md`.
3. Описывай ORM-модели на основе `Base` или `Base` + `TimestampMixin` из `app.modules.system`.
4. Экспортируй модели модуля через [app/modules/__init__.py](/home/misha/code/module_service/fastapi_template/app/modules/__init__.py:1), чтобы Alembic мог их увидеть.
5. Импортируй и подключи router модуля в [app/api/router.py](/home/misha/code/module_service/fastapi_template/app/api/router.py:3).
6. Сгенерируй миграцию через Alembic.
7. Если модулю нужны новые настройки, добавь их в `app/core/config.py` и задокументируй в корневом README.

Если модуль является встроенной инфраструктурой уровня приложения, как `rmq_module`, дополнительно:

1. держи его в собственной директории внутри `app/modules/`;
2. не тащи generic-transport логику в `system`, если она не относится ко всем модулям одинаково;
3. подключай startup/shutdown через `app/lifecycle.py`, а не напрямую из `main.py`;
4. явно отделяй production API от debug API.

Минимальный пример router'а:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/example", tags=["example"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

Минимальный пример модели:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.system import Base, TimestampMixin


class ExampleEntity(Base, TimestampMixin):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
```

## Рабочие Правила

- Держи бизнес-логику в `services/`, а не в handlers.
- Переиспользуй общую инфраструктуру из `app/core/` и `app/modules/system/`.
- Для RabbitMQ используй `app.modules.rmq_module`, а не прямой импорт `aio-pika` в feature-модулях.
- Не создавай ad hoc SQLAlchemy engine внутри модулей.
- Не хардкодь credentials, secrets или пароли в исходниках.
- Предпочитай явные импорты и небольшие сфокусированные файлы.

## Связанные Документы

- [app/modules/system/README.md](/home/misha/code/module_service/fastapi_template/app/modules/system/README.md:1)
- [app/modules/rmq_module/README.md](/home/misha/code/module_service/fastapi_template/app/modules/rmq_module/README.md:1)
- [AGENTS.md](/home/misha/code/module_service/fastapi_template/AGENTS.md:1)
