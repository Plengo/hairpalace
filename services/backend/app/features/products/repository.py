from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.products.models import Product, ProductImage, ProductCategory


class ProductRepository:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, product_id: int, active_only: bool = True) -> Product | None:
        q = (
            select(Product)
            .options(selectinload(Product.images))
            .where(Product.id == product_id)
        )
        if active_only:
            q = q.where(Product.is_active == True)  # noqa: E712
        result = await self._db.execute(q)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Product | None:
        result = await self._db.execute(
            select(Product)
            .options(selectinload(Product.images))
            .where(Product.slug == slug, Product.is_active == True)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        category: ProductCategory | None = None,
        featured_only: bool = False,
        active_only: bool = True,
    ) -> tuple[list[Product], int]:
        query = select(Product).options(selectinload(Product.images))
        if active_only:
            query = query.where(Product.is_active == True)  # noqa: E712

        if category:
            query = query.where(Product.category == category)
        if featured_only:
            query = query.where(Product.is_featured == True)  # noqa: E712

        total_result = await self._db.execute(select(func.count()).select_from(query.subquery()))
        total: int = total_result.scalar_one()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self._db.execute(query)
        return result.scalars().all(), total

    async def create(self, product: Product) -> Product:
        self._db.add(product)
        await self._db.flush()
        # Eagerly load images so model_validate doesn't trigger async IO synchronously
        await self._db.refresh(product, attribute_names=["images"])
        return product

    async def save(self, product: Product) -> Product:
        await self._db.flush()
        await self._db.refresh(product, attribute_names=["images"])
        return product
