from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.features.products.models import ProductCategory
from app.features.products.schemas import ProductCreate, ProductListOut, ProductOut, ProductUpdate
from app.features.products.service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


def _service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


@router.get("", response_model=ProductListOut)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: ProductCategory | None = None,
    featured: bool = False,
    svc: ProductService = Depends(_service),
) -> ProductListOut:
    return await svc.list_products(page=page, page_size=page_size, category=category, featured_only=featured)


@router.get("/{slug}", response_model=ProductOut)
async def get_product(slug: str, svc: ProductService = Depends(_service)) -> ProductOut:
    return await svc.get_product_by_slug(slug)


# ── Admin-only mutations ──────────────────────────────────────────────────────

@router.post("", response_model=ProductOut, status_code=201)
async def create_product(
    payload: ProductCreate,
    _admin: int = Depends(require_admin),
    svc: ProductService = Depends(_service),
) -> ProductOut:
    return await svc.create_product(payload)


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    _admin: int = Depends(require_admin),
    svc: ProductService = Depends(_service),
) -> ProductOut:
    return await svc.update_product(product_id, payload)
