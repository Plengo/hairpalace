"""
Tests for analytics event processors.
Each test inserts a synthetic event dict and asserts the correct DB rows are created.
"""
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models import EventLog, InventoryMovement, OrderLifecycle, ProductSnapshot
from app.processors import inventory, orders, products, users

pytestmark = pytest.mark.asyncio

NOW = datetime.now(timezone.utc).isoformat()


def _base_event(**overrides) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "product.created",
        "event_version": 1,
        "entity_type": "product",
        "entity_id": 42,
        "actor_id": 1,
        "actor_type": "admin",
        "source_service": "hairpalace-backend",
        "produced_at": NOW,
        "payload": {},
        **overrides,
    }


# ── Products ──────────────────────────────────────────────────────────────────

async def test_product_created_writes_event_log_and_snapshot(db):
    event = _base_event(
        event_type="product.created",
        entity_type="product",
        entity_id=10,
        payload={
            "id": 10,
            "name": "Test Wig",
            "slug": "test-wig",
            "category": "wigs",
            "price": "850.00",
            "stock_quantity": 5,
            "is_active": True,
            "is_featured": False,
        },
    )
    await products.process(event, db)

    logs = (await db.execute(select(EventLog))).scalars().all()
    assert len(logs) == 1
    assert logs[0].event_type == "product.created"
    assert logs[0].entity_id == 10

    snaps = (await db.execute(select(ProductSnapshot))).scalars().all()
    assert len(snaps) == 1
    assert snaps[0].product_id == 10
    assert snaps[0].change_type == "created"
    assert snaps[0].stock_quantity == 5
    assert snaps[0].price == "850.00"


async def test_product_deactivated_sets_change_type(db):
    event = _base_event(
        event_type="product.deactivated",
        entity_id=11,
        payload={"id": 11, "name": "Old Wig", "slug": "old-wig", "category": "wigs",
                 "price": "500.00", "stock_quantity": 0, "is_active": False, "is_featured": False},
    )
    await products.process(event, db)
    snap = (await db.execute(select(ProductSnapshot))).scalar_one()
    assert snap.change_type == "deactivated"
    assert snap.is_active is False


async def test_duplicate_product_event_is_idempotent(db):
    event_id = str(uuid.uuid4())
    event = _base_event(event_id=event_id, entity_id=12, payload={"id": 12, "name": "X", "slug": "x",
                        "category": "wigs", "price": "100.00", "stock_quantity": 0,
                        "is_active": True, "is_featured": False})
    await products.process(event, db)
    await products.process(event, db)  # replay — must not raise or duplicate
    count = (await db.execute(select(EventLog))).scalars()
    assert len(list(count)) == 1


# ── Orders ────────────────────────────────────────────────────────────────────

async def test_order_created_writes_event_log_and_lifecycle(db):
    event = _base_event(
        event_type="order.created",
        entity_type="order",
        entity_id=99,
        actor_type="customer",
        payload={"reference": "HP-TEST01", "status": "pending_payment",
                 "total": "1280.00", "item_count": 2, "shipping_city": "Cape Town"},
    )
    await orders.process(event, db)

    logs = (await db.execute(select(EventLog))).scalars().all()
    assert len(logs) == 1

    lc = (await db.execute(select(OrderLifecycle))).scalar_one()
    assert lc.order_id == 99
    assert lc.order_reference == "HP-TEST01"
    assert lc.status_to == "pending_payment"
    assert lc.status_from is None


async def test_order_status_changed_records_transition(db):
    event = _base_event(
        event_type="order.status_changed",
        entity_type="order",
        entity_id=100,
        actor_type="admin",
        payload={"reference": "HP-TEST02", "status_from": "paid",
                 "status_to": "shipped", "total": "850.00"},
    )
    await orders.process(event, db)
    lc = (await db.execute(select(OrderLifecycle))).scalar_one()
    assert lc.status_from == "paid"
    assert lc.status_to == "shipped"


# ── Inventory ─────────────────────────────────────────────────────────────────

async def test_inventory_event_writes_movement_and_event_log(db):
    event = _base_event(
        event_type="product.stock_adjusted",
        entity_type="product",
        entity_id=5,
        payload={"product_name": "Long Straight Wig", "product_slug": "long-straight-wig",
                 "stock_before": 3, "stock_after": 10, "delta": 7, "reason": "Restock delivery"},
    )
    await inventory.process(event, db)

    logs = (await db.execute(select(EventLog))).scalars().all()
    assert len(logs) == 1

    mv = (await db.execute(select(InventoryMovement))).scalar_one()
    assert mv.product_id == 5
    assert mv.delta == 7
    assert mv.stock_before == 3
    assert mv.stock_after == 10
    assert mv.reason == "Restock delivery"


# ── Users (no PII) ────────────────────────────────────────────────────────────

async def test_user_event_writes_event_log_with_empty_payload(db):
    event = _base_event(
        event_type="user.registered",
        entity_type="user",
        entity_id=55,
        actor_type="customer",
        payload={"email": "user@example.com", "name": "Alice"},  # processor must strip this
    )
    await users.process(event, db)

    log = (await db.execute(select(EventLog))).scalar_one()
    assert log.event_type == "user.registered"
    assert log.entity_id == 55
    assert log.payload == {}  # PII stripped

    # No secondary table rows for user events
    snaps = (await db.execute(select(ProductSnapshot))).scalars().all()
    assert len(snaps) == 0
