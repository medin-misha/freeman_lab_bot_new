"""Клавиатуры главного меню: inline и reply."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
GUIDE_BUTTON_TEXT = "Забрать методичку"
DIAGNOSTICS_BUTTON_TEXT = "Пройти диагностику"
BOOKING_BUTTON_TEXT = "записаться на разбор"
CORE_BUTTON_TEXT = "Узнать про Ядро"
MORE_BUTTON_TEXT = "Ещё возможности"
SERVICES_BUTTON_TEXT = "Посмотреть услуги"
SOCIALS_BUTTON_TEXT = "Соцсети"
WHY_DIAGNOSTIC_BUTTON_TEXT = "Зачем мне диагностика"
BASE_DIAGNOSTIC_BUTTON_TEXT = "Базовая диагностика"
INVISIBILITY_DIAGNOSTIC_BUTTON_TEXT = "Диагностика невидимости"
BACK_TO_MENU_BUTTON_TEXT = "Назад в меню"
YOUTUBE_URL = "https://www.youtube.com/@Freemanlifelab"
RUTUBE_URL = "https://rutube.ru/channel/69126193/"
TELEGRAM_URL = "https://t.me/alexfreemanlifelab"
SITE_URL = "https://freemanalexander.ru/"
VK_URL = "https://vk.com/freemanlifelab"
INSTAGRAM_URL = "https://instagram.com/freemanlifelab"


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


def get_more_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает reply-клавиатуру экрана дополнительных возможностей."""

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SERVICES_BUTTON_TEXT)],
            [KeyboardButton(text=SOCIALS_BUTTON_TEXT)],
            [KeyboardButton(text=BACK_TO_MENU_BUTTON_TEXT)]
        ],
        resize_keyboard=True,
        persistent=True,
    )


def get_socials_keyboard() -> InlineKeyboardMarkup:
    """Возвращает inline-клавиатуру со ссылками на соцсети проекта."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="YouTube", url=YOUTUBE_URL),
                InlineKeyboardButton(text="RuTube", url=RUTUBE_URL),
            ],
            [
                InlineKeyboardButton(text="Telegram", url=TELEGRAM_URL),
                InlineKeyboardButton(text="Сайт", url=SITE_URL),
            ],
            [
                InlineKeyboardButton(text="VK", url=VK_URL),
                InlineKeyboardButton(text="Instagram", url=INSTAGRAM_URL),
            ],
        ]
    )
