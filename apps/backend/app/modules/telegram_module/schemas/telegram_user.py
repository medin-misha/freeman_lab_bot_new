from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .user_profile import UserProfileRead
from app.modules.stats_module.schemas.user_bot_stats import UserBotStatsRead
from app.modules.base_diagnostic_module.schemas.diagnostic_run import DiagnosticRunRead
from app.modules.core_request_module.schemas.core_request import CoreRequestRead


class TelegramUserBase(BaseModel):
    telegram_id: int
    username: str | None = None
    last_seen_at: datetime | None = None
    is_blocket_bot: bool = False
    language_code: str | None = None


class TelegramUserCreate(TelegramUserBase):
    pass


class TelegramUserLogin(BaseModel):
    telegram_id: int


class TelegramUserPatch(BaseModel):
    telegram_id: int | None = None
    username: str | None = None
    last_seen_at: datetime | None = None
    is_blocket_bot: bool | None = None
    language_code: str | None = None


class TelegramUserRead(TelegramUserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    user_profile: UserProfileRead | None = None
    bot_stats: UserBotStatsRead | None = None
    diagnostic_runs: list[DiagnosticRunRead] = []
    core_request: CoreRequestRead | None = None

