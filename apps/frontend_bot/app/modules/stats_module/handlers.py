"""
Service-only stats module.

The module keeps Telegram handlers empty on purpose and exposes reusable
helpers for reporting frontend-driven user statistics to backend APIs.
"""

from aiogram import Router

router = Router(name="stats_module")
