"""
test_user.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Tests for User Endpoints ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

"""


from fastapi import status, HTTPException
from typing import List
import pytest
from jose import jwt

from app.config import settings
from app import schemas
from tests.testing_strings import long_email, sql_injections
#----------------------------------[ TEST POST /user ]----------------------------------

def test_create_user(client):
    user_create_json = {
        "email": "email@gmail.com",
        "username": "cool_username1234",
        "password": "password1235"
    }
    result = client.post("/user/", json= user_create_json)
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

    result = client.post("/user/", json= bad_email_json)
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

        result = client.post("/user/", json= bad_password_json)
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

    