from decimal import Decimal

from pydantic import BaseModel


class AdminStatsOut(BaseModel):
    total_products: int
    active_products: int
    total_orders: int
    total_revenue: Decimal
    orders_by_status: dict[str, int]
