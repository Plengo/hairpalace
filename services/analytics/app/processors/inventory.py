"""
Processes hp.inventory events:
  product.stock_adjusted → EventLog + InventoryMovement
"""
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventLog, InventoryMovement


async def process(event_data: dict, db: AsyncSession) -> None:
    payload = event_data.get("payload", {})

    log = EventLog(
        event_id=event_data["event_id"],
        topic="hp.inventory",
        event_type=event_data["event_type"],
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

    movement = InventoryMovement(
        event_id=event_data["event_id"],
        product_id=event_data["entity_id"],
        product_name=payload.get("product_name", ""),
        stock_before=payload.get("stock_before", 0),
        stock_after=payload.get("stock_after", 0),
        delta=payload.get("delta", 0),
        reason=payload.get("reason", ""),
        adjusted_by_id=event_data.get("actor_id"),
    )
    db.add(movement)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
