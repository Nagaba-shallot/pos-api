from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

class ProductCreate(BaseModel):
    name:str
    stock_keeping_unit: str
    price: Decimal
    quantity_in_stock: int
    reorder_level: int 
    category_id: int
    supplier_id: int | None = None

class ProductUpdate(BaseModel):
    name:str | None = None
    stock_keeping_unit: str | None = None
    price: Decimal | None = None
    quantity_in_stock: int | None = None
    reorder_level: int | None = None
    category_id: int | None = None
    supplier_id: int | None = None

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id:int
    created_at: datetime
