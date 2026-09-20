import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/pos_db"
database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

engine_options = {"echo": False, "future": True}

if database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
    if database_url in ("sqlite://", "sqlite:///:memory:"):
        engine_options["poolclass"] = StaticPool

engine = create_engine(database_url, **engine_options)

if engine.dialect.name == "sqlite":

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()