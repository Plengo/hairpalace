"""
Product CRUD — admin-gated mutations, public reads.
"""
import pytest
from httpx import AsyncClient

from app.core.security import create_access_token

BASE = "/api/v1/products"

PRODUCT_PAYLOAD = {
    "name": "Test Body Wave Bundles",
    "category": "hair_extensions",
    "price": "650.00",
    "lead_time_days": 3,
}


def _admin_headers() -> dict:
    token = create_access_token({"sub": "1", "is_admin": True})
    return {"Authorization": f"Bearer {token}"}


def _user_headers() -> dict:
    token = create_access_token({"sub": "2", "is_admin": False})
    return {"Authorization": f"Bearer {token}"}


# ── Positive ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_can_create_product(client: AsyncClient) -> None:
    response = await client.post(BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == PRODUCT_PAYLOAD["name"]
    assert "slug" in data


@pytest.mark.asyncio
async def test_public_can_list_products(client: AsyncClient) -> None:
    await client.post(BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    response = await client.get(BASE)
    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_get_product_by_slug(client: AsyncClient) -> None:
    create = await client.post(BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    slug = create.json()["slug"]
    response = await client.get(f"{BASE}/{slug}")
    assert response.status_code == 200
    assert response.json()["slug"] == slug


# ── Negative ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_non_admin_cannot_create_product(client: AsyncClient) -> None:
    response = await client.post(BASE, json=PRODUCT_PAYLOAD, headers=_user_headers())
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_nonexistent_product(client: AsyncClient) -> None:
    response = await client.get(f"{BASE}/does-not-exist")
    assert response.status_code == 404


# ── Edge cases ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_negative_price_rejected(client: AsyncClient) -> None:
    response = await client.post(
        BASE,
        json={**PRODUCT_PAYLOAD, "price": "-50.00"},
        headers=_admin_headers(),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_filter_by_category(client: AsyncClient) -> None:
    await client.post(BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    await client.post(
        BASE,
        json={**PRODUCT_PAYLOAD, "name": "Wig", "category": "wigs"},
        headers=_admin_headers(),
    )
    response = await client.get(f"{BASE}?category=wigs")
    assert response.status_code == 200
    assert response.json()["total"] == 1
