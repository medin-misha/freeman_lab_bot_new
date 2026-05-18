"""Конфигурация invisible diagnostic модуля."""

from __future__ import annotations

from pathlib import Path

MODULE_DIR = Path(__file__).parent
FILES_DIR = MODULE_DIR / "files"
MESSAGES_PATH = MODULE_DIR / "messages.json"

INVISIBLE_DIAGNOSTIC_TRIGGER_TEXT = "Диагностика невидимости"
INVISIBLE_DIAGNOSTIC_BACK_BUTTON_TEXT = "Назад в меню"
INVISIBLE_DIAGNOSTIC_TYPE = "invisible"
INVISIBLE_DIAGNOSTIC_PREVIEW_FILE_PATH: Path = (
    FILES_DIR / "Инструкция_Диагностика_невидимости.pdf"
)
