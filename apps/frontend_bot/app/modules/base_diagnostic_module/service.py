"""
Оркестрация создания диагностик через backend API.

Модуль скрывает от продуктовых сценариев все транспортные шаги:
поиск backend user по `chat_id`, скачивание Telegram document, создание
backend file и вызов product diagnostic endpoint.
"""

from __future__ import annotations

import io
from typing import TypeAlias, cast

from aiogram import Bot
from aiogram.types import Audio, Document, Voice

from app.modules.system.client import (
    BackendClientError,
    BackendUnexpectedResponseError,
    get_backend_client,
)
from app.modules.system.schemas import TelegramUserRead

from .schemas import (
    DiagnosticCreatePayload,
    DiagnosticCreationResult,
    DiagnosticModuleRead,
    FileRead,
)

TelegramDiagnosticMedia: TypeAlias = Document | Audio | Voice


class BaseDiagnosticModuleError(RuntimeError):
    """Базовая ошибка orchestration-модуля диагностик."""


class DiagnosticUserNotFoundError(BaseDiagnosticModuleError):
    """Backend не нашёл Telegram user по переданному chat_id."""


class InvalidDiagnosticTypeError(BaseDiagnosticModuleError):
    """Diagnostic type пустой или содержит небезопасный path."""


def _normalize_diagnostic_type(diagnostic_type: str) -> str:
    normalized = diagnostic_type.strip().strip("/")
    if not normalized or "/" in normalized:
        raise InvalidDiagnosticTypeError(
            "Diagnostic type must be a non-empty single path segment."
        )
    return normalized


async def _find_backend_user(chat_id: int) -> TelegramUserRead:
    backend_client = get_backend_client()
    payload = await backend_client.get_json(
        path="/telegram/users",
        query_params={
            "search": str(chat_id),
            "field": "telegram_id",
            "page": 1,
            "limit": 1,
        },
    )
    if not isinstance(payload, list):
        raise BackendUnexpectedResponseError(
            "Backend returned an invalid telegram user list payload."
        )

    for item in payload:
        user = TelegramUserRead.model_validate(item)
        if user.telegram_id == chat_id:
            return user

    raise DiagnosticUserNotFoundError(
        f"Telegram user with chat_id={chat_id} was not found in backend."
    )


async def _download_telegram_file_bytes(
    *,
    bot: Bot,
    telegram_file_id: str,
    filename: str,
    content_type: str,
) -> tuple[bytes, str, str]:
    telegram_file = await bot.get_file(telegram_file_id)
    buffer = io.BytesIO()
    await bot.download(telegram_file, destination=buffer)
    return buffer.getvalue(), filename, content_type


def _extract_telegram_file_metadata(
    media: TelegramDiagnosticMedia,
) -> tuple[str, str, str]:
    if isinstance(media, Document):
        return (
            media.file_id,
            media.file_name or f"document_{media.file_unique_id}",
            media.mime_type or "application/octet-stream",
        )

    if isinstance(media, Audio):
        return (
            media.file_id,
            media.file_name or f"audio_{media.file_unique_id}",
            media.mime_type or "audio/mpeg",
        )

    return (
        media.file_id,
        f"voice_{media.file_unique_id}.ogg",
        media.mime_type or "audio/ogg",
    )


async def _create_backend_file(
    *,
    file_bytes: bytes,
    filename: str,
    content_type: str,
) -> FileRead:
    backend_client = get_backend_client()
    payload = await backend_client.post_multipart(
        path="/files/",
        file_field_name="file",
        filename=filename,
        file_bytes=file_bytes,
        content_type=content_type,
    )
    return FileRead.model_validate(payload)


async def _create_backend_diagnostic(
    *,
    user_id: int,
    voice_file_id: int,
    description: str | None,
    diagnostic_type: str,
) -> DiagnosticModuleRead:
    backend_client = get_backend_client()
    payload = await backend_client.post_json(
        path=f"/diagnostic/{diagnostic_type}",
        json_payload=DiagnosticCreatePayload(
            user_id=user_id,
            voice_file_id=voice_file_id,
            description=description,
        ).model_dump(mode="json"),
    )
    return DiagnosticModuleRead.model_validate(cast(dict[str, object], payload))


async def create_diagnostic(
    *,
    bot: Bot,
    document: TelegramDiagnosticMedia,
    chat_id: int,
    description: str | None,
    diagnostic_type: str,
) -> DiagnosticCreationResult:
    """
    Создаёт backend-диагностику по Telegram document/audio/voice.

    Flow:
    1. ищет backend user по `chat_id`
    2. скачивает файл из Telegram
    3. создаёт backend file через `/files/`
    4. вызывает `/diagnostic/<type>`
    """

    telegram_file_id, filename, content_type = _extract_telegram_file_metadata(document)
    return await create_diagnostic_from_telegram_file(
        bot=bot,
        telegram_file_id=telegram_file_id,
        filename=filename,
        content_type=content_type,
        chat_id=chat_id,
        description=description,
        diagnostic_type=diagnostic_type,
    )


async def create_diagnostic_from_telegram_file(
    *,
    bot: Bot,
    telegram_file_id: str,
    filename: str,
    content_type: str,
    chat_id: int,
    description: str | None,
    diagnostic_type: str,
) -> DiagnosticCreationResult:
    """Создаёт backend-диагностику по сохранённым Telegram file-метаданным."""

    normalized_type = _normalize_diagnostic_type(diagnostic_type)

    try:
        telegram_user = await _find_backend_user(chat_id=chat_id)
        file_bytes, normalized_filename, normalized_content_type = (
            await _download_telegram_file_bytes(
                bot=bot,
                telegram_file_id=telegram_file_id,
                filename=filename,
                content_type=content_type,
            )
        )
        uploaded_file = await _create_backend_file(
            file_bytes=file_bytes,
            filename=normalized_filename,
            content_type=normalized_content_type,
        )
        diagnostic = await _create_backend_diagnostic(
            user_id=telegram_user.id,
            voice_file_id=uploaded_file.id,
            description=description,
            diagnostic_type=normalized_type,
        )
    except BackendClientError as exc:
        raise BaseDiagnosticModuleError(str(exc)) from exc

    return DiagnosticCreationResult(
        telegram_user=telegram_user,
        file=uploaded_file,
        diagnostic=diagnostic,
        diagnostic_type=normalized_type,
    )
