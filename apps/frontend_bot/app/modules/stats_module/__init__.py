"""Frontend stats integration module."""

from .handlers import router
from .schemas import (
    UserBotStatsExternalUpdate,
    UserBotStatsRead,
    UserDiagnosticStatsEventUpdate,
    UserDiagnosticStatsRead,
)
from .service import (
    FrontendStatsClient,
    StatsAuthContextError,
    StatsModuleError,
    get_stats_client,
    mark_current_user_channel_subscribed,
    mark_current_user_received_methodology,
    set_current_user_source,
)

__all__ = [
    "FrontendStatsClient",
    "StatsAuthContextError",
    "StatsModuleError",
    "UserBotStatsExternalUpdate",
    "UserBotStatsRead",
    "UserDiagnosticStatsEventUpdate",
    "UserDiagnosticStatsRead",
    "get_stats_client",
    "mark_current_user_channel_subscribed",
    "mark_current_user_received_methodology",
    "set_current_user_source",
    "router",
]
