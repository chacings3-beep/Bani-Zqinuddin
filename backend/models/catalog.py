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
    child_price: int = 67_000
    prices: dict[str, int] = Field(default_factory=lambda: {
        "anak_pendek": 67_000,
        "anak_panjang": 77_000,
        "S_pendek": 97_000,
        "S_panjang": 107_000,
        "M_pendek": 97_000,
        "M_panjang": 107_000,
        "L_pendek": 97_000,
        "L_panjang": 107_000,
        "XL_pendek": 97_000,
        "XL_panjang": 107_000,
        "XXL_pendek": 107_000,
        "XXL_panjang": 117_000,
        "XXXL_pendek": 107_000,
        "XXXL_panjang": 117_000,
        "4XL_pendek": 107_000,
        "4XL_panjang": 117_000,
    })


class PaymentMethod(BaseModel):
    id: str
    title: str
    badge: str
    description: str | None = None
    accounts: list[dict[str, str]] = Field(default_factory=list)


class PaymentAccount(BaseModel):
    id: str
    bank: str
    account_number: str
    account_name: str


class AdminSettings(BaseModel):
    pricing: Pricing
    accounts: list[PaymentAccount]
    images: dict[str, str]


class AccountListUpdate(BaseModel):
    accounts: list[PaymentAccount]


class ImageUploadResponse(BaseModel):
    key: str
    url: str
    images: dict[str, str]


class AdminLogin(BaseModel):
    pin: str = Field(min_length=6, max_length=6)


class AdminSession(BaseModel):
    authenticated: bool


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