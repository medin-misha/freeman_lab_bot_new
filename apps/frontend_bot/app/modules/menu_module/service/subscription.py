"""
Сервисные функции проверки подписки на обязательный канал.

Этот файл хранит нормализацию ссылки канала и повторно используемую проверку
через Telegram Bot API, чтобы и хендлеры, и декораторы использовали одну
логику без дублирования.
"""

from __future__ import annotations

import logging
from urllib.parse import urlparse

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError

from app.modules.menu_module.config import menu_settings

logger = logging.getLogger(__name__)

_ALLOWED_SUBSCRIPTION_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


class SubscriptionCheckError(RuntimeError):
    """Поднимается, когда бот не смог проверить подписку через Telegram API."""


def normalize_channel_reference(raw_channel: str) -> str:
    """Приводит значение `CHANNEL` к формату, пригодному для Bot API."""

    channel = raw_channel.strip()
    if not channel:
        raise ValueError("CHANNEL must not be empty.")

    if channel.startswith("https://") or channel.startswith("http://"):
        parsed = urlparse(channel)
        path = parsed.path.strip("/")
        if not path:
            raise ValueError("CHANNEL URL must contain a channel path.")
        if path.startswith("+") or path.startswith("joinchat/"):
            raise ValueError("CHANNEL must point to a public channel username, not an invite link.")
        return f"@{path.split('/', 1)[0]}"

    if channel.startswith("@") or channel.startswith("-100"):
        return channel

    if channel.lstrip("-").isdigit():
        return channel

    return f"@{channel.lstrip('@')}"


def build_channel_url(channel_reference: str) -> str:
    """Строит URL для кнопки подписки на основе значения `CHANNEL`."""

    channel = channel_reference.strip()
    if channel.startswith("https://") or channel.startswith("http://"):
        return channel

    if channel.startswith("@"):
        return f"https://t.me/{channel[1:]}"

    if channel.startswith("+"):
        return f"https://t.me/{channel}"

    if channel.startswith("-100") or channel.lstrip("-").isdigit():
        raise ValueError("Numeric CHANNEL values cannot be converted into a public Telegram URL.")

    return f"https://t.me/{channel.lstrip('@')}"


def get_required_channel() -> str:
    """Возвращает нормализованную ссылку на обязательный канал."""

    return normalize_channel_reference(menu_settings.channel)


def is_subscription_status_allowed(status: str | ChatMemberStatus) -> bool:
    """Определяет, считается ли Telegram member status активной подпиской."""

    normalized_status = (
        status
        if isinstance(status, ChatMemberStatus)
        else ChatMemberStatus(status)
    )
    return normalized_status in _ALLOWED_SUBSCRIPTION_STATUSES


async def is_user_subscribed(bot: Bot, user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на обязательный канал."""

    try:
        channel = get_required_channel()
    except ValueError as exc:
        raise SubscriptionCheckError("Invalid CHANNEL value.") from exc

    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
    except TelegramAPIError as exc:
        logger.exception("Telegram API failed while checking channel subscription.")
        raise SubscriptionCheckError("Telegram API failed during subscription check.") from exc

    return is_subscription_status_allowed(member.status)
