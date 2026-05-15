"""Reply-клавиатуры default diagnostic модуля."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .config import DEFAULT_DIAGNOSTIC_BACK_BUTTON_TEXT


def get_default_diagnostic_reply_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает reply-клавиатуру сценария базовой диагностики."""

    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=DEFAULT_DIAGNOSTIC_BACK_BUTTON_TEXT)]],
        resize_keyboard=True,
        persistent=True,
    )
