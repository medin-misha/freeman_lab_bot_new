"""Хендлеры products-модуля."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.modules.menu_module.keyboards import SERVICES_BUTTON_TEXT
from app.modules.system.auth import login_required

from .keyboards import (
    BACK_BUTTON_TEXT,
    CONSULTATIONS_BUTTON_TEXT,
    LEAVE_REQUEST_BUTTON_TEXT,
    MENTORING_BUTTON_TEXT,
    REGRESSIONS_BUTTON_TEXT,
    get_product_details_reply_keyboard,
    get_products_menu_reply_keyboard,
)
from .messages import get_messages
from .service import (
    ProductRequestDefinition,
    ProductUserNotFoundError,
    ProductsModuleError,
    submit_product_request,
)

router = Router(name="products_module")
logger = logging.getLogger(__name__)
_MESSAGES = get_messages()

_CONSULTATION_REQUEST = ProductRequestDefinition(product_code="Counseling")
_REGRESSION_REQUEST = ProductRequestDefinition(product_code="Regression")
_MENTORING_REQUEST = ProductRequestDefinition(product_code="Mentoring")


class ProductStates(StatesGroup):
    """Изолированные FSM-состояния products-модуля."""

    choosing_product = State()
    viewing_consultation = State()
    viewing_regression = State()
    viewing_mentoring = State()


@router.message(F.text == SERVICES_BUTTON_TEXT)
@login_required
async def products_menu(message: Message, state: FSMContext) -> None:
    """Показывает меню услуг."""

    await state.set_state(ProductStates.choosing_product)
    await message.answer(
        _MESSAGES["products_menu"],
        reply_markup=get_products_menu_reply_keyboard(),
    )


@router.message(F.text == CONSULTATIONS_BUTTON_TEXT)
@login_required
async def consultation_details(message: Message, state: FSMContext) -> None:
    """Показывает описание консультаций."""

    await state.set_state(ProductStates.viewing_consultation)
    await message.answer(
        _MESSAGES["consultation_description"],
        reply_markup=get_product_details_reply_keyboard(),
    )


@router.message(F.text == REGRESSIONS_BUTTON_TEXT)
@login_required
async def regression_details(message: Message, state: FSMContext) -> None:
    """Показывает описание регрессий."""

    await state.set_state(ProductStates.viewing_regression)
    await message.answer(
        _MESSAGES["regression_description"],
        reply_markup=get_product_details_reply_keyboard(),
    )


@router.message(F.text == MENTORING_BUTTON_TEXT)
@login_required
async def mentoring_details(message: Message, state: FSMContext) -> None:
    """Показывает описание наставничества."""

    await state.set_state(ProductStates.viewing_mentoring)
    await message.answer(
        _MESSAGES["mentoring_description"],
        reply_markup=get_product_details_reply_keyboard(),
    )


@router.message(F.text == BACK_BUTTON_TEXT)
@login_required
async def back_to_products_menu(message: Message, state: FSMContext) -> None:
    """Возвращает пользователя в меню услуг."""

    await state.set_state(ProductStates.choosing_product)
    await message.answer(
        _MESSAGES["products_menu"],
        reply_markup=get_products_menu_reply_keyboard(),
    )


@router.message(F.text == LEAVE_REQUEST_BUTTON_TEXT)
@login_required
async def leave_product_request(message: Message, state: FSMContext) -> None:
    """Оформляет заявку по текущей выбранной услуге."""

    definition = await _get_request_definition(state)
    if definition is None:
        await message.answer(_MESSAGES["request_context_missing"])
        return

    if message.from_user is None:
        await message.answer(_MESSAGES["request_failed"])
        return

    try:
        await submit_product_request(
            telegram_user=message.from_user,
            definition=definition,
        )
    except ProductUserNotFoundError:
        await message.answer(
            _MESSAGES["backend_user_not_found"],
            reply_markup=get_product_details_reply_keyboard(),
        )
        return
    except ProductsModuleError:
        logger.exception(
            "Product request submission failed for telegram_id=%s product_code=%s",
            message.from_user.id,
            definition.product_code,
        )
        await message.answer(
            _MESSAGES["request_failed"],
            reply_markup=get_product_details_reply_keyboard(),
        )
        return

    await message.answer(
        _MESSAGES["request_success"],
        reply_markup=get_product_details_reply_keyboard(),
    )


async def _get_request_definition(
    state: FSMContext,
) -> ProductRequestDefinition | None:
    current_state = await state.get_state()

    if current_state == ProductStates.viewing_consultation.state:
        return _CONSULTATION_REQUEST
    if current_state == ProductStates.viewing_regression.state:
        return _REGRESSION_REQUEST
    if current_state == ProductStates.viewing_mentoring.state:
        return _MENTORING_REQUEST

    return None
