"""
schemas.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Pydantic Schema Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

describes the apps API data contracts (what is sent/received in API requests and responses).
"""

from pydantic import BaseModel
from pydantic import EmailStr
from datetime import datetime

#----------------------------------[ Users ]----------------------------------
"""
UserBase: basic User outline for inheretence
UserCreate: basic creation of user input
UserReturn: response contract for user information
"""
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserReturn(UserBase):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    #neccessary to allow pydantic to use SQLAlchemy ORM models
    class config:
        orm_mode=True



