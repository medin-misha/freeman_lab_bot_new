from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database

from .models import Product
from .schemas import ProductCreate, ProductRead
from .services import create_product, delete_product, get_product, list_products


router = APIRouter(prefix="/products", tags=["products"])

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product_handler(
    data: ProductCreate,
    session: SessionDep,
) -> Product:
    return await create_product(data=data, session=session)


@router.get("/{id}", response_model=ProductRead)
async def get_product_handler(
    id: int,
    session: SessionDep,
) -> Product:
    return await get_product(product_id=id, session=session)


@router.get("", response_model=list[ProductRead])
async def list_products_handler(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1)] = 10,
    user_id: int | None = None,
) -> list[Product]:
    return await list_products(
        session=session,
        page=page,
        limit=limit,
        user_id=user_id,
    )


@router.delete("/{id}")
async def delete_product_handler(
    id: int,
    session: SessionDep,
) -> dict[str, str]:
    result = await delete_product(product_id=id, session=session)
    return {"status": result}
