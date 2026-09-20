import uuid
from fastapi import HTTPException, status
from repositories.receipt_repository import receipt_repository
from schemas.receipt import ReceiptCreate, ReceiptUpdate
from sqlalchemy.orm import Session

def get_receipt(db: Session, id: int):
    receipt = receipt_repository.get(db, id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found"
        )
    return receipt      

def list_receipts(db: Session):  
    return receipt_repository.get_all(db)

def create_receipt(db: Session, data: ReceiptCreate):
    receipt_data = data.model_dump()
    printed_time = receipt_data.pop("printed_time", None)
    if printed_time:
        receipt_data["issued_at"] = printed_time
        
    receipt_data["receipt_number"] = f"REC-{uuid.uuid4().hex[:8].upper()}"
    
    return receipt_repository.create(db, receipt_data)

def update_receipt(db: Session, id: int, data: ReceiptUpdate):
    receipt = get_receipt(db, id)
    update_data = data.model_dump(exclude_unset=True)
    printed_time = update_data.pop("printed_time", None)
    if printed_time:
        update_data["issued_at"] = printed_time
    return receipt_repository.update(db, receipt, update_data)

def delete_receipt(db: Session, id: int):
    receipt = get_receipt(db, id)
    receipt_repository.delete(db, receipt)