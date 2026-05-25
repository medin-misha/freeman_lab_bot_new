import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError

from app.modules.menu_module.handlers import (
    _extract_start_source,
    check_subscription_callback,
    start_command,
)
from app.modules.menu_module.config import menu_settings
from app.modules.menu_module.service.subscription import (
    SubscriptionCheckError,
    build_channel_url,
    is_subscription_status_allowed,
    is_user_subscribed,
    normalize_channel_reference,
)
from app.modules.stats_module import StatsModuleError


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


class StartSourceHelpersTests(unittest.TestCase):
    def test_extract_start_source_returns_default_for_missing_payload(self) -> None:
        # Нет аргумента → дефолт "telegram"
        self.assertEqual(_extract_start_source(None), "telegram")
        self.assertEqual(_extract_start_source(SimpleNamespace(args=None)), "telegram")
        self.assertEqual(_extract_start_source(SimpleNamespace(args="   ")), "telegram")

    def test_extract_start_source_parses_source_prefix(self) -> None:
        # source-<value> → возвращает <value>
        self.assertEqual(_extract_start_source(SimpleNamespace(args="source-instagram")), "instagram")
        self.assertEqual(_extract_start_source(SimpleNamespace(args="source-youtube")), "youtube")

    def test_extract_start_source_trims_whitespace_around_source_value(self) -> None:
        self.assertEqual(_extract_start_source(SimpleNamespace(args="  source-youtube  ")), "youtube")

    def test_extract_start_source_returns_default_for_empty_source_prefix(self) -> None:
        # source- без значения после → дефолт "telegram"
        self.assertEqual(_extract_start_source(SimpleNamespace(args="source-")), "telegram")
        self.assertEqual(_extract_start_source(SimpleNamespace(args="source-  ")), "telegram")

    def test_extract_start_source_returns_none_for_unknown_payload(self) -> None:
        # payload без префикса source- → None (зарезервировано для других типов deep link)
        self.assertIsNone(_extract_start_source(SimpleNamespace(args="some_referral")))
        self.assertIsNone(_extract_start_source(SimpleNamespace(args="instagram")))


class StartCommandTests(unittest.IsolatedAsyncioTestCase):
    async def test_start_command_reports_source_prefix_and_preserves_existing_flow(self) -> None:
        message = SimpleNamespace(
            from_user=SimpleNamespace(id=1),
            bot=object(),
            chat=SimpleNamespace(id=100),
            answer=unittest.mock.AsyncMock(),
        )

        with patch(
            "app.modules.menu_module.handlers.set_current_user_source",
            new=unittest.mock.AsyncMock(),
        ) as set_source, patch(
            "app.modules.menu_module.handlers.is_user_subscribed",
            new=unittest.mock.AsyncMock(return_value=True),
        ), patch(
            "app.modules.menu_module.handlers.send_main_menu",
            new=unittest.mock.AsyncMock(),
        ) as send_main_menu:
            await start_command.__wrapped__(
                message,
                command=SimpleNamespace(args="source-ads_campaign"),
            )

        set_source.assert_awaited_once_with("ads_campaign")
        send_main_menu.assert_awaited_once_with(message)

    async def test_start_command_reports_default_source_when_no_payload(self) -> None:
        message = SimpleNamespace(
            from_user=SimpleNamespace(id=1),
            bot=object(),
            chat=SimpleNamespace(id=100),
            answer=unittest.mock.AsyncMock(),
        )

        with patch(
            "app.modules.menu_module.handlers.set_current_user_source",
            new=unittest.mock.AsyncMock(),
        ) as set_source, patch(
            "app.modules.menu_module.handlers.is_user_subscribed",
            new=unittest.mock.AsyncMock(return_value=True),
        ), patch(
            "app.modules.menu_module.handlers.send_main_menu",
            new=unittest.mock.AsyncMock(),
        ):
            await start_command.__wrapped__(message, command=None)

        set_source.assert_awaited_once_with("telegram")

    async def test_start_command_does_not_set_source_for_unknown_payload(self) -> None:
        message = SimpleNamespace(
            from_user=SimpleNamespace(id=1),
            bot=object(),
            chat=SimpleNamespace(id=100),
            answer=unittest.mock.AsyncMock(),
        )

        with patch(
            "app.modules.menu_module.handlers.set_current_user_source",
            new=unittest.mock.AsyncMock(),
        ) as set_source, patch(
            "app.modules.menu_module.handlers.is_user_subscribed",
            new=unittest.mock.AsyncMock(return_value=True),
        ), patch(
            "app.modules.menu_module.handlers.send_main_menu",
            new=unittest.mock.AsyncMock(),
        ):
            await start_command.__wrapped__(
                message,
                command=SimpleNamespace(args="unknown_referral"),
            )

        set_source.assert_not_awaited()

    async def test_start_command_reports_channel_subscription_for_subscribed_user(self) -> None:
        message = SimpleNamespace(
            from_user=SimpleNamespace(id=1),
            bot=object(),
            chat=SimpleNamespace(id=100),
            answer=AsyncMock(),
        )

        with patch(
            "app.modules.menu_module.handlers.mark_current_user_channel_subscribed",
            new=AsyncMock(),
        ) as mark_channel_subscribed, patch(
            "app.modules.menu_module.handlers.is_user_subscribed",
            new=AsyncMock(return_value=True),
        ), patch(
            "app.modules.menu_module.handlers.send_main_menu",
            new=AsyncMock(),
        ) as send_main_menu:
            await start_command.__wrapped__(message, command=None)

        mark_channel_subscribed.assert_awaited_once_with()
        send_main_menu.assert_awaited_once_with(message)

    async def test_start_command_suppresses_channel_subscription_stats_error(self) -> None:
        message = SimpleNamespace(
            from_user=SimpleNamespace(id=1),
            bot=object(),
            chat=SimpleNamespace(id=100),
            answer=AsyncMock(),
        )

        with patch(
            "app.modules.menu_module.handlers.mark_current_user_channel_subscribed",
            new=AsyncMock(side_effect=StatsModuleError("boom")),
        ), patch(
            "app.modules.menu_module.handlers.is_user_subscribed",
            new=AsyncMock(return_value=True),
        ), patch(
            "app.modules.menu_module.handlers.send_main_menu",
            new=AsyncMock(),
        ) as send_main_menu:
            await start_command.__wrapped__(message, command=None)

        send_main_menu.assert_awaited_once_with(message)

    async def test_start_command_suppresses_source_stats_error(self) -> None:
        message = SimpleNamespace(
            from_user=SimpleNamespace(id=1),
            bot=object(),
            chat=SimpleNamespace(id=100),
            answer=unittest.mock.AsyncMock(),
        )

        with patch(
            "app.modules.menu_module.handlers.set_current_user_source",
            new=unittest.mock.AsyncMock(side_effect=StatsModuleError("boom")),
        ), patch(
            "app.modules.menu_module.handlers.is_user_subscribed",
            new=unittest.mock.AsyncMock(return_value=False),
        ), patch(
            "app.modules.menu_module.handlers.send_subscription_prompt",
            new=unittest.mock.AsyncMock(),
        ) as send_subscription_prompt:
            await start_command.__wrapped__(
                message,
                command=SimpleNamespace(args="source-ads_campaign"),
            )

        send_subscription_prompt.assert_awaited_once_with(message)


class CheckSubscriptionCallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_callback_reports_channel_subscription_for_subscribed_user(self) -> None:
        callback = SimpleNamespace(
            from_user=SimpleNamespace(id=1),
            bot=object(),
            data="menu:check_subscription",
            message=SimpleNamespace(chat=SimpleNamespace(id=100)),
            answer=AsyncMock(),
        )

        with patch(
            "app.modules.menu_module.handlers.mark_current_user_channel_subscribed",
            new=AsyncMock(),
        ) as mark_channel_subscribed, patch(
            "app.modules.menu_module.handlers.is_user_subscribed",
            new=AsyncMock(return_value=True),
        ), patch(
            "app.modules.menu_module.handlers.send_main_menu",
            new=AsyncMock(),
        ) as send_main_menu:
            await check_subscription_callback.__wrapped__(callback)

        callback.answer.assert_awaited_once_with()
        mark_channel_subscribed.assert_awaited_once_with()
        send_main_menu.assert_awaited_once_with(callback)

    async def test_callback_suppresses_channel_subscription_stats_error(self) -> None:
        callback = SimpleNamespace(
            from_user=SimpleNamespace(id=1),
            bot=object(),
            data="menu:check_subscription",
            message=SimpleNamespace(chat=SimpleNamespace(id=100)),
            answer=AsyncMock(),
        )

        with patch(
            "app.modules.menu_module.handlers.mark_current_user_channel_subscribed",
            new=AsyncMock(side_effect=StatsModuleError("boom")),
        ), patch(
            "app.modules.menu_module.handlers.is_user_subscribed",
            new=AsyncMock(return_value=True),
        ), patch(
            "app.modules.menu_module.handlers.send_main_menu",
            new=AsyncMock(),
        ) as send_main_menu:
            await check_subscription_callback.__wrapped__(callback)

        callback.answer.assert_awaited_once_with()
        send_main_menu.assert_awaited_once_with(callback)
