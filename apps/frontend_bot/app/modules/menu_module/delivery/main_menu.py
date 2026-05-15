"""
Доставка главного меню и связанных медиа.

Здесь живёт отправка photo/video-контента и подготовка файлов для Telegram,
чтобы UI-доставка не перегружала `handlers.py`.
"""

from __future__ import annotations

import logging
from pathlib import Path

from aiogram.types import CallbackQuery, FSInputFile, Message

from app.modules.menu_module.config import menu_settings
from app.modules.menu_module.keyboards import (
    get_main_menu_keyboard,
    get_main_menu_reply_keyboard,
)
from app.modules.menu_module.messages import get_messages

logger = logging.getLogger(__name__)
_MESSAGES = get_messages()


async def send_main_menu(target: Message | CallbackQuery) -> None:
    """Отправляет главное меню с медиа для подписанного пользователя."""

    inline_kb, reply_kb, photo, video = _build_main_menu_assets()

    if isinstance(target, CallbackQuery):
        if target.message is None:
            await target.bot.send_photo(
                chat_id=target.from_user.id,
                photo=photo,
                caption=_MESSAGES["main_menu"],
                reply_markup=inline_kb,
            )
            await target.bot.send_video(
                chat_id=target.from_user.id,
                video=video,
                width=menu_settings.preview_video_width,
                height=menu_settings.preview_video_height,
                reply_markup=reply_kb,
            )
            return

        if target.message.reply_markup is not None:
            await target.message.edit_reply_markup(reply_markup=None)

        await target.message.answer_photo(
            photo=photo,
            caption=_MESSAGES["main_menu"],
            reply_markup=inline_kb,
        )
        await target.message.answer_video(
            video=video,
            width=menu_settings.preview_video_width,
            height=menu_settings.preview_video_height,
            reply_markup=reply_kb,
        )
        return

    await target.answer_photo(
        photo=photo,
        caption=_MESSAGES["main_menu"],
        reply_markup=inline_kb,
    )
    await target.answer_video(
        video=video,
        width=menu_settings.preview_video_width,
        height=menu_settings.preview_video_height,
        reply_markup=reply_kb,
    )
def _build_main_menu_assets() -> tuple[object, object, FSInputFile, FSInputFile]:
    inline_kb = get_main_menu_keyboard()
    reply_kb = get_main_menu_reply_keyboard()
    photo = _build_input_file(menu_settings.preview_photo_path)
    video = _build_input_file(_resolve_preview_video_path())
    return inline_kb, reply_kb, photo, video


def _resolve_preview_video_path() -> Path:
    """Возвращает путь к preview-video с поддержкой старого и нового размещения."""

    for candidate in menu_settings.preview_video_candidates:
        if candidate.exists():
            return candidate

    return menu_settings.preview_video_candidates[0]


def _build_input_file(path: Path) -> FSInputFile:
    """Создаёт Telegram input file и заранее пишет warning, если файла ещё нет."""

    if not path.exists():
        logger.warning("Menu media file does not exist yet: %s", path)

    return FSInputFile(path)
