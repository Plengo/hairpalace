import random
import string
from decimal import Decimal

import stripe
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.features.orders.models import Order, OrderItem, OrderStatus
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


def _generate_reference() -> str:
    """Short, human-readable order reference: STR-XXXXXX."""
    return "STR-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class OrderService:

    def __init__(self, db: AsyncSession) -> None:
        self._repo = OrderRepository(db)
        self._products = ProductRepository(db)
        self._notify = NotificationService()

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

        # Create Stripe PaymentIntent — charge upfront (owner needs funds to buy stock)
        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),   # Stripe uses cents
            currency="zar",
            metadata={"user_id": str(user_id)},
        )

        order = Order(
            reference=_generate_reference(),
            user_id=user_id,
            status=OrderStatus.PENDING_PAYMENT,
            stripe_payment_intent_id=intent.id,
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

        return OrderCreatedOut(
            order=OrderOut.model_validate(order),
            client_secret=intent.client_secret,
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

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(order, field, value)

        order = await self._repo.save(order)

        # Notify customer on status transitions they care about
        if payload.status in {OrderStatus.SHIPPED, OrderStatus.DELIVERED}:
            await self._notify.send_order_status_update(order)

        return OrderOut.model_validate(order)
