from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.admin.schemas import AdminStatsOut
from app.features.orders.models import Order
from app.features.products.models import Product


class AdminService:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_stats(self) -> AdminStatsOut:
        total_products: int = await self._db.scalar(
            select(func.count()).select_from(Product)
        ) or 0
        active_products: int = await self._db.scalar(
            select(func.count()).select_from(Product).where(Product.is_active == True)  # noqa: E712
        ) or 0

        rows = (
            await self._db.execute(
                select(
                    Order.status,
                    func.count().label("cnt"),
                    func.sum(Order.total).label("rev"),
                ).group_by(Order.status)
            )
        ).all()

        orders_by_status: dict[str, int] = {}
        total_revenue = Decimal("0.00")
        total_orders = 0
        for row in rows:
            orders_by_status[row.status.value] = row.cnt
            total_orders += row.cnt
            if row.rev:
                total_revenue += row.rev

        return AdminStatsOut(
            total_products=total_products,
            active_products=active_products,
            total_orders=total_orders,
            total_revenue=total_revenue,
            orders_by_status=orders_by_status,
        )
