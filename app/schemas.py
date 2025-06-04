"""
schemas.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Pydantic Schema Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

describes the apps API data contracts (what is sent/received in API requests and responses).
"""

from pydantic import BaseModel
from pydantic import EmailStr
from datetime import datetime
from fastapi import UploadFile
from typing import Optional
#----------------------------------[ Utilities ]----------------------------------
"""
Token: Returns a Token for user login
"""
class Token(BaseModel):
    access_token: str 
    token_type:str

#----------------------------------[ Users ]----------------------------------
"""
UserBase: basic User outline for inheretence
UserCreate: schema for creation of user input [post]
UserLogin: schema for logging into user [post]
UserAuthReturn: response contract for JWT information after UserCreate [post]
UserUpdate: schema for updating any of the Users information (email,password, username) [put]
UserReturn: response contract for user information [get]
"""
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    identification: str
    password: str

class UserAuthReturn(UserBase):
    user_id: int
    jwt_token: str
    created_at: datetime

    #neccessary to allow pydantic to use SQLAlchemy ORM models
    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserReturn(UserBase):
    user_id: int
    created_at: datetime
    #includes:    email: EmailStr
    #             username: str
    model_config = {
        "from_attributes": True
    }

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

    model_config = {
        "from_attributes": True
    }

    
#----------------------------------[ Images ]----------------------------------

class ImageBase(BaseModel):
    caption: str
    adventure_id: int

class ImageReturn(ImageBase):
    image_id: int
    url: str
    owner_id: int

    model_config = {
        "from_attributes": True
    }

class ImageChange(BaseModel):
    caption: str

#----------------------------------[ Comments ]----------------------------------

class CommentBase(BaseModel):
    comment : str

class CommentPost(CommentBase):
    pass

class CommentReturn(CommentBase):
    comment_id: int
    owner_id: int
    created_at: datetime
    owner: UserReturn

