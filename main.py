from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from routers import auth, category, customer, payment, products, receipt, sale_item, sale, supplier, user
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

#Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="POS API", version="1.0.0")

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "The request conflicts with existing data "
            "(duplicate value, unknown reference, or record still in use)."
        },
    )

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(customer.router)
app.include_router(payment.router)
app.include_router(products.router)  
app.include_router(receipt.router)
app.include_router(sale_item.router)
app.include_router(sale.router)
app.include_router(supplier.router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Point of Sale API"}