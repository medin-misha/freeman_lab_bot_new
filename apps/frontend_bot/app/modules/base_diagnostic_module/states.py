"""
Shared FSM states for diagnostic Telegram modules.

Product diagnostic modules can inherit from this `StatesGroup` to reuse a
common vocabulary for file-first diagnostic flows while keeping their own
handlers and transition rules.
"""

from aiogram.fsm.state import State, StatesGroup


class BaseDiagnosticStates(StatesGroup):
    """Base states for diagnostics that upload a file and may ask for text."""

    waiting_for_file = State()
    waiting_for_text = State()
    sending_to_server = State()
