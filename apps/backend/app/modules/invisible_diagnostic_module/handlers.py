from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database

from .models import InvisibleDiagnostic
from .schemas import InvisibleDiagnosticCreate, InvisibleDiagnosticRead
from .services import create_invisible_diagnostic


router = APIRouter(prefix="/diagnostic", tags=["invisible-diagnostic"])

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]


@router.post(
    "/invisible",
    response_model=InvisibleDiagnosticRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_invisible_diagnostic_endpoint(
    data: InvisibleDiagnosticCreate,
    session: SessionDep,
) -> InvisibleDiagnostic:
    return await create_invisible_diagnostic(data=data, session=session)
