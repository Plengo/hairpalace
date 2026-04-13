"""
User registration and login — positive, negative, and edge-case coverage.
"""
import pytest
from httpx import AsyncClient

BASE = "/api/v1/auth"

VALID_USER = {
    "email": "test@strands.co.za",
    "password": "SecurePass123!",
    "full_name": "Test User",
}


# ── Positive ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    response = await client.post(f"{BASE}/register", json=VALID_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == VALID_USER["email"]
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await client.post(f"{BASE}/register", json=VALID_USER)
    response = await client.post(
        f"{BASE}/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_profile_authenticated(client: AsyncClient) -> None:
    await client.post(f"{BASE}/register", json=VALID_USER)
    login = await client.post(
        f"{BASE}/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    token = login.json()["access_token"]
    response = await client.get(f"{BASE}/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == VALID_USER["email"]


# ── Negative ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post(f"{BASE}/register", json=VALID_USER)
    response = await client.post(f"{BASE}/register", json=VALID_USER)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(f"{BASE}/register", json=VALID_USER)
    response = await client.post(
        f"{BASE}/login",
        json={"email": VALID_USER["email"], "password": "WrongPassword!"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client: AsyncClient) -> None:
    response = await client.get(f"{BASE}/me")
    assert response.status_code == 403  # HTTPBearer returns 403 when no token


# ── Edge cases ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_password_too_short(client: AsyncClient) -> None:
    response = await client.post(
        f"{BASE}/register",
        json={**VALID_USER, "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        f"{BASE}/register",
        json={**VALID_USER, "email": "not-an-email"},
    )
    assert response.status_code == 422
