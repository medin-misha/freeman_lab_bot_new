"""
Загрузка текстовых шаблонов menu-модуля.

Файл инкапсулирует чтение `messages.json`, чтобы хендлеры, декораторы и
клавиатуры использовали единый источник пользовательских текстов.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def get_messages() -> dict[str, str]:
    """Читает и кеширует текстовые шаблоны menu-модуля."""

    messages_path = Path(__file__).with_name("messages.json")
    return json.loads(messages_path.read_text(encoding="utf-8"))

