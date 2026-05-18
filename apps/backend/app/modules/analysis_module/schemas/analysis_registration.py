from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnalysisRegistrationCreate(BaseModel):
    user_id: int


class AnalysisRegistrationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int


class AnalysisRegistrationAdminNotificationUser(BaseModel):
    telegram_id: int
    username: str | None = None
    full_name: str | None = None
    date_of_birth: datetime | None = None
    city: str | None = None


class AnalysisRegistrationAdminNotificationPayload(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    user: AnalysisRegistrationAdminNotificationUser
