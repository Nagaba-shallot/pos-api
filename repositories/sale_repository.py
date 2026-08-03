from models.sale import Sales
from sqlalchemy.orm import Session  

class SaleRepository:
    def __init__(self):
        self.model = Sales

    def get(self, db:Session, id:int):
        return db.get(Sales, id)

    def get_all(self, db:Session):
        return db.query(Sales).all()

    def create(self, db:Session, data: dict):
        sale = Sales(**data)
        db.add(sale)
        db.commit()
        db.refresh(sale)
        return sale

    def update(self, db:Session, db_obj: Sales, data:dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Sales):
        db.delete(db_obj)
        db.commit()

sale_repository = SaleRepository()