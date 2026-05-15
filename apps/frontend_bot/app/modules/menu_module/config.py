"""
Модульная конфигурация onboarding/menu-слоя Telegram-бота.

Файл не читает `.env` напрямую. Вместо этого он строит явную проекцию поверх
общего `app.core.settings`, чтобы `menu_module` зависел только от
централизованной конфигурации приложения.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from app.core import MainSettings, settings

MODULE_DIR = Path(__file__).resolve().parent


class MenuModuleSettings(BaseModel):
    """Настройки, которые нужны menu-модулю."""

    channel: str = Field(min_length=1)
    preview_photo_path: Path
    preview_video_width: int = Field(default=1080, gt=0)
    preview_video_height: int = Field(default=1920, gt=0)
    preview_video_candidates: tuple[Path, ...]
    diagnostic_video_width: int = Field(default=1080, gt=0)
    diagnostic_video_height: int = Field(default=1920, gt=0)
    diagnostic_video_candidates: tuple[Path, ...]


def build_menu_settings(main_settings: MainSettings = settings) -> MenuModuleSettings:
    """Строит конфиг menu-модуля из общих настроек Telegram-приложения."""

    return MenuModuleSettings(
        channel=main_settings.channel,
        preview_photo_path=MODULE_DIR / "files" / "images" / "preview.jpg",
        preview_video_width=1080,
        preview_video_height=1920,
        preview_video_candidates=(
            MODULE_DIR / "files" / "images" / "preview.mp4",
            MODULE_DIR / "files" / "videos" / "preview.mp4",
        ),
        diagnostic_video_width=1080,
        diagnostic_video_height=1920,
        diagnostic_video_candidates=(
            MODULE_DIR / "files" / "video" / "diagnostic_preview.mp4",
            MODULE_DIR / "files" / "videos" / "diagnostic_preview.mp4",
            MODULE_DIR / "diagnostic_preview.mp4",
        ),
    )


menu_settings = build_menu_settings()
