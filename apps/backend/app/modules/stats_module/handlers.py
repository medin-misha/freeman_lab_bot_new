from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database

from .models import UserBotStats, UserDiagnosticStats
from .schemas import (
    UserBotStatsExternalUpdate,
    UserBotStatsInternalUpdate,
    UserBotStatsRead,
    UserDiagnosticStatsEventUpdate,
    UserDiagnosticStatsRead,
    UserStatsRebuildRead,
)
from .services import StatsRebuildService, UserBotStatsService, UserDiagnosticStatsService


router = APIRouter(prefix="/stats", tags=["stats"])

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]


@router.get("/user", response_model=UserBotStatsRead, status_code=status.HTTP_200_OK)
async def get_user_bot_stats_handler(
    session: SessionDep,
    user_id: int | None = Query(default=None),
    chat_id: int | None = Query(default=None),
) -> UserBotStats:
    service = UserBotStatsService(session)
    return await service.get_for_user(user_id=user_id, chat_id=chat_id)


@router.patch("/user/external", response_model=UserBotStatsRead, status_code=status.HTTP_200_OK)
async def patch_user_bot_stats_external_handler(
    data: UserBotStatsExternalUpdate,
    session: SessionDep,
    user_id: int | None = Query(default=None),
    chat_id: int | None = Query(default=None),
) -> UserBotStats:
    service = UserBotStatsService(session)
    return await service.apply_external_update(data, user_id=user_id, chat_id=chat_id)


@router.patch("/user/internal", response_model=UserBotStatsRead, status_code=status.HTTP_200_OK)
async def patch_user_bot_stats_internal_handler(
    data: UserBotStatsInternalUpdate,
    session: SessionDep,
    user_id: int | None = Query(default=None),
    chat_id: int | None = Query(default=None),
) -> UserBotStats:
    service = UserBotStatsService(session)
    return await service.apply_internal_update(data, user_id=user_id, chat_id=chat_id)


@router.get("/diagnostic", response_model=UserDiagnosticStatsRead, status_code=status.HTTP_200_OK)
async def get_user_diagnostic_stats_handler(
    diagnostic_code: str,
    session: SessionDep,
    user_id: int | None = Query(default=None),
    chat_id: int | None = Query(default=None),
) -> UserDiagnosticStats:
    service = UserDiagnosticStatsService(session)
    return await service.get_for_user_and_diagnostic(
        diagnostic_code=diagnostic_code,
        user_id=user_id,
        chat_id=chat_id,
    )


@router.patch("/diagnostic/event", response_model=UserDiagnosticStatsRead, status_code=status.HTTP_200_OK)
async def patch_user_diagnostic_stats_event_handler(
    data: UserDiagnosticStatsEventUpdate,
    session: SessionDep,
    user_id: int | None = Query(default=None),
    chat_id: int | None = Query(default=None),
) -> UserDiagnosticStats:
    service = UserDiagnosticStatsService(session)
    return await service.apply_event(data, user_id=user_id, chat_id=chat_id)


@router.post(
    "/admin/rebuild/user",
    response_model=UserStatsRebuildRead,
    status_code=status.HTTP_200_OK,
)
async def rebuild_user_stats_handler(
    session: SessionDep,
    user_id: int | None = Query(default=None),
    chat_id: int | None = Query(default=None),
) -> UserStatsRebuildRead:
    service = StatsRebuildService(session)
    user_bot_stats, diagnostic_stats, rebuilt_at = await service.rebuild_user(
        user_id=user_id,
        chat_id=chat_id,
    )
    return UserStatsRebuildRead(
        rebuilt_at=rebuilt_at,
        user_bot_stats=user_bot_stats,
        diagnostic_stats=diagnostic_stats,
    )


@router.post(
    "/admin/rebuild/batch",
    response_model=list[UserStatsRebuildRead],
    status_code=status.HTTP_200_OK,
)
async def rebuild_user_stats_batch_handler(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 100,
) -> list[UserStatsRebuildRead]:
    service = StatsRebuildService(session)
    rebuilt = await service.rebuild_users_batch(offset=offset, limit=limit)
    return [
        UserStatsRebuildRead(
            rebuilt_at=rebuilt_at,
            user_bot_stats=user_bot_stats,
            diagnostic_stats=diagnostic_stats,
        )
        for user_bot_stats, diagnostic_stats, rebuilt_at in rebuilt
    ]
