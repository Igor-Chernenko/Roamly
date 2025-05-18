"""
user.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ user Router ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles user CRUD operations for the api

Version 0.1.0
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.schemas import UserCreate, UserAuthReturn, UserReturn
from app.database import get_gb
from app.oauth2 import get_current_user, create_access_token
from app.models import Users as User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_password_requirments(password:str):
    """
    simple function to check password requirments:
    -8 characters
    -at least one 1 and 1 number
    """
    if len(password)<8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "password must have at least 8 characters"
        )
    
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)

    if not has_letter or not has_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "password must have at least one number and one letter"
        )
    
#----------------------------------[ POST /user ]----------------------------------
"""
Post request to create a user

Input:
    email: email of user, must be unique and valid EmailStr type
    username: username of user, must be unique
    password: password of user 

process:
    -checks if email/ username already exists
    -Checks password requirments
    -Hashes password
    -Uploads user to database

Returns: 
    -If successfull: returns user information without password and logs them in with JWT token
    -else:
        -returns HTTP 409 if email or username exits
        -returns HTTP 400 if password doesnt meet specifications

"""

@router.post("/", status_code=status.HTTP_200_OK, response_model=UserAuthReturn)
async def post_user(new_user_data: UserCreate, db: Session = Depends(get_gb)):

    if db.query(User).filter(User.email == new_user_data.email).first():
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail="Email has already been used to create acount"
        )
    if db.query(User).filter(User.username == new_user_data.username).first():
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail="There is already an acount with that username"
        )
    
    check_password_requirments(new_user_data.password)

    hashed_password = pwd_context.hash(new_user_data.password)
    new_user_data.password = hashed_password

    new_user = User(**new_user_data.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data= {"user_id":new_user.user_id})
    
    return {
        "jwt_token":access_token,
        "created_at":new_user.created_at,
        "email":new_user.email,
        "username":new_user.username
    }
