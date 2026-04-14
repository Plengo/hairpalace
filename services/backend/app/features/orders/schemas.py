from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.features.orders.models import OrderStatus, PaymentProvider


class CartItemIn(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1, le=50)


class ShippingAddressIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    address: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2, max_length=100)
    province: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=4, max_length=20)


class OrderCreateIn(BaseModel):
    items: list[CartItemIn] = Field(..., min_length=1)
    shipping: ShippingAddressIn
    payment_provider: PaymentProvider = PaymentProvider.STRIPE


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    status: OrderStatus
    payment_provider: PaymentProvider
    subtotal: Decimal
    shipping_fee: Decimal
    total: Decimal
    shipping_name: str
    shipping_address: str
    shipping_city: str
    shipping_province: str
    shipping_postal_code: str
    tracking_number: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut]


class OrderCreatedOut(BaseModel):
    order: OrderOut
    payment_provider: str
    # Stripe: pass to Stripe Elements on the frontend
    client_secret: str | None = None
    # All other providers: redirect the browser here to complete payment
    checkout_url: str | None = None


class AdminOrderUpdate(BaseModel):
    status: OrderStatus | None = None
    admin_notes: str | None = None
    tracking_number: str | None = None


class OrderListOut(BaseModel):
    items: list[OrderOut]
    total: int
    page: int
    page_size: int
