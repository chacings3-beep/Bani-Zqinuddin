from fastapi import APIRouter

from lib.db import db
from models.catalog import (
    CatalogResponse,
    PaymentMethod,
    Pricing,
    ProductColor,
    ProductSize,
    ProductSleeve,
    PricingUpdate,
)

router = APIRouter()

PRODUCT_IMAGES = {
    "hitam_pendek": "https://images.unsplash.com/photo-1610502778270-c5c6f4c7d575?auto=format&fit=crop&w=900&q=85",
    "hitam_panjang": "https://images.unsplash.com/photo-1618354691551-44de113f0164?auto=format&fit=crop&w=900&q=85",
    "putih_pendek": "https://images.unsplash.com/photo-1651761179569-4ba2aa054997?auto=format&fit=crop&w=900&q=85",
    "putih_panjang": "https://images.unsplash.com/photo-1671438118257-cefa6c86fd50?auto=format&fit=crop&w=900&q=85",
}


def default_pricing() -> Pricing:
    return Pricing()


async def get_current_pricing() -> Pricing:
    stored = await db.settings.find_one({"key": "pricing"})
    return Pricing(**stored["value"]) if stored else default_pricing()


def build_catalog(pricing: Pricing) -> CatalogResponse:
    return CatalogResponse(
        product_name="Kaos Bani Zainuddin",
        colors=[
            ProductColor(id="hitam", label="Hitam", hex="#09090B"),
            ProductColor(id="putih", label="Putih", hex="#FFFFFF"),
        ],
        sleeves=[
            ProductSleeve(id="pendek", label="Lengan Pendek"),
            ProductSleeve(id="panjang", label="Lengan Panjang", extra_price=pricing.long_sleeve_extra),
        ],
        sizes=[
            ProductSize(id="anak", label="Anak-anak", category="Anak", extra_price=pricing.child_price - pricing.base_price),
            ProductSize(id="S", label="S", category="Dewasa"),
            ProductSize(id="M", label="M", category="Dewasa"),
            ProductSize(id="L", label="L", category="Dewasa"),
            ProductSize(id="XL", label="XL", category="Dewasa"),
            ProductSize(id="XXL", label="XXL", category="Jumbo", extra_price=pricing.xxl_extra),
            ProductSize(id="XXXL", label="XXXL", category="Jumbo", extra_price=pricing.xxxl_extra),
        ],
        pricing=pricing,
        payment_methods=[
            PaymentMethod(
                id="transfer",
                title="Transfer Bank",
                badge="Direkomendasikan",
                description="Transfer manual ke salah satu rekening panitia.",
                accounts=[
                    {"bank": "BCA", "account_number": "8720192834", "account_name": "Panitia Bani Zainuddin"},
                    {"bank": "Mandiri", "account_number": "1370009823124", "account_name": "Panitia Bani Zainuddin"},
                ],
            ),
            PaymentMethod(
                id="cod",
                title="Cash on Delivery",
                badge="Bayar di tempat",
                description="Bayar tunai saat kaos diambil atau diserahkan panitia.",
            ),
        ],
        images=PRODUCT_IMAGES,
    )


@router.get("/catalog", response_model=CatalogResponse)
async def get_catalog() -> CatalogResponse:
    return build_catalog(await get_current_pricing())


@router.get("/pricing", response_model=Pricing)
async def get_pricing() -> Pricing:
    return await get_current_pricing()


@router.patch("/admin/pricing", response_model=Pricing)
async def update_pricing(input: PricingUpdate) -> Pricing:
    pricing = Pricing(**input.model_dump())
    await db.settings.update_one(
        {"key": "pricing"},
        {"$set": {"key": "pricing", "value": pricing.model_dump()}},
        upsert=True,
    )
    return pricing