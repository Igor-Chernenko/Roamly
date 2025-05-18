"""
oauth2.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ oauth2.py ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles authentication using JWT's (JSON Web Tokens) 

Version 0.1.0
"""

from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_gb
from app.models import Users

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MIN = settings.ACCESS_TOKEN_EXPIRE_MIN

#----------------------------------[ Create JWT Token ]----------------------------------
"""
Create access token based off of user creation/login payload, used to confirm user identity

input: data (json including user creation/login details)

process:
    - finds the time (ACCESS_TOKEN_EXPIRE_MIN) from when called and adds it to payload
    - creates an encoded JWT based off the provided payload, SECRET_KEY, and ALGORITHM

returns: jwt string signed with SECRET_KEY, and ALGORITHM
"""
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    to_encode.update({"exp": expire, "sub": str(data["user_id"])})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

#----------------------------------[ Verify JWT Token ]----------------------------------
"""
Verify that the provided JWT token is real, untampered, unexpired, and extracts user_id

input:
    -JWT token string to decode and parse
    -Standard created credentials exception, does not specify

process:
    - decodes token
    - wrap in TokenData pydantic class for schema validation

Returns:
    User data (id)
"""
class TokenData(BaseModel):
    id: Optional[int]

def verify_token(token: str, credentials_exception):
    try:
        payload_data: dict = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload_data.get("sub")

        if id is None:
            raise credentials_exception
        
        user_data = TokenData(id=id)

    except JWTError:
        raise credentials_exception
    
    return user_data

#----------------------------------[ JWT Middleware processing ]----------------------------------
"""
oauth2_scheme: tells fastapi to expect a bearer token in authorization header for routes that are protected
    -header example: Authorization: Bearer <JWT>

get_current_user:
authentication dependency used in protected routes
    inputs: 
        - jwt token as string formated by fastapi
        - db session
    
    process:
        - extracts token
        - verifies token with verify_token()
        - fetches the user accessing the path

    returns: authenticated User from database
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_gb)):

    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}  
    )

    token_data = verify_token(token, credentials_exception)
    queried_user = db.query(Users).filter(Users.user_id == token_data.id).first()

    return queried_user
