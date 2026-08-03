from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

database_url = "postgresql://postgres:postgres@localhost:5432/pos_db"
engine = create_engine(database_url, echo=False, future=True)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
