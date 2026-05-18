from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CoreFormSubmit(BaseModel):
    telegram_id: str
    full_name: str
    birth_date: date
    city: str
    activity: str | None = None
    request: str | None = None
    priorities: list[str] | None = None
    motivation: str | None = None
    difficulties: str | None = None
    readiness: str | None = None
    weekly_time: str | None = None
    rules: str | None = None
    payment: str | None = None


class CoreRequestCreate(BaseModel):
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


class CoreRequestUpdate(BaseModel):
    activity: str | None = None
    request: str | None = None
    priorities: list[str] | None = None
    motivation: str | None = None
    difficulties: str | None = None
    readiness: str | None = None
    weekly_time: str | None = None
    rules: str | None = None
    payment: str | None = None
    user_id: int | None = None


class CoreRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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


class CoreRequestAdminNotificationUser(BaseModel):
    telegram_id: int
    username: str | None = None
    full_name: str | None = None
    date_of_birth: datetime | None = None
    city: str | None = None


class CoreRequestAdminNotificationPayload(BaseModel):
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
    user: CoreRequestAdminNotificationUser
