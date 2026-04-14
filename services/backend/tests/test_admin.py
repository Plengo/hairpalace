"""
Admin API tests — stock management, admin product/order views, stats dashboard.
"""
import pytest
from httpx import AsyncClient

from app.core.security import create_access_token

PRODUCTS_BASE = "/api/v1/products"
ADMIN_BASE = "/api/v1/admin"

PRODUCT_PAYLOAD = {
    "name": "Brazilian Body Wave",
    "category": "hair_extensions",
    "price": "850.00",
    "lead_time_days": 4,
}


def _admin_headers() -> dict:
    token = create_access_token({"sub": "1", "is_admin": True})
    return {"Authorization": f"Bearer {token}"}


def _user_headers() -> dict:
    token = create_access_token({"sub": "2", "is_admin": False})
    return {"Authorization": f"Bearer {token}"}


# ── Admin product list (includes inactive) ────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_can_list_all_products_including_inactive(client: AsyncClient) -> None:
    # Create a product then soft-delete it
    res = await client.post(PRODUCTS_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    product_id = res.json()["id"]
    await client.delete(f"{PRODUCTS_BASE}/{product_id}", headers=_admin_headers())

    # Public endpoint should see 0 products
    public = await client.get(PRODUCTS_BASE)
    assert public.json()["total"] == 0

    # Admin endpoint should still see 1
    admin = await client.get(f"{ADMIN_BASE}/products", headers=_admin_headers())
    assert admin.status_code == 200
    assert admin.json()["total"] == 1


@pytest.mark.asyncio
async def test_non_admin_cannot_access_admin_products(client: AsyncClient) -> None:
    response = await client.get(f"{ADMIN_BASE}/products", headers=_user_headers())
    assert response.status_code == 403


# ── Stock adjustment ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_can_adjust_stock_positive_delta(client: AsyncClient) -> None:
    res = await client.post(PRODUCTS_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    product_id = res.json()["id"]
    assert res.json()["stock_quantity"] == 0

    adj = await client.patch(
        f"{PRODUCTS_BASE}/{product_id}/stock",
        json={"delta": 10, "reason": "Initial restock"},
        headers=_admin_headers(),
    )
    assert adj.status_code == 200
    assert adj.json()["stock_quantity"] == 10


@pytest.mark.asyncio
async def test_admin_can_adjust_stock_negative_delta(client: AsyncClient) -> None:
    res = await client.post(PRODUCTS_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    product_id = res.json()["id"]
    await client.patch(
        f"{PRODUCTS_BASE}/{product_id}/stock",
        json={"delta": 5, "reason": "Add stock"},
        headers=_admin_headers(),
    )
    adj = await client.patch(
        f"{PRODUCTS_BASE}/{product_id}/stock",
        json={"delta": -3, "reason": "Damaged items removed"},
        headers=_admin_headers(),
    )
    assert adj.status_code == 200
    assert adj.json()["stock_quantity"] == 2


@pytest.mark.asyncio
async def test_stock_adjustment_below_zero_is_rejected(client: AsyncClient) -> None:
    res = await client.post(PRODUCTS_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    product_id = res.json()["id"]
    adj = await client.patch(
        f"{PRODUCTS_BASE}/{product_id}/stock",
        json={"delta": -1, "reason": "Impossible adjustment"},
        headers=_admin_headers(),
    )
    assert adj.status_code == 400


@pytest.mark.asyncio
async def test_non_admin_cannot_adjust_stock(client: AsyncClient) -> None:
    res = await client.post(PRODUCTS_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    product_id = res.json()["id"]
    adj = await client.patch(
        f"{PRODUCTS_BASE}/{product_id}/stock",
        json={"delta": 5, "reason": "Attempt"},
        headers=_user_headers(),
    )
    assert adj.status_code == 403


# ── Soft delete ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_can_soft_delete_product(client: AsyncClient) -> None:
    res = await client.post(PRODUCTS_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    product_id = res.json()["id"]

    delete = await client.delete(f"{PRODUCTS_BASE}/{product_id}", headers=_admin_headers())
    assert delete.status_code == 200
    assert delete.json()["is_active"] is False

    # No longer visible on public endpoint
    slug = res.json()["slug"]
    public = await client.get(f"{PRODUCTS_BASE}/{slug}")
    assert public.status_code == 404


# ── Admin orders ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_can_list_all_orders(client: AsyncClient) -> None:
    response = await client.get(f"{ADMIN_BASE}/orders", headers=_admin_headers())
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_non_admin_cannot_list_admin_orders(client: AsyncClient) -> None:
    response = await client.get(f"{ADMIN_BASE}/orders", headers=_user_headers())
    assert response.status_code == 403


# ── Stats ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_stats_returns_correct_fields(client: AsyncClient) -> None:
    # Create a product so stats are non-trivial
    await client.post(PRODUCTS_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())

    response = await client.get(f"{ADMIN_BASE}/stats", headers=_admin_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["total_products"] == 1
    assert data["active_products"] == 1
    assert data["total_orders"] == 0
    assert "orders_by_status" in data


@pytest.mark.asyncio
async def test_non_admin_cannot_access_stats(client: AsyncClient) -> None:
    response = await client.get(f"{ADMIN_BASE}/stats", headers=_user_headers())
    assert response.status_code == 403
