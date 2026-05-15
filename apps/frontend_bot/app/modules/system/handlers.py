"""
Системные Telegram-хендлеры шаблона.

Этот файл содержит только обязательные команды platform-layer: introspection
для debug-сценариев и команды, связанные с базовой auth-системой, на которую
могут опираться остальные Telegram-модули.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core import settings
from app.core.context import get_current_auth_session
from app.modules.system.auth import get_cached_auth_session, login_required
from app.modules.system.auth.cache import auth_cache
from app.modules.system.config import system_settings
from app.modules.system.messages import get_messages

router = Router(name="system")
_MESSAGES = get_messages()


@router.message(Command("authstatus"))
@login_required(no_cache=True)
async def auth_status_command(message: Message) -> None:
    """Показывает текущую auth-сессию пользователя из in-memory cache."""

    auth_session = get_current_auth_session()
    if auth_session is None:
        await message.answer(_MESSAGES["auth_status_missing_context"])
        return

    telegram_user = auth_session.telegram_user
    username = f"@{telegram_user.username}" if telegram_user.username else "без username"
    profile_state = "есть" if telegram_user.user_profile else "нет"

    await message.answer(
        _MESSAGES["auth_status"].format(
            telegram_id=auth_session.telegram_id,
            backend_user_id=telegram_user.id,
            username=username,
            authenticated_at=auth_session.authenticated_at.isoformat(),
            cache_size=auth_cache.size(),
            profile_state=profile_state,
        )
    )


@router.message(Command("usersysinfo"))
async def user_system_info_command(message: Message) -> None:
    """Показывает техническую системную информацию, когда проект запущен в debug."""

    if not system_settings.debug_commands_enabled:
        await message.answer(_MESSAGES["user_sys_info_disabled"])
        return

    user = message.from_user
    if user is None:
        await message.answer(_MESSAGES["auth_missing_user"])
        return

    username = f"@{user.username}" if user.username else "без username"
    cached_session = get_cached_auth_session(user.id)
    cache_state = "authenticated" if cached_session else "not authenticated"

    await message.answer(
        _MESSAGES["user_sys_info"].format(
            username=username,
            user_id=user.id,
            chat_id=message.chat.id,
            first_name=user.first_name or "—",
            last_name=user.last_name or "—",
            language_code=user.language_code or "—",
            cache_state=cache_state,
            backend_url=settings.backend_url or "—",
        )
    )
