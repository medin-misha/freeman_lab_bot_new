from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.base_diagnostic_module import DiagnosticRun, DiagnosticRunStatus
from app.modules.base_diagnostic_module.services import publish_run_created_to_admin_bot
from app.modules.file_module import File
from app.modules.system.services.errors import DBErrorHandler
from app.modules.telegram_module import TelegramUser

from ..models import InvisibleDiagnostic
from ..schemas import InvisibleDiagnosticCreate


INVISIBLE_DIAGNOSTIC_CODE = "invisible"


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


async def _get_file_or_404(
    session: AsyncSession,
    file_id: int,
) -> File:
    file_record = await session.get(File, file_id)
    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id={file_id} not found.",
        )
    return file_record


async def create_invisible_diagnostic(
    data: InvisibleDiagnosticCreate,
    session: AsyncSession,
) -> InvisibleDiagnostic:
    try:
        await _get_user_or_404(session=session, user_id=data.user_id)
        await _get_file_or_404(session=session, file_id=data.voice_file_id)

        run = DiagnosticRun(
            user_id=data.user_id,
            diagnostic_code=INVISIBLE_DIAGNOSTIC_CODE,
            status=DiagnosticRunStatus.CREATED,
            voice_file_id=data.voice_file_id,
            description=data.description,
        )
        session.add(run)
        await session.flush()

        invisible_diagnostic = InvisibleDiagnostic(diagnostic_run_id=run.id)
        session.add(invisible_diagnostic)

        await session.commit()
    except HTTPException:
        raise
    except Exception as err:
        await session.rollback()
        DBErrorHandler.handle(err=err, model=InvisibleDiagnostic, action="creating")

    stmt = (
        select(InvisibleDiagnostic)
        .options(selectinload(InvisibleDiagnostic.diagnostic_run))
        .where(InvisibleDiagnostic.id == invisible_diagnostic.id)
    )
    result = await session.execute(stmt)
    created = result.scalar_one()
    await publish_run_created_to_admin_bot(
        session=session,
        run=created.diagnostic_run,
    )
    return created
