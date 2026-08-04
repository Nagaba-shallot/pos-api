from database import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), unique=True, nullable=False)
    contact_person = Column(String(100), unique=True, nullable=False)
    contact_email = Column(String(100), unique=True, nullable=False)
    contact_phone = Column(String(20), unique=True, nullable=False)
    address = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    products = relationship("Product", back_populates="supplier")

