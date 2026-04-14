"""
Order lifecycle — positive, negative, and edge-case coverage.
Stripe is mocked so tests remain deterministic and offline.
"""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token

AUTH_BASE = "/api/v1/auth"
PRODUCT_BASE = "/api/v1/products"
ORDER_BASE = "/api/v1/orders"

REGISTER_PAYLOAD = {
    "email": "buyer@strands.co.za",
    "password": "SecurePass123!",
    "full_name": "Buyer User",
}

PRODUCT_PAYLOAD = {
    "name": "Body Wave Bundles",
    "category": "hair_extensions",
    "price": "650.00",
    "lead_time_days": 3,
}

SHIPPING = {
    "name": "Buyer User",
    "address": "12 Long Street",
    "city": "Cape Town",
    "province": "Western Cape",
    "postal_code": "8001",
}


def _admin_headers() -> dict:
    token = create_access_token({"sub": "999", "is_admin": True})
    return {"Authorization": f"Bearer {token}"}


def _mock_stripe_intent(amount: int = 73000) -> MagicMock:
    """Returns a Stripe-like PaymentIntent mock with the minimal fields used."""
    intent = MagicMock()
    intent.id = "pi_test_abc123"
    intent.client_secret = "pi_test_abc123_secret_xyz"
    intent.amount = amount
    return intent


async def _create_product_and_register(client: AsyncClient) -> tuple[int, dict]:
    """Helper: seed one product + register a buyer, returns (product_id, auth_headers)."""
    create = await client.post(PRODUCT_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    product_id = create.json()["id"]

    await client.post(f"{AUTH_BASE}/register", json=REGISTER_PAYLOAD)
    login = await client.post(
        f"{AUTH_BASE}/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    token = login.json()["access_token"]
    return product_id, {"Authorization": f"Bearer {token}"}


# ── Positive ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient) -> None:
    product_id, headers = await _create_product_and_register(client)

    with patch("stripe.PaymentIntent.create", return_value=_mock_stripe_intent()):
        response = await client.post(
            ORDER_BASE,
            json={"items": [{"product_id": product_id, "quantity": 1}], "shipping": SHIPPING},
            headers=headers,
        )

    assert response.status_code == 201
    data = response.json()
    assert "order" in data
    assert data["order"]["status"] == "pending_payment"
    assert data["order"]["reference"].startswith("HP-")
    assert data["client_secret"] == "pi_test_abc123_secret_xyz"


@pytest.mark.asyncio
async def test_order_total_includes_shipping_fee(client: AsyncClient) -> None:
    """Total = product price + flat R80 shipping fee."""
    product_id, headers = await _create_product_and_register(client)

    with patch("stripe.PaymentIntent.create", return_value=_mock_stripe_intent()):
        response = await client.post(
            ORDER_BASE,
            json={"items": [{"product_id": product_id, "quantity": 1}], "shipping": SHIPPING},
            headers=headers,
        )

    order = response.json()["order"]
    assert Decimal(order["subtotal"]) == Decimal("650.00")
    assert Decimal(order["shipping_fee"]) == Decimal("80.00")
    assert Decimal(order["total"]) == Decimal("730.00")


@pytest.mark.asyncio
async def test_list_my_orders(client: AsyncClient) -> None:
    product_id, headers = await _create_product_and_register(client)

    with patch("stripe.PaymentIntent.create", return_value=_mock_stripe_intent()):
        await client.post(
            ORDER_BASE,
            json={"items": [{"product_id": product_id, "quantity": 1}], "shipping": SHIPPING},
            headers=headers,
        )

    response = await client.get(f"{ORDER_BASE}/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_get_my_order_by_id(client: AsyncClient) -> None:
    product_id, headers = await _create_product_and_register(client)

    with patch("stripe.PaymentIntent.create", return_value=_mock_stripe_intent()):
        create_resp = await client.post(
            ORDER_BASE,
            json={"items": [{"product_id": product_id, "quantity": 1}], "shipping": SHIPPING},
            headers=headers,
        )
    order_id = create_resp.json()["order"]["id"]

    response = await client.get(f"{ORDER_BASE}/me/{order_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == order_id


@pytest.mark.asyncio
async def test_admin_can_list_all_orders(client: AsyncClient) -> None:
    product_id, user_headers = await _create_product_and_register(client)

    with patch("stripe.PaymentIntent.create", return_value=_mock_stripe_intent()):
        await client.post(
            ORDER_BASE,
            json={"items": [{"product_id": product_id, "quantity": 1}], "shipping": SHIPPING},
            headers=user_headers,
        )

    response = await client.get(f"{ORDER_BASE}/admin", headers=_admin_headers())
    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_admin_can_update_order_status(client: AsyncClient) -> None:
    product_id, user_headers = await _create_product_and_register(client)

    with patch("stripe.PaymentIntent.create", return_value=_mock_stripe_intent()):
        create_resp = await client.post(
            ORDER_BASE,
            json={"items": [{"product_id": product_id, "quantity": 1}], "shipping": SHIPPING},
            headers=user_headers,
        )
    order_id = create_resp.json()["order"]["id"]

    response = await client.patch(
        f"{ORDER_BASE}/admin/{order_id}",
        json={"status": "sourcing", "admin_notes": "Buying stock from supplier."},
        headers=_admin_headers(),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "sourcing"


# ── Negative ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_unauthenticated_cannot_create_order(client: AsyncClient) -> None:
    response = await client.post(
        ORDER_BASE,
        json={"items": [{"product_id": 1, "quantity": 1}], "shipping": SHIPPING},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_order_with_nonexistent_product(client: AsyncClient) -> None:
    _, headers = await _create_product_and_register(client)

    with patch("stripe.PaymentIntent.create", return_value=_mock_stripe_intent()):
        response = await client.post(
            ORDER_BASE,
            json={"items": [{"product_id": 99999, "quantity": 1}], "shipping": SHIPPING},
            headers=headers,
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_user_cannot_see_another_users_order(client: AsyncClient) -> None:
    product_id, buyer_headers = await _create_product_and_register(client)

    with patch("stripe.PaymentIntent.create", return_value=_mock_stripe_intent()):
        create_resp = await client.post(
            ORDER_BASE,
            json={"items": [{"product_id": product_id, "quantity": 1}], "shipping": SHIPPING},
            headers=buyer_headers,
        )
    order_id = create_resp.json()["order"]["id"]

    # A second user with a different user_id in their token
    other_token = create_access_token({"sub": "8888", "is_admin": False})
    other_headers = {"Authorization": f"Bearer {other_token}"}
    response = await client.get(f"{ORDER_BASE}/me/{order_id}", headers=other_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_non_admin_cannot_access_admin_endpoint(client: AsyncClient) -> None:
    _, user_headers = await _create_product_and_register(client)
    response = await client.get(f"{ORDER_BASE}/admin", headers=user_headers)
    assert response.status_code == 403


# ── Edge cases ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_order_empty_items_rejected(client: AsyncClient) -> None:
    _, headers = await _create_product_and_register(client)
    response = await client.post(
        ORDER_BASE,
        json={"items": [], "shipping": SHIPPING},
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_order_quantity_zero_rejected(client: AsyncClient) -> None:
    product_id, headers = await _create_product_and_register(client)
    response = await client.post(
        ORDER_BASE,
        json={"items": [{"product_id": product_id, "quantity": 0}], "shipping": SHIPPING},
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_order_missing_shipping_rejected(client: AsyncClient) -> None:
    product_id, headers = await _create_product_and_register(client)
    response = await client.post(
        ORDER_BASE,
        json={"items": [{"product_id": product_id, "quantity": 1}]},
        headers=headers,
    )
    assert response.status_code == 422
