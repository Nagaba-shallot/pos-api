from fastapi import HTTPException, status
from repositories import sale_item_repository
from schemas.sale_item import SaleItemCreate, SaleItemUpdate
from sqlalchemy.orm import Session

def get_sale_item(db:Session, id:int):
    sale_item = sale_item_repository.get(db, id)
    if not sale_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details = "Sale item not found"
        )
    return sale_item    

def list_sale_items(db:Session):
    return sale_item_repository.get_all(db)

def create_sale_item(db: Session, data: SaleItemCreate):
    return sale_item_repository.create(db, data.model_dump)

def update_sale_item(db: Session, id: int, data: SaleItemUpdate):
    sale_item = get_sale_item(db, id)
    return sale_item_repository.update(db, sale_item, data.model_dump(exclude_unset=True))

def delete_sale_item(db: Session, id:int):
    sale_item = get_sale_item(db, id)
    sale_item_repository.delete(db, sale_item)