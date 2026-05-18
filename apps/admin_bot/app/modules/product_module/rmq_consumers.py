"""RabbitMQ consumer уведомлений о новой продуктовой заявке."""

from __future__ import annotations

import html
import logging
import re

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pydantic import ValidationError

from app.core import settings
from app.modules.rmq_module import RMQMessage, register_consumer

from .runtime import get_notification_bot
from .schemas import ProductAdminNotificationPayload

logger = logging.getLogger(__name__)

ADMIN_PRODUCT_CREATED_EVENT = "admin.product.created"
ADMIN_PRODUCT_CREATED_QUEUE = "admin.product.created"


def _build_user_label(payload: ProductAdminNotificationPayload) -> str:
    if payload.user.full_name and payload.user.full_name.strip():
        return payload.user.full_name.strip()

    if payload.user.username:
        return f"@{payload.user.username.strip()}"
    return "Пользователь"


def _build_hashtag(product_code: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-zА-Яа-я_]", "_", product_code.strip())
    normalized = normalized.strip("_") or "product"
    return f"#{normalized}"


def _build_message_text(payload: ProductAdminNotificationPayload) -> str:
    user_label = html.escape(_build_user_label(payload))
    return "\n".join(
        [
            "Новая заявка на продукт",
            "",
            _build_hashtag(payload.product_code),
            f"ID: <code>{payload.id}</code>",
            f"Код продукта: <code>{html.escape(payload.product_code)}</code>",
            f"User: {user_label}",
            f"Пользователь: <code>{payload.user.telegram_id}</code>",
        ]
    )


def _build_keyboard(payload: ProductAdminNotificationPayload) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_build_user_label(payload),
                    url=f"tg://user?id={payload.user.telegram_id}",
                )
            ]
        ]
    )


async def _send_notification_to_chat(
    *,
    chat_id: int,
    payload: ProductAdminNotificationPayload,
) -> None:
    bot = get_notification_bot()
    await bot.send_message(
        chat_id=chat_id,
        text=_build_message_text(payload),
        reply_markup=_build_keyboard(payload),
    )


async def handle_product_created(message: RMQMessage) -> None:
    try:
        payload = ProductAdminNotificationPayload.model_validate(message.payload)
    except ValidationError as exc:
        logger.exception("Invalid product admin payload: %s", exc)
        raise

    admin_chat_ids = settings.admins_chat_ids
    if not admin_chat_ids:
        logger.warning("ADMINS_CHAT_IDS is empty; product notification skipped")
        return

    for chat_id in admin_chat_ids:
        try:
            await _send_notification_to_chat(chat_id=chat_id, payload=payload)
        except Exception:
            logger.exception(
                "Failed to deliver product notification to admin chat %s",
                chat_id,
            )


register_consumer(
    queue_name=ADMIN_PRODUCT_CREATED_QUEUE,
    exchange_name=settings.rabbitmq_default_exchange,
    routing_key=ADMIN_PRODUCT_CREATED_EVENT,
    handler=handle_product_created,
)
