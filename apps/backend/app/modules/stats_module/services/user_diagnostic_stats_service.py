from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.base_diagnostic_module.models import DiagnosticRun, DiagnosticRunStatus
from app.modules.telegram_module import TelegramUser

from ..models import UserDiagnosticStats
from ..schemas import UserDiagnosticStatsEventUpdate
from ..utils.time import utcnow


def _build_user_diagnostic_stats_insert_values(
    *,
    telegram_user_id: int,
    diagnostic_code: str,
) -> dict[str, object]:
    now = datetime.utcnow()
    return {
        "telegram_user_id": telegram_user_id,
        "diagnostic_code": diagnostic_code,
        "attempts_total": 0,
        "completed_total": 0,
        "last_started_at": None,
        "last_completed_at": None,
        "last_status": None,
        "created_at": now,
        "updated_at": now,
    }


class UserDiagnosticStatsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_for_user_and_diagnostic(
        self,
        *,
        telegram_user_id: int,
        diagnostic_code: str,
        flush: bool = True,
    ) -> UserDiagnosticStats:
        stats = await self._get_by_user_and_code(telegram_user_id, diagnostic_code)
        if stats is not None:
            return stats

        stmt = insert(UserDiagnosticStats.__table__).values(
            _build_user_diagnostic_stats_insert_values(
                telegram_user_id=telegram_user_id,
                diagnostic_code=diagnostic_code,
            )
        )
        await self.session.execute(
            stmt.on_conflict_do_nothing(
                constraint="uq_user_diagnostic_stats",
            )
        )
        if flush:
            await self.session.flush()
        stats = await self._get_by_user_and_code(telegram_user_id, diagnostic_code)
        if stats is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Failed to initialize UserDiagnosticStats for "
                    f"TelegramUser id={telegram_user_id}, diagnostic_code={diagnostic_code}."
                ),
            )
        return stats

    async def get_for_user_and_diagnostic(
        self,
        diagnostic_code: str,
        *,
        user_id: int | None = None,
        chat_id: int | None = None,
    ) -> UserDiagnosticStats:
        user = await self._resolve_user(user_id=user_id, chat_id=chat_id)
        stats = await self._get_by_user_and_code(user.id, diagnostic_code)
        if stats is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "UserDiagnosticStats for "
                    f"TelegramUser id={user.id}, diagnostic_code={diagnostic_code} not found."
                ),
            )
        return stats

    async def apply_event(
        self,
        data: UserDiagnosticStatsEventUpdate,
        *,
        user_id: int | None = None,
        chat_id: int | None = None,
    ) -> UserDiagnosticStats:
        user = await self._resolve_user(user_id=user_id, chat_id=chat_id)
        stats = await self.ensure_for_user_and_diagnostic(
            telegram_user_id=user.id,
            diagnostic_code=data.diagnostic_code,
        )

        if data.attempts_delta:
            if data.attempts_delta < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="attempts_delta must be >= 0.",
                )
            stats.increment_attempts(data.attempts_delta)

        if data.completed_delta:
            if data.completed_delta < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="completed_delta must be >= 0.",
                )
            stats.increment_completed(data.completed_delta)

        event_time = utcnow()
        if data.started:
            stats.set_last_started_at(self._max_dt(stats.last_started_at, event_time))
        if data.completed:
            stats.set_last_completed_at(self._max_dt(stats.last_completed_at, event_time))
        if data.status is not None:
            stats.set_last_status(data.status)

        self._validate_counters(stats)
        await self.session.flush()
        await self.session.commit()
        return stats

    async def rebuild_for_user(
        self,
        *,
        user_id: int | None = None,
        chat_id: int | None = None,
    ) -> list[UserDiagnosticStats]:
        user = await self._resolve_user(user_id=user_id, chat_id=chat_id)
        runs = await self._list_diagnostic_runs(user.id)
        existing_rows = await self._list_user_diagnostic_stats(user.id)

        existing_by_code: dict[str, UserDiagnosticStats] = {
            row.diagnostic_code: row for row in existing_rows
        }
        runs_by_code: dict[str, list[DiagnosticRun]] = {}
        for run in runs:
            runs_by_code.setdefault(run.diagnostic_code, []).append(run)

        active_codes = set(runs_by_code.keys())
        for row in existing_rows:
            if row.diagnostic_code not in active_codes:
                await self.session.delete(row)

        rebuilt_rows: list[UserDiagnosticStats] = []
        for diagnostic_code, code_runs in runs_by_code.items():
            row = existing_by_code.get(diagnostic_code)
            if row is None:
                row = UserDiagnosticStats(
                    telegram_user_id=user.id,
                    diagnostic_code=diagnostic_code,
                )
                self.session.add(row)

            attempts_total = len(code_runs)
            completed_runs = [
                run for run in code_runs if run.status == DiagnosticRunStatus.COMPLETED
            ]
            completed_total = len(completed_runs)
            last_started_at = max(run.created_at for run in code_runs)
            last_completed_at = max(
                (
                    run.completed_at
                    for run in completed_runs
                    if run.completed_at is not None
                ),
                default=None,
            )
            latest_run = max(
                code_runs,
                key=lambda run: (run.updated_at, run.id),
            )

            row.set_totals(
                attempts_total=attempts_total,
                completed_total=completed_total,
            )
            row.set_last_started_at(last_started_at)
            row.set_last_completed_at(last_completed_at)
            row.set_last_status(latest_run.status)
            self._validate_counters(row)
            rebuilt_rows.append(row)

        await self.session.flush()
        await self.session.commit()
        return sorted(rebuilt_rows, key=lambda row: row.diagnostic_code)

    def _validate_counters(self, stats: UserDiagnosticStats) -> None:
        if stats.attempts_total < 0 or stats.completed_total < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="diagnostic counters must be non-negative.",
            )
        if stats.completed_total > stats.attempts_total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="completed_total cannot exceed attempts_total.",
            )

    async def _resolve_user(self, *, user_id: int | None, chat_id: int | None) -> TelegramUser:
        if user_id is None and chat_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either user_id or chat_id must be provided.",
            )
        if user_id is not None and chat_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide only one identifier: user_id or chat_id.",
            )

        if user_id is not None:
            user = await self.session.get(TelegramUser, user_id)
        else:
            result = await self.session.execute(
                select(TelegramUser).where(TelegramUser.telegram_id == chat_id)
            )
            user = result.scalars().first()

        if user is None:
            target = f"id={user_id}" if user_id is not None else f"telegram_id={chat_id}"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TelegramUser with {target} not found.",
            )
        return user

    async def _get_by_user_and_code(
        self,
        telegram_user_id: int,
        diagnostic_code: str,
    ) -> UserDiagnosticStats | None:
        result = await self.session.execute(
            select(UserDiagnosticStats).where(
                UserDiagnosticStats.telegram_user_id == telegram_user_id,
                UserDiagnosticStats.diagnostic_code == diagnostic_code,
            )
        )
        return result.scalars().first()

    async def _list_diagnostic_runs(self, telegram_user_id: int) -> list[DiagnosticRun]:
        result = await self.session.execute(
            select(DiagnosticRun).where(DiagnosticRun.user_id == telegram_user_id)
        )
        return list(result.scalars().all())

    async def _list_user_diagnostic_stats(
        self,
        telegram_user_id: int,
    ) -> list[UserDiagnosticStats]:
        result = await self.session.execute(
            select(UserDiagnosticStats).where(
                UserDiagnosticStats.telegram_user_id == telegram_user_id
            )
        )
        return list(result.scalars().all())

    @staticmethod
    def _max_dt(lhs: datetime | None, rhs: datetime) -> datetime:
        return rhs if lhs is None or rhs > lhs else lhs
