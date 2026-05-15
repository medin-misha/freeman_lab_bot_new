"""
Service-only base diagnostic module.

This module intentionally keeps Telegram handlers empty for now. Its purpose is
to provide reusable orchestration helpers that product diagnostic modules can
call to create backend diagnostics from Telegram documents.
"""

from aiogram import Router

router = Router(name="base_diagnostic_module")
