"""Загрузка текстовых шаблонов products-модуля."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.core.user_support import apply_developer_contact_to_keys


_MESSAGES_PATH = Path(__file__).with_name("messages.json")
_DEVELOPER_CONTACT_KEYS = {
    "request_failed",
    "backend_user_not_found",
}


@lru_cache(maxsize=1)
def get_messages() -> dict[str, str]:
    """Читает и кеширует текстовые шаблоны модуля."""

    messages = json.loads(_MESSAGES_PATH.read_text(encoding="utf-8"))
    return apply_developer_contact_to_keys(messages, keys=_DEVELOPER_CONTACT_KEYS)
