"""Process-wide runtime objects for base diagnostic delivery flows."""

from __future__ import annotations

from aiogram import Bot, Dispatcher


_delivery_bot: Bot | None = None
_delivery_dispatcher: Dispatcher | None = None


def set_delivery_bot(bot: Bot) -> None:
    """Registers the polling bot instance for RMQ-triggered deliveries."""

    global _delivery_bot
    _delivery_bot = bot


def set_delivery_dispatcher(dispatcher: Dispatcher) -> None:
    """Registers the dispatcher instance for FSM cleanup after deliveries."""

    global _delivery_dispatcher
    _delivery_dispatcher = dispatcher


def clear_delivery_bot() -> None:
    """Clears the registered bot instance during shutdown."""

    global _delivery_bot
    _delivery_bot = None
    clear_delivery_dispatcher()


def clear_delivery_dispatcher() -> None:
    """Clears the registered dispatcher instance during shutdown."""

    global _delivery_dispatcher
    _delivery_dispatcher = None


def get_delivery_bot() -> Bot:
    """Returns the polling bot instance used for out-of-band notifications."""

    if _delivery_bot is None:
        raise RuntimeError("Base diagnostic delivery bot is not initialized.")
    return _delivery_bot


def get_delivery_dispatcher() -> Dispatcher:
    """Returns the dispatcher instance used for FSM cleanup."""

    if _delivery_dispatcher is None:
        raise RuntimeError("Base diagnostic delivery dispatcher is not initialized.")
    return _delivery_dispatcher
