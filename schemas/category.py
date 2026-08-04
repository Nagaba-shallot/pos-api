from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class CategoryCreate(BaseModel):
    name: str
    category_description: str | None = None  

class CategoryUpdate(BaseModel):
    name: str | None = None
    category_description: str | None = None

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    name: str
    category_description: str | None = None
    created_at: datetime
    updated_at: datetime
