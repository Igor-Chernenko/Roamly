"""
test_user.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Tests for User Endpoints ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

"""


from fastapi import status, HTTPException
from typing import List, Optional
import pytest
from jose import jwt

from app.config import settings
from app.oauth2 import verify_password
from app.models import Users
from app import schemas
from tests.testing_strings import long_email, sql_injections

#----------------------------------[ TEST POST /user ]----------------------------------


def test_create_user(client):
    user_create_json = {
        "email": "email@gmail.com",
        "username": "cool_username1234",
        "password": "password1235"
    }
    result = client.post("user/", json= user_create_json)
    response = schemas.UserAuthReturn(**result.json())
    assert result.status_code == status.HTTP_201_CREATED
    assert response.username == "cool_username1234"
    assert response.email == "email@gmail.com"

@pytest.mark.parametrize("email, status_code",[
    ("emailgmailcom", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("emailgmail.com", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("email@gmailcom", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("a@.com", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("@r.com", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("a@@gmail.com", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("$*)%)_/#$%^@@gmail.com", status.HTTP_422_UNPROCESSABLE_ENTITY),
    (long_email(), status.HTTP_422_UNPROCESSABLE_ENTITY),
])
def test_create_user_invalid_email(client, email, status_code):
    bad_email_json = {
        "email": email,
        "username": f"username",
        "password": "password123"
    }

    result = client.post("user/", json= bad_email_json)
    assert result.status_code == status_code, f"failed on email: {email}"

#to do: parameterize
def test_create_user_invalid_password(client):
    bad_passwords: List[str] = [
        "short", "nonumbers", "123456789"
    ]
    for i, password in enumerate(bad_passwords):
        bad_password_json = {
            "email": f"email{i}@gmail.com",
            "username": f"cool_username{i}",
            "password": password
        }

        result = client.post("user/", json= bad_password_json)
        assert result.status_code == status.HTTP_400_BAD_REQUEST, f"failed on passowrd: {password}"
        assert result.json().get('detail') in ["password must have at least 8 characters", "password must have at least one number and one letter"]

def test_already_created_details(client, test_user):
    #testing already created email
    user_invalid_email= test_user.copy()
    user_invalid_email['username'] = "new_username"
    result = client.post('user/', json= user_invalid_email)
    assert result.status_code == status.HTTP_409_CONFLICT
    assert result.json().get('detail') == "Email has already been used to create acount"

    #testing already created username
    user_invalid_username = test_user.copy()
    user_invalid_username['email'] = "new_email@gmail.com"
    result = client.post('user/', json= user_invalid_username)
    assert result.status_code == status.HTTP_409_CONFLICT
    assert result.json().get('detail') == "There is already an acount with that username"

#todo implement sql injection checks
#----------------------------------[ TEST POST /user/login ]----------------------------------

def test_login_user_username(test_user, client):
    user_login_data = {
        "username": test_user['username'],
        "password": test_user['password']
    }
    result = client.post('user/login', data= user_login_data)
    login_data = schemas.Token(**result.json())
    payload = jwt.decode(login_data.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    id = int(payload.get("user_id"))

    assert id == test_user['user_id']
    assert result.status_code == status.HTTP_200_OK

def test_login_user_email(test_user, client):
    user_login_data = {
        "username": test_user['email'],
        "password": test_user['password']
    }
    result = client.post('user/login', data= user_login_data)
    login_data = schemas.Token(**result.json())
    payload = jwt.decode(login_data.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    id = int(payload.get("user_id"))

    assert id == test_user['user_id']
    assert result.status_code == status.HTTP_200_OK

@pytest.mark.parametrize("username, password, status_code",[
    ("bademail@gmail.com","password123", status.HTTP_404_NOT_FOUND),
    ("test_user@gmail.com", "password12", status.HTTP_404_NOT_FOUND),
    ("bademail@gmail.com", "password12", status.HTTP_404_NOT_FOUND),
    (None, "password123", status.HTTP_404_NOT_FOUND),
    ("test_user@gmail.com", None, status.HTTP_404_NOT_FOUND)
])
def test_invalid_login_user(test_user, client, username, password, status_code):
    user_login_data = {
        "username": username,
        "password": password
    }

    result = client.post('user/login', data= user_login_data)
    assert result.status_code == status_code
    assert result.json().get('detail') == "Password or Identification entered was wrong or does not exist"

#----------------------------------[ TEST Delete /user/ ]----------------------------------
def test_delete_user(test_user, session, client):
    jwt = {"Authorization" : f"bearer {test_user['jwt_token']}"}
    id = test_user["user_id"]
    user_query = session.query(Users).filter(Users.user_id == id).all()
    assert user_query
    result = client.delete(f"user/{id}", headers=jwt)
    assert result.status_code == status.HTTP_204_NO_CONTENT
    user_query = session.query(Users).filter(Users.user_id == id).all()
    assert not user_query


#----------------------------------[ Test PUT /user/{id} ]----------------------------------
@pytest.mark.parametrize("username, email, password",[
    (None, None, "password123"),
    (None, "email@gmail.com", None),
    ("username", None, None),
    ("username", "email@gmail.com", None),
    ("username", "email@gmail.com", "password123"),
    (None, "email@gmail.com", "password123")
])
def test_modify_user(test_user, session, client, username, email, password):
    id = test_user['user_id']
    test_put_data = {}
    if username:
        test_put_data["username"] = username
    if email:
        test_put_data["email"] = email
    if password:
        test_put_data["password"] = password
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}

    result = client.put(f"user/{id}", json=test_put_data, headers=jwt)
    assert result.status_code == status.HTTP_204_NO_CONTENT
    user_query = session.query(Users).filter(Users.user_id == id).first()
    if username: 
        assert user_query.username == username
    if email:
        assert user_query.email == email
    if password:
        assert verify_password(password, user_query.password) == True
    
@pytest.mark.parametrize("username, email, password, status_code",[
    (None, None, "OnlyChars", status.HTTP_400_BAD_REQUEST),
    (None, None, "short", status.HTTP_400_BAD_REQUEST),
    (None, None, "123456789", status.HTTP_400_BAD_REQUEST),
    (None, "emailgmailcom", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None, "emailgmail.com", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None, "email@gmailcom", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None, "a@.com", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None, "@r.com", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None, "a@@gmail.com", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None, "$*)%)_/#$%^@@gmail.com", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None, "@gmail.com", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (None, long_email(), None, status.HTTP_422_UNPROCESSABLE_ENTITY)
])
def test_invalid_modify_user(test_user, session, client, username, email, password, status_code):
    id = test_user['user_id']
    test_put_data = {}
    if username:
        test_put_data["username"] = username
    if email:
        test_put_data["email"] = email
    if password:
        test_put_data["password"] = password
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}

    result = client.put(f"/user/{id}", json=test_put_data, headers=jwt)
    assert result.status_code == status_code

#----------------------------------[ Test get /user/{id} ]----------------------------------

def test_get_user(client, test_user):
    id = test_user['user_id']
    result = client.get(f"user/{id}")
    user = schemas.UserReturn(**result.json())
    assert user.email == test_user["email"]
    assert user.username == test_user["username"]
    assert user.user_id == id
    assert user.created_at


def test_invalid_get_user(client, test_user):
    id = 124
    result = client.get(f"user/{id}")
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert result.json().get("detail") == f"could not find user with id={id}"