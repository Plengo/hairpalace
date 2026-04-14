"""
Kafka event producer — all domain events flow through here.
Fire-and-forget design: emission failures never break business logic.
Topic naming: hp.<domain> (products / orders / inventory / users)
"""
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("hairpalace.events")

# ── Topic constants ───────────────────────────────────────────────────────────
TOPIC_PRODUCTS = "hp.products"
TOPIC_ORDERS = "hp.orders"
TOPIC_INVENTORY = "hp.inventory"
TOPIC_USERS = "hp.users"


# ── Canonical event envelope ─────────────────────────────────────────────────
@dataclass
class Event:
    event_type: str                          # e.g. "product.created"
    entity_type: str                         # e.g. "product"
    entity_id: int                           # DB primary key of the affected entity
    payload: dict[str, Any]                  # domain-specific data

    # Optional actor context (populated when triggered by a user action)
    actor_id: int | None = None
    actor_type: str = "system"               # system | admin | customer

    # Auto-generated metadata
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_version: int = 1
    source_service: str = "hairpalace-backend"
    produced_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Producer ──────────────────────────────────────────────────────────────────
class EventProducer:
    """Async aiokafka producer — singleton managed by app lifespan."""

    def __init__(self, bootstrap_servers: str) -> None:
        self._bootstrap = bootstrap_servers
        self._producer = None

    async def start(self) -> None:
        # Import here so the module loads cleanly even when aiokafka isn't
        # available (unit-test environments that mock the producer).
        from aiokafka import AIOKafkaProducer

        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap,
            value_serializer=lambda v: json.dumps(v).encode(),
            key_serializer=lambda k: k.encode() if k else None,
        )
        await self._producer.start()
        logger.info("Kafka producer connected → %s", self._bootstrap)

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def emit(self, topic: str, event: Event, key: str | None = None) -> None:
        """Send event to Kafka. Swallows all exceptions — never breaks callers."""
        if not self._producer:
            logger.debug("Producer not started — skipping %s", event.event_type)
            return
        try:
            await self._producer.send_and_wait(
                topic, value=event.to_dict(), key=key
            )
        except Exception as exc:
            logger.exception("Kafka emit failed [%s]: %s", event.event_type, exc)


# ── Global singleton (initialised by app lifespan) ───────────────────────────
_producer: EventProducer | None = None


def init_producer(bootstrap_servers: str) -> EventProducer:
    global _producer
    _producer = EventProducer(bootstrap_servers)
    return _producer


def get_producer() -> EventProducer | None:
    return _producer
