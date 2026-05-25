"""Хендлеры core-модуля."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from app.modules.menu_module.keyboards import CORE_BUTTON_TEXT
from app.modules.system.auth import login_required

from .config import MODULE_PREFIX
from .keyboards import get_core_keyboard
from .messages import get_messages

router = Router(name=MODULE_PREFIX)
_MESSAGES = get_messages()


@router.message(F.text == CORE_BUTTON_TEXT)
@login_required(branch=f"{MODULE_PREFIX}-miniapp")
async def show_core_entrypoint(message: Message) -> None:
    """Показывает описание Ядра и кнопку открытия mini app."""

    await message.answer(
        _MESSAGES["core_description"],
        reply_markup=get_core_keyboard(),
    )
