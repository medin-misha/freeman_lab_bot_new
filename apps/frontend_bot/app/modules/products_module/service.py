"""Сервисный слой products-модуля."""

from __future__ import annotations

from dataclasses import dataclass

from aiogram.types import User

from app.modules.system.client import (
    BackendClientError,
    BackendUnexpectedResponseError,
    get_backend_client,
)
from app.modules.system.schemas import TelegramUserCreatePayload, TelegramUserRead


class ProductsModuleError(RuntimeError):
    """Базовая ошибка products-модуля."""


class ProductUserNotFoundError(ProductsModuleError):
    """Backend не смог вернуть пользователя для оформления заявки."""


@dataclass(frozen=True, slots=True)
class ProductRequestDefinition:
    """Описание заявки, которую нужно отправить в backend."""

    product_code: str


async def submit_product_request(
    *,
    telegram_user: User,
    definition: ProductRequestDefinition,
) -> None:
    """Ищет backend user и создаёт заявку на продукт."""

    try:
        backend_user = await _find_backend_user_by_telegram_id(telegram_user.id)
        if backend_user is None:
            await _provision_backend_user(telegram_user)
            backend_user = await _find_backend_user_by_telegram_id(telegram_user.id)

        if backend_user is None:
            raise ProductUserNotFoundError(
                f"Telegram user {telegram_user.id} was not found after provisioning."
            )

        backend_client = get_backend_client()
        await backend_client.post_json(
            path="/products",
            json_payload={
                "product_code": definition.product_code,
                "user_id": backend_user.id,
            },
        )
    except ProductUserNotFoundError:
        raise
    except BackendClientError as exc:
        raise ProductsModuleError(str(exc)) from exc


async def _find_backend_user_by_telegram_id(telegram_id: int) -> TelegramUserRead | None:
    backend_client = get_backend_client()
    payload = await backend_client.get_json(
        path="/telegram/users",
        query_params={
            "search": str(telegram_id),
            "field": "telegram_id",
            "page": 1,
            "limit": 1,
        },
    )
    if not isinstance(payload, list):
        raise BackendUnexpectedResponseError(
            "Backend returned an invalid telegram user list payload."
        )

    for item in payload:
        user = TelegramUserRead.model_validate(item)
        if user.telegram_id == telegram_id:
            return user

    return None


async def _provision_backend_user(telegram_user: User) -> None:
    backend_client = get_backend_client()
    await backend_client.create_telegram_user(
        TelegramUserCreatePayload(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            is_blocket_bot=telegram_user.is_bot,
            language_code=telegram_user.language_code,
        )
    )
