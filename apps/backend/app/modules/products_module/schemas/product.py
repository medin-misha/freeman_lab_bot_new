from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    product_code: str = Field(min_length=1, max_length=128)
    user_id: int


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    product_code: str
    user_id: int


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
