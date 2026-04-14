"""
Analytics consumer — subscribes to all hp.* topics and routes events to processors.
Starts from earliest offset so a fresh deployment catches up on all historical events.
Graceful shutdown on SIGTERM / SIGINT.
"""
import asyncio
import json
import logging
import signal

from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import Base, SessionLocal, _ensure_engine, engine
from app.processors import inventory, orders, products, users

logger = logging.getLogger("hairpalace.analytics.consumer")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")

_TOPIC_PROCESSORS = {
    "hp.products": products.process,
    "hp.orders": orders.process,
    "hp.inventory": inventory.process,
    "hp.users": users.process,
}


async def _process_message(msg, db: AsyncSession) -> None:
    try:
        event_data = json.loads(msg.value) if isinstance(msg.value, bytes) else msg.value
        processor = _TOPIC_PROCESSORS.get(msg.topic)
        if processor:
            await processor(event_data, db)
        else:
            logger.warning("No processor for topic %s", msg.topic)
    except Exception:
        logger.exception("Failed to process message from %s offset=%s", msg.topic, msg.offset)


async def consume() -> None:
    settings = get_settings()
    _ensure_engine()

    # Create analytics tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Analytics tables ready")

    consumer = AIOKafkaConsumer(
        *settings.topics,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="hairpalace-analytics",
        value_deserializer=lambda m: m,   # raw bytes — we decode per-message
        auto_offset_reset="earliest",
    )
    await consumer.start()
    logger.info("Consumer started — subscribed to %s", settings.topics)

    loop = asyncio.get_running_loop()
    stop = asyncio.Event()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    try:
        while not stop.is_set():
            # Poll with a short timeout so we can check stop flag
            batch = await consumer.getmany(timeout_ms=500)
            for _tp, messages in batch.items():
                for msg in messages:
                    async with SessionLocal() as db:
                        await _process_message(msg, db)
    finally:
        await consumer.stop()
        logger.info("Consumer stopped")


if __name__ == "__main__":
    asyncio.run(consume())
