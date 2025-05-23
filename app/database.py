"""
Database.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ DataBase Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles Database connections 
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}/{settings.DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind= engine
)

Base = declarative_base()
#create base class that all ORM classes will inherit from


#function to ensure database connection on each route
def get_gb():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()