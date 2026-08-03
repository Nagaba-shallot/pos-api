from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    first_name: str | None = None
    last_name: str | None = None

class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    role: str | None = None
    first_name: str | None = None
    last_name: str | None = None

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    updated_at: datetime