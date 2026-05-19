import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.modules.telegram_module.models import TelegramUser
from app.modules.telegram_module.schemas import TelegramUserCreate
from app.modules.telegram_module.services.user_service import (
    bulk_create_telegram_users,
    create_telegram_user,
)


class TelegramUserServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_telegram_user_creates_related_stats_and_profile(self) -> None:
        session = object()
        telegram_user = TelegramUser(telegram_id=100017)
        telegram_user.id = 17

        with (
            patch(
                "app.modules.telegram_module.services.user_service.CRUD.get_or_create",
                AsyncMock(return_value=(telegram_user, True)),
            ),
            patch(
                "app.modules.telegram_module.services.user_service._create_related_records",
                AsyncMock(),
            ) as create_related_records,
        ):
            created_user, created = await create_telegram_user(
                data=TelegramUserCreate(telegram_id=100017),
                session=session,
            )

        self.assertIs(created_user, telegram_user)
        self.assertTrue(created)
        create_related_records.assert_awaited_once_with(
            session=session,
            telegram_users=[telegram_user],
        )

    async def test_create_telegram_user_cleans_up_when_related_creation_fails(self) -> None:
        session = object()
        telegram_user = TelegramUser(telegram_id=100017)
        telegram_user.id = 17
        error = HTTPException(status_code=400, detail="boom")

        with (
            patch(
                "app.modules.telegram_module.services.user_service.CRUD.get_or_create",
                AsyncMock(return_value=(telegram_user, True)),
            ),
            patch(
                "app.modules.telegram_module.services.user_service._create_related_records",
                AsyncMock(side_effect=error),
            ),
            patch(
                "app.modules.telegram_module.services.user_service._delete_telegram_users_by_ids",
                AsyncMock(),
            ) as delete_users,
        ):
            with self.assertRaises(HTTPException):
                await create_telegram_user(
                    data=TelegramUserCreate(telegram_id=100017),
                    session=session,
                )

        delete_users.assert_awaited_once_with(session=session, user_ids=[17])

    async def test_bulk_create_telegram_users_creates_related_stats_and_profiles(self) -> None:
        session = object()
        telegram_users = [
            TelegramUser(telegram_id=100017),
            TelegramUser(telegram_id=100018),
        ]
        telegram_users[0].id = 17
        telegram_users[1].id = 18

        with (
            patch(
                "app.modules.telegram_module.services.user_service.CRUD.bulk_create",
                AsyncMock(return_value=telegram_users),
            ),
            patch(
                "app.modules.telegram_module.services.user_service._create_related_records",
                AsyncMock(),
            ) as create_related_records,
        ):
            created_users = await bulk_create_telegram_users(
                data=[
                    TelegramUserCreate(telegram_id=100017),
                    TelegramUserCreate(telegram_id=100018),
                ],
                session=session,
            )

        self.assertEqual(created_users, telegram_users)
        create_related_records.assert_awaited_once_with(
            session=session,
            telegram_users=telegram_users,
        )


if __name__ == "__main__":
    unittest.main()
