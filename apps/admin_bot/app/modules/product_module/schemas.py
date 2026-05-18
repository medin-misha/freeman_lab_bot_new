"""Схемы RMQ payload для уведомлений о продуктовых заявках."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProductAdminNotificationUser(BaseModel):
    telegram_id: int
    username: str | None = None
    full_name: str | None = None
    date_of_birth: datetime | None = None
    city: str | None = None


class ProductAdminNotificationPayload(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    product_code: str
    user_id: int
    user: ProductAdminNotificationUser
