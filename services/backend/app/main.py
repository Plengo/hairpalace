import logging
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.events import init_producer
from app.core.middleware import AccessLogMiddleware, RequestIDMiddleware
from app.features.admin.router import router as admin_router
from app.features.contact.router import router as contact_router
from app.features.products.router import router as products_router
from app.features.orders.router import router as orders_router
from app.features.users.router import router as users_router

settings = get_settings()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Start Kafka producer — won't crash if Redpanda is unavailable (tests/dev)
    producer = init_producer(settings.KAFKA_BOOTSTRAP_SERVERS)
    try:
        await producer.start()
    except Exception:  # pragma: no cover
        pass
    yield
    await producer.stop()


app = FastAPI(
    title="Hair Palace API",
    version="1.0.0",
    description="Premium hair & beauty — order-first marketplace",
    docs_url="/api/docs" if settings.APP_ENV != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

# ── Middleware (outermost first) ──────────────────────────────────────────────
app.add_middleware(AccessLogMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(users_router, prefix=PREFIX)
app.include_router(products_router, prefix=PREFIX)
app.include_router(orders_router, prefix=PREFIX)
app.include_router(admin_router, prefix=PREFIX)
app.include_router(contact_router, prefix=PREFIX)


@app.get("/health", tags=["Health"], include_in_schema=False)
async def health() -> dict:
    return {"status": "ok"}
