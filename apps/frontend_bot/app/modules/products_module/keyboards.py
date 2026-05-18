"""Reply-клавиатуры products-модуля."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

CONSULTATIONS_BUTTON_TEXT = "Консультации"
REGRESSIONS_BUTTON_TEXT = "Регрессии"
MENTORING_BUTTON_TEXT = "Наставничество"
LEAVE_REQUEST_BUTTON_TEXT = "Оставить заявку"
BACK_BUTTON_TEXT = "Назад"


def get_products_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает reply-клавиатуру меню услуг."""

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=CONSULTATIONS_BUTTON_TEXT)],
            [KeyboardButton(text=REGRESSIONS_BUTTON_TEXT)],
            [KeyboardButton(text=MENTORING_BUTTON_TEXT)],
            [KeyboardButton(text="Назад в меню")],
        ],
        resize_keyboard=True,
        persistent=True,
    )


def get_product_details_reply_keyboard() -> ReplyKeyboardMarkup:
    """Возвращает reply-клавиатуру конкретной услуги."""

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LEAVE_REQUEST_BUTTON_TEXT)],
            [KeyboardButton(text=BACK_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
        persistent=True,
    )

