from fastapi import status, HTTPException
from typing import List
import pytest
from jose import jwt
from app.config import settings

from app import schemas
from .database import client, session

@pytest.fixture
def test_user(client):
    user_data = {
        "email": "test_user@gmail.com",
        "username": "test_username",
        "password" : "password123"
    }
    result = client.post('/user', json= user_data)
    assert result.status_code == status.HTTP_201_CREATED
    new_user = result.json() 
    new_user["password"] = user_data["password"]
    #add password to fixture for testing
    return new_user
#----------------------------------[ TEST POST /user ]----------------------------------

def test_create_user(client, session):
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

def test_create_user_invalid_email(client):
    bad_emails: List[str] = [
        "emailgmailcom", "emailgmail.com", "email@gmailcom", "a@.com", "@r.com"
    ]

    for i, email in enumerate(bad_emails):
        bad_email_json = {
            "email": email,
            "username": f"cool_username{i}",
            "password": "password1235"
        }

        result = client.post("/user/", json= bad_email_json)
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"failed on email: {email}"

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


    