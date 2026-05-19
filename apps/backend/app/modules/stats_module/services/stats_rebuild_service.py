from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.telegram_module import TelegramUser

from ..models import UserBotStats, UserDiagnosticStats
from ..utils import utcnow
from .user_bot_stats_service import UserBotStatsService
from .user_diagnostic_stats_service import UserDiagnosticStatsService


class StatsRebuildService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_bot_stats_service = UserBotStatsService(session)
        self.user_diagnostic_stats_service = UserDiagnosticStatsService(session)

    async def rebuild_user(
        self,
        *,
        user_id: int | None = None,
        chat_id: int | None = None,
    ) -> tuple[UserBotStats, list[UserDiagnosticStats], datetime]:
        user_bot_stats = await self.user_bot_stats_service.rebuild_for_user(
            user_id=user_id,
            chat_id=chat_id,
        )
        diagnostic_stats = await self.user_diagnostic_stats_service.rebuild_for_user(
            user_id=user_id,
            chat_id=chat_id,
        )
        return user_bot_stats, diagnostic_stats, utcnow()

    async def rebuild_users_batch(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[tuple[UserBotStats, list[UserDiagnosticStats], datetime]]:
        result = await self.session.execute(
            select(TelegramUser.id)
            .order_by(TelegramUser.id.asc())
            .offset(max(offset, 0))
            .limit(max(limit, 1))
        )
        user_ids = list(result.scalars().all())
        rebuilt: list[tuple[UserBotStats, list[UserDiagnosticStats], datetime]] = []
        for user_id in user_ids:
            rebuilt.append(await self.rebuild_user(user_id=user_id))
        return rebuilt
