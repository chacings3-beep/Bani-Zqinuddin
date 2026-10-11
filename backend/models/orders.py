from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


PaymentMethodId = Literal["transfer", "cod"]
OrderStatus = Literal[
    "pending",
    "transfer_verified",
    "in_production",
    "ready_for_pickup",
    "completed",
    "cancelled",
]


class OrderItemCreate(BaseModel):
    product_id: str = "kaos-bani-zainuddin"
    variant_id: str | None = None
    color: str
    sleeve: str
    size: str
    quantity: int = Field(ge=1, le=99)


class OrderCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=8, max_length=30)
    address: str = Field(min_length=8, max_length=500)
    payment_method: PaymentMethodId
    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)


class OrderItem(BaseModel):
    product_id: str = "kaos-bani-zainuddin"
    product_name: str = "Kaos Bani Zainuddin"
    variant_id: str | None = None
    color: str
    color_label: str
    sleeve: str
    sleeve_label: str
    size: str
    size_label: str
    quantity: int
    unit_price: int
    line_total: int


class Order(BaseModel):
    id: str
    order_number: str
    full_name: str
    phone: str
    address: str
    payment_method: PaymentMethodId
    items: list[OrderItem]
    total_amount: int
    status: OrderStatus
    created_at: datetime


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
