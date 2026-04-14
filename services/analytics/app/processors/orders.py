"""
Processes hp.orders events:
  order.created → EventLog + OrderLifecycle(status_from=None, status_to="pending_payment")
  order.status_changed → EventLog + OrderLifecycle(status_from=prev, status_to=new)
"""
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventLog, OrderLifecycle


async def process(event_data: dict, db: AsyncSession) -> None:
    payload = event_data.get("payload", {})
    event_type = event_data["event_type"]

    log = EventLog(
        event_id=event_data["event_id"],
        topic="hp.orders",
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

    lifecycle = OrderLifecycle(
        event_id=event_data["event_id"],
        order_id=event_data["entity_id"],
        order_reference=payload.get("reference", ""),
        customer_id=event_data.get("actor_id"),
        status_from=payload.get("status_from"),
        status_to=payload.get("status_to") or payload.get("status", ""),
        order_total=str(payload.get("total", "")),
        item_count=payload.get("item_count"),
    )
    db.add(lifecycle)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
