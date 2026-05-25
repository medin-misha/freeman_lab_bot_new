from __future__ import annotations

from datetime import datetime, time

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rmq_module import rmq_publisher
from app.modules.stats_module.services.user_bot_stats_service import UserBotStatsService
from app.modules.system import CRUD
from app.modules.telegram_module import TelegramUser, UserProfile
from app.modules.telegram_module.schemas import UserProfilePatch

from ..models import CoreRequest
from ..schemas import (
    CoreFormSubmit,
    CoreRequestAdminNotificationPayload,
    CoreRequestAdminNotificationUser,
    CoreRequestCreate,
    CoreRequestUpdate,
)


ADMIN_CORE_REQUEST_CREATED_EVENT = "admin.core_request.created"
ADMIN_CORE_REQUEST_CREATED_QUEUE = "admin.core_request.created"


def _parse_telegram_id(raw_telegram_id: str) -> int:
    normalized = raw_telegram_id.strip()
    try:
        return int(normalized)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="telegram_id must be a valid integer string.",
        ) from err


async def _get_telegram_user_by_telegram_id_or_404(
    session: AsyncSession,
    telegram_id: int,
) -> TelegramUser:
    result = await session.execute(
        select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
    )
    telegram_user = result.scalars().first()
    if telegram_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TelegramUser with telegram_id={telegram_id} not found.",
        )
    return telegram_user


async def _get_telegram_user_or_404(
    session: AsyncSession,
    user_id: int,
) -> TelegramUser:
    telegram_user = await session.get(TelegramUser, user_id)
    if telegram_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TelegramUser with id={user_id} not found.",
        )
    return telegram_user


def _get_user_profile_or_404(telegram_user: TelegramUser) -> UserProfile:
    user_profile = telegram_user.user_profile
    if user_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UserProfile for TelegramUser id={telegram_user.id} not found.",
        )
    return user_profile


async def _update_user_profile_from_submit(
    *,
    session: AsyncSession,
    telegram_user: TelegramUser,
    data: CoreFormSubmit,
) -> UserProfile:
    user_profile = _get_user_profile_or_404(telegram_user)
    return await CRUD.patch(
        new_data=UserProfilePatch(
            full_name=data.full_name,
            date_of_birth=datetime.combine(data.birth_date, time.min),
            city=data.city,
        ),
        model=UserProfile,
        session=session,
        id=user_profile.id,
    )


async def _build_admin_notification_payload(
    *,
    session: AsyncSession,
    core_request: CoreRequest,
) -> CoreRequestAdminNotificationPayload:
    telegram_user = await _get_telegram_user_or_404(
        session=session,
        user_id=core_request.user_id,
    )
    user_profile = _get_user_profile_or_404(telegram_user)
    return CoreRequestAdminNotificationPayload(
        id=core_request.id,
        created_at=core_request.created_at,
        updated_at=core_request.updated_at,
        user_id=core_request.user_id,
        activity=core_request.activity,
        request=core_request.request,
        priorities=core_request.priorities,
        motivation=core_request.motivation,
        difficulties=core_request.difficulties,
        readiness=core_request.readiness,
        weekly_time=core_request.weekly_time,
        rules=core_request.rules,
        payment=core_request.payment,
        user=CoreRequestAdminNotificationUser(
            telegram_id=telegram_user.telegram_id,
            username=telegram_user.username,
            full_name=user_profile.full_name,
            date_of_birth=user_profile.date_of_birth,
            city=user_profile.city,
        ),
    )


async def publish_core_request_created_to_admin_bot(
    *,
    session: AsyncSession,
    core_request: CoreRequest,
) -> None:
    payload = await _build_admin_notification_payload(
        session=session,
        core_request=core_request,
    )
    await rmq_publisher.publish(
        event=ADMIN_CORE_REQUEST_CREATED_EVENT,
        payload=payload.model_dump(mode="json"),
        queue_name=ADMIN_CORE_REQUEST_CREATED_QUEUE,
        routing_key=ADMIN_CORE_REQUEST_CREATED_EVENT,
    )


async def submit_core_form(
    data: CoreFormSubmit,
    session: AsyncSession,
) -> CoreRequest:
    telegram_id = _parse_telegram_id(data.telegram_id)
    telegram_user = await _get_telegram_user_by_telegram_id_or_404(
        session=session,
        telegram_id=telegram_id,
    )
    await _update_user_profile_from_submit(
        session=session,
        telegram_user=telegram_user,
        data=data,
    )

    core_request = await CRUD.create(
        data=CoreRequestCreate(
            user_id=telegram_user.id,
            activity=data.activity,
            request=data.request,
            priorities=data.priorities,
            motivation=data.motivation,
            difficulties=data.difficulties,
            readiness=data.readiness,
            weekly_time=data.weekly_time,
            rules=data.rules,
            payment=data.payment,
        ),
        model=CoreRequest,
        session=session,
    )

    await UserBotStatsService(session).update_core_application_submitted(
        telegram_user_id=telegram_user.id,
        submitted_at=core_request.created_at,
    )

    await publish_core_request_created_to_admin_bot(
        session=session,
        core_request=core_request,
    )
    return core_request


async def get_core_request(
    core_request_id: int,
    session: AsyncSession,
) -> CoreRequest:
    return await CRUD.get(model=CoreRequest, session=session, id=core_request_id)


async def list_core_requests(
    session: AsyncSession,
    *,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    field: str | None = None,
) -> list[CoreRequest]:
    return await CRUD.get(
        model=CoreRequest,
        session=session,
        page=page,
        limit=limit,
        search=search,
        field=field,
    )


async def patch_core_request(
    core_request_id: int,
    data: CoreRequestUpdate,
    session: AsyncSession,
) -> CoreRequest:
    if data.user_id is not None:
        await _get_telegram_user_or_404(session=session, user_id=data.user_id)

    return await CRUD.patch(
        new_data=data,
        model=CoreRequest,
        session=session,
        id=core_request_id,
    )


async def delete_core_request(
    core_request_id: int,
    session: AsyncSession,
) -> str:
    return await CRUD.delete(model=CoreRequest, session=session, id=core_request_id)
