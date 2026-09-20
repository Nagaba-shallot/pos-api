from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.category_repository import category_repository

def list_categories(db: Session):
    return category_repository.get_all(db)

def get_category(db: Session, id: int):
    category = category_repository.get(db, id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category

def create_category(db: Session, data):
    return category_repository.create(db, data.model_dump())

def update_category(db: Session, category_id: int, data):
    db_obj = get_category(db, category_id)
    return category_repository.update(
        db, db_obj, data.model_dump(exclude_unset=True)
    )

def delete_category(db: Session, category_id: int):
    db_obj = get_category(db, category_id)
    category_repository.delete(db, db_obj)
    return db_obj