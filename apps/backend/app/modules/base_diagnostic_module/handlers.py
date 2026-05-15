from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database

from .models import DiagnosticRun
from .schemas import (
    DiagnosticRunComplete,
    DiagnosticRunCreate,
    DiagnosticRunFileAttach,
    DiagnosticRunRead,
    DiagnosticRunStatusUpdate,
)
from .services import (
    attach_result_file,
    attach_transcribation_file,
    attach_voice_file,
    change_status,
    complete_run,
    create_run,
    get_run,
    list_runs,
)


router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]


@router.post("/runs", response_model=DiagnosticRunRead, status_code=status.HTTP_201_CREATED)
async def create_diagnostic_run(
    data: DiagnosticRunCreate,
    session: SessionDep,
) -> DiagnosticRun:
    return await create_run(data=data, session=session)


@router.get("/runs/{id}", response_model=DiagnosticRunRead)
async def get_diagnostic_run(
    id: int,
    session: SessionDep,
) -> DiagnosticRun:
    return await get_run(run_id=id, session=session)


@router.get("/runs", response_model=list[DiagnosticRunRead])
async def list_diagnostic_runs(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1)] = 10,
    user_id: int | None = None,
    diagnostic_code: str | None = None,
) -> list[DiagnosticRun]:
    return await list_runs(
        session=session,
        page=page,
        limit=limit,
        user_id=user_id,
        diagnostic_code=diagnostic_code,
    )


@router.patch("/runs/{id}/status", response_model=DiagnosticRunRead)
async def patch_diagnostic_run_status(
    id: int,
    data: DiagnosticRunStatusUpdate,
    session: SessionDep,
) -> DiagnosticRun:
    return await change_status(run_id=id, new_status=data.status, session=session)


@router.patch("/runs/{id}/voice-file", response_model=DiagnosticRunRead)
async def patch_diagnostic_run_voice_file(
    id: int,
    data: DiagnosticRunFileAttach,
    session: SessionDep,
) -> DiagnosticRun:
    return await attach_voice_file(run_id=id, file_id=data.file_id, session=session)


@router.patch("/runs/{id}/result-file", response_model=DiagnosticRunRead)
async def patch_diagnostic_run_result_file(
    id: int,
    data: DiagnosticRunFileAttach,
    session: SessionDep,
) -> DiagnosticRun:
    return await attach_result_file(run_id=id, file_id=data.file_id, session=session)


@router.patch("/runs/{id}/transcribation-file", response_model=DiagnosticRunRead)
async def patch_diagnostic_run_transcribation_file(
    id: int,
    data: DiagnosticRunFileAttach,
    session: SessionDep,
) -> DiagnosticRun:
    return await attach_transcribation_file(
        run_id=id,
        file_id=data.file_id,
        session=session,
    )


@router.post("/runs/{id}/complete", response_model=DiagnosticRunRead)
async def complete_diagnostic_run(
    id: int,
    data: DiagnosticRunComplete,
    session: SessionDep,
) -> DiagnosticRun:
    return await complete_run(
        run_id=id,
        result_file_id=data.result_file_id,
        session=session,
    )
