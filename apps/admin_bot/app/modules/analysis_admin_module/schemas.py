"""Схемы RMQ payload для уведомлений о записях на разбор."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AnalysisAdminNotificationUser(BaseModel):
    telegram_id: int
    username: str | None = None
    full_name: str | None = None
    date_of_birth: datetime | None = None
    city: str | None = None


class AnalysisAdminNotificationPayload(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    user: AnalysisAdminNotificationUser
