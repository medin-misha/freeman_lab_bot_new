from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.telegram_module import TelegramUser
from app.modules.system.services.errors import DBErrorHandler

if TYPE_CHECKING:
    from app.modules.base_diagnostic_module.models import DiagnosticRun
    from app.modules.core_request_module.models import CoreRequest

from ..models import UserBotStats
from ..schemas import UserBotStatsExternalUpdate, UserBotStatsInternalUpdate
from ..utils.time import utcnow


def _build_user_bot_stats_insert_values(telegram_user_id: int) -> dict[str, object]:
    now = datetime.utcnow()
    return {
        "telegram_user_id": telegram_user_id,
        "source": None,
        "current_branch": None,
        "channel_subscribe": False,
        "received_methodology": False,
        "received_methodology_at": None,
        "core_application_submitted": False,
        "core_application_submitted_at": None,
        "diagnostics_total": 0,
        "diagnostics_completed_total": 0,
        "last_diagnostic_at": None,
        "review_link_clicked": False,
        "review_public_consent_given": False,
        "created_at": now,
        "updated_at": now,
    }


class UserBotStatsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_for_telegram_user(self, *, telegram_user_id: int) -> UserBotStats:
        try:
            stats = await self._get_by_telegram_user_id(telegram_user_id)
            if stats is not None:
                return stats

            stats = UserBotStats(**_build_user_bot_stats_insert_values(telegram_user_id))
            self.session.add(stats)
            await self._flush_and_commit()
        except HTTPException:
            raise
        except Exception as err:
            await self.session.rollback()
            DBErrorHandler.handle(err=err, model=UserBotStats, action="creating")
        else:
            return stats

    async def bulk_create_for_telegram_users(
        self,
        *,
        telegram_user_ids: list[int],
    ) -> list[UserBotStats]:
        if not telegram_user_ids:
            return []

        unique_user_ids = list(dict.fromkeys(telegram_user_ids))

        try:
            existing_rows = await self._list_by_telegram_user_ids(unique_user_ids)
            existing_by_user_id = {
                row.telegram_user_id: row for row in existing_rows
            }
            missing_user_ids = [
                user_id for user_id in unique_user_ids if user_id not in existing_by_user_id
            ]
            if missing_user_ids:
                new_rows = [
                    UserBotStats(**_build_user_bot_stats_insert_values(user_id))
                    for user_id in missing_user_ids
                ]
                self.session.add_all(new_rows)
                await self._flush_and_commit()
                existing_rows.extend(new_rows)
        except HTTPException:
            raise
        except Exception as err:
            await self.session.rollback()
            DBErrorHandler.handle(err=err, model=UserBotStats, action="bulk creating")
        else:
            rows_by_user_id = {row.telegram_user_id: row for row in existing_rows}
            return [rows_by_user_id[user_id] for user_id in unique_user_ids]

    async def get_or_create_for_user(self, *, user_id: int | None = None, chat_id: int | None = None) -> UserBotStats:
        user = await self._resolve_user(user_id=user_id, chat_id=chat_id)
        stats = await self._get_by_telegram_user_id(user.id)
        if stats is None:
            stats = UserBotStats(**_build_user_bot_stats_insert_values(user.id))
            self.session.add(stats)
            await self.session.flush()
        return stats

    async def get_for_user(self, *, user_id: int | None = None, chat_id: int | None = None) -> UserBotStats:
        user = await self._resolve_user(user_id=user_id, chat_id=chat_id)
        stats = await self._get_by_telegram_user_id(user.id)
        if stats is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"UserBotStats for TelegramUser id={user.id} not found.",
            )
        return stats

    async def apply_external_update(
        self,
        data: UserBotStatsExternalUpdate,
        *,
        user_id: int | None = None,
        chat_id: int | None = None,
    ) -> UserBotStats:
        stats = await self.get_or_create_for_user(user_id=user_id, chat_id=chat_id)

        if data.source is not None:
            stats.set_source(data.source)
        if data.current_branch is not None:
            stats.set_current_branch(data.current_branch)
        if data.channel_subscribe is not None:
            stats.set_channel_subscribe(data.channel_subscribe)
        if data.received_methodology is not None:
            stats.mark_received_methodology(
                received=data.received_methodology,
                at=utcnow() if data.received_methodology else None,
            )
        if data.review_link_clicked is not None:
            stats.mark_review_link_clicked(data.review_link_clicked)
        if data.review_public_consent_given is not None:
            stats.mark_review_public_consent_given(data.review_public_consent_given)

        self._ensure_invariants(stats)
        await self._flush_and_commit()
        return stats

    async def apply_internal_update(
        self,
        data: UserBotStatsInternalUpdate,
        *,
        user_id: int | None = None,
        chat_id: int | None = None,
    ) -> UserBotStats:
        stats = await self.get_or_create_for_user(user_id=user_id, chat_id=chat_id)

        if data.core_application_submitted is not None:
            stats.mark_core_application_submitted(
                submitted=data.core_application_submitted,
                at=utcnow() if data.core_application_submitted else None,
            )

        diagnostics_total = (
            data.diagnostics_total if data.diagnostics_total is not None else stats.diagnostics_total
        )
        diagnostics_completed_total = (
            data.diagnostics_completed_total
            if data.diagnostics_completed_total is not None
            else stats.diagnostics_completed_total
        )
        self._validate_totals(
            diagnostics_total=diagnostics_total,
            diagnostics_completed_total=diagnostics_completed_total,
        )
        stats.set_diagnostics_totals(
            diagnostics_total=diagnostics_total,
            diagnostics_completed_total=diagnostics_completed_total,
        )

        if data.last_diagnostic_at is not None:
            stats.set_last_diagnostic_at(self._max_dt(stats.last_diagnostic_at, data.last_diagnostic_at))

        self._ensure_invariants(stats)
        await self._flush_and_commit()
        return stats

    async def update_core_application_submitted(
        self,
        *,
        telegram_user_id: int,
        submitted_at: datetime,
    ) -> None:
        """Отмечает первую подачу core-заявки для пользователя.

        Принимает внутренний DB id пользователя (не telegram_id).
        Если флаг уже выставлен — ничего не делает, чтобы сохранить
        дату первой заявки (согласованно с логикой rebuild).
        """
        stats = await self._get_by_telegram_user_id(telegram_user_id)
        if stats is None:
            stats = UserBotStats(**_build_user_bot_stats_insert_values(telegram_user_id))
            self.session.add(stats)
            await self.session.flush()
        if not stats.core_application_submitted:
            stats.mark_core_application_submitted(submitted=True, at=submitted_at)
            await self._flush_and_commit()

    async def increment_diagnostics_created(
        self,
        *,
        telegram_user_id: int,
        at: datetime,
        flush: bool = True,
    ) -> None:
        """Вызывается при создании DiagnosticRun: инкрементирует diagnostics_total.

        Принимает внутренний DB id пользователя (не telegram_id).
        Создаёт запись UserBotStats, если её ещё нет.
        flush=False позволяет вызывать внутри уже открытой транзакции — коммит
        делает вызывающий код.
        """
        stats = await self._get_by_telegram_user_id(telegram_user_id)
        if stats is None:
            stats = UserBotStats(**_build_user_bot_stats_insert_values(telegram_user_id))
            self.session.add(stats)
            await self.session.flush()
        stats.increment_diagnostics_total()
        stats.set_last_diagnostic_at(self._max_dt(stats.last_diagnostic_at, at))
        if flush:
            await self.session.flush()

    async def increment_diagnostics_completed(
        self,
        *,
        telegram_user_id: int,
        at: datetime,
        flush: bool = True,
    ) -> None:
        """Вызывается при завершении DiagnosticRun: инкрементирует diagnostics_completed_total.

        Принимает внутренний DB id пользователя (не telegram_id).
        Создаёт запись UserBotStats, если её ещё нет.
        flush=False позволяет вызывать внутри уже открытой транзакции — коммит
        делает вызывающий код.
        """
        stats = await self._get_by_telegram_user_id(telegram_user_id)
        if stats is None:
            stats = UserBotStats(**_build_user_bot_stats_insert_values(telegram_user_id))
            self.session.add(stats)
            await self.session.flush()
        stats.increment_diagnostics_completed_total()
        stats.set_last_diagnostic_at(self._max_dt(stats.last_diagnostic_at, at))
        if flush:
            await self.session.flush()

    async def rebuild_for_user(
        self,
        *,
        user_id: int | None = None,
        chat_id: int | None = None,
    ) -> UserBotStats:
        user = await self._resolve_user(user_id=user_id, chat_id=chat_id)
        stats = await self.get_or_create_for_user(user_id=user.id)

        core_requests = await self._list_core_requests(user.id)
        core_application_submitted = bool(core_requests)
        core_application_submitted_at = (
            min(req.created_at for req in core_requests) if core_requests else None
        )
        stats.mark_core_application_submitted(
            submitted=core_application_submitted,
            at=core_application_submitted_at,
        )

        from app.modules.base_diagnostic_module.models import DiagnosticRunStatus

        diagnostic_runs = await self._list_diagnostic_runs(user.id)
        diagnostics_total = len(diagnostic_runs)
        diagnostics_completed_total = sum(
            1 for run in diagnostic_runs if run.status == DiagnosticRunStatus.COMPLETED
        )
        self._validate_totals(
            diagnostics_total=diagnostics_total,
            diagnostics_completed_total=diagnostics_completed_total,
        )
        stats.set_diagnostics_totals(
            diagnostics_total=diagnostics_total,
            diagnostics_completed_total=diagnostics_completed_total,
        )

        last_diagnostic_at: datetime | None = None
        for run in diagnostic_runs:
            candidate_times = [run.created_at]
            if run.completed_at is not None:
                candidate_times.append(run.completed_at)
            run_last_time = max(candidate_times)
            if last_diagnostic_at is None or run_last_time > last_diagnostic_at:
                last_diagnostic_at = run_last_time
        stats.set_last_diagnostic_at(last_diagnostic_at)

        self._ensure_invariants(stats)
        await self._flush_and_commit()
        return stats

    def _validate_totals(self, *, diagnostics_total: int, diagnostics_completed_total: int) -> None:
        if diagnostics_total < 0 or diagnostics_completed_total < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="diagnostics totals must be non-negative.",
            )
        if diagnostics_completed_total > diagnostics_total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="diagnostics_completed_total cannot exceed diagnostics_total.",
            )

    def _ensure_invariants(self, stats: UserBotStats) -> None:
        if stats.received_methodology and stats.received_methodology_at is None:
            stats.received_methodology_at = utcnow()
        self._validate_totals(
            diagnostics_total=stats.diagnostics_total,
            diagnostics_completed_total=stats.diagnostics_completed_total,
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

    async def _get_by_telegram_user_id(self, telegram_user_id: int) -> UserBotStats | None:
        result = await self.session.execute(
            select(UserBotStats).where(UserBotStats.telegram_user_id == telegram_user_id)
        )
        return result.scalars().first()

    async def _list_by_telegram_user_ids(
        self,
        telegram_user_ids: list[int],
    ) -> list[UserBotStats]:
        result = await self.session.execute(
            select(UserBotStats).where(UserBotStats.telegram_user_id.in_(telegram_user_ids))
        )
        return list(result.scalars().all())

    async def _flush_and_commit(self) -> None:
        await self.session.flush()
        await self.session.commit()

    async def _list_core_requests(self, telegram_user_id: int) -> list[CoreRequest]:
        from app.modules.core_request_module.models import CoreRequest

        result = await self.session.execute(
            select(CoreRequest).where(CoreRequest.user_id == telegram_user_id)
        )
        return list(result.scalars().all())

    async def _list_diagnostic_runs(self, telegram_user_id: int) -> list[DiagnosticRun]:
        from app.modules.base_diagnostic_module.models import DiagnosticRun

        result = await self.session.execute(
            select(DiagnosticRun).where(DiagnosticRun.user_id == telegram_user_id)
        )
        return list(result.scalars().all())

    @staticmethod
    def _max_dt(lhs: datetime | None, rhs: datetime) -> datetime:
        return rhs if lhs is None or rhs > lhs else lhs
