import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"   # awaiting payment confirmation
    PAID = "paid"                          # payment confirmed — triggers sourcing
    SOURCING = "sourcing"                  # owner is buying stock
    PROCESSING = "processing"             # stock acquired, preparing to ship
    SHIPPED = "shipped"                   # dispatched
    DELIVERED = "delivered"               # completed
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentProvider(str, enum.Enum):
    STRIPE = "stripe"
    YOCO = "yoco"
    PAYJUSTNOW = "payjustnow"
    PAYFLEX = "payflex"
    HAPPYPAY = "happypay"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reference: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="orders")

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT, nullable=False
    )

    payment_provider: Mapped[PaymentProvider] = mapped_column(
        Enum(PaymentProvider), default=PaymentProvider.STRIPE, nullable=False
    )

    # Stripe payment intent ID — used to confirm/capture
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(100))

    # Generic external payment ID — stores checkout ID from Yoco, PJN, Payflex, HappyPay
    external_payment_id: Mapped[str | None] = mapped_column(String(200))

    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    shipping_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Shipping address snapshot (denormalised for immutability after order)
    shipping_name: Mapped[str] = mapped_column(String(200), nullable=False)
    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)
    shipping_city: Mapped[str] = mapped_column(String(100), nullable=False)
    shipping_province: Mapped[str] = mapped_column(String(100), nullable=False)
    shipping_postal_code: Mapped[str] = mapped_column(String(20), nullable=False)

    # Admin notes (internal — order-first sourcing context)
    admin_notes: Mapped[str | None] = mapped_column(Text)
    tracking_number: Mapped[str | None] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Price snapshot — protects against future price changes
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


from app.features.users.models import User  # noqa: E402
from app.features.products.models import Product  # noqa: E402
