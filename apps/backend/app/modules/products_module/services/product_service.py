from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rmq_module import rmq_publisher
from app.modules.system import CRUD
from app.modules.telegram_module import TelegramUser

from ..models import Product
from ..schemas import (
    ProductAdminNotificationPayload,
    ProductAdminNotificationUser,
    ProductCreate,
)


ADMIN_PRODUCT_CREATED_EVENT = "admin.product.created"
ADMIN_PRODUCT_CREATED_QUEUE = "admin.product.created"


async def _get_user_or_404(
    session: AsyncSession,
    user_id: int,
) -> TelegramUser:
    user = await session.get(TelegramUser, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TelegramUser with id={user_id} not found.",
        )
    return user


async def _build_admin_notification_payload(
    *,
    session: AsyncSession,
    product: Product,
) -> ProductAdminNotificationPayload:
    user = await _get_user_or_404(session=session, user_id=product.user_id)
    user_profile = user.user_profile
    return ProductAdminNotificationPayload(
        id=product.id,
        created_at=product.created_at,
        updated_at=product.updated_at,
        product_code=product.product_code,
        user_id=product.user_id,
        user=ProductAdminNotificationUser(
            telegram_id=user.telegram_id,
            username=user.username,
            full_name=user_profile.full_name if user_profile else None,
            date_of_birth=user_profile.date_of_birth if user_profile else None,
            city=user_profile.city if user_profile else None,
        ),
    )


async def publish_product_created_to_admin_bot(
    *,
    session: AsyncSession,
    product: Product,
) -> None:
    payload = await _build_admin_notification_payload(
        session=session,
        product=product,
    )
    await rmq_publisher.publish(
        event=ADMIN_PRODUCT_CREATED_EVENT,
        payload=payload.model_dump(mode="json"),
        queue_name=ADMIN_PRODUCT_CREATED_QUEUE,
        routing_key=ADMIN_PRODUCT_CREATED_EVENT,
    )


async def create_product(
    data: ProductCreate,
    session: AsyncSession,
) -> Product:
    await _get_user_or_404(session=session, user_id=data.user_id)
    product = await CRUD.create(
        data=ProductCreate(
            product_code=data.product_code.strip(),
            user_id=data.user_id,
        ),
        model=Product,
        session=session,
    )

    await publish_product_created_to_admin_bot(session=session, product=product)
    return product


async def get_product(
    product_id: int,
    session: AsyncSession,
) -> Product:
    return await CRUD.get(model=Product, session=session, id=product_id)


async def list_products(
    session: AsyncSession,
    *,
    page: int = 1,
    limit: int = 10,
    user_id: int | None = None,
) -> list[Product]:
    filters = {"user_id": user_id} if user_id is not None else None
    return await CRUD.get(
        model=Product,
        session=session,
        page=page,
        limit=limit,
        filters=filters,
    )


async def delete_product(
    product_id: int,
    session: AsyncSession,
) -> str:
    return await CRUD.delete(model=Product, session=session, id=product_id)
