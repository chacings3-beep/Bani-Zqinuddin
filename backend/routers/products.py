from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from lib.admin_auth import require_admin
from lib.db import db
from models.products import MerchandiseProduct, MerchandiseProductCreate, MerchandiseProductUpdate, MerchandiseVariant
from routers.catalog import PRODUCT_IMAGES, UPLOAD_DIR, get_current_images, get_current_pricing

router = APIRouter()


async def get_builtin_product() -> MerchandiseProduct:
    pricing = await get_current_pricing()
    images = await get_current_images()
    colors = [("hitam", "Hitam"), ("putih", "Putih")]
    models = [("pendek", "Lengan Pendek"), ("panjang", "Lengan Panjang")]
    sizes = [("anak", "Anak-anak"), ("S", "S"), ("M", "M"), ("L", "L"), ("XL", "XL"), ("XXL", "XXL"), ("XXXL", "XXXL"), ("4XL", "4XL")]
    variants = [
        MerchandiseVariant(
            id=f"{color_id}-{model_id}-{size_id}",
            color=color_label,
            model=model_label,
            size=size_label,
            price=pricing.prices[f"{size_id}_{model_id}"],
        )
        for color_id, color_label in colors
        for model_id, model_label in models
        for size_id, size_label in sizes
    ]
    return MerchandiseProduct(
        id="kaos-bani-zainuddin",
        name="Kaos Bani Zainuddin",
        description="Kaos kebersamaan Bani Zainuddin dengan pilihan warna, lengan, dan ukuran lengkap.",
        image_url=images.get("hitam_pendek", PRODUCT_IMAGES["hitam_pendek"]),
        active=True,
        editable=False,
        variants=variants,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


async def list_saved_products(include_inactive: bool) -> list[MerchandiseProduct]:
    query = {} if include_inactive else {"active": True}
    documents = await db.products.find(query).sort("created_at", -1).to_list(200)
    return [MerchandiseProduct(**document) for document in documents]


@router.get("/products", response_model=list[MerchandiseProduct])
async def get_products() -> list[MerchandiseProduct]:
    return [await get_builtin_product(), *await list_saved_products(False)]


@router.get("/admin/products", response_model=list[MerchandiseProduct])
async def get_admin_products(_: str = Depends(require_admin)) -> list[MerchandiseProduct]:
    return [await get_builtin_product(), *await list_saved_products(True)]


@router.post("/admin/products", response_model=MerchandiseProduct)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    active: bool = Form(False),
    variants_json: str = Form(...),
    file: UploadFile = File(...),
    _: str = Depends(require_admin),
) -> MerchandiseProduct:
    try:
        variants = [MerchandiseVariant(**item) for item in json.loads(variants_json)]
        payload = MerchandiseProductCreate(name=name, description=description, active=active, variants=variants)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Data produk atau variasi tidak valid") from exc
    extension = Path(file.filename or "product.jpg").suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=422, detail="Gunakan foto JPG, PNG, atau WEBP")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    product_id = str(uuid.uuid4())
    filename = f"product-{product_id}{extension}"
    (UPLOAD_DIR / filename).write_bytes(await file.read())
    product = MerchandiseProduct(
        id=product_id,
        image_url=f"/api/uploads/{filename}",
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    await db.products.insert_one(product.model_dump())
    return product


@router.put("/admin/products/{product_id}", response_model=MerchandiseProduct)
async def update_product(product_id: str, input: MerchandiseProductUpdate, _: str = Depends(require_admin)) -> MerchandiseProduct:
    if product_id == "kaos-bani-zainuddin":
        raise HTTPException(status_code=422, detail="Produk bawaan dikelola melalui pengaturan kaos")
    result = await db.products.update_one({"id": product_id}, {"$set": input.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    document = await db.products.find_one({"id": product_id})
    return MerchandiseProduct(**document)


@router.post("/admin/products/{product_id}/image", response_model=MerchandiseProduct)
async def update_product_image(product_id: str, file: UploadFile = File(...), _: str = Depends(require_admin)) -> MerchandiseProduct:
    extension = Path(file.filename or "product.jpg").suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=422, detail="Gunakan foto JPG, PNG, atau WEBP")
    document = await db.products.find_one({"id": product_id})
    if not document:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"product-{product_id}-{uuid.uuid4().hex}{extension}"
    (UPLOAD_DIR / filename).write_bytes(await file.read())
    await db.products.update_one({"id": product_id}, {"$set": {"image_url": f"/api/uploads/{filename}"}})
    document["image_url"] = f"/api/uploads/{filename}"
    return MerchandiseProduct(**document)


@router.delete("/admin/products/{product_id}", status_code=204)
async def delete_product(product_id: str, _: str = Depends(require_admin)) -> None:
    if product_id == "kaos-bani-zainuddin":
        raise HTTPException(status_code=422, detail="Produk bawaan tidak dapat dihapus")
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")