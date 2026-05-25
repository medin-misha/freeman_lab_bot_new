"""Модульная конфигурация admin_panel_module."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core import MainSettings, settings


class AdminPanelSettings(BaseModel):
    """Настройки, необходимые для админ-панели."""

    admin_url: str = Field(min_length=1)


def build_settings(main_settings: MainSettings = settings) -> AdminPanelSettings:
    """Строит конфиг модуля из общих настроек приложения."""

    return AdminPanelSettings(admin_url=main_settings.admin_url)


admin_panel_settings = build_settings()
