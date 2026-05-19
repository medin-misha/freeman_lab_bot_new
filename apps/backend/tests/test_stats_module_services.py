from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

from fastapi import HTTPException

from app.modules.stats_module.models import UserBotStats, UserDiagnosticStats
from app.modules.stats_module.schemas import UserBotStatsExternalUpdate, UserBotStatsInternalUpdate
from app.modules.stats_module.schemas.user_diagnostic_stats import UserDiagnosticStatsEventUpdate
from app.modules.stats_module.services import UserBotStatsService, UserDiagnosticStatsService


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def first(self):
        return self._rows[0] if self._rows else None

    def all(self):
        return list(self._rows)


class _FakeSession:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.flush_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0
        self.get_map = {}
        self.execute_results = []

    def add(self, obj):
        self.added.append(obj)

    def add_all(self, objs):
        self.added.extend(objs)

    async def delete(self, obj):
        self.deleted.append(obj)

    async def flush(self):
        self.flush_calls += 1

    async def commit(self):
        self.commit_calls += 1

    async def rollback(self):
        self.rollback_calls += 1

    async def get(self, model, key):
        return self.get_map.get((model, key))

    async def execute(self, _stmt):
        if not self.execute_results:
            return _FakeResult([])
        return self.execute_results.pop(0)


def _build_user_bot_stats(telegram_user_id: int) -> UserBotStats:
    return UserBotStats(
        telegram_user_id=telegram_user_id,
        source=None,
        current_branch=None,
        channel_subscribe=False,
        received_methodology=False,
        received_methodology_at=None,
        core_application_submitted=False,
        core_application_submitted_at=None,
        diagnostics_total=0,
        diagnostics_completed_total=0,
        last_diagnostic_at=None,
        review_link_clicked=False,
        review_public_consent_given=False,
    )


def _build_user_diagnostic_stats(telegram_user_id: int, diagnostic_code: str) -> UserDiagnosticStats:
    return UserDiagnosticStats(
        telegram_user_id=telegram_user_id,
        diagnostic_code=diagnostic_code,
        attempts_total=0,
        completed_total=0,
        last_started_at=None,
        last_completed_at=None,
        last_status=None,
    )


class UserBotStatsServiceTests(unittest.IsolatedAsyncioTestCase):
    def test_build_user_bot_stats_insert_values_uses_default_stats_values(self) -> None:
        from app.modules.stats_module.services.user_bot_stats_service import (
            _build_user_bot_stats_insert_values,
        )

        values = _build_user_bot_stats_insert_values(telegram_user_id=17)

        self.assertEqual(values["telegram_user_id"], 17)
        self.assertIsNone(values["source"])
        self.assertIsNone(values["current_branch"])
        self.assertFalse(values["channel_subscribe"])
        self.assertFalse(values["received_methodology"])
        self.assertIsNone(values["received_methodology_at"])
        self.assertFalse(values["core_application_submitted"])
        self.assertIsNone(values["core_application_submitted_at"])
        self.assertEqual(values["diagnostics_total"], 0)
        self.assertEqual(values["diagnostics_completed_total"], 0)
        self.assertIsNone(values["last_diagnostic_at"])
        self.assertFalse(values["review_link_clicked"])
        self.assertFalse(values["review_public_consent_given"])
        self.assertEqual(values["created_at"], values["updated_at"])

    async def test_create_for_telegram_user_adds_default_stats_row(self) -> None:
        session = _FakeSession()
        service = UserBotStatsService(session)

        created = await service.create_for_telegram_user(telegram_user_id=17)

        self.assertIs(session.added[0], created)
        self.assertEqual(created.telegram_user_id, 17)
        self.assertFalse(created.channel_subscribe)
        self.assertFalse(created.received_methodology)
        self.assertFalse(created.core_application_submitted)
        self.assertEqual(created.diagnostics_total, 0)
        self.assertEqual(created.diagnostics_completed_total, 0)
        self.assertFalse(created.review_link_clicked)
        self.assertFalse(created.review_public_consent_given)
        self.assertEqual(session.flush_calls, 1)
        self.assertEqual(session.commit_calls, 1)

    async def test_bulk_create_for_telegram_users_adds_only_missing_rows(self) -> None:
        session = _FakeSession()
        service = UserBotStatsService(session)
        existing = _build_user_bot_stats(telegram_user_id=5)
        session.execute_results = [_FakeResult([existing])]

        created = await service.bulk_create_for_telegram_users(
            telegram_user_ids=[5, 6, 6],
        )

        self.assertEqual([row.telegram_user_id for row in created], [5, 6])
        self.assertEqual(len(session.added), 1)
        self.assertEqual(session.added[0].telegram_user_id, 6)
        self.assertEqual(session.flush_calls, 1)
        self.assertEqual(session.commit_calls, 1)

    async def test_apply_external_update_supports_user_id_and_chat_id(self) -> None:
        session = _FakeSession()
        service = UserBotStatsService(session)
        stats = _build_user_bot_stats(telegram_user_id=7)

        service.get_or_create_for_user = AsyncMock(return_value=stats)
        service._flush_and_commit = AsyncMock()

        await service.apply_external_update(
            UserBotStatsExternalUpdate(source="ads"),
            user_id=7,
        )
        await service.apply_external_update(
            UserBotStatsExternalUpdate(current_branch="flow-a"),
            chat_id=100007,
        )

        self.assertEqual(stats.source, "ads")
        self.assertEqual(stats.current_branch, "flow-a")
        self.assertEqual(service.get_or_create_for_user.await_count, 2)
        first_call = service.get_or_create_for_user.await_args_list[0].kwargs
        second_call = service.get_or_create_for_user.await_args_list[1].kwargs
        self.assertEqual(first_call, {"user_id": 7, "chat_id": None})
        self.assertEqual(second_call, {"user_id": None, "chat_id": 100007})

    async def test_apply_external_update_explicit_false_resets_flags(self) -> None:
        session = _FakeSession()
        service = UserBotStatsService(session)
        stats = _build_user_bot_stats(telegram_user_id=5)
        stats.set_channel_subscribe(True)
        stats.mark_received_methodology(
            received=True,
            at=datetime.now(timezone.utc),
        )
        stats.mark_review_link_clicked(True)
        stats.mark_review_public_consent_given(True)

        service.get_or_create_for_user = AsyncMock(return_value=stats)
        service._flush_and_commit = AsyncMock()

        await service.apply_external_update(
            UserBotStatsExternalUpdate(
                channel_subscribe=False,
                received_methodology=False,
                review_link_clicked=False,
                review_public_consent_given=False,
            ),
            user_id=5,
        )

        self.assertFalse(stats.channel_subscribe)
        self.assertFalse(stats.received_methodology)
        self.assertIsNone(stats.received_methodology_at)
        self.assertFalse(stats.review_link_clicked)
        self.assertFalse(stats.review_public_consent_given)

    async def test_apply_internal_update_rejects_invalid_totals(self) -> None:
        session = _FakeSession()
        service = UserBotStatsService(session)
        stats = _build_user_bot_stats(telegram_user_id=1)

        service.get_or_create_for_user = AsyncMock(return_value=stats)

        with self.assertRaises(HTTPException) as ctx:
            await service.apply_internal_update(
                UserBotStatsInternalUpdate(
                    diagnostics_total=1,
                    diagnostics_completed_total=2,
                ),
                user_id=1,
            )

        self.assertEqual(ctx.exception.status_code, 400)

    async def test_resolve_user_not_found(self) -> None:
        session = _FakeSession()
        service = UserBotStatsService(session)

        with self.assertRaises(HTTPException) as ctx:
            await service._resolve_user(user_id=999, chat_id=None)

        self.assertEqual(ctx.exception.status_code, 404)

    async def test_rebuild_for_user_recalculates_internal_fields(self) -> None:
        session = _FakeSession()
        service = UserBotStatsService(session)
        stats = _build_user_bot_stats(telegram_user_id=3)

        t0 = datetime(2026, 5, 10, 10, 0, tzinfo=timezone.utc)
        t1 = t0 + timedelta(hours=1)
        t2 = t0 + timedelta(hours=2)

        service._resolve_user = AsyncMock(return_value=SimpleNamespace(id=3))
        service.get_or_create_for_user = AsyncMock(return_value=stats)
        service._list_core_requests = AsyncMock(
            return_value=[
                SimpleNamespace(created_at=t1),
                SimpleNamespace(created_at=t2),
            ]
        )
        service._list_diagnostic_runs = AsyncMock(
            return_value=[
                SimpleNamespace(status="created", created_at=t0, completed_at=None),
                SimpleNamespace(status="completed", created_at=t1, completed_at=t2),
            ]
        )
        service._flush_and_commit = AsyncMock()

        rebuilt = await service.rebuild_for_user(user_id=3)

        self.assertIs(rebuilt, stats)
        self.assertTrue(stats.core_application_submitted)
        self.assertEqual(stats.core_application_submitted_at, t1)
        self.assertEqual(stats.diagnostics_total, 2)
        self.assertEqual(stats.diagnostics_completed_total, 1)
        self.assertEqual(stats.last_diagnostic_at, t2)


class UserDiagnosticStatsServiceTests(unittest.IsolatedAsyncioTestCase):
    def test_build_user_diagnostic_stats_insert_values_uses_default_stats_values(self) -> None:
        from app.modules.stats_module.services.user_diagnostic_stats_service import (
            _build_user_diagnostic_stats_insert_values,
        )

        values = _build_user_diagnostic_stats_insert_values(
            telegram_user_id=17,
            diagnostic_code="default",
        )

        self.assertEqual(values["telegram_user_id"], 17)
        self.assertEqual(values["diagnostic_code"], "default")
        self.assertEqual(values["attempts_total"], 0)
        self.assertEqual(values["completed_total"], 0)
        self.assertIsNone(values["last_started_at"])
        self.assertIsNone(values["last_completed_at"])
        self.assertIsNone(values["last_status"])
        self.assertEqual(values["created_at"], values["updated_at"])

    async def test_ensure_for_user_and_diagnostic_adds_default_stats_row(self) -> None:
        session = _FakeSession()
        service = UserDiagnosticStatsService(session)
        created = _build_user_diagnostic_stats(telegram_user_id=17, diagnostic_code="default")
        session.execute_results = [
            _FakeResult([]),
            _FakeResult([]),
            _FakeResult([created]),
        ]

        result = await service.ensure_for_user_and_diagnostic(
            telegram_user_id=17,
            diagnostic_code="default",
        )

        self.assertIs(result, created)
        self.assertEqual(created.telegram_user_id, 17)
        self.assertEqual(created.diagnostic_code, "default")
        self.assertEqual(created.attempts_total, 0)
        self.assertEqual(created.completed_total, 0)
        self.assertIsNone(created.last_started_at)
        self.assertIsNone(created.last_completed_at)
        self.assertIsNone(created.last_status)
        self.assertEqual(session.flush_calls, 1)

    async def test_apply_event_supports_user_id_and_chat_id(self) -> None:
        session = _FakeSession()
        service = UserDiagnosticStatsService(session)
        stats = _build_user_diagnostic_stats(telegram_user_id=11, diagnostic_code="default")

        service._resolve_user = AsyncMock(return_value=SimpleNamespace(id=11))
        service._get_by_user_and_code = AsyncMock(return_value=stats)

        await service.apply_event(
            UserDiagnosticStatsEventUpdate(diagnostic_code="default", attempts_delta=1),
            user_id=11,
        )
        await service.apply_event(
            UserDiagnosticStatsEventUpdate(diagnostic_code="default", attempts_delta=1),
            chat_id=100011,
        )

        first_call = service._resolve_user.await_args_list[0].kwargs
        second_call = service._resolve_user.await_args_list[1].kwargs
        self.assertEqual(first_call, {"user_id": 11, "chat_id": None})
        self.assertEqual(second_call, {"user_id": None, "chat_id": 100011})

    async def test_apply_event_increments_counters(self) -> None:
        session = _FakeSession()
        service = UserDiagnosticStatsService(session)
        stats = _build_user_diagnostic_stats(telegram_user_id=11, diagnostic_code="default")

        service._resolve_user = AsyncMock(return_value=SimpleNamespace(id=11))
        service._get_by_user_and_code = AsyncMock(return_value=stats)

        updated = await service.apply_event(
            UserDiagnosticStatsEventUpdate(
                diagnostic_code="default",
                attempts_delta=2,
                completed_delta=1,
                started=True,
                completed=True,
                status="completed",
            ),
            user_id=11,
        )

        self.assertIs(updated, stats)
        self.assertEqual(stats.attempts_total, 2)
        self.assertEqual(stats.completed_total, 1)
        self.assertIsNotNone(stats.last_started_at)
        self.assertIsNotNone(stats.last_completed_at)
        self.assertEqual(stats.last_status, "completed")

    async def test_apply_event_preserves_invariant_completed_lte_attempts(self) -> None:
        session = _FakeSession()
        service = UserDiagnosticStatsService(session)
        stats = _build_user_diagnostic_stats(telegram_user_id=8, diagnostic_code="default")

        service._resolve_user = AsyncMock(return_value=SimpleNamespace(id=8))
        service._get_by_user_and_code = AsyncMock(return_value=stats)

        with self.assertRaises(HTTPException) as ctx:
            await service.apply_event(
                UserDiagnosticStatsEventUpdate(
                    diagnostic_code="default",
                    attempts_delta=0,
                    completed_delta=1,
                ),
                user_id=8,
            )

        self.assertEqual(ctx.exception.status_code, 400)

    async def test_rebuild_for_user_recalculates_per_diagnostic_and_removes_stale(self) -> None:
        session = _FakeSession()
        service = UserDiagnosticStatsService(session)

        existing_a = _build_user_diagnostic_stats(telegram_user_id=22, diagnostic_code="a")
        stale_c = _build_user_diagnostic_stats(telegram_user_id=22, diagnostic_code="c")

        t0 = datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc)
        t1 = t0 + timedelta(minutes=10)
        t2 = t0 + timedelta(minutes=20)

        service._resolve_user = AsyncMock(return_value=SimpleNamespace(id=22))
        service._list_user_diagnostic_stats = AsyncMock(return_value=[existing_a, stale_c])
        service._list_diagnostic_runs = AsyncMock(
            return_value=[
                SimpleNamespace(
                    diagnostic_code="a",
                    status="created",
                    created_at=t0,
                    completed_at=None,
                    updated_at=t0,
                    id=1,
                ),
                SimpleNamespace(
                    diagnostic_code="a",
                    status="completed",
                    created_at=t1,
                    completed_at=t2,
                    updated_at=t2,
                    id=2,
                ),
                SimpleNamespace(
                    diagnostic_code="b",
                    status="failed",
                    created_at=t2,
                    completed_at=None,
                    updated_at=t2,
                    id=3,
                ),
            ]
        )

        rebuilt = await service.rebuild_for_user(user_id=22)

        self.assertEqual([row.diagnostic_code for row in rebuilt], ["a", "b"])
        self.assertEqual(existing_a.attempts_total, 2)
        self.assertEqual(existing_a.completed_total, 1)
        self.assertEqual(existing_a.last_started_at, t1)
        self.assertEqual(existing_a.last_completed_at, t2)
        self.assertEqual(existing_a.last_status, "completed")

        rebuilt_b = next(row for row in rebuilt if row.diagnostic_code == "b")
        self.assertEqual(rebuilt_b.attempts_total, 1)
        self.assertEqual(rebuilt_b.completed_total, 0)
        self.assertEqual(rebuilt_b.last_status, "failed")
        self.assertEqual(session.deleted, [stale_c])


if __name__ == "__main__":
    unittest.main()
