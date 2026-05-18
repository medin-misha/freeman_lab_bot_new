from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database

from .models import CoreRequest
from .schemas import CoreFormSubmit, CoreRequestRead, CoreRequestUpdate
from .services import (
    delete_core_request,
    get_core_request,
    list_core_requests,
    patch_core_request,
    submit_core_form,
)


router = APIRouter(prefix="/core", tags=["core"])

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]


@router.get("", response_model=list[CoreRequestRead], status_code=status.HTTP_200_OK)
async def list_core_requests_handler(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1)] = 10,
    search: str | None = None,
    field: str | None = None,
) -> list[CoreRequest]:
    return await list_core_requests(
        session=session,
        page=page,
        limit=limit,
        search=search,
        field=field,
    )


@router.get("/{id}", response_model=CoreRequestRead, status_code=status.HTTP_200_OK)
async def get_core_request_handler(
    id: int,
    session: SessionDep,
) -> CoreRequest:
    return await get_core_request(core_request_id=id, session=session)


@router.post(
    "/submit",
    response_model=CoreRequestRead,
    status_code=status.HTTP_201_CREATED,
)
async def submit_core_form_handler(
    data: CoreFormSubmit,
    session: SessionDep,
) -> CoreRequest:
    return await submit_core_form(data=data, session=session)


@router.patch("/{id}", response_model=CoreRequestRead, status_code=status.HTTP_200_OK)
async def patch_core_request_handler(
    id: int,
    data: CoreRequestUpdate,
    session: SessionDep,
) -> CoreRequest:
    return await patch_core_request(core_request_id=id, data=data, session=session)


@router.delete("/{id}", response_model=str, status_code=status.HTTP_200_OK)
async def delete_core_request_handler(
    id: int,
    session: SessionDep,
) -> str:
    return await delete_core_request(core_request_id=id, session=session)
