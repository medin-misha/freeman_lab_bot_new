import io
import logging
import mimetypes
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database
from app.modules.system import CRUD

from .models import File
from .schemas import FileCreate, FileRead
from .services import s3_client

router = APIRouter(prefix="/files", tags=["Files"])
logger = logging.getLogger(__name__)

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]


@router.post("/", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    session: SessionDep,
    file: UploadFile,
    note: Annotated[str | None, Form()] = None,
) -> File:
    filename = file.filename or "unnamed"
    link = await s3_client.create(
        file_obj=file.file,
        filename=filename,
        content_type=file.content_type or "application/octet-stream",
    )
    try:
        return await CRUD.create(
            data=FileCreate(link=link, name=filename, note=note),
            model=File,
            session=session,
        )
    except Exception:
        await s3_client.delete(link)
        raise


@router.get("/{id}", response_class=StreamingResponse)
async def download_file(
    id: int,
    session: SessionDep,
) -> StreamingResponse:
    file_record: File = await CRUD.get(model=File, session=session, id=id)
    data = await s3_client.read(link=file_record.link)

    content_type, _ = mimetypes.guess_type(file_record.name)
    encoded_name = quote(file_record.name, safe="")
    return StreamingResponse(
        io.BytesIO(data),
        media_type=content_type or "application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}"},
    )


@router.delete("/{id}")
async def delete_file(
    id: int,
    session: SessionDep,
) -> dict[str, str]:
    file_record: File = await CRUD.get(model=File, session=session, id=id)
    link = file_record.link

    # DB first — transactional. If this fails, S3 file is untouched.
    await session.delete(file_record)
    await session.commit()

    # S3 after commit — best-effort. If this fails, the DB record is already
    # gone so no broken link exists; the orphaned object can be cleaned manually.
    try:
        await s3_client.delete(link=link)
    except Exception:
        logger.warning("S3 delete failed for link %s after DB record was removed", link)

    return {"status": "ok"}
