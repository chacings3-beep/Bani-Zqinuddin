from fastapi import APIRouter

from lib.db import db
from models.orders import Order, OrderStatusUpdate

router = APIRouter()


@router.get("/admin/orders", response_model=list[Order])
async def get_admin_orders() -> list[Order]:
    documents = await db.orders.find().sort("created_at", -1).to_list(500)
    return [Order(**document) for document in documents]


@router.patch("/admin/orders/{order_id}/status", response_model=Order)
async def update_order_status(order_id: str, input: OrderStatusUpdate) -> Order:
    await db.orders.update_one({"id": order_id}, {"$set": {"status": input.status}})
    document = await db.orders.find_one({"id": order_id})
    if not document:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
    return Order(**document)