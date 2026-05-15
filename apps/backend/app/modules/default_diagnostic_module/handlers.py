from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database

from .models import DefaultDiagnostic
from .schemas import DefaultDiagnosticCreate, DefaultDiagnosticRead
from .services import create_default_diagnostic


router = APIRouter(prefix="/diagnostic", tags=["default-diagnostic"])

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]


@router.post("/default", response_model=DefaultDiagnosticRead, status_code=status.HTTP_201_CREATED)
async def create_default_diagnostic_endpoint(
    data: DefaultDiagnosticCreate,
    session: SessionDep,
) -> DefaultDiagnostic:
    return await create_default_diagnostic(data=data, session=session)
