import hmac
import hashlib
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


# ── Yoco webhook ──────────────────────────────────────────────────────────────

@router.post("/webhook/yoco", include_in_schema=False)
async def yoco_webhook(
    request: Request,
    svc: OrderService = Depends(_service),
) -> dict:
    payload = await request.body()
    signature = request.headers.get("X-Yoco-Signature", "")

    if settings.YOCO_WEBHOOK_SECRET:
        expected = hmac.new(
            settings.YOCO_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Yoco signature")

    data = await request.json()
    if data.get("type") in ("payment.succeeded", "checkout.complete"):
        checkout_id = (
            data.get("payload", {}).get("metadata", {}).get("orderId")
            or data.get("payload", {}).get("checkoutId")
        )
        if checkout_id:
            await svc.confirm_external_payment(checkout_id)

    return {"received": True}


# ── PayJustNow webhook (IPN) ──────────────────────────────────────────────────

@router.post("/webhook/payjustnow", include_in_schema=False)
async def payjustnow_webhook(
    request: Request,
    svc: OrderService = Depends(_service),
) -> dict:
    data = await request.json()
    # PJN sends orderId and status in the IPN body
    if data.get("status") in ("approved", "APPROVED", "COMPLETE"):
        order_id = data.get("orderId") or data.get("id")
        if order_id:
            await svc.confirm_external_payment(str(order_id))

    return {"received": True}


# ── Payflex callback ──────────────────────────────────────────────────────────
# Payflex redirects the customer back to redirectConfirmUrl with orderToken + status
# The frontend hits this endpoint to confirm the payment server-side

@router.post("/payment/payflex/confirm", include_in_schema=False)
async def payflex_confirm(
    request: Request,
    svc: OrderService = Depends(_service),
) -> dict:
    data = await request.json()
    order_token = data.get("orderToken")
    payflex_status = data.get("status", "")
    if payflex_status.upper() == "APPROVED" and order_token:
        await svc.confirm_external_payment(order_token)
    return {"received": True}


# ── HappyPay webhook ──────────────────────────────────────────────────────────

@router.post("/webhook/happypay", include_in_schema=False)
async def happypay_webhook(
    request: Request,
    svc: OrderService = Depends(_service),
) -> dict:
    data = await request.json()
    if data.get("status") in ("PAID", "APPROVED", "SUCCESS"):
        checkout_id = data.get("checkoutId") or data.get("id")
        if checkout_id:
            await svc.confirm_external_payment(str(checkout_id))

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
