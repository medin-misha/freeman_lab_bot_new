"""
Загрузка текстовых шаблонов системного модуля.

Файл инкапсулирует чтение `messages.json`, чтобы хендлеры и декораторы
использовали единый источник текстов и не дублировали код чтения ресурсов.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.core.user_support import apply_developer_contact_to_keys


_DEVELOPER_CONTACT_KEYS = {
    "auth_missing_user",
    "auth_backend_not_configured",
    "auth_backend_unavailable",
    "auth_backend_unexpected_response",
    "auth_failed",
}


@lru_cache(maxsize=1)
def get_messages() -> dict[str, str]:
    """Читает и кеширует системные текстовые шаблоны."""

    messages_path = Path(__file__).with_name("messages.json")
    messages = json.loads(messages_path.read_text(encoding="utf-8"))
    return apply_developer_contact_to_keys(messages, keys=_DEVELOPER_CONTACT_KEYS)
