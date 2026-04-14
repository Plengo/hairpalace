"""
Contact form endpoint — positive and validation tests.
"""
import pytest
from httpx import AsyncClient

BASE = "/api/v1/contact"

VALID_CONTACT = {
    "name": "Thabo Nkosi",
    "email": "thabo@example.com",
    "message": "Hi, I'd like to know when the Brazilian bundles are back in stock.",
}


# ── Positive ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_contact_form_returns_202(client: AsyncClient) -> None:
    response = await client.post(BASE, json=VALID_CONTACT)
    assert response.status_code == 202
    assert "detail" in response.json()


# ── Validation ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_contact_form_rejects_short_message(client: AsyncClient) -> None:
    response = await client.post(BASE, json={**VALID_CONTACT, "message": "Short"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_contact_form_rejects_invalid_email(client: AsyncClient) -> None:
    response = await client.post(BASE, json={**VALID_CONTACT, "email": "not-valid"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_contact_form_rejects_short_name(client: AsyncClient) -> None:
    response = await client.post(BASE, json={**VALID_CONTACT, "name": "X"})
    assert response.status_code == 422
