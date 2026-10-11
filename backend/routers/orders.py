from datetime import datetime, timezone
import re
import uuid

from fastapi import APIRouter, HTTPException, Query

from lib.db import db
from models.orders import Order, OrderCreate, OrderItem
from routers.catalog import get_current_pricing

router = APIRouter()


def normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone)


def calculate_unit_price(size: str, sleeve: str, pricing) -> int:
    if size == "anak":
        base = pricing.child_price
    elif size == "XXL":
        base = pricing.base_price + pricing.xxl_extra
    elif size == "XXXL":
        base = pricing.base_price + pricing.xxxl_extra
    else:
        base = pricing.base_price
    return base + (pricing.long_sleeve_extra if sleeve == "panjang" else 0)


async def make_order(input: OrderCreate) -> Order:
    catalog = await db.settings.find_one({"key": "catalog"})
    _ = catalog  # reserved for future catalog administration
    pricing = await get_current_pricing()
    color_labels = {"hitam": "Hitam", "putih": "Putih"}
    sleeve_labels = {"pendek": "Lengan Pendek", "panjang": "Lengan Panjang"}
    size_labels = {"anak": "Anak-anak", "S": "S", "M": "M", "L": "L", "XL": "XL", "XXL": "XXL", "XXXL": "XXXL"}
    items: list[OrderItem] = []
    for item in input.items:
        if item.color not in color_labels or item.sleeve not in sleeve_labels or item.size not in size_labels:
            raise HTTPException(status_code=422, detail="Variasi kaos tidak valid")
        unit_price = calculate_unit_price(item.size, item.sleeve, pricing)
        items.append(
            OrderItem(
                color=item.color,
                color_label=color_labels[item.color],
                sleeve=item.sleeve,
                sleeve_label=sleeve_labels[item.sleeve],
                size=item.size,
                size_label=size_labels[item.size],
                quantity=item.quantity,
                unit_price=unit_price,
                line_total=unit_price * item.quantity,
            )
        )
    now = datetime.now(timezone.utc)
    order = Order(
        id=str(uuid.uuid4()),
        order_number=f"BZ-{now.strftime('%y%m%d')}-{uuid.uuid4().hex[:5].upper()}",
        full_name=input.full_name.strip(),
        phone=input.phone.strip(),
        address=input.address.strip(),
        payment_method=input.payment_method,
        items=items,
        total_amount=sum(item.line_total for item in items),
        status="pending",
        created_at=now,
    )
    document = order.model_dump()
    document["phone_normalized"] = normalize_phone(order.phone)
    await db.orders.insert_one(document)
    return order


@router.post("/orders", response_model=Order)
async def create_order(input: OrderCreate) -> Order:
    return await make_order(input)


@router.get("/orders/lookup", response_model=list[Order])
async def lookup_orders(phone: str = Query(min_length=8, max_length=30)) -> list[Order]:
    phone_normalized = normalize_phone(phone)
    if len(phone_normalized) < 8:
        raise HTTPException(status_code=422, detail="Nomor telepon tidak valid")
    documents = await db.orders.find({"phone_normalized": phone_normalized}).sort("created_at", -1).to_list(100)
    return [Order(**document) for document in documents]