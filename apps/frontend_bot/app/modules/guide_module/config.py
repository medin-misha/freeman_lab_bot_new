"""Конфигурация guide-модуля: пути к файлам методички и видео."""

from __future__ import annotations

from pathlib import Path

_FILES_DIR = Path(__file__).parent / "files"

GUIDE_PDF_PATH: Path = _FILES_DIR / "Методичка_Потолок_Внутри.pdf"
GUIDE_VIDEO_PATH: Path = _FILES_DIR / "videos" / "guide.mp4"

MODULE_PREFIX = "guide"
