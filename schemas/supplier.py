from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class SupplierCreate(BaseModel):
    company_name: str
    contact_person: str
    contact_email: str
    contact_phone: str
    address: str

class SupplierUpdate(BaseModel):
    company_name: str | None = None
    contact_person: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None

class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    contact_person: str
    contact_email: str
    contact_phone: str
    address: str
    created_at: datetime
    updated_at: datetime