"""Конфигурация default diagnostic модуля."""

from __future__ import annotations

from pathlib import Path

MODULE_DIR = Path(__file__).parent
FILES_DIR = MODULE_DIR / "files"
MESSAGES_PATH = MODULE_DIR / "messages.json"

DEFAULT_DIAGNOSTIC_TRIGGER_TEXT = "Базовая диагностика"
DEFAULT_DIAGNOSTIC_BACK_BUTTON_TEXT = "Назад"
DEFAULT_DIAGNOSTIC_TYPE = "default"
DEFAULT_DIAGNOSTIC_PREVIEW_FILE_PATH: Path = (
    FILES_DIR / "Инструкция_Базовая_Диагнстика.pdf"
)
