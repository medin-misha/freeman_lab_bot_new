"""Загрузка текстовых шаблонов default diagnostic модуля."""

from __future__ import annotations

import json
from functools import lru_cache

from .config import MESSAGES_PATH


@lru_cache(maxsize=1)
def get_messages() -> dict[str, str]:
    """Читает и кеширует текстовые шаблоны модуля."""

    return json.loads(MESSAGES_PATH.read_text(encoding="utf-8"))
