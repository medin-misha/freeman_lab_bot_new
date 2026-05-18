"""Загрузка текстовых шаблонов analysis-модуля."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.core.user_support import apply_developer_contact_to_keys


_DEVELOPER_CONTACT_KEYS = {
    "analysis_registration_failed",
    "analysis_auth_context_missing",
}


@lru_cache(maxsize=1)
def get_messages() -> dict[str, str]:
    """Читает и кеширует текстовые шаблоны модуля."""

    messages_path = Path(__file__).with_name("messages.json")
    messages = json.loads(messages_path.read_text(encoding="utf-8"))
    return apply_developer_contact_to_keys(messages, keys=_DEVELOPER_CONTACT_KEYS)
