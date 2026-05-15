"""Клавиатуры главного меню: inline и reply."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
GUIDE_BUTTON_TEXT = "Забрать методичку"
DIAGNOSTICS_BUTTON_TEXT = "Пройти диагностику"
BOOKING_BUTTON_TEXT = "Записаться на разбор"
CORE_BUTTON_TEXT = "Узнать про Ядро"
MORE_BUTTON_TEXT = "Ещё возможности"
WHY_DIAGNOSTIC_BUTTON_TEXT = "Зачем мне диагностика"
BASE_DIAGNOSTIC_BUTTON_TEXT = "Базовая диагностика"
INVISIBILITY_DIAGNOSTIC_BUTTON_TEXT = "Диагностика невидимости"
BACK_TO_MENU_BUTTON_TEXT = "Назад в меню"


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Возвращает inline-клавиатуру главного меню."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=GUIDE_BUTTON_TEXT, callback_data="menu:guide")],
        ]
    )


def get_main_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает постоянную reply-клавиатуру главного меню."""

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=GUIDE_BUTTON_TEXT)],
            [KeyboardButton(text=DIAGNOSTICS_BUTTON_TEXT)],
            [KeyboardButton(text=BOOKING_BUTTON_TEXT)],
            [KeyboardButton(text=CORE_BUTTON_TEXT)],
            [KeyboardButton(text=MORE_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
        persistent=True,
    )


def get_diagnostic_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает reply-клавиатуру меню диагностики."""

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=WHY_DIAGNOSTIC_BUTTON_TEXT)],
            [KeyboardButton(text=BASE_DIAGNOSTIC_BUTTON_TEXT)],
            [KeyboardButton(text=INVISIBILITY_DIAGNOSTIC_BUTTON_TEXT)],
            [KeyboardButton(text=BACK_TO_MENU_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
        persistent=True,
    )
