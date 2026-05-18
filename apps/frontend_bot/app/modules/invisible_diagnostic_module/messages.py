"""Загрузка текстовых шаблонов invisible diagnostic модуля."""

from __future__ import annotations

import json
from functools import lru_cache

from app.core.user_support import apply_developer_contact_to_keys

from .config import MESSAGES_PATH


_DEVELOPER_CONTACT_KEYS = {
    "diagnostic_creation_failed",
}


@lru_cache(maxsize=1)
def get_messages() -> dict[str, str]:
    """Читает и кеширует текстовые шаблоны модуля."""

    messages = json.loads(MESSAGES_PATH.read_text(encoding="utf-8"))
    return apply_developer_contact_to_keys(messages, keys=_DEVELOPER_CONTACT_KEYS)
