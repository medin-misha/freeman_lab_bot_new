import unittest
from types import SimpleNamespace
from unittest.mock import patch

from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError

from app.modules.menu_module.config import menu_settings
from app.modules.menu_module.service.subscription import (
    SubscriptionCheckError,
    build_channel_url,
    is_subscription_status_allowed,
    is_user_subscribed,
    normalize_channel_reference,
)


class SubscriptionHelpersTests(unittest.TestCase):
    def test_normalize_channel_reference_supports_username(self) -> None:
        self.assertEqual(normalize_channel_reference("@demo_channel"), "@demo_channel")
        self.assertEqual(normalize_channel_reference("demo_channel"), "@demo_channel")

    def test_normalize_channel_reference_supports_public_url(self) -> None:
        self.assertEqual(
            normalize_channel_reference("https://t.me/demo_channel"),
            "@demo_channel",
        )

    def test_normalize_channel_reference_rejects_invite_link(self) -> None:
        with self.assertRaises(ValueError):
            normalize_channel_reference("https://t.me/+secretinvite")

    def test_build_channel_url_from_username(self) -> None:
        self.assertEqual(build_channel_url("@demo_channel"), "https://t.me/demo_channel")

    def test_numeric_channel_cannot_build_public_url(self) -> None:
        with self.assertRaises(ValueError):
            build_channel_url("-1001234567890")

    def test_subscription_status_allowed(self) -> None:
        self.assertTrue(is_subscription_status_allowed(ChatMemberStatus.MEMBER))
        self.assertTrue(is_subscription_status_allowed(ChatMemberStatus.ADMINISTRATOR))
        self.assertFalse(is_subscription_status_allowed(ChatMemberStatus.LEFT))


class SubscriptionServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_is_user_subscribed_returns_true_for_member(self) -> None:
        bot = SimpleNamespace(
            get_chat_member=unittest.mock.AsyncMock(
                return_value=SimpleNamespace(status=ChatMemberStatus.MEMBER)
            )
        )

        with patch.object(menu_settings, "channel", "@demo_channel"):
            self.assertTrue(await is_user_subscribed(bot, user_id=1))

    async def test_is_user_subscribed_returns_false_for_left_user(self) -> None:
        bot = SimpleNamespace(
            get_chat_member=unittest.mock.AsyncMock(
                return_value=SimpleNamespace(status=ChatMemberStatus.LEFT)
            )
        )

        with patch.object(menu_settings, "channel", "@demo_channel"):
            self.assertFalse(await is_user_subscribed(bot, user_id=1))

    async def test_is_user_subscribed_wraps_telegram_errors(self) -> None:
        bot = SimpleNamespace(
            get_chat_member=unittest.mock.AsyncMock(
                side_effect=TelegramAPIError(method="getChatMember", message="boom")
            )
        )

        with patch.object(menu_settings, "channel", "@demo_channel"):
            with self.assertRaises(SubscriptionCheckError):
                await is_user_subscribed(bot, user_id=1)

    async def test_is_user_subscribed_wraps_invalid_channel(self) -> None:
        bot = SimpleNamespace(get_chat_member=unittest.mock.AsyncMock())

        with patch.object(menu_settings, "channel", "https://t.me/+secretinvite"):
            with self.assertRaises(SubscriptionCheckError):
                await is_user_subscribed(bot, user_id=1)
