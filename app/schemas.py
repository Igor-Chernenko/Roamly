"""
schemas.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Pydantic Schema Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

describes the apps API data contracts (what is sent/received in API requests and responses).
"""

from pydantic import BaseModel
from pydantic import EmailStr
from datetime import datetime

from typing import Optional

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

class UserAuthReturn(UserBase):
    jwt_token: str
    created_at: datetime

    #neccessary to allow pydantic to use SQLAlchemy ORM models
    class Config:
        from_attributes = True


class UserReturn(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


#----------------------------------[ Adventures ]----------------------------------
"""
AdventureBase: basic outline for adventure inheretance
AdventureUpdate: schema for updating adventures [PUT]
AdventureReturn: Return Schema for adventure [Get]
"""
class AdventureBase(BaseModel):
    title: str
    description: str

class AdventureUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class AdventureReturn(AdventureBase):
    adventure_id: int
    created_at: datetime
    owner: UserReturn

    class Config:
        from_attributes = True

    
#----------------------------------[ Images ]----------------------------------

