from fastapi import HTTPException, status
from repositories.payment_repository import payment_repository
from schemas.payment import PaymentCreate, PaymentUpdate
from sqlalchemy.orm import Session

def get_payment(db:Session, id:int):
    payment = payment_repository.get(db, id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details = "Payment not found"
        )
    return payment

def list_payments(db:Session):
    return payment_repository.get_all(db)

def create_payment(db: Session, data: PaymentCreate):
    return payment_repository.create(db, data.model_dump())   

def update_payment(db: Session, id: int, data: PaymentUpdate):
    payment = get_payment(db, id)
    return payment_repository.update(db, payment, data.model_dump(exclude_unset=True))

def delete_payment(db: Session, id:int):
    payment = get_payment(db, id)
    payment_repository.delete(db, payment)