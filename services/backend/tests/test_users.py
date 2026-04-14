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


# ── Password reset ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_password_reset_request_always_returns_202(client: AsyncClient) -> None:
    """Returns 202 whether or not the email exists — prevents enumeration."""
    response = await client.post(
        f"{BASE}/password-reset/request",
        json={"email": "nonexistent@example.com"},
    )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_password_reset_confirm_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        f"{BASE}/password-reset/confirm",
        json={"token": "notavalidtoken", "new_password": "NewPassword123!"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_password_reset_full_flow(client: AsyncClient) -> None:
    """Register → request reset → confirm with valid token → login with new password."""
    from app.core.security import create_password_reset_token

    # Register
    reg = await client.post(f"{BASE}/register", json=VALID_USER)
    user_id = reg.json()["id"]

    # Generate a valid reset token the same way the service would
    token = create_password_reset_token({"sub": str(user_id)})

    # Confirm with new password
    confirm = await client.post(
        f"{BASE}/password-reset/confirm",
        json={"token": token, "new_password": "BrandNewPass999!"},
    )
    assert confirm.status_code == 200

    # Old password should no longer work
    old_login = await client.post(
        f"{BASE}/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    assert old_login.status_code == 401

    # New password should work
    new_login = await client.post(
        f"{BASE}/login",
        json={"email": VALID_USER["email"], "password": "BrandNewPass999!"},
    )
    assert new_login.status_code == 200
