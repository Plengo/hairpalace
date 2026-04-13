from fastapi import HTTPException, status
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.products.models import Product, ProductCategory
from app.features.products.repository import ProductRepository
from app.features.products.schemas import ProductCreate, ProductListOut, ProductOut, ProductUpdate


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

    async def create_product(self, payload: ProductCreate) -> ProductOut:
        slug = slugify(payload.name)
        product = Product(slug=slug, **payload.model_dump())
        product = await self._repo.create(product)
        return ProductOut.model_validate(product)

    async def update_product(self, product_id: int, payload: ProductUpdate) -> ProductOut:
        product = await self._repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        product = await self._repo.save(product)
        return ProductOut.model_validate(product)
