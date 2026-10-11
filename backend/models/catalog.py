from pydantic import BaseModel, Field


class ProductColor(BaseModel):
    id: str
    label: str
    hex: str


class ProductSleeve(BaseModel):
    id: str
    label: str
    extra_price: int = 0


class ProductSize(BaseModel):
    id: str
    label: str
    category: str
    extra_price: int = 0


class Pricing(BaseModel):
    base_price: int = 85_000
    child_price: int = 70_000
    long_sleeve_extra: int = 10_000
    xxl_extra: int = 5_000
    xxxl_extra: int = 10_000


class PaymentMethod(BaseModel):
    id: str
    title: str
    badge: str
    description: str | None = None
    accounts: list[dict[str, str]] = Field(default_factory=list)


class CatalogResponse(BaseModel):
    product_name: str
    colors: list[ProductColor]
    sleeves: list[ProductSleeve]
    sizes: list[ProductSize]
    pricing: Pricing
    payment_methods: list[PaymentMethod]
    images: dict[str, str]


class PricingUpdate(Pricing):
    pass