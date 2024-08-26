from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


sqlalchemy_database_url= settings.DATABASE_URL

engine=create_engine(sqlalchemy_database_url)

SessionLocal= sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)

# Base.metadata.create_all(bind=engine)
