import enum
from decimal import Decimal

from sqlalchemy import Boolean, Enum, Integer, Numeric, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductCategory(str, enum.Enum):
    HAIR_EXTENSIONS = "hair_extensions"
    WIGS = "wigs"
    BRAIDING_HAIR = "braiding_hair"
    HAIR_CARE = "hair_care"
    STYLING_TOOLS = "styling_tools"
    ACCESSORIES = "accessories"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Sourcing disclaimer — shown at checkout (order-first model)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=3)

    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(200))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped["Product"] = relationship(back_populates="images")


# Avoid circular imports — resolved at model collection time
from app.features.orders.models import OrderItem  # noqa: E402
