from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.features.products.models import ProductCategory


class ProductImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    alt_text: str | None
    is_primary: bool


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    category: ProductCategory
    price: Decimal
    stock_quantity: int
    is_active: bool
    is_featured: bool
    lead_time_days: int
    images: list[ProductImageOut]


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    category: ProductCategory
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    is_featured: bool = False
    lead_time_days: int = Field(default=3, ge=1, le=30)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    category: ProductCategory | None = None
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    is_featured: bool | None = None
    lead_time_days: int | None = Field(default=None, ge=1, le=30)


class StockAdjustIn(BaseModel):
    """Delta-based stock adjustment — positive adds, negative reduces."""
    delta: int = Field(..., description="Units to add (positive) or remove (negative)")
    reason: str = Field(..., min_length=3, max_length=200)


class StockAdjustOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stock_quantity: int


class ProductListOut(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
