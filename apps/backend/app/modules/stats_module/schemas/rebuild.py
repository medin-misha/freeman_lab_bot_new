from datetime import datetime

from pydantic import BaseModel

from .user_bot_stats import UserBotStatsRead
from .user_diagnostic_stats import UserDiagnosticStatsRead


class UserStatsRebuildRead(BaseModel):
    rebuilt_at: datetime
    user_bot_stats: UserBotStatsRead
    diagnostic_stats: list[UserDiagnosticStatsRead]
