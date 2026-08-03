from database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), unique=True, nullable=False)
    contact_person = Column(String(100), unique=True, nullable=False)
    contact_email = Column(String(100), unique=True, nullable=False)
    contact_phone_number = Column(String(20), unique=True, nullable=False)
    address = Column(String(255), nullable=True)

    products = relationship("Product", back_populates="supplier")
