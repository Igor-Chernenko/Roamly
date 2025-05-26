"""
oauth2.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ oauth2.py ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles authentication using JWT's (JSON Web Tokens) 


"""

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_gb
from app.models import Users
from app.utils import is_email
from app.models import Users

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MIN = settings.ACCESS_TOKEN_EXPIRE_MIN

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    to_encode.update({"exp": expire, "user_id": str(data["user_id"])})
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
        id: str = payload_data.get("user_id")

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

#----------------------------------[ Authenticate User ]----------------------------------
def verify_password(attempted_password: str, password: str)-> bool:
    """
    helper function to check if a password is the same as another password that is hashed
    """
    return pwd_context.verify(attempted_password, password)


"""
Authenticates User by by checking if User is in database

Inputs: identifcation, password: recieved from fast api's OAuth2PasswordRequestForm

Process: uses the is_email function to check if the identification is of an email type
    if it is then it parses the database with that if not then uses username

return:
    - HTTP 404 if user_information could not be found
    - db_query: users information if found
"""
def authenticate_user(identification: str, password: str, db : Session):
    if is_email(identification):
        user_email = identification
        db_query = db.query(Users).filter(Users.email == user_email).first()
    
    else:
        users_username = identification
        db_query = db.query(Users).filter(Users.username == users_username).first()

    if not db_query or not verify_password(password, db_query.password):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"Password or Identification entered was wrong or does not exist"
        )

    return db_query

