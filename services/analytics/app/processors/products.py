"""
Processes hp.products events:
  product.created → EventLog + ProductSnapshot(change_type="created")
  product.updated → EventLog + ProductSnapshot(change_type="updated" | "price_changed")
  product.deactivated → EventLog + ProductSnapshot(change_type="deactivated")
"""
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventLog, ProductSnapshot


async def process(event_data: dict, db: AsyncSession) -> None:
    payload = event_data.get("payload", {})
    snapshot_data = payload if "id" in payload else payload.get("snapshot", payload)

    event_type = event_data["event_type"]
    change_type = {
        "product.created": "created",
        "product.updated": "updated",
        "product.deactivated": "deactivated",
    }.get(event_type, "updated")

    log = EventLog(
        event_id=event_data["event_id"],
        topic="hp.products",
        event_type=event_type,
        event_version=event_data.get("event_version", 1),
        entity_type=event_data["entity_type"],
        entity_id=event_data["entity_id"],
        actor_id=event_data.get("actor_id"),
        actor_type=event_data.get("actor_type", "system"),
        source_service=event_data.get("source_service", "hairpalace-backend"),
        produced_at=datetime.fromisoformat(event_data["produced_at"]),
        payload=payload,
    )
    db.add(log)

    snapshot = ProductSnapshot(
        event_id=event_data["event_id"],
        product_id=snapshot_data.get("id", event_data["entity_id"]),
        product_name=snapshot_data.get("name", ""),
        product_slug=snapshot_data.get("slug", ""),
        category=snapshot_data.get("category", ""),
        price=str(snapshot_data.get("price", "0")),
        stock_quantity=snapshot_data.get("stock_quantity", 0),
        is_active=snapshot_data.get("is_active", True),
        is_featured=snapshot_data.get("is_featured", False),
        change_type=change_type,
        changed_by_id=event_data.get("actor_id"),
        changed_by_type=event_data.get("actor_type", "system"),
    )
    db.add(snapshot)

    try:
        await db.commit()
    except IntegrityError:
        # Duplicate event_id — safe to ignore (idempotent consumption)
        await db.rollback()
