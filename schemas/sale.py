from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class SaleCreate(BaseModel):
    customer_id: int
    user_id: int
    sale_date: datetime
    total_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal

class SaleUpdate(BaseModel):
    customer_id: int | None = None
    user_id: int | None = None
    sale_date: datetime | None = None
    total_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    discount_amount: Decimal | None = None

class SaleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    user_id: int
    sale_date: datetime
    total_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    created_at: datetime
    updated_at: datetime