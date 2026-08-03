from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.category import CategoryUpdate, CategoryCreate, CategoryRead
from services import category_services

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return category_services.list_categories(db)

@router.get("/{id}", response_model=CategoryRead)
def get_category(id: int, db: Session = Depends(get_db)):
    return category_services.get_category(db, id)

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return category_services.create_category(db, data)

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)
):
    return category_services.update_category(db, category_id, data)

@router.delete("/{category_id}", response_model=CategoryRead)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    return category_services.delete_category(db, category_id)
