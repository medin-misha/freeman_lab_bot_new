"""Reply-клавиатуры invisible diagnostic модуля."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .config import INVISIBLE_DIAGNOSTIC_BACK_BUTTON_TEXT


def get_invisible_diagnostic_reply_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает reply-клавиатуру сценария диагностики невидимости."""

    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=INVISIBLE_DIAGNOSTIC_BACK_BUTTON_TEXT)]],
        resize_keyboard=True,
        persistent=True,
    )
