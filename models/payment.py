from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)

    
    sale = relationship("Sales", back_populates="payments")
