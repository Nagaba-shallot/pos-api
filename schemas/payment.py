from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict  

class PaymentCreate(BaseModel):
    sale_id: int
    payment_method: str
    payment_amount: Decimal
    payment_date: datetime  

class PaymentUpdate(BaseModel):
    sale_id: int | None = None
    payment_method: str | None = None
    payment_amount: Decimal | None = None
    payment_date: datetime | None = None

class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sale_id: int
    payment_method: str
    payment_amount: Decimal
    payment_date: datetime
    