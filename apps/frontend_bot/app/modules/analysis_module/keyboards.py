"""Inline-клавиатуры analysis-модуля."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

PUBLIC_ANALYSIS_CALLBACK = "analysis:public"
PRIVATE_ANALYSIS_CALLBACK = "analysis:private"
PUBLIC_ANALYSIS_FORM_DONE_CALLBACK = "analysis:public_form_done"
PRIVATE_ANALYSIS_FORM_DONE_CALLBACK = "analysis:private_form_done"
ANALYSIS_SCHEDULE_DONE_CALLBACK = "analysis:schedule_done"

PUBLIC_ANALYSIS_FORM_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSeQ0Ubtz3nNgXlxzOcIZ2azImdEwcJz-"
    "KBQ74nObMW-2FUzVQ/viewform"
)
PRIVATE_ANALYSIS_FORM_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSfrNR-BjZIZO-YFt4K60Nc01ZCRA9X9k"
    "gw2Kx7qU1bCBX4K3w/viewform"
)
PUBLIC_ANALYSIS_SCHEDULE_URL = (
    "https://docs.google.com/spreadsheets/d/1vJppYEgiGRyplpqPmBuXs2LL1rRRpoRQ4K7ej1ro60Q/"
    "edit?gid=0#gid=0"
)
PRIVATE_ANALYSIS_SCHEDULE_URL = (
    "https://docs.google.com/spreadsheets/d/1vJppYEgiGRyplpqPmBuXs2LL1rRRpoRQ4K7ej1ro60Q/"
    "edit?gid=1665367467#gid=1665367467"
)


def get_analysis_type_keyboard() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру выбора формата разбора."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Публичный разбор",
                    callback_data=PUBLIC_ANALYSIS_CALLBACK,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Приватный разбор",
                    callback_data=PRIVATE_ANALYSIS_CALLBACK,
                )
            ],
        ]
    )


def get_public_analysis_keyboard() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру публичного разбора."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть анкету",
                    url=PUBLIC_ANALYSIS_FORM_URL,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Форму заполнил(а)",
                    callback_data=PUBLIC_ANALYSIS_FORM_DONE_CALLBACK,
                )
            ],
        ]
    )


def get_private_analysis_keyboard() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру приватного разбора."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть анкету",
                    url=PRIVATE_ANALYSIS_FORM_URL,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Форму заполнил(а)",
                    callback_data=PRIVATE_ANALYSIS_FORM_DONE_CALLBACK,
                )
            ],
        ]
    )


def get_public_analysis_schedule_keyboard() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру шага записи в расписание для публичного разбора."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="открыть расписание",
                    url=PUBLIC_ANALYSIS_SCHEDULE_URL,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Я внес(ла) себя в расписание",
                    callback_data=ANALYSIS_SCHEDULE_DONE_CALLBACK,
                )
            ],
        ]
    )


def get_private_analysis_schedule_keyboard() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру шага записи в расписание для приватного разбора."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="открыть расписание",
                    url=PRIVATE_ANALYSIS_SCHEDULE_URL,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Я внес(ла) себя в расписание",
                    callback_data=ANALYSIS_SCHEDULE_DONE_CALLBACK,
                )
            ],
        ]
    )
