"""Сервисный слой analysis-модуля."""

from __future__ import annotations

from app.core.context import get_current_auth_session
from app.modules.system.client import BackendClientError, get_backend_client


class AnalysisModuleError(RuntimeError):
    """Базовая ошибка analysis-модуля."""


class AnalysisAuthContextError(AnalysisModuleError):
    """Не удалось получить backend auth-сессию для текущего update."""


async def submit_analysis_registration() -> None:
    """Создаёт запись на разбор для текущего backend-пользователя."""

    auth_session = get_current_auth_session()
    if auth_session is None:
        raise AnalysisAuthContextError(
            "Current update does not have an authenticated backend session."
        )

    try:
        backend_client = get_backend_client()
        await backend_client.post_json(
            path="/analysis-registrations",
            json_payload={
                "user_id": auth_session.telegram_user.id,
            },
        )
    except BackendClientError as exc:
        raise AnalysisModuleError(str(exc)) from exc
