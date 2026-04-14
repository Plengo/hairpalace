"""
Processes hp.users events — EventLog only (no PII stored).
user.registered, user.login, user.password_reset_requested
"""
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventLog


async def process(event_data: dict, db: AsyncSession) -> None:
    # Deliberately strip payload to avoid PII leaking into analytics DB.
    # We only record that an event happened for a user entity_id.
    log = EventLog(
        event_id=event_data["event_id"],
        topic="hp.users",
        event_type=event_data["event_type"],
        event_version=event_data.get("event_version", 1),
        entity_type=event_data["entity_type"],
        entity_id=event_data["entity_id"],
        actor_id=event_data.get("actor_id"),
        actor_type=event_data.get("actor_type", "customer"),
        source_service=event_data.get("source_service", "hairpalace-backend"),
        produced_at=datetime.fromisoformat(event_data["produced_at"]),
        payload={},  # intentionally empty — no PII
    )
    db.add(log)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
