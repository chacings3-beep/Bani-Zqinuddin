import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from lib.db import db
from models.catalog import (
    CatalogResponse,
    PaymentMethod,
    Pricing,
    ProductColor,
    ProductSize,
    ProductSleeve,
    PricingUpdate,
    AccountListUpdate,
    AdminSettings,
    ImageUploadResponse,
    PaymentAccount,
)
from lib.admin_auth import require_admin

router = APIRouter()

PRODUCT_IMAGES = {
    "hitam_pendek": "https://images.unsplash.com/photo-1610502778270-c5c6f4c7d575?auto=format&fit=crop&w=900&q=85",
    "hitam_panjang": "https://images.unsplash.com/photo-1618354691551-44de113f0164?auto=format&fit=crop&w=900&q=85",
    "putih_pendek": "https://images.unsplash.com/photo-1651761179569-4ba2aa054997?auto=format&fit=crop&w=900&q=85",
    "putih_panjang": "https://images.unsplash.com/photo-1671438118257-cefa6c86fd50?auto=format&fit=crop&w=900&q=85",
}
DEFAULT_ACCOUNTS = [
    {"id": "bri-ahmad", "bank": "BRI", "account_number": "654601043399535", "account_name": "Ahmad Hassan Tsabit"},
]
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"


def default_pricing() -> Pricing:
    return Pricing()


async def get_current_pricing() -> Pricing:
    stored = await db.settings.find_one({"key": "pricing"})
    if not stored:
        return default_pricing()
    value = stored["value"]
    if "prices" in value:
        return Pricing(**value)
    return default_pricing()


async def get_current_images() -> dict[str, str]:
    stored = await db.settings.find_one({"key": "images"})
    return stored["value"] if stored else PRODUCT_IMAGES.copy()


async def get_current_accounts() -> list[PaymentAccount]:
    stored = await db.settings.find_one({"key": "accounts"})
    values = stored["value"] if stored else DEFAULT_ACCOUNTS
    return [PaymentAccount(**account) for account in values]


async def build_catalog(pricing: Pricing) -> CatalogResponse:
    return CatalogResponse(
        product_name="Kaos Bani Zainuddin",
        colors=[
            ProductColor(id="hitam", label="Hitam", hex="#09090B"),
            ProductColor(id="putih", label="Putih", hex="#FFFFFF"),
        ],
        sleeves=[
            ProductSleeve(id="pendek", label="Lengan Pendek"),
            ProductSleeve(id="panjang", label="Lengan Panjang", extra_price=pricing.prices.get("S_panjang", 107_000) - pricing.prices.get("S_pendek", 97_000)),
        ],
        sizes=[
            ProductSize(id="anak", label="Anak-anak", category="Anak", extra_price=pricing.prices.get("anak_pendek", 67_000) - pricing.prices.get("S_pendek", 97_000)),
            ProductSize(id="S", label="S", category="Dewasa"), ProductSize(id="M", label="M", category="Dewasa"),
            ProductSize(id="L", label="L", category="Dewasa"), ProductSize(id="XL", label="XL", category="Dewasa"),
            ProductSize(id="XXL", label="XXL", category="Jumbo", extra_price=pricing.prices.get("XXL_pendek", 107_000) - pricing.prices.get("S_pendek", 97_000)),
            ProductSize(id="XXXL", label="XXXL", category="Jumbo", extra_price=pricing.prices.get("XXXL_pendek", 107_000) - pricing.prices.get("S_pendek", 97_000)),
            ProductSize(id="4XL", label="4XL", category="Jumbo", extra_price=pricing.prices.get("4XL_pendek", 107_000) - pricing.prices.get("S_pendek", 97_000)),
        ],
        pricing=pricing,
        payment_methods=[
            PaymentMethod(
                id="transfer",
                title="Transfer Bank",
                badge="Direkomendasikan",
                description="Transfer manual ke salah satu rekening panitia.",
                accounts=[account.model_dump(exclude={"id"}) for account in await get_current_accounts()],
            ),
            PaymentMethod(
                id="cod",
                title="Cash on Delivery",
                badge="Bayar di tempat",
                description="Bayar tunai saat kaos diambil atau diserahkan panitia.",
            ),
        ],
        images=await get_current_images(),
    )


@router.get("/catalog", response_model=CatalogResponse)
async def get_catalog() -> CatalogResponse:
    return await build_catalog(await get_current_pricing())


@router.get("/uploads/{filename}", response_class=FileResponse)
async def get_uploaded_file(filename: str) -> FileResponse:
    safe_name = Path(filename).name
    path = UPLOAD_DIR / safe_name
    if safe_name != filename or not path.is_file():
        raise HTTPException(status_code=404, detail="Foto tidak ditemukan")
    return FileResponse(path)


@router.get("/pricing", response_model=Pricing)
async def get_pricing(_: str = Depends(require_admin)) -> Pricing:
    return await get_current_pricing()


@router.patch("/admin/pricing", response_model=Pricing)
async def update_pricing(input: PricingUpdate, _: str = Depends(require_admin)) -> Pricing:
    pricing = Pricing(**input.model_dump())
    await db.settings.update_one(
        {"key": "pricing"},
        {"$set": {"key": "pricing", "value": pricing.model_dump()}},
        upsert=True,
    )
    return pricing


@router.get("/admin/settings", response_model=AdminSettings)
async def get_admin_settings(_: str = Depends(require_admin)) -> AdminSettings:
    return AdminSettings(pricing=await get_current_pricing(), accounts=await get_current_accounts(), images=await get_current_images())


@router.put("/admin/accounts", response_model=list[PaymentAccount])
async def update_accounts(input: AccountListUpdate, _: str = Depends(require_admin)) -> list[PaymentAccount]:
    await db.settings.update_one({"key": "accounts"}, {"$set": {"key": "accounts", "value": [account.model_dump() for account in input.accounts]}}, upsert=True)
    return input.accounts


@router.post("/admin/product-image", response_model=ImageUploadResponse)
async def upload_product_image(
    key: str = Form(...),
    file: UploadFile = File(...),
    _: str = Depends(require_admin),
) -> ImageUploadResponse:
    allowed_keys = set(PRODUCT_IMAGES)
    if key not in allowed_keys:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Variasi gambar tidak valid")
    extension = Path(file.filename or "product.jpg").suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Gunakan JPG, PNG, atau WEBP")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{key}-{uuid.uuid4().hex}{extension}"
    (UPLOAD_DIR / filename).write_bytes(await file.read())
    images = await get_current_images()
    images[key] = f"/api/uploads/{filename}"
    await db.settings.update_one({"key": "images"}, {"$set": {"key": "images", "value": images}}, upsert=True)
    return ImageUploadResponse(key=key, url=images[key], images=images)