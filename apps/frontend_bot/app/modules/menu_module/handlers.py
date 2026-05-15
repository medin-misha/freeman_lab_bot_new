"""
Пользовательские хендлеры onboarding и главного меню.

Этот файл владеет командой `/start`, экраном обязательной подписки и входом в
главное меню. Здесь не должно быть тяжёлой инфраструктурной логики: проверка
подписки вынесена в service-слой, а клавиатуры - в отдельный пакет.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.modules.menu_module.delivery import (
    send_diagnostic_menu,
    send_main_menu,
    send_subscription_prompt,
)
from app.modules.menu_module.keyboards import (
    BACK_TO_MENU_BUTTON_TEXT,
    DIAGNOSTICS_BUTTON_TEXT,
    WHY_DIAGNOSTIC_BUTTON_TEXT,
)
from app.modules.menu_module.messages import get_messages
from app.modules.menu_module.service import SubscriptionCheckError, is_user_subscribed

router = Router(name="menu_module")
_MESSAGES = get_messages()


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    """Показывает главное меню или сценарий обязательной подписки."""

    user = message.from_user
    if user is None:
        await message.answer(_MESSAGES["subscription_check_failed"])
        return

    try:
        if await is_user_subscribed(message.bot, user.id):
            await send_main_menu(message)
            return
    except (SubscriptionCheckError, ValueError):
        await message.answer(_MESSAGES["subscription_check_failed"])
        return

    await send_subscription_prompt(message)


@router.message(F.text == DIAGNOSTICS_BUTTON_TEXT)
async def diagnostic_menu(message: Message) -> None:
    """Показывает экран меню диагностики."""

    await send_diagnostic_menu(message)


@router.message(F.text == WHY_DIAGNOSTIC_BUTTON_TEXT)
async def explain_diagnostic_value(message: Message) -> None:
    """Повторно отправляет текст с объяснением пользы диагностики."""

    await message.answer(_MESSAGES["diagnostic_menu"])


@router.message(F.text == BACK_TO_MENU_BUTTON_TEXT)
async def back_to_main_menu(message: Message) -> None:
    """Возвращает пользователя в главное меню."""

    await send_main_menu(message)


@router.callback_query(lambda callback: callback.data == "menu:check_subscription")
async def check_subscription_callback(callback: CallbackQuery) -> None:
    """Повторно проверяет подписку после нажатия кнопки подтверждения."""

    user = callback.from_user
    if user is None:
        await callback.answer(_MESSAGES["subscription_check_failed"], show_alert=True)
        return

    try:
        if await is_user_subscribed(callback.bot, user.id):
            await callback.answer()
            await send_main_menu(callback)
            return
    except (SubscriptionCheckError, ValueError):
        await callback.answer(_MESSAGES["subscription_check_failed"], show_alert=True)
        return

    await callback.answer(_MESSAGES["subscription_still_missing"], show_alert=True)
