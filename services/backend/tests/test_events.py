"""
Event system tests — verifies the Event dataclass structure and that
service operations correctly call the Kafka producer without blocking
business logic when the producer is unavailable.
"""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.events import (
    Event,
    TOPIC_INVENTORY,
    TOPIC_ORDERS,
    TOPIC_PRODUCTS,
    EventProducer,
)
from app.core.security import create_access_token

PRODUCTS_BASE = "/api/v1/products"

PRODUCT_PAYLOAD = {
    "name": "HD Lace Front Wig",
    "category": "wigs",
    "price": "1299.00",
    "lead_time_days": 5,
}


def _admin_headers() -> dict:
    token = create_access_token({"sub": "1", "is_admin": True})
    return {"Authorization": f"Bearer {token}"}


# ── Event dataclass ───────────────────────────────────────────────────────────

def test_event_has_required_fields():
    event = Event(
        event_type="product.created",
        entity_type="product",
        entity_id=1,
        payload={"name": "Test"},
    )
    assert event.event_type == "product.created"
    assert event.entity_type == "product"
    assert event.entity_id == 1
    assert event.source_service == "hairpalace-backend"
    assert event.event_version == 1
    assert event.actor_type == "system"


def test_event_auto_generates_event_id_and_produced_at():
    e1 = Event(event_type="x", entity_type="y", entity_id=1, payload={})
    e2 = Event(event_type="x", entity_type="y", entity_id=1, payload={})
    assert e1.event_id != e2.event_id
    # produced_at should be parseable as ISO datetime
    dt = datetime.fromisoformat(e1.produced_at)
    assert dt is not None


def test_event_to_dict_is_json_serialisable():
    event = Event(event_type="order.created", entity_type="order", entity_id=10, payload={"ref": "HP-ABC"})
    d = event.to_dict()
    assert d["event_type"] == "order.created"
    assert d["payload"]["ref"] == "HP-ABC"
    assert "event_id" in d
    assert "produced_at" in d


# ── Producer resilience ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_emit_failure_does_not_raise():
    """If the Kafka broker is down, emit must swallow the error silently."""
    producer = EventProducer("localhost:9999")
    # Inject a mock internal producer that raises on send_and_wait
    mock_inner = AsyncMock()
    mock_inner.send_and_wait.side_effect = ConnectionError("broker unavailable")
    producer._producer = mock_inner

    event = Event(event_type="product.created", entity_type="product", entity_id=1, payload={})
    # Should not raise
    await producer.emit(TOPIC_PRODUCTS, event)


@pytest.mark.asyncio
async def test_emit_no_op_when_producer_not_started():
    producer = EventProducer("localhost:9999")
    # _producer is None (never started)
    event = Event(event_type="product.created", entity_type="product", entity_id=1, payload={})
    await producer.emit(TOPIC_PRODUCTS, event)   # must not raise


# ── Product service emits events ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_product_emits_product_created_event(client: AsyncClient):
    mock_producer = MagicMock()
    mock_producer.emit = AsyncMock()

    with patch("app.features.products.service.get_producer", return_value=mock_producer):
        response = await client.post(PRODUCTS_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
        assert response.status_code == 201

    mock_producer.emit.assert_awaited_once()
    call_args = mock_producer.emit.call_args
    topic = call_args[0][0]
    event = call_args[0][1]
    assert topic == TOPIC_PRODUCTS
    assert event.event_type == "product.created"
    assert event.actor_type == "admin"


@pytest.mark.asyncio
async def test_adjust_stock_emits_inventory_event(client: AsyncClient):
    create = await client.post(PRODUCTS_BASE, json=PRODUCT_PAYLOAD, headers=_admin_headers())
    product_id = create.json()["id"]

    mock_producer = MagicMock()
    mock_producer.emit = AsyncMock()

    with patch("app.features.products.service.get_producer", return_value=mock_producer):
        response = await client.patch(
            f"{PRODUCTS_BASE}/{product_id}/stock",
            json={"delta": 5, "reason": "Restock"},
            headers=_admin_headers(),
        )
        assert response.status_code == 200

    mock_producer.emit.assert_awaited_once()
    call_args = mock_producer.emit.call_args
    topic = call_args[0][0]
    event = call_args[0][1]
    assert topic == TOPIC_INVENTORY
    assert event.event_type == "product.stock_adjusted"
    assert event.payload["delta"] == 5
