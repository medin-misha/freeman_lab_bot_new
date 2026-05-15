"""
Хендлеры default diagnostic модуля.

Модуль отвечает за пользовательский сценарий базовой диагностики: отправляет
preview и PDF-инструкцию, принимает файл/аудио/voice, при необходимости
запрашивает текст и делегирует создание backend-диагностики в
`base_diagnostic_module`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message

from app.modules.base_diagnostic_module import create_diagnostic_from_telegram_file
from app.modules.menu_module.delivery import send_main_menu
from .config import (
    DEFAULT_DIAGNOSTIC_BACK_BUTTON_TEXT,
    DEFAULT_DIAGNOSTIC_PREVIEW_FILE_PATH,
    DEFAULT_DIAGNOSTIC_TRIGGER_TEXT,
    DEFAULT_DIAGNOSTIC_TYPE,
)
from .keyboards import get_default_diagnostic_reply_keyboard
from .messages import get_messages

router = Router(name="default_diagnostic_module")
_MESSAGES = get_messages()
logger = logging.getLogger(__name__)

_FSM_TELEGRAM_FILE_ID_KEY = "telegram_file_id"
_FSM_FILENAME_KEY = "filename"
_FSM_CONTENT_TYPE_KEY = "content_type"


class DefaultDiagnosticStates(StatesGroup):
    """Изолированные FSM-состояния сценария базовой диагностики."""

    waiting_for_file = State()
    waiting_for_text = State()
    sending_to_server = State()


@dataclass(slots=True)
class _TelegramFilePayload:
    telegram_file_id: str
    filename: str
    content_type: str


@router.message(F.text == DEFAULT_DIAGNOSTIC_TRIGGER_TEXT)
async def send_default_diagnostic_preview(
    message: Message,
    state: FSMContext,
) -> None:
    """Отправляет preview базовой диагностики и PDF-инструкцию."""

    await state.clear()
    await state.set_state(DefaultDiagnosticStates.waiting_for_file)
    await message.answer_document(
        document=FSInputFile(DEFAULT_DIAGNOSTIC_PREVIEW_FILE_PATH),
        caption=_MESSAGES["diagnostic_preview"],
        reply_markup=get_default_diagnostic_reply_keyboard(),
    )


@router.message(F.text == DEFAULT_DIAGNOSTIC_BACK_BUTTON_TEXT)
async def back_to_main_menu(message: Message, state: FSMContext) -> None:
    """Сбрасывает сценарий диагностики и возвращает пользователя в главное меню."""

    await state.clear()
    await send_main_menu(message)


@router.message(
    DefaultDiagnosticStates.waiting_for_file,
    F.document | F.audio | F.voice,
)
async def receive_default_diagnostic_media(
    message: Message,
    state: FSMContext,
) -> None:
    """Принимает медиа и либо сразу создаёт диагностику, либо запрашивает текст."""

    payload = _extract_supported_media(message)
    if payload is None:
        await message.answer(
            _MESSAGES["diagnostic_file_request"],
            reply_markup=get_default_diagnostic_reply_keyboard(),
        )
        return

    description = _normalize_text(message.caption)
    if description is not None:
        await _submit_default_diagnostic(
            message=message,
            state=state,
            payload=payload,
            description=description,
        )
        return

    await state.update_data(
        {
            _FSM_TELEGRAM_FILE_ID_KEY: payload.telegram_file_id,
            _FSM_FILENAME_KEY: payload.filename,
            _FSM_CONTENT_TYPE_KEY: payload.content_type,
        }
    )
    await state.set_state(DefaultDiagnosticStates.waiting_for_text)
    await message.answer(
        _MESSAGES["diagnostic_text_request"],
        reply_markup=get_default_diagnostic_reply_keyboard(),
    )


@router.message(DefaultDiagnosticStates.waiting_for_text, F.text)
async def receive_default_diagnostic_text(
    message: Message,
    state: FSMContext,
) -> None:
    """Получает текст после медиа без caption и создаёт диагностику."""

    description = _normalize_text(message.text)
    if description is None:
        await message.answer(
            _MESSAGES["diagnostic_text_request"],
            reply_markup=get_default_diagnostic_reply_keyboard(),
        )
        return

    data = await state.get_data()
    payload = _payload_from_state(data)
    if payload is None:
        await state.clear()
        await message.answer(
            _MESSAGES["diagnostic_file_request"],
            reply_markup=get_default_diagnostic_reply_keyboard(),
        )
        return

    await _submit_default_diagnostic(
        message=message,
        state=state,
        payload=payload,
        description=description,
    )


@router.message(DefaultDiagnosticStates.waiting_for_file)
async def default_diagnostic_waiting_for_file_fallback(message: Message) -> None:
    """Подсказывает, что в текущем шаге бот ждёт медиафайл."""

    await message.answer(
        _MESSAGES["diagnostic_file_request"],
        reply_markup=get_default_diagnostic_reply_keyboard(),
    )


@router.message(DefaultDiagnosticStates.waiting_for_text)
async def default_diagnostic_waiting_for_text_fallback(message: Message) -> None:
    """Подсказывает, что после медиа без caption нужен отдельный текст."""

    await message.answer(
        _MESSAGES["diagnostic_text_request"],
        reply_markup=get_default_diagnostic_reply_keyboard(),
    )


def _extract_supported_media(message: Message) -> _TelegramFilePayload | None:
    if message.document is not None:
        return _TelegramFilePayload(
            telegram_file_id=message.document.file_id,
            filename=message.document.file_name
            or f"document_{message.document.file_unique_id}",
            content_type=message.document.mime_type or "application/octet-stream",
        )

    if message.audio is not None:
        return _TelegramFilePayload(
            telegram_file_id=message.audio.file_id,
            filename=message.audio.file_name or f"audio_{message.audio.file_unique_id}",
            content_type=message.audio.mime_type or "audio/mpeg",
        )

    if message.voice is not None:
        return _TelegramFilePayload(
            telegram_file_id=message.voice.file_id,
            filename=f"voice_{message.voice.file_unique_id}.ogg",
            content_type=message.voice.mime_type or "audio/ogg",
        )

    return None


def _payload_from_state(data: dict[str, object]) -> _TelegramFilePayload | None:
    telegram_file_id = data.get(_FSM_TELEGRAM_FILE_ID_KEY)
    filename = data.get(_FSM_FILENAME_KEY)
    content_type = data.get(_FSM_CONTENT_TYPE_KEY)

    if not isinstance(telegram_file_id, str):
        return None
    if not isinstance(filename, str):
        return None
    if not isinstance(content_type, str):
        return None

    return _TelegramFilePayload(
        telegram_file_id=telegram_file_id,
        filename=filename,
        content_type=content_type,
    )


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    return normalized


async def _submit_default_diagnostic(
    *,
    message: Message,
    state: FSMContext,
    payload: _TelegramFilePayload,
    description: str,
) -> None:
    await state.set_state(DefaultDiagnosticStates.sending_to_server)

    try:
        await create_diagnostic_from_telegram_file(
            bot=message.bot,
            telegram_file_id=payload.telegram_file_id,
            filename=payload.filename,
            content_type=payload.content_type,
            chat_id=message.chat.id,
            description=description,
            diagnostic_type=DEFAULT_DIAGNOSTIC_TYPE,
        )
    except Exception:
        logger.exception(
            "Default diagnostic creation failed for chat_id=%s",
            message.chat.id,
        )
        await state.clear()
        await message.answer(
            _MESSAGES["diagnostic_creation_failed"],
            reply_markup=get_default_diagnostic_reply_keyboard(),
        )
        return

    await state.clear()
    await message.answer(
        _MESSAGES["diagnostic_created"],
        reply_markup=get_default_diagnostic_reply_keyboard(),
    )
