"""
Загрузка текстовых шаблонов menu-модуля.

Файл инкапсулирует чтение `messages.json`, чтобы хендлеры, декораторы и
клавиатуры использовали единый источник пользовательских текстов.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.core.user_support import apply_developer_contact_to_keys


_DEVELOPER_CONTACT_KEYS = {
    "subscription_check_failed",
}


@lru_cache(maxsize=1)
def get_messages() -> dict[str, str]:
    """Читает и кеширует текстовые шаблоны menu-модуля."""

    messages_path = Path(__file__).with_name("messages.json")
    messages = json.loads(messages_path.read_text(encoding="utf-8"))
    return apply_developer_contact_to_keys(messages, keys=_DEVELOPER_CONTACT_KEYS)
