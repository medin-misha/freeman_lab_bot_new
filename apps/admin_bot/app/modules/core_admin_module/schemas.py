"""Схемы RMQ payload для уведомлений о заявках на ядро."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CoreAdminNotificationUser(BaseModel):
    telegram_id: int
    username: str | None = None
    full_name: str | None = None
    date_of_birth: datetime | None = None
    city: str | None = None


class CoreAdminNotificationPayload(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    activity: str | None = None
    request: str | None = None
    priorities: list[str] | None = None
    motivation: str | None = None
    difficulties: str | None = None
    readiness: str | None = None
    weekly_time: str | None = None
    rules: str | None = None
    payment: str | None = None
    user: CoreAdminNotificationUser
