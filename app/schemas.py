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
UserCreate: schema for creation of user input [post]
UserReturn: response contract for user information [get]
"""
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserReturn(UserBase):
    user_id: int
    created_at: datetime

    #neccessary to allow pydantic to use SQLAlchemy ORM models
    class Config:
        from_attributes = True


#----------------------------------[ Adventures ]----------------------------------
"""
AdventureBase: basic outline for adventure inheretance
AdventureCreate: Schema for creation of adventure input [Post]
AdventureReturn: Return Schema for adventure [Get]
"""
class AdventureBase(BaseModel):
    title: str
    description: str

class AdventureReturn(AdventureBase):
    adventure_id: int
    created_at: datetime
    owner: UserReturn

    class Config:
        from_attributes = True

    
#----------------------------------[ Images ]----------------------------------

