"""Загрузка текстовых шаблонов guide-модуля."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def get_messages() -> dict[str, str]:
    """Читает и кеширует текстовые шаблоны guide-модуля."""

    messages_path = Path(__file__).parent / "messages.json"
    return json.loads(messages_path.read_text(encoding="utf-8"))
