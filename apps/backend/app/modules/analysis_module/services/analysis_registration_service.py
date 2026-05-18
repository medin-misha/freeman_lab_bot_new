from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rmq_module import rmq_publisher
from app.modules.system import CRUD
from app.modules.telegram_module import TelegramUser

from ..models import AnalysisRegistration
from ..schemas import (
    AnalysisRegistrationAdminNotificationPayload,
    AnalysisRegistrationAdminNotificationUser,
    AnalysisRegistrationCreate,
)


ADMIN_ANALYSIS_REGISTRATION_CREATED_EVENT = "admin.analysis_registration.created"
ADMIN_ANALYSIS_REGISTRATION_CREATED_QUEUE = "admin.analysis_registration.created"


async def _get_user_or_404(
    session: AsyncSession,
    user_id: int,
) -> TelegramUser:
    user = await session.get(TelegramUser, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TelegramUser with id={user_id} not found.",
        )
    return user


async def _build_admin_notification_payload(
    *,
    session: AsyncSession,
    analysis_registration: AnalysisRegistration,
) -> AnalysisRegistrationAdminNotificationPayload:
    user = await _get_user_or_404(
        session=session,
        user_id=analysis_registration.user_id,
    )
    user_profile = user.user_profile
    return AnalysisRegistrationAdminNotificationPayload(
        id=analysis_registration.id,
        created_at=analysis_registration.created_at,
        updated_at=analysis_registration.updated_at,
        user_id=analysis_registration.user_id,
        user=AnalysisRegistrationAdminNotificationUser(
            telegram_id=user.telegram_id,
            username=user.username,
            full_name=user_profile.full_name if user_profile else None,
            date_of_birth=user_profile.date_of_birth if user_profile else None,
            city=user_profile.city if user_profile else None,
        ),
    )


async def publish_analysis_registration_created_to_admin_bot(
    *,
    session: AsyncSession,
    analysis_registration: AnalysisRegistration,
) -> None:
    payload = await _build_admin_notification_payload(
        session=session,
        analysis_registration=analysis_registration,
    )
    await rmq_publisher.publish(
        event=ADMIN_ANALYSIS_REGISTRATION_CREATED_EVENT,
        payload=payload.model_dump(mode="json"),
        queue_name=ADMIN_ANALYSIS_REGISTRATION_CREATED_QUEUE,
        routing_key=ADMIN_ANALYSIS_REGISTRATION_CREATED_EVENT,
    )


async def create_analysis_registration(
    data: AnalysisRegistrationCreate,
    session: AsyncSession,
) -> AnalysisRegistration:
    await _get_user_or_404(session=session, user_id=data.user_id)
    analysis_registration = await CRUD.create(
        data=AnalysisRegistrationCreate(user_id=data.user_id),
        model=AnalysisRegistration,
        session=session,
    )

    await publish_analysis_registration_created_to_admin_bot(
        session=session,
        analysis_registration=analysis_registration,
    )
    return analysis_registration


async def get_analysis_registration(
    registration_id: int,
    session: AsyncSession,
) -> AnalysisRegistration:
    return await CRUD.get(model=AnalysisRegistration, session=session, id=registration_id)


async def list_analysis_registrations(
    session: AsyncSession,
    *,
    page: int = 1,
    limit: int = 10,
    user_id: int | None = None,
) -> list[AnalysisRegistration]:
    filters = {"user_id": user_id} if user_id is not None else None
    return await CRUD.get(
        model=AnalysisRegistration,
        session=session,
        page=page,
        limit=limit,
        filters=filters,
    )


async def delete_analysis_registration(
    registration_id: int,
    session: AsyncSession,
) -> str:
    return await CRUD.delete(model=AnalysisRegistration, session=session, id=registration_id)
