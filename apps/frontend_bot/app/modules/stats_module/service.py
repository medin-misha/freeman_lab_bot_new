"""Сервисный слой stats-модуля."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from app.core.context import get_current_auth_session
from app.modules.system.client import (
    BackendClient,
    BackendClientError,
    get_backend_client,
)

from .schemas import (
    UserBotStatsExternalUpdate,
    UserBotStatsRead,
    UserDiagnosticStatsEventUpdate,
    UserDiagnosticStatsRead,
)


class StatsModuleError(RuntimeError):
    """Базовая ошибка stats-модуля."""


class StatsAuthContextError(StatsModuleError):
    """В текущем update нет backend auth-сессии пользователя."""


@dataclass(slots=True, frozen=True)
class FrontendStatsClient:
    """User-scoped клиент для backend stats API."""

    backend_client: BackendClient
    user_id: int

    async def update_user_external_stats(
        self,
        data: UserBotStatsExternalUpdate,
    ) -> UserBotStatsRead:
        """Отправляет bot-driven обновление агрегата пользователя."""

        return await self._patch_user_stats(
            path="/stats/user/external",
            payload=data.model_dump(mode="json", exclude_none=True),
            response_model=UserBotStatsRead,
        )

    async def mark_methodology_received(self) -> UserBotStatsRead:
        """Помечает, что пользователь получил методичку."""

        return await self.update_user_external_stats(
            UserBotStatsExternalUpdate(received_methodology=True)
        )

    async def set_source(self, source: str) -> UserBotStatsRead:
        """Сохраняет source-метку пользователя."""

        return await self.update_user_external_stats(
            UserBotStatsExternalUpdate(source=source)
        )

    async def set_branch(self, branch: str) -> UserBotStatsRead:
        """Сохраняет current_branch пользователя."""

        return await self.update_user_external_stats(
            UserBotStatsExternalUpdate(current_branch=branch)
        )

    async def apply_diagnostic_event(
        self,
        data: UserDiagnosticStatsEventUpdate,
    ) -> UserDiagnosticStatsRead:
        """Отправляет событие по пользовательской диагностике."""

        return await self._patch_user_stats(
            path="/stats/diagnostic/event",
            payload=data.model_dump(mode="json", exclude_none=True),
            response_model=UserDiagnosticStatsRead,
        )

    async def _patch_user_stats(
        self,
        *,
        path: str,
        payload: dict[str, Any],
        response_model: type[UserBotStatsRead] | type[UserDiagnosticStatsRead],
    ) -> UserBotStatsRead | UserDiagnosticStatsRead:
        try:
            response_data = await self.backend_client.patch_json(
                path=path,
                query_params={"user_id": self.user_id},
                json_payload=payload,
            )
        except BackendClientError as exc:
            raise StatsModuleError(str(exc)) from exc

        return response_model.model_validate(cast(dict[str, object], response_data))


def get_stats_client() -> FrontendStatsClient:
    """Возвращает stats client, привязанный к текущей auth-сессии."""

    auth_session = get_current_auth_session()
    if auth_session is None:
        raise StatsAuthContextError(
            "Current update does not have an authenticated backend session."
        )

    return FrontendStatsClient(
        backend_client=get_backend_client(),
        user_id=auth_session.telegram_user.id,
    )


async def mark_current_user_received_methodology() -> UserBotStatsRead:
    """Удобный helper для фиксации выдачи методички текущему пользователю."""

    return await get_stats_client().mark_methodology_received()


async def set_current_user_source(source: str) -> UserBotStatsRead:
    """Удобный helper для фиксации source текущего пользователя."""

    return await get_stats_client().set_source(source)


async def set_current_user_branch(branch: str) -> UserBotStatsRead:
    """Удобный helper для обновления current_branch текущего пользователя."""

    return await get_stats_client().set_branch(branch)


async def mark_current_user_channel_subscribed() -> UserBotStatsRead:
    """Удобный helper для фиксации подписки текущего пользователя на канал."""

    return await get_stats_client().update_user_external_stats(
        UserBotStatsExternalUpdate(channel_subscribe=True)
    )
