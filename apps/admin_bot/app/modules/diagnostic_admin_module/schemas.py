"""Схемы RMQ payload для уведомлений о диагностике."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DiagnosticAdminNotificationUser(BaseModel):
    telegram_id: int
    username: str | None = None
    full_name: str | None = None
    date_of_birth: datetime | None = None
    city: str | None = None


class DiagnosticAdminNotificationFile(BaseModel):
    id: int
    name: str
    link: str
    note: str | None = None


class DiagnosticAdminNotificationPayload(BaseModel):
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
    user: DiagnosticAdminNotificationUser
    voice_file: DiagnosticAdminNotificationFile | None = None
