from fastapi import FastAPI
from routers import category, customer, payment, products, receipt, sale_item, sale, supplier, user
from database import Base, engine
from models.category import Category
from models.customer import Customer
from models.payment import Payment
from models.product import Product
from models.receipt import Receipt
from models.sale_item import SaleItem
from models.sale import Sales
from models.supplier import Supplier
from models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="POS API", version="1.0.0")

app.include_router(category.router)
app.include_router(customer.router)
app.include_router(payment.router)
app.include_router(products.router)  
app.include_router(receipt.router)
app.include_router(sale_item.router)
app.include_router(sale.router)
app.include_router(supplier.router)
app.include_router(user.router)
