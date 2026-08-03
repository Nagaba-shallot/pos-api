from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.supplier import SupplierUpdate, SupplierCreate, SupplierRead
from services import supplier_services

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

@router.get("/", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    return supplier_services.list_suppliers(db)

@router.get("/{id}", response_model=SupplierRead)
def get_supplier(id: int, db: Session = Depends(get_db)):
    return supplier_services.get_supplier(db, id)

@router.post("/", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    return supplier_services.create_supplier(db, data)

@router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier(
    supplier_id: int, data: SupplierUpdate, db: Session = Depends(get_db)
):
    return supplier_services.update_supplier(db, supplier_id, data)

@router.delete("/{supplier_id}", response_model=SupplierRead)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    return supplier_services.delete_supplier(db, supplier_id)
