from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.file_module import File
from app.modules.rmq_module import rmq_publisher
from app.modules.stats_module.services.user_bot_stats_service import UserBotStatsService
from app.modules.stats_module.services.user_diagnostic_stats_service import (
    UserDiagnosticStatsService,
)
from app.modules.system.services.errors import DBErrorHandler
from app.modules.telegram_module import TelegramUser

from ..models import DiagnosticRun, DiagnosticRunStatus
from ..schemas import (
    DiagnosticRunAdminNotificationFile,
    DiagnosticRunAdminNotificationPayload,
    DiagnosticRunAdminNotificationUser,
    DiagnosticRunCreate,
    DiagnosticRunFrontendNotificationPayload,
)


logger = logging.getLogger(__name__)
ADMIN_DIAGNOSTIC_CREATED_EVENT = "admin.diagnostic.created"
ADMIN_DIAGNOSTIC_CREATED_QUEUE = "admin.diagnostic.created"
FRONTEND_DIAGNOSTIC_COMPLETED_EVENT = "frontend.diagnostic.completed"
FRONTEND_DIAGNOSTIC_COMPLETED_QUEUE = "frontend.diagnostic.completed"


def _serialize_run_payload(run: DiagnosticRun) -> dict[str, object]:
    return {
        "id": run.id,
        "created_at": run.created_at,
        "updated_at": run.updated_at,
        "voice_file_id": run.voice_file_id,
        "result_file_id": run.result_file_id,
        "transcribation_file_id": run.transcribation_file_id,
        "user_id": run.user_id,
        "diagnostic_code": run.diagnostic_code,
        "status": run.status,
        "completed_at": run.completed_at,
        "note": run.note,
        "description": run.description,
        "tag": run.tag,
    }


async def _get_run_or_404(
    session: AsyncSession,
    run_id: int,
) -> DiagnosticRun:
    run = await session.get(DiagnosticRun, run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DiagnosticRun with id={run_id} not found.",
        )
    return run


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


def _validate_status(raw_status: str) -> str:
    normalized_status = raw_status.strip().lower()
    if normalized_status not in DiagnosticRunStatus.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid diagnostic status. "
                f"Allowed values: {sorted(DiagnosticRunStatus.values())}."
            ),
        )
    return normalized_status


async def _publish_run_event(
    event: str,
    run: DiagnosticRun,
) -> None:
    await rmq_publisher.publish(
        event=event,
        payload=_serialize_run_payload(run),
        routing_key=event,
    )


async def _build_admin_notification_payload(
    *,
    session: AsyncSession,
    run: DiagnosticRun,
) -> DiagnosticRunAdminNotificationPayload:
    user = await _get_user_or_404(session=session, user_id=run.user_id)
    user_profile = user.user_profile
    voice_file: DiagnosticRunAdminNotificationFile | None = None
    if run.voice_file_id is not None:
        file_record = await _get_file_or_404(session=session, file_id=run.voice_file_id)
        voice_file = DiagnosticRunAdminNotificationFile(
            id=file_record.id,
            name=file_record.name,
            link=file_record.link,
            note=file_record.note,
        )

    return DiagnosticRunAdminNotificationPayload(
        id=run.id,
        created_at=run.created_at,
        updated_at=run.updated_at,
        voice_file_id=run.voice_file_id,
        result_file_id=run.result_file_id,
        transcribation_file_id=run.transcribation_file_id,
        user_id=run.user_id,
        diagnostic_code=run.diagnostic_code,
        status=run.status,
        completed_at=run.completed_at,
        note=run.note,
        description=run.description,
        tag=run.tag,
        user=DiagnosticRunAdminNotificationUser(
            telegram_id=user.telegram_id,
            username=user.username,
            full_name=user_profile.full_name if user_profile else None,
            date_of_birth=user_profile.date_of_birth if user_profile else None,
            city=user_profile.city if user_profile else None,
        ),
        voice_file=voice_file,
    )


async def publish_run_created_to_admin_bot(
    *,
    session: AsyncSession,
    run: DiagnosticRun,
) -> None:
    payload = await _build_admin_notification_payload(session=session, run=run)
    await rmq_publisher.publish(
        event=ADMIN_DIAGNOSTIC_CREATED_EVENT,
        payload=payload.model_dump(mode="json"),
        queue_name=ADMIN_DIAGNOSTIC_CREATED_QUEUE,
        routing_key=ADMIN_DIAGNOSTIC_CREATED_EVENT,
    )


async def publish_run_completed_to_frontend_bot(
    *,
    session: AsyncSession,
    run: DiagnosticRun,
) -> None:
    if run.result_file_id is None:
        logger.warning(
            "Diagnostic run %s completed without result_file_id; frontend notification skipped",
            run.id,
        )
        return

    result_file_name = "Результат_Диагностики.pdf"
    file_record = await session.get(File, run.result_file_id)
    if file_record is not None:
        result_file_name = _normalize_result_filename(file_record.name)

    payload = DiagnosticRunFrontendNotificationPayload(
        id=run.id,
        user_id=run.user_id,
        result_file_id=run.result_file_id,
        result_file_name=result_file_name,
        diagnostic_code=run.diagnostic_code,
        completed_at=run.completed_at,
    )
    await rmq_publisher.publish(
        event=FRONTEND_DIAGNOSTIC_COMPLETED_EVENT,
        payload=payload.model_dump(mode="json"),
        queue_name=FRONTEND_DIAGNOSTIC_COMPLETED_QUEUE,
        routing_key=FRONTEND_DIAGNOSTIC_COMPLETED_EVENT,
    )


def _normalize_result_filename(raw_name: str | None) -> str:
    normalized = (raw_name or "").strip()
    if not normalized:
        return "Результат_Диагностики.pdf"

    suffix = Path(normalized).suffix.strip()
    if suffix:
        return normalized

    return f"{normalized}.pdf"


async def create_run(
    data: DiagnosticRunCreate,
    session: AsyncSession,
) -> DiagnosticRun:
    try:
        await _get_user_or_404(session=session, user_id=data.user_id)

        run = DiagnosticRun(
            user_id=data.user_id,
            diagnostic_code=data.diagnostic_code.strip(),
            status=DiagnosticRunStatus.CREATED,
            note=data.note,
            description=data.description,
            tag=data.tag,
        )
        session.add(run)
        await session.flush()
        await UserDiagnosticStatsService(session).ensure_for_user_and_diagnostic(
            telegram_user_id=run.user_id,
            diagnostic_code=run.diagnostic_code,
            flush=False,
        )
        await UserBotStatsService(session).increment_diagnostics_created(
            telegram_user_id=run.user_id,
            at=run.created_at,
            flush=False,
        )
        await session.commit()
        await session.refresh(run)
    except HTTPException:
        raise
    except Exception as err:
        await session.rollback()
        DBErrorHandler.handle(err=err, model=DiagnosticRun, action="creating")

    await _publish_run_event(event="diagnostic.created", run=run)
    await publish_run_created_to_admin_bot(session=session, run=run)
    return run


async def get_run(
    run_id: int,
    session: AsyncSession,
) -> DiagnosticRun:
    try:
        return await _get_run_or_404(session=session, run_id=run_id)
    except HTTPException:
        raise
    except Exception as err:
        DBErrorHandler.handle(err=err, model=DiagnosticRun, action="reading")


async def list_runs(
    session: AsyncSession,
    *,
    page: int = 1,
    limit: int = 10,
    user_id: int | None = None,
    diagnostic_code: str | None = None,
) -> list[DiagnosticRun]:
    try:
        page = max(page, 1)
        limit = max(limit, 1)

        stmt: Select[tuple[DiagnosticRun]] = select(DiagnosticRun)
        if user_id is not None:
            stmt = stmt.where(DiagnosticRun.user_id == user_id)
        if diagnostic_code is not None:
            stmt = stmt.where(DiagnosticRun.diagnostic_code == diagnostic_code.strip())

        stmt = (
            stmt.order_by(DiagnosticRun.created_at.desc(), DiagnosticRun.id.desc())
            .limit(limit)
            .offset((page - 1) * limit)
        )
        result: Result = await session.execute(stmt)
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception as err:
        DBErrorHandler.handle(err=err, model=DiagnosticRun, action="reading")


async def change_status(
    run_id: int,
    new_status: str,
    session: AsyncSession,
) -> DiagnosticRun:
    normalized_status = _validate_status(new_status)

    try:
        run = await _get_run_or_404(session=session, run_id=run_id)
        previous_status = run.status

        if previous_status == normalized_status:
            return run

        run.status = normalized_status
        if normalized_status == DiagnosticRunStatus.COMPLETED and run.completed_at is None:
            run.completed_at = datetime.now(timezone.utc)

        if normalized_status == DiagnosticRunStatus.COMPLETED:
            await UserBotStatsService(session).increment_diagnostics_completed(
                telegram_user_id=run.user_id,
                at=run.completed_at,
                flush=False,
            )

        await session.commit()
        await session.refresh(run)
    except HTTPException:
        raise
    except Exception as err:
        await session.rollback()
        DBErrorHandler.handle(err=err, model=DiagnosticRun, action="updating")

    await _publish_run_event(event="diagnostic.status_changed", run=run)
    if normalized_status == DiagnosticRunStatus.COMPLETED:
        await _publish_run_event(event="diagnostic.completed", run=run)
    return run


async def attach_voice_file(
    run_id: int,
    file_id: int,
    session: AsyncSession,
) -> DiagnosticRun:
    try:
        run = await _get_run_or_404(session=session, run_id=run_id)
        await _get_file_or_404(session=session, file_id=file_id)
        run.voice_file_id = file_id
        await session.commit()
        await session.refresh(run)
        return run
    except HTTPException:
        raise
    except Exception as err:
        await session.rollback()
        DBErrorHandler.handle(err=err, model=DiagnosticRun, action="updating")


async def attach_result_file(
    run_id: int,
    file_id: int,
    session: AsyncSession,
) -> DiagnosticRun:
    try:
        run = await _get_run_or_404(session=session, run_id=run_id)
        await _get_file_or_404(session=session, file_id=file_id)
        changed = run.result_file_id != file_id
        run.result_file_id = file_id
        await session.commit()
        await session.refresh(run)
    except HTTPException:
        raise
    except Exception as err:
        await session.rollback()
        DBErrorHandler.handle(err=err, model=DiagnosticRun, action="updating")

    if changed:
        await _publish_run_event(event="diagnostic.result_attached", run=run)
    return run


async def attach_transcribation_file(
    run_id: int,
    file_id: int,
    session: AsyncSession,
) -> DiagnosticRun:
    try:
        run = await _get_run_or_404(session=session, run_id=run_id)
        await _get_file_or_404(session=session, file_id=file_id)
        run.transcribation_file_id = file_id
        await session.commit()
        await session.refresh(run)
        return run
    except HTTPException:
        raise
    except Exception as err:
        await session.rollback()
        DBErrorHandler.handle(err=err, model=DiagnosticRun, action="updating")


async def complete_run(
    run_id: int,
    session: AsyncSession,
    *,
    result_file_id: int | None = None,
) -> DiagnosticRun:
    try:
        run = await _get_run_or_404(session=session, run_id=run_id)
        result_attached = False

        if result_file_id is not None:
            await _get_file_or_404(session=session, file_id=result_file_id)
            result_attached = run.result_file_id != result_file_id
            run.result_file_id = result_file_id

        status_changed = run.status != DiagnosticRunStatus.COMPLETED
        run.status = DiagnosticRunStatus.COMPLETED
        if run.completed_at is None:
            run.completed_at = datetime.now(timezone.utc)

        if status_changed:
            await UserBotStatsService(session).increment_diagnostics_completed(
                telegram_user_id=run.user_id,
                at=run.completed_at,
                flush=False,
            )

        await session.commit()
        await session.refresh(run)
    except HTTPException:
        raise
    except Exception as err:
        await session.rollback()
        DBErrorHandler.handle(err=err, model=DiagnosticRun, action="completing")

    if result_attached:
        await _publish_run_event(event="diagnostic.result_attached", run=run)
    if status_changed:
        await _publish_run_event(event="diagnostic.status_changed", run=run)
        await _publish_run_event(event="diagnostic.completed", run=run)
    await publish_run_completed_to_frontend_bot(session=session, run=run)
    return run
