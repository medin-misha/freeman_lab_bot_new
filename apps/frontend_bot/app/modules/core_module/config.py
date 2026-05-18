"""
Модульная конфигурация core_module.

Этот модуль не читает `.env` напрямую и использует только централизованные
настройки приложения.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core import MainSettings, settings


class CoreModuleSettings(BaseModel):
    """Настройки, необходимые для открытия mini app Ядра."""

    core_url: str = Field(min_length=1)


def build_core_settings(main_settings: MainSettings = settings) -> CoreModuleSettings:
    """Строит конфиг модуля из общих настроек приложения."""

    return CoreModuleSettings(core_url=main_settings.core_url)


core_settings = build_core_settings()
