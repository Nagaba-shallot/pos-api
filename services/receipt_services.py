from fastapi import HTTPException, status
from repositories import receipt_repository
from schemas.receipt import ReceiptCreate, ReceiptUpdate
from sqlalchemy.orm import Session

def get_receipt(db:Session, id:int):
    receipt = receipt_repository.get(db, id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details = "Receipt not found"
        )
    return receipt      

def list_receipts(db:Session):  
    return receipt_repository.get_all(db)

def create_receipt(db: Session, data: ReceiptCreate):
    return receipt_repository.create(db, data.model_dump)

def update_receipt(db: Session, id: int, data: ReceiptUpdate):
    receipt = get_receipt(db, id)
    return receipt_repository.update(db, receipt, data.model_dump(exclude_unset=True))

def delete_receipt(db: Session, id:int):
    receipt = get_receipt(db, id)
    receipt_repository.delete(db, receipt)