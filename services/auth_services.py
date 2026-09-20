from typing import Any
from fastapi import HTTPException, status
import jwt
from sqlalchemy.orm import Session

from core.security import (
    create_access_token, 
    decode_access_token, 
    hash_password,
    verify_password

)

from models.user import User
from repositories.user_repository import user_repository
from schemas.user import UserCreate

def register (db:Session, data: UserCreate):
    if user_repository.get_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User name already exists"
        )
    if user_repository.get_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email address already registered"
        )
    values=data.model_dump(exclude={"password"})
    values["password_hash"]=hash_password(data.password)
    return user_repository.create(db, values)

def authenticate(db:Session, username:str, password:str):
    user=user_repository.get_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"www-Authenticate":"Bearer"}
        )
    return{
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }

def get_user_from_token(db:Session, token: str):
    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="INvalid or expired token",
        headers={"www-Authenticate":"Bearer"}
    )

    try:
        payload: dict[str, Any]=decode_access_token(token)
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise credential_error
        user_id = int(subject)
        if user_id <=0:
            raise credential_error
    except Exception as e:
        raise credential_error

    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise credential_error

    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a user"
        )
    return user