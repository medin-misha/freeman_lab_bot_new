"""Router модуля уведомлений о диагностике."""

from __future__ import annotations

import io
import logging
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, BinaryIO

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Document,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.core import settings

from .client import (
    DiagnosticAdminBackendClientError,
    get_diagnostic_admin_backend_client,
)
from .runtime import get_notification_bot
from .states import DiagnosticResultUploadState, DiagnosticTranscriptUploadState

router = Router(name="diagnostic-admin")
logger = logging.getLogger(__name__)

TRANSCRIPT_SUCCESS_MARK = "Вы отправили транскрибацию"


def _is_admin_chat(chat_id: int) -> bool:
    return chat_id in settings.admins_chat_ids


def _build_markup(
    *,
    diagnostic_run_id: int,
    transcript_sent: bool,
    result_sent: bool,
    user_telegram_id: int | None,
) -> InlineKeyboardMarkup | None:
    rows: list[list[InlineKeyboardButton]] = []
    action_row: list[InlineKeyboardButton] = []
    if not transcript_sent:
        action_row.append(
            InlineKeyboardButton(
                text="Прикрепить транскрибацию",
                callback_data=f"diagnostic:transcript:{diagnostic_run_id}",
            )
        )
    if not result_sent:
        action_row.append(
            InlineKeyboardButton(
                text="Отправить результат",
                callback_data=f"diagnostic:result:{diagnostic_run_id}",
            )
        )

    if action_row:
        rows.append(action_row)
    if user_telegram_id is not None:
        rows.append(
            [
                InlineKeyboardButton(
                    text="Открыть пользователя",
                    url=f"tg://user?id={user_telegram_id}",
                )
            ]
        )

    if not rows:
        return None
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _mark_transcription_sent(text: str | None) -> str:
    base_text = text or ""
    if TRANSCRIPT_SUCCESS_MARK in base_text:
        return base_text
    separator = "\n\n" if base_text else ""
    return f"{base_text}{separator}{TRANSCRIPT_SUCCESS_MARK}"


def _replace_status(text: str | None, status_value: str) -> str:
    base_text = text or ""
    status_line = f"Статус: <code>{status_value}</code>"
    if not base_text:
        return status_line
    if re.search(r"^Статус: <code>.*?</code>$", base_text, flags=re.MULTILINE):
        return re.sub(
            r"^Статус: <code>.*?</code>$",
            status_line,
            base_text,
            count=1,
            flags=re.MULTILINE,
        )
    return f"{base_text}\n{status_line}"


async def _edit_notification_message(
    *,
    chat_id: int,
    message_id: int,
    new_text: str,
    reply_markup: InlineKeyboardMarkup | None,
) -> None:
    bot = get_notification_bot()
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=new_text,
        reply_markup=reply_markup,
    )


@asynccontextmanager
async def _open_document(document: Document) -> AsyncIterator[tuple[BinaryIO, str, str]]:
    bot = get_notification_bot()
    telegram_file = await bot.get_file(document.file_id)
    file_path = getattr(telegram_file, "file_path", None)
    filename = document.file_name or f"document_{document.file_unique_id}"
    content_type = document.mime_type or "application/octet-stream"

    if isinstance(file_path, str):
        local_path = Path(file_path)
        if local_path.is_file():
            with local_path.open("rb") as file_obj:
                yield file_obj, filename, content_type
                return

    buffer = io.BytesIO()
    await bot.download(document, destination=buffer)
    buffer.seek(0)
    try:
        yield buffer, filename, content_type
    finally:
        buffer.close()


def _is_transcript_sent(text: str | None) -> bool:
    return TRANSCRIPT_SUCCESS_MARK in (text or "")


def _is_result_sent(text: str | None) -> bool:
    return "Статус: <code>completed</code>" in (text or "")


def _extract_user_telegram_id(message: Message, source_text: str) -> int | None:
    reply_markup = message.reply_markup
    if reply_markup is not None:
        for row in reply_markup.inline_keyboard:
            for button in row:
                url = getattr(button, "url", None)
                if isinstance(url, str) and url.startswith("tg://user?id="):
                    user_id = url.removeprefix("tg://user?id=")
                    if user_id.isdigit():
                        return int(user_id)

    match = re.search(r"Пользователь: <code>(\d+)</code>", source_text)
    if match:
        return int(match.group(1))
    return None


async def _start_document_upload_flow(
    *,
    callback: CallbackQuery,
    state: FSMContext,
    upload_state: object,
    prompt_text: str,
) -> None:
    if callback.from_user is None or callback.message is None:
        await callback.answer("Не удалось определить администратора.", show_alert=True)
        return

    if not _is_admin_chat(callback.message.chat.id):
        await callback.answer("Эта кнопка доступна только в admin chat.", show_alert=True)
        return

    diagnostic_run_id = int(callback.data.rsplit(":", 1)[-1])
    source_text = callback.message.text or callback.message.caption or ""
    user_telegram_id = _extract_user_telegram_id(callback.message, source_text)
    await state.set_state(upload_state)
    await state.update_data(
        diagnostic_run_id=diagnostic_run_id,
        expected_admin_id=callback.from_user.id,
        origin_chat_id=callback.message.chat.id,
        origin_message_id=callback.message.message_id,
        source_text=source_text,
        transcript_sent=_is_transcript_sent(source_text),
        result_sent=_is_result_sent(source_text),
        user_telegram_id=user_telegram_id,
    )
    await callback.answer()
    await callback.message.reply(prompt_text)


async def _upload_file_to_backend(
    *,
    message: Message,
    diagnostic_run_id: int,
    note: str,
) -> int:
    backend_client = get_diagnostic_admin_backend_client()
    async with _open_document(message.document) as (file_obj, filename, content_type):
        uploaded_file = await backend_client.upload_transcribation_file(
            filename=filename,
            content_type=content_type,
            file_obj=file_obj,
            note=note,
        )
    return uploaded_file.id


async def _ensure_expected_sender_and_chat(
    *,
    message: Message,
    state: FSMContext,
) -> dict:
    data = await state.get_data()
    expected_admin_id = data.get("expected_admin_id")
    origin_chat_id = data.get("origin_chat_id")

    if expected_admin_id != message.from_user.id:
        return {}

    if origin_chat_id != message.chat.id:
        await message.answer("Пришлите document в тот же chat, где нажали кнопку.")
        return {}

    return data


@router.callback_query(F.data.startswith("diagnostic:transcript:"))
async def start_transcript_upload(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await _start_document_upload_flow(
        callback=callback,
        state=state,
        upload_state=DiagnosticTranscriptUploadState.waiting_for_document,
        prompt_text=(
            "Ожидаю document-файл для транскрибации диагностики "
            f"<code>{int(callback.data.rsplit(':', 1)[-1])}</code>."
        ),
    )


@router.callback_query(F.data.startswith("diagnostic:result:"))
async def start_result_upload(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await _start_document_upload_flow(
        callback=callback,
        state=state,
        upload_state=DiagnosticResultUploadState.waiting_for_document,
        prompt_text=(
            "Ожидаю document-файл с результатом диагностики "
            f"<code>{int(callback.data.rsplit(':', 1)[-1])}</code>."
        ),
    )


@router.message(DiagnosticTranscriptUploadState.waiting_for_document, F.document)
async def upload_transcript_document(
    message: Message,
    state: FSMContext,
) -> None:
    if message.from_user is None or message.document is None:
        await message.answer("Не удалось прочитать document-файл.")
        return

    data = await _ensure_expected_sender_and_chat(message=message, state=state)
    if not data:
        return

    origin_chat_id = data.get("origin_chat_id")
    origin_message_id = data.get("origin_message_id")
    diagnostic_run_id = data.get("diagnostic_run_id")
    source_text = data.get("source_text", "")
    result_sent = bool(data.get("result_sent"))
    user_telegram_id = data.get("user_telegram_id")

    try:
        backend_client = get_diagnostic_admin_backend_client()
        uploaded_file_id = await _upload_file_to_backend(
            message=message,
            diagnostic_run_id=int(diagnostic_run_id),
            note=f"Transcribation for diagnostic run {diagnostic_run_id}",
        )
        await backend_client.attach_transcribation_file(
            diagnostic_run_id=int(diagnostic_run_id),
            file_id=uploaded_file_id,
        )
    except DiagnosticAdminBackendClientError:
        logger.exception(
            "Diagnostic admin backend flow failed for run %s",
            diagnostic_run_id,
        )
        await message.answer("Не удалось отправить транскрибацию в backend. Попробуйте ещё раз.")
        return
    except Exception:
        logger.exception(
            "Unexpected diagnostic transcription upload failure for run %s",
            diagnostic_run_id,
        )
        await message.answer("Не удалось обработать document. Попробуйте ещё раз.")
        return

    try:
        await _edit_notification_message(
            chat_id=int(origin_chat_id),
            message_id=int(origin_message_id),
            new_text=_mark_transcription_sent(source_text),
            reply_markup=_build_markup(
                diagnostic_run_id=int(diagnostic_run_id),
                transcript_sent=True,
                result_sent=result_sent,
                user_telegram_id=user_telegram_id,
            ),
        )
    except TelegramBadRequest:
        logger.exception(
            "Failed to update diagnostic notification message %s after transcript upload",
            origin_message_id,
        )

    await state.clear()
    await message.answer("Транскрибация успешно отправлена.")


@router.message(DiagnosticResultUploadState.waiting_for_document, F.document)
async def upload_result_document(
    message: Message,
    state: FSMContext,
) -> None:
    if message.from_user is None or message.document is None:
        await message.answer("Не удалось прочитать document-файл.")
        return

    data = await _ensure_expected_sender_and_chat(message=message, state=state)
    if not data:
        return

    origin_chat_id = data.get("origin_chat_id")
    origin_message_id = data.get("origin_message_id")
    diagnostic_run_id = data.get("diagnostic_run_id")
    source_text = data.get("source_text", "")
    transcript_sent = bool(data.get("transcript_sent"))
    user_telegram_id = data.get("user_telegram_id")

    try:
        backend_client = get_diagnostic_admin_backend_client()
        uploaded_file_id = await _upload_file_to_backend(
            message=message,
            diagnostic_run_id=int(diagnostic_run_id),
            note=f"Diagnostic result for run {diagnostic_run_id}",
        )
        await backend_client.complete_diagnostic_run(
            diagnostic_run_id=int(diagnostic_run_id),
            result_file_id=uploaded_file_id,
        )
    except DiagnosticAdminBackendClientError:
        logger.exception(
            "Diagnostic result backend flow failed for run %s",
            diagnostic_run_id,
        )
        await message.answer("Не удалось отправить результат в backend. Попробуйте ещё раз.")
        return
    except Exception:
        logger.exception(
            "Unexpected diagnostic result upload failure for run %s",
            diagnostic_run_id,
        )
        await message.answer("Не удалось обработать document. Попробуйте ещё раз.")
        return

    updated_text = _replace_status(source_text, "completed")

    try:
        await _edit_notification_message(
            chat_id=int(origin_chat_id),
            message_id=int(origin_message_id),
            new_text=updated_text,
            reply_markup=_build_markup(
                diagnostic_run_id=int(diagnostic_run_id),
                transcript_sent=transcript_sent,
                result_sent=True,
                user_telegram_id=user_telegram_id,
            ),
        )
    except TelegramBadRequest:
        logger.exception(
            "Failed to update diagnostic notification message %s after result upload",
            origin_message_id,
        )

    await state.clear()
    await message.answer("Результат диагностики успешно отправлен.")


@router.message(DiagnosticTranscriptUploadState.waiting_for_document)
async def reject_non_document_while_waiting(message: Message) -> None:
    await message.answer("Сейчас ожидаю именно document-файл с транскрибацией.")


@router.message(DiagnosticResultUploadState.waiting_for_document)
async def reject_non_document_result_while_waiting(message: Message) -> None:
    await message.answer("Сейчас ожидаю именно document-файл с результатом диагностики.")
