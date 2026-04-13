import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user_id, require_admin
from app.features.orders.models import OrderStatus
from app.features.orders.schemas import (
    AdminOrderUpdate,
    OrderCreateIn,
    OrderCreatedOut,
    OrderListOut,
    OrderOut,
)
from app.features.orders.service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])
settings = get_settings()


def _service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(db)


@router.post("", response_model=OrderCreatedOut, status_code=201)
async def create_order(
    payload: OrderCreateIn,
    user_id: int = Depends(get_current_user_id),
    svc: OrderService = Depends(_service),
) -> OrderCreatedOut:
    return await svc.create_order(user_id, payload)


@router.get("/me", response_model=OrderListOut)
async def my_orders(
    page: int = Query(1, ge=1),
    user_id: int = Depends(get_current_user_id),
    svc: OrderService = Depends(_service),
) -> OrderListOut:
    return await svc.list_my_orders(user_id, page)


@router.get("/me/{order_id}", response_model=OrderOut)
async def get_my_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: OrderService = Depends(_service),
) -> OrderOut:
    return await svc.get_order(order_id, user_id)


# ── Stripe webhook ────────────────────────────────────────────────────────────

@router.post("/webhook/stripe", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="stripe-signature"),
    svc: OrderService = Depends(_service),
) -> dict:
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        await svc.confirm_payment(event["data"]["object"]["id"])

    return {"received": True}


# ── Admin ─────────────────────────────────────────────────────────────────────

@router.get("/admin", response_model=OrderListOut)
async def admin_list_orders(
    page: int = Query(1, ge=1),
    order_status: OrderStatus | None = None,
    _admin: int = Depends(require_admin),
    svc: OrderService = Depends(_service),
) -> OrderListOut:
    return await svc.admin_list_orders(page, order_status)


@router.patch("/admin/{order_id}", response_model=OrderOut)
async def admin_update_order(
    order_id: int,
    payload: AdminOrderUpdate,
    _admin: int = Depends(require_admin),
    svc: OrderService = Depends(_service),
) -> OrderOut:
    return await svc.admin_update_order(order_id, payload)
