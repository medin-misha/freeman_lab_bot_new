from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database

from .models import AnalysisRegistration
from .schemas import AnalysisRegistrationCreate, AnalysisRegistrationRead
from .services import (
    create_analysis_registration,
    delete_analysis_registration,
    get_analysis_registration,
    list_analysis_registrations,
)


router = APIRouter(
    prefix="/analysis-registrations",
    tags=["analysis-registrations"],
)

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]


@router.post(
    "",
    response_model=AnalysisRegistrationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_analysis_registration_handler(
    data: AnalysisRegistrationCreate,
    session: SessionDep,
) -> AnalysisRegistration:
    return await create_analysis_registration(data=data, session=session)


@router.get("/{id}", response_model=AnalysisRegistrationRead)
async def get_analysis_registration_handler(
    id: int,
    session: SessionDep,
) -> AnalysisRegistration:
    return await get_analysis_registration(registration_id=id, session=session)


@router.get("", response_model=list[AnalysisRegistrationRead])
async def list_analysis_registrations_handler(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1)] = 10,
    user_id: int | None = None,
) -> list[AnalysisRegistration]:
    return await list_analysis_registrations(
        session=session,
        page=page,
        limit=limit,
        user_id=user_id,
    )


@router.delete("/{id}")
async def delete_analysis_registration_handler(
    id: int,
    session: SessionDep,
) -> dict[str, str]:
    result = await delete_analysis_registration(registration_id=id, session=session)
    return {"status": result}
