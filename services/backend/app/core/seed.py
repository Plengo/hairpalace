"""
Seed script — populates the DB with demo products for development.
Run via: make seed
"""
import asyncio
from decimal import Decimal

from app.core.database import SessionLocal
from app.features.products.models import Product, ProductCategory, ProductImage
from app.features.users.models import User
from app.core.security import hash_password


SAMPLE_PRODUCTS = [
    {
        "name": "Brazilian Body Wave Bundles",
        "slug": "brazilian-body-wave-bundles",
        "description": "100% virgin human hair. Naturally wavy texture, soft and full.",
        "category": ProductCategory.HAIR_EXTENSIONS,
        "price": Decimal("850.00"),
        "is_featured": True,
        "lead_time_days": 3,
    },
    {
        "name": "Peruvian Straight Lace Wig 22\"",
        "slug": "peruvian-straight-lace-wig-22",
        "description": "Full lace, transparent HD lace. Pre-plucked hairline. 180% density.",
        "category": ProductCategory.WIGS,
        "price": Decimal("2200.00"),
        "is_featured": True,
        "lead_time_days": 5,
    },
    {
        "name": "Afro Kinky Braiding Hair",
        "slug": "afro-kinky-braiding-hair",
        "description": "Jumbo braid pack. Lightweight, tangle-free. Available in 8 colours.",
        "category": ProductCategory.BRAIDING_HAIR,
        "price": Decimal("120.00"),
        "is_featured": False,
        "lead_time_days": 2,
    },
    {
        "name": "Argan Oil Deep Moisture Treatment",
        "slug": "argan-oil-deep-moisture-treatment",
        "description": "Salon-grade deep conditioning masque. Repairs heat damage.",
        "category": ProductCategory.HAIR_CARE,
        "price": Decimal("180.00"),
        "is_featured": False,
        "lead_time_days": 2,
    },
]


async def seed() -> None:
    async with SessionLocal() as db:
        # Admin user
        admin = User(
            email="admin@strands.co.za",
            hashed_password=hash_password("ChangeMe123!"),
            full_name="STRANDS Admin",
            is_admin=True,
        )
        db.add(admin)

        for data in SAMPLE_PRODUCTS:
            product = Product(**data)
            product.images.append(
                ProductImage(
                    url=f"https://placehold.co/800x600?text={data['slug']}",
                    alt_text=data["name"],
                    is_primary=True,
                )
            )
            db.add(product)

        await db.commit()
        print("✓ Seed complete")


if __name__ == "__main__":
    asyncio.run(seed())
