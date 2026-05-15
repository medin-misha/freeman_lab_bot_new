"""
Локальные схемы универсального diagnostic orchestration-модуля.

Модуль не импортирует backend-код напрямую. Он хранит только минимальные
контракты, которые нужны для поиска пользователя, загрузки файла и создания
diagnostic extension-модуля.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.modules.system.schemas import TelegramUserRead


class FileRead(BaseModel):
    """Ответ backend после создания файла."""

    model_config = ConfigDict(extra="ignore")

    id: int
    link: str
    name: str
    note: str | None = None
    created_at: datetime
    updated_at: datetime


class DiagnosticRunRead(BaseModel):
    """Общая часть diagnostic run из backend."""

    model_config = ConfigDict(extra="ignore")

    id: int
    created_at: datetime
    updated_at: datetime
    voice_file_id: int | None = None
    result_file_id: int | None = None
    transcribation_file_id: int | None = None
    user_id: int
    diagnostic_code: str
    status: str
    completed_at: datetime | None = None
    note: str | None = None
    description: str | None = None
    tag: str | None = None


class DiagnosticModuleRead(BaseModel):
    """Универсальный ответ продуктового diagnostic-модуля."""

    model_config = ConfigDict(extra="allow")

    id: int
    created_at: datetime
    updated_at: datetime
    diagnostic_run_id: int
    diagnostic_run: DiagnosticRunRead


class DiagnosticCreationResult(BaseModel):
    """Единый результат orchestration-пайплайна."""

    model_config = ConfigDict(extra="ignore")

    telegram_user: TelegramUserRead
    file: FileRead
    diagnostic: DiagnosticModuleRead
    diagnostic_type: str


class DiagnosticCreatePayload(BaseModel):
    """Payload для product endpoint `POST /api/diagnostic/<type>`."""

    user_id: int
    voice_file_id: int
    description: str | None = None
