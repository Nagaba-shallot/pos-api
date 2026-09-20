from fastapi import HTTPException, status
from core.security import hash_password
from repositories.user_repository import user_repository
from schemas.user import UserCreate, UserUpdate
from sqlalchemy.orm import Session

def get_user(db:Session, id:int):
    user = user_repository.get(db, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "User not found"
        )
    return user

def list_users(db:Session):
    return user_repository.get_all(db)

def create_user(db: Session, data: UserCreate):
    user_data = data.model_dump()
    user_data["password_hash"] = hash_password(user_data.pop("password"))
    return user_repository.create(db, user_data)

def update_user(db: Session, id: int, data: UserUpdate):
    user = get_user(db, id)
    update_data = data.model_dump(exclude_unset=True)
    password = update_data.pop("password", None)
    if password:
        update_data["password_hash"] = hash_password(password)
    return user_repository.update(db, user, update_data)

def delete_user(db: Session, id:int):
    user = get_user(db, id)
    user_repository.delete(db, user)