from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.orders.models import Order


class OrderRepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, order_id: int) -> Order | None:
        result = await self._db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def get_by_reference(self, reference: str) -> Order | None:
        result = await self._db.execute(select(Order).where(Order.reference == reference))
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: int, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[Order], int]:
        base = select(Order).where(Order.user_id == user_id)
        total = (await self._db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        result = await self._db.execute(
            base.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        return result.scalars().all(), total

    async def list_all(
        self, *, page: int = 1, page_size: int = 50, status=None
    ) -> tuple[list[Order], int]:
        base = select(Order)
        if status:
            base = base.where(Order.status == status)
        total = (await self._db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        result = await self._db.execute(
            base.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        return result.scalars().all(), total

    async def create(self, order: Order) -> Order:
        self._db.add(order)
        await self._db.flush()
        return order

    async def save(self, order: Order) -> Order:
        await self._db.flush()
        return order
