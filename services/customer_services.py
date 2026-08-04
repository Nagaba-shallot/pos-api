from fastapi import HTTPException, status
from repositories.customer_repository import customer_repository
from schemas.customer import CustomerCreate, CustomerUpdate
from sqlalchemy.orm import Session  

def get_customer(db:Session, id:int):
    customer = customer_repository.get(db, id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details = "Customer not found"
        )
    return customer

def list_customers(db:Session):
    return customer_repository.get_all(db)  

def create_customer(db: Session, data: CustomerCreate):
    return customer_repository.create(db, data.model_dump())

def update_customer(db: Session, id: int, data: CustomerUpdate):
    customer = get_customer(db, id)
    return customer_repository.update(db, customer, data.model_dump(exclude_unset=True))    

def delete_customer(db: Session, id:int):
    customer = get_customer(db, id)
    customer_repository.delete(db, customer)