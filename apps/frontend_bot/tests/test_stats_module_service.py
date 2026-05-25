import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.modules.guide_module.handlers import _do_send_guide
from app.modules.stats_module import (
    FrontendStatsClient,
    StatsAuthContextError,
    StatsModuleError,
    UserDiagnosticStatsEventUpdate,
    mark_current_user_channel_subscribed,
    mark_current_user_received_methodology,
    set_current_user_source,
)
from app.modules.system.client import BackendUnavailableError


def _build_user_bot_stats_payload(user_id: int) -> dict[str, object]:
    return {
        "id": 10,
        "telegram_user_id": user_id,
        "source": None,
        "current_branch": None,
        "channel_subscribe": False,
        "received_methodology": True,
        "received_methodology_at": "2026-05-19T18:03:00Z",
        "core_application_submitted": False,
        "core_application_submitted_at": None,
        "diagnostics_total": 0,
        "diagnostics_completed_total": 0,
        "last_diagnostic_at": None,
        "review_link_clicked": False,
        "review_public_consent_given": False,
        "created_at": "2026-05-19T18:00:00Z",
        "updated_at": "2026-05-19T18:03:00Z",
    }


def _build_user_diagnostic_stats_payload(user_id: int) -> dict[str, object]:
    return {
        "id": 21,
        "telegram_user_id": user_id,
        "diagnostic_code": "default",
        "attempts_total": 1,
        "completed_total": 1,
        "last_started_at": "2026-05-19T18:04:00Z",
        "last_completed_at": "2026-05-19T18:05:00Z",
        "last_status": "completed",
        "created_at": "2026-05-19T18:00:00Z",
        "updated_at": "2026-05-19T18:05:00Z",
    }


class StatsModuleServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_mark_current_user_received_methodology_sends_patch(self) -> None:
        auth_session = SimpleNamespace(telegram_user=SimpleNamespace(id=42))
        backend_client = SimpleNamespace(
            patch_json=AsyncMock(return_value=_build_user_bot_stats_payload(user_id=42))
        )

        with patch(
            "app.modules.stats_module.service.get_current_auth_session",
            return_value=auth_session,
        ), patch(
            "app.modules.stats_module.service.get_backend_client",
            return_value=backend_client,
        ):
            stats = await mark_current_user_received_methodology()

        backend_client.patch_json.assert_awaited_once_with(
            path="/stats/user/external",
            query_params={"user_id": 42},
            json_payload={"received_methodology": True},
        )
        self.assertTrue(stats.received_methodology)

    async def test_get_stats_client_requires_auth_context(self) -> None:
        with patch(
            "app.modules.stats_module.service.get_current_auth_session",
            return_value=None,
        ):
            with self.assertRaises(StatsAuthContextError):
                await mark_current_user_received_methodology()

    async def test_apply_diagnostic_event_sends_patch(self) -> None:
        backend_client = SimpleNamespace(
            patch_json=AsyncMock(return_value=_build_user_diagnostic_stats_payload(user_id=42))
        )
        client = FrontendStatsClient(backend_client=backend_client, user_id=42)

        stats = await client.apply_diagnostic_event(
            UserDiagnosticStatsEventUpdate(
                diagnostic_code="default",
                attempts_delta=1,
                completed_delta=1,
                started=True,
                completed=True,
                status="completed",
            )
        )

        backend_client.patch_json.assert_awaited_once_with(
            path="/stats/diagnostic/event",
            query_params={"user_id": 42},
            json_payload={
                "diagnostic_code": "default",
                "attempts_delta": 1,
                "completed_delta": 1,
                "started": True,
                "completed": True,
                "status": "completed",
            },
        )
        self.assertEqual(stats.last_status, "completed")

    async def test_set_current_user_source_sends_patch(self) -> None:
        auth_session = SimpleNamespace(telegram_user=SimpleNamespace(id=42))
        payload = _build_user_bot_stats_payload(user_id=42)
        payload["source"] = "ads_campaign"
        backend_client = SimpleNamespace(
            patch_json=AsyncMock(return_value=payload)
        )

        with patch(
            "app.modules.stats_module.service.get_current_auth_session",
            return_value=auth_session,
        ), patch(
            "app.modules.stats_module.service.get_backend_client",
            return_value=backend_client,
        ):
            stats = await set_current_user_source("ads_campaign")

        backend_client.patch_json.assert_awaited_once_with(
            path="/stats/user/external",
            query_params={"user_id": 42},
            json_payload={"source": "ads_campaign"},
        )
        self.assertEqual(stats.source, "ads_campaign")

    async def test_mark_current_user_channel_subscribed_sends_patch(self) -> None:
        auth_session = SimpleNamespace(telegram_user=SimpleNamespace(id=42))
        payload = _build_user_bot_stats_payload(user_id=42)
        payload["channel_subscribe"] = True
        backend_client = SimpleNamespace(
            patch_json=AsyncMock(return_value=payload)
        )

        with patch(
            "app.modules.stats_module.service.get_current_auth_session",
            return_value=auth_session,
        ), patch(
            "app.modules.stats_module.service.get_backend_client",
            return_value=backend_client,
        ):
            stats = await mark_current_user_channel_subscribed()

        backend_client.patch_json.assert_awaited_once_with(
            path="/stats/user/external",
            query_params={"user_id": 42},
            json_payload={"channel_subscribe": True},
        )
        self.assertTrue(stats.channel_subscribe)

    async def test_backend_errors_are_wrapped(self) -> None:
        backend_client = SimpleNamespace(
            patch_json=AsyncMock(side_effect=BackendUnavailableError("boom"))
        )
        client = FrontendStatsClient(backend_client=backend_client, user_id=42)

        with self.assertRaises(StatsModuleError):
            await client.mark_methodology_received()


class GuideModuleStatsIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_guide_delivery_reports_stats(self) -> None:
        target = SimpleNamespace(
            answer_document=AsyncMock(),
            answer_video=AsyncMock(),
            chat=SimpleNamespace(id=777),
        )

        with patch(
            "app.modules.guide_module.handlers.FSInputFile",
            side_effect=lambda path: path,
        ), patch(
            "app.modules.guide_module.handlers.mark_current_user_received_methodology",
            new=AsyncMock(),
        ) as mark_stats:
            await _do_send_guide(target)

        target.answer_document.assert_awaited_once()
        mark_stats.assert_awaited_once()
        target.answer_video.assert_awaited_once()

    async def test_guide_delivery_suppresses_stats_errors(self) -> None:
        target = SimpleNamespace(
            answer_document=AsyncMock(),
            answer_video=AsyncMock(),
            chat=SimpleNamespace(id=777),
        )

        with patch(
            "app.modules.guide_module.handlers.FSInputFile",
            side_effect=lambda path: path,
        ), patch(
            "app.modules.guide_module.handlers.mark_current_user_received_methodology",
            new=AsyncMock(side_effect=StatsModuleError("boom")),
        ):
            await _do_send_guide(target)

        target.answer_document.assert_awaited_once()
        target.answer_video.assert_awaited_once()
