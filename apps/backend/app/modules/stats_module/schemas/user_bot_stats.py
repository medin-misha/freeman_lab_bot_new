from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBotStatsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    telegram_user_id: int
    source: str | None
    current_branch: str | None
    channel_subscribe: bool
    received_methodology: bool
    received_methodology_at: datetime | None
    core_application_submitted: bool
    core_application_submitted_at: datetime | None
    diagnostics_total: int
    diagnostics_completed_total: int
    last_diagnostic_at: datetime | None
    review_link_clicked: bool
    review_public_consent_given: bool


class UserBotStatsExternalUpdate(BaseModel):
    source: str | None = None
    current_branch: str | None = None
    channel_subscribe: bool | None = None
    received_methodology: bool | None = None
    review_link_clicked: bool | None = None
    review_public_consent_given: bool | None = None


class UserBotStatsInternalUpdate(BaseModel):
    core_application_submitted: bool | None = None
    diagnostics_total: int | None = None
    diagnostics_completed_total: int | None = None
    last_diagnostic_at: datetime | None = None
