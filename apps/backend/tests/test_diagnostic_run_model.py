import unittest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.modules.base_diagnostic_module.models import DiagnosticRun, DiagnosticRunStatus
from app.modules.base_diagnostic_module.schemas import DiagnosticRunCreate
from app.modules.base_diagnostic_module.services.diagnostic_run_service import create_run


class _FakeSession:
    def __init__(self) -> None:
        self.added = []
        self.flush_calls = 0
        self.commit_calls = 0
        self.refresh_calls = []

    def add(self, obj) -> None:
        self.added.append(obj)
        if getattr(obj, "id", None) is None:
            obj.id = len(self.added)
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.utcnow()
        if getattr(obj, "updated_at", None) is None:
            obj.updated_at = obj.created_at

    async def flush(self) -> None:
        self.flush_calls += 1

    async def commit(self) -> None:
        self.commit_calls += 1

    async def refresh(self, obj) -> None:
        self.refresh_calls.append(obj)


class DiagnosticRunServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_run_creates_related_diagnostic_stats(self) -> None:
        session = _FakeSession()

        with (
            patch(
                "app.modules.base_diagnostic_module.services.diagnostic_run_service._get_user_or_404",
                AsyncMock(),
            ),
            patch(
                "app.modules.base_diagnostic_module.services.diagnostic_run_service.UserDiagnosticStatsService.ensure_for_user_and_diagnostic",
                AsyncMock(),
            ) as ensure_stats,
            patch(
                "app.modules.base_diagnostic_module.services.diagnostic_run_service.UserBotStatsService.increment_diagnostics_created",
                AsyncMock(),
            ) as increment_stats,
            patch(
                "app.modules.base_diagnostic_module.services.diagnostic_run_service._publish_run_event",
                AsyncMock(),
            ),
            patch(
                "app.modules.base_diagnostic_module.services.diagnostic_run_service.publish_run_created_to_admin_bot",
                AsyncMock(),
            ),
        ):
            run = await create_run(
                DiagnosticRunCreate(
                    user_id=17,
                    diagnostic_code="default",
                    description="desc",
                    note="note",
                    tag="tag",
                ),
                session=session,
            )

        self.assertIsInstance(run, DiagnosticRun)
        self.assertEqual(run.user_id, 17)
        self.assertEqual(run.diagnostic_code, "default")
        self.assertEqual(run.status, DiagnosticRunStatus.CREATED)
        self.assertEqual(session.flush_calls, 1)
        self.assertEqual(session.commit_calls, 1)
        ensure_stats.assert_awaited_once_with(
            telegram_user_id=17,
            diagnostic_code="default",
            flush=False,
        )
        increment_stats.assert_awaited_once_with(
            telegram_user_id=17,
            at=run.created_at,
            flush=False,
        )


if __name__ == "__main__":
    unittest.main()
