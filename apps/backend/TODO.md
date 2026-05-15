1. Высокий: POST /api/telegram/login фактически позволяет логиниться как любой
     пользователь по одному telegram_id, без подписи Telegram, токена или любой
     другой проверки. Это не “login”, а открытая impersonation-точка: достаточно
     знать чужой id, чтобы получить его профиль и обновить last_seen_at. См.
     fastapi_template/app/modules/telegram/handlers.py:31, fastapi_template/app/
     modules/telegram/schemas/telegram_user.py:21, fastapi_template/app/modules/
     telegram/services/user_service.py:94. Если это не auth endpoint, его нужно
     переименовать и убрать из публичного API; если это auth, нужна проверка
     initData/подписи Telegram.
  2. Высокий: заявленная связь TelegramUser -> UserProfile как one-to-one не
     обеспечена на уровне БД. В ORM стоит uselist=False, но
     userprofile.telegram_user_id не имеет UNIQUE, а публичный POST /api/telegram/
     profile позволяет создавать сколько угодно профилей на одного пользователя. В
     результате TelegramUserRead.user_profile становится недетерминированным. См.
     fastapi_template/app/modules/telegram/models/telegram_user.py:21,
     fastapi_template/app/modules/telegram/models/user_profile.py:12,
     fastapi_template/app/modules/telegram/handlers.py:111, fastapi_template/alembic/
     versions/53ad66fd2c15_init.py:39. Это я локально воспроизвёл: две строки
     UserProfile для одного telegram_user_id вставляются без ошибок, после чего
     SQLAlchemy уже выдаёт предупреждение Multiple rows returned with uselist=False.
  3. Высокий: удаление TelegramUser сейчас сломано. Хотя во второй миграции добавлен
     ON DELETE CASCADE, ORM-relationship не настроен на passive_deletes=True или ORM-
     cascade, поэтому CRUD.delete() при session.delete(instance) пытается сначала
     занулить userprofile.telegram_user_id, что падает на NOT NULL. См.
     fastapi_template/app/modules/system/services/crud.py:336, fastapi_template/app/
     modules/telegram/models/telegram_user.py:21, fastapi_template/app/modules/
     telegram/models/user_profile.py:12, fastapi_template/alembic/
     versions/71d6c9bedd7b_add_telegram_user_profile_cascade_delete.py:24. Это тоже
     подтверждено локальным воспроизведением: коммит удаления падает с
     IntegrityError: NOT NULL constraint failed: userprofile.telegram_user_id.
  4. Средний: создание TelegramUser и UserProfile неатомарно. Сервис сначала коммитит
     пользователя, потом отдельным коммитом создаёт профиль, а при ошибке делает
     “компенсирующее” удаление, которое само может не сработать и лишь логируется.
     Значит, есть окно, где другие запросы увидят пользователя без профиля, и есть
     риск оставить мусорные записи при сбое cleanup. См. fastapi_template/app/
     modules/telegram/services/user_service.py:18, fastapi_template/app/modules/
     telegram/services/user_service.py:38, fastapi_template/app/modules/telegram/
     services/user_service.py:65, fastapi_template/app/modules/system/services/
     crud.py:148, fastapi_template/app/modules/system/services/crud.py:377.

