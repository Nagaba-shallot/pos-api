from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class ReceiptCreate(BaseModel):
    sale_id: int
    receipt_number: str
    receipt_text: str | None = None
    printed_time: datetime

class ReceiptUpdate(BaseModel):
    sale_id: int | None = None
    receipt_number: str | None = None
    receipt_text: str | None = None
    printed_time: datetime | None = None    

class ReceiptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sale_id: int
    receipt_number: str
    receipt_text: str | None = None
    printed_time: datetime