"""RabbitMQ consumer уведомлений о новой заявке на ядро."""

from __future__ import annotations

import html
import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pydantic import ValidationError

from app.core import settings
from app.modules.rmq_module import RMQMessage, register_consumer

from .runtime import get_notification_bot
from .schemas import CoreAdminNotificationPayload

logger = logging.getLogger(__name__)

ADMIN_CORE_REQUEST_CREATED_EVENT = "admin.core_request.created"
ADMIN_CORE_REQUEST_CREATED_QUEUE = "admin.core_request.created"


def _build_user_label(payload: CoreAdminNotificationPayload) -> str:
    if payload.user.full_name and payload.user.full_name.strip():
        return payload.user.full_name.strip()

    if payload.user.username:
        return f"@{payload.user.username.strip()}"
    return "Пользователь"


def _build_message_text(payload: CoreAdminNotificationPayload) -> str:
    user_label = html.escape(_build_user_label(payload))
    priorities = ", ".join(payload.priorities) if payload.priorities else "-"
    return "\n".join(
        [
            "Новая заявка на ядро",
            "",
            f"ID: <code>{payload.id}</code>",
            f"Создано: <code>{payload.created_at.isoformat()}</code>",
            f"User: {user_label}",
            f"Пользователь: <code>{payload.user.telegram_id}</code>",
            f"Активность: {html.escape(payload.activity or '-')}",
            f"Запрос: {html.escape(payload.request or '-')}",
            f"Приоритеты: {html.escape(priorities)}",
        ]
    )


def _build_keyboard(payload: CoreAdminNotificationPayload) -> InlineKeyboardMarkup:
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
    payload: CoreAdminNotificationPayload,
) -> None:
    bot = get_notification_bot()
    await bot.send_message(
        chat_id=chat_id,
        text=_build_message_text(payload),
        reply_markup=_build_keyboard(payload),
    )


async def handle_core_request_created(message: RMQMessage) -> None:
    try:
        payload = CoreAdminNotificationPayload.model_validate(message.payload)
    except ValidationError as exc:
        logger.exception("Invalid core admin payload: %s", exc)
        raise

    admin_chat_ids = settings.admins_chat_ids
    if not admin_chat_ids:
        logger.warning("ADMINS_CHAT_IDS is empty; core notification skipped")
        return

    for chat_id in admin_chat_ids:
        try:
            await _send_notification_to_chat(chat_id=chat_id, payload=payload)
        except Exception:
            logger.exception(
                "Failed to deliver core notification to admin chat %s",
                chat_id,
            )


register_consumer(
    queue_name=ADMIN_CORE_REQUEST_CREATED_QUEUE,
    exchange_name=settings.rabbitmq_default_exchange,
    routing_key=ADMIN_CORE_REQUEST_CREATED_EVENT,
    handler=handle_core_request_created,
)
