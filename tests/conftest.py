"""
conftest.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ fixtures for testing ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

-allows to define pytest fixtures for this pytest package

-Code sets up the test communication with the testing database:

Creates a client pytest fixture that replaces the get_gb object used by the main code to be a testing object that works
with the testing database, to do this it calls the session fixture which drops the current testing database
to reset it and build a new one with the neccessary stuff like gin for trigram indexing on fuzzy searches for adventure title
to mimic real database.
"""


from fastapi.testclient import TestClient
import pytest
from app.main import app
from app import models
from app.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database import get_gb, Base
from fastapi import status, HTTPException

#----------------------------------[ CREATE TEST USER DATABASE]----------------------------------
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}/{settings.DATABASE_NAME}_test"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind= engine
)

@pytest.fixture()
def session():
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.connect() as connection:
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS username_trgm_idx ON users USING gin (username gin_trgm_ops)"
        ))
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS adventure_title_trgm_idx ON adventures USING gin (title gin_trgm_ops)"
        ))

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_gb():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_gb] = override_get_gb
    yield TestClient(app)
#----------------------------------[ CREATE USER IN DATABASE]----------------------------------
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

#----------------------------------[ CREATE ADVENTURES IN DATABASE]----------------------------------

@pytest.fixture
def test_adventures(test_user, session):
    other_user = models.Users(
        username = "otherUser",
        email = "otherEmail@gmail.com",
        password= "irrelevant"
    )
    session.add(other_user)
    session.commit()

    adventure_data = [
        {
                "title": "new adventure part 1",
                "description": "adventure description 1",
                "owner_id": test_user['user_id']
        },
        {
                "title": "new adventure part 2",
                "description": "adventure description 2",
                "owner_id": test_user['user_id']
        },
        {
                "title": "new adventure part 3",
                "description": "adventure description 3",
                "owner_id": test_user['user_id']
        },
        {
                "title": "other users adventure",
                "description": "some description",
                "owner_id": 2
        }
    ]

    adventure_map = [models.Adventures(**data) for data in adventure_data]
    session.add_all(adventure_map)
    session.commit()

    return session.query(models.Adventures).all()