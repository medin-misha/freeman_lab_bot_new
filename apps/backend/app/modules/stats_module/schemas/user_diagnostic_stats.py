from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserDiagnosticStatsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    telegram_user_id: int
    diagnostic_code: str
    attempts_total: int
    completed_total: int
    last_started_at: datetime | None
    last_completed_at: datetime | None
    last_status: str | None


class UserDiagnosticStatsEventUpdate(BaseModel):
    diagnostic_code: str = Field(min_length=1, max_length=128)
    attempts_delta: int = 0
    completed_delta: int = 0
    started: bool = False
    completed: bool = False
    status: str | None = Field(default=None, max_length=32)
