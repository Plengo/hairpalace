"""
Analytics database models — append-only, event-sourced tables.
No PII stored directly; user events only record entity_id, not email/name.
"""
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EventLog(Base):
    """
    Central ledger of every event consumed from Kafka.
    Idempotent on event_id — re-processing the same event is safe.
    """
    __tablename__ = "event_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_version: Mapped[int] = mapped_column(Integer, default=1)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actor_type: Mapped[str] = mapped_column(String(30), default="system")
    source_service: Mapped[str] = mapped_column(String(100), nullable=False)
    produced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    kafka_partition: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kafka_offset: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)


class ProductSnapshot(Base):
    """
    Point-in-time snapshot of a product whenever it changes.
    Enables full price/stock history for AI/analytics without joins.
    """
    __tablename__ = "product_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(300), nullable=False)
    product_slug: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[str] = mapped_column(String(20), nullable=False)   # stored as string to preserve precision
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_featured: Mapped[bool] = mapped_column(default=False)
    # created | updated | price_changed | stock_adjusted | deactivated
    change_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    changed_by_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    changed_by_type: Mapped[str] = mapped_column(String(30), default="system")
    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class OrderLifecycle(Base):
    """
    Records every status transition for an order.
    Used for funnel analytics, cohort analysis, and fulfilment SLAs.
    """
    __tablename__ = "order_lifecycle"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    order_reference: Mapped[str] = mapped_column(String(20), nullable=False)
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    status_from: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status_to: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    order_total: Mapped[str | None] = mapped_column(String(20), nullable=True)
    item_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    event_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class InventoryMovement(Base):
    """
    Delta-log of every stock adjustment.
    Enables stock reconciliation and shrinkage analysis.
    """
    __tablename__ = "inventory_movements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(300), nullable=False)
    stock_before: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_after: Mapped[int] = mapped_column(Integer, nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(300), nullable=False)
    adjusted_by_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    movement_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
