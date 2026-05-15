import logging
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.system import CRUD
from app.modules.system.services.errors import DBErrorHandler

from ..models import TelegramUser, UserProfile
from ..schemas import TelegramUserCreate, UserProfileCreate


logger = logging.getLogger(__name__)


async def _delete_telegram_users_by_ids(
    session: AsyncSession,
    user_ids: list[int],
) -> None:
    if not user_ids:
        return

    try:
        await session.execute(
            delete(TelegramUser).where(TelegramUser.id.in_(user_ids))
        )
        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception(
            "Failed to clean up TelegramUser records after UserProfile creation error.",
            extra={"telegram_user_ids": user_ids},
        )


async def create_telegram_user(
    data: TelegramUserCreate,
    session: AsyncSession,
) -> tuple[TelegramUser, bool]:
    telegram_user, created = await CRUD.get_or_create(
        data=data,
        model=TelegramUser,
        session=session,
        lookup_fields=("telegram_id",),
    )

    if not created:
        return telegram_user, False

    try:
        await CRUD.create(
            data=UserProfileCreate(telegram_user_id=telegram_user.id),
            model=UserProfile,
            session=session,
        )
    except HTTPException:
        await _delete_telegram_users_by_ids(session=session, user_ids=[telegram_user.id])
        raise

    return telegram_user, True


async def bulk_create_telegram_users(
    data: list[TelegramUserCreate],
    session: AsyncSession,
) -> list[TelegramUser]:
    telegram_users = await CRUD.bulk_create(
        data=data,
        model=TelegramUser,
        session=session,
    )

    try:
        await CRUD.bulk_create(
            data=[
                UserProfileCreate(telegram_user_id=telegram_user.id)
                for telegram_user in telegram_users
            ],
            model=UserProfile,
            session=session,
        )
    except HTTPException:
        await _delete_telegram_users_by_ids(
            session=session,
            user_ids=[telegram_user.id for telegram_user in telegram_users],
        )
        raise

    return telegram_users


async def login_telegram_user(
    telegram_id: int,
    session: AsyncSession,
) -> TelegramUser:
    try:
        result = await session.execute(
            select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
        )
        telegram_user = result.scalars().first()

        if telegram_user is None:
            raise HTTPException(
                status_code=404,
                detail=f"TelegramUser with telegram_id={telegram_id} not found.",
            )

        telegram_user.last_seen_at = datetime.utcnow()
        await session.commit()
        await session.refresh(telegram_user)
    except HTTPException:
        raise
    except Exception as err:
        await session.rollback()
        DBErrorHandler.handle(err=err, model=TelegramUser, action="logging in")
    else:
        return telegram_user
