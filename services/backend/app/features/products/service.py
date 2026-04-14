from fastapi import HTTPException, status
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import (
    Event,
    TOPIC_INVENTORY,
    TOPIC_PRODUCTS,
    get_producer,
)
from app.features.products.models import Product, ProductCategory
from app.features.products.repository import ProductRepository
from app.features.products.schemas import (
    ProductCreate,
    ProductListOut,
    ProductOut,
    ProductUpdate,
    StockAdjustOut,
)


async def _emit(topic: str, event: Event) -> None:
    producer = get_producer()
    if producer:
        await producer.emit(topic, event, key=str(event.entity_id))


class ProductService:

    def __init__(self, db: AsyncSession) -> None:
        self._repo = ProductRepository(db)

    async def get_product(self, product_id: int) -> ProductOut:
        product = await self._repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return ProductOut.model_validate(product)

    async def get_product_by_slug(self, slug: str) -> ProductOut:
        product = await self._repo.get_by_slug(slug)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return ProductOut.model_validate(product)

    async def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        category: ProductCategory | None = None,
        featured_only: bool = False,
    ) -> ProductListOut:
        items, total = await self._repo.list(
            page=page, page_size=page_size, category=category, featured_only=featured_only
        )
        return ProductListOut(
            items=[ProductOut.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def admin_list_all(
        self,
        page: int = 1,
        page_size: int = 50,
    ) -> ProductListOut:
        """Admin-only: returns all products, including inactive ones."""
        items, total = await self._repo.list(
            page=page, page_size=page_size, active_only=False
        )
        return ProductListOut(
            items=[ProductOut.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def create_product(
        self, payload: ProductCreate, actor_id: int | None = None
    ) -> ProductOut:
        slug = slugify(payload.name)
        product = Product(slug=slug, **payload.model_dump())
        product = await self._repo.create(product)
        out = ProductOut.model_validate(product)
        await _emit(
            TOPIC_PRODUCTS,
            Event(
                event_type="product.created",
                entity_type="product",
                entity_id=product.id,
                actor_id=actor_id,
                actor_type="admin" if actor_id else "system",
                payload=out.model_dump(mode="json"),
            ),
        )
        return out

    async def update_product(
        self, product_id: int, payload: ProductUpdate, actor_id: int | None = None
    ) -> ProductOut:
        product = await self._repo.get_by_id(product_id, active_only=False)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(product, field, value)

        product = await self._repo.save(product)
        out = ProductOut.model_validate(product)
        await _emit(
            TOPIC_PRODUCTS,
            Event(
                event_type="product.updated",
                entity_type="product",
                entity_id=product.id,
                actor_id=actor_id,
                actor_type="admin" if actor_id else "system",
                payload={"changes": changes, "snapshot": out.model_dump(mode="json")},
            ),
        )
        return out

    async def adjust_stock(
        self,
        product_id: int,
        delta: int,
        reason: str,
        actor_id: int | None = None,
    ) -> StockAdjustOut:
        product = await self._repo.get_by_id(product_id, active_only=False)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        stock_before = product.stock_quantity
        new_qty = stock_before + delta
        if new_qty < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Adjustment would result in negative stock ({new_qty})",
            )
        product.stock_quantity = new_qty
        product = await self._repo.save(product)
        await _emit(
            TOPIC_INVENTORY,
            Event(
                event_type="product.stock_adjusted",
                entity_type="product",
                entity_id=product.id,
                actor_id=actor_id,
                actor_type="admin" if actor_id else "system",
                payload={
                    "product_name": product.name,
                    "product_slug": product.slug,
                    "stock_before": stock_before,
                    "stock_after": product.stock_quantity,
                    "delta": delta,
                    "reason": reason,
                },
            ),
        )
        return StockAdjustOut.model_validate(product)

    async def soft_delete(self, product_id: int, actor_id: int | None = None) -> ProductOut:
        product = await self._repo.get_by_id(product_id, active_only=False)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        product.is_active = False
        product = await self._repo.save(product)
        out = ProductOut.model_validate(product)
        await _emit(
            TOPIC_PRODUCTS,
            Event(
                event_type="product.deactivated",
                entity_type="product",
                entity_id=product.id,
                actor_id=actor_id,
                actor_type="admin" if actor_id else "system",
                payload=out.model_dump(mode="json"),
            ),
        )
        return out
