"""
user.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ user Router ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles user CRUD operations for the api

Version 0.3.0
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy import text
from typing import List, Optional

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

#----------------------------------[ GET /user ]----------------------------------
"""
GET request to Retreive a list of users

Inputs:
    -username to search for
    -amount to skip (default = 0)
    -amount to limit to (default =10)

Process:
    - if the username search term is present:
        -uses trigram indexes to search database and return users with 
         similiar usernames, uses params to avoid sql injections.
        -Pydantic processes each row from query into a UserReturn object to return
    - if the username search term is not present:
        - gets a query of users based off of Inputs

Return:
    -returns List of UserReturn objects

    """
@router.get("/", response_model = List[UserReturn])
async def get_user(
    db: Session = Depends(get_gb),
    username: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):

    if username:
        similarity_amount = 0.1
        sql = text(f"""
        SELECT * FROM users
        WHERE similarity(username, :u) > :sim_amount
        ORDER BY similarity(username, :u) DESC
        OFFSET :offset_amount
        LIMIT :limit_amount
        """)

        params = {
            "u": username,
            "sim_amount": similarity_amount,
            "offset_amount": skip,
            "limit_amount": limit
        }

        user_search = db.execute(sql, params)

        return [UserReturn(**dict(row)) for row in user_search]
    else:
        user_search = (
            db.query(User)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return user_search
    
#----------------------------------[ GET /user/{id} ]----------------------------------
"""
Simple get request to get a user with a certain ID

inputs: Id of user

Return: if found: user
        if not found: HTTP 404 
"""
@router.get("/{id}", response_model = UserReturn)
async def get_user_id(id: int, db: Session = Depends(get_gb)):
    queried_user = db.query(User).filter(User.user_id == id).first()
    
    if not queried_user:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"coult not find user with id={id}"
        )
    
    return queried_user