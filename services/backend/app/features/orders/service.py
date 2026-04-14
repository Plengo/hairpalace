import random
import string
from decimal import Decimal

import httpx
import stripe
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.events import Event, TOPIC_ORDERS, get_producer
from app.features.orders.models import Order, OrderItem, OrderStatus, PaymentProvider
from app.features.orders.repository import OrderRepository
from app.features.orders.schemas import (
    AdminOrderUpdate,
    OrderCreateIn,
    OrderCreatedOut,
    OrderListOut,
    OrderOut,
)
from app.features.products.repository import ProductRepository
from app.features.notifications.service import NotificationService

settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY

SHIPPING_FEE = Decimal("80.00")   # flat-rate — adjust as needed


async def _emit_order(event: Event) -> None:
    producer = get_producer()
    if producer:
        await producer.emit(TOPIC_ORDERS, event, key=str(event.entity_id))


def _generate_reference() -> str:
    """Short, human-readable order reference: HP-XXXXXX."""
    return "HP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def _split_name(full_name: str) -> tuple[str, str]:
    """Split 'Jane Doe' into ('Jane', 'Doe'). Handles single-word names."""
    parts = full_name.strip().split(" ", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""


class OrderService:

    def __init__(self, db: AsyncSession) -> None:
        self._repo = OrderRepository(db)
        self._products = ProductRepository(db)
        self._notify = NotificationService()

    # ── Payment session creation (per provider) ───────────────────────────────

    async def _stripe_checkout(self, total: Decimal, user_id: int, reference: str) -> dict:
        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),
            currency="zar",
            metadata={"user_id": str(user_id), "reference": reference},
        )
        return {"client_secret": intent.client_secret, "stripe_intent_id": intent.id}

    async def _yoco_checkout(self, total: Decimal, order_id: int) -> dict:
        """
        Yoco Online — hosted checkout session.
        Docs: https://developer.yoco.com/online/resources/integration-types/
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://payments.yoco.com/api/checkouts",
                headers={
                    "Authorization": f"Bearer {settings.YOCO_SECRET_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "amount": int(total * 100),
                    "currency": "ZAR",
                    "successUrl": f"{settings.FRONTEND_URL}/orders/{order_id}?payment=confirmed",
                    "cancelUrl": f"{settings.FRONTEND_URL}/checkout?payment=cancelled",
                    "metadata": {"orderId": str(order_id)},
                },
            )
        if resp.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Yoco checkout failed: {resp.text}")
        data = resp.json()
        return {"external_id": data["id"], "checkout_url": data["redirectUrl"]}

    async def _payjustnow_checkout(
        self, total: Decimal, order_id: int, reference: str, shipping_name: str
    ) -> dict:
        """
        PayJustNow — SA BNPL, 3 equal interest-free payments.
        Docs: https://developer.payjustnow.com
        """
        first, last = _split_name(shipping_name)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://merchant.payjustnow.com/api/v1/orders",
                headers={
                    "Authorization": f"Bearer {settings.PJN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "merchantReference": reference,
                    "amount": int(total * 100),
                    "successRedirectUrl": f"{settings.FRONTEND_URL}/orders/{order_id}?payment=confirmed",
                    "failureRedirectUrl": f"{settings.FRONTEND_URL}/checkout?payment=cancelled",
                    "ipnUrl": f"{settings.BACKEND_URL}/api/v1/orders/webhook/payjustnow",
                    "customer": {"firstName": first, "lastName": last},
                },
            )
        if resp.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"PayJustNow checkout failed: {resp.text}")
        data = resp.json()
        return {"external_id": data.get("id") or data.get("orderId"), "checkout_url": data["redirectUrl"]}

    async def _payflex_checkout(
        self, total: Decimal, order_id: int, shipping_name: str
    ) -> dict:
        """
        Payflex — SA BNPL, 4 payments over 6 weeks interest-free.
        Docs: https://developer.payflex.co.za
        """
        first, last = _split_name(shipping_name)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.payflex.co.za/order",
                headers={
                    "Authorization": f"Bearer {settings.PAYFLEX_SECRET}",
                    "Content-Type": "application/json",
                },
                json={
                    "amount": {"amount": int(total * 100), "currency": "ZAR"},
                    "merchant": {
                        "redirectConfirmUrl": f"{settings.FRONTEND_URL}/orders/{order_id}?payment=confirmed",
                        "redirectCancelUrl": f"{settings.FRONTEND_URL}/checkout?payment=cancelled",
                    },
                    "consumer": {"givenNames": first, "surname": last},
                },
            )
        if resp.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Payflex checkout failed: {resp.text}")
        data = resp.json()
        return {"external_id": data["token"], "checkout_url": data["redirectCheckoutUri"]}

    async def _happypay_checkout(
        self, total: Decimal, order_id: int, reference: str
    ) -> dict:
        """
        HappyPay — SA instalment payment solution.
        Docs / credentials: https://happypay.co.za/developers
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.happypay.co.za/v1/checkout",
                headers={
                    "Authorization": f"Bearer {settings.HAPPYPAY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "amount": int(total * 100),
                    "currency": "ZAR",
                    "merchantReference": reference,
                    "successUrl": f"{settings.FRONTEND_URL}/orders/{order_id}?payment=confirmed",
                    "cancelUrl": f"{settings.FRONTEND_URL}/checkout?payment=cancelled",
                    "webhookUrl": f"{settings.BACKEND_URL}/api/v1/orders/webhook/happypay",
                },
            )
        if resp.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"HappyPay checkout failed: {resp.text}")
        data = resp.json()
        return {"external_id": data.get("checkoutId") or data.get("id"), "checkout_url": data["checkoutUrl"]}

    # ── Order creation ────────────────────────────────────────────────────────

    async def create_order(self, user_id: int, payload: OrderCreateIn) -> OrderCreatedOut:
        # Validate products and calculate totals
        items_data = []
        subtotal = Decimal("0.00")

        for cart_item in payload.items:
            product = await self._products.get_by_id(cart_item.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {cart_item.product_id} not found or unavailable",
                )
            line_total = product.price * cart_item.quantity
            subtotal += line_total
            items_data.append((product, cart_item.quantity))

        total = subtotal + SHIPPING_FEE

        # Create the order in the DB first so we have an order.id for the provider return URL
        order = Order(
            reference=_generate_reference(),
            user_id=user_id,
            status=OrderStatus.PENDING_PAYMENT,
            payment_provider=payload.payment_provider,
            subtotal=subtotal,
            shipping_fee=SHIPPING_FEE,
            total=total,
            shipping_name=payload.shipping.name,
            shipping_address=payload.shipping.address,
            shipping_city=payload.shipping.city,
            shipping_province=payload.shipping.province,
            shipping_postal_code=payload.shipping.postal_code,
        )
        order = await self._repo.create(order)

        for product, qty in items_data:
            order.items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=qty,
                    unit_price=product.price,
                    product_name=product.name,
                )
            )
        order = await self._repo.save(order)

        # Create the payment session with the selected provider
        provider = payload.payment_provider
        client_secret: str | None = None
        checkout_url: str | None = None

        if provider == PaymentProvider.STRIPE:
            payment = await self._stripe_checkout(total, user_id, order.reference)
            client_secret = payment["client_secret"]
            order.stripe_payment_intent_id = payment["stripe_intent_id"]
        elif provider == PaymentProvider.YOCO:
            payment = await self._yoco_checkout(total, order.id)
            checkout_url = payment["checkout_url"]
            order.external_payment_id = payment["external_id"]
        elif provider == PaymentProvider.PAYJUSTNOW:
            payment = await self._payjustnow_checkout(total, order.id, order.reference, order.shipping_name)
            checkout_url = payment["checkout_url"]
            order.external_payment_id = payment["external_id"]
        elif provider == PaymentProvider.PAYFLEX:
            payment = await self._payflex_checkout(total, order.id, order.shipping_name)
            checkout_url = payment["checkout_url"]
            order.external_payment_id = payment["external_id"]
        elif provider == PaymentProvider.HAPPYPAY:
            payment = await self._happypay_checkout(total, order.id, order.reference)
            checkout_url = payment["checkout_url"]
            order.external_payment_id = payment["external_id"]

        order = await self._repo.save(order)

        out = OrderOut.model_validate(order)
        await _emit_order(
            Event(
                event_type="order.created",
                entity_type="order",
                entity_id=order.id,
                actor_id=user_id,
                actor_type="customer",
                payload={
                    "reference": order.reference,
                    "status": order.status.value,
                    "total": str(order.total),
                    "item_count": len(order.items),
                    "shipping_city": order.shipping_city,
                    "payment_provider": provider.value,
                },
            )
        )
        return OrderCreatedOut(
            order=out,
            payment_provider=provider.value,
            client_secret=client_secret,
            checkout_url=checkout_url,
        )

    async def confirm_payment(self, stripe_payment_intent_id: str) -> None:
        """Called by Stripe webhook after successful payment — marks order as PAID."""
        from sqlalchemy import select
        from app.core.database import SessionLocal
        from app.features.orders.models import Order

        async with SessionLocal() as db:
            result = await db.execute(
                select(Order).where(Order.stripe_payment_intent_id == stripe_payment_intent_id)
            )
            order = result.scalar_one_or_none()
            if order and order.status == OrderStatus.PENDING_PAYMENT:
                order.status = OrderStatus.PAID
                await db.commit()
                await self._notify.send_order_confirmation(order)
                await self._notify.alert_admin_new_order(order)

    async def confirm_external_payment(self, external_payment_id: str) -> None:
        """Called by Yoco / PayJustNow / Payflex / HappyPay webhooks — marks order as PAID."""
        from sqlalchemy import select
        from app.core.database import SessionLocal
        from app.features.orders.models import Order

        async with SessionLocal() as db:
            result = await db.execute(
                select(Order).where(Order.external_payment_id == external_payment_id)
            )
            order = result.scalar_one_or_none()
            if order and order.status == OrderStatus.PENDING_PAYMENT:
                order.status = OrderStatus.PAID
                await db.commit()
                await self._notify.send_order_confirmation(order)
                await self._notify.alert_admin_new_order(order)

    async def get_order(self, order_id: int, user_id: int) -> OrderOut:
        order = await self._repo.get_by_id(order_id)
        if not order or order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return OrderOut.model_validate(order)

    async def list_my_orders(self, user_id: int, page: int = 1) -> OrderListOut:
        items, total = await self._repo.list_for_user(user_id, page=page)
        return OrderListOut(
            items=[OrderOut.model_validate(o) for o in items],
            total=total,
            page=page,
            page_size=20,
        )

    # ── Admin operations ──────────────────────────────────────────────────────

    async def admin_list_orders(
        self, page: int = 1, status: OrderStatus | None = None
    ) -> OrderListOut:
        items, total = await self._repo.list_all(page=page, status=status)
        return OrderListOut(
            items=[OrderOut.model_validate(o) for o in items],
            total=total,
            page=page,
            page_size=50,
        )

    async def admin_update_order(self, order_id: int, payload: AdminOrderUpdate) -> OrderOut:
        order = await self._repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        status_before = order.status
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(order, field, value)

        order = await self._repo.save(order)

        # Emit status change event if status changed
        if payload.status and payload.status != status_before:
            await _emit_order(
                Event(
                    event_type="order.status_changed",
                    entity_type="order",
                    entity_id=order.id,
                    actor_type="admin",
                    payload={
                        "reference": order.reference,
                        "status_from": status_before.value,
                        "status_to": order.status.value,
                        "total": str(order.total),
                    },
                )
            )

        # Notify customer on status transitions they care about
        if payload.status in {OrderStatus.SHIPPED, OrderStatus.DELIVERED}:
            await self._notify.send_order_status_update(order)

        return OrderOut.model_validate(order)
