from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.features.admin.schemas import AdminStatsOut
from app.features.admin.service import AdminService
from app.features.orders.models import OrderStatus
from app.features.orders.schemas import AdminOrderUpdate, OrderListOut, OrderOut
from app.features.orders.service import OrderService
from app.features.products.schemas import ProductListOut
from app.features.products.service import ProductService

router = APIRouter(prefix="/admin", tags=["Admin"])


def _admin_svc(db: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(db)


def _product_svc(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


def _order_svc(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(db)


# ── Products ──────────────────────────────────────────────────────────────────

@router.get("/products", response_model=ProductListOut)
async def admin_list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    _admin: int = Depends(require_admin),
    svc: ProductService = Depends(_product_svc),
) -> ProductListOut:
    """Return all products, including inactive ones."""
    return await svc.admin_list_all(page=page, page_size=page_size)


# ── Orders ────────────────────────────────────────────────────────────────────

@router.get("/orders", response_model=OrderListOut)
async def admin_list_orders(
    page: int = Query(1, ge=1),
    order_status: OrderStatus | None = None,
    _admin: int = Depends(require_admin),
    svc: OrderService = Depends(_order_svc),
) -> OrderListOut:
    return await svc.admin_list_orders(page=page, status=order_status)


@router.patch("/orders/{order_id}", response_model=OrderOut)
async def admin_update_order(
    order_id: int,
    payload: AdminOrderUpdate,
    _admin: int = Depends(require_admin),
    svc: OrderService = Depends(_order_svc),
) -> OrderOut:
    return await svc.admin_update_order(order_id, payload)


# ── Stats / dashboard ─────────────────────────────────────────────────────────

@router.get("/stats", response_model=AdminStatsOut)
async def admin_stats(
    _admin: int = Depends(require_admin),
    svc: AdminService = Depends(_admin_svc),
) -> AdminStatsOut:
    return await svc.get_stats()
