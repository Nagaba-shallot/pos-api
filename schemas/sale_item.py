from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class SaleItemCreate(BaseModel):
    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount_amount: Decimal
    subtotal: Decimal

class SaleItemUpdate(BaseModel):
    sale_id: int | None = None
    product_id: int | None = None
    quantity: int | None = None
    unit_price: Decimal | None = None
    discount_amount: Decimal | None = None
    subtotal: Decimal | None = None

class SaleItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount_amount: Decimal
    subtotal: Decimal