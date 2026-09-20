from models.user import User
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self):
        self.model = User

    def get_by_username(self, db:Session, username:str):
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(self.model).filter(self.model.email == email).first()


    def get_by_id(self, db: Session, id: int):
        return db.get(self.model, id)

    def get(self, db:Session, id:int):
        return db.get(User, id)

    def get_all(self, db:Session):
        return db.query(User).all()

    def create(self, db:Session, data: dict):
        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db:Session, db_obj: User, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:User):
        db.delete(db_obj)
        db.commit()

user_repository = UserRepository()