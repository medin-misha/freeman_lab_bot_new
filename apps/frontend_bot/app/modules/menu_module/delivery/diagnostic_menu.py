"""Доставка меню диагностики и его медиа."""

from __future__ import annotations

import logging
from pathlib import Path

from aiogram.types import FSInputFile, Message

from app.modules.menu_module.config import menu_settings
from app.modules.menu_module.keyboards import get_diagnostic_menu_reply_keyboard
from app.modules.menu_module.messages import get_messages

logger = logging.getLogger(__name__)
_MESSAGES = get_messages()


async def send_diagnostic_menu(message: Message) -> None:
    """Отправляет текст и preview-видео меню диагностики."""

    await message.answer(_MESSAGES["diagnostic_menu"])
    await message.answer_video(
        video=_build_input_file(_resolve_diagnostic_video_path()),
        width=menu_settings.diagnostic_video_width,
        height=menu_settings.diagnostic_video_height,
        reply_markup=get_diagnostic_menu_reply_keyboard(),
    )


def _resolve_diagnostic_video_path() -> Path:
    """Возвращает путь к preview-видео меню диагностики."""

    for candidate in menu_settings.diagnostic_video_candidates:
        if candidate.exists():
            return candidate

    return menu_settings.diagnostic_video_candidates[0]


def _build_input_file(path: Path) -> FSInputFile:
    """Создаёт Telegram input file и заранее пишет warning, если файла ещё нет."""

    if not path.exists():
        logger.warning("Diagnostic preview video does not exist yet: %s", path)

    return FSInputFile(path)
