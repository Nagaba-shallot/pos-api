from database import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=False)
    receipt_number = Column(String(100), unique=True, nullable=False)
    issued_at = Column(DateTime, default=func.now())

    
    sales = relationship("Sales", back_populates="receipts")
