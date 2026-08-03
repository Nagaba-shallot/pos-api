from database import Base
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String
)
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stock_keeping_unit = Column(String, unique=True, nullable=False, index=True)
    price = Column(Numeric(10,2), nullable=False)
    quantity_in_stock = Column(Integer, nullable=False)
    reorder_level = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=True)

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product") 

