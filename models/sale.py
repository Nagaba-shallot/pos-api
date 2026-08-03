from database import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship

class Sales(Base):
    __tablename__ = "sales"

    sale_id = Column(Integer, primary_key=True, index=True)
    sale_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    
    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    sale_items = relationship("SaleItem", back_populates="sales")
    payments = relationship("Payment", back_populates="sale")
    receipts = relationship("Receipt", back_populates="sales")
