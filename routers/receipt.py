from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.receipt import ReceiptUpdate, ReceiptCreate, ReceiptRead
from services import receipt_services

router = APIRouter(prefix="/receipts", tags=["receipts"])

@router.get("/", response_model=list[ReceiptRead])
def list_receipts(db: Session = Depends(get_db)):
    return receipt_services.list_receipts(db)

@router.get("/{id}", response_model=ReceiptRead)
def get_receipt(id: int, db: Session = Depends(get_db)):
    return receipt_services.get_receipt(db, id)

@router.post("/", response_model=ReceiptRead, status_code=status.HTTP_201_CREATED)
def create_receipt(data: ReceiptCreate, db: Session = Depends(get_db)):
    return receipt_services.create_receipt(db, data)

@router.put("/{receipt_id}", response_model=ReceiptRead)
def update_receipt(
    receipt_id: int, data: ReceiptUpdate, db: Session = Depends(get_db)
):
    return receipt_services.update_receipt(db, receipt_id, data)

@router.delete("/{receipt_id}", response_model=ReceiptRead)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    return receipt_services.delete_receipt(db, receipt_id)
