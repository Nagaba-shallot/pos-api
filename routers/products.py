from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.product import ProductUpdate, ProductCreate, ProductRead
from services import product_services

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[ProductRead])
def list_product(db: Session = Depends(get_db)):
    return product_services.list_products(db)

@router.get("/{id}", response_model=ProductRead)
def get_product(id:int, db: Session = Depends(get_db)):
    return product_services.get_product(db, id)

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    return product_services.create_product(db, data)

@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id:int, data:ProductUpdate, db: Session = Depends(get_db)
):
    return product_services.create_product(db, data)

@router.delete("/{product_id}", response_model=ProductRead)
def delete_product(
    delete_id:int, data:ProductUpdate, db: Session = Depends(get_db)
):
    return product_services.delete_product(db, data)