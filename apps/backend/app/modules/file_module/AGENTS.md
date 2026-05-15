# File Module Guide For AI Agents

## Purpose

`app.modules.file_module` — прикладной модуль для хранения файлов.

Модуль отвечает за:

- хранение метаданных файла в модели `File`;
- загрузку, скачивание и удаление файлов в S3-совместимом хранилище через `S3Client`;
- HTTP-эндпоинты upload / download / delete.

Модуль зависит от `app.modules.system` и переиспользует его инфраструктуру вместо того, чтобы дублировать её локально.

## Dependency On `system`

`file_module` — прикладной модуль, построенный поверх `system`.

Текущие зависимости:

- `Base` и `TimestampMixin` для ORM-модели `File`;
- `CRUD` для операций с базой данных.

Предпочтительные импорты:

```python
from app.modules.system import Base, TimestampMixin, CRUD
```

Не дублируй CRUD-логику и обработку ошибок БД внутри этого модуля.

## What This Module Owns

Модуль владеет одной сущностью:

- `File` — запись с метаданными загруженного файла.

Разделение ответственности:

- в бакете файл хранится под ключом `<uuid4_hex>.<extension>`;
- `File.link` содержит полный публичный URL файла в бакете;
- `File.name` содержит оригинальное имя файла (в том числе кириллическое);
- `File.note` — опциональная пользовательская заметка.

Ключ в бакете намеренно отвязан от имени файла, чтобы избежать проблем с кодировками в хранилище.

## Module Map

### `models/`

Содержит ORM-модель.

Важный файл:

- `models/file.py`

Ожидания агента:

- `File` наследует `Base` (первичный ключ `id`) и `TimestampMixin` (`created_at`, `updated_at`);
- `link` — `String(1024)`, ненулевое (выводится из `Mapped[str]`);
- `name` — `String(512)`, ненулевое (выводится из `Mapped[str]`);
- `note` — `Text`, `nullable`.

### `schemas/`

Содержит Pydantic-схемы.

Важный файл:

- `schemas/file.py`

Ожидания агента:

- `FileCreate` — внутренняя схема для `CRUD.create()`, содержит `link`, `name`, `note`;
- `FileRead` — схема ответа API, содержит все поля включая `id`, `created_at`, `updated_at`.

`FileCreate` никогда не принимается напрямую от клиента. Хэндлер формирует её сам после загрузки файла в S3.

### `services/`

Содержит асинхронный клиент хранилища.

Важный файл:

- `services/s3_client.py`

Ожидания агента:

- `S3Client` — класс с тремя async-методами: `create`, `read`, `delete`;
- `create(file_obj: BinaryIO, filename: str, content_type: str) → str` — стримит файл в бакет без копирования байт в память, возвращает публичный URL; размер файла определяется через `seek(0,2)` без чтения данных;
- `read(link) → bytes` — скачивает файл по URL, возвращает байты;
- `delete(link) → None` — удаляет файл по URL;
- `_scheme → str` — свойство, возвращает `"https"` или `"http"` по `settings.minio_secure`;
- `_key_from_link(link) → str` — приватный хелпер, извлекает ключ объекта из полного URL;
- формат ключа в бакете: `uuid4().hex + Path(filename).suffix`;
- `s3_client` — синглтон класса `S3Client`, используется в `handlers.py`.

Все параметры подключения берутся из `app.core.config.settings`:
`minio_endpoint`, `minio_access_key`, `minio_secret_key`, `minio_bucket`, `minio_secure`.

Клиент создаёт новый `aiobotocore` сессион и клиент на каждый вызов через `async with self._client()`.
Не кешируй клиент между вызовами — `aiobotocore` не гарантирует переиспользование.

### `handlers.py`

Содержит FastAPI-роутер с тремя эндпоинтами.

Текущие маршруты объявлены с префиксом `/files`:

- `POST /api/files/` — загрузка файла;
- `GET /api/files/{id}` — скачивание файла;
- `DELETE /api/files/{id}` — удаление файла и записи.

Ожидания агента:

- хэндлеры тонкие — транспортный код без бизнес-логики;
- `SessionDep` определён через `Annotated[AsyncSession, Depends(database.get_session)]`;
- upload-хэндлер принимает `UploadFile` и опциональный `note: str = Form(None)`;
- download-хэндлер возвращает `StreamingResponse` с `Content-Disposition: attachment; filename*=UTF-8''<url-encoded-name>`;
- `Content-Type` при скачивании определяется через `mimetypes.guess_type(file_record.name)`, fallback — `application/octet-stream`.

## Handler Contracts

### `POST /api/files/`

1. нормализует имя файла: `filename = file.filename or "unnamed"`;
2. вызывает `s3_client.create(file.file, filename, file.content_type)` — передаёт `SpooledTemporaryFile` напрямую, без `await file.read()`;
3. вызывает `CRUD.create(FileCreate(link=..., name=filename, note=note), File, session)`;
4. если `CRUD.create` бросает исключение — вызывает `s3_client.delete(link)` для отката загрузки, затем пробрасывает исключение дальше;
5. возвращает `FileRead` со статусом `201 Created`.

### `GET /api/files/{id}`

1. вызывает `CRUD.get(File, session, id=id)` — `404`, если не найдено;
2. вызывает `s3_client.read(file_record.link)`;
3. возвращает `StreamingResponse` с корректными заголовками для кириллических имён.

### `DELETE /api/files/{id}`

Порядок обязателен:

1. вызывает `CRUD.get(File, session, id=id)` — получает запись и сохраняет `link` локально;
2. удаляет запись из БД: `session.delete(file_record)` + `session.commit()` — транзакция гарантирует атомарность;
3. вызывает `s3_client.delete(link)` в блоке `try/except` — если S3 бросает исключение, логирует `WARNING` и не прерывает ответ;
4. возвращает `{"status": "ok"}`.

Порядок БД → S3 намеренный:
- если БД упала — S3-файл цел, состояние согласованное;
- если S3 упала после коммита — файл осиротел в бакете, но битой ссылки в БД нет; сирота логируется для ручной чистки.

Не меняй порядок на S3 → БД: потеря соединения с БД после удаления из S3 оставит запись с нерабочим `link`.

## Change Rules

Хорошие изменения в этом модуле:

- добавление полей метаданных файла в `File`;
- расширение `S3Client` новыми методами работы с хранилищем;
- улучшение обработки ошибок при S3-операциях.

Нежелательные изменения:

- добавление бизнес-логики в `handlers.py`;
- дублирование CRUD или DB-error-логики из `system`;
- хранение credentials напрямую в коде;
- изменение порядка шагов в `delete`-хэндлере без учёта консистентности данных.

## Safety Notes

- если добавляются или переименовываются поля модели, синхронно обновляй `models`, `schemas` и создавай новую миграцию через `uv run alembic revision --autogenerate -m "..."`;
- если меняется экспорт, обновляй `file_module/__init__.py` и `app/modules/__init__.py`;
- если меняется поведение `S3Client` или хэндлеров, обновляй и `README.md`, и этот файл;
- `_key_from_link` зависит от формата URL `http(s)://{endpoint}/{bucket}/{key}` — если формат URL изменится, нужно обновить и хелпер.

## Practical Agent Workflow

При работе в этом модуле:

1. Убедись, что изменение относится к домену файлового хранилища, а не к общей инфраструктуре.
2. Для операций с БД используй `CRUD` из `system`, не пиши запросы вручную.
3. Для операций с хранилищем используй `s3_client` из `services`.
4. Держи `handlers.py` тонким — координацию между S3 и БД допустимо оставить прямо в хэндлере, так как логика линейная и несложная.
5. При изменении контракта `delete` — всегда проверяй порядок шагов (БД → S3).
6. Обновляй документацию при изменении поведения или публичных интерфейсов.

Этот модуль должен оставаться простым, предсказуемым и сфокусированным на загрузке и хранении файлов.
