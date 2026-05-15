from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DiagnosticRunCreate(BaseModel):
    user_id: int
    diagnostic_code: str = Field(min_length=1, max_length=128)
    description: str | None = None
    note: str | None = None
    tag: str | None = Field(default=None, max_length=255)


class DiagnosticRunStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=32)


class DiagnosticRunFileAttach(BaseModel):
    file_id: int


class DiagnosticRunComplete(BaseModel):
    result_file_id: int | None = None


class DiagnosticRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class DiagnosticRunAdminNotificationUser(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class DiagnosticRunAdminNotificationFile(BaseModel):
    id: int
    name: str
    link: str
    note: str | None = None


class DiagnosticRunAdminNotificationPayload(BaseModel):
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
    user: DiagnosticRunAdminNotificationUser
    voice_file: DiagnosticRunAdminNotificationFile | None = None


class DiagnosticRunFrontendNotificationPayload(BaseModel):
    id: int
    user_id: int
    result_file_id: int
    result_file_name: str
    diagnostic_code: str
    completed_at: datetime | None = None
