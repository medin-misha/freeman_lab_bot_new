"""RMQ consumers for delivering completed diagnostics to Telegram users."""

from __future__ import annotations

import logging
from pathlib import Path

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import URLInputFile
from pydantic import BaseModel, ValidationError

from app.modules.menu_module.keyboards import get_main_menu_reply_keyboard
from app.modules.rmq_module.config import rmq_settings
from app.modules.rmq_module import RMQMessage, register_consumer
from app.modules.system.client import get_backend_client

from .runtime import get_delivery_bot, get_delivery_dispatcher

logger = logging.getLogger(__name__)

FRONTEND_DIAGNOSTIC_COMPLETED_EVENT = "frontend.diagnostic.completed"
FRONTEND_DIAGNOSTIC_COMPLETED_QUEUE = "frontend.diagnostic.completed"


class DiagnosticCompletedPayload(BaseModel):
    id: int
    user_id: int
    result_file_id: int
    result_file_name: str
    diagnostic_code: str


async def handle_diagnostic_completed(message: RMQMessage) -> None:
    try:
        payload = DiagnosticCompletedPayload.model_validate(message.payload)
    except ValidationError as exc:
        logger.exception("Invalid frontend diagnostic payload: %s", exc)
        raise

    backend_client = get_backend_client()
    user = await backend_client.get_telegram_user(payload.user_id)
    bot = get_delivery_bot()
    dispatcher = get_delivery_dispatcher()
    fsm_context = dispatcher.fsm.get_context(
        bot=bot,
        chat_id=user.telegram_id,
        user_id=user.telegram_id,
    )

    try:
        await fsm_context.clear()
        await bot.send_document(
            chat_id=user.telegram_id,
            document=URLInputFile(
                backend_client.build_file_download_url(payload.result_file_id),
                filename=_normalize_result_filename(payload.result_file_name),
            ),
            caption=(
                "Ваша диагностика готова! Вот результат\n"
                "После диагностики вы можете записаться на разбор"
            ),
            reply_markup=get_main_menu_reply_keyboard(),
        )
    except TelegramForbiddenError:
        logger.warning(
            "User %s blocked the bot; diagnostic result delivery skipped",
            user.telegram_id,
        )
    except TelegramBadRequest:
        logger.exception(
            "Telegram rejected diagnostic result delivery for chat_id=%s",
            user.telegram_id,
        )
        raise


def _normalize_result_filename(raw_name: str) -> str:
    normalized = raw_name.strip()
    if not normalized:
        return "Результат_Диагностики.pdf"

    suffix = Path(normalized).suffix.strip()
    if suffix:
        return normalized

    return f"{normalized}.pdf"


register_consumer(
    queue_name=FRONTEND_DIAGNOSTIC_COMPLETED_QUEUE,
    exchange_name=rmq_settings.rabbitmq_default_exchange,
    routing_key=FRONTEND_DIAGNOSTIC_COMPLETED_EVENT,
    handler=handle_diagnostic_completed,
)
