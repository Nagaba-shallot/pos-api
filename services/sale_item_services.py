from fastapi import HTTPException, status
from repositories.sale_item_repository import sale_item_repository
from schemas.sale_item import SaleItemCreate, SaleItemUpdate
from sqlalchemy.orm import Session

def get_sale_item(db:Session, id:int):
    sale_item = sale_item_repository.get(db, id)
    if not sale_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail = "Sale item not found"
        )
    return sale_item    

def list_sale_items(db:Session):
    return sale_item_repository.get_all(db)

def create_sale_item(db: Session, data: SaleItemCreate):
    item_data = data.model_dump()
    if not item_data.get("subtotal") or item_data["subtotal"] == 0:
        item_data["subtotal"] = (item_data["quantity"] * item_data["unit_price"]) - item_data["discount_amount"]
        
    return sale_item_repository.create(db, item_data)

def update_sale_item(db: Session, id: int, data: SaleItemUpdate):
    sale_item = get_sale_item(db, id)
    
    update_data = data.model_dump(exclude_unset=True)
    if any(k in update_data for k in ["quantity", "unit_price", "discount_amount"]):
        qty = update_data.get("quantity", sale_item.quantity)
        price = update_data.get("unit_price", sale_item.unit_price)
        disc = update_data.get("discount_amount", sale_item.discount_amount)
        update_data["subtotal"] = (qty * price) - disc
        
    return sale_item_repository.update(db, sale_item, update_data)

def delete_sale_item(db: Session, id: int):
    sale_item = get_sale_item(db, id)
    sale_item_repository.delete(db, sale_item)