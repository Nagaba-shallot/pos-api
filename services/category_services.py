from sqlalchemy.orm import Session
from repositories import category_repository

def list_categories(db: Session):
    return category_repository.get_all(db)

def get_category(db: Session, id: int):
    return category_repository.get(db, id)

def create_category(db: Session, data):
    category_data = data.model_dump() if hasattr(data, "model_dump") else data.dict()
    return category_repository.create(db, category_data)

def update_category(db: Session, category_id: int, data):
    db_obj = category_repository.get(db, category_id)
    if not db_obj:
        return None
    category_data = data.model_dump() if hasattr(data, "model_dump") else data.dict()
    return category_repository.update(db, db_obj, category_data)

def delete_category(db: Session, category_id: int):
    db_obj = category_repository.get(db, category_id)
    if not db_obj:
        return None
    category_repository.delete(db, db_obj)
    return db_obj
