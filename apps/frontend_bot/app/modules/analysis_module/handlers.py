"""
Хендлеры analysis-модуля.

Модуль отвечает за пользовательский сценарий записи на разбор: принимает вход
по кнопке `Записаться на Разбор`, показывает выбор формата и отправляет
отдельные сообщения для публичного и приватного сценария с анкетами.
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.modules.menu_module.keyboards import BOOKING_BUTTON_TEXT
from app.modules.system.auth.decorators import login_required

from .keyboards import (
    ANALYSIS_SCHEDULE_DONE_CALLBACK,
    PRIVATE_ANALYSIS_CALLBACK,
    PRIVATE_ANALYSIS_FORM_DONE_CALLBACK,
    PUBLIC_ANALYSIS_CALLBACK,
    PUBLIC_ANALYSIS_FORM_DONE_CALLBACK,
    get_analysis_type_keyboard,
    get_private_analysis_keyboard,
    get_private_analysis_schedule_keyboard,
    get_public_analysis_keyboard,
    get_public_analysis_schedule_keyboard,
)
from .config import MODULE_PREFIX
from .messages import get_messages
from .service import AnalysisAuthContextError, AnalysisModuleError, submit_analysis_registration

router = Router(name=MODULE_PREFIX)
logger = logging.getLogger(__name__)
_MESSAGES = get_messages()


@router.message(F.text.lower() == BOOKING_BUTTON_TEXT)
@login_required(branch=f"{MODULE_PREFIX}-start")
async def analysis_entrypoint(message: Message) -> None:
    """Показывает вводный экран записи на разбор."""

    await message.answer(
        _MESSAGES["analysis_intro"],
        reply_markup=get_analysis_type_keyboard(),
    )


@router.callback_query(F.data == PUBLIC_ANALYSIS_CALLBACK)
@login_required(branch=f"{MODULE_PREFIX}-public")
async def public_analysis_selected(callback: CallbackQuery) -> None:
    """Отправляет следующий шаг для публичного разбора."""

    await callback.answer()
    if callback.message is None:
        return

    if callback.message.reply_markup is not None:
        await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        _MESSAGES["public_analysis_selected"],
        reply_markup=get_public_analysis_keyboard(),
    )


@router.callback_query(F.data == PRIVATE_ANALYSIS_CALLBACK)
@login_required(branch=f"{MODULE_PREFIX}-private")
async def private_analysis_selected(callback: CallbackQuery) -> None:
    """Отправляет следующий шаг для приватного разбора."""

    await callback.answer()
    if callback.message is None:
        return

    if callback.message.reply_markup is not None:
        await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        _MESSAGES["private_analysis_selected"],
        reply_markup=get_private_analysis_keyboard(),
    )


@router.callback_query(F.data == PUBLIC_ANALYSIS_FORM_DONE_CALLBACK)
@login_required(branch=f"{MODULE_PREFIX}-public-schedule")
async def public_analysis_form_done(callback: CallbackQuery) -> None:
    """Переводит пользователя к шагу записи в расписание публичного разбора."""

    await callback.answer()
    if callback.message is None:
        return

    if callback.message.reply_markup is not None:
        await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        _MESSAGES["analysis_schedule_selected"],
        reply_markup=get_public_analysis_schedule_keyboard(),
    )


@router.callback_query(F.data == PRIVATE_ANALYSIS_FORM_DONE_CALLBACK)
@login_required(branch=f"{MODULE_PREFIX}-private-schedule")
async def private_analysis_form_done(callback: CallbackQuery) -> None:
    """Переводит пользователя к шагу записи в расписание приватного разбора."""

    await callback.answer()
    if callback.message is None:
        return

    if callback.message.reply_markup is not None:
        await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        _MESSAGES["analysis_schedule_selected"],
        reply_markup=get_private_analysis_schedule_keyboard(),
    )


@router.callback_query(F.data == ANALYSIS_SCHEDULE_DONE_CALLBACK)
@login_required(branch=f"{MODULE_PREFIX}-done")
async def analysis_schedule_done(callback: CallbackQuery) -> None:
    """Создаёт запись на разбор после подтверждения шага с расписанием."""

    await callback.answer()
    if callback.message is None:
        return

    try:
        await submit_analysis_registration()
    except AnalysisAuthContextError:
        logger.exception("Analysis registration failed: auth context is missing.")
        await callback.message.answer(_MESSAGES["analysis_auth_context_missing"])
        return
    except AnalysisModuleError:
        telegram_user = callback.from_user
        logger.exception(
            "Analysis registration submission failed for telegram_id=%s",
            telegram_user.id if telegram_user is not None else None,
        )
        await callback.message.answer(_MESSAGES["analysis_registration_failed"])
        return

    if callback.message.reply_markup is not None:
        await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(_MESSAGES["analysis_registration_success"])
