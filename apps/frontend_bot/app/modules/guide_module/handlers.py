"""Хендлер guide-модуля: отправляет методичку (PDF) и обучающее видео."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.modules.guide_module.config import GUIDE_PDF_PATH, GUIDE_VIDEO_PATH
from app.modules.guide_module.messages import get_messages
from app.modules.menu_module.keyboards import GUIDE_BUTTON_TEXT
from app.modules.system.auth import login_required

router = Router(name="guide_module")
_MESSAGES = get_messages()

async def _do_send_guide(target: Message) -> None:
    """Отправляет PDF-методичку и видео-инструкцию."""

    await target.answer_document(
        document=FSInputFile(GUIDE_PDF_PATH),
        caption=_MESSAGES["guide_description"],
    )

    await target.answer_video(
        video=FSInputFile(GUIDE_VIDEO_PATH),
    )


@router.callback_query(F.data == "menu:guide")
@login_required
async def send_guide_callback(callback: CallbackQuery) -> None:
    """Отправляет методичку по нажатию inline-кнопки."""

    await callback.answer()
    await _do_send_guide(callback.message)


@router.message(F.text == GUIDE_BUTTON_TEXT)
@login_required
async def send_guide_message(message: Message) -> None:
    """Отправляет методичку по нажатию reply-кнопки."""

    await _do_send_guide(message)

