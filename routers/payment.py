from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.payment import PaymentUpdate, PaymentCreate, PaymentRead
from services import payment_services

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/", response_model=list[PaymentRead])
def list_payments(db: Session = Depends(get_db)):
    return payment_services.list_payments(db)

@router.get("/{id}", response_model=PaymentRead)
def get_payment(id: int, db: Session = Depends(get_db)):
    return payment_services.get_payment(db, id)

@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    return payment_services.create_payment(db, data)

@router.put("/{payment_id}", response_model=PaymentRead)
def update_payment(
    payment_id: int, data: PaymentUpdate, db: Session = Depends(get_db)
):
    return payment_services.update_payment(db, payment_id, data)

@router.delete("/{payment_id}", response_model=PaymentRead)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_services.delete_payment(db, payment_id)
