from datetime import datetime

from pydantic import BaseModel, Field


class MerchandiseVariant(BaseModel):
    id: str
    color: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=60)
    size: str = Field(min_length=1, max_length=60)
    price: int = Field(ge=0)


class MerchandiseProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=2, max_length=500)
    active: bool = False
    variants: list[MerchandiseVariant] = Field(min_length=1, max_length=200)


class MerchandiseProductUpdate(MerchandiseProductCreate):
    pass


class MerchandiseProduct(BaseModel):
    id: str
    name: str
    description: str
    image_url: str
    active: bool
    editable: bool = True
    variants: list[MerchandiseVariant]
    created_at: datetime