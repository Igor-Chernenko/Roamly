"""
Database.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ DataBase Schema Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

handles SQLalchemy Database Model Schema creation (Database strucuture)

Model Design Verion: 0.1
"""
from database import Base
from sqlalchemy import text, Column, Integer, String, TIMESTAMP

#----------------------------------[ Users ]----------------------------------
"""
Data model for Users table in Database
    Collums:
        user_id: integer, primary key 
        username: string, unqique 
        email: string, unique
        password: string, unique, will be encrypted through hashing
        created_at: time, default= when created
"""
class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key = True, nullable=False)
    username = Column(String, nullable = False, unique = True)
    email = Column(String, nullable = False, unique = True)
    password = Column(String, nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default= text("now()"))

#----------------------------------[ Adventures ]----------------------------------

    