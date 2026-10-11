from fastapi import APIRouter, Depends, HTTPException
from fastapi import Cookie, Response

from lib.admin_auth import create_session, require_admin, revoke_session, verify_pin
from lib.db import db
from models.catalog import AdminLogin, AdminSession
from models.orders import Order, OrderStatusUpdate

router = APIRouter()


@router.post("/admin/login", response_model=AdminSession)
async def admin_login(input: AdminLogin, response: Response) -> AdminSession:
    if not verify_pin(input.pin):
        raise HTTPException(status_code=401, detail="PIN admin salah")
    response.set_cookie("admin_session", create_session(), httponly=True, samesite="lax", secure=False, max_age=60 * 60 * 12, path="/")
    return AdminSession(authenticated=True)


@router.get("/admin/session", response_model=AdminSession)
async def admin_session(admin_session: str | None = Cookie(default=None)) -> AdminSession:
    try:
        require_admin(admin_session)
        return AdminSession(authenticated=True)
    except HTTPException:
        return AdminSession(authenticated=False)


@router.post("/admin/logout", response_model=AdminSession)
async def admin_logout(response: Response, admin_session: str | None = Cookie(default=None)) -> AdminSession:
    revoke_session(admin_session)
    response.delete_cookie("admin_session", path="/")
    return AdminSession(authenticated=False)


@router.get("/admin/orders", response_model=list[Order])
async def get_admin_orders(_: str = Depends(require_admin)) -> list[Order]:
    documents = await db.orders.find().sort("created_at", -1).to_list(500)
    return [Order(**document) for document in documents]


@router.patch("/admin/orders/{order_id}/status", response_model=Order)
async def update_order_status(order_id: str, input: OrderStatusUpdate, _: str = Depends(require_admin)) -> Order:
    await db.orders.update_one({"id": order_id}, {"$set": {"status": input.status}})
    document = await db.orders.find_one({"id": order_id})
    if not document:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
    return Order(**document)