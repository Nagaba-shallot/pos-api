from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict  

class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str | None = None
    address: str | None = None  

class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    address: str | None = None

class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str | None = None
    address: str | None = None
    created_at: datetime
    updated_at: datetime