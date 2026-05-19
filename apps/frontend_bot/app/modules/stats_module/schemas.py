"""Локальные схемы frontend stats-модуля."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBotStatsRead(BaseModel):
    """Read-схема агрегированной статистики пользователя."""

    model_config = ConfigDict(extra="ignore")

    id: int
    telegram_user_id: int
    source: str | None = None
    current_branch: str | None = None
    channel_subscribe: bool
    received_methodology: bool
    received_methodology_at: datetime | None = None
    core_application_submitted: bool
    core_application_submitted_at: datetime | None = None
    diagnostics_total: int
    diagnostics_completed_total: int
    last_diagnostic_at: datetime | None = None
    review_link_clicked: bool
    review_public_consent_given: bool
    created_at: datetime
    updated_at: datetime


class UserBotStatsExternalUpdate(BaseModel):
    """Payload для bot-driven обновления user stats."""

    source: str | None = None
    current_branch: str | None = None
    channel_subscribe: bool | None = None
    received_methodology: bool | None = None
    review_link_clicked: bool | None = None
    review_public_consent_given: bool | None = None


class UserDiagnosticStatsRead(BaseModel):
    """Read-схема per-diagnostic статистики пользователя."""

    model_config = ConfigDict(extra="ignore")

    id: int
    telegram_user_id: int
    diagnostic_code: str
    attempts_total: int
    completed_total: int
    last_started_at: datetime | None = None
    last_completed_at: datetime | None = None
    last_status: str | None = None
    created_at: datetime
    updated_at: datetime


class UserDiagnosticStatsEventUpdate(BaseModel):
    """Payload события для per-diagnostic статистики."""

    diagnostic_code: str = Field(min_length=1, max_length=128)
    attempts_delta: int = 0
    completed_delta: int = 0
    started: bool = False
    completed: bool = False
    status: str | None = Field(default=None, max_length=32)
