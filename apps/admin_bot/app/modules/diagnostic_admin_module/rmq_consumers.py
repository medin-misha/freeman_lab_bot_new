"""RabbitMQ consumer уведомлений о новой диагностике."""

from __future__ import annotations

import html
import logging
import re

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, URLInputFile
from pydantic import ValidationError

from app.core import settings
from app.modules.rmq_module import RMQMessage, register_consumer

from .client import get_diagnostic_admin_backend_client
from .runtime import get_notification_bot
from .schemas import DiagnosticAdminNotificationPayload

logger = logging.getLogger(__name__)

ADMIN_DIAGNOSTIC_CREATED_EVENT = "admin.diagnostic.created"
ADMIN_DIAGNOSTIC_CREATED_QUEUE = "admin.diagnostic.created"


def _build_user_label(payload: DiagnosticAdminNotificationPayload) -> str:
    if payload.user.username:
        return f"@{html.escape(payload.user.username)}"

    full_name = " ".join(
        part.strip()
        for part in [payload.user.first_name or "", payload.user.last_name or ""]
        if part and part.strip()
    )
    if full_name:
        return html.escape(full_name)
    return "без username"


def _build_hashtag(diagnostic_code: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-zА-Яа-я_]", "_", diagnostic_code.strip())
    normalized = normalized.strip("_") or "diagnostic"
    return f"#{normalized}"


def _build_message_text(payload: DiagnosticAdminNotificationPayload) -> str:
    lines = [
        "Новая диагностика",
        "",
        _build_hashtag(payload.diagnostic_code),
        f"ID: <code>{payload.id}</code>",
        f"Username: {_build_user_label(payload)}",
        f"Пользователь: <code>{payload.user.telegram_id}</code>",
        f"Статус: <code>{html.escape(payload.status)}</code>",
    ]

    if payload.description:
        lines.extend(["", "Описание:", html.escape(payload.description)])
    if payload.note:
        lines.extend(["", "Note:", html.escape(payload.note)])
    if payload.voice_file:
        lines.extend(["", f"Файл: <code>{html.escape(payload.voice_file.name)}</code>"])
    return "\n".join(lines)


def _build_keyboard(payload: DiagnosticAdminNotificationPayload) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Прикрепить транскрибацию",
                    callback_data=f"diagnostic:transcript:{payload.id}",
                ),
                InlineKeyboardButton(
                    text="Отправить результат",
                    callback_data=f"diagnostic:result:{payload.id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Открыть пользователя",
                    url=f"tg://user?id={payload.user.telegram_id}",
                )
            ],
        ]
    )


async def _send_notification_to_chat(
    *,
    chat_id: int,
    payload: DiagnosticAdminNotificationPayload,
) -> None:
    bot = get_notification_bot()
    text = _build_message_text(payload)
    reply_markup = _build_keyboard(payload)

    if payload.voice_file_id is not None:
        try:
            backend_client = get_diagnostic_admin_backend_client()
            await bot.send_document(
                chat_id=chat_id,
                document=URLInputFile(
                    backend_client.build_file_download_url(payload.voice_file_id),
                    filename=payload.voice_file.name if payload.voice_file else None,
                ),
            )
        except Exception:
            logger.exception("Failed to send diagnostic document to admin chat %s", chat_id)

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
    )


async def handle_diagnostic_created(message: RMQMessage) -> None:
    try:
        payload = DiagnosticAdminNotificationPayload.model_validate(message.payload)
    except ValidationError as exc:
        logger.exception("Invalid diagnostic admin payload: %s", exc)
        raise

    admin_chat_ids = settings.admins_chat_ids
    if not admin_chat_ids:
        logger.warning("ADMINS_CHAT_IDS is empty; diagnostic notification skipped")
        return

    for chat_id in admin_chat_ids:
        try:
            await _send_notification_to_chat(chat_id=chat_id, payload=payload)
        except Exception:
            logger.exception(
                "Failed to deliver diagnostic notification to admin chat %s",
                chat_id,
            )


register_consumer(
    queue_name=ADMIN_DIAGNOSTIC_CREATED_QUEUE,
    exchange_name=settings.rabbitmq_default_exchange,
    routing_key=ADMIN_DIAGNOSTIC_CREATED_EVENT,
    handler=handle_diagnostic_created,
)
